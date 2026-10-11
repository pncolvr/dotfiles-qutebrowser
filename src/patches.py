"""Reload-safe customizations of qutebrowser widgets.

These use qutebrowser internals; check them after browser upgrades.
"""

from qutebrowser.mainwindow import mainwindow, prompt, tabwidget
from qutebrowser.misc import miscwidgets
from qutebrowser.qt import sip


def apply(palette):
    _install_title_cleanup()
    _install_popup_fixes()
    _install_fullscreen_notice(palette['ACCENT'])


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


def _install_fullscreen_notice(accent):
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
            font-family: "Noto Sans Mono";
            font-size: 12px;
            font-weight: bold;
        """

        def setStyleSheet(self, stylesheet):
            super().setStyleSheet(self._theme_stylesheet)

    miscwidgets.FullscreenNotification = _ThemedFullscreenNotification
