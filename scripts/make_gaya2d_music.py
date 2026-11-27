"""Musik ceria ala kartun 2D (disintesis dari nol, bebas hak cipta) untuk komposisi Gaya2D.

120 BPM, 30 fps -> 1 ketukan = 15 frame, 1 bar = 60 frame (2 detik).
  bar 0       intro: glockenspiel + riser
  bar 1-20    10 gaya x 2 bar: ukulele/pluck, bass, kick-clap, hi-hat, 'pop' tiap ganti gaya
  bar 21-22   penutup: akor akhir + 'ding'
Output: public/gaya2d_music.wav
"""
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
BEAT = 0.5
BAR = 2.0
BARS = 23
N = int((BARS * BAR + 0.5) * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(7)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i : i + len(sig)] += sig * (1 - pan) ** 0.5 * 1.0
    R[i : i + len(sig)] += sig * (1 + pan) ** 0.5 * 1.0


def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def pluck(m, dur=0.45, d=0.18):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * np.sin(6 * np.pi * f * t)
    return s * env(n, 0.003, d) * 0.18


def glock(m, dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t)
    return s * env(n, 0.002, 0.35) * 0.16


def bass(m, dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.tanh(2.2 * np.sin(2 * np.pi * f * t))
    return s * env(n, 0.004, 0.25) * 0.26


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.7


def clap():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    nz = np.diff(np.concatenate([[0], nz]))  # cerahkan
    e = np.exp(-t * 22) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    return nz * e * 0.16


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    nz = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    return nz * np.exp(-t * (14 if open_ else 70)) * 0.07


def pop():
    """Bunyi 'blup' kartun tiap ganti gaya."""
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = 300 + 900 * (t / 0.16)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.07) * 0.35


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    nz = np.diff(np.concatenate([[0], rng.standard_normal(n)]))
    return nz * (t / dur) ** 2 * 0.12


# Progresi akor C - Am - F - G (1 bar per akor)
CHORDS = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]
ROOTS = [48, 45, 41, 43]
MELODY = [  # (ketukan dalam 2 bar, nada) motif riang
    (0, 72), (1, 76), (1.5, 79), (2.5, 76), (3, 74), (4, 72), (5, 74), (5.5, 76), (6.5, 72), (7, 67),
]

# Intro
for k, m in enumerate([72, 76, 79, 84]):
    add(glock(m), k * BEAT, pan=0.3 * (k % 2 * 2 - 1))
add(riser(BAR), 0)

for bar in range(1, 21):
    t0 = bar * BAR
    c = (bar - 1) % 4
    # strum ukulele: 'down, down-up, up-down-up'
    for b, vel in [(0, 1), (1, 0.7), (1.5, 0.6), (2.5, 0.6), (3, 0.8), (3.5, 0.6)]:
        for j, m in enumerate(CHORDS[c]):
            add(pluck(m + 12), t0 + b * BEAT + j * 0.012, pan=-0.25, gain=vel)
    # bass
    for b in [0, 1.5, 2, 3]:
        add(bass(ROOTS[c] - 12 + (7 if b == 3 else 0)), t0 + b * BEAT)
    # drum
    for b in range(4):
        add(kick(), t0 + b * BEAT, gain=1 if b % 2 == 0 else 0.75)
        if b % 2 == 1:
            add(clap(), t0 + b * BEAT, pan=0.1)
        add(hat(), t0 + (b + 0.5) * BEAT, pan=0.4)
    add(hat(True), t0 + 3.5 * BEAT, pan=0.4)
    # melodi glock tiap pasangan bar (bar ganjil = awal gaya)
    if (bar - 1) % 2 == 0:
        add(pop(), t0, gain=1)
        if bar > 2:  # lagu mulai ramai setelah gaya pertama
            for b, m in MELODY:
                add(glock(m + (0 if (bar // 2) % 2 else 2 if m < 76 else 0), 0.8), t0 + b * BEAT, pan=0.35, gain=0.8)

# Penutup
t0 = 21 * BAR
for j, m in enumerate([48, 60, 64, 67, 72]):
    add(pluck(m, 2.5, 0.9), t0 + j * 0.03, gain=1.2)
add(bass(36, 2.0), t0)
add(kick(), t0)
add(glock(84, 2.5), t0 + BEAT * 2)
add(glock(91, 2.5), t0 + BEAT * 2.5)

mix = np.stack([L, R], 1)
mix /= np.max(np.abs(mix)) / 0.89
fade = int(0.4 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
out = os.path.join(ROOT, "public", "gaya2d_music.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("OK", out, round(len(mix) / SR, 2), "detik")
