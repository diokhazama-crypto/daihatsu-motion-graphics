import sys, math, random, json, subprocess
import numpy as np
import cairo
from PIL import Image
import aset_kampung as E
import aset_pro as P
import aset_dasar as lib
from aset_dasar import (W, H, OUT, hx, clamp, ease, eout, lerp, pop, fs, fill, rrect, ell, poly, line, text,
                 CH, sweat, spark, bulb_glow, sack)

lib.SHADE = True
FPS = 30
VDUR = 58.64          # voice length
DUR = 61.3            # + CTA tail
NF = int(DUR * FPS)

def spring(t, t0, amp=1.0, freq=14, damp=6):
    if t < t0: return 0.0
    d = t - t0
    return amp * math.exp(-damp * d) * math.sin(freq * d)

# ------------------------------------------------------------ words
WORDS = []   # master: narasi episode dibaca di gaya.py
FIX = {16: "bisa", 17: "bangkrut", 22: "Modal", 77: "Gran", 93: "sekilo", 109: "melongo.", 113: "bangkrut,", 121: "kunci.",
       140: "Bersambung."}
JOIN = {25, 30, 71, 87, 103}      # append to previous token (bertahun-tahun, gara-gara, diperiksa, diantar, anak-anak)
words = []
for i, (w, a, b) in enumerate(WORDS):
    w = FIX.get(i, w)
    if i in JOIN:
        prev = words[-1]
        if i in (71, 87): prev[0] = prev[0] + w        # di + periksa -> diperiksa
        else: prev[0] = prev[0] + w
        prev[2] = b; continue
    words.append([w, a, b])
CHUNKS = []; cur = []
for w in words:
    cur.append(w)
    if len(cur) >= 3 or w[0][-1] in ",.?!" or len(" ".join(x[0] for x in cur)) > 15:
        CHUNKS.append(cur); cur = []
if cur: CHUNKS.append(cur)

def talk(t, spans):
    for a, b in spans:
        if a <= t <= b:
            e = lib.env(t)
            return clamp((e - 0.12) * 1.4) * (0.6 + 0.4 * abs(math.sin(t * 19)))
    return 0.0

# ------------------------------------------------------------ characters
CH['kadapur'] = dict(skin=hx('#E3AE85'), shirt=hx('#FFFFFF'), pants=hx('#2B2B33'), hair='hijab', hij=hx('#1F4E99'), ciput=hx('#FFFFFF'),
                     bros=hx('#F2C230'), kind='man', long=True, collar=True, collar_col=hx('#E8E8E8'), buttons=True, belt=None, foot='shoe', badge=hx('#2EAD6B'))
CH['koki1'] = dict(skin=hx('#D39B6B'), dress=hx('#F4F1EA'), dots=hx('#F4F1EA'), hair='hijab', hij=hx('#2EAD6B'), ciput=hx('#FFFFFF'),
                   kind='daster', celemek=hx('#2EAD6B'), trim=hx('#2EAD6B'), foot='shoe')
CH['koki2'] = dict(skin=hx('#C98A5A'), shirt=hx('#FFFFFF'), pants=hx('#3B3B46'), hair='cap', kind='man', collar=True, buttons=True, foot='shoe',
                   pocket=True)
for i, (sk, hair) in enumerate([('#D39B6B', 'spiky'), ('#E3AE85', 'hijab'), ('#C98A5A', 'short'), ('#F1C6A0', 'hijab'), ('#B97B4E', 'spiky'), ('#E3AE85', 'short')]):
    d = dict(skin=hx(sk), shirt=hx('#FFFFFF'), pants=hx('#D7141A'), hair=hair, kind='man', collar=True, buttons=True, foot='shoe', badge=hx('#D7141A'))
    if hair == 'hijab': d.update(hij=hx('#FFFFFF'), ciput=hx('#FFFFFF'))
    CH[f'murid{i}'] = d
CH['guru'] = dict(skin=hx('#E3AE85'), shirt=hx('#B85C9E'), pants=hx('#2B2B33'), hair='hijab', hij=hx('#6A2D5E'), ciput=hx('#FFFFFF'), kind='man',
                  long=True, pattern='batik', pat_col=hx('#F2C230'), foot='shoe', watch=hx('#E8E8E8'))

# ------------------------------------------------------------ acting wrapper
_person = lib.person
def person3(c, x, y, who, po=None, s=1.0, t=0.0, flip=False):
    po = dict(po or {})
    if who == 'julit' and (po.get('eyes') == 'wide' or po.get('mouth', 0) > .3):
        po['jiggle'] = 1
    if who == 'rahmat' and po.get('eyes') == 'wide':
        po['peci_lift'] = 1
    return _person(c, x, y, who, po, s=s, t=t, flip=flip)
E.person = person3
person = person3

# ------------------------------------------------------------ props
def uang_terbang(c, t, t0, x0, y0, n=8):
    d = t - t0
    if d < 0: return
    for i in range(n):
        ph = (d * .55 + i / n) % 1.6
        x = x0 + (i - n / 2) * 60 + ph * 300 * (1 if i % 2 else -1) + 30 * math.sin(t * 3 + i)
        y = y0 - ph * 700
        c.save(); c.translate(x, y); c.rotate(.3 * math.sin(t * 4 + i))
        rrect(c, -60, -30, 120, 60, 6); fs(c, hx('#F07AA8'), 4)
        ell(c, 0, 0, 20, 20); c.set_source_rgba(1, 1, 1, .6); c.set_line_width(3); c.stroke()
        text(c, "100", -32, -12, 16, hx('#8E2443')); text(c, "Rp", 30, 12, 16, hx('#8E2443'))
        fl = math.sin(t * 16 + i) * .8
        for sgn in (-1, 1):
            c.save(); c.translate(sgn * 20, -30); c.scale(sgn, 1); c.rotate(-.4 - fl * .4)
            c.move_to(0, 0); c.curve_to(20, -40, 60, -40, 70, -20); c.curve_to(50, -16, 30, -8, 0, 0); c.close_path(); fs(c, (1, 1, 1), 3)
            c.restore()
        c.restore()

