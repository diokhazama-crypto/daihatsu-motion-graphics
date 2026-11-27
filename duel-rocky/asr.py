"""Whisper check in Indonesian: pads 0.6 s of silence, transcribes each voices/<id>.wav, compares letter by letter (spaces ignored, similarity ≥ 0.85) with the line
("asr" overrides the expected text; numbers spoken as words are compared through "say"). Writes voices/words.json.
Usage: python asr.py"""
import json, re, os, sys, difflib, numpy as np, soundfile as sf, soxr
from faster_whisper import WhisperModel
HERE = os.path.dirname(os.path.abspath(__file__))
m = WhisperModel(os.environ.get('WHISPER_MODEL', 'small'), device='cpu', compute_type='int8')
norm = lambda s: re.sub(r'[^a-z0-9 ]', ' ', s.lower().replace('-', ' ')).split()
bad, words = 0, {}
for L in json.load(open(os.path.join(HERE, 'lines.json'))):
    y, sr = sf.read(os.path.join(HERE, 'voices', L['id'] + '.wav'))
    y = soxr.resample(y, sr, 16000); pad = np.zeros(int(.6 * 16000))
    segs, _ = m.transcribe(np.concatenate([pad, y, pad]).astype(np.float32), beam_size=5, language='id', word_timestamps=True)
    segs = list(segs); got = ' '.join(s.text.strip() for s in segs)
    words[L['id']] = [(w.word.strip(), round(w.start - .6, 3), round(w.end - .6, 3)) for s in segs for w in s.words]
    want = L.get('asr', L.get('say', L['text']))
    a, b = ''.join(norm(want)), ''.join(norm(got))   # letters only: Whisper splits names ('Day Hatsu') and joins words ('kedilai')
    r = difflib.SequenceMatcher(None, a, b).ratio(); ok = r >= .85; bad += not ok
    print(('OK  ' if ok else 'DIFF'), L['id'], f'{r:.2f}', '|', want, '→', got)
json.dump(words, open(os.path.join(HERE, 'voices/words.json'), 'w'), indent=0)
print('mismatches:', bad); sys.exit(1 if bad else 0)
