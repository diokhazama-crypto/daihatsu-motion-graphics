"""Susun src/iklan.json untuk komposisi GranMaxIklan (gaya iklan profesional).

Musik = lagu MP3 (public/music.wav dari prep_music.py), 130 BPM.
Potongan di awal bar (tiap 4 ketukan) -> tenang tapi tetap sinkron lagu.
Jalankan: python3 scripts/build_iklan.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
# Grid ketukan lagu MP3 (sama dengan build_timeline.py / prep_music.py)
T0 = 0.10521
BEAT = 0.461525  # 130 BPM, 1 bar = 4 ketukan = 1.846 dtk
DUR = 1811       # = panjang public/music.wav (60.36 dtk)
MUSIC = "music.wav"


def fr(n):
    """frame untuk ketukan n (bar k = ketukan 4k)."""
    return 0 if n <= 0 else int(round((T0 + n * BEAT) * FPS))


# Struktur lagu (ketukan): 0-31 drop | 32-39 jeda | 40-71 drop | 72-103 (ulang) drop
#                          | 104-111 jeda | 112-128 penutup
# (ketukan_mulai, klip, detik_sumber, transisi, ekstra)
# transisi: dissolve | slide | zoom | black (dip ke hitam) | none
SHOTS = [
    (0, "pu_silver", 4.8, "none", {"rate": 0.75}),
    (8, "pu_silver", 39.7, "black", {"rate": 0.7}),
    (16, "pu_silver", 8.88, "dissolve", {"rate": 0.8}),
    (20, "pu_silver", 32.67, "slide", {"rate": 0.8}),
    (24, "pu_silver", 25.48, "dissolve", {"rate": 0.8}),
    (28, "pu_silver", 36.27, "slide", {"rate": 0.8}),
    # jeda lagu
    (32, "detail", 95.5, "black", {"rate": 0.8}),
    # drop 2: fitur
    (40, "pu_silver", 12.97, "dissolve", {"rate": 0.8}),
    (44, "detail", 28.0, "dissolve", {"rate": 0.9}),
    (48, "detail", 20.0, "slide", {"rate": 0.9}),
    (52, "detail", 37.0, "dissolve", {"rate": 0.9}),
    (56, "detail", 85.0, "slide", {"rate": 0.9}),
    (60, "detail", 101.0, "dissolve", {"rate": 0.9}),
    (64, "pu_silver", 29.05, "slide", {"rate": 0.8}),
    (68, "detail", 135.5, "dissolve", {"rate": 0.9}),
    # lagu diulang: bukti di lapangan
    (72, "spbu", 1.0, "black", {"rate": 0.9}),
    (80, "pasar", 0.2, "dissolve", {"rate": 0.9}),
    (84, "pasar", 4.6, "slide", {"rate": 0.9}),
    (88, "spbu", 18.0, "dissolve", {"rate": 0.9}),
    (92, "pasar", 10.5, "slide", {"rate": 0.9}),
    (96, "blindvan", 32.0, "zoom", {"rate": 0.75}),
    (100, "blindvan", 50.8, "dissolve", {"rate": 0.8}),
    # jeda 2: tagline
    (104, "pu_silver", 40.0, "black", {"rate": 0.6}),
    # penutup
    (112, "pu_silver", 39.6, "dissolve", {"rate": 0.35, "blur": 16, "dim": 0.5}),
]

# Bagian gelap (kedip hitam) di klip pu_silver -> potongan digeser otomatis
DIPS = {"pu_silver": [4.0, 8.0, 12.1, 16.5, 20.9, 24.6, 28.3, 31.8, 35.4, 38.9]}
PREROLL = 0.5  # transisi mulai +-0.45 dtk sebelum potongan


def avoid_dips(clip, t, dur, rate):
    for _ in range(40):
        a, b = t - PREROLL * rate, t + dur * rate
        hit = [d for d in DIPS.get(clip, []) if a - 0.05 < d + 0.3 and d - 0.05 < b]
        if not hit:
            return t
        t = round(max(hit) + 0.35 + PREROLL * rate, 2)
    return t


# (ketukan_mulai, ketukan_selesai, gaya, data)
TEXTS = [
    (0.6, 7.6, "intro", {"a": "Setiap usaha", "b": "butuh partner yang bisa diandalkan."}),
    (8.5, 15.6, "title", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "PICK UP  ·  BLIND VAN"}),
    (16.4, 19.7, "lower", {"cat": "DESAIN", "main": "Bak luas & kokoh", "sub": "Siap angkut muatan harian"}),
    (20.4, 23.7, "lower", {"cat": "MESIN", "main": "1.5L Dual VVT-i", "sub": "Bertenaga & efisien"}),
    (24.4, 31.7, "lower", {"cat": "DAYA ANGKUT", "main": "Dimensi bak lega", "sub": "Bongkar muat lebih praktis"}),
    (32.5, 39.6, "statement", {"a": "Dirancang untuk", "b": "kerja keras."}),
    (40.4, 43.7, "lower", {"cat": "KABIN", "main": "Lega & ergonomis", "sub": "Nyaman untuk perjalanan jauh"}),
    (44.4, 51.7, "lower", {"cat": "FITUR", "main": "AC & Power Steering", "sub": "Dingin, ringan, tidak bikin capek"}),
    (52.4, 55.7, "lower", {"cat": "FITUR", "main": "Head unit audio", "sub": "Teman di setiap perjalanan"}),
    (56.4, 59.7, "lower", {"cat": "KENYAMANAN", "main": "Jok empuk & rapi", "sub": "Betah seharian di jalan"}),
    (60.4, 67.7, "lower", {"cat": "DAYA TAHAN", "main": "Bak rata & kuat", "sub": "Dibuat untuk dipakai kerja"}),
    (68.4, 71.7, "lower", {"cat": "SIAP KERJA", "main": "Langsung jalan", "sub": "Dari dealer ke tempat usaha"}),
    (72.5, 79.6, "statement", {"a": "Terbukti", "b": "di lapangan."}),
    (80.4, 87.7, "lower", {"cat": "PERFORMA", "main": "Muatan maksimal", "sub": "Tetap stabil & bandel"}),
    (88.4, 95.7, "lower", {"cat": "ANDALAN", "main": "Pedagang & pengusaha", "sub": "Dari pasar sampai gudang"}),
    (96.4, 103.7, "lower", {"cat": "VARIAN", "main": "Tersedia Blind Van", "sub": "Ruang kargo tertutup & aman"}),
    (104.5, 111.7, "tagline", {"main": "GRAN MAX", "sub": "Teman setia usaha Anda."}),
]

CTA = {
    "beat": 112,
    "brand": "DAIHATSU GRAN MAX",
    "tag": "Teman setia usaha Anda.",
    "promo": ["Promo Akhir Tahun", "DP Ringan", "Angsuran Bersahabat"],
    "contact": "Informasi & pemesanan",
    "name": "DIO DAIHATSU",
    "phone": "0811-549-6949",
    "fine": "*Syarat & ketentuan berlaku",
}

TR_LEN = {"dissolve": 12, "slide": 14, "zoom": 12, "black": 20, "none": 0}


def build():
    shots = []
    for i, s in enumerate(SHOTS):
        bar, clip, t, tr = s[:4]
        extra = s[4] if len(s) > 4 else {}
        f0 = fr(bar)
        f1 = fr(SHOTS[i + 1][0]) if i + 1 < len(SHOTS) else DUR
        rate = extra.get("rate", 1)
        t2 = avoid_dips(clip, t, (f1 - f0) / FPS, rate)
        if t2 != t:
            print(f"  geser {clip} {t} -> {t2}")
        d = {"f": f0, "d": f1 - f0, "clip": clip, "t": t2, "in": tr, "ov": TR_LEN[tr]}
        d.update(extra)
        shots.append(d)
    texts = [{"f": fr(a), "d": fr(b) - fr(a), "style": st, **data} for a, b, st, data in TEXTS]
    cta = dict(CTA)
    cta["f"] = fr(cta.pop("beat"))
    cta["d"] = DUR - cta["f"]
    out = {"fps": FPS, "durationInFrames": DUR, "music": MUSIC, "shots": shots, "texts": texts, "cta": cta,
           "bars": [fr(4 * k) for k in range(33)]}
    path = os.path.join(ROOT, "src", "iklan.json")
    json.dump(out, open(path, "w"), indent=1)
    print("saved", path)


if __name__ == "__main__":
    build()
