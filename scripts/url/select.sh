#!/usr/bin/env bash

WORKSPACE=$(dirname "${BASH_SOURCE[0]:-0}")

source "$WORKSPACE/_common.sh"

QUTEBROWSER_SESSION="$HOME/.local/share/qutebrowser/sessions/_autosave.yml"

mapfile -t titles < <(yq -r '.windows[].tabs[].history[] | select(.active) | .title' "$QUTEBROWSER_SESSION")

if [[ ${#titles[@]} -eq 0 ]]; then
   update "no active tabs found"
   exit 1
fi

if [[ ${#titles[@]} -eq 1 ]]; then
   selected_titles=("${titles[0]}")
else
    mapfile -t selected_titles < <(printf '%s\n' "${titles[@]}" | rofi -dmenu -multi-select -case-smart -sort -sorting-method fzf -p "")
fi

if (( ${#selected_titles[@]} )); then
    selected_json=$(printf '%s\n' "${selected_titles[@]}" | jq -R -s -c 'split("\n")[:-1]')
    urls=($(yq -r --argjson t "$selected_json" '.windows[].tabs[].history[] | select(.active and (.title | IN($t[]))) | .url' "$QUTEBROWSER_SESSION"))
    clean_urls=$(printf '%s\n' "${urls[@]}" | clean_all)
    echo -n "$clean_urls" | wl-copy
fi

update "selection copied"