# Daihatsu Motion Graphics

Video promo TikTok "jedag jedug" (9:16, 1080×1920, 30 fps) yang dibuat dengan [Remotion](https://remotion.dev).
Potongan, zoom, flash dan teks semuanya dikunci ke ketukan lagu.

## Video yang ada

| ID | Isi | Durasi |
|----|-----|--------|
| `GranMaxPromo` | v1-v2: jedag jedug TikTok, sinkron lagu MP3 | 60 detik |
| `GranMaxIklan` | v3: iklan profesional, pakai lagu MP3 yang sama, potongan tiap bar | 60 detik |
| `GranMaxTanjakan` | v4: cinematic TikTok, Gran Max angkut 2.900 kg sawit di tanjakan, 60 fps | 23,5 detik |

Render versi 3:

```bash
python3 scripts/prep_music.py assets/lagu.mp3   # public/music.wav (lagu MP3, sama dgn v1-v2)
python3 scripts/build_iklan.py        # src/iklan.json (edit SHOTS/TEXTS/CTA di sini)
npx remotion render GranMaxIklan out/granmax_iklan.mp4 --crf=18
```

Render versi 4 (cinematic tanjakan):

```bash
pip install opencv-python-headless scipy
python3 scripts/clean_pov.py <video_mentah.mp4> public/clips/tanjakan.mp4   # hapus teks bawaan "POV"
mkdir -p public/tanjakan && ffmpeg -i public/clips/tanjakan.mp4 -q:v 3 -start_number 0 public/tanjakan/%04d.jpg
ffmpeg -i <video_mentah.mp4> -vn -ac 2 -ar 44100 assets/mesin_tanjakan.wav   # raungan mesin asli
cp <lagu.mp3> assets/lagu_tanjakan.mp3
python3 scripts/build_tanjakan.py        # src/tanjakan.json (edit SHOTS/TEXTS/CTA di sini)
python3 scripts/make_tanjakan_audio.py   # public/tanjakan_audio.wav (lagu + mesin)
npm run render:tanjakan                  # -> out/granmax_tanjakan.mp4
```

Potongan v4 dikunci ke hentakan bass lagu (150 BPM): intro bass = "2.900 KG", break = slow-mo,
DROP di 6,76 dtk lagu = KUAT / BANDEL / TANGGUH, lalu lagu diulang mulus dari drop untuk end card.
Transisi: `black`, `flash`, `whip`, `punch`, `glitch` (RGB split), `cut`; speed ramp per shot (r0 -> r1).

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
