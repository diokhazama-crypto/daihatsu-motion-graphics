"""Susun src/timeline.json berdasarkan grid ketukan lagu (bukan detik).

Semua potongan ditulis dalam nomor ketukan (n). Ketukan n jatuh di
    t(n) = T0 + n * BEAT  (detik)
Lagu: 130 BPM, ketukan "jedug" terkuat di awal tiap bar (n kelipatan 4).
Jalankan: python3 scripts/build_timeline.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 60
T0 = 0.10521          # ketukan pertama di lagu (detik)
BEAT = 0.461525       # 130 BPM
TOTAL_SEC = 60.38     # panjang music.wav (lihat prep_music.py)
DUR = int(round(TOTAL_SEC * FPS))
LAST_BEAT = 128


def fr(n):
    """frame untuk ketukan n (boleh pecahan)."""
    if n <= 0:
        return 0
    return int(round((T0 + n * BEAT) * FPS))


# Bagian lagu (dalam ketukan). Lagu diputar 1x penuh + diulang sampai ketukan 128.
SECTIONS = {
    "a1": (0, 32),        # drop pertama
    "break1": (32, 40),   # jeda
    "b1": (40, 72),       # drop kedua
    "a2": (72, 104),      # (loop) drop pertama lagi
    "break2": (104, 112), # jeda
    "b2": (112, 129),     # penutup
}

# (ketukan_mulai, klip, detik_sumber, transisi, ekstra)
# Catatan: pu_silver punya kedip hitam (~0.3 dtk) di 4.0, 8.0, 12.1, 16.5, 20.9,
# 24.6, 28.3, 31.8, 35.4, 38.9 detik -> jangan ambil potongan yang melewati titik itu.
SHOTS = [
    # --- A1: hook cepat 1 ketukan per shot
    (0, "pu_silver", 5.4, "zoom"),
    (1, "detail", 97.0, "whip"),
    (2, "pu_silver", 32.3, "zoom"),
    (3, "spbu", 3.0, "whip"),
    (4, "pasar", 5.0, "zoom"),
    (5, "blindvan", 46.0, "whip"),
    (6, "detail", 37.0, "zoom"),
    (7, "pu_silver", 8.35, "whip"),
    # judul
    (8, "pu_silver", 40.2, "flash"),
    (12, "pu_silver", 4.4, "whip"),
    (14, "pu_silver", 6.4, "zoom"),
    (16, "pu_silver", 35.8, "spin"),
    (18, "pu_silver", 24.9, "whip"),
    (20, "pu_silver", 28.6, "zoom"),
    (22, "pu_silver", 32.3, "flash"),
    (24, "pu_silver", 8.4, "whip"),
    (26, "pu_silver", 26.0, "zoom"),
    (28, "pu_silver", 41.0, "whip"),
    (29, "detail", 136.0, "zoom"),
    (30, "pu_silver", 4.6, "whip"),
    (31, "detail", 98.0, "zoom"),
    # --- break1: Blind Van
    (32, "blindvan", 50.5, "fade"),
    (36, "blindvan", 8.5, "zoom"),
    (38, "blindvan", 18.6, "whip"),
    (39, "pu_silver", 10.8, "zoom"),
    # --- B1: fitur, 2 ketukan per shot
    (40, "detail", 28.0, "flash"),
    (42, "detail", 21.0, "whip"),
    (44, "detail", 39.0, "zoom"),
    (46, "pu_silver", 17.6, "whip"),
    (48, "detail", 75.0, "spin"),
    (50, "detail", 86.0, "whip"),
    (52, "pu_silver", 22.6, "zoom"),
    (54, "blindvan", 22.5, "whip"),
    (56, "detail", 6.0, "zoom"),
    (58, "detail", 99.0, "whip"),
    (60, "detail", 103.0, "zoom"),
    (62, "detail", 128.0, "spin"),
    (64, "pu_silver", 28.6, "whip"),
    (66, "pu_silver", 36.0, "zoom"),
    (68, "detail", 136.5, "whip"),
    (70, "pu_silver", 41.0, "zoom"),
    # --- A2: bukti di lapangan
    (72, "spbu", 10.0, "flash"),
    (76, "pasar", 0.2, "whip"),
    (78, "spbu", 20.0, "zoom"),
    (80, "pasar", 4.0, "whip"),
    (82, "spbu", 27.0, "spin"),
    (84, "pasar", 7.5, "whip"),
    (86, "detail", 135.0, "zoom"),
    (88, "pasar", 10.5, "flash"),
    (92, "spbu", 6.0, "whip"),
    (94, "pasar", 13.5, "zoom"),
    (96, "detail", 100.0, "whip"),
    (98, "blindvan", 47.5, "spin"),
    (100, "pu_silver", 36.5, "whip"),
    (101, "spbu", 24.0, "zoom"),
    (102, "pasar", 12.0, "whip"),
    (103, "pu_silver", 41.5, "zoom"),
    # --- break2
    (104, "spbu", 0.5, "fade", {"rate": 0.8, "dim": 0.4}),
    # stutter menjelang drop (dalam ketukan pecahan)
    (110, "pasar", 9.0, "cut"),
    (110.25, "black", 0, "cut"),
    (110.5, "spbu", 20.0, "cut"),
    (110.75, "black", 0, "cut"),
    (111, "pu_silver", 41.0, "cut"),
    (111.25, "black", 0, "cut"),
    (111.5, "pasar", 12.0, "cut"),
    (111.75, "black", 0, "cut"),
    # --- B2: hero + CTA
    (112, "pu_silver", 39.6, "flash", {"rate": 0.7}),
    (116, "blindvan", 50.0, "zoom", {"rate": 0.5, "blur": 14, "dim": 0.45}),
]

# (mulai, selesai, gaya, baris, ekstra)
TEXTS = [
    (0, 4, "kicker", ["BUTUH MOBIL", "BUAT KERJA?"]),
    (4, 8, "kicker", ["YANG TANGGUH", "& IRIT?"]),
    (8, 12, "title", ["GRAN MAX"], {"sub": "PICK UP 1.5"}),
    (12, 14, "word", ["TANGGUH"]),
    (14, 16, "word", ["BANDEL"]),
    (16, 18, "word", ["IRIT"]),
    (18, 22, "word", ["BAK LUAS"]),
    (22, 24, "word", ["1.5L VVT-i"]),
    (24, 28, "word", ["SIAP", "KERJA"]),
    (32, 36, "title", ["BLIND VAN"], {"sub": "JUGA READY"}),
    (40, 42, "chip", ["AC DINGIN"], {"head": "FITUR"}),
    (42, 44, "chip", ["POWER STEERING"], {"head": "FITUR"}),
    (44, 46, "chip", ["AUDIO"], {"head": "FITUR"}),
    (46, 50, "chip", ["KABIN LEGA"], {"head": "FITUR"}),
    (50, 54, "chip", ["JOK NYAMAN"], {"head": "FITUR"}),
    (54, 58, "chip", ["PRAKTIS & KOKOH"], {"head": "FITUR"}),
    (58, 62, "chip", ["BAK RATA & KUAT"], {"head": "FITUR"}),
    (62, 64, "chip", ["DETAIL RAPI"], {"head": "FITUR"}),
    (64, 68, "word", ["SIAP", "TEMPUR"]),
    (68, 72, "word", ["SIAP", "CUAN"]),
    (72, 76, "title", ["GAS TERUS!"], {"sub": "BUKTI DI LAPANGAN"}),
    (76, 80, "word", ["SAYUR", "SEGUNUNG"]),
    (80, 84, "word", ["MUATAN", "MAKSIMAL"]),
    (84, 88, "word", ["TETAP", "STABIL"]),
    (88, 92, "title", ["ANDALAN"], {"sub": "PARA PENGUSAHA"}),
    (92, 96, "word", ["KERJA KERAS"]),
    (96, 100, "word", ["UNTUNG DERAS"]),
    (100, 104, "word", ["PILIHAN", "TEPAT"]),
    (104.3, 110, "kicker", ["MAU USAHA", "MAKIN LANCAR?"]),
    (112, 116, "hero", ["GRAN MAX"], {"sub": "PICK UP • BLIND VAN"}),
]

CTA = {
    "start": 116,
    "head": "PROMO AKHIR TAHUN",
    "line1": "DP RINGAN",
    "line2": "ANGSURAN BERSAHABAT",
    "name": "DIO DAIHATSU",
    "phone": "0822-5699-6949",
    "note": "Chat WA sekarang!",
}

# ketukan mana yang "keras" (untuk denyut zoom): sesuai energi bass di lagu
LOUD = ["a1", "b1", "a2", "b2"]


# Bagian gelap (kedip hitam) di klip sumber, detik. Potongan digeser otomatis menjauhinya.
DIPS = {"pu_silver": [4.0, 8.0, 12.1, 16.5, 20.9, 24.6, 28.3, 31.8, 35.4, 38.9]}
PREROLL = 0.5  # transisi halus mulai +-0.4 dtk sebelum ketukan


def avoid_dips(clip, t, dur, rate):
    for _ in range(40):
        a, b = t - PREROLL * rate, t + dur * rate
        hit = [d for d in DIPS.get(clip, []) if a - 0.05 < d + 0.3 and d - 0.05 < b]
        if not hit:
            return t
        t = round(max(hit) + 0.35 + PREROLL * rate, 2)
    return t


def build():
    shots = []
    for i, s in enumerate(SHOTS):
        n, clip, t, tr = s[:4]
        extra = s[4] if len(s) > 4 else {}
        n_next = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else None
        f0 = fr(n)
        f1 = fr(n_next) if n_next is not None else DUR
        t2 = avoid_dips(clip, t, (f1 - f0) / FPS, extra.get("rate", 1))
        if t2 != t:
            print(f"  geser {clip} {t} -> {t2} (hindari kedip hitam)")
            t = t2
        d = {"f": f0, "d": f1 - f0, "clip": clip, "t": t, "in": tr}
        d.update(extra)
        shots.append(d)

    texts = []
    for s in TEXTS:
        a, b, style, lines = s[:4]
        extra = s[4] if len(s) > 4 else {}
        d = {"f": fr(a), "d": fr(b) - fr(a), "style": style, "lines": lines}
        d.update(extra)
        texts.append(d)

    cta = dict(CTA)
    st = cta.pop("start")
    cta["f"] = fr(st)
    cta["d"] = DUR - cta["f"]
    cta["steps"] = [fr(st + k) - fr(st) for k in range(8)]
    cta["lastBeat"] = fr(LAST_BEAT)

    beats = []
    for n in range(0, LAST_BEAT + 1):
        sec_name = next(k for k, (a, b) in SECTIONS.items() if a <= n < b)
        w = 0.0
        if sec_name in LOUD and fr(n) < cta["f"]:
            w = {0: 1.0, 1: 0.45, 2: 0.7, 3: 0.75}[n % 4]
        elif sec_name in LOUD:
            w = 0.35 if n % 4 == 0 else 0.0
        beats.append({"f": fr(n), "w": w})

    out = {
        "fps": FPS,
        "bpm": 130,
        "durationInFrames": DUR,
        "sections": {k: [fr(a), fr(b) if b <= LAST_BEAT else DUR] for k, (a, b) in SECTIONS.items()},
        "drops": [fr(8), fr(40), fr(72), fr(112)],
        "leaks": [fr(8), fr(32), fr(40), fr(72), fr(112), cta["f"]],
        "stutter": [fr(110), fr(112)],
        "beats": beats,
        "shots": shots,
        "texts": texts,
        "cta": cta,
    }
    path = os.path.join(ROOT, "src", "timeline.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print("saved", path, "frames", DUR, "shots", len(shots))


if __name__ == "__main__":
    build()