def nota(c, x, y, s, t, stamp_t):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-.04)
    rrect(c, -170, -230, 340, 460, 8); fs(c, (1, 1, 1), 5)
    text(c, "NOTA PESANAN", 0, -190, 30, OUT)
    c.move_to(-140, -165); c.line_to(140, -165); c.set_source_rgb(*OUT); c.set_line_width(3); c.stroke()
    rows = [("Paket sembako", "500"), ("Beras 5kg", "500"), ("Minyak 1L", "500"), ("Gula 1kg", "500"), ("Mie instan", "1000")]
    for i, (a, b) in enumerate(rows):
        text(c, a, -140, -125 + i * 40, 22, OUT, font="Inter", align='l'); text(c, b, 140, -125 + i * 40, 22, OUT, font="Inter", align='r')
    c.move_to(-140, 80); c.line_to(140, 80); c.stroke()
    text(c, "PEMBAYARAN:", -140, 115, 22, OUT, font="Inter Black", align='l')
    k = pop(t, stamp_t, .25)
    if k > .03:
        c.save(); c.translate(20, 170); c.scale(k * 1.0, k * 1.0); c.rotate(-.18)
        rrect(c, -150, -42, 300, 84, 10); c.set_source_rgb(*hx('#D7141A')); c.set_line_width(8); c.stroke()
        text(c, "BELUM DIBAYAR", 0, 0, 34, hx('#D7141A'))
        c.restore()
    c.restore()

def dandang(c, x, y, s, t, steam=True):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -70, -10, 140, 24, 6); fs(c, hx('#3A3A44'), 4)             # stove
    for k in range(5):
        fx = -40 + k * 20
        c.move_to(fx - 6, -10); c.curve_to(fx - 6, -26 - 6 * math.sin(t * 20 + k), fx + 6, -26 - 6 * math.cos(t * 18 + k), fx + 6, -10)
        c.close_path(); fill(c, hx('#4FA3F7'), .9)
    rrect(c, -80, -170, 160, 160, 18); fs(c, hx('#C9CED4'), 5)
    c.rectangle(-80, -120, 160, 10); fill(c, (1, 1, 1), .6)
    c.move_to(-60, -160); c.line_to(-60, -20); c.set_source_rgba(1, 1, 1, .7); c.set_line_width(8); c.stroke()
    ell(c, 0, -170, 86, 18); fs(c, hx('#AAB1B8'), 5)
    rrect(c, -14, -196, 28, 18, 6); fs(c, hx('#2B2B2B'), 3)
    for sgn in (-1, 1):
        rrect(c, sgn * 92 - 12, -140, 24, 14, 5); fs(c, hx('#2B2B2B'), 3)
    if steam:
        for k in range(4):
            ph = (t * .7 + k / 4) % 1
            ell(c, -30 + k * 20 + 20 * math.sin(t + k), -200 - ph * 260, 24 + ph * 30, 20 + ph * 24); fill(c, (1, 1, 1), .55 * (1 - ph))
    c.restore()

def ompreng(c, x, y, s=1.0, full=True):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -90, -55, 180, 110, 14); fs(c, hx('#D5DADF'), 4)
    for (bx, by, bw, bh) in ((-80, -45, 90, 90), (16, -45, 64, 40), (16, 1, 30, 44), (52, 1, 28, 44)):
        rrect(c, bx, by, bw, bh, 8); fs(c, hx('#BFC6CD'), 2)
    if full:
        ell(c, -35, 0, 38, 36); fs(c, (1, 1, 1), 2)                       # nasi
        ell(c, 48, -25, 22, 16); fs(c, (1, 1, 1), 2); ell(c, 48, -25, 10, 9); fill(c, hx('#F2C230'))   # telur
        for k in range(4): ell(c, 26 + k * 3, 14 + k * 8, 10, 6); fill(c, hx('#3E9B47'))             # sayur
        ell(c, 66, 22, 12, 12); fs(c, hx('#F07D2B'), 2)                   # jeruk
    c.restore()

