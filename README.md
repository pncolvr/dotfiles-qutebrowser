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
in the separate repo at [`~/.local/share/qutebrowser/userscripts`](//github.com/pncolvr/qutebrowser-userscripts). Bindings call
its scripts by name. Keep browser settings and theme in this repo.
Run `:config-source` after changing bindings.

Use `>gr` to regenerate custom CSS/JavaScript and reload the page.

## rbw autofill

`>bw` starts a browser-owned rbw operation and always confirms the entry and
destination through Quickshell. Focus a login input first. `:rbw-fill username`,
`:rbw-fill password` and `:rbw-fill totp` fill only the focused field. Nothing is
submitted or copied to the clipboard automatically.

The hook in `src/patches.py` registers `src/rbw.py`; `src/rbw_form.js` fills through
the browser API in an isolated world. The helper `qute-rbw` lives in the separate
userscripts repository. Secrets travel over a private socket rather than browser
command arguments. Handles expire, cannot replay, and are bound to the original
tab/document; navigation and configuration reload cancel pending work.

Setup, limitations and all cross-repository tests live in Quickshell:
`~/.config/quickshell/docs/features/rbw.md` and `tests/security/rbw/`.
This integration supports rbw 1.15.x and refuses protected/unknown entries,
unsupported URI regex rules, frames and ambiguous forms. Reload Quickshell and
run `:config-source` after installation. The website receives the login secret;
this is not protection against a compromised website or machine.
