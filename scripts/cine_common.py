"""Fungsi bersama untuk menyusun timeline JSON komposisi sinematik (src/Cinematic.tsx).

Lagu: assets/lagu_tanjakan.mp3 (150 BPM, 14.36 dtk). Struktur (detik lagu):
  0.05-2.04 intro bass | 2.04-6.76 break | 6.76 DROP, hentakan bass 8.21 9.98 10.44 10.59 12.19
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 60
SRC_FPS = 30
COLD = 1.6           # cold open (4 ketukan) sebelum lagu masuk
SONG_END = 14.355    # panjang lagu (36 ketukan)
# hentakan bass lagu -> kilatan putih (detik lagu, kekuatan)
BASS_HITS = [(0.05, 1.0), (6.78, 1.0), (8.21, 0.5), (9.98, 0.45), (10.44, 0.35), (10.59, 0.5), (12.19, 0.6)]
# kick drum di bagian drop -> denyut cahaya halus
KICKS = [6.82, 7.02, 7.42, 7.72, 8.01, 8.42, 9.02, 9.32, 9.61, 9.81, 10.01, 10.61, 10.91, 11.22, 11.61,
         12.21, 12.52, 12.7, 13.01, 13.21, 13.83, 14.12]


def v(p, ts):
    """(putaran 0.., detik lagu) -> detik video."""
    return COLD + p * SONG_END + ts


def fr(sec):
    return int(round(sec * FPS))


def smooth(x):
    return x * x * (3 - 2 * x)


def compile_timeline(name, shots_in, texts_in, cta_in, impacts, pulses, passes, src_frames, engine_bed=0.32, fps=60):
    """shots_in: (detik_video, detik_sumber, r0, r1, transisi, ekstra). Simpan src/<name>.json."""
    global FPS
    FPS = fps
    total = fr(COLD + passes * SONG_END)
    starts = [fr(s[0]) for s in shots_in] + [total]
    shots, fmap = [], []
    for i, (t, t0, r0, r1, tr, extra) in enumerate(shots_in):
        f0, f1 = starts[i], starts[i + 1]
        n = f1 - f0
        pos = t0 * SRC_FPS
        for k in range(n):
            fmap.append(round(min(pos, src_frames - 1.001), 3))
            pos += (r0 + (r1 - r0) * smooth(k / max(1, n - 1))) * SRC_FPS / FPS
        print(f"shot {i:2d}: video {f0 / FPS:5.2f}-{f1 / FPS:5.2f}  sumber {t0:5.2f}-{pos / SRC_FPS:5.2f} dtk  {tr}")
        shots.append({"f": f0, "d": n, "in": tr, "r0": r0, **extra})
    texts = [{"f": fr(a), "d": fr(b) - fr(a), "style": st, **d} for a, b, st, d in texts_in]
    cta = dict(cta_in)
    cta["f"] = fr(cta.pop("start"))
    cta["d"] = total - cta["f"]
    imp = [{"f": fr(t), "k": k} for t, k in impacts]
    hit = {x["f"] for x in imp}
    pul = [{"f": fr(t), "k": k} for t, k in pulses if all(abs(fr(t) - h) > 6 for h in hit)]
    out = {
        "fps": FPS, "srcFps": SRC_FPS, "durationInFrames": total, "audio": f"{name}_audio.wav",
        "song": {"cold": COLD, "end": SONG_END, "passes": passes, "engineBed": engine_bed},
        "shots": shots, "texts": texts, "cta": cta, "map": fmap, "impacts": imp, "pulses": pul,
    }
    path = os.path.join(ROOT, "src", f"{name}.json")
    json.dump(out, open(path, "w"), separators=(",", ":"))
    print("saved", path, f"{total} frame = {total / FPS:.2f} dtk")
