# Daihatsu Motion Graphics

Video promo TikTok "jedag jedug" (9:16, 1080×1920, 30 fps) yang dibuat dengan [Remotion](https://remotion.dev).
Potongan, zoom, flash dan teks semuanya dikunci ke ketukan lagu.

## Video yang ada

| ID | Isi | Durasi |
|----|-----|--------|
| `GranMaxPromo` | v1-v2: jedag jedug TikTok, sinkron lagu MP3 | 60 detik |
| `GranMaxIklan` | v3: iklan profesional, pakai lagu MP3 yang sama, potongan tiap bar | 60 detik |
| `SigraSinematik` | Sigra 1.2 R MT: gaya sinematik malam (grading gelap, aksen merah, lampu menyala, mask lewat lampu) | 30 detik |
| `SigraTerang` | Sama persis dengan `SigraSinematik`, tapi grading terang (kecerahan mendekati asli) | 30 detik |
| `AylaTerang` | All New Ayla 1.2 R CVT: gaya sama dengan `SigraTerang`, gabungan Ayla hitam & merah, lagu mp3 diputar 2x | 28,7 detik |

Render versi 3:

```bash
python3 scripts/prep_music.py assets/lagu.mp3   # public/music.wav (lagu MP3, sama dgn v1-v2)
python3 scripts/build_iklan.py        # src/iklan.json (edit SHOTS/TEXTS/CTA di sini)
npx remotion render GranMaxIklan out/granmax_iklan.mp4 --crf=18
```

Render Sigra (pakai lagu dari video Sigra-nya sendiri, 152 BPM, drop di 20,1 dtk):

```bash
python3 scripts/prep_sigra.py <Sigra_IMP_30detik_speed125.mp4>   # public/clips/sigra.mp4 (sudah di-grade) + public/sigra_music.wav
python3 scripts/build_sigra.py        # src/sigra.json (edit SHOTS / TITLE di sini)
npx remotion render SigraSinematik out/sigra_sinematik.mp4 --crf=18

# versi terang
python3 scripts/prep_sigra.py <Sigra_IMP_30detik_speed125.mp4> --terang   # public/clips/sigra_terang.mp4
npx remotion render SigraTerang out/sigra_terang.mp4 --crf=18
```

Render Ayla (lagu mp3 14,3 dtk diputar 2x tanpa jeda, 152 BPM, drop di 6,46 & 20,83 dtk):

```bash
python3 scripts/prep_sigra.py <VID_..._204340.mp4> --terang --no-delogo --no-audio --out public/clips/ayla_a_terang.mp4
python3 scripts/prep_sigra.py <VID_..._203838.mp4> --terang --no-delogo --no-audio --res 1080x1920 --out public/clips/ayla_b_terang.mp4
scripts/prep_ayla_music.sh <lagu.mp3>   # public/ayla_music.wav, 2x putar + sambungan mulus
python3 scripts/build_ayla.py         # src/ayla.json (edit SHOTS / TEXTS di sini)
npx remotion render AylaTerang out/ayla_terang.mp4 --crf=18
```

Semua video memakai komponen yang sama (`Sinematik` di `src/SigraSinematik.tsx`) dan alat timeline
bersama `scripts/timeline.py`.

Efek di `SigraSinematik` / `SigraTerang`:
- transisi (berpusat di ketukan): `push` (whip blur searah), `zoom` (zoom-through), `spin`,
  `slice` (wipe bilah bertangga), `leak` (light leak hangat), `blur` (blur dissolve),
  `mask` (shot berikutnya muncul di dalam lampu depan lalu membesar)
- efek: `lightOn` (lampu menyala), `focus` (rack focus), `flash` (kilat di drop)
- lampu (`src/sigraFx.tsx`): inti putih, bloom, flare horizontal, pantulan di lantai
- teks gaya judul (huruf muncul satu per satu + garis merah): atur di `TEXTS` pada `scripts/build_sigra.py`

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
