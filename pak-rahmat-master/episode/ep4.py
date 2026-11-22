"""PAK RAHMAT EP 4 - MAS DIO & NAMBAH ARMADA (68 dtk) - CONTOH EPISODE LENGKAP.
Hanya berisi adegan + pengaturan episode; gambar tetap ada di aset_*.py, gaya PRO PLUS di gaya.py.
Render: python3 jalankan.py 4 render  (lihat README.md)."""
from aset_dio import *          # W, H, hx, CH, street, rahmat_po, dio_po, pose_seq, brosur, card, ... + modul E, P, G, lib
import gaya

N = 4
VDUR = 65.3           # panjang narasi
DUR = 68.0            # + kartu penutup
HOOK = ("NYESEL BELI?!", 2.2)
PUNCH = (0.12, 56.82)
BERSAMBUNG = 64.28
CTA = dict(baris1="KENAPA PAK RAHMAT", baris2="HAMPIR MENYERAH?",
           pilihan=[("SEPI PEMBELI", '#2E6BD6'), ("MODAL HABIS", '#D7141A')])
SUASANA = [(59.15, 999, 'freeze'), (39.62, 43.25, 'morning'), (10.1, 23.35, 'tense'), (43.25, 50.95, 'tense'),
           (23.35, 39.62, 'warm'), (54.95, 59.15, 'warm')]

RAHMAT_SPEAK = [(14.05, 16.95), (26.95, 29.85), (46.6, 48.9), (51.1, 54.4)]
DIO_SPEAK = [(30.2, 33.3), (49.15, 50.5)]

def pale_k(t):
    if 17.9 <= t < 24.6: return min(eout((t - 17.9) / .7), 1 - ease((t - 23.6) / 1.0))
    if 45.4 <= t < 55.6: return .45 * min(ease((t - 45.4) / .6), 1 - ease((t - 55.1) / .5))
    return 0.0

def set_pale(t):
    return set_pucat(pale_k(t))

HOOK_D = [(0, (95, -10), (20, 0)), (2.3, (150, -150), (150, -150))]

# ------------------------------------------------------------ adegan
def sc_hook(c, t, t0):
    CH['dio']['skin'] = tuple(lerp(a, b, clamp((t - 2.3) / .5)) for a, b in zip(DIO_SKIN, PALE))
    m = .3 * abs(math.sin(t * 13)) if t > 2.3 else 0
    street(c, t, [rahmat_po(**SERIUS),
                  dio_po(aF=pose_seq(t, HOOK_D)[0], aB=pose_seq(t, HOOK_D)[1], eyes='wide' if t > 2.3 else 'open',
                         brows='up', expr='o' if t > 2.3 else 'grin', mouth=m, look=(-6, -2), tilt=4 * math.sin(t * 22) if t > 2.3 else 0)])
    if t > 2.3:
        gloom(c, POS_D, YS, 1.0, clamp((t - 2.4) / .4))
        sweat(c, POS_D - 90, 1040, 1.1); sweat(c, POS_D + 80, 1060, .9)
        exclaim(c, POS_D + 10, 880 - 10 * abs(math.sin(t * 8)), 1.0, pop(t, 2.35, .25))

def dio_walk_x(t):
    return lerp(-300, POS_D, ease((t - 4.35) / 4.6))

def sc_datang(c, t, t0):
    dx = dio_walk_x(t)
    walking = t < 8.9
    wave = t > 8.6
    dpo = dio_po(x=dx, step=1 if walking else 0, aF=tuple(lerp(p, q, backk(t, 8.6)) for p, q in zip((25 + 25 * math.sin(t * 9), 10), (160 + 18 * math.sin(t * 10), -40))),
                 aB=(-25 * math.sin(t * 9), 10), expr='grin' if wave else 'smile', eyes='happy' if wave else 'open', look=(6, 0),
                 hold=None if wave else brosur, flip=False if walking else True)
    look_up = t > 8.9
    rpo = rahmat_po(aF=(110, -20) if not look_up else (40, 10), aB=(110, -20) if not look_up else (-10, 10), look=(4, 6) if not look_up else (6, 0),
                    expr='smile', hold=(lambda c, h: lib.sack(c, h[0] + 10, h[1] - 30, 96, 60)) if not look_up else None)
    if PRO:
        rpo['aF'], rpo['aB'] = pose_seq(t, [(0, (110, -20), (110, -20)), (8.9, (40, 10), (-10, 10))])
    street(c, t, [rpo, dpo])
    if PRO and walking:
        for j in range(3):
            ph = (t * 1.6 + j / 3) % 1
            P.puff(c, dx - 30 - ph * 70, YS - 6 - ph * 24, 10 + ph * 18, .35 * (1 - ph))
    name_card(c, dx + 30, 900, pop(t, 5.5, .35) * (1 - ease((t - 8.4) / .3)))

