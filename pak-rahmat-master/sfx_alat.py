"""ALAT SUARA: generator sound effect + musik ukulele + ducking (dulu sfx_ep4pro.py).
Episode menulis fungsi suara(S) yang memanggil:
  S.musik([(t0, t1, S.section(durasi, bpm, chords, bass, pola, gain, padon, bright)), ...])
  S.put(sinyal, detik, gain)        sound effect      (mis. S.put(S.pop(), 2.4, .3))
  S.put_amb(sinyal, detik, gain)    suasana (burung, hujan, jangkrik) dengan fade
  S.diam(t0, t1)                    musik dipelankan (mis. awal kilas balik)
Lalu jalankan.py memanggil S.campur() -> mix_pro.wav (suara narasi + sfx + suasana + musik ber-ducking).
Akord siap pakai: C/CB (ceria), F/FB, Am/AmB (tegang), SLOWAm/SLOWB (sedih); pola FULL atau [0,1,2,3]."""
import numpy as np, subprocess, wave

SR = 44100
DUR = 68.0
N = int(DUR * SR)
rng = np.random.default_rng(5)

def T(d): return np.arange(int(d * SR)) / SR

def bandnoise(d, lo, hi):
    n = int(d * SR)
    x = rng.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n)
    return y / (np.abs(y).max() + 1e-9)

def lowpass(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))

def env_ad(n, a, d_tau):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d_tau)
    return e

def saw(f, t):
    ph = np.cumsum(np.broadcast_to(f, t.shape) / SR)
    return 2 * (ph % 1) - 1

# ---------------- generators
def whoosh(d=0.45):
    t = T(d); n = len(t)
    x = bandnoise(d, 300, 6000)
    # sweeping emphasis
    X = np.fft.rfft(x)
    e = np.sin(np.pi * t / d) ** 2
    y = lowpass(x * e, 2500) * 1.6
    return y * e

def pop():
    t = T(.12)
    f = 300 + 700 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)

def ding(f0=1568, d=1.4):
    t = T(d)
    y = sum(a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-t * (2.5 + m)) for m, a in ((1, 1), (2.01, .4), (3.02, .2), (4.1, .1)))
    return y * np.minimum(1, t / .003)

def chime():
    out = np.zeros(int(1.8 * SR))
    for i, f in enumerate([523.25, 659.25, 783.99, 1046.5, 1318.5]):
        d = ding(f, 1.4) * .5
        s = int(i * .07 * SR); out[s:s + len(d)] += d[:len(out) - s]
    return out

def clink():
    t = T(.18)
    f = rng.uniform(3200, 5200)
    return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.48 * t)) * np.exp(-t * 28)

def thud():
    t = T(.35)
    f = 55 + 90 * np.exp(-t * 25)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    y[:300] += rng.standard_normal(300) * .4 * np.linspace(1, 0, 300)
    return y

def boing():
    t = T(.6)
    f = 180 + 260 * (1 - np.exp(-t * 10)) + 60 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * np.minimum(1, t / .005)

def brass(f, d):
    t = T(d)
    vib = 1 + .006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / .3)
    y = saw(f * vib, t) + .5 * saw(f * 2.003 * vib, t)
    y = lowpass(y, 1400)
    e = np.minimum(1, t / .03) * np.minimum(1, (d - t) / .08)
    return y * e * .5

def dun_dun():
    out = np.zeros(int(1.6 * SR))
    for st, f, d in ((0, 146.8, .22), (.28, 138.6, .22), (.56, 110, .9)):
        b = brass(f, d) + .6 * brass(f / 2, d)
        s = int(st * SR); out[s:s + len(b)] += b
    return out

def sad_trombone():
    out = np.zeros(int(2.6 * SR))
    for st, f, d in ((0, 196, .42), (.45, 185, .42), (.9, 174.6, .42), (1.35, 164.8, 1.2)):
        t = T(d)
        vib = 1 + (.03 * np.sin(2 * np.pi * 6 * t) if d > 1 else 0) - .02 * (t / d)
        y = saw(f * vib, t); y = lowpass(y, 900)
        e = np.minimum(1, t / .05) * np.minimum(1, (d - t) / .1)
        s = int(st * SR); out[s:s + len(y)] += y * e * .55
    return out

