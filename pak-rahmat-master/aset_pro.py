import sys, math, random, subprocess
import numpy as np
import cairo
from PIL import Image, ImageFilter
import aset_kampung as E
import aset_dasar as lib
from aset_dasar import W, H, OUT, hx, clamp, ease, eout, lerp, pop, fs, fill, rrect, ell, poly, line, text, spark, bulb_glow

lib.SHADE = True
FPS = 30
DUR = E.DUR
NF = int(DUR * FPS)

def spring(t, t0, amp=1.0, freq=14, damp=6):
    if t < t0: return 0.0
    d = t - t0
    return amp * math.exp(-damp * d) * math.sin(freq * d)

# ------------------------------------------------------------ world fx
DUST = [(random.Random(i).uniform(0, 1), random.Random(i * 7).uniform(0, 1), random.Random(i * 13).uniform(1.5, 4)) for i in range(70)]
def dust(c, t, x0, y0, w, h, col=(1, .97, .85), a=.6):
    for i, (u, v, r) in enumerate(DUST):
        x = x0 + ((u + t * 0.015 * (1 + i % 3)) % 1) * w
        y = y0 + ((v + t * 0.02 * (1 + i % 2)) % 1) * h
        ell(c, x + 8 * math.sin(t + i), y, r, r); fill(c, col, a * (.5 + .5 * math.sin(t * 2 + i)))

def sun_rays(c, t, sx, sy, a0=.12, col=(1, .97, .8)):
    for k in range(8):
        ang = math.radians(95 + k * 10 + 3 * math.sin(t * .3 + k)); w = math.radians(2.2 + (k % 3))
        L = 3400
        g = cairo.RadialGradient(sx, sy, 40, sx, sy, L)
        g.add_color_stop_rgba(0, *col, a0 * (.6 + .4 * math.sin(t * .7 + k))); g.add_color_stop_rgba(1, *col, 0)
        c.set_source(g); poly(c, [(sx, sy), (sx + L * math.cos(ang - w), sy + L * math.sin(ang - w)), (sx + L * math.cos(ang + w), sy + L * math.sin(ang + w))]); c.fill()

def puff(c, x, y, r, a, col=(.92, .88, .8)):
    for dx, dy, rr in ((0, 0, 1), (.7, -.3, .8), (-.6, -.25, .75), (.2, -.6, .7)):
        ell(c, x + dx * r, y + dy * r, rr * r, rr * r * .85); fill(c, col, a)

def car_fx(c, t, car):
    x, y = car['x'], car['y']
    if t < 33.35:
        for k in range(8):
            ph = (t * 3 + k / 8) % 1
            puff(c, x + 120 - ph * 380, y - 20 - ph * 60, 18 + ph * 55, .55 * (1 - ph))
        for k in range(3):
            yy = y - 420 + k * 120
            c.move_to(x - 80 - k * 30, yy); c.line_to(x - 300 - k * 30, yy); c.set_source_rgba(1, 1, 1, .8); c.set_line_width(8); c.stroke()
    d = t - 33.3
    if 0 <= d < 1:
        for k in range(9):
            a = math.pi + k * math.pi / 8; r = 60 + 260 * eout(d)
            puff(c, x + 430 + r * math.cos(a) * 1.6, y - 10 + r * .35 * math.sin(a), 30 + 40 * d, .6 * (1 - d))
    k = (t - 33.6) / .9
    if 0 <= k < 1:
        c.save(); c.rectangle(x + 8, y - 255, 540, 165); c.rectangle(x + 540, y - 420, 326, 328); c.clip()
        gx = x - 200 + k * 1300
        poly(c, [(gx, y - 450), (gx + 70, y - 450), (gx - 60, y - 60), (gx - 130, y - 60)])
        c.set_source_rgba(1, 1, 1, .55 * math.sin(k * math.pi)); c.fill(); c.restore()
        for j in range(2):
            spark(c, gx - 20 + j * 260, y - 380 + j * 120, 28 * math.sin(k * math.pi), math.sin(k * math.pi))

