"""Buat ulang lembar karakter Pak Bos: python3 referensi/lembar_pakbos.py  ->  referensi/PakBos_lembar_karakter.png
Definisi tokoh: CH['pakbos'] di aset_dasar.py (safari=True, gendut=True, kepala, bahu, arm_w, leg_w; badan di safari_badan)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import cairo, aset_dasar as lib
from aset_dasar import hx, text
lib.SHADE = True
W, H = 2620, 900
s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *hx('#F3EEE2')); g.add_color_stop_rgb(1, *hx('#D9CFBC')); c.set_source(g); c.paint()
POSE = [("SANTAI", dict(aF=(12, 18), aB=(-10, -14), expr='smile', eyes='open', look=(0, 0))),
        ("KACAK PINGGANG", dict(aF=(40, -100), aB=(-40, 100), expr='flat', eyes='squint', brows='angry', look=(4, 0))),
        ("MENUNJUK", dict(aF=(92, -6), aB=(-10, -14), expr='grin', eyes='open', brows='up', look=(6, 0))),
        ("JEMPOL", dict(aF=(100, -15), thumb=True, expr='grin', eyes='happy', brows='up', look=(4, -2))),
        ("BERWIBAWA", dict(aF=(38, -100), aB=(38, -100), expr='smile', eyes='half', brows='smug', look=(0, 2)))]
for i, (lbl, po) in enumerate(POSE):
    x = 200 + i * 440
    lib.person(c, x, 800, 'pakbos', po, s=1.45, t=1.0 + i * .7)
    text(c, lbl, x, 860, 28, hx('#3B2A1E'), font="Inter Black")
lib.person(c, 2400, 800, 'rahmat', {'expr': 'smile', 'look': (-4, 0)}, s=1.45, t=1.0)
text(c, "PEMBANDING: PAK RAHMAT", 2400, 860, 24, hx('#3B2A1E'), font="Inter Black")
text(c, "PAK BOS - LEMBAR KARAKTER", W / 2, 46, 44, hx('#3B2A1E'), font="Inter Black")
s.write_to_png(os.path.join(ROOT, 'referensi', 'PakBos_lembar_karakter.png'))
print('ok')
