"""DIO — Sales Daihatsu: score (sampled instruments, CC0) + procedural sound. Reads events.json, writes out/mix.wav.
150 BPM (beat 0.4 s), E Phrygian. Harpsichord 16ths, contrabass/cello pizzicato, woodblock clock, timpani, bass drum,
trombone/tuba/horn ♭9 stab, tam-tam, glockenspiel, tubular bell. No piano, no string pad."""
import json, os, sys
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.environ['LIB']
sys.path.insert(0, LIB); sys.path.insert(0, os.path.join(LIB, 'core', 'audio'))
from core.audio import sampler as Sm
import sfx
from sfx import SR, t_, env_exp, bp, lp, hp, noise, norm, add

E = json.load(open(os.path.join(HERE, 'events.json')))
DUR = E['dur']; N = int((DUR + .05) * SR)
SEC = {e['name']: e['t'] for e in E['ev'] if e['type'] == 'sec'}
EV = [e for e in E['ev'] if e['type'] != 'sec']
BEAT = .4
Sm.seed(11)
M = []
def n(t, inst, p, d, v, pan=0., gain=1.): M.append((round(t, 4), inst, p, d, v, pan, gain))

road, sil, rev = SEC['road'], SEC['silence'], SEC['reveal']

# A — flash cards: harpsichord ostinato in 16ths (E Phrygian), contrabass pizzicato on every beat
seq = ['E4', 'B4', 'G4', 'B4', 'F4', 'B4', 'G4', 'B4']
k = 0; t = 0.0
while t < road - 1e-6:
    n(t, 'harpsichord', seq[k % 8], BEAT / 4 * .9, .6 if k % 4 == 0 else .48, -.25); k += 1; t += BEAT / 4
for i in range(3): n(i * BEAT, 'contrabass_pizz', ['E2', 'E2', 'F2'][i], .5, .75, .1)
# B — the road: the harpsichord stops; woodblock clock, cello pizz, timpani rising on each step of the car
for i in range(4):
    tt = road + i * BEAT
    n(tt, 'woodblock', 'b' if i % 2 == 0 else 'a', None, .5, .35, .8)
    n(tt, 'timpani', ['F2', 'G2', 'A2', 'Bb2'][i], .5, .55 + i * .1)
    n(tt, 'cellos_pizz', ['E3', 'E3', 'F3', 'E3'][i], .4, .6, -.2, .8)
n(road, 'contrabass', 'E2', sil - road, .35, 0, .6)
n(road + 3 * BEAT, 'bass_drum', None, None, .6, 0, .8)
# silence: one woodblock tick only (in the sfx), everything else gated
# C — reveal: tam-tam + bass drum + low brass E(♭9) + timpani; glockenspiel three notes; tubular bell
n(rev, 'gong', None, None, .8, 0, .9); n(rev, 'bass_drum', None, None, .95)
for p, inst in [('E2', 'trombone'), ('B2', 'trombone'), ('E2', 'tuba'), ('E3', 'horn'), ('F4', 'horn')]: n(rev, inst, p, 1.4, .75, 0, .7)
n(rev, 'timpani', 'F2', 1.0, .85)
n(rev, 'contrabass', 'E2', DUR - rev, .4, 0, .55)
for i, p in enumerate(['E6', 'G6', 'B6']): n(rev + .8 + i * .2, 'glockenspiel', p, 1.2, .45, -.3 + i * .3, .8)
n(rev + 1.6, 'tubular_bells', 'E4', 1.5, .65, 0, .8)
mus = Sm.render(M, dur=DUR + .05, master=False)[:N]
mus = np.pad(mus, ((0, max(0, N - len(mus))), (0, 0)))

# ───────── Sound effects ─────────
dry = np.zeros((N, 2)); wet = np.zeros((N, 2)); amb = np.zeros((N, 2))
def hit(p=1.):      # card hit: high-passed noise transient + metallic ring 1760/2637/4186 Hz + a 52 Hz drop
    d = .45; tt = t_(d)
    tr = hp(noise(d), 3000) * env_exp(d, .004)
    ring = sum(a * np.sin(2 * np.pi * f * p * tt) * env_exp(d, tau) for f, a, tau in [(1760, .5, .08), (2637, .35, .05), (4186, .2, .03)])
    sub = np.sin(2 * np.pi * 52 * tt * (1 - .4 * tt)) * env_exp(d, .09)
    return norm(tr + ring + sub * 1.2)
