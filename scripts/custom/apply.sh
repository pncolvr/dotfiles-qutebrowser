#!/usr/bin/env bash

WORKSPACE=$(dirname "$BASH_SOURCE[0]:-0")

echo "updating css"
"$WORKSPACE"/css-apply.sh

echo "updating js"
"$WORKSPACE"/js-apply.sh