#!/bin/sh
# DIO — Sales Daihatsu (Text Flash Cuts), 5 s, 1080x1920, 30 fps. One command: sh build.sh
# Needs: the Lemo-Opuscar library (LIB) with core deps, ffmpeg 7+, and the 3 images in gen/ (prompts/PROMPTS.md).
set -e
LIB=${LIB:-/root/lemo-opuscar}
HERE=$(cd "$(dirname "$0")" && pwd)
export LIB
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the library folder"; exit 1; }
PY="$LIB/.venv/bin/python"
for l in vsco2ce vcsl; do [ -d "$LIB/core/audio/instruments/$l" ] || (cd "$LIB" && sh tools/fetch.sh instruments $l); done
mkdir -p "$HERE/out"
"$PY" "$HERE/tools/prep.py"
cd "$LIB"
node core/render/events.mjs "$HERE" --size 1080x1920
node core/render/readcheck.mjs "$HERE" --size 1080x1920 --step 0.0333
node core/render/video.mjs "$HERE" --size 1080x1920 --fps 30 --workers ${WORKERS:-3} --out "$HERE/out/video.mp4"
"$PY" "$HERE/mix.py"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/dio-sales-daihatsu.mp4" 30 0
node core/render/still.mjs "$HERE" 3.6 --size 1080x1920 --prefix poster_ --out "$HERE/out" >/dev/null
cp "$HERE/out/poster_3.6.jpg" "$HERE/poster.jpg"
echo "done: $HERE/dio-sales-daihatsu.mp4"
