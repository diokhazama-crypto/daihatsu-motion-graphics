"""Ubah 1 foto jadi beberapa gambar gaya 2D untuk komposisi Gaya2D.

Pakai:  python3 scripts/make_2d.py assets/foto.jpg
Hasil:  public/gaya2d/{cel,sketch,line,boil0-2,manga,poster,pixel,water}.png/jpg + head.png
Hanya butuh Pillow + numpy (tanpa AI / model).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "gaya2d")
os.makedirs(OUT, exist_ok=True)

src = Image.open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "assets", "foto.jpg")).convert("RGB")
# Lebar kerja 1080; parameter filter disetel untuk lebar 720 lalu diskalakan.
W = 1080
src = src.resize((W, round(src.height * W / src.width)), Image.LANCZOS)
H = src.height
S = W / 720


def odd(n):
    n = max(3, int(round(n)))
    return n if n % 2 else n + 1


def mode_smooth(im, size, n):
    for _ in range(n):
        im = im.filter(ImageFilter.ModeFilter(odd(size * S)))
    return im


def lines(im, r=8, th=205, grow=False):
    """Garis hitam di atas putih, dari teknik 'color dodge' sketsa pensil."""
    g = ImageOps.grayscale(im).filter(ImageFilter.GaussianBlur(0.8 * S))
    inv = ImageOps.invert(g).filter(ImageFilter.GaussianBlur(r * S))
    a = np.asarray(g, float)
    b = np.asarray(inv, float)
    sk = np.clip(a * 255 / (256 - b), 0, 255)
    out = Image.fromarray(np.where(sk < th, 0, 255).astype("uint8")).filter(ImageFilter.MedianFilter(odd(3 * S)))
    if grow:
        out = out.filter(ImageFilter.MinFilter(odd(3 * S)))
    return out


def save(im, name, **kw):
    im.save(os.path.join(OUT, name), **kw)
    print("  ", name)


print("Membuat gaya 2D ->", OUT)

# Sketsa pensil
g = ImageOps.grayscale(src)
inv = ImageOps.invert(g).filter(ImageFilter.GaussianBlur(10 * S))
sk = np.clip(np.asarray(g, float) * 255 / (256 - np.asarray(inv, float)), 0, 255).astype("uint8")
save(ImageEnhance.Contrast(Image.fromarray(sk)).enhance(1.6), "sketch.jpg", quality=90)

# Line art + 3 frame 'line boil'
save(lines(src), "line.png", optimize=True)
for i, (dx, dy, th) in enumerate([(0, 0, 205), (1, -1, 200), (-1, 1, 210)]):
    shifted = src.transform(src.size, Image.AFFINE, (1, 0, dx * S, 0, 1, dy * S))
    save(lines(shifted, 8, th), f"boil{i}.png", optimize=True)

# Kartun cel: warna rata + garis tebal
sm = mode_smooth(src.filter(ImageFilter.MedianFilter(odd(7 * S))), 9, 3)
q = ImageEnhance.Color(sm).enhance(1.4).quantize(8, dither=Image.Dither.NONE).convert("RGB")
cel = ImageChops.multiply(q, lines(src, 8, 195, True).convert("RGB"))
save(cel, "cel.jpg", quality=92)

# Poster vektor: palet tetap 7 warna
pal = [(26, 34, 64), (52, 74, 140), (232, 190, 150), (196, 140, 104), (242, 196, 82), (248, 240, 225), (225, 37, 27)]
pimg = Image.new("P", (1, 1))
pimg.putpalette(sum(pal, ()) + (0, 0, 0) * (256 - len(pal)))
post = mode_smooth(src.filter(ImageFilter.GaussianBlur(2 * S)), 7, 4).quantize(palette=pimg, dither=Image.Dither.NONE)
save(post.convert("RGB"), "poster.png", optimize=True)

# Pixel art (72 px lebar, 16 warna)
px = src.resize((72, round(72 * H / W)), Image.BILINEAR)
px = ImageEnhance.Color(px).enhance(1.4).quantize(16, dither=Image.Dither.NONE).convert("RGB")
save(px.resize((W, H), Image.NEAREST), "pixel.png", optimize=True)

# Manga: hitam, screentone titik, putih + garis
gg = np.asarray(ImageOps.autocontrast(g).filter(ImageFilter.GaussianBlur(S)), float)
yy, xx = np.mgrid[0:H, 0:W]
cell = round(6 * S)
dot = ((xx % cell - cell / 2) ** 2 + (yy % cell - cell / 2) ** 2) < 5 * S * S
m = np.where(gg < 70, 0, np.where(gg < 150, np.where(dot, 0, 255), 255)).astype("uint8")
manga = ImageChops.multiply(Image.fromarray(m), lines(src, 8, 200))
save(manga, "manga.png", optimize=True)

# Cat air
wc = mode_smooth(src.filter(ImageFilter.GaussianBlur(4 * S)), 11, 3)
wc = wc.quantize(12, dither=Image.Dither.NONE).convert("RGB").filter(ImageFilter.GaussianBlur(2.5 * S))
wc = Image.blend(ImageEnhance.Color(wc).enhance(1.25), Image.new("RGB", src.size, (252, 248, 238)), 0.3)
rng = np.random.default_rng(1)
grain = Image.fromarray((235 + rng.integers(0, 20, (H, W))).astype("uint8")).filter(ImageFilter.GaussianBlur(0.7 * S))
wc = ImageChops.multiply(wc, grain.convert("RGB"))
wc = ImageChops.multiply(wc, lines(src, 8, 200).point(lambda v: max(v, 90)).convert("RGB"))
save(wc, "water.jpg", quality=90)

# Stiker kepala (lingkaran, border putih) dari versi kartun.
# Kotak wajah dalam koordinat relatif foto (dipotong bebas bar hitam).
fx0, fy0, fx1, fy1 = 165 / 720, 150 / 956, 605 / 720, 590 / 956
box = (round(fx0 * W), round(fy0 * H), round(fx1 * W), round(fy1 * H))
D = 600
face = cel.crop(box).resize((D, D), Image.LANCZOS)
mask = Image.new("L", (D, D), 0)
ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
B = 28
head = Image.new("RGBA", (D + 2 * B, D + 2 * B), (0, 0, 0, 0))
ImageDraw.Draw(head).ellipse((0, 0, D + 2 * B - 1, D + 2 * B - 1), fill=(255, 255, 255, 255))
head.paste(face, (B, B), mask)
save(head, "head.png", optimize=True)
print("Selesai.")
