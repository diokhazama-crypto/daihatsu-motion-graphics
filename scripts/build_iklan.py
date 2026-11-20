"""Susun src/iklan.json untuk komposisi GranMaxIklan (gaya iklan profesional).

Musik 96 BPM -> 1 bar = 2.5 dtk = 75 frame. Semua posisi ditulis dalam BAR.
Jalankan: python3 scripts/build_iklan.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
BAR_F = 75
DUR = 1815  # 60.5 dtk


def fr(bar):
    return int(round(bar * BAR_F))


# (bar_mulai, klip, detik_sumber, transisi, ekstra)
# transisi: dissolve | slide | zoom | black (dip ke hitam) | none
SHOTS = [
    (0, "pu_silver", 4.75, "none", {"rate": 0.6}),
    (2, "pu_silver", 39.3, "black", {"rate": 0.6}),
    (4, "pu_silver", 8.75, "dissolve", {"rate": 0.7}),
    (5, "pu_silver", 32.55, "slide", {"rate": 0.7}),
    (6, "pu_silver", 25.1, "dissolve", {"rate": 0.7}),
    (7, "pu_silver", 36.1, "slide", {"rate": 0.7}),
    (8, "pu_silver", 12.6, "dissolve", {"rate": 0.7}),
    (9, "detail", 28.0, "dissolve", {"rate": 0.9}),
    (10, "detail", 20.0, "slide", {"rate": 0.9}),
    (11, "detail", 37.0, "dissolve", {"rate": 0.9}),
    (12, "detail", 85.0, "black", {"rate": 0.8}),
    (13, "detail", 95.5, "dissolve", {"rate": 0.9}),
    (14, "spbu", 1.0, "black", {"rate": 0.9}),
    (16, "pasar", 0.2, "dissolve", {"rate": 0.85}),
    (17, "pasar", 4.6, "slide", {"rate": 0.85}),
    (18, "spbu", 18.0, "dissolve", {"rate": 0.9}),
    (19, "blindvan", 32.0, "zoom", {"rate": 0.6}),
    (20, "blindvan", 50.8, "dissolve", {"rate": 0.8}),
    (21, "pu_silver", 40.0, "dissolve", {"rate": 0.55}),
    (22, "blindvan", 50.4, "black", {"rate": 0.5, "blur": 16, "dim": 0.5}),
]

# Bagian gelap (kedip hitam) di klip pu_silver -> potongan digeser otomatis
DIPS = {"pu_silver": [4.0, 8.0, 12.1, 16.5, 20.9, 24.6, 28.3, 31.8, 35.4, 38.9]}
PREROLL = 0.75  # transisi mulai +-0.6 dtk sebelum potongan


def avoid_dips(clip, t, dur, rate):
    for _ in range(40):
        a, b = t - PREROLL * rate, t + dur * rate
        hit = [d for d in DIPS.get(clip, []) if a - 0.05 < d + 0.3 and d - 0.05 < b]
        if not hit:
            return t
        t = round(max(hit) + 0.35 + PREROLL * rate, 2)
    return t


# (bar_mulai, bar_selesai, gaya, data)
TEXTS = [
    (0.2, 1.9, "intro", {"a": "Setiap usaha", "b": "butuh partner yang bisa diandalkan."}),
    (2.15, 3.95, "title", {"top": "DAIHATSU", "main": "GRAN MAX", "sub": "PICK UP  ·  BLIND VAN"}),
    (4.15, 4.95, "lower", {"cat": "DESAIN", "main": "Bak luas & kokoh", "sub": "Siap angkut muatan harian"}),
    (5.15, 5.95, "lower", {"cat": "MESIN", "main": "1.5L Dual VVT-i", "sub": "Bertenaga & efisien"}),
    (6.15, 7.95, "lower", {"cat": "DAYA ANGKUT", "main": "Dimensi bak lega", "sub": "Bongkar muat lebih praktis"}),
    (8.15, 8.95, "lower", {"cat": "KABIN", "main": "Lega & ergonomis", "sub": "Nyaman untuk perjalanan jauh"}),
    (9.15, 10.95, "lower", {"cat": "FITUR", "main": "AC & Power Steering", "sub": "Dingin, ringan, tidak bikin capek"}),
    (11.15, 11.95, "lower", {"cat": "FITUR", "main": "Head unit audio", "sub": "Teman di setiap perjalanan"}),
    (12.15, 13.95, "statement", {"a": "Dirancang untuk", "b": "kerja keras."}),
    (14.2, 15.9, "statement", {"a": "Terbukti", "b": "di lapangan."}),
    (16.15, 17.95, "lower", {"cat": "PERFORMA", "main": "Muatan maksimal", "sub": "Tetap stabil & bandel"}),
    (18.15, 18.95, "lower", {"cat": "ANDALAN", "main": "Pedagang & pengusaha", "sub": "Dari pasar sampai gudang"}),
    (19.15, 20.95, "lower", {"cat": "VARIAN", "main": "Tersedia Blind Van", "sub": "Ruang kargo tertutup & aman"}),
    (21.1, 21.95, "tagline", {"main": "GRAN MAX", "sub": "Teman setia usaha Anda."}),
]

CTA = {
    "bar": 22,
    "brand": "DAIHATSU GRAN MAX",
    "tag": "Teman setia usaha Anda.",
    "promo": ["Promo Akhir Tahun", "DP Ringan", "Angsuran Bersahabat"],
    "contact": "Informasi & pemesanan",
    "name": "DIO DAIHATSU",
    "phone": "0822-5699-6949",
    "fine": "*Syarat & ketentuan berlaku",
}

TR_LEN = {"dissolve": 18, "slide": 20, "zoom": 18, "black": 24, "none": 0}


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
    cta["f"] = fr(cta.pop("bar"))
    cta["d"] = DUR - cta["f"]
    out = {"fps": FPS, "barFrames": BAR_F, "durationInFrames": DUR, "shots": shots, "texts": texts, "cta": cta,
           "bars": [fr(b) for b in range(25)]}
    path = os.path.join(ROOT, "src", "iklan.json")
    json.dump(out, open(path, "w"), indent=1)
    print("saved", path)


if __name__ == "__main__":
    build()
