"""Browser-owned rbw operations. Secrets never pass through command arguments."""

import json
import os
from pathlib import Path
import re
import secrets
import signal
import shutil
import socket
import stat
import struct
import tempfile
import time

from qutebrowser.api import cmdutils, message
from qutebrowser.commands import runners
from qutebrowser.misc import objects
from qutebrowser.qt import sip
from qutebrowser.qt.core import QObject, QProcess, QProcessEnvironment, QSocketNotifier, QTimer, QUrl
from qutebrowser.qt.network import QLocalSocket
from qutebrowser.utils import objreg, usertypes

FORM_SOURCE = Path(__file__).with_name("rbw_form.js").read_text(encoding="utf-8")
MODES = {"login", "username", "password", "totp"}
MAX_PAYLOAD = 65536
MESSAGES = {
    "filled": "rbw: credentials filled.",
    "cancelled": "rbw: cancelled.",
    "expired": "rbw: request expired.",
    "destination": "rbw: destination changed; fill cancelled.",
    "form": "rbw: focus a supported login field and try again.",
    "unavailable": "rbw: vault unavailable or request could not be completed.",
    "nomatches": "rbw: no matching logins.",
    "mismatch": "rbw: selected entry does not permit this site.",
    "protected": "rbw: protected entry or unsupported vault metadata; fill refused.",
    "missing": "rbw: install rbw and configure its account before filling.",
    "version": "rbw: unsupported CLI version; this integration supports rbw 1.15.x.",
    "picker": "rbw: entry picker unavailable; check Quickshell.",
}


def private_directory(path):
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError("Invalid runtime directory")


