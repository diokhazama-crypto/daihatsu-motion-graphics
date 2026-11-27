"""Original synthesized score → music/score.wav (48 kHz stereo, full length). Cue times come from events.json (story.js).
Instruments (numpy only): theremin lead (sine + 2nd/3rd harmonic, legato glide, delayed vibrato, spring reverb), Karplus–Strong twang guitar,
analogue bass, square-wave arpeggio, retro drum machine, kazoo stinger.
  standoff  E minor, 100 bpm: lonely theremin + twang + low drone, rim clicks
  sales     E major, 120 bpm: bright square arpeggio, bouncy bass, light drums ("suspiciously normal" 2026)
  rocky     E mixolydian surf, 120 bpm: twang riff + full drums + theremin theme
  finale    the theme in full, ends on a stinger
Usage: python score.py"""
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve, lfilter
HERE = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(HERE, 'events.json'))); DUR = E['dur']
CUE = {e['id']: e for e in E['ev'] if e['type'] == 'cue'}
STING = [e['t'] for e in E['ev'] if e.get('name') == 'stinger'][0]
SR = 48000; N = int(DUR * SR) + SR
rng = np.random.default_rng(3)

def tt(d): return np.arange(int(round(d * SR))) / SR
def mf(m): return 440 * 2 ** ((m - 69) / 12)
NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
def M(s): n, o = (s[:2], s[2:]) if len(s) > 2 and s[1] in '#b' else (s[:1], s[1:]); return 12 * (int(o) + 1) + NOTE[n]
def lp(x, f, o=2): return sosfilt(butter(o, min(f, SR * .45), 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def adsr(n, a=.005, d=.1, s=.6, r=.1, hold=None):
    i = np.arange(n); A, D, R = max(int(a * SR), 1), max(int(d * SR), 1), max(int(r * SR), 1); H = max(n - R if hold is None else int(hold * SR), 1)
    e = np.where(i < A, i / A, np.where(i < A + D, 1 - (1 - s) * (i - A) / D, s))
    return np.where(i >= H, e[min(H, n - 1)] * np.clip(1 - (i - H) / R, 0, 1), e)
def saw(ph): return 2 * (ph % 1) - 1
def sq(ph, w=.5): return np.where(ph % 1 < w, 1., -1.)

class Bus:
    def __init__(s): s.b = np.zeros((N, 2))
    def add(s, x, at, g=1., pan=0.):
        st = int(round(at * SR)); l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
        if st < 0: x = x[-st:]; st = 0
        e = min(N, st + len(x))
        if e > st: s.b[st:e, 0] += x[:e - st] * g * l; s.b[st:e, 1] += x[:e - st] * g * r
    def cut(s, t0, t1, fade=.006):
        a, b, f = int(t0 * SR), int(t1 * SR), int(fade * SR); s.b[a:b] = 0
        if a - f > 0: s.b[a - f:a] *= np.linspace(1, 0, f)[:, None]
B = {k: Bus() for k in ['drums', 'bass', 'lead', 'harm']}

# —— instruments ——
def theremin(notes, glide=.07, vib=.3, rate=5.6, bright=.16, v=1.):
    t0 = notes[0][0]; t1 = max(t + d for t, d, _ in notes) + .3; n = int((t1 - t0) * SR)
    target = np.full(n, float(notes[0][2])); amp = np.zeros(n); venv = np.zeros(n)
    for t, d, m in notes:
        a = int((t - t0) * SR); target[a:] = m
        env = adsr(int((d + .14) * SR), .04, .08, .85, .14, hold=d); amp[a:a + len(env)] = np.maximum(amp[a:a + len(env)], env[:n - a])
        L = int((d + .14) * SR); w = np.clip((np.arange(L) / SR - .15) / .25, 0, 1); venv[a:a + L] = np.maximum(venv[a:a + L], w[:n - a])
    k = 1 - np.exp(-1 / (glide * SR)); mid = lfilter([k], [1, -(1 - k)], target, zi=[target[0] * (1 - k)])[0]
    f = mf(mid + vib * venv * np.sin(np.arange(n) / SR * rate * 2 * np.pi)); ph = np.cumsum(f) / SR
    x = np.sin(2 * np.pi * ph) + bright * np.sin(4 * np.pi * ph) + .06 * np.sin(6 * np.pi * ph)
    return t0, lp(x * amp, 5000) * v
def ks(m, d=1.2, v=1., bright=.6):   # Karplus–Strong twang
    f = mf(m); L = int(SR / f); n = int(d * SR); buf = rng.uniform(-1, 1, L) * (1 - .4 * (1 - bright)); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % L]; buf[i % L] = .5 * (buf[i % L] + buf[(i + 1) % L]) * .996
    out = out + .25 * np.tanh(out * 3)   # a little drive = twang
    return hp(out, 90) * adsr(n, .001, .05, 1, .08) * v
KSC = {}
def twang(m, d=1.0, v=1.):
    k = (m, round(d, 2))
    if k not in KSC: KSC[k] = ks(m, d)
    return KSC[k] * v
def bass(d, m, v=1., cut=700):
    n = int((d + .05) * SR); ph = np.cumsum(np.full(n, mf(m))) / SR
    x = .6 * saw(ph) + .5 * np.sin(2 * np.pi * ph) + .25 * np.sin(4 * np.pi * ph)
    return lp(x, cut) * adsr(n, .004, .12, .6, .05, hold=d) * v
def sqpl(d, m, v=1., w=.3, cut=2600):
    n = int((d + .1) * SR); ph = np.cumsum(np.full(n, mf(m))) / SR
    return lp(sq(ph, w) * adsr(n, .002, .08, .3, .08, hold=d), cut) * v
def kick(v=1.): d = .3; t = tt(d); f = 50 + 110 * np.exp(-t / .03); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .12) * v
def snare(v=1.): d = .22; t = tt(d); return (bp(rng.standard_normal(len(t)), 1200, 6000) * np.exp(-t / .06) + .4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / .04)) * v
def hat(v=1.): d = .06; t = tt(d); return bp(rng.standard_normal(len(t)), 6000, 12000) * np.exp(-t / .015) * v
def rim(v=1.): d = .08; t = tt(d); return (np.sin(2 * np.pi * 1700 * t) * .5 + bp(rng.standard_normal(len(t)), 2000, 5000)) * np.exp(-t / .012) * v
def crash(v=1., d=2.0): t = tt(d); return (bp(rng.standard_normal(len(t)), 3000, 11000) + .3 * bp(rng.standard_normal(len(t)), 800, 3000)) * np.exp(-t / .5) * v
def kazoo(notes, v=1.):
    t0 = notes[0][0]; n = int((max(t + d for t, d, _ in notes) - t0 + .1) * SR); f = np.zeros(n); amp = np.zeros(n)
    for t, d, m in notes: a, b = int((t - t0) * SR), int((t + d - t0) * SR); f[a:] = mf(m); amp[a:b] = 1
    amp = lp(amp, 40); ph = np.cumsum(f * (1 + .01 * np.sin(np.arange(n) / SR * 2 * np.pi * 6))) / SR
    x = saw(ph) * (1 + .3 * rng.standard_normal(n) * .2); x = bp(x, 400, 3500); return t0, x * amp * v
