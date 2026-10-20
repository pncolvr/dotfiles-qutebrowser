"""Site-specific webpage dark mode overrides."""


def apply(config):
    config.set('colors.webpage.darkmode.enabled', True, '*://archlinux.org/*')
    for pattern in (
        '*://connect.stripe.com/*',
        '*://docs.google.com/*',
        '*://drive.google.com/*',
        '*://faturas.portaldasfinancas.gov.pt/*',
        '*://github.com/*',
        '*://medium.com/*',
        '*://packages.cachyos.org/*',
        '*://pncolvr.github.io/*',
        '*://studio.buymeacoffee.com/*',
        '*://www.flama-home.com/*',
        '*://www.twitch.tv/*',
        '*://www.youtube.com/*',
    ):
        config.set('colors.webpage.darkmode.enabled', False, pattern)
