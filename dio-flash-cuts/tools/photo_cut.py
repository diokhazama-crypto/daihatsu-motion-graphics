"""Dio's photo → a detailed cut-out for the colour shots (art/dio_photo.png, RGBA, same crop/scale as art/dio.png).
Keeps the real photo (face, shirt, lanyard), softly graded to sit on the film's red: a touch more contrast,
slightly lower saturation except reds, a crisp unsharp mask, and a uniform black outline (the style's line).
Run with a Python that has opencv-python-headless, numpy, scipy:  python tools/photo_cut.py"""
import os
import cv2
import numpy as np
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
img = cv2.imread(os.path.join(HERE, 'src', 'dio.jpg'))
mask = cv2.imread(os.path.join(HERE, 'src', 'dio_mask.png'), cv2.IMREAD_GRAYSCALE)
X0, Y0, X1, Y1, SC = 600, 1040, 2480, 4000, .5          # identical to tools/stylize.py (the head rig shares coordinates)
img = cv2.resize(img[Y0:Y1, X0:X1], None, fx=SC, fy=SC, interpolation=cv2.INTER_AREA).astype(np.float32) / 255
a = cv2.resize(mask[Y0:Y1, X0:X1], None, fx=SC, fy=SC, interpolation=cv2.INTER_AREA).astype(np.float32) / 255
m = a > .5
lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = ndi.binary_fill_holes(lab == (1 + int(np.argmax(sz))))
a = a * m

# grade: unsharp mask, gentle S-curve, saturation down 12 % except reds
blur = cv2.GaussianBlur(img, (0, 0), 2.0); img = np.clip(img + (img - blur) * .6, 0, 1)
img = np.clip(.5 + (img - .5) * 1.12, 0, 1)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
red = ((hsv[..., 0] < 15) | (hsv[..., 0] > 330)) & (hsv[..., 1] > .4)
hsv[..., 1] *= np.where(red, 1.0, .88)
img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# black outline, ~4 px, outside the figure
ring = ndi.binary_dilation(m, iterations=4) & ~m
out = np.zeros((*m.shape, 4), np.float32)
out[..., :3] = img * a[..., None]
out[..., 3] = a
out[ring, :3] = (10 / 255, 10 / 255, 12 / 255); out[ring, 3] = 1
rgb = np.where(out[..., 3:] > 0, out[..., :3] / np.maximum(out[..., 3:], 1e-6), 0)
res = np.dstack([np.clip(rgb, 0, 1), out[..., 3:]]) * 255
os.makedirs(os.path.join(HERE, 'art'), exist_ok=True)
cv2.imwrite(os.path.join(HERE, 'art', 'dio_photo.png'), res.astype(np.uint8))
print('art/dio_photo.png', res.shape)