def peer_matches(descriptor, pid):
    with socket.socket(fileno=os.dup(descriptor)) as connection:
        actual, uid, _ = struct.unpack("3i", connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
    return actual == pid and uid == os.getuid()


def decode_payload(data, mode):
    payload = json.loads(data)
    fields = {"username", "password"} if mode == "login" else {mode}
    if not isinstance(payload, dict) or set(payload) != fields | {"version", "mode"}:
        raise ValueError("Invalid response")
    if type(payload["version"]) is not int or payload["version"] != 1 or payload["mode"] != mode:
        raise ValueError("Invalid response")
    for field in fields:
        value = payload[field]
        if not isinstance(value, str) or not value or any(char in value for char in "\0\r\n") or len(value.encode("utf-8")) > 16000:
            raise ValueError("Invalid response")
    if mode == "totp" and not re.fullmatch(r"[0-9]{6,10}", payload["totp"]):
        raise ValueError("Invalid response")
    return {field: payload[field] for field in fields}


class Operation(QObject):
    def __init__(self, controller, win_id, tabbed, tab, url, mode):
        super().__init__(controller)
        self.controller = controller
        self.win_id, self.tabbed, self.tab = win_id, tabbed, tab
        self.url, self.mode = url, mode
        self.handle = secrets.token_hex(16)
        self.done = False
        self.claimed = False
        self.directory = None
        self.fifo_fd = None
        self.notifier = None
        self.connections = []
        self.buffer = bytearray()
        self.command_buffer = bytearray()
        self.length = None
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(lambda: self.process.readAllStandardOutput())
        self.process.readyReadStandardError.connect(lambda: self.process.readAllStandardError())
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(lambda _: self.finish("unavailable"))
        self.channel = QLocalSocket(self)
        self.channel.connected.connect(self.connected)
        self.channel.readyRead.connect(self.read_payload)
        self.channel.errorOccurred.connect(lambda _: self.finish("unavailable"))
        self.channel.disconnected.connect(lambda: self.finish("unavailable") if not self.done and self.length is not None else None)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.finish("expired"))
        self.timer.start(300000)
        for signal_name in ("load_started", "url_changed", "destroyed"):
            signal = getattr(tab, signal_name, None)
            if signal is not None:
                slot = lambda *_: self.finish("destination")
                signal.connect(slot)
                self.connections.append((signal, slot))
        signal = tabbed.widget.currentChanged
        slot = lambda *_: self.finish("destination") if not self.destination_valid() else None
        signal.connect(slot)
        self.connections.append((signal, slot))

    def destination_valid(self):
        try:
            return self.tabbed.widget.currentWidget() is self.tab and self.tab.url().toString(
                QUrl.ComponentFormattingOption.FullyEncoded) == self.url
        except Exception:
            return False

    def javascript(self, request, callback=None):
        # This calls the backend directly; no jseval command or key-event logging.
        self.tab.run_js_async(FORM_SOURCE + "(" + json.dumps(request, ensure_ascii=True) + ")", callback=callback, world=42)

    def prepare(self):
        try:
            self.javascript({"action": "prepare", "handle": self.handle, "url": self.url, "mode": self.mode}, self.prepared)
        except Exception:
            self.finish("form")

    def prepared(self, status):
        if self.done:
            return
        if status != "ready" or not self.destination_valid():
            self.finish("destination" if not self.destination_valid() else "form")
            return
        try:
            runtime = Path(os.environ["XDG_RUNTIME_DIR"])
            private_directory(runtime)
            root = runtime / "qute-rbw"
            root.mkdir(mode=0o700, exist_ok=True)
            private_directory(root)
            self.directory = Path(tempfile.mkdtemp(prefix="job.", dir=root))
            fifo = self.directory / "commands"
            os.mkfifo(fifo, 0o600)
            self.fifo_fd = os.open(fifo, os.O_RDWR | os.O_NONBLOCK | os.O_CLOEXEC)
            self.notifier = QSocketNotifier(self.fifo_fd, QSocketNotifier.Type.Read, self)
            self.notifier.activated.connect(self.read_command)
            environment = QProcessEnvironment.systemEnvironment()
            for key, value in {"QUTE_FIFO": fifo, "QUTE_URL": self.url, "QUTERBW_HANDLE": self.handle,
                               "QUTERBW_DIRECTORY": self.directory, "QUTERBW_BROWSER_PID": os.getpid(),
                               "QUTERBW_MODE": self.mode, "PYTHONDONTWRITEBYTECODE": "1", "RUST_LOG": "off"}.items():
                environment.insert(key, str(value))
            self.process.setProcessEnvironment(environment)
            self.process.setProgram(str(self.controller.script))
            self.process.start()
        except Exception:
            self.finish("unavailable")

    def read_command(self, *_):
        if self.done:
            return
        try:
            self.command_buffer.extend(os.read(self.fifo_fd, 1024))
            if len(self.command_buffer) > 512:
                raise ValueError("Invalid command")
            if b"\n" not in self.command_buffer:
                return
            command = bytes(self.command_buffer)
            self.command_buffer.clear()
            if command != f"rbw-fill-once {self.handle}\n".encode("ascii"):
                raise ValueError("Invalid command")
            # Only this fixed, non-secret command reaches the normal command runner.
            runners.CommandRunner(self.win_id, parent=self).run_safely(command.decode("ascii").rstrip("\n"))
        except Exception:
            self.finish("unavailable")

    def claim(self):
        if self.done or self.claimed:
            return
        if not self.destination_valid():
            self.finish("destination")
            return
        self.claimed = True
        self.controller.operations.pop(self.handle, None)
        self.timer.start(10000)
        try:
            path = self.directory / "reply"
            info = path.lstat()
            if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
                raise ValueError("Invalid endpoint")
            self.channel.connectToServer(str(path))
        except Exception:
            self.finish("unavailable")

    def connected(self):
        try:
            if not peer_matches(int(self.channel.socketDescriptor()), int(self.process.processId())):
                raise ValueError("Invalid peer")
        except Exception:
            self.finish("unavailable")

    def read_payload(self):
        if self.done:
            return
        try:
            self.buffer.extend(bytes(self.channel.readAll()))
            if len(self.buffer) > MAX_PAYLOAD + 4:
                raise ValueError("Response too large")
            if self.length is None and len(self.buffer) >= 4:
                self.length = struct.unpack("!I", self.buffer[:4])[0]
                if not 0 < self.length <= MAX_PAYLOAD:
                    raise ValueError("Invalid length")
            if self.length is None or len(self.buffer) < self.length + 4:
                return
            if len(self.buffer) != self.length + 4 or not self.destination_valid():
                self.finish("destination")
                return
            values = decode_payload(bytes(self.buffer[4:]), self.mode)
            self.buffer.clear()
            if self.notifier:
                self.notifier.setEnabled(False)
            self.javascript({"action": "apply", "handle": self.handle, "values": values,
                             "expiresAt": int(time.time() * 1000) + max(0, self.timer.remainingTime())}, self.filled)
            values.clear()
        except Exception:
            self.finish("unavailable")

    def filled(self, status):
        if not self.done:
            self.finish("filled" if status == "filled" else "destination" if status == "destination" else "form")

    def process_finished(self, code, _status):
        if not self.done:
            self.finish({2: "nomatches", 3: "cancelled", 4: "mismatch", 5: "protected", 6: "missing", 7: "version", 8: "picker"}.get(code, "unavailable"))
        self.deleteLater()

    def stop_process(self, force=False):
        if sip.isdeleted(self.process):
            return
        if self.process.state() == QProcess.ProcessState.NotRunning:
            return
        pid = int(self.process.processId())
        try:
            if os.getpgid(pid) == pid:
                os.killpg(pid, signal.SIGKILL if force else signal.SIGTERM)
            else:
                self.process.kill() if force else self.process.terminate()
        except ProcessLookupError:
            pass

    def finish(self, status):
        if self.done:
            return
        self.done = True
        self.timer.stop()
        self.controller.operations.pop(self.handle, None)
        self.controller.jobs.discard(self)
        for signal, slot in self.connections:
            try:
                signal.disconnect(slot)
            except Exception:
                pass
        self.connections.clear()
        self.buffer.clear()
        self.command_buffer.clear()
        if self.notifier:
            self.notifier.setEnabled(False)
        if self.fifo_fd is not None:
            os.close(self.fifo_fd)
            self.fifo_fd = None
        if self.channel.state() == QLocalSocket.LocalSocketState.ConnectedState:
            self.channel.write(b"1" if status == "filled" else b"0")
            self.channel.flush()
            self.channel.disconnectFromServer()
        else:
            self.channel.abort()
        try:
            self.javascript({"action": "discard", "handle": self.handle})
        except Exception:
            pass
        if self.directory:
            shutil.rmtree(self.directory, ignore_errors=True)
        if self.process.state() != QProcess.ProcessState.NotRunning:
            # Allow the acknowledgement to reach the helper; force cleanup if it stalls.
            QTimer.singleShot(250, lambda: self.stop_process())
            QTimer.singleShot(1000, lambda: self.stop_process(True))
        else:
            self.deleteLater()
        message.info(MESSAGES.get(status, MESSAGES["unavailable"]))


