#!/usr/bin/env bash

WORKSPACE=$(dirname "${BASH_SOURCE[0]:-0}")
source "$WORKSPACE/_common.sh"

clean_url=$(clean "$1")
wl-copy "$clean_url"

update "$clean_url copied"