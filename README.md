# Info

This is my personal daily driver qutebrowser configuration that I use for personal activities.
It has some, not all, QOLs for my web browsing.

# Relevant Commands
I use this repo as a git submodule on my dotfiles.  
The following command is isued on the dotfiles repo, to have this one as a submodule.
```shell
git submodule add git@github.com:pncolvr/dotfiles-qutebrowser.git .config/qutebrowser
```

## When cloning a "parent repo" to include the submodules

```shell
git clone --recurse-submodules <repository-url>
```
_or_ if we cloned the repo without the submodules
```shell
git submodule update --init --recursive
```

# Syncing submodules

```shell
git submodule sync --recursive
```

# Custom userscripts

Executable scripts, page JavaScript and site-specific Greasemonkey sources live
in the separate repo at `~/.local/share/qutebrowser/userscripts`. Bindings call
its scripts by name. Keep browser settings, theme and the global scrollbar
stylesheet in this repo. Run `:config-source` after changing bindings.

Use `,gr` to regenerate custom CSS/JavaScript and reload the page.