class Controller(QObject):
    def __init__(self, parent, script):
        super().__init__(parent)
        self.script = Path(script)
        self.operations = {}
        self.jobs = set()
        self.attached = False

    def attach(self):
        if not self.attached and objects.qapp is not None:
            self.setParent(objects.qapp)
            objects.qapp.aboutToQuit.connect(self.cancel)
            self.attached = True

    def cancel(self):
        for job in tuple(self.jobs):
            job.finish("cancelled")

    def start(self, win_id, mode):
        try:
            self.attach()
            if mode not in MODES:
                raise ValueError("Invalid mode")
            for job in tuple(self.jobs):
                if job.win_id == win_id:
                    job.finish("cancelled")
            tabbed = objreg.get("tabbed-browser", scope="window", window=win_id)
            tab = tabbed.widget.currentWidget()
            url = tab.url().toString(QUrl.ComponentFormattingOption.FullyEncoded)
            parsed = QUrl(url)
            if parsed.scheme() not in {"http", "https"} or not parsed.host() or parsed.userName() or parsed.password():
                raise ValueError("Invalid destination")
            operation = Operation(self, win_id, tabbed, tab, url, mode)
            self.jobs.add(operation)
            self.operations[operation.handle] = operation
            operation.prepare()
        except Exception:
            message.info(MESSAGES["unavailable"])

    def claim(self, win_id, handle):
        operation = self.operations.get(handle)
        if operation is None or operation.win_id != win_id:
            message.info(MESSAGES["expired"])
            return
        operation.claim()


def install(script=None):
    """Replace registrations on config reload and revoke all previous handles."""
    previous = getattr(objects, "_rbw_controller", None)
    if previous:
        previous.cancel()
    controller = Controller(objects.qapp, script or Path.home() / ".local/share/qutebrowser/userscripts/qute-rbw")
    # Config is also loaded before QApplication exists during a fresh startup.
    # The module registry keeps the controller alive until its first command/reload.
    objects._rbw_controller = controller
    controller.attach()
    for name in ("rbw-fill", "rbw-fill-once"):
        objects.commands.pop(name, None)

    @cmdutils.register(name="rbw-fill", backend=usertypes.Backend.QtWebEngine)
    @cmdutils.argument("win_id", value=cmdutils.Value.win_id)
    @cmdutils.argument("mode", choices=sorted(MODES))
    def start(win_id, mode="login"):
        """Confirm an rbw login for the current tab, then fill its fields."""
        controller.start(win_id, mode)

    @cmdutils.register(name="rbw-fill-once", backend=usertypes.Backend.QtWebEngine, no_replace_variables=True)
    @cmdutils.argument("win_id", value=cmdutils.Value.win_id)
    def complete(win_id, handle):
        """Consume a pending rbw operation; never accepts credential arguments."""
        controller.claim(win_id, handle)
    return controller
