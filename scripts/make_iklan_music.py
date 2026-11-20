"""Musik iklan cinematic (bebas hak cipta, disintesis dari nol) untuk GranMaxIklan.

96 BPM -> 1 bar = 2.5 detik = 75 frame. 24 bar = 60 detik.
  bar 0-3   intro: pad hangat + piano arpeggio
  bar 4-11  piano + bass + beat lembut
  bar 12-13 tarik napas: pad + riser
  bar 14-21 penuh: string pad terang, kick, clap halus, bass berdenyut
  bar 22-23 penutup: hit rendah + piano & pad memudar
Output: public/iklan_music.wav
"""
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
BPM = 96
BEAT = 60 / BPM
BAR = BEAT * 4
TOTAL = 60.5
N = int(TOTAL * SR)
rng = np.random.default_rng(11)


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f):
    return sosfilt(butter(2, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)


def bp(x, a, b):
    return sosfilt(butter(2, [a, b], btype="band", fs=SR, output="sos"), x)


def place(tr, sig, t, g=1.0):
    i = int(t * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    tr[i:j] += sig[: j - i] * g


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# --------------------------------------------------------------- instrumen
def piano(m, dur=2.2, vel=1.0):
    f = midi(m)
    t = tt(dur)
    s = np.zeros(len(t))
    for h, a in [(1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06), (6, 0.03)]:
        fh = f * h * (1 + 0.0004 * h * h)
        s += a * np.sin(2 * np.pi * fh * t + rng.random()) * np.exp(-t * (1.6 + 0.9 * h))
    att = np.minimum(1, t / 0.004)
    hammer = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 120) * 0.03
    return (s * att + hammer) * 0.22 * vel


def supersaw(f, t, v=7, det=0.25):
    out = np.zeros(len(t))
    for k in range(v):
        d = 1 + det * 0.01 * (k - (v - 1) / 2)
        out += 2 * ((f * d * t + rng.random()) % 1) - 1
    return out / v


def pad(notes, dur, bright=1400, amp=0.16):
    t = tt(dur)
    s = sum(supersaw(midi(m), t) for m in notes) / len(notes)
    s = lp(s, bright)
    env = np.minimum(1, t / 0.9) * np.clip((dur - t) / 0.9, 0, 1)
    return s * env * amp


def strings(notes, dur, amp=0.13):
    t = tt(dur)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.2 * t)
    s = np.zeros(len(t))
    for m in notes:
        f = midi(m)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        for h, a in [(1, 1), (2, 0.5), (3, 0.33), (4, 0.25), (5, 0.2)]:
            s += a * np.sin(h * ph + rng.random())
    s = lp(s / len(notes), 3200)
    env = np.minimum(1, t / 0.6) * np.clip((dur - t) / 0.6, 0, 1)
    return s * env * amp


def bass(m, dur, amp=0.32):
    t = tt(dur)
    f = midi(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.01) * np.exp(-t * 2.2)
    return s * env * amp


def kick(amp=0.7):
    t = tt(0.5)
    f = 48 + 90 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    return np.tanh(s * 1.5) * amp


def clap(amp=0.25):
    t = tt(0.35)
    n = rng.standard_normal(len(t))
    env = sum((t >= o) * np.exp(-(t - o).clip(0) * (80 if k < 2 else 14)) for k, o in enumerate([0, 0.012, 0.024]))
    return bp(n, 1000, 4000) * env * amp


def shaker(amp=0.08):
    t = tt(0.09)
    return hp(rng.standard_normal(len(t)), 6000) * np.exp(-t * 45) * np.minimum(1, t / 0.01) * amp


def riser(d):
    t = tt(d)
    n = rng.standard_normal(len(t))
    out = np.zeros(len(t))
    seg = int(0.05 * SR)
    for i in range(0, len(t), seg):
        p = i / len(t)
        lo = 400 + 5000 * p ** 1.5
        out[i:i + seg] = bp(n[i:i + seg], lo, min(lo * 2, 16000))
    return out * (t / d) ** 2.2 * 0.35


def boom(amp=0.9):
    t = tt(3.5)
    s = np.sin(2 * np.pi * (34 + 40 * np.exp(-t * 6)) * t) * np.exp(-t * 1.4)
    air = lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 2.5) * 0.25
    return np.tanh((s + air) * 1.3) * amp


def reverse_swell(d=1.6):
    t = tt(d)
    n = bp(rng.standard_normal(len(t)), 2000, 9000)
    return n * (t / d) ** 3 * 0.2


