#!/usr/bin/env bash

SRC_DIR="$HOME/.config/qutebrowser/custom/css"
rm -f "$HOME"/.config/qutebrowser/greasemonkey/_g.css.*.js
for f in "$SRC_DIR"/*.css; do
  [ -f "$f" ] || continue
  name="$(basename "${f%.css}")"
  out_name="_g.css.$name.js"
  out="$HOME/.config/qutebrowser/greasemonkey/$out_name"
  content=$(cat "$f")
  cat > "$out" <<EOF
// ==UserScript==
// @name         $name
// @namespace    http://$name/
// @version      0.1
// @description  $name
// @author       pncolvr
// @match        https://$name/*
// @match        https://*.$name/*
// @grant        none
// @run-at       document-end
// ==/UserScript==

(function() {
    GM_addStyle(\`
$content
\`)
})();
EOF
  ln -sf "$out" "/home/pncolvr/.local/share/qutebrowser-webapp/config/greasemonkey/$out_name"
  ln -sf "$out" "/home/pncolvr/.local/share/qutebrowser-twitch-chat/config/greasemonkey/$out_name"
  echo "Generated $out"
done