#!/bin/sh
# Master + mux with any ffmpeg (6.x included): two-pass loudnorm to -14 LUFS / -1.5 dBTP, audio cut/padded to the picture's exact length.
# Usage: sh tools/master.sh video.mp4 mix.wav out.mp4
set -e
V=$1; A=$2; O=$3; TMP=$(mktemp -d)
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$V")
M=$(ffmpeg -hide_banner -nostats -i "$A" -af "apad,atrim=0:$D,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | grep "\"$1\"" | sed 's/.*: "\(.*\)".*/\1/'; }
ffmpeg -hide_banner -loglevel error -y -i "$A" -af "apad,atrim=0:$D,loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" -ar 48000 "$TMP/a.wav"
ffmpeg -hide_banner -loglevel error -y -i "$V" -i "$TMP/a.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$TMP/out.mp4"
mv "$TMP/out.mp4" "$O"; rm -rf "$TMP"
ffmpeg -hide_banner -nostats -i "$O" -af ebur128=peak=true -f null - 2>&1 | grep -E "^ +I:|^ +Peak:" | tr -s ' '
echo "wrote $O"
