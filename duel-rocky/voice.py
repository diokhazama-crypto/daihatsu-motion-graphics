"""Voice post-processing: out/raw/<id>.wav (edge-tts via tools/tts_proxy.py) → voices/<id>.wav (48 kHz, per character)
+ voices/dur.json + voices/lips.json (mouth openness o and brightness b per 1/24 s).
SHERIFF: low, slow, light saturation + 180 Hz bump (gravel). BANDIT: presence boost, slightly higher. SALES: clean, bright.
Usage: python voice.py"""
import json, os, numpy as np, soundfile as sf, soxr
from scipy.signal import lfilter
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
L = json.load(open(os.path.join(HERE, 'lines.json')))
os.makedirs(os.path.join(HERE, 'voices'), exist_ok=True)
def peq(x, f, gain_db, q=1.0):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return lfilter(np.array(b) / a[0], np.array(a) / a[0], x)
dur, lips = {}, {}
for l in L:
    y, sr = sf.read(os.path.join(HERE, 'out/raw', l['id'] + '.wav'))
    if y.ndim > 1: y = y.mean(1)
    y = soxr.resample(y, sr, SR)
    y = y / (np.abs(y).max() + 1e-9) * .9
    if l['who'] == 'SHERIFF':
        sat = np.tanh(y * 2.6) / np.tanh(2.6); y = .72 * y + .28 * sat
        y = peq(y, 180, 3.0, .8); y = peq(y, 3000, -1.5, 1.0)
    elif l['who'] == 'BANDIT':
        y = peq(y, 3200, 2.5, .9); y = peq(y, 200, -2, .8)
    else:
        y = peq(y, 4500, 1.5, .8)
    y = y / (np.abs(y).max() + 1e-9) * .9
    sf.write(os.path.join(HERE, 'voices', l['id'] + '.wav'), y.astype(np.float32), SR)
    dur[l['id']] = round(len(y) / SR, 3)
    hop = SR // 24; win = int(.05 * SR)
    nF = int(np.ceil(len(y) / hop)) + 1; yp = np.pad(y, (win // 2, win + hop * 2)); wnd = np.hanning(win)
    S = np.abs(np.fft.rfft(np.stack([yp[i * hop:i * hop + win] * wnd for i in range(nF)]), n=4096, axis=1)).T
    freqs = np.fft.rfftfreq(4096, 1 / SR)
    rms = np.sqrt((S ** 2).mean(0)); pk = np.percentile(rms, 95) + 1e-9
    cen = (S * freqs[:, None]).sum(0) / (S.sum(0) + 1e-9)
    o = [round(float(np.clip((r / pk - .1) / .8, 0, 1)), 2) for r in rms]
    b = [round(float(np.clip((c - 1200) / 2600, 0, 1)), 2) for c in cen]
    lips[l['id']] = {'o': o, 'b': b}
    print(l['id'], dur[l['id']])
json.dump(dur, open(os.path.join(HERE, 'voices/dur.json'), 'w'), indent=0)
json.dump(lips, open(os.path.join(HERE, 'voices/lips.json'), 'w'))
