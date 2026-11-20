"""Audio GranMaxTanjakan: lagu MP3 + raungan mesin asli dari video.

  0 - 1.6 dtk   cold open: raungan mesin saja (+ desir naik ke hentakan pertama)
  1.6 dtk       lagu masuk (utuh 14.36 dtk), mesin tetap terdengar pelan di bawahnya
  lagu diputar 3 putaran (sambungan crossfade 20 ms), end card di drop putaran 3, lalu fade out
Raungan mesin ikut speed ramp gambar: saat slow-mo suaranya melambat & jadi lebih berat.

Pemakaian: python3 scripts/make_tanjakan_audio.py
  butuh assets/lagu_tanjakan.mp3 dan assets/mesin_tanjakan.wav
  (mesin: ffmpeg -i video.mp4 -vn -ac 2 -ar 44100 assets/mesin_tanjakan.wav)
Output: public/tanjakan_audio.wav
"""
import json
import os
import subprocess
import wave

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
TL = json.load(open(os.path.join(ROOT, "src", "tanjakan.json")))
FPS = TL["fps"]
TOTAL = TL["durationInFrames"] / FPS
N = int(round(TOTAL * SR))
SONG = TL["song"]
rng = np.random.default_rng(3)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).reshape(-1, 2).astype(np.float64) / 32768.0


def filt(x, f, kind="low"):
    return sosfilt(butter(2, f, btype=kind, fs=SR, output="sos"), x, axis=0)


def place(tr, sig, t, g=1.0):
    i = int(round(t * SR))
    j = min(len(tr), i + len(sig))
    if i < len(tr):
        tr[i:j] += sig[: j - i] * g


# ------------------------------------------------------------------ lagu
song = load(os.path.join(ROOT, "assets", "lagu_tanjakan.mp3"))
cold, end, passes = SONG["cold"], SONG["end"], SONG["passes"]
music = np.zeros((N, 2))
one = song[: int(round(end * SR))]
xf = int(0.02 * SR)                      # crossfade 20 ms di tiap sambungan putaran
seq = one.copy()
for _ in range(passes - 1):
    ramp = np.linspace(0, 1, xf)[:, None]
    seam = seq[-xf:] * (1 - ramp) + one[:xf] * ramp
    seq = np.concatenate([seq[:-xf], seam, one[xf:]])
place(music, seq, cold)

# ------------------------------------------------------------------ mesin (ikut speed ramp)
eng = load(os.path.join(ROOT, "assets", "mesin_tanjakan.wav")).mean(axis=1)
fmap = np.array(TL["map"]) / TL["srcFps"]          # detik sumber per frame keluaran
tout = np.arange(N) / SR
src_t = np.interp(tout * FPS, np.arange(len(fmap)), fmap)
eng_out = np.interp(src_t * SR, np.arange(len(eng)), eng)
duck = np.ones(N)                                  # anti klik di tiap potongan
w_ = int(0.012 * SR)
for s in TL["shots"][1:]:
    i = int(s["f"] / FPS * SR)
    duck[max(0, i - w_):i] = np.linspace(1, 0, min(w_, i))
    duck[i:i + w_] = np.linspace(0, 1, len(duck[i:i + w_]))
eng_out = filt(eng_out, 50, "high") * duck
eng_out /= np.abs(eng_out).max()
card = TL["cta"]["f"] / FPS
pts = [(0, 0.0), (0.25, 1.4), (cold, 1.7), (cold + 0.4, 0.32), (card - 1, 0.3), (card, 0.12), (TOTAL, 0.0)]
eng_out *= np.interp(tout, [p[0] for p in pts], [p[1] for p in pts])

# ------------------------------------------------------------------ sfx kecil
def riser(dur):
    n = int(dur * SR)
    x = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    for i in range(0, n, 1024):
        fc = 400 + 6000 * x[i] ** 2
        out[i:i + 1024] = sosfilt(butter(2, [fc * 0.7, min(fc * 1.4, 20000)], "band", fs=SR, output="sos"),
                                  noise[i:i + 1024])
    return out * x ** 2.5


def whoosh(dur=0.5):
    n = int(dur * SR)
    x = np.linspace(0, 1, n)
    out = filt(rng.standard_normal(n), [500, 5000], "band")
    return out * np.sin(np.pi * x) ** 3


sfx = np.zeros(N)
r = riser(cold - 0.1)
place(sfx, r / np.abs(r).max(), 0.1, 0.35)
for s in TL["shots"]:
    if s["in"] == "whip":
        wh = whoosh()
        place(sfx, wh / np.abs(wh).max(), s["f"] / FPS - 0.25, 0.22)

# ------------------------------------------------------------------ mix & master
mix = music * 0.9 + (eng_out * 0.5)[:, None] + (sfx * 0.6)[:, None]
fade = np.ones(N)
nf = int(1.6 * SR)
fade[-nf:] = np.linspace(1, 0, nf) ** 1.5
mix *= fade[:, None]
mix = np.tanh(mix * 1.2) / np.tanh(1.2)            # limiter lembut
mix *= 0.95 / np.abs(mix).max()
out = os.path.join(ROOT, "public", TL["audio"])
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("saved", out, f"{TOTAL:.2f} dtk")