def blip(): d = .06; tt = t_(d); return norm(np.sin(2 * np.pi * 3000 * tt) * env_exp(d, .012))
def swell(d=.12): x = hp(noise(d), 800) * np.linspace(0, 1, int(round(d * SR))) ** 3; return norm(x)
def slam():
    a = sfx.thump(1, 95) * .8; b = sfx.click(.7, .6); m = max(len(a), len(b))
    return norm(np.pad(a, (0, m - len(a))) + np.pad(b, (0, m - len(b))))
def engine():       # a short low engine bark under each step
    d = .32; tt = t_(d); f = 46 + 20 * np.exp(-tt * 9)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .5 + np.sin(2 * np.pi * np.cumsum(f) / SR)
    return norm(lp(x, 400) * env_exp(d, .09))
def latch():        # door latch "klek" on the reveal
    a = sfx.clack(.5, 1); b = np.pad(sfx.click(.9, .7), (int(.03 * SR), 0)); m = max(len(a), len(b))
    return norm(np.pad(a, (0, m - len(a))) + np.pad(b, (0, m - len(b))))

for e in EV:
    t, k = e['t'], e['type']
    if k == 'hit': x = hit(e.get('p', 1)); add(dry, x, t, .55); add(wet, x, t, .25)
    elif k == 'blip': add(dry, blip(), t, .22, .3)
    elif k == 'cut': add(dry, sfx.click(1.2, .8), t, .3)
    elif k == 'slit': add(dry, swell(.1), t, .3)
    elif k == 'rush': add(dry, sfx.whoosh(.3, 1), t, .4, -.4)
    elif k == 'rail': add(dry, slam(), t, .5, -.5)
    elif k == 'step': kk = e['k']; add(dry, engine(), t, .25 + kk * .1); add(dry, sfx.thump(1, 60), t, .2 + kk * .08)
    elif k == 'bar': add(dry, slam(), t, .5); add(dry, hit(1.8), t, .2)
    elif k == 'tick': x = Sm.hit('woodblock', 'b', .85); add(dry, x, t, .9, .3); add(wet, x, t, .8)
    elif k == 'pre': add(dry, swell(.07), t - .01, .3)
    elif k == 'snap':                # neck crack: low clack + click + noise transient
        a = sfx.clack(.55, 1); b = np.pad(sfx.click(.8, .8), (int(.012 * SR), 0)); mm = max(len(a), len(b))
        x = norm(np.pad(a, (0, mm - len(a))) + np.pad(b, (0, mm - len(b))) + hp(noise(mm / SR), 1500)[:mm] * env_exp(mm / SR, .003)[:mm])
        add(dry, x, t, .8); add(wet, x, t, .5)
    elif k == 'reveal': x = hit(.72); add(dry, x, t, .6); add(wet, x, t, .8); add(dry, sfx.thump(1, 38), t, .9); add(dry, latch(), t + .25, .35, .3)

# ambience: a thin night wind under the road and the reveal
d = DUR + .05; wind = bp(noise(d), 200, 1400)[:N] * (.6 + .4 * np.sin(2 * np.pi * .7 * t_(d)[:N]))
x = np.arange(N) / SR
wenv = np.clip((x - (road - .1)) / .2, 0, 1)
amb[:, 0] += wind * wenv * .05; amb[:, 1] += np.roll(wind, 300) * wenv * .05

ir_d = 1.8; ir = lp(noise(ir_d) * env_exp(ir_d, .4), 5000); ir /= np.sqrt((ir ** 2).sum())
for ch in range(2): wet[:, ch] = fftconvolve(wet[:, ch], ir)[:N]
mus_wet = np.stack([fftconvolve(mus[:, ch], ir * .5)[:N] for ch in range(2)], 1)

# hard silence: from the silence cue to the reveal only the woodblock tick sounds
def mask(a, b, fade=.02): return np.minimum(1, np.clip((a - x) / fade, 0, 1) + np.clip((x - b) / fade, 0, 1))
gate = mask(sil + .015, rev - .075)

music = (mus * .62 + mus_wet * .16) * gate[:, None]
fx = dry + wet * .3
tick_t = sil
keep = ((x >= tick_t - .01) & (x < tick_t + .2)) | (x >= rev - .14)
fx = fx * np.maximum(gate, keep.astype(float))[:, None]
mix = music + fx + amb * gate[:, None]
fade = np.clip((DUR - x) / .12, 0, 1); mix *= fade[:, None]
for ch in range(2): mix[:, ch] = sfx.limit(mix[:, ch], .5)
mix = mix / np.abs(mix).max() * .9
for ch in range(2): mix[:, ch] = sfx.limit(mix[:, ch], .5, .003)
mix = mix / np.abs(mix).max() * .9
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
sf.write(os.path.join(HERE, 'out', 'mix.wav'), mix.astype(np.float32), SR)
print('mix ok', mix.shape, 'instruments:', sorted({m[1] for m in M}))
