"""Reload-safe customizations of qutebrowser widgets and scripts.

These use qutebrowser internals; check them after browser upgrades.
"""

import re

from qutebrowser.mainwindow import mainwindow, prompt, tabwidget
from qutebrowser.misc import miscwidgets
from qutebrowser.qt import sip
from qutebrowser.utils import resources

GREASEMONKEY_HIDDEN_SCRIPT_NAME_PATTERNS = (r"dark reader",)


def apply(palette):
    _install_rbw()
    _install_caret_style_fix()
    _install_greasemonkey_message_filter()
    _install_message_presentation()
    _install_centered_overlays()
    _install_omnibar()
    _install_title_cleanup()
    _install_popup_fixes()
    _install_fullscreen_notice(palette['ACCENT'], palette['FONT_FAMILY'])


def _install_caret_style_fix():
    # qutebrowser #7498: Trusted Types blocks innerHTML on sites like YouTube.
    # The style element contains CSS, so insert it as text instead of HTML.
    # Tabs capture this resource when created; restart to update existing tabs.
    filename = 'javascript/caret.js'
    resources._cache[filename] = resources.read_file(filename).replace(
        'node.innerHTML = style;', 'node.textContent = style;',
    )


def _install_greasemonkey_message_filter():
    from qutebrowser.browser import greasemonkey

    if not hasattr(greasemonkey.LoadResults, '_qute_original_successful_str'):
        greasemonkey.LoadResults._qute_original_successful_str = (
            greasemonkey.LoadResults.successful_str
        )

    original = greasemonkey.LoadResults._qute_original_successful_str
    patterns = tuple(
        re.compile(pattern, re.IGNORECASE)
        for pattern in GREASEMONKEY_HIDDEN_SCRIPT_NAME_PATTERNS
    )

    def format_visible_scripts(self):
        visible = [
            script for script in self.successful
            if not any(pattern.search(str(script)) for pattern in patterns)
        ]
        if len(visible) == len(self.successful):
            return original(self)
        if not visible:
            return 'No visible Greasemonkey scripts loaded'

        names = '\n'.join(str(script) for script in sorted(visible, key=str))
        return f'Loaded Greasemonkey scripts:\n\n{names}'

    greasemonkey.LoadResults.successful_str = format_visible_scripts


