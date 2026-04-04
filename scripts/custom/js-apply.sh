#!/usr/bin/env bash

SRC_DIR="$HOME/.config/qutebrowser/custom/js"
for f in "$SRC_DIR"/*.js; do
  [ -f "$f" ] || continue
  name="$(basename "$f")"
  out_name="_c.js.$name"
  out="$HOME/.config/qutebrowser/greasemonkey/$out_name"
  ln -sf "$SRC_DIR/$name" "$out"
  ln -sf "$out" "/home/pncolvr/.local/share/qutebrowser-webapp/config/greasemonkey/$out_name"
  ln -sf "$out" "/home/pncolvr/.local/share/qutebrowser-twitch-chat/config/greasemonkey/$out_name"
  echo "Generated $out"
done