def cam_datang(t):
    dx = dio_walk_x(t)
    k = ease((t - 8.6) / 1.4)
    return (lerp(max(dx + 120, 700), 1190, k), lerp(1150, 1180, k), lerp(1.0, 1.25, k))

def sc_serius(c, t, t0):
    serius = t > 11.7
    hand = t < 12.4
    rpo = rahmat_po(**SERIUS) if serius else rahmat_po(aF=(60, 0), aB=(-10, 10), expr='smile', look=(6, 0))
    dpo = dio_po(aF=(95, -5) if hand else (20, 10), aB=(20, 0), expr='grin' if not serius else ('smile' if t < 12.6 else 'o'),
                 eyes='happy' if t < 11.0 else ('open' if t < 12.6 else 'wide'), look=(-6, 0), brows='up' if t > 12.6 else 'normal')
    if PRO:
        rpo['aF'], rpo['aB'] = pose_seq(t, [(0, (60, 0), (-10, 10)), (11.7, SERIUS['aF'], SERIUS['aB'])])
        dpo['aF'] = pose_seq(t, [(0, (95, -5), (20, 0)), (12.4, (20, 10), (20, 0))])[0]
    street(c, t, [rpo, dpo])
    if t > 12.6:
        sweat(c, POS_D - 80, 1050, .9)

def sc_nyesel(c, t, t0):
    m = talk(t, RAHMAT_SPEAK)
    rpo = rahmat_po(aF=(92, -6), aB=(-40, 100), eyes='squint', brows='angry', expr='flat', mouth=m, look=(6, 0))
    dpo = dio_po(aF=(20, 10), aB=(20, 0), expr='o', eyes='wide', brows='up', look=(-6, 0))
    street(c, t, [rpo, dpo])
    sweat(c, POS_D - 80, 1050, .9)

def sc_pucat(c, t, t0):
    pk = set_pale(t)
    scratch = 19.3 <= t < 21.5
    po = dict(aF=(160, 60 + 14 * math.sin(t * 16)) if scratch else (150, -150), aB=(20, 0) if scratch else (150, -150),
              eyes='wide', brows='up', expr='o' if t < 19.3 else 'frown', mouth=.25 * abs(math.sin(t * 11)) if t < 18.0 else 0,
              look=(-4, -2), tilt=3 * math.sin(t * 24) if t < 19.3 else 0)
    if PRO:
        a = pose_seq(t, [(0, (150, -150), (150, -150)), (19.3, (160, 60), (20, 0)), (21.5, (150, -150), (150, -150))])
        po['aF'] = (a[0][0], a[0][1] + (14 * math.sin(t * 16) if scratch else 0)); po['aB'] = a[1]
    street(c, t, [rahmat_po(**SERIUS), dio_po(**po)])
    gloom(c, POS_D, YS, 1.0, pk)
    for k in range(2):
        sweat(c, POS_D - 85 + k * 170, 1030 + ((t * 90 + k * 60) % 110), 1.0)
    if t > 21.6:
        tail = (POS_D - 20, 940)
        k = pop(t, 21.62, .35)
        if bubble(c, 1250, 600, 560, 320, k, tail):
            c.save(); c.translate(1250, 600); c.scale(k, k)
            c.save(); c.translate(-150, 120); c.rotate(-.05)
            lib.gran_max(c, 0, 0, t, 0, False, 0, cargo=False, s=.33)
            c.restore()
            smoke(c, 110, 0, t, 5, 1.1)
            # flat tyre squiggle
            c.move_to(-70, 118); c.curve_to(-60, 128, -40, 128, -30, 118); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
            text(c, "MOGOK?", -40, -100, 50, hx('#D7141A'), OUT, 0)
            k2 = pop(t, 22.4, .25)
            if k2 > .03:
                c.save(); c.translate(200, -70); c.scale(k2, k2); c.rotate(.15)
                text(c, "?!", 0, 0, 90, hx('#FFE14D'), OUT, 9)
                c.restore()
            c.restore()