BIRDS = [(random.Random(k).uniform(0, 1), random.Random(k + 9).uniform(-200, 300), random.Random(k + 3).uniform(.6, 1.1)) for k in range(6)]
def birds(c, t):
    for k, (ph, y, s) in enumerate(BIRDS):
        x = ((ph + t * .035 * s) % 1) * 4400 - 800
        fl = math.sin(t * 9 + k)
        c.move_to(x - 26 * s, y - 10 * s * fl); c.curve_to(x - 12 * s, y - 14 * s, x - 6 * s, y - 4 * s, x, y)
        c.curve_to(x + 6 * s, y - 4 * s, x + 12 * s, y - 14 * s, x + 26 * s, y - 10 * s * fl)
        c.set_source_rgba(.15, .15, .2, .8); c.set_line_width(5 * s); c.stroke()

_street = E.street
def street_pro(c, t, st):
    st = dict(st)
    fx = list(st.get('fx', []))
    tod = st.get('tod', 'day')
    pre = []
    if tod in ('day', 'morning'):
        fx.insert(0, lambda c: sun_rays(c, t, 2700, -40, .11))
        fx.append(lambda c: dust(c, t, 1600, 300, 1400, 1100, (1, .97, .85), .35))
    elif tod == 'sore':
        fx.insert(0, lambda c: sun_rays(c, t, 300, 300, .14, (1, .78, .45)))
    fx.insert(0, lambda c: birds(c, t))
    car = st.get('car')
    if car and 30.35 <= t < 37.1:
        car = dict(car)
        car['pitch'] = .028 * ease((t - 32.7) / .6) if t < 33.3 else .028 * math.exp(-5 * (t - 33.3)) * math.cos(13 * (t - 33.3))
        car['smoke'] = False
        st['car'] = car
        fx.append(lambda c, car=car: car_fx(c, t, car))
    st['fx'] = fx
    st['pre_car'] = list(st.get('pre_car', [])) + pre
    _street(c, t, st)
E.street = street_pro

_gudang = E.gudang
def gudang_pro(c, t, st):
    _gudang(c, t, st)
    night = st.get('night', False)
    col = (.7, .8, 1) if night else (1, .97, .85)
    g = cairo.LinearGradient(210, 320, 500, 1500)
    g.add_color_stop_rgba(0, *col, .22 if not night else .14); g.add_color_stop_rgba(1, *col, 0)
    c.set_source(g); poly(c, [(80, 320), (340, 320), (900, 1500), (300, 1500)]); c.fill()
    c.save(); poly(c, [(80, 320), (340, 320), (900, 1500), (300, 1500)]); c.clip()
    dust(c, t, 80, 320, 820, 1180, col, .5); c.restore()
E.gudang = gudang_pro

