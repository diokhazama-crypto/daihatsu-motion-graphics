#!/usr/bin/env bash
# Lagu Ayla diputar 2x tanpa jeda -> public/ayla_music.wav (28.71 dtk).
# mp3 aslinya 14.34 dtk dan sedikit lebih pendek dari 9 bar; putaran kedua dimulai di 14.37 dtk
# (ketukan pertamanya jatuh ~30 ms dari grid). Celah senyap ~60 ms di sambungan diisi gema dari
# ketukan terakhir supaya transisinya mulus, lalu limiter supaya tidak pecah.
# Pemakaian: scripts/prep_ayla_music.sh <lagu.mp3>
set -e
SRC=${1:?file mp3}
ffmpeg -v error -y -i "$SRC" -filter_complex "\
[0:a]aresample=48000,asplit=3[x][y][z];\
[y]adelay=14370|14370[y2];\
[z]atrim=14.06:14.30,asetpts=PTS-STARTPTS,aecho=0.8:0.6:30|55|80:0.55|0.4|0.25,afade=t=in:d=0.02,afade=t=out:st=0.12:d=0.2,volume=0.75,adelay=14240|14240[z2];\
[x][y2][z2]amix=inputs=3:normalize=0:duration=longest,atrim=0:28.71,alimiter=limit=0.95:level=false" \
  -ac 2 -ar 48000 public/ayla_music.wav
echo "ok public/ayla_music.wav"
