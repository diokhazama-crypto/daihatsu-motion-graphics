import sys, math, random, json, subprocess
import numpy as np
import cairo
from PIL import Image, ImageFilter
import aset_dasar as lib
from aset_dasar import (W, H, OUT, hx, clamp, ease, eout, lerp, pop, fs, fill, rrect, ell, poly, line, text,
                 person, CH, sweat, spark, bulb_glow, zzz, exclaim, sack)

PRO = '--pro' in sys.argv
lib.SHADE = PRO
FPS = 60 if PRO else 30
DUR = 56.36
NF = int(DUR * FPS)

def spring(t, t0, amp=1.0, freq=14, damp=6):
    if t < t0: return 0.0
    d = t - t0
    return amp * math.exp(-damp * d) * math.sin(freq * d)

def kf(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        if ta <= t <= tb:
            k = ease((t - ta) / (tb - ta))
            if isinstance(va, tuple): return tuple(lerp(a, b, k) for a, b in zip(va, vb))
            return lerp(va, vb, k)
    return keys[-1][1]

def env_t(t):
    return lib.env(t)

# ------------------------------------------------------------ words
WORDS = []   # master: narasi episode dibaca di gaya.py
FIX = {3: "Gran", 13: "bahan", 14: "gosip", 19: "nyinyir.", 24: "sok kaya", 59: "beras", 60: "sekilo", 65: "toko",
       71: "Gran", 82: "melongo.", 83: "Sorenya,", 85: "Bu Julit", 93: "besok", 94: "ke sini", 112: "Pak Rahmat,", 117: "jebakan?"}
words = [[FIX.get(i, w), a, b] for i, (w, a, b) in enumerate(WORDS)]
# merge "Ha ha ha"
CHUNKS = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w[0][-1] in ",.?!" or len(" ".join(x[0] for x in cur)) > 15:
        CHUNKS.append(cur); cur = []
if cur: CHUNKS.append(cur)

# speakers (mouth animation)
def talk(t, spans):
    for a, b in spans:
        if a <= t <= b:
            e = env_t(t)
            return clamp((e - 0.12) * 1.4) * (0.6 + 0.4 * abs(math.sin(t * 19)))
    return 0.0
JULIT_SPEAK = [(0.0, 2.0), (9.4, 13.5)]
ISTRI_SPEAK = [(39.9, 42.7)]

# ------------------------------------------------------------ characters (detailed)
CH['rahmat'] = dict(skin=hx('#D39B6B'), shirt=hx('#2F8F5B'), pants=hx('#5A4232'), hair='peci', mus=True, kind='man',
                    collar=True, collar_col=hx('#257A4C'), buttons=True, pocket=True, belt=hx('#3B2A1E'), watch=hx('#E8E8E8'),
                    foot='sandal', sandal_col=hx('#5A3A22'), peci_band=hx('#C9A43A'), cuff=hx('#257A4C'))
CH['burahmat'] = dict(skin=hx('#E3AE85'), dress=hx('#C98A3B'), dots=hx('#7A3E1E'), hair='hijab', hij=hx('#8E2443'), ciput=hx('#F3E5C8'),
                      bros=hx('#F2C230'), kind='daster', celemek=hx('#F4F1EA'), trim=hx('#7A3E1E'), gelang=True, foot='sandal', sandal_col=hx('#8E2443'))
CH['julit'] = dict(skin=hx('#F1C6A0'), dress=hx('#9B4DCA'), dots=hx('#F7A8D8'), hair='rollers', lips=True, kind='daster',
                   kalung=True, gelang=True, trim=hx('#F7A8D8'), foot='sandal', sandal_col=hx('#E5473B'))
CH['friend'] = dict(skin=hx('#E3AE85'), dress=hx('#2EAD6B'), dots=hx('#FFF3B0'), hair='hijab', hij=hx('#F5C02E'), ciput=hx('#FFFFFF'),
                    bros=hx('#E5473B'), kind='daster', trim=hx('#FFF3B0'), foot='sandal', sandal_col=hx('#2E86DE'))
CH['bos'] = dict(skin=hx('#E3AE85'), shirt=hx('#7A3E1E'), pants=hx('#2B2B33'), hair='short', kind='man', pattern='batik', pat_col=hx('#F2C230'),
                 collar=True, buttons=True, belt=hx('#1E1E1E'), watch=hx('#F2C230'), kacamata=True, long=True, foot='shoe')
CH['anak'] = dict(skin=hx('#D39B6B'), shirt=hx('#E5473B'), pants=hx('#2C3E66'), hair='spiky', kind='man', pattern='garis', pat_col=(1, 1, 1),
                  foot='sandal')

# ------------------------------------------------------------ small detailed props
PRODUCT_COLS = ['#E5473B', '#F2C230', '#2E86DE', '#2EAD6B', '#F07D2B', '#9B4DCA', '#FFFFFF', '#F07AA8', '#7AC74F']

def product(c, x, yb, kind, col, w=40, h=60):
    if kind == 'botol':
        rrect(c, x + 4, yb - h, w - 8, h, 8); fs(c, hx('#F4C430'), 3)
        c.rectangle(x + 4, yb - h * .6, w - 8, h * .3); fill(c, hx(col))
        c.rectangle(x + w / 2 - 6, yb - h - 10, 12, 12); fs(c, hx('#2EAD6B'), 2)
        c.rectangle(x + 8, yb - h + 6, 4, h - 14); fill(c, (1, 1, 1), .5)
    elif kind == 'mie':
        rrect(c, x, yb - h * .5, w + 10, h * .5, 3); fs(c, hx(col), 3)
        ell(c, x + (w + 10) / 2, yb - h * .27, w * .3, h * .14); fill(c, (1, 1, 1), .8)
        c.rectangle(x + 3, yb - h * .5 + 3, w + 4, 5); fill(c, (1, 1, 1), .5)
    elif kind == 'gula':
        rrect(c, x, yb - h * .75, w, h * .75, 6); fs(c, (1, 1, 1), 3)
        c.rectangle(x + 3, yb - h * .5, w - 6, h * .22); fill(c, hx('#2E6BD6'))
    elif kind == 'kaleng':
        rrect(c, x + 2, yb - h * .55, w - 4, h * .55, 4); fs(c, hx('#C9CED4'), 3)
        c.rectangle(x + 2, yb - h * .45, w - 4, h * .3); fill(c, hx(col))
    else:
        c.rectangle(x, yb - h, w, h); fs(c, hx(col), 3)
        c.rectangle(x + 4, yb - h * .62, w - 8, h * .22); fill(c, (1, 1, 1), .7)
        c.rectangle(x + 4, yb - h * .3, w * .5, 4); fill(c, (0, 0, 0), .3)

RNG = random.Random(11)
SHELF_ITEMS = []
for row, yb in enumerate([838, 948, 1058]):
    x = 700
    while x < 1440:
        kind = RNG.choice(['botol', 'mie', 'gula', 'kaleng', 'kotak', 'kotak'])
        w = {'botol': 34, 'mie': 40, 'gula': 40, 'kaleng': 34, 'kotak': RNG.choice([36, 44])}[kind]
        h = RNG.choice([60, 72, 84])
        SHELF_ITEMS.append((x, yb, kind, RNG.choice(PRODUCT_COLS), w, h, RNG.random()))
        x += w + (10 if kind == 'mie' else 0) + RNG.choice([3, 5, 8])

def timbangan(c, x, y, s=1.0, needle=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -50, -20, 100, 20, 6); fs(c, hx('#D7141A'), 4)
    rrect(c, -36, -90, 72, 72, 10); fs(c, hx('#D7141A'), 4)
    ell(c, 0, -54, 26, 26); fs(c, (1, 1, 1), 3)
    for k in range(9):
        a = math.radians(-120 + k * 30)
        c.move_to(20 * math.sin(a), -54 - 20 * math.cos(a)); c.line_to(24 * math.sin(a), -54 - 24 * math.cos(a))
        c.set_source_rgb(*OUT); c.set_line_width(2); c.stroke()
    a = math.radians(-100 + needle * 200)
    c.move_to(0, -54); c.line_to(20 * math.sin(a), -54 - 20 * math.cos(a)); c.set_source_rgb(*hx('#D7141A')); c.set_line_width(3); c.stroke()
    ell(c, 0, -108, 56, 12); fs(c, hx('#C9CED4'), 4)
    c.rectangle(-4, -100, 8, 12); fill(c, OUT)
    c.restore()

def toples(c, x, y, col):
    rrect(c, x - 30, y - 70, 60, 70, 12); fs(c, hx('#DDF1F8'), 3, .7)
    for k in range(8):
        ell(c, x - 18 + (k % 4) * 12, y - 14 - (k // 4) * 16, 7, 7); fill(c, hx(PRODUCT_COLS[(k + len(col)) % 9]))
    rrect(c, x - 26, y - 84, 52, 16, 5); fs(c, hx(col), 3)
    c.rectangle(x - 22, y - 64, 6, 50); fill(c, (1, 1, 1), .5)

def blek_kerupuk(c, x, y):
    c.rectangle(x - 45, y - 120, 90, 120); fs(c, hx('#C9CED4'), 4)
    rrect(c, x - 32, y - 100, 64, 60, 6); fs(c, hx('#DDF1F8'), 3, .85)
    for k in range(6):
        ell(c, x - 18 + (k % 3) * 18, y - 82 + (k // 3) * 20, 10, 7); fill(c, hx('#F6E3A0'))
    rrect(c, x - 48, y - 130, 96, 14, 4); fs(c, hx('#E23A3A'), 3)
    text(c, "KERUPUK", x, y - 22, 14, hx('#E23A3A'))

def kulkas(c, x, y, w=150, h=470):
    rrect(c, x, y - h, w, h, 10); fs(c, (1, 1, 1), 5)
    rrect(c, x + 8, y - h + 8, w - 16, 50, 6); fs(c, hx('#2E86DE'), 3)
    text(c, "DINGIN", x + w / 2, y - h + 33, 26, (1, 1, 1))
    rrect(c, x + 12, y - h + 68, w - 24, h - 110, 6); fs(c, hx('#BFE4F2'), 3)
    for r in range(4):
        yb = y - h + 150 + r * 85
        c.rectangle(x + 16, yb, w - 32, 4); fill(c, hx('#9AB5C4'))
        for k in range(5):
            bx = x + 22 + k * 23
            rrect(c, bx, yb - 62, 16, 62, 5); fs(c, hx(PRODUCT_COLS[(r * 3 + k) % 9]), 2)
            c.rectangle(bx + 3, yb - 72, 10, 10); fill(c, OUT)
    poly(c, [(x + 30, y - h + 70), (x + 60, y - h + 70), (x + 20, y - 45), (x + 14, y - 45)]); fill(c, (1, 1, 1), .35)
    rrect(c, x + w - 24, y - h / 2 - 40, 8, 80, 4); fs(c, hx('#9AA1A9'), 2)

def tabung_gas(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -30, -90, 60, 90, 22); fs(c, hx('#7AC74F'), 4)
    rrect(c, -16, -108, 32, 20, 6); fs(c, hx('#7AC74F'), 3)
    c.rectangle(-30, -60, 60, 6); fill(c, (0, 0, 0), .2)
    text(c, "3kg", 0, -36, 18, (1, 1, 1), OUT, 3)
    c.restore()

def rak_telur(c, x, y, n=4):
    for k in range(n):
        yy = y - k * 22
        rrect(c, x - 55, yy - 16, 110, 18, 3); fs(c, hx('#B8A27A'), 3)
        for j in range(5):
            ell(c, x - 44 + j * 22, yy - 20, 10, 12); fs(c, hx('#F3D9B1'), 2)

def galon(c, x, y):
    rrect(c, x - 30, y - 100, 60, 100, 18); fs(c, hx('#7CC4F5'), 4, .85)
    rrect(c, x - 14, y - 118, 28, 22, 6); fs(c, hx('#2E86DE'), 3)
    c.rectangle(x - 22, y - 80, 8, 60); fill(c, (1, 1, 1), .5)

def kresek(c, x, y, col):
    c.move_to(x - 16, y); c.curve_to(x - 26, y + 40, x - 18, y + 70, x, y + 72); c.curve_to(x + 18, y + 70, x + 26, y + 40, x + 16, y)
    c.close_path(); fs(c, col, 3)
    ell(c, x - 8, y - 6, 6, 8); c.set_source_rgb(*OUT); c.set_line_width(3); c.stroke()
    ell(c, x + 8, y - 6, 6, 8); c.stroke()

def chalkboard(c, x, y, lines_):
    c.move_to(x - 70, y); c.line_to(x - 40, y - 330); c.move_to(x + 70, y); c.line_to(x + 40, y - 330)
    c.set_source_rgb(*hx('#6B4A33')); c.set_line_width(10); c.stroke()
    rrect(c, x - 110, y - 330, 220, 250, 8); fs(c, hx('#8A5A30'), 5)
    c.rectangle(x - 96, y - 316, 192, 222); fill(c, hx('#2F3A32'))
    text(c, "HARGA HARI INI", x, y - 292, 20, hx('#FFE14D'), font="Inter Black")
    for i, l_ in enumerate(lines_):
        text(c, l_, x, y - 252 + i * 38, 19, (1, 1, 1), font="Inter")

def rosters(c, x0, x1, y, h=60):
    n = int((x1 - x0) / h)
    for i in range(n):
        bx = x0 + i * h
        c.rectangle(bx + 2, y + 2, h - 4, h - 4); fs(c, hx('#E8DCC4'), 3)
        ell(c, bx + h / 2, y + h / 2, h * .28, h * .28); fill(c, hx('#5A4A3A'))
        poly(c, [(bx + h / 2, y + 8), (bx + h - 8, y + h / 2), (bx + h / 2, y + h - 8), (bx + 8, y + h / 2)]); c.set_source_rgba(0, 0, 0, .25); c.set_line_width(2); c.stroke()

def bricks(c, x0, y0, x1, y1, col='#C0703A'):
    c.save(); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.clip()
    c.rectangle(x0, y0, x1 - x0, y1 - y0); fill(c, hx(col))
    for r in range(int((y1 - y0) / 22) + 1):
        yy = y0 + r * 22
        c.move_to(x0, yy); c.line_to(x1, yy); c.set_source_rgba(.95, .9, .8, .8); c.set_line_width(3); c.stroke()
        off = 0 if r % 2 else 30
        for k in range(int((x1 - x0) / 60) + 2):
            xx = x0 + off + k * 60
            c.move_to(xx, yy); c.line_to(xx, yy + 22); c.stroke()
    c.restore()
    c.rectangle(x0, y0, x1 - x0, y1 - y0); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()

STONES = [(random.Random(i).uniform(0, 1), random.Random(i + 3).uniform(0, 1), random.Random(i + 7).uniform(.6, 1.2), random.Random(i + 9).random()) for i in range(120)]
def batu_alam(c, x0, y0, x1, y1):
    c.save(); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.clip()
    c.rectangle(x0, y0, x1 - x0, y1 - y0); fill(c, hx('#8E8A80'))
    for u, v, s, r in STONES:
        x = x0 + u * (x1 - x0); y = y0 + v * (y1 - y0)
        col = [hx('#B5AC9A'), hx('#A39886'), hx('#C9C0AE'), hx('#9A8F7E')][int(r * 4)]
        poly(c, [(x - 30 * s, y - 12 * s), (x + 4 * s, y - 20 * s), (x + 32 * s, y - 6 * s), (x + 22 * s, y + 16 * s), (x - 20 * s, y + 18 * s)])
        fs(c, col, 2)
    c.restore()
    c.rectangle(x0, y0, x1 - x0, y1 - y0); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()

def genteng(c, x0, x1, y0, y1, apex_x):
    poly(c, [(x0, y1), (x1, y1), (apex_x + 120, y0), (apex_x - 120, y0)]); fs(c, hx('#B8452E'), 6)
    c.save(); poly(c, [(x0, y1), (x1, y1), (apex_x + 120, y0), (apex_x - 120, y0)]); c.clip()
    rows = int((y1 - y0) / 34)
    for r in range(rows + 1):
        yy = y0 + r * 34
        frac = (yy - y0) / (y1 - y0)
        xa = lerp(apex_x - 120, x0, frac); xb = lerp(apex_x + 120, x1, frac)
        off = 0 if r % 2 else 24
        x = xa - 48 + off
        while x < xb + 48:
            c.arc(x + 24, yy, 24, 0, math.pi); c.set_source_rgba(.45, .12, .06, .5); c.set_line_width(3); c.stroke()
            x += 48
        c.rectangle(xa - 60, yy - 2, xb - xa + 120, 4); fill(c, (1, .7, .5), .25)
    c.restore()
    rrect(c, apex_x - 130, y0 - 18, 260, 22, 8); fs(c, hx('#8E2F1E'), 5)
    c.rectangle(x0 - 10, y1 - 4, x1 - x0 + 20, 16); fs(c, hx('#E8E2D4'), 4)

def tree(c, x, y, s=1.0, t=0.0, dark=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    poly(c, [(-22, 0), (22, 0), (14, -260), (-14, -260)]); fs(c, hx('#6B4A33'), 5)
    for k in range(5):
        c.move_to(-12, -40 - k * 45); c.curve_to(-4, -50 - k * 45, 4, -30 - k * 45, 10, -44 - k * 45); c.set_source_rgba(0, 0, 0, .25); c.set_line_width(3); c.stroke()
    line(c, [(0, -200), (-70, -300)], 14, hx('#6B4A33')); line(c, [(0, -220), (80, -310)], 14, hx('#6B4A33'))
    sway = 5 * math.sin(t * 1.3 + x)
    cols = [hx('#2E7D32'), hx('#3E9B47'), hx('#58B05E'), hx('#7CC56E')] if not dark else [hx('#14321C'), hx('#1C3F24'), hx('#22502C'), hx('#2A5C33')]
    blobs = [(-90, -330, 85), (90, -340, 85), (0, -400, 100), (-40, -300, 80), (60, -290, 75), (0, -320, 90)]
    for i, (dx, dy, r) in enumerate(blobs):
        ell(c, dx + sway, dy, r, r * .85); fs(c, cols[i % 2], 5)
    for i, (dx, dy, r) in enumerate(blobs):
        ell(c, dx + sway - r * .25, dy - r * .25, r * .45, r * .35); fill(c, cols[2 + i % 2], .9)
    c.restore()

def tiang_listrik(c, x, t, night=False):
    c.rectangle(x - 13, 200, 26, 1150); fs(c, hx('#8D8F93'), 5)
    for k in range(10):
        c.rectangle(x - 13, 300 + k * 100, 26, 4); fill(c, (0, 0, 0), .2)
    c.rectangle(x - 120, 250, 240, 16); fs(c, hx('#6F7276'), 4)
    for dx in (-100, -40, 40, 100):
        rrect(c, x + dx - 6, 232, 12, 20, 4); fs(c, hx('#E8E2D4'), 2)
    rrect(c, x + 16, 420, 70, 110, 8); fs(c, hx('#9AA1A9'), 4)        # transformer
    c.rectangle(x + 24, 440, 54, 6); fill(c, (0, 0, 0), .25)
    rrect(c, x - 70, 760, 110, 34, 6); fs(c, hx('#2E7D32'), 4)
    text(c, "JL. MAWAR", x - 15, 777, 18, (1, 1, 1))
    for k in range(3):   # posters stuck on pole
        c.rectangle(x - 12, 1000 + k * 60, 24, 40); fill(c, hx(['#F2C230', '#FFFFFF', '#F07AA8'][k]), .9)

def wires(c, x0, x1, ys, t):
    for i, yy in enumerate(ys):
        sag = 70 + i * 12
        c.move_to(x0, yy); c.curve_to(lerp(x0, x1, .3), yy + sag, lerp(x0, x1, .7), yy + sag, x1, yy)
        c.set_source_rgb(*hx('#2B2B30')); c.set_line_width(4); c.stroke()

def bird(c, x, y, t, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    ell(c, 0, 0, 18, 12); fs(c, hx('#5A4A3A'), 3)
    ell(c, 14, -8, 9, 9); fs(c, hx('#5A4A3A'), 3)
    poly(c, [(22, -9), (30, -6), (22, -4)]); fill(c, hx('#F2C230'))
    ell(c, 16, -10, 2, 2); fill(c, OUT)
    c.move_to(-18, 0); c.line_to(-30, 6 + 3 * math.sin(t * 6)); c.set_source_rgb(*OUT); c.set_line_width(3); c.stroke()
    c.restore()

# ------------------------------------------------------------ TOKO (detailed)
def toko(c, t, mode='normal', night=False, shutter=0.0):
    # mode: normal | kosong | habis
    # building body
    c.rectangle(620, 380, 1100, 960); fs(c, hx('#F3E5C8'), 6)
    rosters(c, 660, 1680, 395, 60)
    c.rectangle(620, 455, 1100, 14); fs(c, hx('#E0CFAE'), 4)
    # sign
    rrect(c, 650, 475, 1040, 170, 14); fs(c, hx('#D8312B'), 7)
    rrect(c, 664, 489, 1012, 142, 10); c.set_source_rgba(1, 1, 1, .35); c.set_line_width(3); c.stroke()
    text(c, "TOKO SEMBAKO RAHMAT", 1170, 535, 66, hx('#FFE14D'), OUT, 10)
    text(c, "Sedia: Beras • Minyak • Gula • Telur • Gas LPG", 1170, 588, 26, (1, 1, 1), OUT, 4)
    text(c, "Telp/WA 08xx-xxxx-xxxx", 1170, 618, 18, hx('#FFE14D'))
    for bx in (690, 1650):
        ell(c, bx, 500, 7, 7); fs(c, hx('#C9CED4'), 2)
    # pillars + bricks
    c.rectangle(620, 650, 60, 690); fs(c, hx('#E9DABA'), 5)
    c.rectangle(1660, 650, 60, 690); fs(c, hx('#E9DABA'), 5)
    bricks(c, 620, 1150, 680, 1340); bricks(c, 1660, 1150, 1720, 1340)
    # interior
    dark = .55 if night else 0
    c.rectangle(680, 730, 980, 610); fs(c, hx('#7A4E2E'), 5)
    c.rectangle(684, 734, 972, 60); fill(c, hx('#6A4026'))
    # TL lamp
    rrect(c, 1020, 744, 300, 16, 8); fs(c, (1, 1, 1), 3)
    if night: bulb_glow(c, 1170, 760, 520, .5)
    # shelves
    for yb in (848, 958, 1068):
        c.rectangle(690, yb, 760, 14); fs(c, hx('#B98A56'), 3)
        for bx in (700, 1440):
            c.rectangle(bx - 4, yb + 10, 8, 30); fill(c, hx('#8A5E30'))
    for (sx, yb, kind, col, w, h, r) in SHELF_ITEMS:
        if mode == 'kosong' and r > .12: continue
        product(c, sx, yb, kind, col, w, h)
    if mode == 'kosong':
        for k in range(4):   # cobweb + dust
            c.move_to(690, 794 + k * 12); c.curve_to(720, 810 + k * 8, 740, 800 + k * 6, 760 - k * 10, 794)
            c.set_source_rgba(1, 1, 1, .5); c.set_line_width(1.5); c.stroke()
        for k in range(30):
            ell(c, 700 + (k * 97 % 740), 860 + (k * 53 % 200), 2, 2); fill(c, (1, 1, 1), .35)
    # hanging kresek + sachets
    for k in range(4):
        kresek(c, 720 + k * 38, 800, [hx('#E5473B'), hx('#1E1E1E'), hx('#F4F1EA'), hx('#2E86DE')][k])
    for k in range(3):
        xx = 1290 + k * 28
        c.move_to(xx + 11, 794); c.line_to(xx + 11, 806); c.set_source_rgb(*OUT); c.set_line_width(2); c.stroke()
        for j in range(5):
            rrect(c, xx, 806 + j * 30, 22, 27, 3); fs(c, hx(PRODUCT_COLS[(k * 5 + j) % 9]), 2)
    # kulkas
    kulkas(c, 1490, 1340)
    # counter
    c.rectangle(860, 1140, 600, 26); fs(c, hx('#A8763E'), 5)
    c.rectangle(870, 1166, 580, 174); fs(c, hx('#BFE4F2'), 5, .85)
    for i in range(8):
        product(c, 885 + i * 70, 1320, ['kotak', 'kaleng', 'mie', 'gula'][i % 4], PRODUCT_COLS[i % 9], 44, 70)
    c.move_to(900, 1176); c.line_to(960, 1330); c.set_source_rgba(1, 1, 1, .6); c.set_line_width(10); c.stroke()
    timbangan(c, 930, 1140, .9, .35 + .05 * math.sin(t * 2))
    for i, col in enumerate(['#E5473B', '#2E86DE', '#F2C230']):
        toples(c, 1110 + i * 72, 1140, col)
    rrect(c, 1340, 1110, 60, 30, 4); fs(c, hx('#3A3A44'), 3)     # kalkulator
    for k in range(6):
        c.rectangle(1346 + (k % 3) * 18, 1116 + (k // 3) * 11, 12, 7); fill(c, (1, 1, 1), .7)
    # kerupuk tins + eggs + sacks
    blek_kerupuk(c, 770, 1340); blek_kerupuk(c, 1580, 1340) if False else None
    rak_telur(c, 1400, 1130, 0)
    if mode == 'habis':
        for k in range(3):
            poly(c, [(700 + k * 50, 1340), (760 + k * 50, 1340), (750 + k * 50, 1300), (710 + k * 50, 1306)]); fs(c, hx('#EDE6D4'), 3)
        rrect(c, 690, 1180, 160, 70, 6); fs(c, (1, 1, 1), 4)
        text(c, "BERAS", 770, 1200, 24, hx('#D8312B'))
        text(c, "HABIS", 770, 1232, 30, hx('#D8312B'))
    elif mode != 'kosong':
        for (sx, sy) in [(760, 1300), (860, 1306), (810, 1232)]:
            sack(c, sx - 20, sy, 110, 72)
    # shutter (rolled)
    c.rectangle(670, 718, 1000, 24); fs(c, hx('#9AA1A9'), 4)
    if shutter > 0:
        sh_h = shutter * 600
        c.rectangle(680, 742, 980, sh_h); fs(c, hx('#B9C0C8'), 4)
        for k in range(int(sh_h / 18)):
            c.rectangle(680, 742 + k * 18, 980, 3); fill(c, (0, 0, 0), .18)
    # awning seng
    poly(c, [(600, 650), (1740, 650), (1790, 735), (550, 735)]); fs(c, hx('#5C88B5'), 6)
    c.save(); poly(c, [(600, 650), (1740, 650), (1790, 735), (550, 735)]); c.clip()
    for k in range(60):
        xx = 560 + k * 22
        c.move_to(xx + 30, 650); c.line_to(xx, 735); c.set_source_rgba(1, 1, 1, .25 if k % 2 else .0); c.set_line_width(8); c.stroke()
        c.move_to(xx + 41, 650); c.line_to(xx + 11, 735); c.set_source_rgba(0, 0, 0, .15); c.set_line_width(3); c.stroke()
    c.restore()
    c.rectangle(548, 733, 1244, 14); fs(c, hx('#8D8F93'), 4)          # talang
    c.rectangle(560, 747, 14, 593); fs(c, hx('#8D8F93'), 3)           # downpipe
    for bx in (700, 1150, 1640):
        line(c, [(bx, 740), (bx - 40, 800)], 6, hx('#6F7276'), False)
    # meter listrik + kabel
    rrect(c, 630, 900, 40, 56, 4); fs(c, (1, 1, 1), 3)
    rrect(c, 636, 908, 28, 14, 2); fs(c, hx('#2B2B2B'), 2)
    c.move_to(650, 900); c.curve_to(650, 820, 600, 760, 590, 700); c.set_source_rgb(*OUT); c.set_line_width(3); c.stroke()
    # BUKA sign
    if not night or shutter < .5:
        c.move_to(1690, 760); c.line_to(1670, 790); c.move_to(1690, 760); c.line_to(1710, 790); c.set_source_rgb(*OUT); c.set_line_width(2); c.stroke()
        rrect(c, 1650, 790, 80, 36, 6); fs(c, hx('#2EAD6B'), 3)
        text(c, "BUKA", 1690, 808, 18, (1, 1, 1))
    # step tiles
    c.rectangle(600, 1340, 1140, 24); fs(c, hx('#D9D2C0'), 4)
    for k in range(24):
        c.move_to(600 + k * 48, 1340); c.line_to(600 + k * 48, 1364); c.set_source_rgba(0, 0, 0, .2); c.set_line_width(2); c.stroke()
    # gas + galon + chalkboard + bench (outside)
    for k in range(3):
        tabung_gas(c, 1760 + (k % 2) * 60, 1430 - (k // 2) * 96, .9)
    galon(c, 1880, 1430)
    chalkboard(c, 480, 1440, ["Beras 5kg ... 75rb", "Minyak 1L ... 18rb", "Gula 1kg ... 17rb", "Telur 1kg ... 28rb", "Gas 3kg ... 22rb"])

# ------------------------------------------------------------ JULIT HOUSE (detailed)
def rumah_julit(c, t, st):
    night = st.get('night', False)
    # toren on stand
    for lx in (2560, 2640):
        c.rectangle(lx - 5, 470, 10, 140); fs(c, hx('#7D848C'), 3)
    rrect(c, 2540, 470, 120, 16, 4); fs(c, hx('#7D848C'), 3)
    rrect(c, 2550, 360, 100, 112, 30); fs(c, hx('#F07D2B'), 5)
    for k in range(3):
        c.rectangle(2550, 384 + k * 28, 100, 4); fill(c, (0, 0, 0), .2)
    # parabola
    ell(c, 2000, 560, 46, 30); fs(c, hx('#C9CED4'), 4)
    line(c, [(2000, 560), (2030, 530)], 4, hx('#7D848C'), False)
    # walls
    c.rectangle(1850, 740, 860, 600); fs(c, hx('#BFE3B4'), 6)
    batu_alam(c, 1850, 1170, 2710, 1340)
    genteng(c, 1810, 2750, 520, 760, 2280)
    rosters(c, 2000, 2320, 776, 40); rosters(c, 2420, 2560, 776, 35)
    # main window
    wx0, wy0, ww, wh = 2010, 860, 300, 250
    c.rectangle(wx0 - 14, wy0 - 14, ww + 28, wh + 28); fs(c, hx('#8A5A30'), 5)
    win_lit = st.get('win_lit', False)
    c.rectangle(wx0, wy0, ww, wh); fill(c, hx('#FFE9A6') if win_lit else hx('#3C5468'))
    jp = st.get('julit_win')
    if jp is not None:
        c.save(); c.rectangle(wx0, wy0, ww, wh); c.clip()
        person(c, jp.get('x', 2160), 1340 + jp.get('dy', 0), 'julit', jp, t=t, flip=jp.get('flip', True))
        c.restore()
    cl = st.get('curtain', 0.2)
    for side in (0, 1):
        if side == 0:
            c.move_to(wx0, wy0); c.line_to(wx0 + 60 + cl * 70, wy0); c.curve_to(wx0 + 40 + cl * 70, wy0 + 120, wx0 + 70 + cl * 60, wy0 + 200, wx0 + 30, wy0 + wh); c.line_to(wx0, wy0 + wh)
        else:
            c.move_to(wx0 + ww, wy0); c.line_to(wx0 + ww - 60 - cl * 90, wy0); c.curve_to(wx0 + ww - 40 - cl * 90, wy0 + 120, wx0 + ww - 70 - cl * 80, wy0 + 200, wx0 + ww - 30, wy0 + wh); c.line_to(wx0 + ww, wy0 + wh)
        c.close_path(); fs(c, hx('#F28AA8'), 4)
        for k in range(4):
            xx = (wx0 + 12 + k * 14) if side == 0 else (wx0 + ww - 12 - k * 14)
            c.move_to(xx, wy0 + 4); c.line_to(xx + (8 if side == 0 else -8), wy0 + wh - 10); c.set_source_rgba(.6, .2, .3, .35); c.set_line_width(2); c.stroke()
    c.rectangle(wx0, wy0 - 6, ww, 12); fs(c, hx('#C9CED4'), 3)   # curtain rail
    c.rectangle(wx0, wy0, ww, wh); c.set_source_rgb(1, 1, 1); c.set_line_width(14); c.stroke()
    c.move_to(wx0 + ww / 2, wy0); c.line_to(wx0 + ww / 2, wy0 + 40); c.set_source_rgb(1, 1, 1); c.set_line_width(8); c.stroke()
    c.rectangle(wx0, wy0, ww, wh); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
    rrect(c, wx0 - 26, wy0 + wh + 10, ww + 52, 22, 6); fs(c, (1, 1, 1), 4)
    # flower box under window
    rrect(c, wx0 + 10, wy0 + wh + 32, ww - 20, 40, 6); fs(c, hx('#8A5A30'), 4)
    for k in range(8):
        ell(c, wx0 + 30 + k * 36, wy0 + wh + 26, 14, 14); fs(c, hx(['#E5473B', '#F2C230', '#F07AA8', '#FFFFFF'][k % 4]), 2)
        ell(c, wx0 + 30 + k * 36, wy0 + wh + 26, 4, 4); fill(c, hx('#F2C230'))
    # door
    rrect(c, 2410, 960, 160, 380, 6); fs(c, hx('#8A5A30'), 6)
    for (dx, dy, dw, dh) in ((2426, 980, 58, 150), (2496, 980, 58, 150), (2426, 1150, 58, 170), (2496, 1150, 58, 170)):
        rrect(c, dx, dy, dw, dh, 4); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(3); c.stroke()
    ell(c, 2555, 1160, 8, 8); fs(c, hx('#F2C230'), 3)
    rrect(c, 2440, 915, 100, 36, 6); fs(c, (1, 1, 1), 3)
    text(c, "No. 12", 2490, 933, 20, OUT)
    rrect(c, 2588, 1000, 30, 46, 8); fs(c, hx('#3A3A44'), 3)
    ell(c, 2603, 1022, 10, 12); fill(c, hx('#FFE9A6') if night else hx('#F6F1E4'))
    if night: bulb_glow(c, 2603, 1022, 160, .4)
    ell(c, 2398, 1100, 6, 6); fs(c, (1, 1, 1), 2)    # bel
    # AC outdoor
    rrect(c, 2620, 860, 80, 60, 4); fs(c, hx('#E8E8E8'), 4)
    ell(c, 2648, 890, 20, 20); c.set_source_rgba(0, 0, 0, .4); c.set_line_width(3); c.stroke()
    for k in range(3):
        a = t * 12 + k * 2.1
        c.move_to(2648, 890); c.line_to(2648 + 17 * math.cos(a), 890 + 17 * math.sin(a)); c.stroke()
    # terrace chairs
    for k, cx_ in enumerate((2210, 2300)):
        col = hx(['#2E86DE', '#E5473B'][k])
        rrect(c, cx_ - 36, 1240, 72, 14, 5); fs(c, col, 3)
        rrect(c, cx_ - 34, 1180, 14, 64, 5); fs(c, col, 3)
        for lx in (cx_ - 32, cx_ + 30):
            line(c, [(lx, 1254), (lx, 1330)], 7, col, False)
    rrect(c, 2245, 1264, 30, 20, 4); fs(c, (1, 1, 1), 2)     # cup
    # fence
    for px in (1860, 2700):
        c.rectangle(px - 24, 1180, 48, 160); fs(c, hx('#E8E2D4'), 4)
        rrect(c, px - 30, 1166, 60, 18, 4); fs(c, hx('#C9C3B6'), 3)
    rrect(c, 1866, 1150, 30, 34, 4); fs(c, hx('#2E86DE'), 3)      # mailbox
    c.rectangle(1884, 1230, 792, 8); fs(c, hx('#2B2B30'), 2)
    c.rectangle(1884, 1320, 792, 8); fs(c, hx('#2B2B30'), 2)
    for k in range(int(792 / 26)):
        xx = 1890 + k * 26
        if 2400 < xx < 2580: continue
        c.move_to(xx, 1340); c.line_to(xx, 1210); c.set_source_rgb(*hx('#2B2B30')); c.set_line_width(5); c.stroke()
        poly(c, [(xx - 6, 1212), (xx + 6, 1212), (xx, 1196)]); fill(c, hx('#2B2B30'))
    # gate (open)
    c.save(); c.translate(2400, 1340)
    for k in range(6):
        c.move_to(k * 12, 0); c.line_to(k * 12, -120); c.set_source_rgb(*hx('#2B2B30')); c.set_line_width(4); c.stroke()
    c.restore()
    # pots along fence
    for k, px in enumerate((1920, 2010, 2620)):
        poly(c, [(px - 30, 1290), (px + 30, 1290), (px + 22, 1340), (px - 22, 1340)]); fs(c, hx('#C0703A'), 4)
        for j in range(5):
            a = -math.pi / 2 + (j - 2) * .3
            poly(c, [(px - 5, 1290), (px + 5, 1290), (px + 70 * math.cos(a), 1290 + 90 * math.sin(a))]); fs(c, hx('#3E9B47') if k != 1 else hx('#6AA84F'), 2)
    # sandals on terrace
    for k in range(2):
        ell(c, 2350 + k * 22, 1334, 10, 5); fs(c, hx('#E5473B'), 2)

# ------------------------------------------------------------ STREET
BGH = [(i, random.Random(i).choice(['#E8C27A', '#9CCFD8', '#F4A99B', '#C5E1A5', '#D7B9F2']), random.Random(i + 1).randint(180, 320)) for i in range(-8, 18)]
def street(c, t, st):
    tod = st.get('tod', 'day')
    night = tod == 'night'
    skies = {'day': ('#4FA8EE', '#CFEFFF'), 'sore': ('#F2774B', '#FFD58A'), 'night': ('#0D1640', '#2B3A78'), 'morning': ('#58B2F2', '#FFE3B8')}
    top, bot = skies[tod]
    g = cairo.LinearGradient(0, -900, 0, 1340)
    g.add_color_stop_rgb(0, *hx(top)); g.add_color_stop_rgb(1, *hx(bot))
    c.set_source(g); c.rectangle(-3000, -3000, 9000, 4340); c.fill()
    if night:
        for i in range(120):
            ell(c, (i * 173) % 4200 - 900, (i * 97) % 900 - 300, 2.5, 2.5); fill(c, (1, 1, .9), .5 + .5 * math.sin(t * 3 + i))
    else:
        for k in range(6):
            cx_ = (k * 620 + t * 14) % 4400 - 1200; cy_ = 80 + (k * 97 % 280)
            for dx, dy, r in [(0, 0, 50), (55, -20, 60), (115, 0, 48), (60, 20, 50)]:
                ell(c, cx_ + dx, cy_ + dy, r, r * .85); fill(c, (1, 1, 1), .9)
        if tod == 'sore':
            bulb_glow(c, 300, 300, 500, .5); ell(c, 300, 300, 90, 90); fill(c, hx('#FFE07A'))
    # background houses with details
    for i, col, hh in BGH:
        bx = i * 300 + 40
        top_y = 1340 - 660 - hh
        c.rectangle(bx, top_y, 240, hh + 200); fs(c, hx(col) if not night else hx('#1D2550'), 4)
        poly(c, [(bx - 20, top_y), (bx + 260, top_y), (bx + 120, top_y - 90)]); fs(c, hx('#A0522D') if not night else hx('#141A38'), 4)
        for wy in range(2):
            for wx in range(2):
                rrect(c, bx + 30 + wx * 110, top_y + 30 + wy * 90, 70, 56, 4); fs(c, hx('#FFE9A6') if night and (i + wx + wy) % 3 == 0 else hx('#2E4A66'), 3)
    # mosque dome far
    ell(c, 3300, 560, 120, 110); fs(c, hx('#2E7D32') if not night else hx('#123018'), 5)
    c.rectangle(3180, 560, 240, 120); fs(c, hx('#F3E5C8') if not night else hx('#2A2F48'), 5)
    c.rectangle(3440, 300, 30, 380); fs(c, hx('#F3E5C8') if not night else hx('#2A2F48'), 4)
    # left house (detailed small)
    c.rectangle(-560, 760, 1140, 580); fs(c, hx('#7EC8E3') if not night else hx('#2C3E66'), 6)
    genteng(c, -600, 620, 520, 770, 30)
    for k in range(3):
        x0 = -460 + k * 330
        c.rectangle(x0 - 10, 880 - 10, 220, 200); fs(c, hx('#8A5A30'), 4)
        c.rectangle(x0, 880, 200, 180); fill(c, hx('#FFE9A6') if night and st.get('left_lit') else hx('#2E4A66'))
        for b in range(1, 8):
            c.move_to(x0 + b * 25, 880); c.line_to(x0 + b * 25, 1060); c.set_source_rgb(*hx('#2B2B30')); c.set_line_width(3); c.stroke()
    # trees
    tree(c, 3000, 1340, 1.1, t, night)
    tree(c, -700, 1340, 1.2, t, night)
    # sidewalk pavers
    c.rectangle(-3000, 1340, 9000, 90); fs(c, hx('#C9C3B6'), 5)
    for r in range(3):
        for k in range(-60, 200):
            xx = k * 46 + (r % 2) * 23
            rrect(c, xx, 1344 + r * 28, 44, 26, 4); c.set_source_rgba(0, 0, 0, .12); c.set_line_width(2); c.stroke()
    # gutter (selokan) with grates
    c.rectangle(-3000, 1430, 9000, 30); fill(c, hx('#5A5F66'))
    for k in range(-30, 90):
        xx = k * 120
        rrect(c, xx, 1432, 90, 26, 3); fs(c, hx('#7D848C'), 2)
        for j in range(6):
            c.move_to(xx + 8 + j * 14, 1434); c.line_to(xx + 8 + j * 14, 1456); c.set_source_rgba(0, 0, 0, .5); c.set_line_width(3); c.stroke()
    # road
    c.rectangle(-3000, 1460, 9000, 300); fill(c, hx('#55585E'))
    for k in range(-20, 60):
        c.rectangle(k * 240, 1600, 130, 14); fill(c, hx('#F2F2F2'), .85)
    for (px, py, pw) in ((300, 1520, 160), (1900, 1690, 220), (2900, 1540, 140)):
        rrect(c, px, py, pw, 40, 12); fill(c, hx('#4A4D52'))
    ell(c, 1300, 1700, 50, 18); fs(c, hx('#6F7276'), 3)    # manhole
    for k in range(3):
        c.move_to(1260, 1694 + k * 6); c.line_to(1340, 1694 + k * 6); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(2); c.stroke()
    for (cx_, cy_) in ((700, 1560), (2300, 1660)):
        c.move_to(cx_, cy_); c.line_to(cx_ + 30, cy_ + 10); c.line_to(cx_ + 45, cy_ + 4); c.line_to(cx_ + 80, cy_ + 16)
        c.set_source_rgba(0, 0, 0, .35); c.set_line_width(2); c.stroke()
    c.rectangle(-3000, 1760, 9000, 3000); fill(c, hx('#6DBF5B') if not night else hx('#244A2A'))
    for i in range(-20, 80):
        ell(c, i * 140 + 40, 1800 + (i * 31 % 50), 50, 22); fill(c, hx('#4FA343') if not night else hx('#1C3A20'))
    # poles + wires
    tiang_listrik(c, 560 if False else 540, t, night)
    tiang_listrik(c, 2780, t, night)
    wires(c, -1500, 540, [242, 262, 282], t); wires(c, 540, 2780, [242, 262, 282], t); wires(c, 2780, 4500, [242, 262, 282], t)
    if not night:
        bird(c, 1500, 320 + 3 * math.sin(t * 2), t, 1.0); bird(c, 1560, 322, t + 1, .9)
    toko(c, t, st.get('toko', 'normal'), night, st.get('shutter', 0))
    rumah_julit(c, t, st)
    for ch in st.get('people', []):
        person(c, ch['x'], ch['y'], ch['who'], ch, s=ch.get('s', 1.0), t=t, flip=ch.get('flip', False))
    for f in st.get('pre_car', []): f(c)
    car = st.get('car')
    if car: draw_car(c, t, car)
    for ch in st.get('people_front', []):
        person(c, ch['x'], ch['y'], ch['who'], ch, s=ch.get('s', 1.0), t=t, flip=ch.get('flip', False))
    for f in st.get('fx', []): f(c)
    if night:
        c.save(); c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        c.rectangle(-3000, -3000, 9000, 9000); c.rectangle(680, 730, 980, 610)
        c.set_source_rgba(.03, .05, .18, .45); c.fill(); c.restore()
        bulb_glow(c, 1170, 760, 480, .4)

def paket(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.move_to(-50, -110); c.line_to(50, -110); c.line_to(56, 0); c.line_to(-56, 0); c.close_path(); fs(c, hx('#EAF6FB'), 4, .55)
    rrect(c, -46, -60, 50, 58, 5); fs(c, (1, 1, 1), 3)          # beras 5kg
    c.rectangle(-42, -40, 42, 14); fill(c, hx('#2E6BD6'))
    rrect(c, 10, -88, 26, 86, 7); fs(c, hx('#F4C430'), 3)        # minyak
    c.rectangle(12, -60, 22, 20); fill(c, hx('#E5473B'))
    rrect(c, -40, -100, 40, 34, 4); fs(c, (1, 1, 1), 3)          # gula
    c.rectangle(-36, -90, 32, 8); fill(c, hx('#2EAD6B'))
    rrect(c, 2, -104, 36, 16, 3); fs(c, hx('#E5473B'), 2)        # mie
    for k in (-1, 1):
        c.move_to(k * 30, -110); c.curve_to(k * 30, -150, k * 6, -150, k * 6, -110); c.set_source_rgba(.6, .7, .75, .9); c.set_line_width(4); c.stroke()
    c.move_to(-46, -104); c.line_to(-40, -10); c.set_source_rgba(1, 1, 1, .7); c.set_line_width(5); c.stroke()
    c.restore()

def kardus(c, x, y, w=120, h=80, label="PAKET SEMBAKO"):
    c.rectangle(x, y - h, w, h); fs(c, hx('#C98B4A'), 4)
    c.rectangle(x, y - h * .55, w, 10); fill(c, hx('#E8C27A'))
    text(c, label, x + w / 2, y - h * .25, 11, hx('#5A3A1E'))

def draw_car(c, t, car):
    x, y = car['x'], car['y']
    c.save(); c.translate(x + 690, y); c.rotate(car.get('pitch', 0)); c.translate(-(x + 690), -y)
    if car.get('load'):
        for r in range(3):
            for k in range(4):
                kardus(c, x + 30 + k * 125 + (r % 2) * 20, y - 250 - r * 80, 118, 80)
        c.move_to(x + 30, y - 490); c.line_to(x + 540, y - 260); c.move_to(x + 540, y - 490); c.line_to(x + 30, y - 260)
        c.set_source_rgb(*hx('#E5473B')); c.set_line_width(5); c.stroke()
    lib.gran_max(c, x, y, t, car.get('ang', 0), car.get('driver', False), 0, cargo=False, driver_po=car.get('dpo'))
    c.restore()
    if car.get('smoke'):
        for k in range(6):
            ph = (t * 2.5 + k / 6) % 1
            ell(c, x - 40 - ph * 260, y - 90 - ph * 50, 18 + ph * 40, 18 + ph * 40); fill(c, (.85, .85, .85), .55 * (1 - ph))

# ------------------------------------------------------------ GUDANG (interior)
def gudang(c, t, st):
    night = st.get('night', False)
    c.rectangle(-1000, -1000, 3080, 2300); fill(c, hx('#D9CDB5') if not night else hx('#3E3A44'))
    for k in range(18):   # wall stains
        ell(c, (k * 211) % 1400 - 200, (k * 137) % 900 + 200, 40 + k % 3 * 20, 20 + k % 2 * 14); fill(c, (0, 0, 0), .05)
    c.rectangle(-1000, 1300, 3080, 1200); fill(c, hx('#9A9286') if not night else hx('#2E2B33'))
    for k in range(-6, 30):
        c.move_to(k * 90, 1300); c.line_to(k * 90 - 200, 2500); c.set_source_rgba(0, 0, 0, .12); c.set_line_width(3); c.stroke()
    for k in range(6):
        c.move_to(-1000, 1300 + k * 70 + k * k * 6); c.line_to(2080, 1300 + k * 70 + k * k * 6); c.stroke()
    # barred window
    c.rectangle(80, 320, 260, 220); fs(c, hx('#8FC6E8') if not night else hx('#0D1640'), 6)
    for k in range(1, 6):
        c.move_to(80 + k * 43, 320); c.line_to(80 + k * 43, 540); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    if night and st.get('shadow'):
        a = st['shadow']
        c.save(); c.rectangle(80, 320, 260, 220); c.clip()
        ell(c, 230, 470, 60, 70); fill(c, (0, 0, 0), a)
        poly(c, [(150, 420), (310, 420), (270, 380), (190, 380)]); fill(c, (0, 0, 0), a)
        ell(c, 230, 600, 110, 90); fill(c, (0, 0, 0), a)
        c.restore()
    # calendar
    rrect(c, 420, 300, 170, 220, 6); fs(c, (1, 1, 1), 4)
    c.rectangle(420, 300, 170, 50); fill(c, hx('#D8312B'))
    text(c, "NOVEMBER", 505, 325, 20, (1, 1, 1))
    for r in range(5):
        for k in range(7):
            col = hx('#D8312B') if k == 0 else OUT
            text(c, str(r * 7 + k + 1) if r * 7 + k + 1 <= 30 else "", 438 + k * 22, 370 + r * 30, 13, col, font="Inter")
    # clock
    ell(c, 720, 380, 70, 70); fs(c, (1, 1, 1), 6)
    line(c, [(720, 380), (720 + 40 * math.sin(t * .2), 380 - 40 * math.cos(t * .2))], 6, OUT, False)
    line(c, [(720, 380), (720 + 55 * math.sin(t * 2), 380 - 55 * math.cos(t * 2))], 4, hx('#D8312B'), False)
    # wall fan
    c.save(); c.translate(930, 420)
    rrect(c, -14, 0, 28, 80, 6); fs(c, hx('#9AA1A9'), 3)
    ell(c, 0, 0, 86, 86); c.set_source_rgba(0, 0, 0, .7); c.set_line_width(3); c.stroke()
    for k in range(3):
        a = t * 18 + k * 2.094
        c.save(); c.rotate(a); ell(c, 44, 0, 40, 18); fs(c, hx('#7CC4F5'), 3, .85); c.restore()
    ell(c, 0, 0, 14, 14); fs(c, hx('#2E86DE'), 3)
    for k in range(10):
        a = k * math.pi / 5
        c.move_to(0, 0); c.line_to(86 * math.cos(a), 86 * math.sin(a)); c.set_source_rgba(0, 0, 0, .25); c.set_line_width(1.5); c.stroke()
    c.restore()
    # TL lamp
    rrect(c, 300, 200, 420, 22, 10); fs(c, (1, 1, 1), 4)
    bulb_glow(c, 510, 211, 700 if night else 400, .45 if night else .25)
    # stock: sacks + boxes on right
    for r in range(4):
        for k in range(3):
            sack(c, 1080 + k * 120 + (r % 2) * 50, 1290 - r * 70, 118, 74)
    for r in range(3):
        for k in range(2):
            lbl = ["MINYAK GORENG", "GULA PASIR", "MIE INSTAN"][(r + k) % 3]
            kardus(c, -60 + k * 150, 1290 - r * 95, 140, 92, lbl)

def packing_table(c, t, st):
    c.rectangle(200, 1180, 760, 28); fs(c, hx('#A8763E'), 5)
    for lx in (220, 930):
        c.rectangle(lx, 1208, 20, 140); fs(c, hx('#8A5E30'), 4)
    # items on table
    for k in range(4):
        rrect(c, 250 + k * 60, 1130, 50, 50, 5); fs(c, (1, 1, 1), 3); c.rectangle(254 + k * 60, 1150, 42, 12); fill(c, hx('#2E6BD6'))
    for k in range(5):
        rrect(c, 520 + k * 30, 1100, 24, 80, 6); fs(c, hx('#F4C430'), 3)
    for k in range(3):
        rrect(c, 700 + k * 44, 1150, 40, 30, 3); fs(c, hx('#E5473B'), 2)
    ell(c, 880, 1160, 22, 22); fs(c, hx('#8D6E63'), 3); ell(c, 880, 1160, 9, 9); fill(c, hx('#5D4037'))   # tape

# ------------------------------------------------------------ PHONE UI
def phone(c, x, y, s, msgs, t, header="Nomor Tidak Dikenal", group=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -230, -440, 460, 880, 54); fs(c, hx('#1E1E22'), 8)
    rrect(c, -210, -400, 420, 800, 28); fill(c, hx('#ECE5DD'))
    rrect(c, -210, -400, 420, 110, 28); fill(c, hx('#2F7D62')); c.rectangle(-210, -340, 420, 50); fill(c, hx('#2F7D62'))
    ell(c, -160, -345, 30, 30); fs(c, hx('#C9CED4'), 3)
    if group:
        for k in range(3): ell(c, -170 + k * 10, -350 + k * 6, 10, 10); fill(c, hx(PRODUCT_COLS[k]))
    else:
        ell(c, -160, -355, 12, 12); fill(c, hx('#7D848C')); ell(c, -160, -330, 20, 12); fill(c, hx('#7D848C'))
    text(c, header, -115, -358, 26, (1, 1, 1), align='l')
    text(c, "online" if not group else "Bu Julit, Bu Sri, Bu Ani, +24", -115, -322, 17, (.85, 1, .9), font="Inter", align='l')
    yy = -260
    for (ta, who, msg, me) in msgs:
        k = pop(t, ta, .25)
        if k <= .03: continue
        c.save()
        c.select_font_face("Inter"); c.set_font_size(22)
        lines_ = msg.split("\n")
        wmax = max(c.text_extents(l_).width for l_ in lines_) + 40
        if who: wmax = max(wmax, c.text_extents(who).width + 40)
        bh = 34 * len(lines_) + (30 if who else 0) + 16
        bx = 200 - wmax if me else -195
        c.translate(bx + wmax / 2, yy + bh / 2); c.scale(k, k); c.translate(-(bx + wmax / 2), -(yy + bh / 2))
        rrect(c, bx, yy, wmax, bh, 16); fs(c, hx('#DCF8C6') if me else (1, 1, 1), 2)
        ty = yy + 24
        if who:
            text(c, who, bx + 20, ty, 18, hx('#D8312B') if 'Julit' in who else hx('#2E6BD6'), font="Inter Black", align='l'); ty += 30
        for l_ in lines_:
            text(c, l_, bx + 20, ty, 22, OUT, font="Inter", align='l'); ty += 34
        c.restore()
        yy += bh + 16
    # typing dots
    if st_typing(t, msgs):
        for k in range(3):
            ell(c, -170 + k * 22, yy + 20 - 6 * abs(math.sin(t * 8 + k)), 7, 7); fill(c, hx('#7D848C'))
    rrect(c, -200, 330, 340, 56, 28); fill(c, (1, 1, 1))
    ell(c, 172, 358, 28, 28); fill(c, hx('#2F7D62'))
    c.restore()

def st_typing(t, msgs):
    nxt = [m[0] for m in msgs if m[0] > t]
    return nxt and nxt[0] - t < .8

# ------------------------------------------------------------ FX
def focus_lines(c, t, t0, t1, cx=W / 2, cy=H * .42):
    if not (t0 <= t < t1): return
    a = min(1, (t - t0) / .08) * min(1, (t1 - t) / .2)
    rnd = random.Random(int(t * 30))
    for i in range(70):
        ang = rnd.uniform(0, 2 * math.pi); r0 = rnd.uniform(430, 640); r1 = 1500; w = rnd.uniform(.004, .014)
        poly(c, [(cx + r0 * math.cos(ang), cy + r0 * math.sin(ang)), (cx + r1 * math.cos(ang - w), cy + r1 * math.sin(ang - w)), (cx + r1 * math.cos(ang + w), cy + r1 * math.sin(ang + w))])
        c.set_source_rgba(.05, .05, .08, .55 * a); c.fill()

def pill(c, s, t, t0, y=280, col=hx('#FFE14D'), rot=-.04, fg=OUT, size=74):
    k = pop(t, t0, .35)
    if k <= 0.03: return
    c.save(); c.translate(W / 2, y); c.scale(k, k); c.rotate(rot)
    c.select_font_face("Inter Black"); c.set_font_size(size)
    w = c.text_extents(s).width + 90
    rrect(c, -w / 2 + 6, -56, w, 124, 30); fill(c, (0, 0, 0), .25)
    rrect(c, -w / 2, -62, w, 124, 30); fs(c, col, 9)
    text(c, s, 0, 0, size, fg)
    c.restore()

def rain_cloud(c, t, x, y, k=1.0):
    if k <= .02: return
    c.save(); c.translate(x, y); c.scale(k, k)
    for i in range(10):
        ph = (t * 1.8 + i * .13) % 1
        lx = -60 + i * 14
        c.move_to(lx, 20 + ph * 160); c.line_to(lx - 6, 40 + ph * 160); c.set_source_rgba(.45, .7, 1, .9 * (1 - ph)); c.set_line_width(4); c.stroke()
    for dx, dy, r in ((-50, 0, 40), (0, -22, 50), (50, 0, 40), (0, 12, 42)):
        ell(c, dx, dy, r, r * .8); fs(c, hx('#8C96A6'), 5)
    c.restore()

def steam(c, t, x, y):
    for k in range(3):
        ph = (t * 1.5 + k / 3) % 1
        ell(c, x + (k - 1) * 30, y - ph * 120, 16 + ph * 20, 14 + ph * 16); fill(c, (1, 1, 1), .8 * (1 - ph))

# ------------------------------------------------------------ SCENES
def S_street(fn_state):
    def d(c, t, t0): street(c, t, fn_state(t))
    return d

def st_s1(t):   # Lah baru beli Gran Max?
    m = talk(t, JULIT_SPEAK)
    return {'tod': 'morning', 'toko': 'kosong', 'car': {'x': 700, 'y': 1600},
            'julit_win': None, 'curtain': .3,
            'people': [{'who': 'julit', 'x': 1980, 'y': 1420, 'flip': True, 'aF': (110, -20), 'aB': (20, 0), 'mouth': m, 'eyes': 'squint', 'brows': 'up', 'look': (6, 0)}]}

def st_s2(t):
    return {'tod': 'morning', 'toko': 'kosong', 'car': {'x': 700, 'y': 1600}}

def st_s4(t):   # nyinyir
    m = talk(t, JULIT_SPEAK)
    close = t >= 9.4
    return {'tod': 'morning', 'toko': 'kosong', 'car': {'x': 700, 'y': 1600},
            'people': [{'who': 'friend', 'x': 2330, 'y': 1420, 'flip': True, 'aF': (60, 80), 'expr': 'o' if t > 11.3 else 'smile', 'eyes': 'squint', 'tilt': 5 * math.sin(t * 4)},
                       {'who': 'julit', 'x': 2080, 'y': 1420, 'flip': True, 'aF': (120 + 30 * math.sin(t * 7), -30) if close else (150, -120),
                        'aB': (20, 10), 'mouth': m, 'eyes': 'squint', 'brows': 'smug', 'expr': 'pout' if not close else 'smile', 'look': (6, 0)}]}

def st_s5(t):   # mulutnya gak ada rem
    return {'tod': 'morning', 'toko': 'kosong', 'car': {'x': 700, 'y': 1600},
            'people': [{'who': 'friend', 'x': 2330, 'y': 1420, 'flip': True, 'aF': (170, -160), 'aB': (170, -160), 'eyes': 'closed', 'expr': 'frown'},
                       {'who': 'julit', 'x': 2080, 'y': 1420, 'flip': True, 'aF': (120 + 40 * math.sin(t * 14), -30), 'aB': (20, 10),
                        'mouth': .4 + .5 * abs(math.sin(t * 22)), 'eyes': 'squint', 'brows': 'smug', 'look': (6, 0)}],
            'fx': [lambda c: rem_blong(c, t)]}

def rem_blong(c, t):
    k = pop(t, 14.7, .3)
    if k <= .03: return
    c.save(); c.translate(1880, 950); c.scale(k, k); c.rotate(.08 * math.sin(t * 6))
    line(c, [(0, 60), (0, 330)], 14, hx('#9AA1A9'))
    poly(c, [(0, -130), (140, 110), (-140, 110)]); fs(c, hx('#D7141A'), 8)
    poly(c, [(0, -86), (100, 84), (-100, 84)]); fs(c, (1, 1, 1), 3)
    text(c, "REM", 0, 20, 40, OUT); text(c, "BLONG!", 0, 62, 30, hx('#D7141A'))
    c.restore()

def st_s6(t):
    s = st_s5(16.5); s['fx'] = []
    s['people'][1]['mouth'] = .7
    return s

def sc_group_chat(c, t, t0):
    street(c, t, {'tod': 'morning', 'toko': 'kosong', 'car': {'x': 700, 'y': 1600}})
    c.set_source_rgba(1, 1, 1, .35); c.paint()
    msgs = [(4.6, "Bu Julit", "Ibu2!! Toko Pak Rahmat\nKOSONG MELOMPONG!", False),
            (5.5, "Bu Sri", "Masa sih bu??", False),
            (6.2, "Bu Ani", "Wah, bangkrut tuh...", False),
            (6.9, "Bu Julit", "Gara2 beli mobil kali", False)]
    phone(c, cam_center(t)[0], cam_center(t)[1] - 20, 1.05, msgs, t, "GRUP IBU-IBU RT 05", group=True)

def cam_center(t):
    return (W / 2 + 0, H / 2 - 120)

def sc_gudang_pack(c, t, t0):
    gudang(c, t, {})
    packing_table(c, t, {})
    n = int(clamp((t - 21.0) / 3.4) * 200)
    # paket stacks right
    cnt = min(18, int(clamp((t - 20.6) / 4.6) * 18))
    for i in range(cnt):
        paket(c, 1050 + (i % 6) * 110 - (i // 6) * 30, 1500 + (i // 6) * 110, 1.0)
    # rahmat & istri packing
    a = 120 + 40 * math.sin(t * 9)
    def hold_bag(c, hnd):
        paket(c, hnd[0] + 30, hnd[1] + 60, .7)
    person(c, 430, 1460, 'rahmat', {'aF': (a, -40), 'aB': (110, -30), 'expr': 'grin', 'look': (4, 6), 'hold': hold_bag if math.sin(t * 9) > 0 else None}, s=1.05, t=t)
    person(c, 760, 1460, 'burahmat', {'flip': True, 'aF': (120 + 40 * math.sin(t * 9 + 2), -40), 'aB': (110, -30), 'expr': 'grin', 'look': (-4, 6)}, s=1.0, t=t)
    # counter board
    rrect(c, 760, 600, 280, 150, 14); fs(c, hx('#2F3A32'), 6)
    text(c, "PAKET", 900, 640, 30, hx('#FFE14D'))
    text(c, f"{n}/200", 900, 700, 60, (1, 1, 1))

def sc_dulu_sekarang(c, t, t0):
    # top: dulu (sepia)
    c.save(); c.rectangle(0, 0, W, H / 2); c.clip()
    c.save(); c.translate(0, -500); c.scale(1, 1)
    c.translate(W / 2, H / 4 + 500); c.scale(.62, .62); c.translate(-1150, -1100)
    street(c, t, {'tod': 'day', 'toko': 'normal'})
    person(c, 1220, 1420, 'rahmat', {'aF': (100, -20), 'expr': 'smile'}, t=t)
    person(c, 1500, 1420, 'b2', {'flip': True, 'aF': (90, -10), 'expr': 'smile'}, t=t)
    def bag1(c):
        rrect(c, 1320, 1170, 70, 60, 6); fs(c, (1, 1, 1), 3, .8)
        text(c, "1 KG", 1355, 1200, 18, OUT)
    bag1(c)
    c.restore()
    c.set_source_rgba(.45, .32, .15, .45); c.paint()
    c.restore()
    # bottom: sekarang
    c.save(); c.rectangle(0, H / 2, W, H / 2); c.clip()
    c.translate(W / 2, H * .75); c.scale(.62, .62); c.translate(-1150, -1100)
    street(c, t, {'tod': 'day', 'toko': 'kosong', 'car': {'x': -300, 'y': 1600, 'load': True}})
    def scroll(c, hnd):
        c.save(); c.translate(hnd[0] + 10, hnd[1])
        k = clamp((t - 28.6) / .8)
        rrect(c, -20, -10, 80, 60 + 300 * k, 6); fs(c, (1, 1, 1), 4)
        for j in range(int(6 * k) + 1):
            c.move_to(-10, 10 + j * 45); c.line_to(50, 10 + j * 45); c.set_source_rgba(0, 0, 0, .4); c.set_line_width(4); c.stroke()
        c.restore()
    person(c, 1500, 1440, 'bos', {'flip': True, 'aF': (100, -10), 'expr': 'grin', 'hold': scroll}, s=1.1, t=t)
    person(c, 1220, 1440, 'rahmat', {'aF': (170, -40), 'aB': (170, -40), 'expr': 'grin', 'eyes': 'wide'}, t=t)
    k = pop(t, 29.3, .3)
    if k > .03:
        c.save(); c.translate(1350, 900); c.scale(k, k); c.rotate(-.1)
        rrect(c, -230, -70, 460, 140, 20); fs(c, hx('#D8312B'), 8)
        text(c, "BORONG SATU TOKO!", 0, 0, 44, (1, 1, 1), OUT, 6)
        c.restore()
    c.restore()
    c.rectangle(0, H / 2 - 8, W, 16); fill(c, (1, 1, 1))
    for (lbl, y, col, ta) in (("DULU", 110, hx('#D9B98A'), 25.6), ("SEKARANG", H / 2 + 110, hx('#FFE14D'), 27.9)):
        k = pop(t, ta, .3)
        if k > .03:
            c.save(); c.translate(W / 2, y); c.scale(k, k)
            c.select_font_face("Inter Black"); c.set_font_size(62)
            w = c.text_extents(lbl).width + 70
            rrect(c, -w / 2, -48, w, 96, 24); fs(c, col, 8); text(c, lbl, 0, 0, 62, OUT)
            c.restore()

def st_s9(t):   # Gran Max loaded passes julit
    if t < 33.3:
        k = eout((t - 30.4) / 2.9); x = lerp(-1300, 1500, k); moving = True
    else:
        x = 1500; moving = False
    shock = t >= 34.7
    return {'tod': 'day', 'toko': 'kosong',
            'car': {'x': x, 'y': 1620, 'load': True, 'driver': True, 'smoke': moving, 'ang': (x + 1300) / 62, 'dpo': {'aF': (110, 20), 'expr': 'grin'}},
            'people': [{'who': 'friend', 'x': 2330, 'y': 1420, 'flip': True, 'aF': (170, -150) if shock else (60, 80), 'expr': 'o', 'eyes': 'wide' if shock else 'open'},
                       {'who': 'julit', 'x': 2080, 'y': 1420, 'flip': True, 'aF': (170, -160) if shock else (20, 10), 'aB': (20, 10),
                        'mouth': .9 if shock else 0, 'expr': 'o', 'eyes': 'wide' if shock else 'squint', 'look': (-6, 0)}],
            'fx': [lambda c: sweat(c, 1990, 1000, 1.1)] if shock else []}

def st_s10(t):   # sore, julit beli beras, habis
    m = talk(t, ISTRI_SPEAK)
    return {'tod': 'sore', 'toko': 'habis',
            'people': [{'who': 'burahmat', 'x': 1150, 'y': 1370, 'aF': (120, -40), 'aB': (20, 0), 'mouth': m, 'expr': 'grin', 'eyes': 'happy' if t > 40.5 else 'open'},
                       {'who': 'julit', 'x': 1100 if t < 39 else 1050, 'y': 1460, 'flip': False, 'aF': (100, -20), 'aB': (20, 0),
                        'expr': 'smile' if t < 40.4 else 'frown', 'eyes': 'squint' if t < 40.4 else 'wide', 'brows': 'smug' if t < 40.4 else 'up', 'look': (6, -4),
                        'step': 1 if t < 39 else 0, 's': 1.05}]}

def st_s11(t):   # julit walks off grumpy, hahaha
    x = lerp(1050, 2200, clamp((t - 43.2) / 1.0))
    return {'tod': 'sore', 'toko': 'habis',
            'people': [{'who': 'burahmat', 'x': 1150, 'y': 1370, 'aF': (170, -100), 'expr': 'grin', 'eyes': 'happy', 'mouth': .5 * abs(math.sin(t * 14))},
                       {'who': 'rahmat', 'x': 1320, 'y': 1370, 'flip': True, 'aF': (170, -110), 'expr': 'grin', 'eyes': 'happy', 'mouth': .5 * abs(math.sin(t * 14 + 1))},
                       {'who': 'julit', 'x': x, 'y': 1460, 'flip': False, 'step': 1, 'aF': (10, 0), 'expr': 'frown', 'brows': 'angry', 'eyes': 'squint'}],
            'fx': [lambda c: steam(c, t, x + 10, 1040), lambda c: rain_cloud(c, t, x, 900, 1.0)]}

def sc_night_order(c, t, t0):
    gudang(c, t, {'night': True, 'shadow': clamp((t - 47.4) / .8) * .85 if t > 47.4 else 0})
    for r in range(2):
        for k in range(3):
            sack(c, 250 + k * 120 + (r % 2) * 40, 1480 - r * 70, 118, 74)
    def hp(c, hnd):
        rrect(c, hnd[0] - 14, hnd[1] - 50, 30, 54, 6); fs(c, hx('#1E1E22'), 3)
        rrect(c, hnd[0] - 10, hnd[1] - 46, 22, 44, 4); fill(c, hx('#BFE4F2'))
        bulb_glow(c, hnd[0], hnd[1] - 24, 120, .5)
    person(c, 330, 1440, 'rahmat', {'sit': True, 'aF': (150, -100), 'aB': (40, 30), 'expr': 'o' if t > 46.3 else 'smile', 'eyes': 'wide' if t > 46.3 else 'open',
                                    'look': (6, -2), 'hold': hp, 'brows': 'up' if t > 47.6 else 'normal'}, s=1.05, t=t)
    if t > 48.6: sweat(c, 250, 1000, 1.0)
    msgs = [(44.9, "", "Pak, saya mau pesan\n500 PAKET sembako.", False),
            (47.7, "", "Syaratnya: barang\ndikirim dulu ya...", False),
            (49.9, "", "Bayarnya belakangan.", False)]
    if t > 44.6:
        k = eout((t - 44.6) / .4)
        phone(c, 760, lerp(2400, 620, k), .66, msgs, t, "Nomor Tidak Dikenal")

def sc_cliff(c, t, t0):
    g = cairo.RadialGradient(540, 900, 50, 540, 900, 1300)
    g.add_color_stop_rgb(0, *hx('#5A1020')); g.add_color_stop_rgb(1, *hx('#12030A'))
    c.set_source(g); c.rectangle(-1000, -1000, 3080, 4000); c.fill()
    for k in range(16):
        a = k * math.pi / 8 + t * .3
        c.move_to(540, 900); c.line_to(540 + 1800 * math.cos(a), 900 + 1800 * math.sin(a)); c.line_to(540 + 1800 * math.cos(a + .1), 900 + 1800 * math.sin(a + .1)); c.close_path()
        c.set_source_rgba(1, .2, .2, .08); c.fill()
    person(c, 540, 1600, 'rahmat', {'aF': (150, -150), 'aB': (150, -150), 'eyes': 'wide', 'brows': 'up', 'expr': 'o', 'look': (0, -2), 'tilt': 3 * math.sin(t * 20)}, s=1.6, t=t)
    for k in range(2): sweat(c, 300 + k * 480, 820 + ((t * 120 + k * 50) % 160), 1.2)
    for k in range(6):
        a = t * 1.5 + k * 1.05
        x = 540 + 420 * math.cos(a); y = 560 + 200 * math.sin(a)
        text(c, "?", x, y, 90 + 20 * math.sin(t * 4 + k), hx('#FFE14D'), OUT, 10)
    if t > 55.3:
        k = pop(t, 55.3, .4)
        c.set_source_rgba(0, 0, 0, .55 * clamp((t - 55.3) / .3)); c.paint()
        c.save(); c.translate(W / 2, 900); c.scale(k, k); c.rotate(-.05)
        rrect(c, -380, -100, 760, 200, 24); fs(c, hx('#FFE14D'), 10)
        text(c, "BERSAMBUNG...", 0, 0, 84, OUT)
        c.restore()
    for tb in (51.3, 53.3):
        d = t - tb
        if 0 <= d < .18:
            c.set_source_rgba(1, 1, 1, .7 * (1 - d / .18)); c.paint()

def sc_freeze(c, t, t0):
    street(c, 16.5, st_s6(16.5))
    c.set_source_rgba(.5, .5, .55, .35); c.paint()
    rnd = random.Random(int(t * 20))
    for k in range(8):
        y = rnd.uniform(0, 2000)
        c.rectangle(-500, y, 3000, rnd.uniform(2, 6)); fill(c, (1, 1, 1), .4)

SCENES = [
 (0.0, 2.3, S_street(st_s1), [(0, 1500, 980, .62), (2.3, 1700, 1000, .72)]),
 (2.3, 4.45, S_street(st_s2), [(2.3, 1170, 990, 1.25), (4.45, 1000, 1000, 1.4)]),
 (4.45, 7.6, sc_group_chat, [(4.45, 2000, 1000, 1.0), (7.6, 2000, 1000, 1.0)]),
 (7.6, 9.4, S_street(st_s4), [(7.6, 2150, 1050, 1.05), (9.4, 2180, 1060, 1.15)]),
 (9.4, 13.75, S_street(st_s4), [(9.4, 2110, 1020, 1.75), (13.75, 2100, 1010, 1.95)]),
 (13.75, 17.2, S_street(st_s5), [(13.75, 2050, 1050, 1.2), (17.2, 2020, 1040, 1.3)]),
 (17.2, 20.45, sc_freeze, [(17.2, 2050, 1050, 1.3), (20.45, 2050, 1050, 1.35)]),
 (20.45, 25.5, sc_gudang_pack, [(20.45, 540, 980, .95), (23.2, 600, 1100, 1.05), (25.5, 640, 1150, 1.0)]),
 (25.5, 30.35, sc_dulu_sekarang, None),
 (30.35, 37.1, S_street(st_s9), None),
 (37.1, 43.15, S_street(st_s10), [(37.1, 1150, 1050, .9), (39.9, 1120, 1080, 1.2), (43.15, 1100, 1080, 1.3)]),
 (43.15, 44.2, S_street(st_s11), [(43.15, 1500, 1050, .85), (44.2, 1650, 1050, .9)]),
 (44.2, 51.15, sc_night_order, [(44.2, 600, 1050, 1.1), (44.6, 560, 1000, .95), (51.15, 560, 1000, 1.0)]),
 (51.15, DUR + 1, sc_cliff, [(51.15, 540, 1000, .9), (55.3, 540, 980, 1.15), (DUR, 540, 980, 1.2)]),
]

def cam_for(t, keys):
    if keys is None:
        if 30.35 <= t < 37.1:
            if t < 33.3:
                k = eout((t - 30.4) / 2.9); x = lerp(-1300, 1500, k) + 430
                return (x, 1180, .85)
            if t < 34.6: return (1930, 1180, .85)
            return (lerp(1930, 2100, ease((t - 34.6) / .6)), lerp(1180, 1050, ease((t - 34.6) / .6)), lerp(.85, 1.6, ease((t - 34.6) / .6)))
        return (W / 2, H / 2, 1.0)
    return lib.cam_keys(keys, t)

def captions(c, t, base_y=1480):
    for ci, ch in enumerate(CHUNKS):
        a = ch[0][1] - 0.05
        b = CHUNKS[ci + 1][0][1] - 0.05 if ci + 1 < len(CHUNKS) else DUR
        b = min(b, ch[-1][2] + 0.6)
        if not (a <= t < b): continue
        k = eout((t - a) / .16)
        size = 104
        c.select_font_face("Inter Black"); c.set_font_size(size)
        strs = [w[0].upper() for w in ch]
        sp = c.text_extents(" ").x_advance
        tot = sum(c.text_extents(s).x_advance for s in strs) + sp * (len(strs) - 1)
        if tot > 980:
            size *= 980 / tot; c.set_font_size(size); sp = c.text_extents(" ").x_advance
            tot = sum(c.text_extents(s).x_advance for s in strs) + sp * (len(strs) - 1)
        c.save(); c.translate(W / 2, base_y + 40 * (1 - k)); c.rotate(-0.02)
        x = -tot / 2
        cur = [w for w in ch if w[1] - 0.03 <= t]
        for w, s in zip(ch, strs):
            c.set_font_size(size); adv = c.text_extents(s).x_advance
            active = cur and w is cur[-1]
            bump = 1 + .14 * max(0, 1 - (t - w[1]) / .15) if active and t >= w[1] else 1
            c.save(); c.translate(x + adv / 2, 0); c.scale(bump, bump)
            text(c, s, 4, 8, size, (0, 0, 0), alpha=.35 * k)
            text(c, s, 0, 0, size, hx('#FFE14D') if active else (1, 1, 1), OUT, size * .2, alpha=k)
            c.restore()
            x += adv + sp
        c.restore()

CUTS = [s[0] for s in SCENES[1:]]

def render(fi):
    t = fi / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    sc = next(s for s in SCENES if s[0] <= t < s[1])
    t0, t1, fn, keys = sc
    if fn is sc_dulu_sekarang:
        fn(c, t, t0)
    else:
        cx, cy, z = cam_for(t, keys)
        amp = 0
        for s in (13.75, 17.2, 34.7, 51.3, 53.3):
            if 0 <= t - s < .3: amp = max(amp, 16 * (1 - (t - s) / .3))
        c.save(); c.translate(W / 2 + amp * math.sin(t * 97), H / 2 + amp * math.cos(t * 73)); c.scale(z, z); c.translate(-cx, -cy)
        if fn is sc_group_chat:
            c.restore(); c.save()
            c.translate(W / 2, H / 2); c.scale(1.0, 1.0); c.translate(-2000, -1000)
            street(c, t, {'tod': 'morning', 'toko': 'kosong', 'car': {'x': 700, 'y': 1600}})
            c.restore(); c.save()
            c.set_source_rgba(1, 1, 1, .4); c.paint()
            msgs = [(4.6, "Bu Julit", "Ibu-ibu!! Toko Pak Rahmat\nKOSONG MELOMPONG!", False),
                    (5.5, "Bu Sri", "Masa sih bu??", False),
                    (6.2, "Bu Ani", "Wah, bangkrut tuh...", False),
                    (6.9, "Bu Julit", "Gara-gara beli mobil kali", False)]
            k = eout((t - 4.45) / .35)
            phone(c, W / 2, lerp(2300, 800, k), 1.05, msgs, t, "GRUP IBU-IBU RT 05", group=True)
        else:
            fn(c, t, t0)
        c.restore()
    # overlays
    focus_lines(c, t, 34.7, 35.9, cy=H * .45)
    focus_lines(c, t, 13.75, 14.4, cy=H * .45)
    if 17.2 <= t < 20.45:
        k = pop(t, 17.3, .3)
        if k > .03:
            c.save(); c.translate(W / 2, 560); c.scale(k, k); c.rotate(-.08)
            rrect(c, -360, -90, 720, 180, 20); fs(c, hx('#D8312B'), 10)
            text(c, "TUNGGU DULU!", 0, 0, 84, (1, 1, 1), OUT, 10)
            c.restore()
        for k in range(2):   # rewind marks
            x = 120 + k * 60
            poly(c, [(x + 50, 160), (x, 195), (x + 50, 230)]); fs(c, (1, 1, 1), 4)
        text(c, "PAUSE", 300, 196, 40, (1, 1, 1), OUT, 6, align='l')
    if 20.45 <= t < 25.5: pill(c, "TERNYATA...", t, 20.6, col=hx('#FFE14D'))
    if 37.1 <= t < 39.5: pill(c, "SORENYA...", t, 37.2, col=hx('#FF9F43'))
    if 44.2 <= t < 45.5: pill(c, "MALAMNYA...", t, 44.25, col=hx('#7FB3FF'))
    for s in CUTS:
        d = t - s
        if 0 <= d < 0.1: c.set_source_rgba(1, 1, 1, .3 * (1 - d / .1)); c.paint()
    gr = cairo.RadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * .78)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0); gr.add_color_stop_rgba(1, 0, 0, .04, .3)
    c.set_source(gr); c.paint()
    if t > DUR - .3: c.set_source_rgba(0, 0, 0, clamp((t - (DUR - .3)) / .3)); c.paint()
    captions(c, t)
    surf.flush()
    return bytes(surf.get_data())
