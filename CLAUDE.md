# Aturan tetap: video animasi Pak Rahmat (berlaku otomatis, pengguna tidak perlu mengetik pembuka)

Jika pengguna mengirim audio narasi dan/atau minta "buat ep N" (atau hanya mengirim audio), langsung ikuti aturan ini.
Ini menggantikan membaca PANDUAN_VIDEO_V4 dan MASTER_PAK_RAHMAT di Drive: JANGAN buka Drive untuk episode biasa.

## Dilarang
- Unggah / backup apa pun ke Google Drive (video, MP3, words.json, CATATAN, kode). Hasil cukup dikirim ke pengguna (SendUserFile).
- Membuka arsip episode lama, cerita lain, skill/tool video lain, web search. Pakai kode master saja.
- Membuat banyak versi: langsung PRO PLUS satu kali.
- Menulis ulang kode di chat. Balasan chat maks 5 baris, tanpa rekap langkah.

## Langkah (kode master: `pak-rahmat-master/`, lihat README.md di sana; jangan baca aset_*.py utuh, pakai grep)
1. Terima audio. Jika ada yang kurang jelas, tanya SEKALI dalam satu pesan.
2. `pip install pycairo faster-whisper` lalu `python3 jalankan.py N siap <audio>`. Tampilkan teks polos terkoreksi (nama/merek),
   koreksi `kerja/epN/words.json`. Usulkan kartu penutup 2 pilihan. Tunggu konfirmasi pengguna.
3. Tulis `episode/epN.py` (salin TEMPLATE.py; contoh lengkap ep4.py, ep5.py). Cek: `jalankan.py N cek <dtk...>`, lihat 1-2 gambar saja.
4. Render `python3 jalankan.py N render` (~15-20 menit, jalankan di background, JANGAN jalankan dua kali). Kirim MP4 ke pengguna.
5. Revisi: `render --seg i` (segmen yang berubah saja).
6. Simpan: commit + push kode episode ke git (bukan Drive). Tambah ringkasan episode + cliffhanger ke bagian "Ringkasan" di bawah.

## Gaya PRO PLUS (sudah ada di gaya.py)
9:16 1080x1920 30 fps. Hook detik pertama (close-up + teks besar + garis fokus). Teks per kata putih bergaris hitam, kata aktif kuning,
maks 3 kata/baris, zona aman (x~490, y~1330). KAMERA TENANG: tanpa whip pan, kilatan putih, handheld, kamera miring; zoom hentak (PUNCH) maks 2.
Sound effect + musik ukulele (ducking). Penutup: kartu 2 pilihan + "FOLLOW UNTUK EP N+1". Watermark "PAK RAHMAT SERIES • EP N".
Sensor nama jika diminta: "tiiit" 1000 Hz + balok hitam.

## Cerita Pak Rahmat
- Latar: toko sembako Pak Rahmat, kampung, rumah Bu Julit, dealer Daihatsu (tulisan DAIHATSU merah, tanpa logo). Gran Max pick up putih
  (stiker kuning-merah). Bentuk toko, mobil, tokoh HARUS sama: pakai aset_*.py, jangan gambar ulang.
- Tokoh: Pak Rahmat (peci hitam, kumis, kaos hijau), Bu Rahmat (CH burahmat), anak, Bu Julit (daster ungu, rol rambut pink),
  teman julit (friend), Dio - Sales Daihatsu (CH['dio'], jangan diubah), pembeli b1-b4, Kepala Dapur MBG, koki, murid, guru.
- Awalan nama file: `PakRahmat_GranMax_ep<N>_`.

## Ringkasan episode
- Ep 1: juragan sembako kerja keras, Bu Julit nyinyir; suatu pagi Gran Max baru ternyata milik Pak Rahmat.
- Ep 2: toko kosong dikira bangkrut, ternyata bungkus 200 paket sembako. Cliff: pesanan 500 paket bayar belakangan.
- Ep 3: pemesannya Dapur MBG (pemasok sembako lokal). Cliff: ditawari pasokan rutin tiap pagi, sanggup?
- Ep 4: "nyesel beli Gran Max" ke Mas Dio (sales), ternyata nyesel kenapa nggak dari dulu; mau nambah armada. Cliff: dulu hampir menyerah.
- Ep 5 (84 dtk): kilas balik 3 tahun lalu, modal dibawa kabur pemasok, utang pelanggan numpuk, Bu Julit mengejek; Pak Rahmat narik ojek,
  jaga toko, jual bensin botolan; istri menangis, toko bangkit; Bu Julit datang mau ngutang, "utang yang dulu aja belum lunas".
  Penutup: "masih dibolehin utang?" (BOLEH UTANG / GAK BOLEH). Properti baru di ep5.py: rak_bensin, buku_utang, kaleng_uang, air_mata, sc_ojek.
- Ep 6: (isi setelah dibuat)
