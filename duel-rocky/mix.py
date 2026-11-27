"""Mix: procedural foley (events.json) + dialogue (voices/) + score (music/score.wav, ducked under dialogue) + ambience → out/mix.wav
Usage: python mix.py   (after events.mjs, voice.py, score.py)"""
import sys, os, json, numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = os.environ['LIB']
sys.path.insert(0, os.path.join(LIB, 'core/audio'))
from sfx import SR, t_, env_exp, bp, lp, hp, norm, click, clack, whoosh, pop, ding, thump, compress, limit, add
E = json.load(open(os.path.join(HERE, 'events.json'))); DUR = E['dur']; N = int(DUR * SR)
rng = np.random.default_rng(5)
def nz(d): return rng.standard_normal(int(round(d * SR)))
def sweep(f0, f1, d, curve=1.0): tt = t_(d); f = f0 * (f1 / f0) ** ((tt / d) ** curve); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def bpsweep(x, f0, f1, q=.35):
    out = np.zeros_like(x); n = len(x)
    for i in range(0, n, 480):
        f = f0 * (f1 / f0) ** (i / n); s = bp(x[max(0, i - 2400):i + 480], f * (1 - q), min(f * (1 + q), 20000)); out[i:i + 480] = s[-len(out[i:i + 480]):]
    return out
def hann(d): return np.sin(np.pi * t_(d) / d)

# —— foley (all synthesized) ——
def tick(): d = .05; return norm(np.sin(2 * np.pi * 2600 * t_(d)) * env_exp(d, .01) + bp(nz(d), 2000, 7000) * env_exp(d, .004) * .5)
def gulp(): d = .25; x = sweep(420, 110, d, .6) * env_exp(d, .07); return norm(lp(x, 1200))
def whip(): d = .25; return norm(bpsweep(nz(d), 600, 5000, .4) * hann(d) ** 2)
def twitch(): return norm(np.concatenate([clack(1.6) * .6, np.zeros(int(.06 * SR)), clack(1.8) * .4]))
def boom():
    d = 1.6; tt = t_(d); sub = np.sin(2 * np.pi * np.cumsum(55 * (1 + 1.5 * np.exp(-tt / .08))) / SR) * env_exp(d, .45)
    sw = bpsweep(nz(d), 4000, 300, .5) * env_exp(d, .5) * .5
    rise = np.sin(2 * np.pi * np.cumsum(np.linspace(200, 1200, len(tt))) / SR) * hann(d) * .2
    return norm(sub + sw + rise)
def portal_hum(d):
    tt = t_(d); x = np.sin(2 * np.pi * 110 * tt) * .5 + np.sin(2 * np.pi * 165.5 * tt) * .3 + np.sin(2 * np.pi * 220.7 * tt) * .2
    x *= 1 + .25 * np.sin(2 * np.pi * 3 * tt); x += bp(nz(d), 800, 2400) * .15 * (1 + np.sin(2 * np.pi * .7 * tt))
    e = np.minimum(1, tt / .3) * np.minimum(1, (d - tt) / .3); return norm(x * e)
def swoosh(d=.4): return norm(bpsweep(nz(d), 400, 4000, .35) * hann(d) ** 2)
def landing(): return norm(thump(1, 75) + np.pad(lp(nz(.12), 1500) * env_exp(.12, .03) * .6, (0, len(thump(1, 75)) - int(.12 * SR))))
def boing(): d = .6; tt = t_(d); f = 200 * (1 + .35 * np.sin(2 * np.pi * 16 * tt) * np.exp(-tt / .25)); return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, .2))
def snap(): d = .08; return norm(bp(nz(d), 1500, 7000) * env_exp(d, .008))
def fall(): d = .5; tt = t_(d); return norm(np.sin(2 * np.pi * np.cumsum(np.linspace(1400, 300, len(tt))) / SR) * hann(d) * .6 + bpsweep(nz(d), 3000, 600, .4) * hann(d) * .5)
def car_land():
    x = norm(thump(1, 60)) + np.pad(norm(clack(.6)) * .6, (0, len(thump(1, 60)) - len(clack(.6))))
    sp = np.sin(2 * np.pi * 90 * t_(.5)) * env_exp(.5, .12) * (1 + .5 * np.sin(2 * np.pi * 14 * t_(.5))) * .5
    y = np.zeros(int(.7 * SR)); y[:len(x)] += x; y[int(.05 * SR):int(.05 * SR) + len(sp)] += sp; return norm(y)