def engine(d, f0, f1, rough=.3):
    t = T(d)
    f = np.linspace(f0, f1, len(t)) * (1 + .03 * np.sin(2 * np.pi * 7 * t))
    y = saw(f, t) * .6 + saw(f * .5, t) * .4
    y = lowpass(y, 420) + rough * lowpass(rng.standard_normal(len(t)), 300)
    return y / (np.abs(y).max() + 1e-9)

def motorbike(d):
    t = T(d)
    f = 95 * (1 + .05 * np.sin(2 * np.pi * 3 * t))
    y = saw(f, t) * .5 + saw(f * 2, t) * .3
    return lowpass(y, 1100) * np.minimum(1, t / .1) * np.minimum(1, (d - t) / .2)

def squeal(d=.45):
    t = T(d)
    f = 2400 * (1 + .015 * np.sin(2 * np.pi * 30 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** .5 * .5

def click():
    y = np.zeros(int(.25 * SR))
    y[:500] = rng.standard_normal(500) * np.linspace(1, 0, 500)
    t = T(.25); y += .6 * np.sin(2 * np.pi * 120 * t) * np.exp(-t * 30)
    return y

def jingle(d=.7):
    out = np.zeros(int((d + .2) * SR))
    for k in range(14):
        s = int(rng.uniform(0, d) * SR); c = clink() * rng.uniform(.3, .8)
        out[s:s + len(c)] += c[:len(out) - s]
    return out

def crickets(d):
    t = T(d)
    y = np.zeros(len(t))
    for f0, rate, ph in ((4300, 2.1, 0), (4700, 1.6, .5), (3900, 2.6, .2)):
        chirp = (np.sin(2 * np.pi * 28 * t) > .2).astype(float) * (np.sin(2 * np.pi * rate * t + ph * 6) > .55)
        y += np.sin(2 * np.pi * f0 * t) * lowpass(chirp, 300) * .3
    return y

def birds(d, n=8):
    out = np.zeros(int(d * SR))
    for k in range(n):
        st = rng.uniform(0, d - .5); L = rng.uniform(.08, .18)
        t = T(L); f = rng.uniform(2200, 3600) + rng.uniform(-900, 900) * np.sin(np.pi * t / L)
        c = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / L)
        for r in range(rng.integers(1, 4)):
            s = int((st + r * (L + .04)) * SR)
            if s + len(c) < len(out): out[s:s + len(c)] += c * .4
    return out

def flies(d):
    t = T(d)
    f = 210 + 30 * np.sin(2 * np.pi * 1.3 * t) + 15 * np.sin(2 * np.pi * 7 * t)
    y = saw(f, t) * (.5 + .5 * np.sin(2 * np.pi * .8 * t)) * np.minimum(1, t / .3) * np.minimum(1, (d - t) / .3)
    return lowpass(y, 1800) * .5

def flip():
    y = bandnoise(.09, 1500, 7000) * np.exp(-T(.09) * 40)
    return y

def snore(d):
    t = T(d)
    pulse = np.clip(np.sin(2 * np.pi * t / 1.8), 0, 1) ** 2
    y = lowpass(rng.standard_normal(len(t)), 260) * (1 + .5 * np.sin(2 * np.pi * 45 * t)) * pulse
    return y / (np.abs(y).max() + 1e-9) * .6

def kaching():
    out = np.zeros(int(1.2 * SR))
    c = jingle(.25); out[:len(c)] += c * .6
    d = ding(2093, 1.0); s = int(.12 * SR); out[s:s + len(d)] += d[:len(out) - s] * .6
    return out

def sparkle():
    out = np.zeros(int(1.0 * SR))
    for k in range(10):
        f = 1800 + k * 220; d = ding(f, .5) * .18
        s = int(k * .045 * SR); out[s:s + len(d)] += d[:len(out) - s]
    return out

def confetti_pop():
    y = bandnoise(.25, 600, 8000) * np.exp(-T(.25) * 18)
    return y + .5 * thud()[:len(y)]


# ---------------- music
def pluck(f, d=1.0, bright=1.0):
    t = T(d)
    y = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (3 + 2.2 * k / bright)) / k for k in range(1, 7))
    return y * np.minimum(1, t / .002)