def spring(x, mix=.28, d=1.6):
    t = tt(d); ir = rng.standard_normal(len(t)) * np.exp(-t / .35) * (1 + .5 * np.sin(2 * np.pi * 9 * t)); ir = bp(ir, 300, 5000); ir /= np.abs(ir).sum() ** .5 * 6
    w = fftconvolve(x, ir)[:len(x)]; return x * (1 - mix) + w * mix

# —— cues ——
def grid(cue, beat): c = CUE[cue]; return c['t'] + beat * 60 / c['bpm']

# standoff: E minor, 100 bpm, 11 beats; lonely
c = 'standoff'; b = 60 / 100
mel = [(0, 1.5, 'E4'), (1.5, .5, 'G4'), (2, 2, 'B4'), (4, .5, 'C5'), (4.5, .5, 'B4'), (5, 1, 'A#4'), (6, 2.5, 'B4'), (8.5, .5, 'D5'), (9, 2, 'E5')]
t0, x = theremin([(grid(c, s), d * b, M(m)) for s, d, m in mel], v=.55); B['lead'].add(spring(x), t0, pan=.15)
for s, m in [(0, 'E2'), (4, 'E2'), (8, 'E2')]: B['harm'].add(twang(M(m) + 12, 2.2, .5), grid(c, s), pan=-.3)
for s, m in [(2, 'B3'), (6, 'B3'), (9, 'E4')]: B['harm'].add(twang(M(m), 1.2, .35), grid(c, s), pan=-.2)
B['bass'].add(bass(6.6, M('E2'), .5, 300), 0)
for s in range(1, 11, 2): B['drums'].add(rim(.25), grid(c, s), pan=.3)