def honk():
    d = .5; tt = t_(d); x = np.zeros(len(tt))
    for f in (392, 494): ph = np.cumsum(np.full(len(tt), f)) / SR; x += np.sign(np.sin(2 * np.pi * ph)) * .5
    x = bp(x, 300, 3000); e = np.ones(len(tt)); e[:int(.01 * SR)] = np.linspace(0, 1, int(.01 * SR)); e[int(.2 * SR):int(.26 * SR)] = .1; e[-int(.03 * SR):] = np.linspace(1, 0, int(.03 * SR))
    return norm(x * e)
def blip(): d = .05; return norm(np.sin(2 * np.pi * 1700 * t_(d)) * hann(d))
def leather(): d = .3; return norm(bp(nz(d), 300, 2000) * hann(d) ** 2 * (1 + (rng.random(len(t_(d))) > .97) * 3))
def engine():
    d = 1.8; tt = t_(d); f = 38 + 30 * np.clip(tt / .3, 0, 1) * np.exp(-np.maximum(0, tt - .35) / .5) + 10 * np.clip(tt - .9, 0, 1)
    ph = np.cumsum(f) / SR; x = sum(np.sin(2 * np.pi * ph * k) / k for k in range(1, 9)) + .3 * bp(nz(d), 200, 1500)
    starter = np.zeros(len(tt)); s = int(.25 * SR); starter[:s] = np.sign(np.sin(2 * np.pi * 22 * tt[:s])) * bp(nz(.25), 500, 3000) * .5
    e = np.minimum(1, tt / .05) * np.minimum(1, (d - tt) / .4); return norm(lp(x, 2500) * e * (tt > .2) + starter)
def hop(): return norm(np.concatenate([swoosh(.3) * .5, boing()[:int(.3 * SR)] * .5]))
def door(): a = norm(clack(.5)); b = norm(thump(.8, 90)); y = np.zeros(int(.12 * SR) + len(b)); y[:len(a)] += a * .7; y[int(.12 * SR):] += b * .5; return y
def suck(): d = .6; x = bpsweep(nz(d), 3500, 250, .4) * np.linspace(.3, 1, len(t_(d))); x += np.sin(2 * np.pi * np.cumsum(np.linspace(900, 150, len(x))) / SR) * .3 * hann(d); return norm(np.concatenate([x, pop(.8)[:int(.1 * SR)] * .6]))
def close_(): d = .4; x = bpsweep(nz(d), 300, 3000, .4)[::-1] * np.linspace(0, 1, len(t_(d))) ** 2; return norm(np.concatenate([x, norm(thump(1, 55)) * .9]))
def weed(d): tt = t_(d); return norm(bp(nz(d), 1500, 6000) * (.3 + .7 * (np.sin(2 * np.pi * 5 * tt) > .6)) * hann(d) ** .7)
def title_hit(): return norm(np.concatenate([np.zeros(int(.02 * SR)), norm(pop(1)) * .6]) )
def ding_(): return norm(ding(1))
def nod(): d = .12; return norm(bp(nz(d), 400, 1500) * hann(d))
FX = {'tick': (tick, .35), 'gulp': (gulp, .5), 'whip': (whip, .5), 'twitch': (twitch, .35), 'boom': (boom, .95), 'whoosh': (lambda: swoosh(.35), .5), 'land': (landing, .7),
      'ding': (ding_, .3), 'boing': (boing, .4), 'click': (lambda: norm(click(1)), .35), 'snap': (snap, .6), 'fall': (fall, .45), 'carLand': (car_land, .9), 'honk': (honk, .55),
      'blip': (blip, .25), 'nod': (nod, .3), 'leather': (leather, .35), 'engine': (engine, .7), 'hop': (hop, .45), 'pop': (lambda: norm(pop(1)), .5), 'door': (door, .4),
      'suck': (suck, .7), 'close': (close_, .7), 'title': (title_hit, .4)}

