#!/bin/sh
# Rebuild "Duel di Depan Bank" from scratch: sh build.sh
# Needs the Lemo-Opuscar library with its core + voice tiers (LIB below), ffmpeg, and internet for edge-tts.
set -e
LIB=${LIB:-/root/lemo-opuscar}
export LIB
HERE=$(cd "$(dirname "$0")" && pwd)
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the library folder"; exit 1; }
PY="$LIB/.venv/bin/python"
sh "$HERE/tools/fonts.sh"                                                        # 0. fonts (OFL) → fonts/
SSL_CERT_FILE=${SSL_CERT_FILE:-} "$PY" "$HERE/tools/tts_proxy.py" "$LIB/core/tts/tts_zh.py" "$HERE/lines.json" "$HERE/out/raw"   # 1. edge-tts voices
"$PY" "$HERE/voice.py"                                                           # 2. per-character processing + lip-sync envelopes
"$PY" "$HERE/asr.py"                                                             # 3. Whisper check (Indonesian)
cd "$LIB"
node core/render/events.mjs "$HERE" --size 1080x1920                             # 4. timeline → events.json
"$PY" "$HERE/score.py"                                                           # 5. synthesized score → music/score.wav
"$PY" "$HERE/mix.py"                                                             # 6. foley + voices + ducked score + ambience → out/mix.wav
"$PY" "$HERE/tools/srt.py"                                                       # 7. subtitles_id.srt
node core/render/video.mjs "$HERE" --size 1080x1920 --fps 24 --workers 4 --out "$HERE/out/video.mp4"   # 8. picture
sh "$HERE/tools/master.sh" "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/duel-rocky.mp4"            # 9. -14 LUFS + mux