# --------------------------------------------------------------- aransemen
# Progresi: Fmaj7 - G - Em7 - Am (tiap bar), dalam C mayor
CH = [
    (41, [65, 69, 72, 76]),  # Fmaj7
    (43, [67, 71, 74, 79]),  # G
    (40, [64, 67, 71, 74]),  # Em7
    (45, [69, 72, 76, 81]),  # Am
]
MEL = [  # melodi piano (offset beat, midi) per bar
    [(0, 81), (1.5, 79), (2, 76), (3, 77)],
    [(0, 79), (1.5, 74), (2, 76), (3, 74)],
    [(0, 76), (1.5, 74), (2, 71), (3, 72)],
    [(0, 76), (2, 72), (3, 74)],
]

music = np.zeros(N)
drums = np.zeros(N)
fx = np.zeros(N)
sc = np.ones(N)

for b in range(24):
    t0 = b * BAR
    root, notes = CH[b % 4]
    intro = b < 4
    mid = 4 <= b < 12
    breath = 12 <= b < 14
    full = 14 <= b < 22
    end = b >= 22

    if not end:
        place(music, pad(notes, BAR + 0.9, 1100 if intro or breath else 1800), t0, 1.0)
    if full:
        place(music, strings([n + 12 for n in notes[1:]], BAR + 0.6), t0, 1.0)

    # piano arpeggio 8th
    if not end and not breath:
        arp = [notes[0], notes[1], notes[2], notes[3], notes[2], notes[1], notes[2], notes[3]]
        for k, m in enumerate(arp):
            place(music, piano(m, 1.6, 0.55 if intro else 0.45), t0 + k * BEAT / 2)
    if breath:
        for k, m in enumerate(notes):
            place(music, piano(m, 3.0, 0.5), t0 + k * BEAT)
    # melodi
    if mid or full:
        for off, m in MEL[b % 4]:
            place(music, piano(m + (12 if full else 0), 2.5, 0.9), t0 + off * BEAT)
    # bass
    if mid:
        place(music, bass(root, BAR * 0.95), t0)
    if full:
        for k in range(8):
            place(music, bass(root, BEAT / 2 * 0.95, 0.26), t0 + k * BEAT / 2)
    # drum lembut
    if mid:
        for k in range(4):
            if k in (0, 2):
                place(drums, kick(0.55), t0 + k * BEAT)
            for s16 in range(2):
                place(drums, shaker(0.06 + 0.03 * s16), t0 + (k + s16 / 2 + 0.5) * BEAT)
    if full:
        for k in range(4):
            place(drums, kick(0.75), t0 + k * BEAT)
            i = int((t0 + k * BEAT) * SR)
            dk = np.linspace(0.45, 1, int(0.25 * SR)) ** 1.4
            j = min(N, i + len(dk))
            sc[i:j] = np.minimum(sc[i:j], dk[: j - i])
            if k in (1, 3):
                place(drums, clap(0.22), t0 + k * BEAT)
            for s16 in range(4):
                place(drums, shaker(0.05 + 0.03 * (s16 % 2)), t0 + (k + s16 / 4) * BEAT)

# penutup: akor terakhir panjang
end_t = 22 * BAR
place(music, pad([53, 57, 60, 64], 5.5, 1500, 0.2), end_t)
for k, m in enumerate([53, 60, 64, 69, 72]):
    place(music, piano(m, 4.5, 0.7), end_t + k * 0.12)

# efek
place(fx, reverse_swell(1.6), 2 * BAR - 1.6)       # menuju judul
place(fx, boom(0.55), 2 * BAR)                        # judul
place(fx, riser(BAR * 2), 12 * BAR)                   # menuju bagian penuh
place(fx, boom(0.7), 14 * BAR)
place(fx, reverse_swell(2.0), end_t - 2.0)
place(fx, boom(0.85), end_t)                          # end card

# reverb sederhana (IR noise eksponensial)
ir_t = tt(2.4)
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 2.6)
ir = lp(ir, 6000)
ir /= np.sqrt(np.sum(ir ** 2))
wet = fftconvolve(music, ir)[:N]

mix = (music * 0.75 + wet * 0.45) * sc + drums * 0.8 + fx
mix = hp(mix, 28)
mix /= np.percentile(np.abs(mix), 99.95) + 1e-9
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.9
fi = int(0.02 * SR)
mix[:fi] *= np.linspace(0, 1, fi)
fo = int(2.0 * SR)
mix[-fo:] *= np.linspace(1, 0, fo) ** 2

# stereo: reverb sedikit dilebarkan
d = int(0.017 * SR)
L = mix.copy()
R = mix.copy()
R[d:] += wet[:-d] * 0.06
L[:-d] += wet[d:] * 0.06
st = np.stack([L, R], 1)
st /= np.max(np.abs(st)) / 0.9
out = os.path.join(ROOT, "public", "iklan_music.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("saved", out)
