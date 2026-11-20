"""Susun src/kelebihan.json untuk komposisi GranMaxKelebihan (iklan profesional 9:16, 60 fps, +-45 dtk).

Sumber: video HP Gran Max Pick Up putih, bak kayu tinggi penuh sawit (frame di public/kelebihan/, 30 fps).
Momen sumber yang dipakai (detik):
  A 0-7.5    pick up menjauh di halaman tanah merah (lebar, langit)
  B 8-10.5   close-up belakang: emblem Gran Max + bak penuh sawit
  C 11-17    di tepi jalan, siap masuk aspal
  D 17-21.5  berbelok masuk jalan, kabin putih terlihat
  E 22-25.5  melaju di jalan raya (detik 26+ kamera ke langit -> tidak dipakai)
Lagu 3 putaran (lihat cine_common.py):
  putaran 1  pembuka GRAN MAX + kelebihan 01-03
  putaran 2  kelebihan 04-05 + teks kinetik di drop
  putaran 3  hero, rekap checklist, end card dealer
Semua efek dikunci ke lagu: potongan & kilatan di hentakan bass, denyut cahaya di tiap kick,
transisi dissolve di bagian break (tenang), whip/punch/glitch di bagian drop.
Jalankan: python3 scripts/build_kelebihan.py
"""
from cine_common import BASS_HITS, KICKS, compile_timeline, v

SRC_FRAMES = 768  # pakai sampai detik 25.6 saja

# (detik_video_mulai, detik_sumber, kecepatan_awal, kecepatan_akhir, transisi_masuk, ekstra)
# transisi: black | flash | whip | punch | glitch | dissolve | cut ; ekstra: zoom, build, blur, dim
SHOTS = [
    (0.0, 8.6, 0.35, 0.35, "black", {}),                        # cold open: close-up bak
    # ---- putaran 1
    (v(0, 0.05), 9.4, 0.25, 0.6, "flash", {"zoom": 1.2}),       # emblem Gran Max
    (v(0, 2.04), 11.4, 0.45, 0.4, "whip", {}),                  # 01 daya angkut
    (v(0, 4.4), 2.4, 0.5, 0.45, "dissolve", {}),
    (v(0, 6.05), 5.4, 1.4, 2.6, "cut", {"build": 1}),           # build-up ke drop
    (v(0, 6.78), 17.4, 1.0, 0.6, "flash", {"zoom": 1.16}),      # DROP: 02 mesin tangguh
    (v(0, 7.58), 13.4, 1.0, 0.6, "punch", {"zoom": 1.2}),
    (v(0, 8.21), 8.3, 1.0, 0.6, "punch", {"zoom": 1.14}),
    (v(0, 9.01), 22.5, 0.7, 0.6, "whip", {}),
    (v(0, 9.98), 1.0, 1.0, 1.0, "glitch", {"zoom": 1.1}),
    (v(0, 10.44), 10.0, 1.0, 1.0, "glitch", {"zoom": 1.25}),
    (v(0, 10.59), 19.3, 0.5, 0.45, "flash", {}),                # 03 lincah: berbelok
    (v(0, 12.19), 20.4, 0.45, 0.4, "flash", {"zoom": 1.08}),
    # ---- putaran 2
    (v(1, 0.05), 22.1, 0.3, 0.7, "flash", {"zoom": 1.18}),      # 04 irit
    (v(1, 2.04), 0.3, 0.45, 0.4, "dissolve", {}),
    (v(1, 3.65), 14.4, 0.45, 0.4, "dissolve", {}),              # 05 perawatan mudah
    (v(1, 5.25), 6.2, 0.5, 0.5, "dissolve", {}),
    (v(1, 6.05), 9.0, 1.4, 2.6, "cut", {"build": 1}),
    (v(1, 6.78), 12.0, 1.0, 0.6, "flash", {"zoom": 1.18}),      # MUAT BANYAK.
    (v(1, 7.58), 24.0, 1.0, 0.6, "punch", {"zoom": 1.2}),       # IRIT.
    (v(1, 8.21), 18.4, 1.0, 0.6, "punch", {"zoom": 1.15}),      # LINCAH.
    (v(1, 9.01), 8.8, 0.7, 0.6, "punch", {"zoom": 1.22}),       # TANGGUH.
    (v(1, 9.98), 16.0, 1.0, 1.0, "glitch", {"zoom": 1.1}),
    (v(1, 10.44), 4.0, 1.0, 1.0, "glitch", {"zoom": 1.25}),
    (v(1, 10.59), 22.8, 0.45, 0.45, "flash", {}),
    (v(1, 12.19), 9.8, 0.35, 0.3, "flash", {"zoom": 1.1}),
    # ---- putaran 3
    (v(2, 0.05), 18.0, 0.25, 0.5, "flash", {"zoom": 1.2}),      # hero
    (v(2, 2.04), 12.4, 0.3, 0.3, "dissolve", {"blur": 14, "dim": 0.45}),  # latar rekap
    (v(2, 6.76), 3.0, 0.25, 0.2, "flash", {"blur": 18, "dim": 0.45}),     # latar end card
]

