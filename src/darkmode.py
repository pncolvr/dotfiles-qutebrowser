"""Site-specific webpage dark mode overrides."""


def apply(config):
    config.set('colors.webpage.darkmode.enabled', True, '*://archlinux.org/*')
    for pattern in (
        '*://accounts.google.com/*',
        '*://calendar.google.com/*',
        '*://chrome.google.com/*',
        '*://chromewebstore.google.com/*',
        '*://connect.stripe.com/*',
        '*://docs.google.com/*',
        '*://drive.google.com/*',
        '*://faturas.portaldasfinancas.gov.pt/*',
        '*://github.com/*',
        '*://mail.google.com/*',
        '*://medium.com/*',
        '*://myaccount.google.com/*',
        '*://packages.cachyos.org/*',
        '*://pncolvr.github.io/*',
        '*://studio.buymeacoffee.com/*',
        '*://www.flama-home.com/*',
        '*://www.portaldasfinancas.gov.pt/*',
        '*://www.twitch.tv/*',
        '*://www.youtube.com/*',
    ):
        config.set('colors.webpage.darkmode.enabled', False, pattern)
