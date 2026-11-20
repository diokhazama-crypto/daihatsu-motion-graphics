"""Susun src/tanjakan.json untuk komposisi GranMaxTanjakan (cinematic TikTok, 60 fps, +-45 dtk).

Sumber gambar: 1 video HP (Gran Max angkut sawit di tanjakan), dibersihkan dari teks
bawaan oleh scripts/clean_pov.py lalu dipecah jadi frame JPG di public/tanjakan/ (30 fps).
Musik: assets/lagu_tanjakan.mp3 (150 BPM, 14.36 dtk). Struktur lagu (detik lagu):
  0.05-2.04  intro bass berat
  2.04-6.76  break / build-up (tanpa bass)
  6.76       DROP. Bass masuk lagi (hentakan) di 8.21, 9.98, 10.44, 10.59, 12.19
Urutan video: [cold open 1.6 dtk: raungan mesin] + lagu 3 putaran:
  putaran 1  hook: muatan 2.900 kg, medan, KUAT / BANDEL / TANGGUH
  putaran 2  cerita: andalan kerja, TANJAKAN? LEWAT. JALAN RUSAK? LIBAS.
  putaran 3  hero Gran Max Pick Up + end card dealer
Semua potongan ditulis sebagai (putaran, detik lagu) supaya pas dengan ketukan.

Speed ramp: tiap shot punya kecepatan awal & akhir (r0 -> r1). Peta frame sumber (pecahan)
dihitung di sini; komposisi mem-blend 2 frame tetangga supaya slow-mo halus.
Jalankan: python3 scripts/build_tanjakan.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 60
SRC_FPS = 30
SRC_FRAMES = 1875            # jumlah frame di public/tanjakan/
COLD = 1.6                   # cold open (4 ketukan) sebelum lagu masuk
SONG_END = 14.355            # panjang lagu (36 ketukan)
PASSES = 3
END = COLD + PASSES * SONG_END


def v(p, ts):
    """(putaran 0..2, detik lagu) -> detik video."""
    return COLD + p * SONG_END + ts


def fr(sec):
    return int(round(sec * FPS))


# (detik_video_mulai, detik_sumber, kecepatan_awal, kecepatan_akhir, transisi_masuk, ekstra)
# transisi: black | flash | whip | punch | glitch | cut ; ekstra: zoom, build, blur, dim
SHOTS = [
    (0.0, 5.0, 0.55, 0.55, "black", {}),                       # cold open: tanjakan berbatu
    # ---- putaran 1: hook
    (v(0, 0.05), 24.0, 0.25, 0.8, "flash", {"zoom": 1.2}),     # BOOM: muatan 2.900 kg
    (v(0, 2.04), 13.4, 0.5, 0.45, "whip", {}),                 # bak bergoyang di jalan rusak
    (v(0, 3.65), 6.6, 0.55, 0.5, "whip", {}),                  # batu-batu menanjak
    (v(0, 5.25), 2.0, 0.7, 1.6, "whip", {}),                   # build-up: makin cepat
    (v(0, 6.05), 40.0, 1.4, 2.6, "cut", {"build": 1}),         # zoom & blur menuju drop
    (v(0, 6.78), 29.5, 1.0, 0.6, "flash", {"zoom": 1.16}),     # DROP: KUAT.
    (v(0, 7.58), 33.0, 1.0, 0.6, "punch", {"zoom": 1.22}),     # BANDEL.
    (v(0, 8.21), 36.6, 1.0, 0.55, "punch", {"zoom": 1.14}),    # TANGGUH.
    (v(0, 9.01), 48.6, 0.55, 0.7, "whip", {}),                 # gerbang estate
    (v(0, 9.98), 44.0, 1.0, 1.0, "glitch", {"zoom": 1.1}),     # stutter
    (v(0, 10.44), 15.0, 1.0, 1.0, "glitch", {"zoom": 1.25}),
    (v(0, 10.59), 50.0, 0.45, 0.75, "flash", {}),              # lewat gerbang
    (v(0, 12.19), 26.6, 0.5, 0.35, "flash", {"zoom": 1.1}),    # muatan dari dekat, slow-mo
    # ---- putaran 2: cerita
    (v(1, 0.05), 0.0, 0.5, 1.0, "flash", {"zoom": 1.15}),      # kelokan jalan tanah
    (v(1, 2.04), 17.0, 0.45, 0.4, "whip", {}),                 # slow-mo sinematik
    (v(1, 3.65), 20.3, 0.45, 0.4, "whip", {}),
    (v(1, 5.25), 31.0, 0.7, 1.6, "whip", {}),                  # build-up 2
    (v(1, 6.05), 37.6, 1.4, 2.6, "cut", {"build": 1}),
    (v(1, 6.78), 9.0, 1.0, 0.6, "flash", {"zoom": 1.18}),      # TANJAKAN?
    (v(1, 7.58), 11.0, 1.0, 0.6, "punch", {"zoom": 1.2}),      # LEWAT.
    (v(1, 8.21), 3.8, 1.0, 0.6, "punch", {"zoom": 1.15}),      # JALAN RUSAK?
    (v(1, 9.01), 22.0, 0.7, 0.6, "punch", {"zoom": 1.22}),     # LIBAS.
    (v(1, 9.98), 42.0, 1.0, 1.0, "glitch", {"zoom": 1.1}),     # stutter
    (v(1, 10.44), 28.0, 1.0, 1.0, "glitch", {"zoom": 1.25}),
    (v(1, 10.59), 45.5, 0.45, 0.7, "flash", {}),
    (v(1, 12.19), 34.3, 0.5, 0.35, "flash", {"zoom": 1.1}),
    # ---- putaran 3: hero + end card
    (v(2, 0.05), 57.0, 0.25, 0.6, "flash", {"zoom": 1.2}),     # Gran Max berbelok
    (v(2, 2.04), 58.1, 0.3, 0.3, "whip", {"zoom": 1.06}),      # profil samping, slow-mo
    (v(2, 6.76), 59.6, 0.25, 0.2, "flash", {"blur": 18, "dim": 0.45}),  # latar end card
]

# (detik_video_mulai, detik_video_selesai, gaya, data)
TEXTS = [
    (0.15, v(0, 0.0), "pov", {"a": "POV: raungan Gran Max", "b": "di tanjakan"}),
    # putaran 1
    (v(0, 0.05), v(0, 2.0), "counter", {"value": 2900, "unit": "KG", "sub": "MUATAN SAWIT · SEKALI JALAN"}),
    (v(0, 2.14), v(0, 3.6), "lower", {"cat": "MEDAN", "main": "TANAH & BATU", "sub": "Menanjak tanpa ragu"}),
    (v(0, 3.75), v(0, 5.2), "lower", {"cat": "TENAGA", "main": "TETAP NGEGAS", "sub": "Muatan penuh, tetap jalan"}),
    (v(0, 5.3), v(0, 6.7), "suspense", {"a": "Gas terus..."}),
    (v(0, 6.78), v(0, 7.56), "punch", {"w": "KUAT."}),
    (v(0, 7.58), v(0, 8.19), "punch", {"w": "BANDEL."}),
    (v(0, 8.21), v(0, 8.98), "punch", {"w": "TANGGUH."}),
    (v(0, 9.1), v(0, 12.1), "statement", {"a": "Bukan sekadar", "b": "PICK UP."}),
    (v(0, 12.25), v(0, 14.3), "statement", {"a": "Ini partner", "b": "CARI NAFKAH."}),
    # putaran 2
    (v(1, 0.05), v(1, 2.0), "lower", {"cat": "ANDALAN", "main": "PETANI SAWIT", "sub": "Dari kebun sampai tujuan"}),
    (v(1, 2.14), v(1, 3.6), "lower", {"cat": "BAK", "main": "LEGA & KUAT", "sub": "Angkut banyak sekali jalan"}),
    (v(1, 3.75), v(1, 5.2), "lower", {"cat": "KENDALI", "main": "STABIL", "sub": "Di jalan bergelombang"}),
    (v(1, 5.3), v(1, 6.7), "suspense", {"a": "Masih ragu?"}),
    (v(1, 6.78), v(1, 7.56), "punch", {"w": "TANJAKAN?"}),
    (v(1, 7.58), v(1, 8.19), "punch", {"w": "LEWAT."}),
    (v(1, 8.21), v(1, 8.98), "punch", {"w": "JALAN RUSAK?", "size": 190}),
    (v(1, 9.01), v(1, 9.95), "punch", {"w": "LIBAS."}),
    (v(1, 10.65), v(1, 12.1), "statement", {"a": "Muatan berat", "b": "BUKAN MASALAH."}),
    (v(1, 12.25), v(1, 14.3), "statement", {"a": "Kerja keras", "b": "SETIAP HARI."}),
    # putaran 3
    (v(2, 0.1), v(2, 6.6), "hero", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "PICK UP · TANGGUH DI SEGALA MEDAN"}),
]

CTA = {
    "brand": "DAIHATSU GRAN MAX",
    "tag": "Teman setia usaha Anda.",
    "promo": ["Promo Akhir Tahun", "DP Ringan", "Angsuran Bersahabat"],
    "contact": "Informasi & pemesanan",
    "name": "DIO DAIHATSU",
    "phone": "0822-5699-6949",
    "fine": "*Syarat & ketentuan berlaku",
}

# kilatan putih (flash) di hentakan bass - detik video: kekuatan 0..1
IMPACTS = [(v(p, t), k) for p in (0, 1) for t, k in
           [(0.05, 1.0), (6.78, 1.0), (8.21, 0.5), (9.98, 0.45), (10.44, 0.35), (10.59, 0.5), (12.19, 0.6)]]
IMPACTS += [(v(2, 0.05), 1.0), (v(2, 6.76), 0.8)]


def smooth(x):
    return x * x * (3 - 2 * x)


def build():
    total = fr(END)
    starts = [fr(s[0]) for s in SHOTS] + [total]
    shots, fmap = [], []
    for i, (t, t0, r0, r1, tr, extra) in enumerate(SHOTS):
        f0, f1 = starts[i], starts[i + 1]
        n = f1 - f0
        pos = t0 * SRC_FPS
        for k in range(n):
            fmap.append(round(min(pos, SRC_FRAMES - 1.001), 3))
            pos += (r0 + (r1 - r0) * smooth(k / max(1, n - 1))) * SRC_FPS / FPS
        print(f"shot {i:2d}: video {f0 / FPS:5.2f}-{f1 / FPS:5.2f}  sumber {t0:5.2f}-{pos / SRC_FPS:5.2f} dtk  {tr}")
        shots.append({"f": f0, "d": n, "in": tr, **extra})
    texts = [{"f": fr(a), "d": fr(b) - fr(a), "style": st, **d} for a, b, st, d in TEXTS]
    cta = dict(CTA, f=fr(v(2, 6.76) + 0.15))
    cta["d"] = total - cta["f"]
    out = {
        "fps": FPS, "srcFps": SRC_FPS, "durationInFrames": total, "audio": "tanjakan_audio.wav",
        "song": {"cold": COLD, "end": SONG_END, "passes": PASSES},
        "shots": shots, "texts": texts, "cta": cta, "map": fmap,
        "impacts": [{"f": fr(t), "k": k} for t, k in IMPACTS],
    }
    path = os.path.join(ROOT, "src", "tanjakan.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print("saved", path, f"{total} frame = {total / FPS:.2f} dtk")


if __name__ == "__main__":
    build()
