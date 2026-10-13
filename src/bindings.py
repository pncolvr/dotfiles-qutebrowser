"""Keybindings grouped by purpose."""


def apply(config, paths):
    home = paths.home
    default_page = paths.default_page

    # Navigation, tabs, and sessions
    config.bind('h', 'back')
    config.bind('l', 'forward')
    config.bind('H', 'scroll left')
    config.bind('L', 'scroll right')
    config.bind('o', 'cmd-set-text -s :open')
    config.bind('!', 'cmd-set-text -s :open !')
    # config.bind('b', 'cmd-set-text -s :quickmark-load -t')
    # config.bind('B', 'cmd-set-text -s :quickmark-load')
    config.bind('<Ctrl-l>', 'cmd-set-text :open {url:pretty}')
    config.bind('<Ctrl-t>', 'cmd-set-text -s :open -t ')
    config.bind(',co', 'tab-only')
    config.bind(',pp', 'open -t -- {clipboard}')
    config.bind(',gH', f'open {default_page}')
    config.bind(',w', 'session-save')

    # Search and translation
    config.bind(',sd', 'open -t !da {primary}')
    config.bind(',tg', 'open -t https://translate.google.com/'
                      '?sl=pt-PT&tl=es&text={primary}&op=translate')
    config.bind('<Ctrl-F>', 'cmd-set-text /')

    # Downloads and exports
    config.unbind('d')
    config.bind('dc', 'download-clear')
    config.bind('do', 'download-open')
    
    # Toggle prompting and the destination together; defaults are in settings.py.
    config.bind('dp', 'config-cycle downloads.location.prompt ;; '
                      'config-cycle downloads.location.directory '
                      f'{home}/Downloads {home}/Downloads/mods_download')
    config.bind(',ss', ':screenshot ~/Pictures/qutebrowser/{date}.png')
    config.bind(',sS', ':print --pdf ~/Pictures/qutebrowser/{date}.pdf')
    config.bind(',cc', 'spawn --userscript certificate')

    # URLs and media
    config.bind(',yy', 'spawn --userscript clean_url')
    config.bind(',yY', 'hint links userscript clean_url')
    config.bind(',YY', 'spawn --userscript select_urls')
    # Packaged alternative, kept for a later retry:
    # config.bind(',mm', 'spawn --userscript view_in_mpv --force-window=immediate')
    config.bind(',mm', 'spawn --userscript to_mpv')
    config.bind(',MM', 'spawn --userscript download')
    # config.bind(',mM', 'hint links userscript view_in_mpv --force-window=immediate')
    config.bind(',mM', 'hint links userscript to_mpv')

    # Userscripts (custom reader wrappers keep output in temporary storage)
    config.bind(',qr', 'spawn --userscript qr')
    config.bind(',rr', 'spawn --userscript readability-js')

    # Page scripts
    config.bind(',mo', 'spawn --userscript mono')
    config.bind(',ui', 'spawn --userscript unlockinsta')
    config.bind(',gh', 'spawn --userscript home')
    config.bind('D', 'spawn --userscript darkreader toggle domain')
    config.bind(',gr', 'spawn --userscript apply_custom')

    # Browser controls
    config.bind('<F12>', 'devtools')
    config.bind('<Ctrl+b>', 'config-cycle statusbar.show never always')
    config.bind(',cs', ':config-source')
