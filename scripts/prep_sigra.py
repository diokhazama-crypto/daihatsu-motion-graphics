#!/usr/bin/env python3
"""Siapkan footage Sigra untuk komposisi SigraSinematik.

- buang teks bawaan di shot pembuka (delogo)
- grading gelap ala referensi: abu-abu dingin, hitam pekat, highlight ditekan,
  hanya warna MERAH yang dibiarkan menyala (lis grille, dashboard, lampu belakang)
- upscale 720x1280 -> 1080x1920, fps asli (38) dipertahankan
- audio lagu -> public/sigra_music.wav

Pemakaian:
  python3 scripts/prep_sigra.py <Sigra_IMP_30detik_speed125.mp4>
  python3 scripts/prep_sigra.py <video> --terang  # versi terang -> public/clips/sigra_terang.mp4
  python3 scripts/prep_sigra.py <video> --test 1.5 11 29.5   # cuma bikin PNG uji
"""
import subprocess
import sys

import numpy as np

try:
    import cv2  # pip install opencv-python-headless
except ImportError:  # pragma: no cover
    sys.exit("butuh opencv: pip install opencv-python-headless")

W, H = 720, 1280
OUT_W, OUT_H = 1080, 1920
# teks "New Sigra 1.2 R MT IMP / Bronze Metallic" di shot pertama (frame 0-93 @38fps)
DELOGO = "delogo=x=80:y=335:w=565:h=130:enable='lt(n,94)'"
# gelap: low-key ala parkiran malam. terang: kecerahan mendekati asli, warna lembut, merah tetap menonjol.
LOOKS = {
    "gelap": dict(redsat=1.35, sat=0.10, k=2.6, gam=1.9, top=0.62, red=0.35, tint=[0.94, 1.0, 1.05]),
    "terang": dict(redsat=1.08, sat=0.38, k=1.8, gam=1.35, top=0.96, red=0.15, tint=[0.97, 1.0, 1.03]),
}
LOOK = LOOKS["terang" if "--terang" in sys.argv else "gelap"]
TINT = np.array(LOOK["tint"], np.float32)  # bayangan sedikit dingin


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def red_mask(r, mx, sat, hue):
    """Mask area merah yang dibiarkan berwarna.

    Dibuat longgar (merah kusam / gelap / agak keunguan dari kompresi video HP tetap masuk),
    tapi oranye/bronze bodi mobil tetap di luar. Lalu dihaluskan secara spasial supaya bidang
    merah (dashboard, panel pintu) tidak belang: lubang kecil ditutup (morph close) + blur.
    """
    is_r = smooth(r - (mx - 0.04), 0.0, 0.04)              # R (hampir) paling besar
    hue_ok = np.where(hue >= 0, 1 - smooth(hue, 16, 28),   # sisi oranye: ketat (bronze ~30 derajat)
                      1 - smooth(-hue, 30, 45))            # sisi magenta: longgar
    m = (is_r * hue_ok * smooth(sat, 0.14, 0.32) * smooth(mx, 0.03, 0.12)).astype(np.float32)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    m = cv2.GaussianBlur(m, (0, 0), 3.5)
    return np.clip(m * 1.25, 0, 1)


def grade(rgb: np.ndarray) -> np.ndarray:
    x = rgb.astype(np.float32) / 255.0
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    mx = x.max(-1)
    mn = x.min(-1)
    sat = (mx - mn) / (mx + 1e-4)
    hue = 60.0 * (g - b) / (mx - mn + 1e-4)  # derajat, valid saat R paling besar
    red = red_mask(r, mx, sat, hue)

    # desaturasi semua kecuali merah
    s = LOOK["sat"] + red * (LOOK["redsat"] - LOOK["sat"])
    col = luma[..., None] + (x - luma[..., None]) * s[..., None]
    # merah yang agak keunguan (kompresi HP) digeser sedikit ke merah murni
    col[..., 2] -= red * np.clip(col[..., 2] - col[..., 1], 0, None) * 0.6
    col = np.clip(col, 0, 1)

    # kurva tone: hitam lebih pekat, highlight (langit) roll-off
    k, gam, top = LOOK["k"], LOOK["gam"], LOOK["top"]
    col = top * (1 - np.exp(-k * col**gam)) / (1 - np.exp(-k))
    # merah sedikit diangkat supaya "menyala" di atas latar gelap
    col = col * (1 + LOOK["red"] * red[..., None])
    # tint dingin di bayangan, netral di highlight
    lum2 = col.mean(-1, keepdims=True)
    col = col * (TINT + (1 - TINT) * np.clip(lum2 * 1.6, 0, 1))
    return (np.clip(col, 0, 1) * 255 + 0.5).astype(np.uint8)


def frames(src, extra=()):
    cmd = ["ffmpeg", "-v", "error", *extra, "-i", src, "-vf", f"{DELOGO},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)


def main():
    src = sys.argv[1]
    if "--test" in sys.argv:
        for t in sys.argv[sys.argv.index("--test") + 1 :]:
            fr = next(frames(src, ["-ss", t]))
            out = np.concatenate([fr, grade(fr)], 1)
            name = f"test_{t}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{2*W}x{H}", "-i", "-", name], input=out.tobytes(), check=True)
            print("tulis", name)
        return

    out = "public/clips/sigra_terang.mp4" if "--terang" in sys.argv else "public/clips/sigra.mp4"
    subprocess.run(["mkdir", "-p", "public/clips"], check=True)
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "38", "-i", "-",
         "-vf", f"scale={OUT_W}:{OUT_H}:flags=lanczos,unsharp=5:5:0.4,format=yuv420p",
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "19", out],
        stdin=subprocess.PIPE,
    )
    for i, fr in enumerate(frames(src)):
        enc.stdin.write(grade(fr).tobytes())
        if i % 100 == 0:
            print("frame", i, flush=True)
    enc.stdin.close()
    enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "2", "-ar", "48000", "public/sigra_music.wav"], check=True)
    print(f"ok {out} + public/sigra_music.wav")


if __name__ == "__main__":
    main()