def sc_tertawa(c, t, t0):
    set_pale(t)
    laugh = 24.4 <= t < 27.0
    thumb = t >= 28.45
    m = talk(t, RAHMAT_SPEAK)
    if laugh:
        rpo = rahmat_po(aF=(12, 200), aB=(70, -20), eyes='happy', expr='grin', mouth=.35 + .35 * abs(math.sin(t * 14)), tilt=-8 + 3 * math.sin(t * 14))
    elif thumb:
        rpo = rahmat_po(aF=(165, -60), aB=(-10, 10), eyes='happy', expr='grin', mouth=m, thumb=True)
    elif t >= 26.95:
        rpo = rahmat_po(aF=(70, -20), aB=(-10, 10), eyes='open', expr='grin', mouth=m, look=(6, 0))
    else:
        rpo = rahmat_po(**SERIUS)
    if PRO:
        rpo['aF'], rpo['aB'] = pose_seq(t, [(0, SERIUS['aF'], SERIUS['aB']), (24.4, (12, 200), (70, -20)), (26.95, (70, -20), (-10, 10)),
                                            (28.45, (165, -60), (-10, 10))])
    confused = t > 24.6
    dpo = dio_po(aF=(30, 10), aB=(20, 0), eyes='open' if confused else 'wide', brows='up', expr='o' if t < 24.6 else 'flat', look=(-6, -1),
                 tilt=-6 if confused else 0)
    street(c, t, [rpo, dpo])
    gloom(c, POS_D, YS, 1.0, pale_k(t))
    if laugh:
        for j, ta in enumerate((24.5, 25.0, 25.5, 26.0)):
            k = pop(t, ta, .25)
            if k > .03:
                c.save(); c.translate(POS_R - 150 + j * 70 + 8 * math.sin(t * 12 + j), 880 - j * 46); c.scale(k, k); c.rotate(-.15 + j * .1)
                text(c, "HA", 0, 0, 62, hx('#FFE14D'), OUT, 8); c.restore()
    if 24.8 < t < 27.4: tanya(c, POS_D, 860, t, 24.8, .7, 2)
    if thumb:
        d = t - 28.5
        for j in range(8):
            a = j * math.pi / 4 + d
            spark(c, POS_R + 130 + 110 * math.cos(a), 900 + 80 * math.sin(a), 18 * max(0, 1 - d / 1.2), max(0, 1 - d / 1.2))

def sc_lega(c, t, t0):
    m = talk(t, DIO_SPEAK)
    dpo = dio_po(aF=(20, 190), aB=(10, 0) if t < 31.8 else (150, -40), eyes='closed' if t < 31.0 else 'happy', expr='grin', mouth=m,
                 tilt=6 * math.sin(t * 2), look=(-6, 0))
    rpo = rahmat_po(aF=(12, 200), aB=(70, -20), eyes='happy', expr='grin', mouth=.2 + .25 * abs(math.sin(t * 12)), tilt=-5)
    if PRO: dpo['aB'] = pose_seq(t, [(0, (0, 0), (10, 0)), (31.8, (0, 0), (150, -40))])[1]
    street(c, t, [rpo, dpo])
    if t < 31.4:   # fiuuh
        k = pop(t, 30.3, .3)
        if k > .03:
            c.save(); c.translate(POS_D - 170, 980); c.scale(k, k)
            for j in range(3):
                c.move_to(0, j * 26); c.curve_to(-40, j * 26 - 20, -70, j * 26 + 10, -110, j * 26 - 6)
                c.set_source_rgba(1, 1, 1, .9); c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
            c.restore()
    k = pop(t, 32.35, .35)
    if k > .03 and t < 34.1:
        card(c, 1190, 700, k, "PENSIUN DINI?!", hx('#D7141A'), 66, (1, 1, 1), rot=.06)

def sc_rame(c, t, t0):
    busy = lambda ph: (120 + 40 * math.sin(t * 7 + ph), -40)
    people = [{'who': 'rahmat', 'x': 1040, 'y': 1370, 'aF': busy(0), 'aB': (90, -20), 'expr': 'grin', 'look': (5, 4)},
              {'who': 'burahmat', 'x': 1290, 'y': 1370, 'flip': True, 'aF': busy(2), 'aB': (90, -20), 'expr': 'grin', 'look': (-5, 4)}]
    q = [('b2', 1165, 34.2), ('b1', 760, 34.2), ('b4', 1560, 34.2), ('anak', 590, 37.85), ('friend', 1740, 37.85), ('b3', 420, 38.3)]
    front = []
    for i, (who, x, ta) in enumerate(q):
        if t < ta: continue
        k = eout((t - ta) / .5)
        xx = lerp(x + (-500 if x < 1200 else 500), x, k)
        flip = x > 1200
        front.append({'who': who, 'x': xx, 'y': 1540 if i == 0 else 1480, 'flip': flip, 'step': 1 if k < 1 else 0,
                      'aF': (100, -20) if i % 2 else (40, 10), 'expr': 'smile', 'look': (-5 if flip else 5, -2), 's': .9 if i == 0 else .95})
    street(c, t, people, front=front)
    # MBG order sheet pinned on the pillar
    k = pop(t, 35.5, .35)
    if k > .03:
        c.save(); c.translate(1700, 900); c.scale(k, k); c.rotate(.05)
        rrect(c, -130, -160, 260, 320, 8); fs(c, (1, 1, 1), 6)
        c.rectangle(-130, -160, 260, 70); fill(c, hx('#1F4E99'))
        text(c, "PESANAN", 0, -140, 26, (1, 1, 1)); text(c, "DAPUR MBG", 0, -108, 30, hx('#FFE14D'))
        for j in range(4):
            yy = -50 + j * 52
            c.move_to(-100, yy); c.line_to(-88, yy + 14); c.line_to(-66, yy - 10); c.set_source_rgb(*hx('#2EAD6B')); c.set_line_width(7); c.stroke()
            c.rectangle(-50, yy - 4, 140 - (j % 2) * 30, 8); fill(c, (0, 0, 0), .3)
        ell(c, 0, -170, 12, 12); fs(c, hx('#D7141A'), 3)
        c.restore()
    for j, ta in enumerate((35.0, 36.3, 37.2, 38.2, 38.9)):
        coin_pop(c, 1000 + j * 70, 1050, t, ta)
    if t > 37.9:
        card(c, 1170, 640, pop(t, 37.95, .3), "RAME!", hx('#FFE14D'), 80, rot=.06)