def pad(f, d):
    t = T(d)
    y = sum(np.sin(2 * np.pi * f * m * t + m) / m for m in (1, 2, 3)) * (1 + .1 * np.sin(2 * np.pi * 4 * t))
    e = np.minimum(1, t / .4) * np.minimum(1, (d - t) / .4)
    return y * e * .25

def section(d, bpm, chords, bass, pattern, gain=1.0, padon=False, bright=1.0):
    out = np.zeros(int(d * SR)); beat = 60 / bpm; t = 0.0; bar = 0
    while t < d:
        ch = chords[bar % len(chords)]
        for i, p in enumerate(pattern):
            s0 = int((t + p * beat) * SR)
            if s0 >= len(out): break
            notes = ch if i % 2 == 0 else ch[1:]
            for k, f in enumerate(notes):
                pl = pluck(f * (2 if i in (3, 6) else 1), .9, bright) * (.22 if i % 2 else .3)
                ss = s0 + int(k * .012 * SR); e = min(len(out), ss + len(pl))
                if ss < len(out): out[ss:e] += pl[:e - ss]
        for p in (0, 2):
            s0 = int((t + p * beat) * SR)
            b = pluck(bass[bar % len(bass)] / 2, 1.2) * .7; e = min(len(out), s0 + len(b))
            if s0 < len(out): out[s0:e] += b[:e - s0]
        if padon:
            s0 = int(t * SR); pd = sum(pad(f / 2, 4 * beat) for f in ch); e = min(len(out), s0 + len(pd))
            out[s0:e] += pd[:e - s0]
        t += 4 * beat; bar += 1
    return out * gain

C = [(261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6)]
CB = [130.8, 98.0, 110.0, 87.3]
Am = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (261.6, 329.6, 392.0), (196.0, 246.9, 293.7)]
AmB = [110.0, 87.3, 130.8, 98.0]
FULL = [0, .5, 1, 1.5, 2, 2.75, 3, 3.5]
SLOW = [0, 1, 2, 3]

def thunder():
    y = lowpass(rng.standard_normal(int(2.5 * SR)), 180)
    y = y / (np.abs(y).max() + 1e-9)
    return y * np.exp(-T(2.5) * 1.6) * np.minimum(1, T(2.5) / .05)

def ping():
    out = np.zeros(int(.5 * SR))
    for k, f in enumerate((1318.5, 1760.0)):
        d = ding(f, .4) * .5; s0 = int(k * .09 * SR); out[s0:s0 + len(d)] += d[:len(out) - s0]
    return out

def scratch():
    t = T(.45)
    f = 300 + 2500 * np.abs(np.sin(2 * np.pi * 3 * t))
    y = bandnoise(.45, 400, 6000) * (.5 + .5 * np.sin(2 * np.pi * np.cumsum(f) / SR))
    return y * np.exp(-t * 3)

def tape():
    y = bandnoise(.3, 1500, 8000) * (.6 + .4 * np.sin(2 * np.pi * 37 * T(.3)))
    return y * np.minimum(1, T(.3) / .01) * np.exp(-T(.3) * 4)

def wind(d):
    y = lowpass(rng.standard_normal(int(d * SR)), 500)
    y = y / (np.abs(y).max() + 1e-9)
    return y * (.5 + .5 * np.sin(2 * np.pi * .4 * T(d))) * np.minimum(1, T(d) / .3) * np.minimum(1, (d - T(d)) / .3)

