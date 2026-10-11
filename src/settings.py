"""Browser behavior, content policies, downloads, search, and zoom."""


def apply(config, c, paths):
    # General behavior
    c.auto_save.interval = 3000
    c.messages.timeout = 5000
    c.changelog_after_upgrade = 'patch'
    c.statusbar.show = 'always'
    c.qt.chromium.low_end_device_mode = 'always'
    c.editor.command = ['code', '{file}']
    c.url.default_page = paths.default_page
    c.url.start_pages = [paths.default_page]
    c.tabs.favicons.show = 'pinned'
    c.tabs.show = 'multiple'
    c.tabs.title.alignment = 'center'
    c.tabs.title.format = '{index}:{audio} {current_title}'
    c.tabs.indicator.width = 0
    # Return to the landing page when the last tab closes.
    c.tabs.last_close = 'default-page'
    c.input.insert_mode.auto_leave = True
    c.input.insert_mode.auto_load = True
    c.completion.open_categories = [
        'searchengines', 'quickmarks', 'bookmarks', 'history', 'filesystem',
    ]

    # Downloads
    # dp toggles both prompting and the destination directory.
    # These defaults keep the two cycles aligned when config is loaded.
    c.downloads.position = 'bottom'
    c.downloads.remove_finished = 500
    c.downloads.location.prompt = True
    c.downloads.location.directory = paths.downloads

    # Content and privacy
    c.content.blocking.adblock.lists = [
        'https://easylist.to/easylist/easylist.txt',
        'https://easylist.to/easylist/easyprivacy.txt',
        'https://downloads.vivaldi.com/lists/abp/antiadblockfilters-current.txt',
        'https://downloads.vivaldi.com/lists/abp/abp-filters-anti-cv-current.txt',
        'https://easylist-downloads.adblockplus.org/easylistportuguese.txt',
        'https://secure.fanboy.co.nz/fanboy-cookiemonster.txt',
    ]
    c.content.mouse_lock = 'ask'
    c.content.pdfjs = False
    c.content.autoplay = False
    c.content.blocking.enabled = True
    config.set('content.blocking.enabled', False, 'https://www.youtube.com/*')
    c.content.local_content_can_access_file_urls = True
    c.content.local_content_can_access_remote_urls = True
    config.set('content.geolocation', False)
    config.set('content.webrtc_ip_handling_policy', 'default-public-interface-only')
    config.set('content.cookies.accept', 'all')
    config.set('content.cookies.store', True)
    config.set('content.local_storage', True)

    # Search and zoom
    c.zoom.levels = [f'{level}%' for level in range(25, 501, 5)]
    c.zoom.mouse_divider = 8192
    c.url.searchengines = {
        'DEFAULT': 'https://start.duckduckgo.com/?q={}',
        '!da': 'https://duckduckgo.com/?q={}',
        '!pc': 'https://www.pcdiga.com/search?query={}',
        '!pdb': 'https://www.protondb.com/search?q={}',
        '!a': 'https://archlinux.org/packages/?sort=&q={}&maintainer=&flagged=',
        '!aur': ('https://aur.archlinux.org/packages'
                 '?O=0&SeB=nd&K={}&outdated=&SB=p&SO=d&PP=50&submit=Go'),
        '!w': 'https://wiki.archlinux.org/index.php?search={}',
        '!yt': 'https://www.youtube.com/results?search_query={}',
        '!am': 'https://www.amazon.es/s?k={}',
        '!sg': 'https://www.steamgriddb.com/search/grids?term={}',
        '!mw': 'https://www.merriam-webster.com/dictionary/{}',
        '!dlpo': 'https://dicionario.priberam.org/pt-pt/{}',
    }
