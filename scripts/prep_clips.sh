#!/usr/bin/env bash
# Konversi klip mentah (HEVC 720x1280) -> H.264 1080x1920 30fps tanpa audio.
# Pemakaian: scripts/prep_clips.sh <folder_klip_mentah>
set -e
SRC=${1:?folder klip mentah}
OUT=public/clips; mkdir -p $OUT
enc() { ffmpeg -v error -y -i "$1" -an -vf "$2,fps=30,format=yuv420p" -c:v libx264 -preset veryfast -crf 18 -g 15 "$OUT/$3"; echo "ok $3"; }
FULL="scale=1080:1920:flags=lanczos"
# Klip dengan teks bawaan di bagian bawah: crop bagian atas supaya teksnya terbuang.
CROPTOP="crop=518:922:101:0,scale=1080:1920:flags=lanczos"
enc "$SRC/a942d102-2_5474153689558067449.mp4" "$FULL"    pu_silver.mp4
enc "$SRC/f084ed65-2_5474153689558067450.mp4" "$CROPTOP" blindvan.mp4
enc "$SRC/c7e76905-2_5474153689558067451.mp4" "$FULL"    detail.mp4
enc "$SRC/13b15d89-2_5474153689558067453.mp4" "$FULL"    spbu.mp4
enc "$SRC/84e07abe-2_5474153689558067456.mp4" "$CROPTOP" pasar.mp4