# sales: E major 120 bpm, bright arpeggio
c = 'sales'; b = .5; nb = int((CUE[c]['end'] - CUE[c]['t']) / b)
prog = [('E', [52, 56, 59, 64]), ('A', [57, 61, 64, 69]), ('B', [59, 63, 66, 71]), ('E', [52, 56, 59, 64])]
for k in range(nb * 4):
    bar = (k // 16) % 4; ch = prog[bar][1]; B['harm'].add(sqpl(.12, ch[k % 4] + 12, .16), grid(c, k / 4), pan=.35 if k % 2 else -.35)
for k in range(nb):
    bar = (k // 4) % 4; root = prog[bar][1][0] - 12
    B['bass'].add(bass(.4, root + (7 if k % 2 else 0), .55), grid(c, k))
    B['drums'].add(kick(.6) if k % 2 == 0 else snare(.3), grid(c, k)); B['drums'].add(hat(.18), grid(c, k + .5))
mel2 = [(0, 1, 'B4'), (1, 1, 'G#4'), (2, 2, 'E5'), (8, 1, 'C#5'), (9, 1, 'E5'), (10, 2, 'A4'), (16, 1, 'D#5'), (17, 1, 'F#5'), (18, 2, 'B5'), (24, 4, 'E5')]
t0, x = theremin([(grid(c, s), d * b, M(m)) for s, d, m in mel2 if s < nb], v=.32); B['lead'].add(spring(x), t0, pan=.1)

# rocky: surf twang riff + full drums
c = 'rocky'; nb = int((CUE[c]['end'] - CUE[c]['t']) / b)
riff = ['E3', 'E3', 'G3', 'A3', 'B3', 'A3', 'G3', 'D3']
B['drums'].add(crash(.35), grid(c, 0))
for k in range(nb * 2):
    m = M(riff[k % 8]) + (5 if (k // 16) % 4 == 2 else 0); B['harm'].add(twang(m + 12, .45, .42), grid(c, k / 2), pan=-.3)
for k in range(nb):
    root = M('E2') + (5 if (k // 8) % 4 == 2 else 0); B['bass'].add(bass(.42, root + (12 if k % 4 == 3 else 0), .6), grid(c, k))
    B['drums'].add(kick(.7) if k % 2 == 0 else snare(.45), grid(c, k)); B['drums'].add(hat(.22), grid(c, k + .5)); B['drums'].add(hat(.12), grid(c, k))
mel3 = [(0, 1.5, 'E5'), (1.5, .5, 'D5'), (2, 1, 'B4'), (3, 1, 'G4'), (4, 2, 'A4'), (6, 2, 'B4'), (8, 1.5, 'E5'), (9.5, .5, 'F#5'), (10, 2, 'G#5'), (12, 4, 'E5'),
        (16, 1.5, 'A5'), (17.5, .5, 'G5'), (18, 2, 'E5'), (20, 2, 'D5'), (22, 4, 'E5')]
t0, x = theremin([(grid(c, s), d * b, M(m)) for s, d, m in mel3 if s < nb], v=.38); B['lead'].add(spring(x), t0, pan=.1)

# finale: theme in full, stinger
c = 'finale'; nb = int((STING - CUE[c]['t']) / b)
B['drums'].add(crash(.45), grid(c, 0))
for k in range(nb * 2):
    m = M(riff[k % 8]) + (5 if (k // 16) % 2 == 1 else 0); B['harm'].add(twang(m + 12, .45, .45), grid(c, k / 2), pan=-.3)
for k in range(nb * 4): B['harm'].add(sqpl(.1, [64, 68, 71, 76][k % 4] + 12, .1), grid(c, k / 4), pan=.4)
for k in range(nb):
    root = M('E2') + (5 if (k // 8) % 2 == 1 else 0); B['bass'].add(bass(.42, root, .62), grid(c, k))
    B['drums'].add(kick(.75) if k % 2 == 0 else snare(.5), grid(c, k)); B['drums'].add(hat(.24), grid(c, k + .5))
t0, x = theremin([(grid(c, s), d * b, M(m)) for s, d, m in mel3 if s < nb], v=.4); B['lead'].add(spring(x), t0, pan=.1)
# stinger: E chord twang + crash + kazoo "ta-daa"
for m in ['E3', 'B3', 'E4', 'G#4', 'B4']: B['harm'].add(twang(M(m), 2.2, .4), STING, pan=-.1)
B['bass'].add(bass(1.2, M('E2'), .7), STING); B['drums'].add(crash(.5, 2.4), STING); B['drums'].add(kick(.9), STING)
t0, x = kazoo([(STING - .32, .14, M('B4')), (STING - .16, .14, M('C#5')), (STING, .55, M('E5'))], v=.18); B['lead'].add(x, t0, pan=.2)

# hard cuts at silences (reverb tails too)
for e in E['ev']:
    if e['type'] == 'silence':
        for bus in B.values(): bus.cut(e['t'], e['end'])
mix = sum(bus.b for bus in B.values())
mix = mix[:int(DUR * SR)]
mix /= np.abs(mix).max() + 1e-9; mix *= .8
os.makedirs(os.path.join(HERE, 'music'), exist_ok=True)
sf.write(os.path.join(HERE, 'music/score.wav'), mix.astype(np.float32), SR)
print('score', DUR, 's')
