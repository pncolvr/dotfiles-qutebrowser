"""Load shared configuration for the main browser and alternate profiles."""

from pathlib import Path
from runpy import run_path
from types import SimpleNamespace

root = Path(__file__).resolve().parent
src = root / 'src'
home = Path.home()
paths = SimpleNamespace(
    home=str(home),
    stylesheet=str(src / 'custom/css/scrollbars.css'),
    downloads=str(home / 'Downloads'),
    default_page=(home / 'Projects/helpers/browser/landingpage/home/index.html').as_uri(),
)

config.load_autoconfig(True)

# Execute each file again on reload so edits are picked up immediately.
theme = run_path(str(src / 'theme.py'))
theme['apply'](c, paths)
run_path(str(src / 'settings.py'))['apply'](config, c, paths)
run_path(str(src / 'darkmode.py'))['apply'](config)
run_path(str(src / 'bindings.py'))['apply'](config, paths)
run_path(str(src / 'patches.py'))['apply'](theme)
