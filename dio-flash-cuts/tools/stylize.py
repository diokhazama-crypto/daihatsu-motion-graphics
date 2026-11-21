"""Dio's photo → a flat cel figure in the film's palette (art/dio.png, RGBA, half body).
src/dio.jpg = the user's photo; src/dio_mask.png = person mask (rembg, isnet-general-use; made once, kept in the repo).
Classes by colour: navy shirt → black (+ one dark tone), skin → two flat tones, hair/features → black, khaki → pale,
lanyard → red, white card/paper/logo → paper white. Then a mode filter, speck removal and a uniform black outline.
Run with a Python that has opencv-python-headless, numpy, scipy, pillow:  python tools/stylize.py"""
import os
import cv2
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img = cv2.imread(os.path.join(HERE, 'src', 'dio.jpg'))
mask = cv2.imread(os.path.join(HERE, 'src', 'dio_mask.png'), cv2.IMREAD_GRAYSCALE)
X0, Y0, X1, Y1, SC = 600, 1040, 2480, 4000, .5          # half body crop (source pixels), then scale
img = cv2.resize(img[Y0:Y1, X0:X1], None, fx=SC, fy=SC, interpolation=cv2.INTER_AREA)
mask = cv2.resize(mask[Y0:Y1, X0:X1], None, fx=SC, fy=SC, interpolation=cv2.INTER_AREA)
m = mask > 128
lab, n = ndi.label(m); sizes = ndi.sum(m, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sizes)))   # largest blob only
m = ndi.binary_fill_holes(m)

sm = cv2.bilateralFilter(img, 9, 40, 9); sm = cv2.bilateralFilter(sm, 9, 40, 9)
hsv = cv2.cvtColor(sm, cv2.COLOR_BGR2HSV).astype(np.float32)
H, S, V = hsv[..., 0] * 2, hsv[..., 1] / 255, hsv[..., 2] / 255
B, G, R = [sm[..., i].astype(np.float32) for i in range(3)]

K_BLK, K_DK, K_SKIN, K_SKIN2, K_PALE, K_WHT, K_RED = range(7)
yy = np.arange(m.shape[0])[:, None] * np.ones(m.shape)
HEAD = yy < 470                                          # above the collar (crop coordinates)
cls = np.full(m.shape, K_BLK, np.uint8)
skin = (H < 40) & (S > .16) & (S < .75) & (V > .33) & (R > B + 20)
white = (S < .16) & (V > .78)
redish = (((H > 290) | (H < 12)) & (S > .35) & (R > B + 30)) | ((H > 170) & (H < 215) & (S > .35) & (V > .55))
# head: hair and features black, skin two tones, eye whites paper
cls[HEAD & skin] = K_SKIN
cls[HEAD & skin & (V < .64)] = K_SKIN2
cls[HEAD & redish & ~(V < .3)] = K_SKIN2                  # lips stay skin, never red
cls[HEAD & white & ~skin] = K_WHT
xx = np.broadcast_to(np.arange(m.shape[1])[None, :], m.shape)
MOUTH = (yy > 330) & (yy < 400) & (xx > 440) & (xx < 590)
cls[HEAD & (V < .30) & ~MOUTH] = K_BLK
cls[HEAD & MOUTH & ((V < .30) | ~skin)] = K_SKIN2                 # the mouth is redrawn below as one closed line
# body: shirt black with one dark tone from a heavily blurred value (big shapes, no wrinkle blotches)
Vb = cv2.GaussianBlur(V.astype(np.float32), (0, 0), 9)
body = ~HEAD
cls[body] = np.where(Vb[body] > .40, K_DK, K_BLK)
cls[body & skin] = K_SKIN
cls[body & skin & (V < .62)] = K_SKIN2
red = body & redish & (xx > 360) & (xx < 640) & (yy < 980)          # the lanyard only, not the shirt print
red = ndi.binary_closing(red, iterations=4)
lb, nn = ndi.label(red); sz = ndi.sum(red, lb, range(1, nn + 1)); red = np.isin(lb, 1 + np.where(sz > 400)[0])
cls[red] = K_RED
wh = body & white & ~skin & (xx > 330)                               # pocket paper and ID card, not the print
lb, nn = ndi.label(wh); sz = ndi.sum(wh, lb, range(1, nn + 1)); wh = ndi.binary_fill_holes(np.isin(lb, 1 + np.where(sz > 600)[0]))
cls[wh] = K_WHT
# mode filter: each pixel takes the most common class in a 7×7 window
votes = np.stack([cv2.boxFilter((cls == k).astype(np.float32), -1, (9, 9)) for k in range(7)])
cls = votes.argmax(0).astype(np.uint8)
# remove specks below 60 px by absorbing them into their surroundings
for k in range(7):
    lb, nn = ndi.label(cls == k)
    if nn == 0: continue
    sz = ndi.sum(np.ones_like(lb), lb, range(1, nn + 1))
    small = np.isin(lb, 1 + np.where(sz < 60)[0])
    if small.any():
        v2 = votes.copy(); v2[k][small] = -1
        cls[small] = v2[:, small].argmax(0)

PAL = {K_BLK: (10, 10, 12), K_DK: (38, 38, 46), K_SKIN: (236, 200, 172), K_SKIN2: (205, 156, 128),
       K_PALE: (216, 212, 204), K_WHT: (242, 239, 232), K_RED: (212, 22, 43)}
out = np.zeros((*cls.shape, 4), np.uint8)
for k, c in PAL.items(): out[cls == k, :3] = c
# outline: class boundaries (not between black and dark-shirt) + the silhouette edge, ~4 px
edge = np.zeros(cls.shape, bool)
for dy, dx in [(0, 1), (1, 0)]:
    a, b = cls, np.roll(cls, (-dy, -dx), (0, 1))
    diff = (a != b) & ~(np.isin(a, [K_BLK, K_DK]) & np.isin(b, [K_BLK, K_DK])) & ~(np.isin(a, [K_SKIN, K_SKIN2]) & np.isin(b, [K_SKIN, K_SKIN2]))
    edge |= diff
edge = ndi.binary_dilation(edge, iterations=1)
sil = ndi.binary_dilation(m, iterations=3) & ~ndi.binary_erosion(m, iterations=1)
out[(edge & m) | sil, :3] = (10, 10, 12)
alpha = ndi.binary_dilation(m, iterations=3)
cv2.polylines(out, [np.array([[482, 372], [497, 379], [522, 378], [540, 368]], np.int32)], False, (10, 10, 12, 255), 5, cv2.LINE_AA)   # closed smile
out[..., 3] = alpha * 255
os.makedirs(os.path.join(HERE, 'art'), exist_ok=True)
cv2.imwrite(os.path.join(HERE, 'art', 'dio.png'), cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
print('art/dio.png', out.shape)