sfxb, vob, amb = np.zeros((N, 2)), np.zeros((N, 2)), np.zeros((N, 2))
vo_mask = np.zeros(N)
for e in E['ev']:
    if e['type'] == 'vo':
        y, sr = sf.read(os.path.join(HERE, 'voices', e['id'] + '.wav'))
        y = compress(y, thr=.22, ratio=3.5); y = norm(y, .9)
        g = {'SHERIFF': .9, 'BANDIT': 1.15, 'SALES': .9}[e['who']]
        add(vob, y, e['t'], g, {'SHERIFF': .08, 'BANDIT': -.08, 'SALES': 0}[e['who']])
        a, b = int(e['t'] * SR), min(N, int((e['t'] + len(y) / SR) * SR)); vo_mask[a:b] = 1
    elif e['type'] == 'sfx':
        n = e['name']
        if n == 'portalHum': add(sfxb, portal_hum(e['end'] - e['t']), e['t'], .18)
        elif n == 'weed': add(sfxb, weed(e['dur']), e['t'], .12)
        elif n in FX: fn, gain = FX[n]; add(sfxb, fn(), e['t'], gain)
# ambience: night wind + crickets (street), soft dawn birds (end card)
END = [e['t'] for e in E['ev'] if e['type'] == 'cut' and e['id'] == 'end'][0]
tt = np.arange(N) / SR
wind = lp(np.cumsum(rng.standard_normal(N)) * .01, 600); wind = hp(wind, 60); wind = norm(wind) * (.6 + .4 * np.sin(2 * np.pi * .13 * tt))
crick = np.sin(2 * np.pi * 4300 * tt) * ((np.sin(2 * np.pi * 28 * tt) > .2) * (np.sin(2 * np.pi * 1.6 * tt) > .1))
crick2 = np.sin(2 * np.pi * 3900 * tt) * ((np.sin(2 * np.pi * 31 * tt + 1) > .3) * (np.sin(2 * np.pi * 1.1 * tt + 2) > .3))
night = (wind * .16 + crick * .035 + crick2 * .025) * (tt < END)
birds = np.zeros(N)
for k in range(10):
    t0 = END + .4 + k * .55 + rng.random() * .3
    if t0 + .2 > DUR: break
    d = .12; s = sweep(2600 + rng.random() * 800, 3800 + rng.random() * 800, d) * hann(d); a = int(t0 * SR); birds[a:a + len(s)] += s[:N - a] * .05
dawnb = (lp(rng.standard_normal(N), 400) * .03 + birds) * (tt >= END)
amb[:, 0] += night + dawnb; amb[:, 1] += night * .9 + dawnb
# night ambience swells in the silences
for e in E['ev']:
    if e['type'] == 'silence': a, b = int(e['t'] * SR), int(e['end'] * SR); amb[a:b] *= 1.8
# score, ducked ~ -7 dB under dialogue (smoothed)
mus, sr = sf.read(os.path.join(HERE, 'music/score.wav'))
mus = mus[:N] if len(mus) >= N else np.pad(mus, ((0, N - len(mus)), (0, 0)))
from scipy.ndimage import uniform_filter1d
duck = 1 - .55 * uniform_filter1d(np.maximum.accumulate(vo_mask[::-1])[::-1] * 0 + vo_mask, int(.25 * SR))
mix = vob * 1.0 + sfxb * .7 + mus * 1.25 * duck[:, None] + amb * .8
mix = mix / (np.abs(mix).max() + 1e-9) * .95
mix = np.stack([limit(c, .95) for c in mix.T], 1)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out/mix.wav'), mix.astype(np.float32), SR)
for name, b in [('voice', vob), ('sfx', sfxb), ('amb', amb)]: print(name, 'rms', round(float(np.sqrt((b ** 2).mean())), 4))
print('mix written', DUR)
