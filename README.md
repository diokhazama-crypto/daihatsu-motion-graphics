# Daihatsu Motion Graphics

Video promo TikTok "jedag jedug" (9:16, 1080×1920, 30 fps) yang dibuat dengan [Remotion](https://remotion.dev).
Potongan, zoom, flash dan teks semuanya dikunci ke ketukan lagu.

## Video yang ada

| ID | Isi | Durasi |
|----|-----|--------|
| `GranMaxPromo` | Gran Max Pick Up & Blind Van: hook, fitur, bukti muatan, CTA WA | 60 detik |

## Struktur

```
src/GranMaxPromo.tsx      komposisi utama (transisi, teks, CTA)
src/timeline.json         HASIL GENERATE: daftar shot & teks dalam frame
scripts/build_timeline.py EDIT DI SINI: urutan shot/teks per ketukan lagu
scripts/prep_music.py     MP3 33 dtk -> music.wav 60 dtk (loop di awal bar)
scripts/prep_clips.sh     konversi video HP (HEVC) -> H.264 1080x1920
public/clips/*.mp4        klip (tidak di-commit, terlalu besar)
public/music.wav          musik (tidak di-commit)
```

## Cara render ulang

```bash
npm install
scripts/prep_clips.sh <folder-video-mentah>     # bikin public/clips/*
python3 scripts/prep_music.py assets/lagu.mp3   # bikin public/music.wav
python3 scripts/build_timeline.py               # bikin src/timeline.json
npm run render                                  # -> out/granmax_promo.mp4
```

Preview interaktif: `npm run studio`.

## Mengganti isi

- **Teks, nomor WA, promo**: ubah `TEXTS` / `CTA` di `scripts/build_timeline.py`, lalu jalankan lagi `build_timeline.py`.
- **Urutan shot**: ubah `SHOTS` (ketukan mulai, nama klip, detik di klip, jenis transisi).
  Transisi yang tersedia: `cut`, `zoom`, `whip`, `spin`, `flash`, `fade`.
- **Lagu lain**: ukur BPM & ketukan pertama (mis. dengan `librosa`), lalu isi `T0` dan `BEAT`
  di `build_timeline.py` dan `prep_music.py`.

Lagu yang dipakai: 130 BPM, ketukan pertama di 0.105 dtk, "jedug" terkuat di awal tiap bar.
