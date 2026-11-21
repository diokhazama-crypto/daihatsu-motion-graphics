"""Susun src/pickup.json untuk komposisi GranMaxPickup (iklan profesional 9:16, 30 fps, +-45 dtk).

Sumber: 4 klip digabung oleh scripts/prep_multi.py (public/pickup/, offset di src/pickup_clips.json):
  A 16 dtk   Gran Max hitam dimuat sawit di kebun
  B 25 dtk   Gran Max silver bak tinggi melaju di desa (depan, samping, menjauh)
  C 141 dtk  detail ASMR: kunci, kontak, speedometer, setir, dashboard, head unit, jok, bak, mesin, tangki
  D 43 dtk   Gran Max silver baru di showroom (ada kedip gelap di 4.0 8.0 12.1 16.5 20.9 24.6 28.3 31.8 35.4 38.9)
Dihindari: teks bawaan di awal C & D, emblem "1.5" (supaya umum untuk semua tipe), klaim AC.
Konsep "dari showroom sampai kebun", lagu 3 putaran (lihat cine_common.py):
  putaran 1  pembuka + kelebihan 01-03 (kabin, dashboard, mesin), detail cepat di drop
  putaran 2  kelebihan 04-05 (bak, daya angkut), kerja nyata angkut sawit, teks kinetik
  putaran 3  hero, rekap checklist, end card dealer
Jalankan: python3 scripts/build_pickup.py
"""
import json
import os

from cine_common import BASS_HITS, KICKS, ROOT, compile_timeline, v

CL = json.load(open(os.path.join(ROOT, "src", "pickup_clips.json")))


def s(clip, t):
    """detik di klip -> detik di deret gabungan."""
    return CL["offsets"][clip] + t


# (detik_video_mulai, detik_sumber, kecepatan_awal, kecepatan_akhir, transisi_masuk, ekstra)
SHOTS = [
    (0.0, s("C", 6.4), 0.4, 0.4, "black", {}),                     # cold open: kunci (ASMR)
    # ---- putaran 1: showroom & fitur
    (v(0, 0.05), s("D", 39.6), 0.3, 0.6, "flash", {"zoom": 1.2}),   # tampak depan 3/4
    (v(0, 2.04), s("D", 13.2), 0.45, 0.4, "whip", {}),              # 01 kabin
    (v(0, 3.65), s("C", 37.6), 0.5, 0.45, "dissolve", {}),          # 02 dashboard / head unit
    (v(0, 5.25), s("C", 116.6), 0.5, 0.5, "dissolve", {}),          # 03 mesin (kap terbuka)
    (v(0, 6.05), s("C", 21.5), 1.4, 2.6, "cut", {"build": 1}),      # setir -> build-up
    (v(0, 6.78), s("C", 15.0), 1.0, 0.6, "flash", {"zoom": 1.16}),  # DROP: kontak
    (v(0, 7.58), s("C", 18.3), 1.0, 0.6, "punch", {"zoom": 1.2}),   # speedometer
    (v(0, 8.21), s("C", 28.5), 1.0, 0.6, "punch", {"zoom": 1.14}),  # tombol dashboard
    (v(0, 9.01), s("D", 21.5), 0.7, 0.6, "whip", {}),               # jok
    (v(0, 9.98), s("C", 85.0), 1.0, 1.0, "glitch", {"zoom": 1.1}),
    (v(0, 10.44), s("C", 124.5), 1.0, 1.0, "glitch", {"zoom": 1.25}),
    (v(0, 10.59), s("D", 26.0), 0.45, 0.4, "flash", {}),            # 04 bak (showroom)
    (v(0, 12.19), s("D", 36.4), 0.35, 0.3, "flash", {"zoom": 1.08}),
    # ---- putaran 2: kerja nyata
    (v(1, 0.05), s("A", 2.0), 0.3, 0.7, "flash", {"zoom": 1.18}),   # 05 daya angkut: muat sawit
    (v(1, 2.04), s("A", 9.0), 0.45, 0.4, "dissolve", {}),
    (v(1, 3.65), s("B", 1.0), 0.45, 0.4, "dissolve", {}),           # melaju bermuatan
    (v(1, 5.25), s("B", 4.3), 0.45, 0.45, "dissolve", {}),
    (v(1, 6.05), s("B", 6.8), 1.4, 2.6, "cut", {"build": 1}),
    (v(1, 6.78), s("B", 8.2), 1.0, 0.6, "flash", {"zoom": 1.18}),   # MUAT BANYAK.
    (v(1, 7.58), s("A", 12.0), 1.0, 0.6, "punch", {"zoom": 1.2}),   # IRIT.
    (v(1, 8.21), s("B", 14.6), 1.0, 0.6, "punch", {"zoom": 1.15}),  # LINCAH.
    (v(1, 9.01), s("C", 100.0), 0.7, 0.6, "punch", {"zoom": 1.22}), # TANGGUH.
    (v(1, 9.98), s("A", 5.0), 1.0, 1.0, "glitch", {"zoom": 1.1}),
    (v(1, 10.44), s("B", 16.0), 1.0, 1.0, "glitch", {"zoom": 1.25}),
    (v(1, 10.59), s("B", 18.6), 0.45, 0.45, "flash", {}),
    (v(1, 12.19), s("A", 14.0), 0.35, 0.3, "flash", {"zoom": 1.1}),
    # ---- putaran 3: hero + end card
    (v(2, 0.05), s("B", 9.0), 0.25, 0.5, "flash", {"zoom": 1.2}),   # depan, bermuatan
    (v(2, 2.04), s("D", 40.0), 0.3, 0.3, "dissolve", {"blur": 14, "dim": 0.45}),  # latar rekap
    (v(2, 6.76), s("B", 21.0), 0.25, 0.2, "flash", {"blur": 18, "dim": 0.45}),    # latar end card
]