DAYS = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU"]
DAY_T0 = 39.62; DAY_DT = .6

def sc_antar(c, t, t0):
    i = int(clamp((t - DAY_T0) / DAY_DT, 0, len(DAYS) - .001))
    ph = clamp((t - (DAY_T0 + i * DAY_DT)) / DAY_DT)
    x = lerp(-900, 2000, ph)
    car = {'x': x, 'y': 1620, 'load': True, 'sticker': True, 'driver': True, 'moving': True, 'ang': x / 62,
           'dpo': {'aF': (110, 20), 'expr': 'grin', 'eyes': 'happy' if i % 2 else 'open'}}
    st = {'tod': 'morning' if i % 2 == 0 else 'day', 'toko': 'normal', 'people': watchers(t, x) if PRO else [], 'pre_car': [lambda c: G.draw_car3(c, t, car)]}
    E.street(c, t, st)
    for j in range(3):
        yy = 1220 + j * 120
        c.move_to(x - 120 - j * 40, yy); c.line_to(x - 420 - j * 40, yy); c.set_source_rgba(1, 1, 1, .7); c.set_line_width(8); c.stroke()

def sc_masalah(c, t, t0):
    set_pale(t)
    m = talk(t, RAHMAT_SPEAK); md = talk(t, DIO_SPEAK)
    if t < 44.5:
        rpo = rahmat_po(aF=(70, -20), aB=(-10, 10), expr='grin', eyes='happy', look=(6, 0))
    else:
        rpo = rahmat_po(**dict(SERIUS, mouth=m))
    if t < 45.4:
        dpo = dio_po(aF=(165, -60), aB=(20, 0), expr='grin', eyes='happy', thumb=True, look=(-6, 0))
    elif t < 49.15:
        dpo = dio_po(aF=(20, 10), aB=(20, 0), expr='flat' if t < 46.6 else 'o', eyes='open' if t < 46.6 else 'wide', brows='up', look=(-6, 0))
    else:
        dpo = dio_po(aF=(100, -15), aB=(60, -60), expr='o', mouth=md, eyes='wide', brows='up', look=(-6, -2))
    if PRO:
        rpo['aF'], rpo['aB'] = pose_seq(t, [(0, (70, -20), (-10, 10)), (44.5, SERIUS['aF'], SERIUS['aB'])])
        dpo['aF'], dpo['aB'] = pose_seq(t, [(0, (165, -60), (20, 0)), (45.4, (20, 10), (20, 0)), (49.15, (100, -15), (60, -60))])
    street(c, t, [rpo, dpo])
    gloom(c, POS_D, YS, 1.0, pale_k(t))
    if t > 45.5: sweat(c, POS_D - 80, 1040, .9)
    if t > 49.8: tanya(c, POS_D, 860, t, 49.85, .8, 3)

