"""Keybindings grouped by purpose."""


def apply(config, paths):
    home = paths.home
    scripts_folder = paths.scripts
    default_page = paths.default_page

    # Navigation, tabs, and sessions
    config.bind('h', 'back')
    config.bind('l', 'forward')
    config.bind('H', 'scroll left')
    config.bind('L', 'scroll right')
    config.bind('o', 'cmd-set-text -s :open')
    config.bind('!', 'cmd-set-text -s :open !')
    config.bind('b', 'cmd-set-text -s :quickmark-load -t')
    config.bind('B', 'cmd-set-text -s :quickmark-load')
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
    config.bind(',cc', f'spawn /usr/bin/ghostty -e {scripts_folder}/hold.sh '
                      f'{scripts_folder}/certificate.sh {{url}}')

    # URLs and media
    config.bind(',yy', f'spawn --userscript {scripts_folder}/url/clean.sh {{url}}')
    config.bind(',yY', f'hint links spawn --userscript {scripts_folder}/url/clean.sh {{hint-url}}')
    config.bind(',YY', f'spawn --userscript {scripts_folder}/url/select.sh')
    config.bind(',mm', 'spawn --userscript '
                      '~/.config/quickshell/src/services/launcher/launcher.sh '
                      'provider media "{title}" "{url}"')
    config.bind(',MM', f'spawn /usr/bin/ghostty -e {scripts_folder}/hold.sh '
                      f'{scripts_folder}/download.sh {{url}}')
    config.bind(',mM', 'hint links spawn --userscript '
                      '~/.config/quickshell/src/services/launcher/launcher.sh '
                      'provider media "{title}" "{hint-url}"')

    # Page scripts
    config.bind(',mo', f'jseval -f {scripts_folder}/js/mono.js')
    config.bind(',ui', f'jseval -f {scripts_folder}/js/unlockinsta.js')
    config.bind(',gh', f'jseval -f {scripts_folder}/js/home.js')
    config.bind('D', f'spawn --userscript {scripts_folder}/python/darkreader.py '
                    'toggle domain')
    config.bind(',gr', f'spawn --userscript {scripts_folder}/custom/apply.sh ;; '
                      'greasemonkey-reload ;; reload')

    # Browser controls
    config.bind('<F12>', 'devtools')
    config.bind('<Ctrl+b>', 'config-cycle statusbar.show never always')
    config.bind(',cs', ':config-source')
