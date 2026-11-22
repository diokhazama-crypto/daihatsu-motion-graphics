"""ASET DIO + PROPERTI PRO PLUS (dulu bagian umum ep4.py). GAMBAR TETAP: jangan ubah bentuk/warna CH['dio'].
Isi: CH['dio'] (Dio Sales Daihatsu, versi A, hd), set_pucat, talk, backk/pose_seq (ancang-ancang + pantulan),
confetti, lightning, watchers, brosur, gloom, tanya, card, name_card, bubble, smoke, ribbon, coin_pop, parked,
street (sudah mendukung depth of field), POS_R/POS_D/YS, rahmat_po/dio_po, SERIUS, rain."""
import math, random
import numpy as np
import cairo
import aset_kampung as E
import aset_pro as P
import aset_mbg as G
import aset_dasar as lib
from aset_dasar import (W, H, OUT, hx, clamp, ease, eout, lerp, pop, fs, fill, rrect, ell, poly, line, text,
                 CH, sweat, spark, exclaim)

lib.SHADE = True

def talk(t, spans):
    for a, b in spans:
        if a <= t <= b:
            e = lib.env(t)
            return clamp((e - 0.12) * 1.4) * (0.6 + 0.4 * abs(math.sin(t * 19)))
    return 0.0

# ------------------------------------------------------------ characters
DIO_SKIN = hx('#F6D9C2'); PALE = hx('#D9E3D3')
CH['dio'] = dict(skin=DIO_SKIN, shirt=hx('#1F2F6B'), pants=hx('#D8CBB4'), hair='dio2', kind='man', eye_style='almond',
                 collar=True, collar_col=hx('#1A285C'), collar_pipe=hx('#F4F1EA'), buttons=True, placket=True, seams=True,
                 pocket=True, pocket_flap=True, cuff=hx('#F4F1EA'), side_panel=True, chest_text="DAIHATSU", lanyard=True,
                 id_name="DIO", foot='sneaker', chino=True, belt=None, hd=True)

def set_pucat(k):
    """k 0..1: kulit Dio memucat (0 = normal)."""
    CH['dio']['skin'] = tuple(lerp(a, b, k) for a, b in zip(DIO_SKIN, PALE))
    return k

def reset_tokoh():
    CH['dio']['skin'] = DIO_SKIN

person = G.person

# ------------------------------------------------------------ PRO: gesture tween (anticipation + overshoot)
PRO = True   # master: selalu gaya PRO PLUS
def backk(t, ts, d=.28):
    if not PRO: return 1.0 if t >= ts else 0.0
    u = (t - ts) / d
    if u < -.45: return 0.0
    if u < 0: return -.09 * math.sin(math.pi * (u + .45) / .45)
    if u < 1: return 1 + 2.70158 * (u - 1) ** 3 + 1.70158 * (u - 1) ** 2
    return 1.0

def pose_seq(t, seq, d=.28):
    cur = None
    for i, (ts, aF, aB) in enumerate(seq):
        if i == 0: cur = [aF, aB]; continue
        if t < ts - .5: break
        k = backk(t, ts, d)
        cur = [tuple(lerp(p, q, k) for p, q in zip(A, B)) for A, B in zip(cur, (aF, aB))]
    return cur

def confetti(c, t, t0, n=110):
    d = t - t0
    if not (0 <= d < 2.4): return
    rnd = random.Random(9)
    cols = [hx(x) for x in ('#E5473B', '#F2C230', '#2E86DE', '#2EAD6B', '#F07AA8', '#FFFFFF')]
    for i in range(n):
        x0 = rnd.uniform(-100, W + 100); vx = rnd.uniform(-160, 160); vy = rnd.uniform(-900, -300); sp = rnd.uniform(4, 11)
        x = x0 + .3 * vx * d + 40 * math.sin(d * 3 + i); y = rnd.uniform(-900, -20) - vy * d * 1.1
        a = clamp((2.4 - d) / .5)
        c.save(); c.translate(x, y); c.rotate(sp * d + i); c.scale(1, abs(math.cos(sp * d * .7 + i)) + .15)
        c.rectangle(-9, -5, 18, 10); fill(c, cols[i % 6], a); c.restore()

def lightning(c, t, at, a=.55):
    d = t - at
    if 0 <= d < .35:
        f = a * (1 - d / .35) * (1 if d < .06 or .12 < d < .18 else .45)
        c.set_source_rgba(.85, .9, 1, f); c.paint()