def sc_satu(c, t, t0):
    # background: the warung, dimmed
    c.save(); c.translate(W / 2, H / 2); c.scale(1.05, 1.05); c.translate(-1190, -1180)
    street(c, t, [rahmat_po(aF=(170, -20), aB=(-40, 100), eyes='open', brows='up', expr='frown', mouth=talk(t, RAHMAT_SPEAK), thumb=True, look=(4, -2)),
                  dio_po(aF=(20, 10), aB=(20, 0), expr='o', eyes='wide', brows='up', look=(-6, -2))])
    c.restore()
    k = eout((t - 51.0) / .35)
    c.set_source_rgba(.05, .06, .12, .55 * k); c.paint()
    if k <= .02: return
    c.save(); c.translate(W / 2 - 30, lerp(1400, 760, k))
    rrect(c, -440, -330, 880, 640, 34); fs(c, (1, 1, 1), 10)
    c.move_to(0, -280); c.line_to(0, 280); c.set_source_rgba(0, 0, 0, .15); c.set_line_width(4); c.set_dash([14, 10]); c.stroke(); c.set_dash([])
    # left: one car
    text(c, "MOBIL", -220, -270, 40, hx('#1F2F6B'))
    c.save(); c.translate(-370, 160); lib.gran_max(c, 0, 0, t, 0, False, 0, cargo=False, s=.33); c.restore()
    kk = pop(t, 51.9, .3)
    if kk > .03:
        c.save(); c.translate(-220, -130); c.scale(kk, kk)
        ell(c, 0, 0, 74, 74); fs(c, hx('#D7141A'), 8); text(c, "1", 0, 4, 100, (1, 1, 1), OUT, 8)
        c.restore()
    # right: orders pile up
    text(c, "PESANAN", 220, -270, 40, hx('#1F2F6B'))
    n = int(clamp((t - 53.2) / 1.2) * 14) + 3
    for i in range(n):
        r, col = i // 4, i % 4
        E.paket(c, 100 + col * 80 + (r % 2) * 40, 250 - r * 92, .72)
    if PRO:
        for j in range(7):
            d = t - (53.15 + j * .2)
            if 0 <= d < .55:
                u = eout(d / .55)
                c.save(); c.translate(lerp(520, 180 + (j % 4) * 70, u), lerp(-330 + j * 30, 120 - (j // 4) * 90, u) - 120 * math.sin(math.pi * u))
                c.rotate(4 * d + j); rrect(c, -36, -46, 72, 92, 4); fs(c, (1, 1, 1), 3)
                for q in range(4): c.rectangle(-26, -30 + q * 16, 52, 5); fill(c, (0, 0, 0), .3)
                c.restore()
    kk = pop(t, 53.4, .3)
    if kk > .03:
        c.save(); c.translate(380, -150); c.scale(kk, kk); c.rotate(-.1)
        poly(c, [(0, -70), (50, -10), (20, -10), (20, 60), (-20, 60), (-20, -10), (-50, -10)]); fs(c, hx('#D7141A'), 6)
        c.restore()
    c.restore()

def sc_armada(c, t, t0):
    set_pale(t)
    happy = t >= 56.2
    m = talk(t, DIO_SPEAK)
    dpo = dio_po(aF=(165, -60) if happy else (150, -150), aB=(30, -40) if happy else (150, -150), thumb=happy, expr='grin' if happy else 'o',
                 eyes='happy' if happy else 'wide', brows='up' if not happy else 'normal', look=(-6, 0))
    rpo = rahmat_po(aF=(70, -20), aB=(-10, 10), expr='grin', eyes='happy' if t > 57.4 else 'open', look=(6, 0))
    crowd = []
    if PRO:
        dpo['aF'], dpo['aB'] = pose_seq(t, [(0, (150, -150), (150, -150)), (56.2, (165, -60), (30, -40))])
        if t > 56.9:
            wv = 10 * math.sin(t * 12)
            crowd = [{'who': 'burahmat', 'x': 1600, 'y': 1430 + 60 * (1 - eout((t - 56.9) / .35)), 'flip': True, 'aF': (165 + wv, -20), 'aB': (165 - wv, -20),
                      'expr': 'grin', 'eyes': 'happy', 'mouth': .3 * abs(math.sin(t * 10))}]
    street(c, t, [rpo, dpo] + crowd)
    if happy:
        d = t - 56.25
        for j in range(10):
            a = j * math.pi / 5 + d * .8
            spark(c, POS_D + 160 * math.cos(a), 1000 + 120 * math.sin(a), 22 * max(0, 1 - d / 1.6), max(0, 1 - d / 1.6))
        k = pop(t, 56.85, .35)
        if bubble(c, 1190, 600, 760, 380, k, (POS_D - 40, 930)):
            c.save(); c.translate(1190, 600); c.scale(k, k)
            c.save(); c.translate(-350, 120); lib.gran_max(c, 0, 0, t, 0, False, 0, cargo=False, s=.3); c.restore()
            c.save(); c.translate(40, 120); lib.gran_max(c, 0, 0, t, 0, False, 0, cargo=False, s=.3); c.restore()
            ribbon(c, 170, -40, .55, t)
            k2 = pop(t, 57.25, .3)
            if k2 > .03:
                c.save(); c.translate(-10, -110); c.scale(k2, k2); text(c, "+1", 0, 0, 92, hx('#2EAD6B'), OUT, 9); c.restore()
            c.restore()

def sc_dulu(c, t, t0):
    people = [{'who': 'rahmat', 'x': 1120, 'y': 1400, 'sit': True, 'aF': (150, -150), 'aB': (150, -150), 'eyes': 'half', 'expr': 'frown',
               'brows': 'up', 'tilt': 12, 'look': (0, 6)}]
    street(c, t, people, tod='night', toko='kosong', shutter=.55, car=False)
    # 'TUTUP' card on shutter
    c.save(); c.translate(1170, 900); c.rotate(.06 + .03 * math.sin(t * 1.5))
    c.move_to(-60, -80); c.line_to(0, -130); c.line_to(60, -80); c.set_source_rgb(*OUT); c.set_line_width(3); c.stroke()
    rrect(c, -110, -80, 220, 100, 6); fs(c, hx('#C98B4A'), 5); text(c, "TUTUP", 0, -30, 46, hx('#5A1E10'))
    c.restore()

def day_card(c, t):
    if not (DAY_T0 <= t < 43.25): return
    i = int(clamp((t - DAY_T0) / DAY_DT, 0, len(DAYS) - .001))
    ta = DAY_T0 + i * DAY_DT
    k = pop(t, ta, .2)
    c.save(); c.translate(W / 2 - 30, 470); c.rotate(-.04)
    rrect(c, -220, -150, 440, 300, 20); fs(c, (1, 1, 1), 9)
    c.rectangle(-220, -150, 440, 80); fill(c, hx('#D7141A')); rrect(c, -220, -150, 440, 300, 20); c.set_source_rgb(*OUT); c.set_line_width(9); c.stroke()
    for sgn in (-1, 1):
        rrect(c, sgn * 110 - 10, -175, 20, 50, 8); fs(c, hx('#9AA1A9'), 4)
    text(c, "ANTAR BARANG", 0, -110, 30, (1, 1, 1))
    c.save(); c.translate(0, 40); c.scale(1, k); text(c, DAYS[i], 0, 0, 92, OUT); c.restore()
    c.restore()

SCENES = [
 (0.0, 4.35, sc_hook, [(0, 1190, 1170, 1.75), (0.6, 1190, 1180, 1.65), (2.2, 1210, 1170, 1.6), (2.6, 1350, 1110, 1.95), (4.35, 1350, 1110, 2.0)]),
 (4.35, 10.1, sc_datang, cam_datang),
 (10.1, 14.0, sc_serius, [(10.1, 1190, 1190, 1.25), (11.7, 1190, 1190, 1.3), (12.4, 1080, 1160, 1.65), (14.0, 1070, 1150, 1.7)]),
 (14.0, 17.22, sc_nyesel, [(14.0, 1150, 1170, 1.4), (17.22, 1170, 1170, 1.48)]),
 (17.22, 23.35, sc_pucat, [(17.22, 1350, 1100, 1.85), (19.3, 1350, 1100, 1.95), (21.4, 1350, 1100, 1.95), (22.0, 1270, 980, 1.1), (23.35, 1270, 980, 1.12)]),
 (23.35, 30.2, sc_tertawa, [(23.35, 1190, 1180, 1.3), (24.3, 1190, 1180, 1.35), (26.9, 1150, 1170, 1.45), (28.4, 1110, 1160, 1.6), (30.2, 1110, 1160, 1.62)]),
 (30.2, 34.1, sc_lega, [(30.2, 1300, 1150, 1.65), (32.2, 1250, 1110, 1.35), (34.1, 1230, 1100, 1.32)]),
 (34.1, 39.62, sc_rame, [(34.1, 1170, 1000, .95), (39.62, 1180, 990, 1.0)]),
 (39.62, 43.25, sc_antar, [(39.62, 1100, 1060, .95), (43.25, 1100, 1060, .97)]),
 (43.25, 50.95, sc_masalah, [(43.25, 1190, 1190, 1.25), (45.3, 1190, 1180, 1.32), (46.55, 1080, 1160, 1.65), (48.9, 1080, 1160, 1.7),
                             (49.15, 1350, 1110, 1.75), (50.95, 1350, 1110, 1.8)]),
 (50.95, 54.95, sc_satu, 'split'),
 (54.95, 59.15, sc_armada, [(54.95, 1350, 1110, 1.8), (56.25, 1330, 1100, 1.7), (56.8, 1220, 980, 1.05), (59.15, 1220, 980, 1.07)]),
 (59.15, DUR + 1, sc_dulu, [(59.15, 1170, 1100, .9), (64.2, 1140, 1130, 1.15), (DUR, 1140, 1130, 1.18)]),
]

# ------------------------------------------------------------ PRO PLUS: sisipan close-up (gerak kamera halus)
KEYS = {
    sc_serius: [(10.1, 1190, 1190, 1.25), (11.6, 1190, 1190, 1.3), (12.1, 1030, 1150, 2.1), (14.0, 1025, 1145, 2.2)],
    sc_nyesel: [(14.0, 1150, 1170, 1.4), (15.1, 1150, 1170, 1.45), (15.5, 1040, 1150, 2.0), (17.22, 1040, 1150, 2.05)],
    sc_pucat: [(17.22, 1350, 1100, 1.85), (17.9, 1365, 1140, 2.4), (19.2, 1365, 1140, 2.5), (19.6, 1350, 1100, 1.95),
                 (21.4, 1350, 1100, 1.95), (22.0, 1270, 980, 1.1), (23.35, 1270, 980, 1.12)],
    sc_tertawa: [(23.35, 1190, 1180, 1.3), (24.6, 1190, 1180, 1.35), (25.0, 1030, 1150, 2.1), (26.7, 1030, 1150, 2.15),
                   (27.1, 1190, 1180, 1.35), (28.3, 1150, 1170, 1.45), (28.7, 1060, 1150, 1.9), (30.2, 1060, 1150, 1.95)],
    sc_rame: [(34.1, 1170, 1000, .95), (35.6, 1170, 1000, .97), (36.0, 1640, 960, 1.7), (37.4, 1640, 960, 1.75),
                (37.8, 1170, 1000, .97), (39.62, 1180, 990, 1.0)],
    sc_masalah: [(43.25, 1190, 1190, 1.25), (44.4, 1190, 1180, 1.3), (44.8, 1030, 1150, 2.1), (46.4, 1030, 1150, 2.15),
                   (46.8, 1080, 1160, 1.65), (48.9, 1080, 1160, 1.7), (49.15, 1350, 1110, 1.75), (50.95, 1350, 1110, 1.8)],
    sc_armada: [(54.95, 1360, 1140, 2.3), (56.0, 1360, 1140, 2.4), (56.5, 1330, 1100, 1.7), (56.8, 1220, 980, 1.05), (59.15, 1220, 980, 1.07)],
    sc_dulu: [(59.15, 1170, 1100, .9), (61.0, 1150, 1110, 1.0), (62.2, 1130, 1100, 1.9), (64.2, 1130, 1100, 2.0), (DUR, 1130, 1100, 2.0)],
}

SCENES = [(a, b, fn, KEYS.get(fn, keys)) for (a, b, fn, keys) in SCENES]

# ------------------------------------------------------------ akting tambahan (dipasang gaya.pasang ke E.person)
def akting(who, t, po):
    if who == 'dio':
        if 10.1 <= t < 10.85:                       # betulkan kerah, senyum percaya diri
            po['aF'] = (26, 198 + 6 * math.sin(t * 22)); po['eyes'] = 'happy'; po['expr'] = 'grin'
        elif 57.7 <= t < 59.15:                     # mode closing: keluarkan brosur promo
            po['aF'] = (100, -15); po['hold'] = brosur; po['thumb'] = False; po['eyes'] = 'happy'; po['expr'] = 'grin'
    if who == 'rahmat':
        if 14.05 <= t < 16.95:                      # menunjuk sambil menghentak
            jab = abs(math.sin(t * 5))
            po['aF'] = (92 + 10 * jab, -6 + 8 * jab)
        elif t >= 59.15 and po.get('sit'):          # memegangi kepala
            po['aF'] = (165, 38 + 4 * math.sin(t * 1.5)); po['aB'] = (165, 38); po['tilt'] = 14

# ------------------------------------------------------------ efek & label
def efek_bawah(c, t):            # sebelum grading
    E.focus_lines(c, t, 12.55, 13.2, cy=H * .42)
    E.focus_lines(c, t, 49.2, 49.9, cy=H * .42)
    E.focus_lines(c, t, 0.1, 0.9, cy=H * .45)
    E.focus_lines(c, t, 17.3, 18.1, cy=H * .45)
    E.focus_lines(c, t, 56.8, 57.7, cy=H * .5)
    if t >= 59.15: rain(c, t, .45)
    lightning(c, t, 59.2); lightning(c, t, 62.6, .35)

def efek_atas(c, t):             # sesudah grading, sebelum teks narasi
    if 34.15 <= t < 35.8: E.pill(c, "TERNYATA...", t, 34.2, y=330, col=hx('#FFE14D'))
    if 56.9 <= t < 59.15: E.pill(c, "NAMBAH ARMADA!", t, 57.15, y=270, col=hx('#2EAD6B'), fg=(1, 1, 1))
    if 60.9 <= t < 64.2: E.pill(c, "DULU...", t, 60.96, y=330, col=hx('#D9B98A'))
    day_card(c, t)
    confetti(c, t, 56.85)

def vignette(t):
    return .4 if t >= 59.15 else .34

# ------------------------------------------------------------ suara (sound effect + musik), dipakai jalankan.py
def suara(S):
    S.musik([
        (0.0, 4.35, S.section(4.8, 84, S.Am, S.AmB, [0, 1, 2, 3], .8, padon=True, bright=.6)),          # hook, tense-comedic
        (4.35, 10.1, S.section(6.1, 108, S.C, S.CB, S.FULL, .95)),                                          # Dio datang, ceria
        (10.1, 23.35, S.section(13.6, 76, S.Am, S.AmB, [0, 1, 2, 3], .8, padon=True, bright=.6)),         # serius / pucat
        (23.35, 34.1, S.section(11.1, 112, S.F, S.FB, S.FULL, 1.05)),                                       # tertawa, lega
        (34.1, 43.25, S.section(9.5, 118, S.C, S.CB, S.FULL, 1.05)),                                        # rame + antar
        (43.25, 50.95, S.section(8.0, 80, S.Am, S.AmB, [0, 1, 2, 3], .8, padon=True, bright=.6)),         # masalah lagi
        (50.95, 59.15, S.section(8.5, 112, S.F, S.FB, S.FULL, 1.0)),                                        # satu mobil -> armada
        (59.15, 65.4, S.section(6.6, 64, S.SLOWAm, S.SLOWB, [0, 2], .75, padon=True, bright=.4)),         # flashback sedih
        (65.4, S.DUR, S.section(3.0, 108, S.C, S.CB, S.FULL, .9)),                                            # CTA
    ])
    for c0 in [4.35, 10.1, 17.22, 23.35, 34.1, 39.62, 43.25, 50.95, 54.95]: S.put(S.whoosh(.4), c0 - .2, .22)
    S.put(S.thud(), 0.15, .5); S.put(S.boing(), 0.2, .22)
    S.put(S.squeal(.3), 2.3, .12); S.put(S.pop(), 2.4, .3)                                  # sales panik "!"
    S.put(S.pop(), 5.55, .35)                                                           # kartu nama Dio
    for k in range(8): S.put(S.click()[:int(.08 * S.SR)], 4.6 + k * .5, .12)             # langkah kaki
    S.put(S.ding(1568, .8), 8.7, .2)                                                    # sapaan
    S.put(S.dun_dun(), 11.75, .45)                                                      # muka serius
    S.put(S.thud(), 17.3, .4); S.put(S.heartbeat(3.4), 18.0, .35)                           # waduh, pucat
    S.put(S.pop(), 21.65, .35); S.put(S.engine(.9, 45, 30) * .6, 21.9, .3); S.put(S.thud(), 22.7, .3); S.put(S.boing(), 22.75, .18)   # mobil mogok di bayangan
    S.put(S.scratch(), 23.35, .35)                                                      # "hah"
    for k in range(4): S.put(S.boing(), 24.5 + k * .5, .1)                             # tertawa
    S.put(S.sparkle(), 28.5, .35); S.put(S.ding(1760, .6), 28.55, .25)                      # jempol
    S.put(S.wind(1.0), 30.3, .25)                                                       # fiuuh lega
    S.put(S.pop(), 32.37, .4)                                                           # pensiun dini
    S.put(S.pop(), 34.2, .3)                                                            # TERNYATA
    S.put(S.pop(), 35.5, .3)                                                            # lembar pesanan MBG
    for at in (35.0, 36.3, 37.2, 38.2, 38.9): S.put(S.kaching(), at, .22)
    S.put(S.pop(), 37.95, .35)                                                          # RAME!
    for k in range(6):
        S.put(S.flip(), 39.62 + k * .6, .4); S.put(S.engine(.6, 50, 64), 39.62 + k * .6, .22)
    S.put(S.dun_dun(), 44.6, .45)                                                       # serius lagi
    for k in range(3): S.put(S.pop(), 49.85 + k * .12, .22)                             # ???
    S.put(S.pop(), 51.3, .35); S.put(S.pop(), 51.9, .4)                                     # kartu, angka 1
    for k in range(8): S.put(S.thud()[:int(.15 * S.SR)], 53.25 + k * .15, .18)            # pesanan menumpuk
    S.put(S.boing(), 55.05, .2)                                                         # walah
    S.put(S.thud(), 56.82, .45); S.put(S.chime(), 56.85, .4); S.put(S.sparkle(), 56.9, .35); S.put(S.confetti_pop(), 56.85, .3)
    S.put(S.pop(), 57.15, .35); S.put(S.pop(), 57.27, .3)
    S.put(S.thunder(), 59.2, .35)
    S.put(S.dun_dun(), 64.28, .45)
    S.put(S.pop(), 65.55, .4); S.put(S.chime(), 65.6, .35); S.put(S.pop(), 66.4, .3); S.put(S.sparkle(), 66.45, .3)

    # ---------------- PRO extras
    for at in (2.3, 8.6, 11.7, 19.3, 24.4, 28.45, 44.5, 49.15, 56.2): S.put(S.whoosh(.25), at - .08, .12)   # gestur (ancang-ancang)
    for k in range(7): S.put(S.flip(), 53.15 + k * .2, .35)                                                     # kertas pesanan terbang
    for k in range(5): S.put(S.pop(), 56.9 + k * .09, .12)                                                      # confetti
    S.put(S.thunder(), 62.6, .25); S.put(S.click()[:int(.1 * S.SR)], 59.2, .35)                                       # kilat
    for k in range(3): S.put(S.click()[:int(.07 * S.SR)], 4.75 + k * .9, .08)                                     # debu langkah

    S.put_amb(S.birds(34, 30), 0.0, .06); S.put_amb(S.birds(25, 18), 34.1, .06)
    S.put_amb(S.lowpass(S.rng.standard_normal(int(5.5 * S.SR)), 700) * .3, 34.1, .07)     # keramaian pembeli
    S.put_amb(S.rainfx(6.6), 59.15, .16); S.put_amb(S.crickets(6.4), 59.15, .05)
    S.diam(59.15, 59.9)                    # musik hening sesaat di awal kilas balik