# (detik_video_mulai, detik_video_selesai, gaya, data)
TEXTS = [
    (0.2, v(0, 0.0), "kicker", {"a": "DAIHATSU PRESENTS"}),
    # putaran 1
    (v(0, 0.05), v(0, 2.0), "hero", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "5 KELEBIHAN UNTUK USAHA ANDA"}),
    (v(0, 2.14), v(0, 6.0), "feature", {"no": "01", "main": "DAYA ANGKUT BESAR", "sub": "Bak lega, muat lebih banyak sekali jalan"}),
    (v(0, 6.78), v(0, 10.4), "feature", {"no": "02", "main": "MESIN TANGGUH", "sub": "Tetap bertenaga membawa beban berat"}),
    (v(0, 10.65), v(0, 14.3), "feature", {"no": "03", "main": "LINCAH", "sub": "Mudah bermanuver, gesit di jalan sempit"}),
    # putaran 2
    (v(1, 0.1), v(1, 3.55), "feature", {"no": "04", "main": "IRIT BAHAN BAKAR", "sub": "Biaya operasional lebih hemat"}),
    (v(1, 3.75), v(1, 6.0), "feature", {"no": "05", "main": "PERAWATAN MUDAH", "sub": "Suku cadang mudah didapat & terjangkau"}),
    (v(1, 6.78), v(1, 7.56), "punch", {"w": "MUAT BANYAK."}),
    (v(1, 7.58), v(1, 8.19), "punch", {"w": "IRIT."}),
    (v(1, 8.21), v(1, 8.98), "punch", {"w": "LINCAH."}),
    (v(1, 9.01), v(1, 9.95), "punch", {"w": "TANGGUH."}),
    (v(1, 10.65), v(1, 12.1), "statement", {"a": "Pilihan cerdas", "b": "PENGUSAHA."}),
    (v(1, 12.25), v(1, 14.3), "statement", {"a": "Investasi", "b": "JANGKA PANJANG."}),
    # putaran 3
    (v(2, 0.1), v(2, 2.0), "hero", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "PICK UP · TEMAN SETIA USAHA ANDA"}),
    (v(2, 2.14), v(2, 6.65), "recap", {"top": "KENAPA PILIH", "main": "GRAN MAX?", "items": [
        "Daya angkut besar", "Mesin tangguh", "Lincah bermanuver", "Irit bahan bakar", "Perawatan mudah"]}),
]

CTA = {
    "start": v(2, 6.76) + 0.15,
    "brand": "DAIHATSU GRAN MAX",
    "tag": "Teman setia usaha Anda.",
    "promo": ["Promo Akhir Tahun", "DP Ringan", "Angsuran Bersahabat"],
    "contact": "Informasi & pemesanan",
    "name": "DIO DAIHATSU",
    "phone": "0811-549-6949",
    "fine": "*Syarat & ketentuan berlaku",
}

IMPACTS = [(v(p, t), k) for p in (0, 1) for t, k in BASS_HITS] + [(v(2, 0.05), 1.0), (v(2, 6.76), 0.8)]
PULSES = [(v(p, t), 0.22) for p in (0, 1) for t in KICKS]

if __name__ == "__main__":
    compile_timeline("kelebihan", SHOTS, TEXTS, CTA, IMPACTS, PULSES, passes=3, src_frames=SRC_FRAMES, engine_bed=0.22)
