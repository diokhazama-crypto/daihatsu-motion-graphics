"""Susun src/tanjakan.json untuk komposisi GranMaxTanjakan (cinematic TikTok, 60 fps).

Sumber gambar: 1 video HP (Gran Max angkut sawit di tanjakan), dibersihkan dari teks
bawaan oleh scripts/clean_pov.py lalu dipecah jadi frame JPG di public/tanjakan/ (30 fps).
Musik: assets/lagu_tanjakan.mp3 (150 BPM, 14.36 dtk). Struktur lagu (detik lagu):
  0.05-2.04  intro bass berat
  2.04-6.76  break / build-up (tanpa bass)
  6.76       DROP. Bass masuk lagi (hentakan) di 8.21, 9.98, 10.44, 10.59, 12.19
Urutan video:
  [cold open 1.6 dtk: raungan mesin saja] + [lagu utuh] + [lagu diulang dari drop = end card]
Semua potongan ditulis dalam DETIK LAGU supaya pas dengan ketukan.

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
SONG_END = 14.355            # 36 ketukan
DROP = 6.757                 # titik loop: SONG_END - 19 ketukan
END = COLD + SONG_END + (SONG_END - DROP)


def v(ts, loop=False):
    """detik lagu -> detik video."""
    return COLD + (SONG_END + ts - DROP if loop else ts)


def fr(sec):
    return int(round(sec * FPS))


# (detik_video_mulai, detik_sumber, kecepatan_awal, kecepatan_akhir, transisi_masuk, ekstra)
# transisi: black | flash | whip | punch | glitch | cut
SHOTS = [
    (0.0, 5.0, 0.55, 0.55, "black", {}),                     # cold open: tanjakan berbatu
    (v(0.05), 24.0, 0.25, 0.8, "flash", {"zoom": 1.2}),      # BOOM: muatan 2.900 kg
    (v(2.04), 13.4, 0.5, 0.45, "whip", {}),                  # bak bergoyang di jalan rusak
    (v(3.65), 6.6, 0.55, 0.5, "whip", {}),                   # batu-batu menanjak
    (v(5.25), 2.0, 0.7, 1.6, "whip", {}),                    # build-up: makin cepat
    (v(6.05), 40.0, 1.4, 2.6, "cut", {"build": 1}),          # zoom & blur menuju drop
    (v(6.78), 29.5, 1.0, 0.6, "flash", {"zoom": 1.16}),      # DROP: KUAT.
    (v(7.58), 33.0, 1.0, 0.6, "punch", {"zoom": 1.22}),      # BANDEL.
    (v(8.21), 36.6, 1.0, 0.55, "punch", {"zoom": 1.14}),     # TANGGUH.
    (v(9.01), 48.6, 0.55, 0.7, "whip", {}),                  # gerbang estate
    (v(9.98), 44.0, 1.0, 1.0, "glitch", {"zoom": 1.1}),      # stutter
    (v(10.44), 15.0, 1.0, 1.0, "glitch", {"zoom": 1.25}),
    (v(10.59), 50.0, 0.45, 0.75, "flash", {}),               # lewat gerbang
    (v(12.19), 57.0, 0.55, 0.45, "flash", {"zoom": 1.08}),   # hero: Gran Max berbelok
    (v(DROP, True), 58.3, 0.3, 0.25, "flash", {"blur": 18, "dim": 0.45}),  # latar end card
]

# (detik_video_mulai, detik_video_selesai, gaya, data)
TEXTS = [
    (0.15, v(0.0), "pov", {"a": "POV: raungan Gran Max 1.3", "b": "di tanjakan"}),
    (v(0.05), v(2.0), "counter", {"value": 2900, "unit": "KG", "sub": "MUATAN SAWIT · SEKALI JALAN"}),
    (v(2.14), v(3.6), "lower", {"cat": "MESIN", "main": "1.3 LITER", "sub": "Raungannya bikin merinding"}),
    (v(3.75), v(5.2), "lower", {"cat": "MEDAN", "main": "TANAH & BATU", "sub": "Menanjak tanpa ragu"}),
    (v(5.3), v(6.7), "suspense", {"a": "Gas terus..."}),
    (v(6.78), v(7.56), "punch", {"w": "KUAT."}),
    (v(7.58), v(8.19), "punch", {"w": "BANDEL."}),
    (v(8.21), v(8.98), "punch", {"w": "TANGGUH."}),
    (v(9.1), v(12.1), "statement", {"a": "Bukan sekadar", "b": "PICK UP."}),
    (v(12.25), v(14.3), "hero", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "TERBUKTI DI LAPANGAN"}),
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
IMPACTS = [(v(0.05), 1.0), (v(6.78), 1.0), (v(8.21), 0.5), (v(9.98), 0.45), (v(10.44), 0.35),
           (v(10.59), 0.5), (v(12.19), 0.6), (v(DROP, True), 0.7)]


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
    cta = dict(CTA, f=fr(v(DROP, True) + 0.15))
    cta["d"] = total - cta["f"]
    out = {
        "fps": FPS, "srcFps": SRC_FPS, "durationInFrames": total, "audio": "tanjakan_audio.wav",
        "song": {"cold": COLD, "end": SONG_END, "drop": DROP},
        "shots": shots, "texts": texts, "cta": cta, "map": fmap,
        "impacts": [{"f": fr(t), "k": k} for t, k in IMPACTS],
    }
    path = os.path.join(ROOT, "src", "tanjakan.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print("saved", path, f"{total} frame = {total / FPS:.2f} dtk")


if __name__ == "__main__":
    build()
