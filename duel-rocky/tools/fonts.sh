#!/bin/sh
# Fetch the fonts the page uses (SIL Open Font License 1.1, see CREDITS) into fonts/. Files already there are kept.
set -e
D=$(cd "$(dirname "$0")/.." && pwd)/fonts; mkdir -p "$D"
get() { [ -s "$D/$1" ] && return 0; curl -fsSL --retry 2 -o "$D/$1.part" "$2" && mv "$D/$1.part" "$D/$1" && echo "fonts/$1"; }
get baloo2-800.woff2 "https://fonts.gstatic.com/s/baloo2/v23/wXK0E3kTposypRydzVT08TS3JnAmtdiayppo_lc.woff2"
get rye.woff2 "https://fonts.gstatic.com/s/rye/v17/r05XGLJT86YzEZ7t.woff2"
get vt323.woff2 "https://fonts.gstatic.com/s/vt323/v18/pxiKyp0ihIEF2isfFJXUdVNF.woff2"
