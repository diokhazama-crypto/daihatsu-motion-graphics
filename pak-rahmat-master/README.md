# KODE MASTER PAK RAHMAT

Satu folder untuk semua episode Pak Rahmat (gaya PRO PLUS, 9:16 1080x1920, 30 fps).
Gambar tetap (tokoh, toko, Gran Max, kampung, Dapur MBG, Dio) ada di `aset_*.py` dan **tidak digambar ulang**.
Episode baru cukup menulis `episode/ep<N>.py` (adegan + pengaturan + suara).

## Langkah tiap episode

```bash
pip install pycairo faster-whisper numpy pillow        # sekali per sesi (ffmpeg & font Inter sudah ada)
python3 jalankan.py 5 siap /path/audio_narasi.wav        # transkrip -> kerja/ep5/words.json + teks polos
#   koreksi nama/merek di kerja/ep5/words.json ([kata, mulai, selesai])
cp episode/TEMPLATE.py episode/ep5.py                    # isi adegan sesuai narasi
python3 jalankan.py 5 cek 1 12 25 40 55 63               # 1 gambar 540 px -> kerja/ep5/cek.png
python3 jalankan.py 5 render                             # -> kerja/ep5/PakRahmat_GranMax_ep5_PROPLUS.mp4
python3 jalankan.py 5 render --seg 2                     # revisi: render ulang segmen 2 saja, lalu gabung
python3 jalankan.py 5 arsip                              # narasi MP3 + words.json + ep5.py ber-awalan arsip
```

Render ep 4 (68 dtk) di 4 inti: sekitar 14 menit.

## Isi folder

| File | Isi |
|------|-----|
| `jalankan.py` | satu pintu: siap / cek / render / arsip |
| `gaya.py` | mesin PRO PLUS: teks per kata zona aman, hook, BERSAMBUNG, kartu 2 pilihan + FOLLOW EP N+1, watermark, kamera tenang + zoom hentak, depth of field, grading per suasana |
| `sfx_alat.py` | generator sound effect + musik ukulele + ducking |
| `aset_dasar.py` | (dulu lib.py) `person`, `gran_max`, `motor`, `sack`, `sweat`, `spark`, `exclaim`, `zzz`, `cloud`, `cam_keys`; CH dasar: rahmat, julit, friend, anak, b1-b4 |
| `aset_kampung.py` | (dulu ep2.py) `toko` (TOKO SEMBAKO RAHMAT, mode normal/kosong/habis, rolling door, malam), `rumah_julit`, `street` (jalan kampung lengkap, tod day/morning/sore/night), `gudang`, `packing_table`, `phone`, `paket`, `kardus`, `draw_car`, produk warung, `focus_lines`, `pill`, `rain_cloud`, `steam`; CH burahmat, bos |
| `aset_pro.py` | (dulu ep2pro.py) `post` (bloom, grading, grain, vignette), `sun_rays`, `dust`, `puff`, `birds` |
| `aset_mbg.py` | (dulu ep3.py) `dapur_mbg`, `kelas`, `kantor`, `draw_car3` (Gran Max PEMASOK DAPUR MBG), `car_load`, `nota`, `dandang`, `ompreng`, `gembok`, `checklist`, `kontrak`, `alarm`, `uang_terbang`; CH kadapur, koki1-2, murid0-5, guru; `person3` (peci terangkat, rol rambut bergetar) |
| `aset_dio.py` | (dulu bagian umum ep4.py) CH['dio'] final, `set_pucat`, `talk`, `pose_seq`/`backk`, `brosur`, `name_card`, `bubble`, `gloom`, `tanya`, `card`, `ribbon`, `coin_pop`, `smoke`, `confetti`, `lightning`, `rain`, `watchers`, `street` (dua tokoh di depan toko, mendukung blur latar), `POS_R=1020`, `POS_D=1360`, `YS=1430`, `rahmat_po`, `dio_po`, `SERIUS` |
| `referensi/` | lembar karakter Pak Bos (`PakBos_lembar_karakter.png`) + skrip pembuatnya (`lembar_pakbos.py`). Pak Bos = `CH['pakbos']` di `aset_dasar.py` (safari krem, badan gendut, kepala besar) |
| `episode/ep4.py` | contoh episode lengkap (adegan, sisipan close-up, akting, efek, suara) |
| `episode/TEMPLATE.py` | kerangka episode baru |
| `kerja/ep<N>/` | file kerja (audio, words.json, hasil render) - tidak disimpan |

Cari fungsi tanpa membaca file utuh: `grep -n "def nama" aset_*.py`.

## Aturan

- Tokoh/lokasi/properti baru: buat di `episode/ep<N>.py`; setelah pengguna setuju, pindahkan ke `aset_*.py` yang cocok.
- Kamera tenang: tanpa whip pan, kilatan putih, handheld, kamera miring; `PUNCH` maks 2.
- Sensor nama jika diminta: "tiiit" 1000 Hz + balok hitam.

## Catatan migrasi

- Hasil ep 4 lewat master identik piksel dengan `ep4plus.py` lama (diuji 25 frame), kecuali satu perbaikan:
  gerak mulut ikut suara (`talk`) dulu selalu 0 karena amplop audio dipotong ke durasi ep 1; sekarang berfungsi.
- `aset_*` tidak lagi membaca `words.json`; teks narasi hanya dibaca `gaya.py`.