def heartbeat(d):
    out = np.zeros(int(d * SR)); t0 = 0.0
    while t0 < d - .3:
        for off, g in ((0, 1), (.18, .7)):
            b = thud()[:int(.25 * SR)] * g; s0 = int((t0 + off) * SR); out[s0:s0 + len(b)] += b[:len(out) - s0]
        t0 += .75
    return out

def drone(d, f=55):
    t = T(d)
    y = sum(np.sin(2 * np.pi * f * m * t * (1 + .002 * np.sin(2 * np.pi * .3 * t))) / m for m in (1, 2, 3, 4))
    return y * np.minimum(1, t / 1.0) * np.minimum(1, (d - t) / .5) * .4

C = [(261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6)]
CB = [130.8, 98.0, 110.0, 87.3]
F = [(174.6, 220.0, 261.6), (196.0, 246.9, 293.7), (261.6, 329.6, 392.0), (261.6, 329.6, 392.0)]
FB = [87.3, 98.0, 130.8, 130.8]
Am = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (164.8, 207.7, 246.9), (220.0, 261.6, 329.6)]
AmB = [110.0, 87.3, 82.4, 110.0]
FULL = [0, .5, 1, 1.5, 2, 2.75, 3, 3.5]
def rainfx(d):
    y = bandnoise(d, 800, 9000) * .5 + lowpass(rng.standard_normal(int(d * SR)), 400) * .3
    return y * np.minimum(1, T(d) / .6) * np.minimum(1, (d - T(d)) / .6)

SLOWAm = [(220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7), (164.8, 207.7, 246.9)]
SLOWB = [110.0, 87.3, 98.0, 82.4]

# ------------------------------------------------------------ mixer
_mus = _sfx = _amb = None
_diam = []

def mulai(dur):
    global DUR, N, _mus, _sfx, _amb, _diam
    DUR = dur; N = int(dur * SR)
    _mus, _sfx, _amb, _diam = np.zeros(N), np.zeros(N), np.zeros(N), []

def musik(segs):
    for a, b, sig in segs:
        s0 = int(a * SR); e = min(N, int((b + .3) * SR)); L = e - s0
        seg = sig[:L].copy(); f = int(.3 * SR)
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        _mus[s0:s0 + len(seg)] += seg

def put(sig, at, g=1.0):
    s0 = int(at * SR)
    if s0 >= N: return
    e = min(N, s0 + len(sig)); _sfx[s0:e] += sig[:e - s0] * g

def put_amb(sig, at, g):
    s0 = int(at * SR); e = min(N, s0 + len(sig))
    fade = np.minimum(1, np.minimum(np.arange(e - s0), (e - s0) - np.arange(e - s0)) / (.3 * SR))
    _amb[s0:e] += sig[:e - s0] * g * fade

def diam(a, b):
    _diam.append((a, b))

def campur(voice_path="audio_mentah.wav", out="mix_pro.wav"):
    voice_raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", voice_path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                               capture_output=True).stdout
    voice = np.frombuffer(voice_raw, np.int16).astype(np.float32) / 32768
    voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
    blk = int(.05 * SR)
    ve = np.sqrt(np.convolve(voice ** 2, np.ones(blk) / blk, 'same'))
    ve = np.clip(ve / (np.percentile(ve, 95) + 1e-9), 0, 1)
    ve = np.convolve(ve, np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
    mg = 0.15 * (1 - .6 * ve)
    t = np.arange(N) / SR
    mg *= np.clip(t / .8, 0, 1)
    for a, b in _diam:
        mg *= 1 - ((t >= a) & (t < b)) * (1 - np.clip((t - (b - .3)) / .3, 0, 1))
    mix = voice + _sfx * .9 + _amb + _mus * mg
    peak = np.abs(mix).max()
    mix = np.tanh(mix / max(peak, 1) * 1.1) / np.tanh(1.1) * .95
    w = wave.open(out, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
    return peak