def watchers(t, x):
    lk = lambda px: (max(-6, min(6, (x + 430 - px) / 120)), -1)
    return [{'who': 'julit', 'x': 380, 'y': 1420, 'aF': (38, -100), 'aB': (38, -100), 'eyes': 'squint', 'brows': 'smug', 'expr': 'pout', 'look': lk(380)},
            {'who': 'friend', 'x': 560, 'y': 1420, 'aF': (60, 80), 'eyes': 'wide', 'expr': 'o', 'look': lk(560)}]

# ------------------------------------------------------------ props
def brosur(c, hnd):
    c.save(); c.translate(hnd[0] + 10, hnd[1] - 40); c.rotate(-.15)
    rrect(c, -40, -55, 80, 110, 6); fs(c, (1, 1, 1), 4)
    c.rectangle(-34, -48, 68, 30); fill(c, hx('#1F2F6B'))
    text(c, "PROMO", 0, -33, 14, (1, 1, 1))
    for k in range(3):
        c.rectangle(-30, -8 + k * 16, 60, 6); fill(c, (0, 0, 0), .25)
    c.restore()

def gloom(c, x, y, s, a):
    """blue 'pucat' lines over the forehead (head centre ~ y-350*s)."""
    if a <= .02: return
    hy = y - 352 * s
    c.save(); ell(c, x + 6 * s, hy, 64 * s, 64 * s); c.clip()
    for k in range(7):
        xx = x + (-40 + k * 14) * s
        c.move_to(xx, hy - 66 * s); c.line_to(xx, hy - (20 + (k % 2) * 8) * s)
        c.set_source_rgba(.25, .35, .85, .55 * a); c.set_line_width(4 * s); c.stroke()
    c.restore()

def tanya(c, x, y, t, t0, s=1.0, n=3):
    k = pop(t, t0, .3)
    if k <= .03: return
    for j in range(n):
        c.save(); c.translate(x + (j - (n - 1) / 2) * 70 * s, y - 20 * abs(math.sin(t * 3 + j)) - (j % 2) * 30 * s); c.scale(k * s, k * s)
        c.rotate(.2 * math.sin(t * 2 + j))
        text(c, "?", 0, 0, 90, hx('#FFE14D'), OUT, 9)
        c.restore()

def card(c, x, y, k, lbl, col, size=60, fg=OUT, rot=-.05, pad=60, sub=None):
    if k <= .03: return
    c.save(); c.translate(x, y); c.scale(k, k); c.rotate(rot)
    c.select_font_face("Inter Black"); c.set_font_size(size)
    w = c.text_extents(lbl).width + pad
    hh = size * 1.7 + (size * .7 if sub else 0)
    rrect(c, -w / 2 + 6, -hh / 2 + 10, w, hh, 24); fill(c, (0, 0, 0), .25)
    rrect(c, -w / 2, -hh / 2, w, hh, 24); fs(c, col, 9)
    if sub:
        text(c, lbl, 0, -size * .35, size, fg); text(c, sub, 0, size * .65, size * .5, fg, font="Inter Black")
    else:
        text(c, lbl, 0, 0, size, fg)
    c.restore()

def name_card(c, x, y, k):
    if k <= .03: return
    c.save(); c.translate(x, y); c.scale(k, k); c.rotate(-.04)
    rrect(c, -200 + 6, -70 + 10, 400, 140, 18); fill(c, (0, 0, 0), .25)
    rrect(c, -200, -70, 400, 140, 18); fs(c, (1, 1, 1), 7)
    c.save(); rrect(c, -200, -70, 400, 140, 18); c.clip(); c.rectangle(-200, -70, 26, 140); fill(c, hx('#1F2F6B')); c.restore()
    text(c, "MAS DIO", 14, -20, 56, hx('#1F2F6B'))
    text(c, "SALES DAIHATSU", 14, 34, 28, hx('#D7141A'))
    c.restore()

