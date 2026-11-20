"""Siapkan public/music.wav dari MP3 lagu (130 BPM, +-33.4 detik) jadi 1 menit.

Lagu diputar penuh sampai ketukan 72 (awal bar), lalu disambung lagi dari
ketukan 0 sampai ketukan 56, ditutup "jedug" terakhir yang di-fade.
Sambungan tepat di awal bar sehingga ketukan tidak meleset.

Jalankan: python3 scripts/prep_music.py path/lagu.mp3
"""
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
T0, BEAT = 0.10521, 0.461525


def t(n):
    return T0 + n * BEAT


def load(path):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
        check=True, capture_output=True,
    ).stdout
    return np.frombuffer(raw, dtype=np.int16).reshape(-1, 2).astype(np.float32) / 32768


def main():
    src = sys.argv[1]
    y = load(src)
    i = lambda sec: int(round(sec * SR))  # noqa: E731

    part1 = y[: i(t(72))]
    part2 = y[i(t(0)): i(t(56))]
    tail = y[i(t(56)): i(t(56) + 1.2)].copy()
    tail *= np.linspace(1, 0, len(tail))[:, None] ** 1.5

    xf = i(0.012)  # crossfade kecil supaya sambungan tidak "klik"
    def join(a, b):
        ramp = np.linspace(0, 1, xf)[:, None]
        mid = a[-xf:] * (1 - ramp) + b[:xf] * ramp
        return np.concatenate([a[:-xf], mid, b[xf:]])

    out = join(join(part1, part2), tail)
    out /= max(1.0, np.abs(out).max() / 0.98)
    pcm = (out * 32767).astype(np.int16)
    path = os.path.join(ROOT, "public", "music.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("saved", path, f"{len(out) / SR:.2f}s")


if __name__ == "__main__":
    main()