def gembok(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.arc(0, -16, 18, math.pi, 2 * math.pi); c.set_source_rgb(*hx('#9AA1A9')); c.set_line_width(8); c.stroke()
    rrect(c, -26, -18, 52, 40, 8); fs(c, hx('#F2C230'), 4)
    ell(c, 0, 0, 6, 6); fill(c, OUT); c.rectangle(-2, 0, 4, 12); fill(c, OUT)
    c.restore()

def checklist(c, x, y, s, t, t0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(.03)
    rrect(c, -190, -260, 380, 520, 14); fs(c, hx('#A8763E'), 6)
    rrect(c, -60, -280, 120, 40, 10); fs(c, hx('#9AA1A9'), 4)
    rrect(c, -165, -230, 330, 470, 6); fs(c, (1, 1, 1), 3)
    text(c, "PEMERIKSAAN", 0, -195, 30, OUT)
    items = ["Kualitas beras", "Telur segar", "Minyak bersegel", "Harga wajar", "Izin usaha"]
    for i, it in enumerate(items):
        yy = -130 + i * 74
        rrect(c, -145, yy - 22, 44, 44, 6); fs(c, (1, 1, 1), 3)
        text(c, it, -86, yy, 26, OUT, font="Inter", align='l')
        k = pop(t, t0 + i * .35, .2)
        if k > .03:
            c.save(); c.translate(-123, yy); c.scale(k, k)
            c.move_to(-14, 0); c.line_to(-3, 14); c.line_to(20, -18); c.set_source_rgb(*hx('#2EAD6B')); c.set_line_width(9); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
            c.restore()
    c.restore()

def kontrak(c, x, y, s, t, t0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-.03)
    rrect(c, -200, -270, 400, 540, 8); fs(c, (1, 1, 1), 5)
    text(c, "SURAT PERJANJIAN", 0, -225, 30, OUT)
    text(c, "PASOKAN RUTIN", 0, -185, 34, hx('#1F4E99'))
    text(c, "SETIAP PAGI", 0, -140, 28, hx('#D7141A'))
    for i in range(7):
        c.move_to(-160, -90 + i * 30); c.line_to(160 - (i % 3) * 30, -90 + i * 30); c.set_source_rgba(0, 0, 0, .35); c.set_line_width(4); c.stroke()
    for sx_ in (-90, 90):
        c.move_to(sx_ - 70, 200); c.line_to(sx_ + 70, 200); c.set_source_rgb(*OUT); c.set_line_width(3); c.stroke()
    k = clamp((t - t0) / .8)
    if k > 0:
        c.move_to(-150, 190)
        for j in range(int(20 * k)):
            c.line_to(-150 + j * 6, 190 - 14 * math.sin(j * 1.3))
        c.set_source_rgb(*hx('#1F4E99')); c.set_line_width(4); c.stroke()
    c.restore()

def alarm(c, x, y, s, t):
    c.save(); c.translate(x + 5 * math.sin(t * 60), y); c.scale(s, s)
    for sgn in (-1, 1):
        ell(c, sgn * 60, -110, 34, 30); fs(c, hx('#D7141A'), 5)
    ell(c, 0, 0, 120, 120); fs(c, hx('#D7141A'), 7)
    ell(c, 0, 0, 96, 96); fs(c, (1, 1, 1), 4)
    line(c, [(0, 0), (0, -60)], 8, OUT, False); line(c, [(0, 0), (0, 70)], 5, OUT, False)
    text(c, "04.00", 0, 40, 30, hx('#D7141A'))
    for sgn in (-1, 1):
        for k in range(3):
            c.move_to(sgn * (150 + k * 20), -60 + k * 30); c.line_to(sgn * (180 + k * 20), -70 + k * 30); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    c.restore()

# ------------------------------------------------------------ DAPUR MBG (detailed)
def dapur_mbg(c, t, st):
    # sky / ground
    g = cairo.LinearGradient(0, -900, 0, 1340)
    g.add_color_stop_rgb(0, *hx('#58B2F2')); g.add_color_stop_rgb(1, *hx('#FFE3B8'))
    c.set_source(g); c.rectangle(-3000, -3000, 9000, 4340); c.fill()
    for k in range(5):
        cx_ = (k * 620 + t * 14) % 3600 - 900; cy_ = 80 + (k * 97 % 260)
        for dx, dy, r in [(0, 0, 50), (55, -20, 60), (115, 0, 48), (60, 20, 50)]:
            ell(c, cx_ + dx, cy_ + dy, r, r * .85); fill(c, (1, 1, 1), .9)
    E.tree(c, -150, 1340, 1.1, t); E.tree(c, 2250, 1340, 1.15, t)
    # building
    c.rectangle(200, 520, 1800, 820); fs(c, hx('#F4F1EA'), 7)
    c.rectangle(200, 520, 1800, 60); fs(c, hx('#2EAD6B'), 5)
    c.rectangle(200, 1240, 1800, 100); fs(c, hx('#D9D2C0'), 5)
    # sign
    rrect(c, 360, 300, 1480, 240, 20); fs(c, hx('#1F4E99'), 8)
    rrect(c, 380, 320, 1440, 200, 14); c.set_source_rgba(1, 1, 1, .4); c.set_line_width(3); c.stroke()
    ell(c, 500, 420, 70, 70); fs(c, hx('#FFFFFF'), 5)                      # generic bowl icon
    c.arc(500, 420, 44, 0, math.pi); fs(c, hx('#F2C230'), 4)
    for k in range(3):
        c.move_to(480 + k * 20, 380); c.curve_to(470 + k * 20, 360, 490 + k * 20, 345, 480 + k * 20, 325); c.set_source_rgb(*hx('#9AA1A9')); c.set_line_width(4); c.stroke()
    text(c, "DAPUR MBG", 1150, 385, 104, (1, 1, 1), OUT, 12)
    text(c, "MAKAN BERGIZI GRATIS", 1150, 470, 44, hx('#FFE14D'), OUT, 6)
    for px in (420, 1780):
        c.rectangle(px - 8, 540, 16, 40); fs(c, hx('#7D848C'), 3)
    # kitchen opening (service window)
    c.rectangle(260, 640, 980, 600); fs(c, hx('#DCE3E8'), 6)
    for k in range(10):     # wall tiles
        for j in range(6):
            c.rectangle(264 + k * 98, 644 + j * 50, 96, 48); c.set_source_rgba(0, 0, 0, .08); c.set_line_width(2); c.stroke()
    poly(c, [(420, 650), (1080, 650), (1020, 740), (480, 740)]); fs(c, hx('#AAB1B8'), 5)      # exhaust hood
    rrect(c, 700, 600, 100, 60, 6); fs(c, hx('#9AA1A9'), 4)
    for k in range(3):
        rrect(c, 300 + k * 60, 760, 50, 36, 4); fs(c, hx('#D5DADF'), 2)
    # shelves with ompreng
    for j in range(3):
        c.rectangle(1080, 770 + j * 70, 140, 8); fs(c, hx('#9AA1A9'), 2)
        for k in range(4):
            rrect(c, 1090 + k * 32, 744 + j * 70, 30, 26, 4); fs(c, hx('#D5DADF'), 2)
    # cooks + pots
    if st.get('cooks', True):
        person(c, 470, 1180, 'koki1', {'aF': (120 + 30 * math.sin(t * 6), -40), 'aB': (40, 0), 'expr': 'smile', 'look': (4, 2)}, s=.92, t=t)
        person(c, 980, 1180, 'koki2', {'flip': True, 'aF': (110 + 25 * math.sin(t * 5 + 1), -30), 'expr': 'smile', 'look': (-4, 2)}, s=.92, t=t)
    for k, px in enumerate((620, 830)):
        dandang(c, px, 1080, .95, t + k)
    c.rectangle(260, 1080, 980, 30); fs(c, hx('#C9CED4'), 5)                # stainless counter
    c.rectangle(270, 1110, 960, 130); fs(c, hx('#AAB1B8'), 5)
    for k in range(4):
        rrect(c, 300 + k * 230, 1130, 200, 90, 6); c.set_source_rgba(0, 0, 0, .25); c.set_line_width(3); c.stroke()
        ell(c, 390 + k * 230, 1175, 8, 8); fs(c, hx('#E8E8E8'), 2)
    for k in range(5):
        ompreng(c, 330 + k * 130, 1062, .55)
    # loading bay door
    c.rectangle(1320, 760, 420, 480); fs(c, hx('#9AA1A9'), 6)
    for k in range(26):
        c.rectangle(1320, 760 + k * 18, 420, 3); fill(c, (0, 0, 0), .18)
    rrect(c, 1360, 690, 340, 54, 8); fs(c, hx('#F2C230'), 4)
    text(c, "AREA BONGKAR MUAT", 1530, 717, 26, OUT)
    # posters
    rrect(c, 1780, 640, 190, 250, 8); fs(c, (1, 1, 1), 4)
    text(c, "DICARI!", 1875, 680, 34, hx('#D7141A'))
    text(c, "PEMASOK", 1875, 730, 26, OUT); text(c, "SEMBAKO", 1875, 765, 26, OUT); text(c, "LOKAL", 1875, 800, 26, hx('#1F4E99'))
    for k in range(4):
        c.move_to(1810, 840 + k * 12); c.line_to(1940, 840 + k * 12); c.set_source_rgba(0, 0, 0, .25); c.set_line_width(2); c.stroke()
    rrect(c, 1780, 920, 190, 120, 8); fs(c, hx('#E8F6EA'), 4)
    text(c, "GIZI", 1875, 955, 26, hx('#2EAD6B')); text(c, "SEIMBANG", 1875, 990, 24, hx('#2EAD6B'))
    for k, col in enumerate(('#2EAD6B', '#F2C230', '#E5473B', '#2E86DE')):
        ell(c, 1815 + k * 40, 1020, 12, 12); fill(c, hx(col))
    # gas + galon + bins + pots
    for k in range(3):
        rrect(c, 2010 + k * 70, 1220, 60, 120, 20); fs(c, hx('#2E86DE'), 4)
        rrect(c, 2024 + k * 70, 1196, 32, 28, 8); fs(c, hx('#2E86DE'), 3)
    for k, (col, lbl) in enumerate((('#2EAD6B', 'ORGANIK'), ('#F2C230', 'ANORGANIK'))):
        rrect(c, 1330 + k * 120, 1250, 100, 90, 8); fs(c, hx(col), 4)
        text(c, lbl, 1380 + k * 120, 1295, 13, OUT)
    for px in (160, 1260, 1960):
        poly(c, [(px - 30, 1290), (px + 30, 1290), (px + 22, 1340), (px - 22, 1340)]); fs(c, hx('#C0703A'), 4)
        for j in range(5):
            a = -math.pi / 2 + (j - 2) * .3
            poly(c, [(px - 5, 1290), (px + 5, 1290), (px + 70 * math.cos(a), 1290 + 90 * math.sin(a))]); fs(c, hx('#3E9B47'), 2)
    # yard + road
    c.rectangle(-3000, 1340, 9000, 90); fs(c, hx('#C9C3B6'), 5)
    c.rectangle(-3000, 1430, 9000, 330); fill(c, hx('#55585E'))
    for k in range(-20, 60):
        c.rectangle(k * 240, 1600, 130, 14); fill(c, hx('#F2F2F2'), .85)
    c.rectangle(-3000, 1760, 9000, 3000); fill(c, hx('#D9CDB0'))
    for r in range(14):
        for k in range(-30, 70):
            xx = k * 70 + (r % 2) * 35; yy = 1770 + r * 44
            rrect(c, xx, yy, 66, 40, 5); c.set_source_rgba(0, 0, 0, .12); c.set_line_width(2); c.stroke()
    c.rectangle(-3000, 1760, 9000, 14); fill(c, hx('#9A9286'))
    for px in (-60, 640, 1500, 2200):      # planters
        rrect(c, px, 1960, 360, 110, 10); fs(c, hx('#9AA1A9'), 5)
        c.rectangle(px + 10, 1960, 340, 16); fill(c, hx('#6B4A33'))
        for j in range(9):
            ell(c, px + 30 + j * 38, 1945 - (j % 2) * 16, 26, 26); fs(c, hx('#3E9B47'), 3)
            ell(c, px + 30 + j * 38, 1930 - (j % 2) * 16, 10, 10); fill(c, hx(['#E5473B', '#F2C230', '#F07AA8'][j % 3]))
    # bench + bicycle
    rrect(c, 1080, 1880, 300, 24, 6); fs(c, hx('#A8763E'), 4)
    for lx in (1100, 1350): c.rectangle(lx, 1904, 14, 60); fs(c, hx('#5A3A22'), 3)
    rrect(c, 1080, 1830, 300, 20, 6); fs(c, hx('#A8763E'), 4)
    for wx in (1560, 1720):
        ell(c, wx, 1880, 52, 52); c.set_source_rgb(*OUT); c.set_line_width(7); c.stroke()
    line(c, [(1560, 1880), (1630, 1810), (1720, 1880)], 7, hx('#E5473B'), False)
    line(c, [(1630, 1810), (1700, 1810), (1720, 1880)], 7, hx('#E5473B'), False)
    line(c, [(1700, 1810), (1695, 1780), (1720, 1775)], 6, OUT, False)
    rrect(c, 1610, 1792, 40, 12, 5); fs(c, OUT, 2)
    # welcome sign
    c.rectangle(-170, 1700, 16, 260); fs(c, hx('#7D848C'), 3)
    rrect(c, -330, 1600, 340, 120, 12); fs(c, hx('#2EAD6B'), 5)
    text(c, "SELAMAT DATANG", -160, 1640, 26, (1, 1, 1)); text(c, "Area Dapur MBG", -160, 1685, 22, hx('#FFE14D'))
    # banner
    rrect(c, 260, 560, 900, 60, 8); fs(c, hx('#E5473B'), 4)
    text(c, "Gizi Seimbang untuk Generasi Emas", 710, 590, 30, (1, 1, 1))
    for f in st.get('people', []):
        person(c, f['x'], f['y'], f['who'], f, s=f.get('s', 1.0), t=t, flip=f.get('flip', False))
    car = st.get('car')
    if car: draw_car3(c, t, car)
    for f in st.get('front', []):
        person(c, f['x'], f['y'], f['who'], f, s=f.get('s', 1.0), t=t, flip=f.get('flip', False))
    for f in st.get('fx', []): f(c)
    P.sun_rays(c, t, 2600, -60, .1)

def car_load(c, x, y, t, labels_t=None):
    # beras sacks, egg trays, minyak boxes in bed
    for k in range(4):
        sack(c, x + 80 + k * 115, y - 285, 112, 72)
    for k in range(3):
        sack(c, x + 140 + k * 115, y - 345, 112, 72)
    for k in range(2):
        E.rak_telur(c, x + 480, y - 270 - k * 1, 3)
    for k in range(2):
        E.kardus(c, x + 30 + k * 130, y - 380, 120, 70, "MINYAK GORENG")

def draw_car3(c, t, car):
    x, y = car['x'], car['y']
    c.save(); c.translate(x + 690, y); c.rotate(car.get('pitch', 0)); c.translate(-(x + 690), -y)
    if car.get('load'): car_load(c, x, y, t)
    lib.gran_max(c, x, y, t, car.get('ang', 0), car.get('driver', False), 0, cargo=False, driver_po=car.get('dpo'))
    if car.get('sticker'):
        rrect(c, x + 120, y - 240, 300, 46, 8); fs(c, hx('#1F4E99'), 3)
        text(c, "PEMASOK DAPUR MBG", x + 270, y - 217, 22, (1, 1, 1))
    c.restore()
    if car.get('moving'):
        for k in range(8):
            ph = (t * 3 + k / 8) % 1
            P.puff(c, x + 120 - ph * 380, y - 20 - ph * 60, 18 + ph * 55, .5 * (1 - ph))

# ------------------------------------------------------------ classroom (kids eating)
def kelas(c, t):
    c.rectangle(-1000, -1000, 3080, 2400); fill(c, hx('#F6E7C1'))
    c.rectangle(-1000, 1100, 3080, 300); fill(c, hx('#E3CFA0'))
    c.rectangle(-1000, 1400, 3080, 1500); fill(c, hx('#B98A56'))
    for k in range(-6, 20):
        c.move_to(k * 120, 1400); c.line_to(k * 160 - 300, 2600); c.set_source_rgba(0, 0, 0, .12); c.set_line_width(3); c.stroke()
    # blackboard
    rrect(c, 140, 300, 800, 420, 10); fs(c, hx('#8A5A30'), 6)
    c.rectangle(160, 320, 760, 380); fill(c, hx('#2F4A3A'))
    text(c, "MENU HARI INI", 540, 380, 46, (1, 1, 1), font="Inter Black")
    for i, l_ in enumerate(["Nasi putih", "Telur balado", "Tumis sayur", "Buah jeruk"]):
        text(c, "- " + l_, 230, 450 + i * 55, 34, hx('#FFE9A6'), font="Inter", align='l')
    # windows
    for k, wx in enumerate((-260, 1010)):
        c.rectangle(wx, 360, 200, 300); fs(c, hx('#8FC6E8'), 6)
        c.move_to(wx + 100, 360); c.line_to(wx + 100, 660); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    # posters / clock
    ell(c, 980, 220, 50, 50); fs(c, (1, 1, 1), 5)
    line(c, [(980, 220), (980, 185)], 5, OUT, False); line(c, [(980, 220), (1005, 230)], 4, OUT, False)
    for k, (col, lbl) in enumerate((('#F2C230', 'A B C'), ('#7AC74F', '1 2 3'))):
        rrect(c, -230 + k * 1240 - (0 if k == 0 else 0), 760, 170, 120, 8); fs(c, hx(col), 4)
        text(c, lbl, -145 + k * 1240, 820, 30, OUT)
    # desks + kids
    kids = [('murid0', 180, 1480), ('murid1', 470, 1480), ('murid2', 760, 1480), ('murid3', 320, 1820), ('murid4', 620, 1820), ('murid5', 910, 1820)]
    for i, (who, x, y) in enumerate(kids):
        eat = (t * 1.3 + i * .37) % 1
        spoon = (150 if eat < .5 else 100, -60 if eat < .5 else -10)
        mouth = .5 if .4 < eat < .55 else 0
        person(c, x, y, who, {'sit': True, 'aF': spoon, 'aB': (60, 30), 'expr': 'grin' if eat > .55 else 'smile', 'mouth': mouth,
                              'eyes': 'happy' if eat > .7 else 'open', 'look': (2, 4)}, s=.7, t=t + i)
        c.rectangle(x - 120, y - 150, 240, 20); fs(c, hx('#C98B4A'), 4)
        c.rectangle(x - 110, y - 130, 220, 110); fill(c, hx('#A8763E'))
        ompreng(c, x + 10, y - 175, .7)
    person(c, 1080, 1700, 'guru', {'flip': True, 'aF': (150, -60), 'expr': 'grin', 'eyes': 'happy'}, s=1.0, t=t)

def kantor(c, t):
    c.rectangle(-1000, -1000, 3080, 2400); fill(c, hx('#E8EEF2'))
    c.rectangle(-1000, 1300, 3080, 1500); fill(c, hx('#B8C2CC'))
    rrect(c, 120, 260, 420, 300, 8); fs(c, (1, 1, 1), 5)            # calendar all days checked
    c.rectangle(120, 260, 420, 60); fill(c, hx('#2EAD6B'))
    text(c, "JADWAL PASOK", 330, 290, 28, (1, 1, 1))
    for r in range(4):
        for k in range(7):
            x = 150 + k * 55; y = 350 + r * 50
            c.move_to(x, y); c.line_to(x + 10, y + 12); c.line_to(x + 30, y - 10); c.set_source_rgb(*hx('#2EAD6B')); c.set_line_width(5); c.stroke()
    rrect(c, 640, 280, 300, 200, 8); fs(c, hx('#1F4E99'), 5)
    text(c, "DAPUR MBG", 790, 360, 40, (1, 1, 1)); text(c, "Ruang Kepala Dapur", 790, 410, 20, hx('#FFE14D'))
    # desk
    c.rectangle(-100, 1200, 1300, 40); fs(c, hx('#8A5E30'), 5)
    c.rectangle(-90, 1240, 1280, 300); fill(c, hx('#6B4A33'))
    rrect(c, 820, 1140, 110, 64, 6); fs(c, hx('#3A3A44'), 3)    # laptop
    rrect(c, 830, 1080, 90, 64, 4); fs(c, hx('#BFE4F2'), 3)

# ------------------------------------------------------------ scenes
def street_rahmat(c, t, st):
    E.street(c, t, st)

def sc_hook(c, t, t0):        # gudang with mountain of paket, rahmat worried
    E.gudang(c, t, {})
    for r in range(4):
        for k in range(7):
            E.paket(c, 560 + k * 100 - r * 20, 1480 - r * 120, .95)
    person(c, 320, 1500, 'rahmat', {'aF': (170, -165), 'aB': (40, -90), 'eyes': 'wide', 'expr': 'o', 'brows': 'up', 'look': (6, -4)}, s=1.1, t=t)
    rrect(c, 640, 560, 380, 180, 14); fs(c, hx('#2F3A32'), 6)
    text(c, "PAKET", 830, 600, 30, hx('#FFE14D')); text(c, "500", 830, 670, 76, (1, 1, 1))

def sc_nota(c, t, t0):
    sc_hook(c, t, t0)
    nota(c, 560, 900, 1.25, t, 4.75)

def sc_bangkrut(c, t, t0):
    E.gudang(c, t, {})
    person(c, 540, 1520, 'rahmat', {'aF': (172, -170 + 8 * math.sin(t * 20)), 'aB': (172, -170), 'eyes': 'wide', 'expr': 'o', 'brows': 'up', 'mouth': .6 * abs(math.sin(t * 9))}, s=1.25, t=t)
    uang_terbang(c, t, 6.0, 540, 1200, 9)
    sweat(c, 380, 960, 1.3); sweat(c, 710, 980, 1.1)

def sc_istri(c, t, t0):
    E.gudang(c, t, {})
    shake = 8 * math.sin(t * 30) if t > 8.6 else 0
    person(c, 700 + shake, 1520, 'burahmat', {'flip': True, 'aF': (170, -160), 'aB': (170, -160), 'eyes': 'wide', 'expr': 'o', 'mouth': .5 * abs(math.sin(t * 11)), 'brows': 'up'}, s=1.1, t=t)
    person(c, 330, 1520, 'rahmat', {'aF': (60, -20), 'aB': (40, -60), 'eyes': 'half', 'expr': 'frown', 'brows': 'up', 'look': (6, 0)}, s=1.1, t=t)
    for k in range(2): sweat(c, 620 + k * 170, 960, 1.1)
    if t > 10.0:
        uang_terbang(c, t, 10.0, 540, 900, 6)
        k = pop(t, 12.1, .3)
        if k > .03:
            c.save(); c.translate(540, 600); c.scale(k, k); c.rotate(-.06)
            text(c, "???", 0, 0, 120, hx('#FFE14D'), OUT, 12)
            c.restore()

def st_berangkat(t):
    k = clamp((t - 13.6) / 5.4)
    x = lerp(-900, 1800, k)
    return {'tod': 'morning', 'toko': 'normal', 'car': {'x': x, 'y': 1620, 'driver': True, 'ang': x / 62, 'dpo': {'aF': (110, 20), 'expr': 'frown', 'brows': 'up'}}}

def sc_berangkat(c, t, t0):
    E.street(c, t, st_berangkat(t))
    k = clamp((t - 13.6) / 5.4); x = lerp(-900, 1800, k)
    for j in range(8):
        ph = (t * 3 + j / 8) % 1
        P.puff(c, x + 120 - ph * 380, 1600 - ph * 60, 18 + ph * 55, .5 * (1 - ph))
    # address card
    kk = pop(t, 15.3, .3)
    if kk > .03:
        c.save(); c.translate(x + 400, 1020); c.scale(kk, kk)
        rrect(c, -200, -70, 400, 140, 16); fs(c, (1, 1, 1), 6)
        poly(c, [(-150, -30), (-120, 30), (-90, -30)]); c.arc(-120, -34, 30, math.pi, 2 * math.pi); fs(c, hx('#D7141A'), 4)
        ell(c, -120, -34, 10, 10); fill(c, (1, 1, 1))
        text(c, "ALAMAT PEMESAN", 40, -22, 24, OUT); text(c, "Jl. Merdeka No. 8", 40, 22, 26, hx('#1F4E99'))
        c.restore()

def cam_berangkat(t):
    k = clamp((t - 13.6) / 5.4); x = lerp(-900, 1800, k) + 430
    return (x, 1150, .8)

def sc_reveal(c, t, t0):
    car = {'x': -60, 'y': 1640, 'driver': False}
    people = [{'who': 'rahmat', 'x': 820, 'y': 1660, 'aF': (170, -150) if t > 20.3 else (40, 10), 'aB': (170, -150) if t > 20.3 else (20, 0),
               'eyes': 'wide' if t > 20.2 else 'open', 'expr': 'o', 'brows': 'up', 'look': (6, -6)},
              {'who': 'burahmat', 'x': 1000, 'y': 1660, 'aF': (150, -80) if t > 20.3 else (30, 10), 'eyes': 'wide' if t > 20.2 else 'open', 'expr': 'o', 'look': (4, -6)}]
    dapur_mbg(c, t, {'car': car, 'front': people})

def sc_salaman(c, t, t0):
    shake = 6 * math.sin(t * 14)
    people = [{'who': 'rahmat', 'x': 820, 'y': 1660, 'aF': (100, -10 + shake), 'expr': 'grin', 'eyes': 'happy'},
              {'who': 'kadapur', 'x': 1060, 'y': 1660, 'flip': True, 'aF': (100, -10 + shake), 'aB': (110, -70), 'expr': 'grin', 'mouth': talk(t, [(25.6, 28.1)]) * .6},
              {'who': 'burahmat', 'x': 620, 'y': 1660, 'aF': (60, 40), 'expr': 'grin'}]
    dapur_mbg(c, t, {'car': {'x': -260, 'y': 1640}, 'front': people})

def sc_periksa(c, t, t0):
    dapur_mbg(c, t, {'car': {'x': -260, 'y': 1640}, 'front': [
        {'who': 'kadapur', 'x': 1060, 'y': 1660, 'flip': True, 'aF': (120, -40), 'expr': 'smile', 'look': (-4, 4)},
        {'who': 'rahmat', 'x': 820, 'y': 1660, 'aF': (40, -100), 'aB': (40, -100), 'expr': 'smile'}]})

def sc_muat(c, t, t0):
    # driving with load from left to dapur
    if t < 35.0:
        k = eout((t - 32.0) / 3.0); x = lerp(-1300, 300, k); moving = True
    else:
        x = 300; moving = False
    pitch = .028 * ease((t - 34.4) / .6) if t < 35.0 else .028 * math.exp(-5 * (t - 35.0)) * math.cos(13 * (t - 35.0))
    unload = t > 36.2
    front = []
    if unload:
        def sackh(c, hnd): sack(c, hnd[0] + 10, hnd[1] - 50, 110, 70)
        front = [{'who': 'koki2', 'x': lerp(1250, 1450, clamp((t - 36.2) / 1.5)), 'y': 1680, 'aF': (165, -10), 'aB': (165, -10), 'step': 1, 'hold': sackh, 'expr': 'grin'},
                 {'who': 'rahmat', 'x': 1160, 'y': 1680, 'aF': (120, -30), 'expr': 'grin', 'flip': False}]
    dapur_mbg(c, t, {'cooks': True, 'car': {'x': x, 'y': 1640, 'load': True, 'driver': not unload, 'moving': moving, 'pitch': pitch, 'sticker': True,
                                         'ang': (x + 1300) / 62, 'dpo': {'aF': (110, 20), 'expr': 'grin'}}, 'front': front})
    for (lbl, ta, dx, dy, col) in (("BERAS", 34.48, 200, -420, '#2E6BD6'), ("TELUR", 35.06, 520, -440, '#F07D2B'), ("MINYAK", 35.6, 60, -480, '#E5A23B')):
        k = pop(t, ta, .3)
        if k > .03:
            c.save(); c.translate(x + dx, 1640 + dy); c.scale(k, k)
            rrect(c, -90, -34, 180, 68, 34); fs(c, hx(col), 5)
            text(c, lbl, 0, 0, 34, (1, 1, 1), OUT, 5)
            c.restore()

def cam_muat(t):
    if t < 35.0:
        k = eout((t - 32.0) / 3.0); x = lerp(-1300, 300, k) + 430
        return (x, 1170, .95)
    return (lerp(730, 900, ease((t - 35.0) / 3)), 1170, .95)

def sc_dulu_kini(c, t, t0):
    # top sepia: toko 1 kg
    c.save(); c.rectangle(0, 0, W, H / 2); c.clip()
    c.translate(W / 2, H / 4); c.scale(.62, .62); c.translate(-1150, -1100)
    E.street(c, t, {'tod': 'day', 'toko': 'normal'})
    person(c, 1220, 1420, 'rahmat', {'aF': (100, -20), 'expr': 'smile'}, t=t)
    person(c, 1500, 1420, 'b2', {'flip': True, 'aF': (90, -10), 'expr': 'smile'}, t=t)
    rrect(c, 1320, 1170, 70, 60, 6); fs(c, (1, 1, 1), 3, .8); text(c, "1 KG", 1355, 1200, 18, OUT)
    c.restore()
    c.save(); c.rectangle(0, 0, W, H / 2); c.clip(); c.set_source_rgba(.45, .32, .15, .45); c.paint(); c.restore()
    # bottom: kids eating
    c.save(); c.rectangle(0, H / 2, W, H / 2); c.clip()
    c.translate(W / 2, H * .75); c.scale(.8, .8); c.translate(-600, -1560)
    kelas(c, t)
    c.restore()
    c.rectangle(0, H / 2 - 8, W, 16); fill(c, (1, 1, 1))
    for (lbl, y, col, ta) in (("DULU", 110, hx('#D9B98A'), 38.1), ("SEKARANG", H / 2 + 110, hx('#FFE14D'), 40.6)):
        k = pop(t, ta, .3)
        if k > .03:
            c.save(); c.translate(W / 2 - 30, y); c.scale(k, k)
            c.select_font_face("Inter Black"); c.set_font_size(62)
            w = c.text_extents(lbl).width + 70
            rrect(c, -w / 2, -48, w, 96, 24); fs(c, col, 8); text(c, lbl, 0, 0, 62, OUT)
            c.restore()

def st_julit(t):
    shock = t >= 44.9
    locked = t >= 49.3
    m = 0.9 if shock and not locked else 0
    return {'tod': 'day', 'toko': 'normal',
            'car': {'x': 760, 'y': 1620, 'load': True, 'sticker': True},
            'people': [{'who': 'friend', 'x': 2330, 'y': 1420, 'flip': True, 'aF': (170, -150) if shock else (60, 80), 'expr': 'o' if not locked else 'grin', 'eyes': 'wide' if shock and not locked else 'happy'},
                       {'who': 'julit', 'x': 2080, 'y': 1420, 'flip': True, 'aF': (170, -160) if shock and not locked else (38, -100), 'aB': (38, -100),
                        'mouth': m, 'expr': 'o' if not locked else 'flat', 'eyes': 'wide' if shock else 'squint', 'look': (-6, 0)}]}

def draw_car3_street(c, t, st):
    # E.street draws its own car via E.draw_car; we need sticker+load -> wrap
    pass

def sc_julit(c, t, t0):
    st = st_julit(t)
    car = st.pop('car')
    st['pre_car'] = [lambda c: draw_car3(c, t, car)]
    E.street(c, t, st)
    if t >= 44.9:
        sweat(c, 1990, 1000, 1.1)
    if t >= 49.3:
        k = pop(t, 49.3, .3)
        if k > .03:
            gembok(c, 2068, 1092, 1.25 * k)
            c.save(); c.translate(2030, 1080)
            for j in range(5):
                c.move_to(-46 + j * 22, -4); c.line_to(-36 + j * 22, 10); c.set_source_rgb(*hx('#9AA1A9')); c.set_line_width(5); c.stroke()
            c.restore()

def sc_tawaran(c, t, t0):
    kantor(c, t)
    person(c, 300, 1500, 'rahmat', {'aF': (100, -30), 'eyes': 'wide' if t > 52.4 else 'open', 'expr': 'o' if t > 52.4 else 'smile', 'look': (6, 0)}, s=1.1, t=t)
    person(c, 820, 1500, 'kadapur', {'flip': True, 'aF': (100, -20), 'aB': (40, 0), 'expr': 'grin', 'mouth': .3 * abs(math.sin(t * 9)) if t < 54 else 0}, s=1.1, t=t)
    kk = eout((t - 51.0) / .4)
    if kk > 0: kontrak(c, 560, lerp(1500, 860, kk), .95, t, 53.0)

def sc_sanggup(c, t, t0):
    g = cairo.LinearGradient(0, 0, 0, 1900)
    g.add_color_stop_rgb(0, *hx('#1E2A5A')); g.add_color_stop_rgb(1, *hx('#F29E6B'))
    c.set_source(g); c.rectangle(-1000, -1000, 3080, 4000); c.fill()
    person(c, 540, 1620, 'rahmat', {'aF': (172, -168 + 10 * math.sin(t * 14)), 'aB': (38, -100), 'eyes': 'wide', 'expr': 'o', 'brows': 'up'}, s=1.45, t=t)
    alarm(c, 860, 560, .9, t)
    # long list scroll
    c.save(); c.translate(230, 560); c.rotate(-.05)
    rrect(c, -150, -200, 300, 400, 8); fs(c, (1, 1, 1), 5)
    text(c, "PASOKAN BESOK", 0, -165, 22, OUT)
    for i, l_ in enumerate(["Beras 500 kg", "Telur 300 kg", "Minyak 200 L", "Sayur ...", "Buah ...", "Gula ...", "...?"]):
        text(c, l_, -125, -120 + i * 44, 22, OUT, font="Inter", align='l')
    c.restore()
    for k in range(5):
        a = t * 1.4 + k * 1.25
        text(c, "?", 540 + 430 * math.cos(a), 420 + 170 * math.sin(a), 80, hx('#FFE14D'), OUT, 9)
    if t >= 57.1:
        k = pop(t, 57.1, .35)
        c.set_source_rgba(0, 0, 0, .5 * clamp((t - 57.1) / .3)); c.paint()
        c.save(); c.translate(W / 2 - 30, 900); c.scale(k, k); c.rotate(-.05)
        rrect(c, -380, -100, 760, 200, 24); fs(c, hx('#FFE14D'), 10)
        text(c, "BERSAMBUNG...", 0, 0, 84, OUT)
        c.restore()

SCENES = [
 (0.0, 2.8, sc_hook, [(0, 380, 1000, 1.8), (0.6, 400, 1000, 1.85), (1.7, 560, 1000, 1.0), (2.8, 560, 990, 1.02)]),
 (2.8, 5.9, sc_nota, [(2.8, 560, 960, 1.0), (5.9, 560, 940, 1.1)]),
 (5.9, 8.5, sc_bangkrut, [(5.9, 540, 1000, 1.0), (8.5, 540, 980, 1.08)]),
 (8.5, 13.6, sc_istri, [(8.5, 520, 1050, 1.15), (13.6, 520, 1000, 1.0)]),
 (13.6, 19.0, sc_berangkat, None),
 (19.0, 25.6, sc_reveal, [(19.0, 900, 1300, 1.3), (20.4, 1050, 1080, .78), (25.6, 1060, 1090, .8)]),
 (25.6, 28.6, sc_salaman, [(25.6, 880, 1180, 1.05), (28.6, 880, 1180, 1.1)]),
 (28.6, 32.0, sc_periksa, [(28.6, 880, 1180, 1.05), (32.0, 880, 1180, 1.08)]),
 (32.0, 38.05, sc_muat, None),
 (38.05, 43.85, sc_dulu_kini, 'split'),
 (43.85, 50.6, sc_julit, [(43.85, 1650, 1080, .78), (44.9, 2080, 1020, 1.6), (49.2, 2080, 1040, 1.8), (50.6, 2080, 1040, 1.85)]),
 (50.6, 54.85, sc_tawaran, [(50.6, 560, 1050, .95), (54.85, 560, 1000, 1.05)]),
 (54.85, DUR + 1, sc_sanggup, [(54.85, 540, 1000, .95), (57.1, 540, 980, 1.05), (DUR, 540, 980, 1.08)]),
]

def tod_at(t):
    if 13.6 <= t < 19.0: return 'morning'
    if 19.0 <= t < 38.05 or 38.05 <= t < 50.6: return 'day'
    if 54.85 <= t: return 'sore'
    return 'indoor'
P.tod_at = tod_at
P.GRADE.setdefault('indoor', (.92, .99, 1.06))

# ------------------------------------------------------------ overlays (calm)
def captions_safe(c, t, base_y=1330, cx=490, maxw=840):
    for ci, ch in enumerate(CHUNKS):
        a = ch[0][1] - 0.05
        b = CHUNKS[ci + 1][0][1] - 0.05 if ci + 1 < len(CHUNKS) else VDUR
        b = min(b, ch[-1][2] + 0.6)
        if not (a <= t < b): continue
        k = eout((t - a) / .16)
        size = 100
        c.select_font_face("Inter Black"); c.set_font_size(size)
        strs = [w[0].upper() for w in ch]
        sp = c.text_extents(" ").x_advance
        tot = sum(c.text_extents(s).x_advance for s in strs) + sp * (len(strs) - 1)
        if tot > maxw:
            size *= maxw / tot; c.set_font_size(size); sp = c.text_extents(" ").x_advance
            tot = sum(c.text_extents(s).x_advance for s in strs) + sp * (len(strs) - 1)
        c.save(); c.translate(cx, base_y + 40 * (1 - k)); c.rotate(-0.02)
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

def hook(c, t):
    if t >= 1.9: return
    k = max(pop(t, .1, .25), .02)
    a = clamp((1.9 - t) / .25)
    c.save(); c.translate(W / 2 - 40, 520); c.scale(k, k); c.rotate(-.1)
    c.push_group()
    rrect(c, -380, -120, 760, 240, 26); fs(c, hx('#D7141A'), 12)
    text(c, "KENA TIPU?!", 0, 0, 110, (1, 1, 1), OUT, 14)
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()

def cta(c, t):
    if t < VDUR + .2: return
    d = t - (VDUR + .2)
    c.set_source_rgba(.04, .01, .03, min(.92, d * 4)); c.paint()
    k = max(pop(t, VDUR + .25, .35), .02)
    c.save(); c.translate(W / 2 - 30, 640); c.scale(k, k)
    rrect(c, -400, -170, 800, 340, 34); fs(c, (1, 1, 1), 10)
    text(c, "SANGGUP NGGAK?", 0, -105, 54, OUT)
    for i, (lbl, col) in enumerate((("SANGGUP!", '#2EAD6B'), ("KEWALAHAN", '#D7141A'))):
        c.save(); c.translate(-190 + i * 380, 30); c.rotate(.04 * math.sin(t * 6 + i * 2))
        rrect(c, -170, -70, 340, 140, 26); fs(c, hx(col), 8)
        text(c, lbl, 0, 0, 46, (1, 1, 1), OUT, 6)
        c.restore()
    c.restore()
    k2 = pop(t, VDUR + .7, .3)
    if k2 > .03:
        c.save(); c.translate(W / 2 - 30, 920); c.scale(k2, k2)
        text(c, "Tulis jawabanmu di komentar!", 0, 0, 46, (1, 1, 1), OUT, 8)
        c.restore()
    k3 = pop(t, VDUR + 1.1, .35)
    if k3 > .03:
        c.save(); c.translate(W / 2 - 30, 1110); c.scale(k3, k3); c.rotate(-.03)
        rrect(c, -330, -70, 660, 140, 70); fs(c, hx('#FFE14D'), 9)
        text(c, "FOLLOW UNTUK EP 4", -30, 0, 52, OUT)
        bx = 260 + 10 * math.sin(t * 8)
        poly(c, [(bx - 22, -26), (bx + 20, 0), (bx - 22, 26)]); fs(c, OUT, 2)
        c.restore()

def watermark(c, t):
    c.save(); c.translate(40, 215)
    rrect(c, 0, -26, 410, 52, 26); fill(c, (0, 0, 0), .32)
    ell(c, 30, 0, 16, 16); fill(c, hx('#D8312B'), .95)
    text(c, "PAK RAHMAT SERIES • EP 3", 56, 0, 24, (1, 1, 1), align='l', alpha=.92)
    c.restore()

def render(fi):
    t = fi / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    sc = next(s for s in SCENES if s[0] <= t < s[1])
    t0, t1, fn, keys = sc
    if keys == 'split':
        fn(c, t, t0)
    else:
        if keys is None:
            cx, cy, z = cam_berangkat(t) if fn is sc_berangkat else cam_muat(t)
        else:
            cx, cy, z = lib.cam_keys(keys, t)
        for p in (0.12, 44.9):
            if t >= p: z *= 1 + .07 * math.exp(-7 * (t - p))
        amp = 0
        for s in (0.12, 44.9):
            if 0 <= t - s < .3: amp = max(amp, 10 * (1 - (t - s) / .3))
        c.save(); c.translate(W / 2 + amp * math.sin(t * 97), H / 2 + amp * math.cos(t * 73)); c.scale(z, z); c.translate(-cx, -cy)
        fn(c, t, t0)
        c.restore()
    E.focus_lines(c, t, 0.1, 0.9, cy=H * .45)
    E.focus_lines(c, t, 20.3, 21.1, cy=H * .5)
    E.focus_lines(c, t, 44.9, 45.9, cy=H * .45)
    if 35.2 <= t < 36.6:
        pass
    P.post(surf, min(t, VDUR), 0.0)
    c = cairo.Context(surf)
    if 13.6 <= t < 15.2: E.pill(c, "BESOK PAGINYA...", t, 13.7, y=320, col=hx('#FFD08A'))
    if 20.3 <= t < 22.0:
        k = pop(t, 20.35, .3)
        if k > .03:
            c.save(); c.translate(W / 2 - 30, 520); c.scale(k, k); c.rotate(-.07)
            rrect(c, -330, -90, 660, 180, 24); fs(c, hx('#FFE14D'), 10)
            text(c, "LADALAH!", 0, 0, 100, OUT)
            c.restore()
    if 28.6 <= t < 32.0:
        kk = eout((t - 28.65) / .35)
        checklist(c, W / 2 - 30, lerp(2200, 820, kk), 1.0, t, 29.3)
    hook(c, t)
    gr = cairo.RadialGradient(W / 2, H / 2, H * .32, W / 2, H / 2, H * .78)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0); gr.add_color_stop_rgba(1, 0, 0, .04, .34)
    c.set_source(gr); c.paint()
    captions_safe(c, t)
    cta(c, t)
    watermark(c, t)
    if t < .25: c.set_source_rgba(0, 0, 0, 1 - t / .25); c.paint()
    if t > DUR - .3: c.set_source_rgba(0, 0, 0, clamp((t - (DUR - .3)) / .3)); c.paint()
    surf.flush()
    return bytes(surf.get_data())