# ------------------------------------------------------------ post
NOISE = [np.random.default_rng(i).normal(0, 4.0, (H // 2, W // 2, 1)).astype(np.float32) for i in range(4)]
GRADE = {'morning': (.97, 1.0, 1.04), 'day': (.98, 1.0, 1.03), 'freeze': (1, 1, 1), 'indoor': (.92, .99, 1.06),
         'sore': (.86, .97, 1.1), 'night': (1.1, .97, .88), 'cliff': (.9, .9, 1.12)}

def tod_at(t):
    if 17.2 <= t < 20.45: return 'freeze'
    if 20.45 <= t < 25.5: return 'indoor'
    if 30.35 <= t < 37.1 or 25.5 <= t < 30.35: return 'day'
    if 37.1 <= t < 44.2: return 'sore'
    if 44.2 <= t < 51.15: return 'night'
    if t >= 51.15: return 'cliff'
    return 'morning'

def post(surf, t, whip):
    tod = tod_at(t)
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    rgb = a[:, :, :3].astype(np.float32)
    thr, stren = (165, .55) if tod in ('night', 'cliff') else (205, .3)
    sm = np.asarray(Image.fromarray(a[:, :, :3]).resize((W // 4, H // 4), Image.BILINEAR)).astype(np.float32)
    lum = sm.mean(axis=2, keepdims=True)
    bright = np.clip((lum - thr) / 50, 0, 1) * sm
    bl = Image.fromarray(bright.astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)).resize((W, H), Image.BILINEAR)
    rgb += np.asarray(bl).astype(np.float32) * stren
    gray = rgb.mean(axis=2, keepdims=True)
    sat = {'freeze': .35, 'night': 1.0, 'cliff': 1.1}.get(tod, 1.14)
    rgb = gray + (rgb - gray) * sat
    g = GRADE[tod]
    rgb[:, :, 0] *= g[0]; rgb[:, :, 1] *= g[1]; rgb[:, :, 2] *= g[2]
    x = np.clip(rgb, 0, 255) / 255.0
    rgb = (x + 0.07 * (x - 0.5) * (1 - np.abs(2 * x - 1))) * 255
    rgb += np.repeat(np.repeat(NOISE[int(t * FPS) % 4], 2, 0), 2, 1)
    if whip > 0.01:
        sh = int(26 * whip); acc = np.zeros_like(rgb)
        for k in range(-3, 4): acc += np.roll(rgb, k * sh, axis=1)
        rgb = acc / 7
    np.copyto(a[:, :, :3], np.clip(rgb, 0, 255).astype(np.uint8))
    surf.mark_dirty()

CUTS = [s[0] for s in E.SCENES[1:]]
PUNCH = [13.75, 17.2, 24.35, 29.3, 34.7, 51.3, 55.3]
SHAKES = [13.75, 17.2, 29.3, 33.3, 34.7, 51.3, 53.3]

def render(fi):
    t = fi / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    sc = next(s for s in E.SCENES if s[0] <= t < s[1])
    t0, t1, fn, keys = sc
    if fn is E.sc_dulu_sekarang:
        fn(c, t, t0)
    elif fn is E.sc_group_chat:
        c.save(); c.translate(W / 2 + 6 * math.sin(t * .9), H / 2); c.translate(-2000, -1000)
        E.street(c, t, {'tod': 'morning', 'toko': 'kosong', 'car': {'x': 700, 'y': 1600}})
        c.restore()
        c.set_source_rgba(1, 1, 1, .35); c.paint()
        msgs = [(4.6, "Bu Julit", "Ibu-ibu!! Toko Pak Rahmat\nKOSONG MELOMPONG!", False), (5.5, "Bu Sri", "Masa sih bu??", False),
                (6.2, "Bu Ani", "Wah, bangkrut tuh...", False), (6.9, "Bu Julit", "Gara-gara beli mobil kali", False)]
        k = eout((t - 4.45) / .35)
        c.save(); c.translate(W / 2, lerp(2300, 800, k)); c.rotate(.03 * math.sin(t * 1.5)); c.translate(-W / 2, -lerp(2300, 800, k))
        E.phone(c, W / 2, lerp(2300, 800, k), 1.05, msgs, t, "GRUP IBU-IBU RT 05", group=True)
        c.restore()
        for at in (4.6, 5.5, 6.2, 6.9):
            d = t - at
            if 0 <= d < .4:
                for j in range(6):
                    a = j * math.pi / 3
                    spark(c, W / 2 + 330 * math.cos(a), 700 + 200 * math.sin(a), 22 * (1 - d / .4), 1 - d / .4)
    else:
        cx, cy, z = E.cam_for(t, keys)
        cx += 6 * math.sin(t * .9) + 3 * math.sin(t * 2.3); cy += 5 * math.sin(t * 1.1 + 1)
        for p in PUNCH:
            if t >= p: z *= 1 + .07 * math.exp(-7 * (t - p))
        amp = 0
        for s in SHAKES:
            if 0 <= t - s < .35: amp = max(amp, 18 * (1 - (t - s) / .35))
        c.save(); c.translate(W / 2 + amp * math.sin(t * 97), H / 2 + amp * math.cos(t * 73)); c.scale(z, z); c.translate(-cx, -cy)
        fn(c, t, t0)
        c.restore()
    # extra screen fx
    E.focus_lines(c, t, 34.7, 35.9, cy=H * .45)
    E.focus_lines(c, t, 13.75, 14.4, cy=H * .45)
    E.focus_lines(c, t, 51.15, 51.8, cy=H * .42)
    if 20.45 <= t < 25.5 and t >= 24.35:
        d = t - 24.35
        for j in range(10):
            a = j * math.pi / 5 + d
            spark(c, 900 + 200 * math.cos(a), 700 + 120 * math.sin(a), 26 * max(0, 1 - d / 1.2), max(0, 1 - d / 1.2))
    if 25.5 <= t < 30.35 and t >= 29.3:
        d = t - 29.3
        for j in range(12):
            a = j * math.pi / 6
            spark(c, W / 2 + (120 + 360 * eout(min(1, d))) * math.cos(a), H * .72 + (80 + 240 * eout(min(1, d))) * math.sin(a), 24 * max(0, 1 - d), max(0, 1 - d))
    for s in CUTS:
        d = t - s
        if 0 <= d < 0.1: c.set_source_rgba(1, 1, 1, .3 * (1 - d / .1)); c.paint()
    for tb in (51.3, 53.3):
        d = t - tb
        if 0 <= d < .12: c.set_source_rgba(1, 1, 1, .5 * (1 - d / .12)); c.paint()
    whip = 0.0
    for s in CUTS:
        d = t - s
        if -0.07 <= d < 0: whip = max(whip, (d + .07) / .07)
        elif 0 <= d < 0.1: whip = max(whip, 1 - d / .1)
    post(surf, t, whip)
    c = cairo.Context(surf)
    # crisp overlays
    if 17.2 <= t < 20.45:
        k = pop(t, 17.3, .3)
        if k > .03:
            c.save(); c.translate(W / 2, 560); c.scale(k, k); c.rotate(-.08)
            rrect(c, -360 + 8, -90 + 12, 720, 180, 20); fill(c, (0, 0, 0), .25)
            rrect(c, -360, -90, 720, 180, 20); fs(c, hx('#D8312B'), 10)
            text(c, "TUNGGU DULU!", 0, 0, 84, (1, 1, 1), OUT, 10)
            c.restore()
        for k in range(2):
            x = 120 + k * 60
            poly(c, [(x + 50, 160), (x, 195), (x + 50, 230)]); fs(c, (1, 1, 1), 4)
        text(c, "PAUSE", 300, 196, 40, (1, 1, 1), OUT, 6, align='l')
    if 20.45 <= t < 25.5: E.pill(c, "TERNYATA...", t, 20.6, col=hx('#FFE14D'))
    if 37.1 <= t < 39.5: E.pill(c, "SORENYA...", t, 37.2, col=hx('#FF9F43'))
    if 44.2 <= t < 45.5: E.pill(c, "MALAMNYA...", t, 44.25, col=hx('#7FB3FF'))
    gr = cairo.RadialGradient(W / 2, H / 2, H * .32, W / 2, H / 2, H * .78)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0); gr.add_color_stop_rgba(1, 0, 0, .04, .4 if tod_at(t) in ('night', 'cliff') else .34)
    c.set_source(gr); c.paint()
    if t < .3: c.set_source_rgba(0, 0, 0, 1 - t / .3); c.paint()
    if t > DUR - .35: c.set_source_rgba(0, 0, 0, clamp((t - (DUR - .35)) / .35)); c.paint()
    E.captions(c, t)
    surf.flush()
    return bytes(surf.get_data())
