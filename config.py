import os
from urllib.request import urlopen
from qutebrowser.mainwindow import tabwidget

config.load_autoconfig(True)

if not os.path.exists(config.configdir / "theme.py"):
    theme = "https://raw.githubusercontent.com/catppuccin/qutebrowser/main/setup.py"
    with urlopen(theme) as themehtml:
        with open(config.configdir / "theme.py", "a") as file:
            file.writelines(themehtml.read().decode("utf-8"))

if os.path.exists(config.configdir / "theme.py"):
    import theme
    theme.setup(c, 'macchiato', True)

c.auto_save.interval = 3000

c.changelog_after_upgrade = "patch"
c.colors.statusbar.normal.bg = "rgba(0, 0, 0, 0)"
c.content.blocking.adblock.lists = [
    "https://easylist.to/easylist/easylist.txt",
    "https://easylist.to/easylist/easyprivacy.txt",
    "https://downloads.vivaldi.com/lists/abp/antiadblockfilters-current.txt",
    "https://downloads.vivaldi.com/lists/abp/abp-filters-anti-cv-current.txt",
    "https://easylist-downloads.adblockplus.org/easylistportuguese.txt",
    "https://secure.fanboy.co.nz/fanboy-cookiemonster.txt",
]
c.content.mouse_lock = "ask"
c.content.pdfjs = True
c.statusbar.show = "always"

tabwidget.TabWidget.MUTE_STRING = ""
tabwidget.TabWidget.AUDIBLE_STRING = ""

text_color = '#ffffff'
active_background = '#6272a4'
# active tabs
c.colors.tabs.selected.even.bg = active_background
c.colors.tabs.selected.odd.bg  = active_background
c.colors.tabs.selected.even.fg = text_color
c.colors.tabs.selected.odd.fg  = text_color

#inactive tabs
c.colors.tabs.even.bg = '#000000'
c.colors.tabs.odd.bg  = '#101010'
c.colors.tabs.even.fg = text_color
c.colors.tabs.odd.fg  = text_color

c.tabs.padding = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
c.colors.webpage.bg = '#1e1e1e'
# fonts
c.fonts.default_family = []
c.fonts.default_size = '10pt'
c.fonts.web.family.fixed = 'JetBrains Mono'
c.fonts.web.family.sans_serif = 'JetBrains Mono'
c.fonts.web.family.serif = 'JetBrains Mono'
c.fonts.web.family.standard = 'JetBrains Mono'

# c.fonts.tabs.selected = "9pt JetBrains Mono"
# c.fonts.tabs.unselected = "9pt JetBrains Mono"

config.set('fonts.tabs.selected', '8pt JetBrains Mono')
config.set('fonts.tabs.unselected', '8pt JetBrains Mono')

c.downloads.position = 'bottom'

c.editor.command = ['code', '{file}']
default_page = 'file:///home/pncolvr/Projects/helpers/browser/landingpage/home/index.html'
c.url.default_page = default_page
c.url.start_pages = [default_page]

c.content.autoplay = False

c.content.blocking.enabled = True
config.set("content.blocking.enabled", False, "https://www.youtube.com/*")


c.content.local_content_can_access_file_urls = True
c.content.local_content_can_access_remote_urls = True

c.tabs.favicons.show = 'pinned'
c.tabs.show = 'multiple'
c.tabs.title.alignment = 'center'
c.tabs.title.format = '{index}:{audio} {current_title}'

c.tabs.indicator.width = 0


c.input.insert_mode.auto_leave = True
c.input.insert_mode.auto_load = True

# dark mode setup
c.colors.webpage.darkmode.enabled = False
c.colors.webpage.darkmode.algorithm = 'lightness-cielab'
c.colors.webpage.darkmode.policy.images = 'never'
# config.set('colors.webpage.darkmode.enabled', False, 'file://*')
c.colors.webpage.preferred_color_scheme = "dark"


# privacy
config.set("content.geolocation", False)
config.set("content.webrtc_ip_handling_policy", "default-public-interface-only")
config.set("content.cookies.accept", "all")
config.set("content.cookies.store", True)
# config.set("content.cookies.block_thirdparty", False)
config.set("content.local_storage", True)
# config.set("content.javascript.can_access_clipboard", True)

# c.content.headers.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
c.zoom.default = 90
c.zoom.levels = [
    "25%", "30%", "35%", "40%", "45%", "50%", "55%", "60%", "65%", "70%",
    "75%", "80%", "85%", "90%", "95%", "100%", "105%", "110%", "115%",
    "120%", "125%", "130%", "135%", "140%", "145%", "150%", "155%",
    "160%", "165%", "170%", "175%", "180%", "185%", "190%", "195%",
    "200%", "205%", "210%", "215%", "220%", "225%", "230%", "235%",
    "240%", "245%", "250%", "255%", "260%", "265%", "270%", "275%",
    "280%", "285%", "290%", "295%", "300%", "305%", "310%", "315%",
    "320%", "325%", "330%", "335%", "340%", "345%", "350%", "355%",
    "360%", "365%", "370%", "375%", "380%", "385%", "390%", "395%",
    "400%", "405%", "410%", "415%", "420%", "425%", "430%", "435%",
    "440%", "445%", "450%", "455%", "460%", "465%", "470%", "475%",
    "480%", "485%", "490%", "495%", "500%"
]

