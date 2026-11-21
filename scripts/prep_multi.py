"""Gabungkan beberapa klip video HP jadi SATU deret frame JPG (1080x1920, 30 fps) + satu wav,
supaya komposisi sinematik (src/Cinematic.tsx) bisa memotong dari banyak klip.

Pemakaian:
  python3 scripts/prep_multi.py <nama> A=<klip_a.mp4> B=<klip_b.mp4> ...
Hasil:
  public/<nama>/0000.jpg ...          frame berurutan semua klip
  assets/mesin_<nama>.wav             audio asli semua klip, sejajar dengan frame
  src/<nama>_clips.json               {"A": detik_mulai_di_deret, ...} untuk build_<nama>.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
SR = 44100

name = sys.argv[1]
clips = [a.split("=", 1) for a in sys.argv[2:]]
out_dir = os.path.join(ROOT, "public", name)
os.makedirs(out_dir, exist_ok=True)
tmp_wavs = []
offsets = {}
start = 0
for key, path in clips:
    n0 = start
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-an",
                    "-vf", f"fps={FPS},scale=1080:1920:flags=lanczos,unsharp=5:5:0.3",
                    "-q:v", "3", "-start_number", str(n0), os.path.join(out_dir, "%04d.jpg")], check=True)
    n1 = len([f for f in os.listdir(out_dir) if f.endswith(".jpg")])
    count = n1 - n0
    dur = count / FPS
    wav = os.path.join(ROOT, "assets", f"_{name}_{key}.wav")
    # audio dipotong/ditambal persis sepanjang frame klip ini
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "2", "-ar", str(SR),
                    "-af", f"apad,atrim=0:{dur}", wav], check=True)
    tmp_wavs.append(wav)
    offsets[key] = round(n0 / FPS, 4)
    print(f"{key}: frame {n0}-{n1 - 1} ({dur:.2f} dtk) <- {os.path.basename(path)}")
    start = n1

lst = os.path.join(ROOT, "assets", f"_{name}_list.txt")
with open(lst, "w") as f:
    for w in tmp_wavs:
        f.write(f"file '{w}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                os.path.join(ROOT, "assets", f"mesin_{name}.wav")], check=True)
for w in tmp_wavs + [lst]:
    os.remove(w)
json.dump({"frames": start, "offsets": offsets}, open(os.path.join(ROOT, "src", f"{name}_clips.json"), "w"), indent=1)
print("total", start, "frame")
