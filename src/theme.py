"""Custom qutebrowser UI theme matching Quickshell Theme.qml and Hyprland."""

from pathlib import Path

from qutebrowser.utils import standarddir

BACKGROUND = '#000000'
SURFACE = '#1b1a1a'
MESSAGE_BG = BACKGROUND
TEXT = '#d8dadc'
INACTIVE = '#b0b3b8'
MUTED = '#62666b'
BORDER = '#2a2d38'
ACCENT = '#6b8fb3'
URGENT = '#b80f0a'
OK = '#3e8e5a'
ACTIVE = '#5c9e7e'
WARNING = '#fd6d37'
FONT_FAMILY = 'Noto Sans Mono'
FONT_SIZE = '10pt'
FONT_REGULAR = f'{FONT_SIZE} {FONT_FAMILY}'
FONT_BOLD = f'bold {FONT_REGULAR}'
FONT_TAB_SELECTED = f'9pt {FONT_FAMILY}'
FONT_TAB_UNSELECTED = f'bold 8pt {FONT_FAMILY}'
PROFILE_BACKGROUNDS = {
    'webapp': '#1b2a3a',
    'hobby': '#30243d',
}


def apply(c):
    # Fonts and webpage background.
    c.tabs.padding = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
    c.colors.webpage.bg = '#1e1e1e'
    c.fonts.default_family = [FONT_FAMILY]
    c.fonts.default_size = FONT_SIZE
    c.fonts.web.family.fixed = FONT_FAMILY
    c.fonts.web.family.sans_serif = FONT_FAMILY
    c.fonts.web.family.serif = FONT_FAMILY
    c.fonts.web.family.standard = FONT_FAMILY
    c.fonts.tabs.selected = FONT_TAB_SELECTED
    c.fonts.tabs.unselected = FONT_TAB_UNSELECTED
    c.colors.webpage.darkmode.enabled = False
    c.colors.webpage.darkmode.policy.images = 'never'
    c.colors.webpage.preferred_color_scheme = 'dark'

    # Completion: quiet rows, clear section headers, and a subtle blue selection.
    c.completion.height = '35%'
    c.completion.shrink = True
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
    c.colors.messages.error.bg = MESSAGE_BG
    c.colors.messages.error.fg = URGENT
    c.colors.messages.error.border = BORDER
    c.colors.messages.warning.bg = MESSAGE_BG
    c.colors.messages.warning.fg = WARNING
    c.colors.messages.warning.border = BORDER
    c.colors.messages.info.bg = MESSAGE_BG
    c.colors.messages.info.fg = TEXT
    c.colors.messages.info.border = BORDER
    for level in ('error', 'warning', 'info'):
        setattr(c.fonts.messages, level, FONT_BOLD)
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
    c.fonts.contextmenu = FONT_REGULAR
    c.fonts.prompts = FONT_REGULAR

    # --basedir profiles store their configuration in a config/ subdirectory.
    profile_dir = Path(standarddir.config())
    if profile_dir.name == 'config':
        profile_dir = profile_dir.parent
    profile = profile_dir.name.removeprefix('qutebrowser-')
    if profile == 'qutebrowser':
        profile = 'default'
    c.statusbar.widgets = [
        'keypress', 'search_match', 'url', 'scroll', 'history', 'tabs', 'progress',
        f'text:{profile}',
    ]

    # Insert, passthrough, and caret use accent backgrounds with white text.
    # Keep command entry on a black background.
    c.colors.statusbar.normal.bg = PROFILE_BACKGROUNDS.get(profile, BACKGROUND)
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