c.zoom.mouse_divider = 8192

c.url.searchengines = {
        'DEFAULT': 'https://start.duckduckgo.com/?q={}',
        # '!g': 'https://www.google.com/search?q={}',
        '!da': 'https://duckduckgo.com/?q={}',
        '!pc': 'https://www.pcdiga.com/search?query={}',
        '!a': 'https://archlinux.org/packages/?sort=&q={}&maintainer=&flagged=',
        '!aur': 'https://aur.archlinux.org/packages?O=0&SeB=nd&K={}&outdated=&SB=p&SO=d&PP=50&submit=Go',
        '!w': 'https://wiki.archlinux.org/index.php?search={}',
        '!yt': 'https://www.youtube.com/results?search_query={}',
        '!am': 'https://www.amazon.es/s?k={}',
        '!sg': 'https://www.steamgriddb.com/search/grids?term={}'
        }

# config.bind(',sg', 'open -t !g {primary}')
config.bind(',sd', 'open -t !da {primary}')
# config.bind(',su', 'open -t !aur {primary}')
# config.bind(',sy', 'open -t !yt {primary}')
# config.bind(',sp', 'open -t !pc {primary}')
# config.bind(',sw', 'open -t !w {primary}')
config.bind(',tg', 'open -t https://translate.google.com/?sl=pt-PT&tl=es&text={primary}&op=translate')

c.completion.open_categories = ['searchengines', 'quickmarks', 'bookmarks', 'history', 'filesystem']

# config.set('input.mode_override', 'passthrough', 'www.youtube.com')

conf_folder="/home/pncolvr/.config/qutebrowser"

config.bind('o', 'cmd-set-text -s :open')
config.bind('!', 'cmd-set-text -s :open !')

# custom binds
config.unbind('d')
# config.bind('dm', 'config-cycle colors.webpage.darkmode.enabled')
config.bind('dc', 'download-clear')
config.bind('do', 'download-open')
config.bind('<F12>', 'devtools')
config.bind('<Ctrl-F>', 'cmd-set-text /')

config.bind(',mo', f'jseval -f {conf_folder}/sripts/js/mono.js')
config.bind(',ui', f'jseval -f {conf_folder}/sripts/js/unlockinsta.js')
# config.bind('<Ctrl-Alt-Shift-Meta-F3>', f'jseval -f {conf_folder}/scripts/js/embedyt.js')
config.bind(',gh', f'jseval -f {conf_folder}/scripts/js/home.js')

config.bind(',co', 'tab-only')
config.bind('<Ctrl+b>', 'config-cycle statusbar.show never always')

config.bind(',cs', ':config-source')
config.bind('<Ctrl-l>', 'cmd-set-text :open {url:pretty}')
config.bind('<Ctrl-t>', 'cmd-set-text -s :open -t ')

# im dumb...
# config.bind('<Ctrl-b>', 'back')
# config.bind('<Ctrl-w>', 'forward')

config.bind(',pp', 'open -t -- {clipboard}')
config.bind(',ss', ':screenshot ~/Pictures/qutebrowser/{date}.png')
config.bind(',sS', ':print --pdf ~/Pictures/qutebrowser/{date}.pdf')


# config.bind('<Ctrl-PgDown>', 'tab-next')
# config.bind('<Ctrl-PgUp>', 'tab-prev')
config.bind(',yy', f'spawn --userscript {conf_folder}/scripts/url/clean.sh {{url}}')
config.bind(',yY', f'hint links spawn --userscript {conf_folder}/scripts/url/clean.sh {{hint-url}}')
config.bind(',YY', f'spawn --userscript {conf_folder}/scripts/url/select.sh')
config.bind(',cc', f'spawn --userscript /usr/bin/kitty --hold -e {conf_folder}/scripts/certificate.sh {{url}}')

config.bind(',gH', f'open {default_page}')

config.bind(',mm', 'spawn --userscript ~/.config/hypr/scripts/tolocalplayer.sh "{title}" "{url}"')
config.bind(',MM', f'spawn --userscript /usr/bin/kitty --hold -e {conf_folder}/scripts/download.sh {{url}}')
config.bind(',mM', 'hint links spawn --userscript ~/.config/hypr/scripts/tolocalplayer.sh "{title}" "{hint-url}"')

config.bind(',gr', f'spawn --userscript {conf_folder}/scripts/custom/css-apply.sh ;; greasemonkey-reload ;; reload')

config.bind('D', f'spawn --userscript {conf_folder}/scripts/python/darkreader.py toggle domain')
