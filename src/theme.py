"""Custom qutebrowser UI theme matching Quickshell Theme.qml and Hyprland."""

BACKGROUND = '#000000'
SURFACE = '#1b1a1a'
TEXT = '#d8dadc'
INACTIVE = '#b0b3b8'
MUTED = '#62666b'
BORDER = '#2a2d38'
ACCENT = '#6b8fb3'
URGENT = '#b80f0a'
OK = '#3e8e5a'
ACTIVE = '#5c9e7e'
WARNING = '#fd6d37'


def apply(c, paths):
    # Fonts, webpage background, and scrollbars.
    c.scrolling.bar = 'overlay'
    c.content.user_stylesheets = [paths.stylesheet]
    c.tabs.padding = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
    c.colors.webpage.bg = '#1e1e1e'
    c.fonts.default_family = ['Noto Sans Mono']
    c.fonts.default_size = '10pt'
    c.fonts.web.family.fixed = 'JetBrains Mono'
    c.fonts.web.family.sans_serif = 'JetBrains Mono'
    c.fonts.web.family.serif = 'JetBrains Mono'
    c.fonts.web.family.standard = 'JetBrains Mono'
    c.fonts.tabs.selected = '9pt JetBrains Mono'
    c.fonts.tabs.unselected = 'bold 8pt Noto Sans Mono'
    c.colors.webpage.darkmode.enabled = True
    c.colors.webpage.darkmode.policy.images = 'never'
    c.colors.webpage.preferred_color_scheme = 'dark'

    # Completion: quiet rows, clear section headers, and a subtle blue selection.
    c.completion.height = '35%'
    c.completion.shrink = True
    # Reserve a fixed strip for the animated thumb in src/scrollbars.py.
    c.completion.scrollbar.width = 20
    c.completion.scrollbar.padding = 0
    c.colors.completion.category.bg = BACKGROUND
    c.colors.completion.category.fg = ACCENT
    c.colors.completion.category.border.top = BACKGROUND
    c.colors.completion.category.border.bottom = BACKGROUND
    c.colors.completion.even.bg = BACKGROUND
    c.colors.completion.odd.bg = BACKGROUND
    c.colors.completion.fg = TEXT
    c.colors.completion.match.fg = ACCENT
    c.colors.completion.item.selected.bg = BORDER
    c.colors.completion.item.selected.fg = TEXT
    c.colors.completion.item.selected.border.top = ACCENT
    c.colors.completion.item.selected.border.bottom = ACCENT
    c.colors.completion.item.selected.match.fg = ACCENT
    c.colors.completion.scrollbar.bg = 'transparent'
    c.colors.completion.scrollbar.fg = ACCENT

    # Downloads and navigation hints.
    c.colors.downloads.bar.bg = BACKGROUND
    c.colors.downloads.start.bg = BACKGROUND
    c.colors.downloads.start.fg = ACCENT
    c.colors.downloads.stop.bg = BACKGROUND
    c.colors.downloads.stop.fg = ACTIVE
    c.colors.downloads.error.bg = URGENT
    c.colors.downloads.error.fg = TEXT
    c.colors.downloads.system.bg = 'none'
    c.colors.downloads.system.fg = 'none'
    c.colors.hints.bg = ACCENT
    c.colors.hints.fg = BACKGROUND
    c.colors.hints.match.fg = TEXT
    c.hints.border = '1px solid ' + ACCENT
    c.colors.keyhint.bg = SURFACE
    c.colors.keyhint.fg = TEXT
    c.colors.keyhint.suffix.fg = ACCENT

    # Messages, prompts, tooltips, and context menus.
    c.colors.messages.error.bg = URGENT
    c.colors.messages.error.fg = TEXT
    c.colors.messages.error.border = URGENT
    c.colors.messages.warning.bg = SURFACE
    c.colors.messages.warning.fg = WARNING
    c.colors.messages.warning.border = WARNING
    c.colors.messages.info.bg = SURFACE
    c.colors.messages.info.fg = TEXT
    c.colors.messages.info.border = BORDER
    c.colors.prompts.bg = SURFACE
    c.colors.prompts.fg = TEXT
    c.colors.prompts.border = '1px solid ' + BORDER
    c.colors.prompts.selected.bg = ACCENT
    c.colors.prompts.selected.fg = TEXT
    c.colors.tooltip.bg = BACKGROUND
    c.colors.tooltip.fg = TEXT
    c.colors.contextmenu.menu.bg = SURFACE
    c.colors.contextmenu.menu.fg = TEXT
    c.colors.contextmenu.disabled.bg = SURFACE
    c.colors.contextmenu.disabled.fg = MUTED
    c.colors.contextmenu.selected.bg = ACCENT
    c.colors.contextmenu.selected.fg = TEXT
    c.fonts.contextmenu = '10pt Noto Sans Mono'
    c.fonts.prompts = '10pt Noto Sans Mono'

    # Insert, passthrough, and caret use accent backgrounds with white text.
    # Keep command entry on a black background.
    c.colors.statusbar.normal.bg = BACKGROUND
    c.colors.statusbar.normal.fg = TEXT
    c.colors.statusbar.command.bg = BACKGROUND
    c.colors.statusbar.command.fg = '#ffffff'
    c.colors.statusbar.insert.bg = ACTIVE
    c.colors.statusbar.insert.fg = '#ffffff'
    c.colors.statusbar.passthrough.bg = WARNING
    c.colors.statusbar.passthrough.fg = '#ffffff'
    c.colors.statusbar.caret.bg = ACCENT
    c.colors.statusbar.caret.fg = '#ffffff'
    c.colors.statusbar.caret.selection.bg = ACCENT
    c.colors.statusbar.caret.selection.fg = '#ffffff'
    c.colors.statusbar.private.bg = SURFACE
    c.colors.statusbar.private.fg = TEXT
    c.colors.statusbar.command.private.bg = BACKGROUND
    c.colors.statusbar.command.private.fg = '#ffffff'
    c.colors.statusbar.progress.bg = ACCENT
    c.colors.statusbar.url.fg = TEXT
    c.colors.statusbar.url.hover.fg = ACCENT
    c.colors.statusbar.url.success.http.fg = TEXT
    c.colors.statusbar.url.success.https.fg = TEXT
    c.colors.statusbar.url.warn.fg = WARNING
    c.colors.statusbar.url.error.fg = WARNING

    # Active tabs use the accent background, including pinned tabs.
    c.colors.tabs.bar.bg = BACKGROUND
    c.colors.tabs.even.bg = BACKGROUND
    c.colors.tabs.odd.bg = BACKGROUND
    c.colors.tabs.even.fg = INACTIVE
    c.colors.tabs.odd.fg = INACTIVE
    c.colors.tabs.selected.even.bg = ACCENT
    c.colors.tabs.selected.odd.bg = ACCENT
    c.colors.tabs.selected.even.fg = BACKGROUND
    c.colors.tabs.selected.odd.fg = BACKGROUND
    c.colors.tabs.pinned.even.bg = BACKGROUND
    c.colors.tabs.pinned.odd.bg = BACKGROUND
    c.colors.tabs.pinned.even.fg = INACTIVE
    c.colors.tabs.pinned.odd.fg = INACTIVE
    c.colors.tabs.pinned.selected.even.bg = ACCENT
    c.colors.tabs.pinned.selected.odd.bg = ACCENT
    c.colors.tabs.pinned.selected.even.fg = BACKGROUND
    c.colors.tabs.pinned.selected.odd.fg = BACKGROUND
    c.colors.tabs.indicator.start = ACCENT
    c.colors.tabs.indicator.stop = OK
    c.colors.tabs.indicator.error = URGENT
    c.colors.tabs.indicator.system = 'none'