TEXTS = [
    (0.2, v(0, 0.0), "kicker", {"a": "DAIHATSU PRESENTS"}),
    # putaran 1
    (v(0, 0.05), v(0, 2.0), "hero", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "PICK UP · DARI SHOWROOM SAMPAI KEBUN"}),
    (v(0, 2.14), v(0, 3.6), "feature", {"no": "01", "main": "KABIN LEGA", "sub": "Nyaman & ergonomis"}),
    (v(0, 3.75), v(0, 5.2), "feature", {"no": "02", "main": "DASHBOARD PRAKTIS", "sub": "Semua tombol mudah dijangkau"}),
    (v(0, 5.3), v(0, 6.7), "feature", {"no": "03", "main": "MESIN TANGGUH", "sub": "Siap kerja keras setiap hari"}),
    (v(0, 6.78), v(0, 7.56), "punch", {"w": "NYALAKAN."}),
    (v(0, 7.58), v(0, 8.19), "punch", {"w": "GAS."}),
    (v(0, 8.21), v(0, 8.98), "punch", {"w": "KERJA."}),
    (v(0, 10.65), v(0, 14.3), "feature", {"no": "04", "main": "BAK LUAS", "sub": "Lantai rata, mudah bongkar muat"}),
    # putaran 2
    (v(1, 0.1), v(1, 3.55), "feature", {"no": "05", "main": "DAYA ANGKUT BESAR", "sub": "Muat lebih banyak sekali jalan"}),
    (v(1, 3.75), v(1, 6.0), "statement", {"a": "Dari kebun", "b": "SAMPAI TUJUAN."}),
    (v(1, 6.78), v(1, 7.56), "punch", {"w": "MUAT BANYAK."}),
    (v(1, 7.58), v(1, 8.19), "punch", {"w": "IRIT."}),
    (v(1, 8.21), v(1, 8.98), "punch", {"w": "LINCAH."}),
    (v(1, 9.01), v(1, 9.95), "punch", {"w": "TANGGUH."}),
    (v(1, 10.65), v(1, 12.1), "statement", {"a": "Pilihan cerdas", "b": "PENGUSAHA."}),
    (v(1, 12.25), v(1, 14.3), "statement", {"a": "Teman kerja", "b": "SETIAP HARI."}),
    # putaran 3
    (v(2, 0.1), v(2, 2.0), "hero", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "PICK UP · TEMAN SETIA USAHA ANDA"}),
    (v(2, 2.14), v(2, 6.65), "recap", {"top": "KENAPA PILIH", "main": "GRAN MAX?", "items": [
        "Kabin lega", "Dashboard praktis", "Mesin tangguh", "Bak luas", "Daya angkut besar"]}),
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
    compile_timeline("pickup", SHOTS, TEXTS, CTA, IMPACTS, PULSES, passes=3, src_frames=CL["frames"],
                     engine_bed=0.25, fps=30)