def bubble(c, x, y, w, h, k, tail):
    """thought bubble (cloud) with small trailing circles toward tail=(tx,ty)."""
    if k <= .03: return False
    c.save(); c.translate(x, y); c.scale(k, k)
    for j, r in enumerate((14, 22)):
        tx = lerp(tail[0] - x, 0, .25 + j * .22) ; ty = lerp(tail[1] - y, h / 2, .25 + j * .22)
        ell(c, tx, ty, r, r); fs(c, (1, 1, 1), 5)
    for (dx, dy, r) in ((-w * .32, -h * .18, h * .36), (0, -h * .3, h * .42), (w * .32, -h * .16, h * .36),
                        (-w * .36, h * .16, h * .32), (w * .34, h * .18, h * .32), (0, h * .22, h * .38)):
        ell(c, dx, dy, r * 1.25, r); fs(c, (1, 1, 1), 7)
    for (dx, dy, r) in ((-w * .32, -h * .18, h * .36), (0, -h * .3, h * .42), (w * .32, -h * .16, h * .36),
                        (-w * .36, h * .16, h * .32), (w * .34, h * .18, h * .32), (0, h * .22, h * .38)):
        ell(c, dx, dy, r * 1.25 - 6, r - 6); fill(c, (1, 1, 1))
    rrect(c, -w * .5, -h * .38, w, h * .76, 40); fill(c, (1, 1, 1))
    c.restore()
    return True

def smoke(c, x, y, t, n=5, s=1.0):
    for j in range(n):
        ph = (t * .9 + j / n) % 1
        P.puff(c, x + 20 * math.sin(t * 2 + j) * s, y - ph * 160 * s, (16 + ph * 34) * s, .75 * (1 - ph), (.45, .45, .5))

def ribbon(c, x, y, s=1.0, t=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.rectangle(-14, -90, 28, 180); fill(c, hx('#D7141A'))
    for sgn in (-1, 1):
        c.save(); c.scale(sgn, 1); c.rotate(.12 * math.sin(t * 5))
        c.move_to(0, -90); c.curve_to(60, -170, 120, -120, 90, -80); c.curve_to(70, -60, 30, -80, 0, -90); c.close_path(); fs(c, hx('#E5473B'), 5)
        poly(c, [(4, -86), (60, -10), (34, -6)]); fs(c, hx('#D7141A'), 4)
        c.restore()
    ell(c, 0, -90, 20, 18); fs(c, hx('#B30F14'), 5)
    c.restore()

def coin_pop(c, x, y, t, t0):
    d = t - t0
    if not (0 <= d < 1.0): return
    a = 1 - d
    c.save(); c.translate(x, y - 140 * eout(d))
    ell(c, 0, 0, 30, 30); fs(c, hx('#F2C230'), 5, a); text(c, "Rp", 0, 0, 22, hx('#8A5E10'), alpha=a)
    c.restore()

# ------------------------------------------------------------ street helpers
CAR_PARK = {'x': -760, 'y': 1620}

def parked(t, extra=None):
    car = dict(CAR_PARK); car.update(extra or {})
    return lambda c: G.draw_car3(c, t, car)

# ------------------------------------------------------------ depth of field: gaya.py mengatur MODE
class StopBG(Exception): pass
MODE = ['full']      # 'full' | 'bg' (latar saja) | 'fg' (tokoh saja)

def street(c, t, people, tod='day', toko='normal', shutter=0.0, fx=None, car=True, front=None):
    if MODE[0] == 'fg':
        for p in list(people) + list(front or []):
            E.person(c, p['x'], p['y'], p['who'], p, s=p.get('s', 1.0), t=t, flip=p.get('flip', False))
        return
    if MODE[0] == 'bg':
        people, front = [], []
    st = {'tod': tod, 'toko': toko, 'shutter': shutter, 'people': people, 'fx': list(fx or []),
          'pre_car': [parked(t)] if car else [], 'people_front': front or []}
    E.street(c, t, st)
    if MODE[0] == 'bg':
        raise StopBG

POS_R = 1020; POS_D = 1360; YS = 1430      # two-shot positions on the shop step

def rahmat_po(**kw):
    d = {'who': 'rahmat', 'x': POS_R, 'y': YS}; d.update(kw); return d

def dio_po(**kw):
    d = {'who': 'dio', 'x': POS_D, 'y': YS, 'flip': True}; d.update(kw); return d

SERIUS = dict(aF=(40, -100), aB=(-40, 100), eyes='squint', brows='angry', expr='flat', look=(5, 0))


def rain(c, t, a=.5):
    rnd = random.Random(3)
    for i in range(140):
        x0 = rnd.uniform(-200, W + 200); sp = rnd.uniform(1800, 2600); y0 = rnd.uniform(0, H)
        y = (y0 + t * sp) % (H + 200) - 100; x = x0 - (y * .18)
        c.move_to(x, y); c.line_to(x - 10, y + 50); c.set_source_rgba(.8, .85, 1, a * rnd.uniform(.4, 1)); c.set_line_width(2.5); c.stroke()