def _install_message_presentation():
    from qutebrowser.mainwindow import messageview
    from qutebrowser.qt.core import QEasingCurve, QPoint, QPropertyAnimation, Qt

    if not hasattr(messageview.Message, '_qute_original_init'):
        messageview.Message._qute_original_init = messageview.Message.__init__
    if not hasattr(messageview.MessageView, '_qute_original_show_message'):
        messageview.MessageView._qute_original_show_message = (
            messageview.MessageView.show_message
        )
    if not hasattr(messageview.MessageView, '_qute_original_clear_messages'):
        messageview.MessageView._qute_original_clear_messages = (
            messageview.MessageView.clear_messages
        )

    original_init = messageview.Message._qute_original_init
    original_show_message = messageview.MessageView._qute_original_show_message
    original_clear_messages = messageview.MessageView._qute_original_clear_messages

    def initialize_centered_message(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def show_newest_message_first(self, info):
        if getattr(self, '_qute_message_exit_pending', False):
            self._qute_message_exit_animation.stop()
            self._qute_message_exit_pending = False
            self.move(self._qute_message_exit_target)

        previous_count = len(self._messages)
        original_show_message(self, info)
        if len(self._messages) > previous_count:
            newest = self._messages[-1]
            self._vbox.removeWidget(newest)
            self._vbox.insertWidget(0, newest)

            prompt_container = getattr(self.parentWidget(), '_prompt_container', None)
            if prompt_container is not None and prompt_container.isVisible():
                prompt_container.raise_()
            omnibar = getattr(self.parentWidget().status, '_qute_omnibar', None)
            if omnibar is not None and omnibar.isVisible():
                omnibar.raise_()
                completion = getattr(self.parentWidget(), '_completion', None)
                if completion is not None and completion.isVisible():
                    completion.raise_()

            animation = getattr(self, '_qute_message_entry_animation', None)
            if animation is None:
                animation = QPropertyAnimation(self, b'pos', self)
                self._qute_message_entry_animation = animation
            animation.stop()
            target = self.pos()
            curve = QEasingCurve(QEasingCurve.Type.OutBack)
            curve.setOvershoot(0.8)
            animation.setDuration(320)
            animation.setEasingCurve(curve)
            animation.setStartValue(target + QPoint(0, -18))
            animation.setEndValue(target)
            animation.start()

    def clear_messages_with_exit(self):
        if not self._messages or not self.isVisible():
            original_clear_messages(self)
            return
        if getattr(self, '_qute_message_exit_pending', False):
            return

        self._clear_timer.stop()
        entry_animation = getattr(self, '_qute_message_entry_animation', None)
        if entry_animation is not None:
            entry_animation.stop()
        target = self.pos()
        self._qute_message_exit_target = target
        self._qute_message_exit_pending = True

        animation = getattr(self, '_qute_message_exit_animation', None)
        if animation is None:
            animation = QPropertyAnimation(self, b'pos', self)
            self._qute_message_exit_animation = animation

            def finish_exit():
                if not self._qute_message_exit_pending:
                    return
                self._qute_message_exit_pending = False
                self.move(self._qute_message_exit_target)
                original_clear_messages(self)

            animation.finished.connect(finish_exit)

        curve = QEasingCurve(QEasingCurve.Type.InCubic)
        animation.setDuration(220)
        animation.setEasingCurve(curve)
        animation.setStartValue(target)
        animation.setEndValue(target + QPoint(0, -18))
        animation.start()

    messageview.Message.__init__ = initialize_centered_message
    messageview.MessageView.show_message = show_newest_message_first
    messageview.MessageView.clear_messages = clear_messages_with_exit


def _install_centered_overlays():
    from functools import partial

    from qutebrowser.completion import completionwidget
    from qutebrowser.config import config
    from qutebrowser.mainwindow import messageview
    from qutebrowser.misc import keyhintwidget, objects

    main_window_class = mainwindow.MainWindow
    if not hasattr(main_window_class, '_qute_original_update_overlay_geometry'):
        main_window_class._qute_original_update_overlay_geometry = (
            main_window_class._update_overlay_geometry
        )

    original_update = main_window_class._qute_original_update_overlay_geometry

    def center_overlays(self, widget, centered, padding):
        if isinstance(widget, messageview.MessageView):
            if not widget.isVisible():
                return
            available_width = max(1, self.width() - 2 * padding)
            content_width = max(
                (message.sizeHint().width() for message in widget._messages),
                default=160,
            )
            width = min(available_width, min(560, max(420, content_width + 24)))
            height = (
                widget.heightForWidth(width)
                if widget.hasHeightForWidth()
                else widget.sizeHint().height()
            )
            height = max(1, min(height, self.height() - 2 * padding))
            widget.setGeometry(
                (self.width() - width) // 2,
                padding,
                width,
                height,
            )
        elif isinstance(widget, keyhintwidget.KeyHintView):
            if not widget.isVisible():
                return
            width = min(widget.sizeHint().width(), max(1, self.width() - 2 * padding))
            height = min(widget.sizeHint().height(), max(1, self.height() - 2 * padding))
            widget.setGeometry(
                self.width() - width - padding,
                padding,
                width,
                height,
            )
            widget.raise_()
        elif isinstance(widget, completionwidget.CompletionView):
            omnibar = getattr(self.status, '_qute_omnibar', None)
            if not widget.isVisible():
                return
            width = min(max(1, self.width() - 2 * padding), 950)
            if omnibar is not None and omnibar.isVisible():
                left = omnibar.x()
                width = omnibar.width()
                top = omnibar.y() + omnibar.height()
            else:
                left = (self.width() - width) // 2
                if config.val.statusbar.position == 'top' and self.status.isVisible():
                    top = self.status.geometry().bottom() + padding
                else:
                    bottom = self.status.geometry().top() if self.status.isVisible() else self.height()
                    top = bottom - widget.sizeHint().height() - padding
            height = min(widget.sizeHint().height(), self.height() - top - padding)
            if height > 0:
                widget.setGeometry(left, top, width, height)
                widget.raise_()
        elif getattr(widget, '_qute_omnibar_widget', False):
            if not widget.isVisible():
                return
            width = max(1, min(self.width() - 2 * padding, 950))
            height = max(widget.minimumSizeHint().height(), widget.sizeHint().height())
            top = 0
            height = min(height, max(1, self.height() - top - padding))
            widget.setGeometry(
                (self.width() - width) // 2,
                top,
                width,
                height,
            )
            completion = getattr(self, '_completion', None)
            if completion is not None and completion.isVisible():
                center_overlays(self, completion, True, padding)
        elif isinstance(widget, prompt.PromptContainer):
            if not widget.isVisible():
                return
            available_width = max(1, self.width() - 2 * padding)
            content_width = max(widget.sizeHint().width(), 420)
            desired_width = max(525, int(content_width * 1.25))
            width = min(available_width, min(950, desired_width))
            height = (
                widget.heightForWidth(width)
                if widget.hasHeightForWidth()
                else widget.sizeHint().height()
            )
            height = max(1, min(height, self.height() - 2 * padding))
            widget.setGeometry(
                (self.width() - width) // 2,
                max(padding, (self.height() - height) // 2),
                width,
                height,
            )
        else:
            original_update(self, widget, centered, padding)

    main_window_class._update_overlay_geometry = center_overlays

    app = getattr(objects, 'qapp', None)
    if app is None:
        return
    for window in app.topLevelWidgets():
        if not isinstance(window, main_window_class):
            continue
        if getattr(window, '_qute_centered_overlay_signals_connected', False):
            continue
        for widget, signal, centered, padding in window._overlays:
            signal.connect(partial(
                window._update_overlay_geometry, widget, centered, padding,
            ))
        window._qute_centered_overlay_signals_connected = True
        window._update_overlay_geometries()


def _install_omnibar():
    from functools import partial

    from qutebrowser.config import stylesheet
    from qutebrowser.mainwindow.statusbar import bar
    from qutebrowser.qt.core import Qt
    from qutebrowser.qt.widgets import QHBoxLayout, QWidget
    from qutebrowser.misc import objects

    def ensure_omnibar(statusbar):
        omnibar = getattr(statusbar, '_qute_omnibar', None)
        if omnibar is not None:
            return omnibar

        main_window = statusbar.parentWidget()
        omnibar = QWidget(main_window)
        omnibar._qute_omnibar_widget = True
        omnibar.setObjectName('QuteOmnibar')
        omnibar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        layout = QHBoxLayout(omnibar)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(0)
        statusbar.cmd.setMinimumHeight(statusbar.cmd.sizeHint().height())
        statusbar.cmd._qute_original_stylesheet = statusbar.cmd.styleSheet()
        stylesheet.set_register(statusbar.cmd, statusbar.cmd._qute_original_stylesheet + """
            QLineEdit {
                color: {{ conf.colors.statusbar.command.fg }};
                font: {{ conf.fonts.statusbar }};
            }
        """)
        stylesheet.set_register(omnibar, """
            QWidget#QuteOmnibar {
                background-color: {{ conf.colors.statusbar.command.bg }};
                color: {{ conf.colors.statusbar.command.fg }};
                font: {{ conf.fonts.statusbar }};
                border: 1px solid {{ conf.colors.prompts.border }};
            }
            QWidget#QuteOmnibar QLineEdit {
                color: {{ conf.colors.statusbar.command.fg }};
                font: {{ conf.fonts.statusbar }};
            }
        """)

        statusbar._stack.removeWidget(statusbar.cmd)
        statusbar._stack.setCurrentWidget(statusbar.txt)
        layout.addWidget(statusbar.cmd)
        omnibar.setMinimumHeight(statusbar.cmd.sizeHint().height() + 18)
        statusbar._qute_omnibar = omnibar

        completion_overlay = next(
            index for index, (widget, _signal, _centered, _padding)
            in enumerate(main_window._overlays)
            if widget is main_window._completion
        )
        main_window._overlays.insert(completion_overlay, (
            omnibar, main_window._completion.update_geometry, True, 12,
        ))
        main_window._completion.update_geometry.connect(partial(
            main_window._update_overlay_geometry, omnibar, True, 12,
        ))
        return omnibar

    def show_omnibar(statusbar):
        omnibar = ensure_omnibar(statusbar)
        if statusbar.cmd.parentWidget() is not omnibar:
            statusbar._stack.removeWidget(statusbar.cmd)
            statusbar._stack.setCurrentWidget(statusbar.txt)
            omnibar.layout().addWidget(statusbar.cmd)
        omnibar.show()
        omnibar.raise_()
        statusbar.cmd.show()
        statusbar.cmd.setFocus()
        statusbar.parentWidget()._update_overlay_geometry(omnibar, True, 12)

    def restore_command(statusbar):
        omnibar = getattr(statusbar, '_qute_omnibar', None)
        if omnibar is None or statusbar.cmd.parentWidget() is not omnibar:
            return
        omnibar.layout().removeWidget(statusbar.cmd)
        statusbar.cmd.hide()
        statusbar.cmd.setParent(statusbar)
        statusbar._stack.addWidget(statusbar.cmd)
        statusbar._stack.setCurrentWidget(statusbar.txt)
        omnibar.hide()

    statusbar_class = bar.StatusBar
    if not hasattr(statusbar_class, '_qute_original_show_cmd_widget'):
        statusbar_class._qute_original_show_cmd_widget = statusbar_class._show_cmd_widget
        statusbar_class._qute_original_hide_cmd_widget = statusbar_class._hide_cmd_widget

    original_show = statusbar_class._qute_original_show_cmd_widget
    original_hide = statusbar_class._qute_original_hide_cmd_widget

    def show_cmd_widget(self):
        omnibar = getattr(self, '_qute_omnibar', None)
        if omnibar is None or self.cmd.parentWidget() is not omnibar:
            original_show(self)
        show_omnibar(self)

    def hide_cmd_widget(self):
        original_hide(self)
        restore_command(self)

    statusbar_class._show_cmd_widget = show_cmd_widget
    statusbar_class._hide_cmd_widget = hide_cmd_widget

    app = getattr(objects, 'qapp', None)
    if app is None:
        return
    for window in app.topLevelWidgets():
        if not isinstance(window, mainwindow.MainWindow):
            continue
        statusbar = window.status
        if getattr(statusbar, '_qute_omnibar_signals_connected', False):
            continue
        statusbar.cmd.show_cmd.connect(partial(show_omnibar, statusbar))
        statusbar.cmd.hide_cmd.connect(partial(restore_command, statusbar))
        statusbar._qute_omnibar_signals_connected = True
        if statusbar._stack.currentWidget() is statusbar.cmd:
            show_omnibar(statusbar)


def _install_title_cleanup():
    tabwidget.TabWidget.MUTE_STRING = ''
    tabwidget.TabWidget.AUDIBLE_STRING = ''

    # Match Quickshell's title suffix cleanup before qutebrowser formats tabs.
    window_title_clean_patterns = (
        '- Vivaldi', '- qutebrowser', '- FreeTube', '- YouTube',
        '- Google Search', '- Twitch', '- Microsoft Azure',
    )

    # Keep the original method across :config-source reloads.
    if not hasattr(tabwidget.TabWidget, '_original_get_tab_fields'):
        tabwidget.TabWidget._original_get_tab_fields = tabwidget.TabWidget.get_tab_fields

    def clean_tab_title_fields(
        self, idx,
        original=tabwidget.TabWidget._original_get_tab_fields,
        patterns=window_title_clean_patterns,
    ):
        fields = original(self, idx)
        title = fields['current_title']
        for pattern in patterns:
            title = title.removesuffix(f' {pattern}')
        fields['current_title'] = title
        fields['title_sep'] = ' - ' if title else ''
        return fields

    tabwidget.TabWidget.get_tab_fields = clean_tab_title_fields


def _install_popup_fixes():
    # Give menu text its own padding rather than relying on the desktop Qt style.
    if not hasattr(mainwindow.MainWindow, '_original_popup_stylesheet'):
        mainwindow.MainWindow._original_popup_stylesheet = mainwindow.MainWindow.STYLESHEET
    mainwindow.MainWindow.STYLESHEET = mainwindow.MainWindow._original_popup_stylesheet + """
        QMenu { padding: 4px; }
        QMenu::item { padding: 6px 24px; }
    """

    if not hasattr(prompt.PromptContainer, '_original_popup_stylesheet'):
        prompt.PromptContainer._original_popup_stylesheet = prompt.PromptContainer.STYLESHEET
    prompt.PromptContainer.STYLESHEET = prompt.PromptContainer._original_popup_stylesheet + """
        QWidget#PromptContainer { border: {{ conf.colors.prompts.border }}; }
        QLineEdit {
            selection-background-color: {{ conf.colors.prompts.selected.bg }};
            selection-color: {{ conf.colors.prompts.selected.fg }};
        }
        QWidget#PromptContainer[overwritePrompt="true"] {
            border: 2px solid {{ conf.colors.messages.warning.fg }};
        }
        QLabel#OverwritePromptTitle { color: {{ conf.colors.messages.warning.fg }}; }
    """

    if not hasattr(prompt.PromptContainer, '_original_show_prompts'):
        prompt.PromptContainer._original_show_prompts = prompt.PromptContainer._on_show_prompts

    def _show_clean_prompt(
        self, question,
        original=prompt.PromptContainer._original_show_prompts,
    ):
        previous = self._prompt
        original(self, question)
        # Work around qutebrowser #8993: the previous save prompt can leave remnants.
        if previous is not None and previous is not self._prompt and not sip.isdeleted(previous):
            previous.hide()
            previous.setParent(None)

        overwrite = question is not None and question.title in (
            'Overwrite existing file?', 'Overwrite special file?',
        )
        self.setProperty('overwritePrompt', overwrite)
        if overwrite:
            title_label = self._prompt._vbox.itemAt(0).widget()
            title_label.setObjectName('OverwritePromptTitle')
            title_label.style().unpolish(title_label)
            title_label.style().polish(title_label)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update_geometry.emit()
        self.update()
        if self.parentWidget() is not None:
            self.parentWidget().update()

    prompt.PromptContainer._on_show_prompts = _show_clean_prompt


def _install_fullscreen_notice(accent, font_family):
    _fullscreen_base = getattr(
        miscwidgets.FullscreenNotification,
        '_qute_original_class',
        miscwidgets.FullscreenNotification,
    )

    class _ThemedFullscreenNotification(_fullscreen_base):
        _qute_original_class = _fullscreen_base
        _theme_stylesheet = f"""
            background-color: rgba(0, 0, 0, 128);
            color: {accent};
            border: none;
            border-radius: 16px;
            padding: 14px;
            font-family: "{font_family}";
            font-size: 12px;
            font-weight: bold;
        """

        def setStyleSheet(self, stylesheet):
            super().setStyleSheet(self._theme_stylesheet)

    miscwidgets.FullscreenNotification = _ThemedFullscreenNotification


def _install_rbw():
    from pathlib import Path
    from runpy import run_path

    run_path(str(Path(__file__).with_name("rbw.py")))["install"]()
