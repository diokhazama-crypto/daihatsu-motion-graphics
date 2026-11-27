"""Subtitles → subtitles_id.srt, with the same timing rules as main.js (the captions are also burned into the picture).
Usage: python tools/srt.py"""
import json, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = {l['id']: l for l in json.load(open(os.path.join(HERE, 'lines.json')))}
D = json.load(open(os.path.join(HERE, 'voices/dur.json')))
VO = {e['id']: e['t'] for e in json.load(open(os.path.join(HERE, 'events.json')))['ev'] if e['type'] == 'vo'}
CLIPS = [6.6, 37.1, 44.6, 50.4]
def ts(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
out = []
for i, (id_, t0) in enumerate(sorted(VO.items(), key=lambda x: x[1]), 1):
    txt = L[id_].get('sub', L[id_]['text']); d = D[id_]
    t1 = t0 + max(d + .5, .9 + len(txt) / 17, 1.8)
    cut = next((c for c in CLIPS if c > t0 + .1), None)
    if cut and t1 > cut: t1 = max(cut - .02, t0 + d + .2)
    out.append(f'{i}\n{ts(t0)} --> {ts(t1)}\n{L[id_]["who"].title()}: {txt}\n')
open(os.path.join(HERE, 'subtitles_id.srt'), 'w').write('\n'.join(out)); print('subtitles_id.srt', len(out))
