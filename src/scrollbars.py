"""Quickshell scrollbar geometry and input policy for qutebrowser's Qt UI.

Webpage thumbs live in the shared scrollbars.js userscript. Qt receives wheel
phases before Chromium does, so momentum filtering belongs here as well.
"""

from qutebrowser.qt.core import (
    QCoreApplication, QEvent, QObject, QPoint, QRectF, QSize, Qt, QTimer,
    QVariantAnimation, QEasingCurve,
)
from qutebrowser.qt.gui import QColor, QPainter, QWheelEvent
from qutebrowser.qt.widgets import QApplication, QAbstractItemView, QScrollBar

GUTTER = 20
WIDTH = 6
HOVER_WIDTH = 10
MINIMUM = 24
GROW_DURATION = 120
HIDE_DELAY = 450
FADE_DURATION = 200


class ScrollBar(QScrollBar):
    """Keep QScrollBar's range/accessibility, paint an animated centered thumb."""

    def __init__(self, orientation, parent=None, *, accent='#6b8fb3'):
        super().__init__(orientation, parent)
        self.accent = QColor(accent)
        self.motion_enabled = True
        self._thickness = float(WIDTH)
        self._opacity = 0.0
        self._viewport_hover = False
        self._bar_hover = False
        self._drag_offset = None
        self._hold = QTimer(self)
        self._hold.setSingleShot(True)
        self._hold.setInterval(HIDE_DELAY)
        self._hold.timeout.connect(self._fade)
        self._grow = QVariantAnimation(self)
        self._grow.setDuration(GROW_DURATION)
        self._grow.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._grow.valueChanged.connect(self._set_thickness)
        self._fade_animation = QVariantAnimation(self)
        self._fade_animation.setDuration(FADE_DURATION)
        self._fade_animation.valueChanged.connect(self._set_opacity)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.valueChanged.connect(self._activity)
        self.rangeChanged.connect(self._range_changed)

    def sizeHint(self):
        return QSize(GUTTER, MINIMUM) if self.orientation() == Qt.Orientation.Vertical else QSize(MINIMUM, GUTTER)

    def minimumSizeHint(self):
        return self.sizeHint()

    def _set_thickness(self, value):
        self._thickness = float(value)
        self.update()

    def _set_opacity(self, value):
        self._opacity = float(value)
        self.update()

    def _animate(self, animation, current, destination, setter):
        animation.stop()
        if not self.motion_enabled:
            setter(destination)
            return
        animation.setStartValue(current)
        animation.setEndValue(destination)
        animation.start()

    def set_motion_enabled(self, enabled):
        self.motion_enabled = enabled
        if not enabled:
            for animation, setter in ((self._grow, self._set_thickness), (self._fade_animation, self._set_opacity)):
                if animation.state() == QVariantAnimation.State.Running:
                    destination = animation.endValue()
                    animation.stop()
                    setter(destination)

    def _active(self):
        return self._bar_hover or self._drag_offset is not None

    def _activity(self, *_args):
        self._fade_animation.stop()
        self._set_opacity(1.0)
        self._hold.start()

    def _fade(self):
        if not self._active():
            self._animate(self._fade_animation, self._opacity, 0.0, self._set_opacity)

    def set_viewport_hover(self, hovered):
        self._viewport_hover = hovered
        self._activity()

    def _range_changed(self, minimum, maximum):
        if maximum <= minimum:
            self._hold.stop()
            self._fade_animation.stop()
            self._set_opacity(0.0)
        else:
            self._activity()

    def thumb_rect(self):
        vertical = self.orientation() == Qt.Orientation.Vertical
        length = self.height() if vertical else self.width()
        cross = self.width() if vertical else self.height()
        span = self.maximum() - self.minimum()
        thumb = min(length, max(MINIMUM, length * self.pageStep() / max(1, span + self.pageStep())))
        fraction = (self.value() - self.minimum()) / max(1, span)
        if not vertical and self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            fraction = 1 - fraction
        start = fraction * (length - thumb)
        inset = (cross - self._thickness) / 2
        return QRectF(inset, start, self._thickness, thumb) if vertical else QRectF(start, inset, thumb, self._thickness)

    def paintEvent(self, _event):
        if self.maximum() <= self.minimum() or self._opacity <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(self.accent)
        color.setAlphaF(self._opacity)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(self.thumb_rect(), 3, 3)

    def _hover(self, point):
        vertical = self.orientation() == Qt.Orientation.Vertical
        cross = point.x() if vertical else point.y()
        center = (self.width() if vertical else self.height()) / 2
        hovered = abs(cross - center) <= self._thickness / 2
        self._bar_hover = hovered
        wide = hovered or self._drag_offset is not None
        destination = float(HOVER_WIDTH if wide else WIDTH)
        if self._grow.endValue() != destination or self._grow.state() != QVariantAnimation.State.Running:
            if self._thickness != destination:
                self._animate(self._grow, self._thickness, destination, self._set_thickness)
        self._activity()

    def enterEvent(self, event):
        self._hover(event.position())

    def leaveEvent(self, _event):
        self._bar_hover = False
        if self._drag_offset is None:
            self._animate(self._grow, self._thickness, float(WIDTH), self._set_thickness)
        self._activity()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        rect = self.thumb_rect()
        vertical = self.orientation() == Qt.Orientation.Vertical
        point = event.position().y() if vertical else event.position().x()
        start = rect.top() if vertical else rect.left()
        length = rect.height() if vertical else rect.width()
        self._drag_offset = point - start if rect.contains(event.position()) else length / 2
        self.setSliderDown(True)
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        self._animate(self._grow, self._thickness, float(HOVER_WIDTH), self._set_thickness)
        self._activity()
        if not rect.contains(event.position()):
            self._seek(point)
        event.accept()

    def _seek(self, point):
        rect = self.thumb_rect()
        vertical = self.orientation() == Qt.Orientation.Vertical
        travel = (self.height() - rect.height()) if vertical else (self.width() - rect.width())
        fraction = min(1, max(0, (point - self._drag_offset) / max(1, travel)))
        if not vertical and self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            fraction = 1 - fraction
        self.setValue(round(self.minimum() + fraction * (self.maximum() - self.minimum())))

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None:
            self._seek(event.position().y() if self.orientation() == Qt.Orientation.Vertical else event.position().x())
        else:
            self._hover(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self._drag_offset is None:
            return super().mouseReleaseEvent(event)
        self._drag_offset = None
        self.setSliderDown(False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        if not self.rect().contains(event.position().toPoint()):
            self.leaveEvent(event)
        else:
            self._hover(event.position())
        self._activity()
        event.accept()

    def hideEvent(self, _event):
        self._drag_offset = None
        self._bar_hover = False
        self._viewport_hover = False
        self.setSliderDown(False)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._hold.stop()
        self._grow.stop()
        self._fade_animation.stop()
        self._set_thickness(float(WIDTH))
        self._set_opacity(0.0)


class ViewHover(QObject):
    def __init__(self, view, bars):
        super().__init__(view)
        self.bars = bars
        view.installEventFilter(self)

    def eventFilter(self, _obj, event):
        if event.type() in (QEvent.Type.Enter, QEvent.Type.Leave):
            for bar in self.bars:
                bar.set_viewport_hover(event.type() == QEvent.Type.Enter)
        return False


class WheelPolicy(QObject):
    """Drop momentum and normalize mouse ticks before Chromium loses Qt phases."""

    def __init__(self, parent):
        super().__init__(parent)
        self._forwarding = False

    def eventFilter(self, obj, event):
        if event.type() != QEvent.Type.Wheel or self._forwarding:
            return False
        # Restrict this policy to page views and our completion scrollbars.
        widget = obj
        while widget is not None:
            if widget.property('quickshellScrollInput'):
                break
            widget = widget.parent()
        if widget is None or event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            return False
        if event.phase() == Qt.ScrollPhase.ScrollMomentum:
            event.accept()
            return True
        if event.pixelDelta().isNull() and event.angleDelta().isNull():
            return False
        delta = event.angleDelta()
        pixels = event.pixelDelta()
        if pixels.isNull():
            pixels = QPoint(round(delta.x() / 120 * 40), round(delta.y() / 120 * 40))
        webengine = widget.inherits('QWebEngineView')
        if isinstance(widget, QAbstractItemView):
            horizontal, vertical = widget.horizontalScrollBar(), widget.verticalScrollBar()
            dx, dy = pixels.x(), pixels.y()
            can_horizontal = (horizontal.maximum() > horizontal.minimum() and
                              widget.horizontalScrollBarPolicy() != Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            if can_horizontal and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier or
                                   vertical.maximum() == vertical.minimum()):
                dx, dy = dx or dy, 0
            before = (horizontal.value(), vertical.value())
            if can_horizontal:
                direction = 1 if widget.layoutDirection() == Qt.LayoutDirection.RightToLeft else -1
                horizontal.setValue(horizontal.value() + direction * dx)
            vertical.setValue(vertical.value() - dy)
            event.setAccepted(before != (horizontal.value(), vertical.value()))
            return True
        if not webengine and not event.pixelDelta().isNull():
            return False
        # QtWebEngine's WebEventFactory ignores pixelDelta and derives pixels
        # from angleDelta using wheelScrollLines * 20px per 120 angle units.
        # Preserve precise touchpad deltas through that conversion too.
        angle = QPoint()
        if webengine:
            factor = 120 / (max(1, QApplication.wheelScrollLines()) * 20)
            angle = QPoint(round(pixels.x() * factor), round(pixels.y() * factor))
        forwarded = QWheelEvent(
            event.position(), event.globalPosition(),
            pixels, angle, event.buttons(), event.modifiers(), event.phase(), event.inverted(),
            Qt.MouseEventSource.MouseEventSynthesizedByApplication, event.pointingDevice(),
        )
        self._forwarding = True
        try:
            QCoreApplication.sendEvent(obj, forwarded)
        finally:
            self._forwarding = False
        event.setAccepted(forwarded.isAccepted())
        return True


def attach(view, accent):
    _ensure_policy()
    if hasattr(view, '_quickshell_scrollbars'):
        for bar in view._quickshell_scrollbars:
            bar.accent = QColor(accent)
            bar.update()
        return
    bars = []
    for orientation in (Qt.Orientation.Vertical, Qt.Orientation.Horizontal):
        bar = ScrollBar(orientation, accent=accent)
        if orientation == Qt.Orientation.Vertical:
            view.setVerticalScrollBar(bar)
        else:
            view.setHorizontalScrollBar(bar)
        bars.append(bar)
    view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setProperty('quickshellScrollInput', True)
    view._quickshell_scrollbars = bars
    view._quickshell_scroll_hover = ViewHover(view, bars)


def _ensure_policy():
    app = QApplication.instance()
    if app is not None and not hasattr(app, '_quickshell_wheel_policy'):
        app._quickshell_wheel_policy = WheelPolicy(app)
        app.installEventFilter(app._quickshell_wheel_policy)


def install(accent):
    from qutebrowser.completion import completionwidget
    from qutebrowser.browser.webengine import webview

    app = QApplication.instance()
    _ensure_policy()

    cls = completionwidget.CompletionView
    original = getattr(cls, '_quickshell_original_init', cls.__init__)
    cls._quickshell_original_init = original

    def init(self, *args, **kwargs):
        original(self, *args, **kwargs)
        attach(self, accent)

    cls.__init__ = init
    # Existing windows are updated on :config-source; constructors stay unstacked.
    for widget in app.allWidgets() if app is not None else ():
        if isinstance(widget, cls):
            attach(widget, accent)
        elif isinstance(widget, webview.WebEngineView):
            widget.setProperty('quickshellScrollInput', True)

    web_cls = webview.WebEngineView
    web_original = getattr(web_cls, '_quickshell_original_init', web_cls.__init__)
    web_cls._quickshell_original_init = web_original

    def web_init(self, *args, **kwargs):
        web_original(self, *args, **kwargs)
        _ensure_policy()
        self.setProperty('quickshellScrollInput', True)

    web_cls.__init__ = web_init
