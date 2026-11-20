"""Hapus teks bawaan (burned-in) dari video HP dengan inpainting per frame,
lalu upscale ke 1080x1920 H.264 30 fps tanpa audio.

Pemakaian: python3 scripts/clean_pov.py <video_mentah.mp4> <keluaran.mp4>
Butuh: pip install opencv-python-headless ; ffmpeg
"""
import subprocess
import sys

import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
ROI = (250, 460, 80, 650)  # y0, y1, x0, x1 area teks (resolusi 720x1280)

# 1) masker: piksel yang hampir selalu putih di area teks = huruf
cap = cv2.VideoCapture(src)
n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
acc, cnt = None, 0
for i in range(0, n, 15):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ok, fr = cap.read()
    if not ok:
        continue
    w = (fr.min(axis=2) > 225).astype(np.float32)
    acc = w if acc is None else acc + w
    cnt += 1
y0, y1, x0, x1 = ROI
mask = np.zeros(acc.shape, np.uint8)
mask[y0:y1, x0:x1] = (acc[y0:y1, x0:x1] / cnt > 0.85) * 255
mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
m_roi = mask[y0:y1, x0:x1]

# 2) inpaint tiap frame -> ffmpeg
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
h, w = acc.shape
ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", "30", "-i", "-",
     "-vf", "scale=1080:1920:flags=lanczos,unsharp=5:5:0.4,format=yuv420p",
     "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "15", dst],
    stdin=subprocess.PIPE)
k = 0
while True:
    ok, fr = cap.read()
    if not ok:
        break
    roi = fr[y0:y1, x0:x1]
    fr[y0:y1, x0:x1] = cv2.inpaint(roi, m_roi, 6, cv2.INPAINT_TELEA)
    ff.stdin.write(fr.tobytes())
    k += 1
ff.stdin.close()
ff.wait()
print(f"ok {k} frame -> {dst}")
