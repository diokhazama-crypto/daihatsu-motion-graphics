"""gen/ → assets/: the two car images are keyed from chroma green to RGBA and cropped to the car; the headlamp becomes a JPG.
Saturated reds are pulled to the film's red #d4162b. Input names: gen/granmax_front.*, gen/granmax_side.*, gen/headlamp.* (png/jpg/webp)."""
import glob, os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import minimum_filter, uniform_filter
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G, A = os.path.join(HERE, 'gen'), os.path.join(HERE, 'assets')
os.makedirs(A, exist_ok=True)
RED = np.array([212, 22, 43], np.float32)

def one(n):
    fs = sorted(f for f in glob.glob(os.path.join(G, n + '*')) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')))
    if not fs: sys.exit(f'missing gen/{n}.png (see prompts/PROMPTS.md)')
    return fs[0]

def fix_red(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = (r > 150) & (g < 90) & (b < 90) & (r - np.maximum(g, b) > 110)
    k = np.clip((r - np.maximum(g, b) - 110) / 40, 0, 1)[..., None] * m[..., None]
    return rgb * (1 - k) + RED * k

def key(src, out, maxw=1600):
    im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    gn = g - np.maximum(r, b)
    a = 1 - np.clip((gn - 12) / 60, 0, 1)
    a = uniform_filter(minimum_filter(a, size=3), size=2)
    g2 = np.where(gn > 0, (r + b) / 2, g)                 # despill
    rgb = fix_red(np.dstack([r, g2, b]))
    ys, xs = np.where(a > .5)
    if len(xs) < 1000: sys.exit(f'{src}: no chroma-green background found to key')
    pad = 6; y0, y1, x0, x1 = max(0, ys.min() - pad), ys.max() + pad, max(0, xs.min() - pad), xs.max() + pad
    o = Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8)[y0:y1, x0:x1], 'RGBA')
    if o.width > maxw: o = o.resize((maxw, round(o.height * maxw / o.width)), Image.LANCZOS)
    o.save(os.path.join(A, out), optimize=True); print('key', out, o.size)

key(one('granmax_front'), 'front.png')
key(one('granmax_side'), 'side.png')
im = np.asarray(Image.open(one('headlamp')).convert('RGB')).astype(np.float32)
Image.fromarray(fix_red(im).clip(0, 255).astype(np.uint8)).save(os.path.join(A, 'lamp.jpg'), quality=93); print('jpg lamp.jpg')
