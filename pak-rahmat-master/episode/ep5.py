"""PAK RAHMAT EP 5 - HAMPIR MENYERAH (84 dtk). Kilas balik 3 tahun lalu: modal dibawa kabur pemasok, utang pelanggan
numpuk, Bu Julit mengejek, Pak Rahmat narik ojek + jaga toko + jual bensin botolan, istri menangis, toko bangkit lagi,
lalu Bu Julit datang mau berutang. Penutup: tetangga begini masih dibolehin utang?
Properti baru (kandidat aset): rak_bensin, buku_utang, kaleng_uang, air_mata, sc_ojek (motor + penumpang)."""
from aset_dio import *
from aset_dasar import bulb_glow, zzz
import gaya

N = 5
VDUR = 81.48
DUR = 84.2
HOOK = ("MAU BANGKRUT?!", 2.2)
PUNCH = (0.12, 73.45)
BERSAMBUNG = None
CTA = dict(baris1="KALAU KAMU PAK RAHMAT,", baris2="MASIH DIBOLEHIN UTANG?",
           pilihan=[("BOLEH UTANG", '#2EAD6B'), ("GAK BOLEH", '#D7141A')])
SUASANA = [(4.95, 9.4, 'dulu'), (9.4, 17.25, 'tense'), (17.25, 27.5, 'dulu'), (27.5, 29.05, 'morning'), (29.05, 30.85, 'dulu'),
           (30.85, 55.8, 'night'), (55.8, 64.25, 'warm'), (64.25, 69.2, 'morning')]

RAHMAT_SPEAK = [(51.36, 54.5), (71.72, 73.9)]
JULIT_SPEAK = [(20.3, 24.4), (35.5, 41.9)]
ISTRI_SPEAK = [(45.7, 47.8)]
FLASH0, FLASH1 = 4.95, 999        # seluruh cerita = 3 tahun lalu

SEDIH = dict(aF=(160, -150), aB=(160, -150), eyes='half', expr='frown', brows='up', look=(0, 6))
LESU = dict(aF=(10, 5), aB=(-10, 5), eyes='half', expr='frown', brows='up', look=(0, 5), tilt=6)

def fade_out(t, t1, d=.3): return 1 - ease((t - t1) / d)
def show(t, t0, t1, d=.3): return pop(t, t0, d) * fade_out(t, t1)


# ------------------------------------------------------------ properti baru
def rak_bensin(c, x, y, s=1.0, t=0.0, night=False):
    """rak kayu bensin botolan (y = lantai)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    for lx in (-130, 130):
        c.rectangle(lx - 10, -330, 20, 330); fs(c, hx('#8A5A30'), 4)
    for j, sy in enumerate((-300, -200, -100)):
        c.rectangle(-150, sy + 70, 300, 16); fs(c, hx('#A8743F'), 4)
        for k in range(5):
            bx = -110 + k * 55
            rrect(c, bx - 16, sy - 8, 32, 78, 8); fs(c, hx('#F2A81D') if (j + k) % 4 else hx('#E8C23A'), 4)
            c.rectangle(bx - 7, sy - 28, 14, 22); fs(c, hx('#D9DEE3'), 3)
            c.rectangle(bx - 10, sy + 20, 20, 6); fill(c, (1, 1, 1), .5)
    c.save(); c.translate(0, -390); c.rotate(-.05)
    rrect(c, -120, -40, 240, 80, 6); fs(c, hx('#C98B4A'), 5)
    text(c, "BENSIN", 0, -8, 40, hx('#B3261E')); text(c, "Rp 10.000", 0, 24, 22, OUT)
    c.restore()
    if night:
        bulb_glow(c, 0, -460, 180, .35); ell(c, 0, -460, 16, 16); fill(c, hx('#FFF2B0'))
    c.restore()

def buku_utang(c, x, y, k, t, n_baris=5, julit=False, stamp_t=None):
    if k <= .03: return
    c.save(); c.translate(x, y); c.scale(k, k); c.rotate(-.04)
    rrect(c, -250, -300, 500, 600, 12); fs(c, hx('#2E6BD6'), 7)
    rrect(c, -225, -275, 450, 550, 6); fs(c, hx('#FFFDF2'), 3)
    text(c, "BUKU UTANG", 0, -235, 40, hx('#B3261E'))
    rows = [("Bu Sri", "50.000"), ("Pak Udin", "125.000"), ("Mas Joko", "80.000"), ("Bu Tini", "200.000"),
            ("Pak Rudi", "65.000"), ("Bu Ani", "90.000")]
    if julit: rows = [("Bu Julit", "350.000")] + rows[:3]
    for i, (nm, rp) in enumerate(rows[:n_baris]):
        yy = -165 + i * 70
        c.move_to(-200, yy + 28); c.line_to(200, yy + 28); c.set_source_rgba(.3, .5, .9, .5); c.set_line_width(2); c.stroke()
        a = clamp((t - (stamp_t or 0)) * 4) if julit and i == 0 and stamp_t else 1
        text(c, nm, -190, yy, 32, OUT, align='l')
        text(c, "Rp " + rp, 190, yy, 32, hx('#B3261E') if (julit and i == 0) else OUT, align='r')
    if stamp_t is not None and t >= stamp_t:
        ks = pop(t, stamp_t, .2)
        c.save(); c.translate(20, 170); c.scale(1.6 - .6 * ks, 1.6 - .6 * ks); c.rotate(-.18)
        c.push_group()
        rrect(c, -190, -50, 380, 100, 10); c.set_source_rgb(*hx('#D7141A')); c.set_line_width(10); c.stroke()
        text(c, "BELUM LUNAS", 0, 0, 52, hx('#D7141A'))
        c.pop_group_to_source(); c.paint_with_alpha(ks * .92)
        c.restore()
    c.restore()

def kaleng_uang(c, x, y, k, t, isi):
    """kaleng tabungan; isi 0..1 tinggi tumpukan uang."""
    if k <= .03: return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.save(); c.rectangle(-150, -220, 300, 260); c.clip()
    hh = 40 + 200 * isi
    for j in range(int(hh / 22) + 1):
        rrect(c, -130 + (j % 2) * 12, 20 - j * 22, 250, 26, 6); fs(c, hx('#F07AA8') if j % 3 else hx('#7FC77F'), 3)
    c.restore()
    c.rectangle(-150, -220, 300, 260); c.set_source_rgb(*OUT); c.set_line_width(9); c.stroke()
    rrect(c, -170, 30, 340, 40, 10); fs(c, hx('#A9B2BA'), 6)
    rrect(c, -160, -40, 320, 90, 10); fs(c, hx('#D7141A'), 6)
    text(c, "TABUNGAN TOKO", 0, 5, 34, (1, 1, 1), OUT, 5)
    c.restore()

def air_mata(c, x, y, t, s=1.0, a=1.0):
    """air mata dari kedua mata (x,y = kaki tokoh, tinggi standar)."""
    if a <= .02: return
    for sgn, ph in ((-1, 0.0), (1, .45)):
        u = (t * 1.3 + ph) % 1
        ex, ey = x + sgn * 34 * s, y - 330 * s
        c.move_to(ex, ey); c.line_to(ex + sgn * 4, ey + 70 * s); c.set_source_rgba(.55, .8, 1, .7 * a); c.set_line_width(7 * s); c.stroke()
        dy = ey + 20 + u * 90 * s
        c.move_to(ex, dy - 14); c.curve_to(ex + 10, dy, ex + 8, dy + 12, ex, dy + 12); c.curve_to(ex - 8, dy + 12, ex - 10, dy, ex, dy - 14)
        c.set_source_rgba(.55, .82, 1, a * (1 - u)); c.fill()

def hati(c, x, y, k):
    if k <= .03: return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.move_to(0, 30); c.curve_to(-60, -10, -40, -60, 0, -30); c.curve_to(40, -60, 60, -10, 0, 30); c.close_path(); fs(c, hx('#E5473B'), 5)
    c.restore()

def ghost_granmax(c, t, x, y, a):
    if a <= .02: return
    c.push_group(); lib.gran_max(c, x, y, t, 0, cargo=False); c.pop_group_to_source(); c.paint_with_alpha(a)


# ------------------------------------------------------------ adegan
JX0 = 1560                    # posisi Bu Julit di sebelah toko

def julit_po(**kw):
    d = {'who': 'julit', 'x': JX0, 'y': YS, 'flip': True}; d.update(kw); return d

def sc_hook(c, t, t0):
    m = talk(t, [(3.3, 4.9)]) * 0  # (narator)
    seneng = t > 3.2
    rpo = rahmat_po(x=1020, **SEDIH)
    jpo = julit_po(x=1500, aF=pose_seq(t, [(0, (40, 10), (20, 0)), (3.3, (150, -40), (40, -100))])[0],
                   aB=(40, -100) if seneng else (20, 0), eyes='happy' if seneng else 'squint', expr='grin' if seneng else 'pout',
                   brows='smug', mouth=.4 * abs(math.sin(t * 12)) if seneng else 0, look=(-6, 0))
    street(c, t, [rpo, jpo], toko='kosong', car=False)
    gloom(c, 1020, YS, 1.0, clamp((t - .3) / .4))
    if seneng:
        for j in range(3): spark(c, 1580 + 60 * math.cos(t * 3 + j * 2), 960 + 40 * math.sin(t * 4 + j), 18, .8)

def sc_dulu(c, t, t0):
    a = clamp((t - 7.4) / .5) * fade_out(t, 9.1)
    street(c, t, [rahmat_po(x=1120, **LESU)], toko='kosong', car=False)
    ghost_granmax(c, t, -500, 1620, .3 * a)

def x_merah(c, t):
    """tanda X merah + kartu di atas bayangan Gran Max (koordinat layar)."""
    a = clamp((t - 7.4) / .3) * fade_out(t, 9.1)
    if a <= .02: return
    c.save(); c.translate(300, 1200); c.set_line_width(18); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(-150, -110); c.line_to(150, 110); c.move_to(150, -110); c.line_to(-150, 110)
    c.set_source_rgba(*hx('#D7141A'), .95 * a); c.stroke(); c.restore()
    card(c, W / 2 - 30, 700, pop(t, 7.5, .3) * fade_out(t, 9.1), "BELUM PUNYA GRAN MAX", (1, 1, 1), 50)

def cam_dulu(t):
    k = ease((t - 7.2) / 1.0) * (1 - ease((t - 8.9) / .5))
    return (lerp(1150, 380, k), lerp(1100, 1120, k), lerp(1.2, .95, k))

def sc_tutup(c, t, t0):
    sh = .45 * ease((t - 9.4) / 1.2)
    rp = rahmat_po(x=1120, y=1400, sit=True, aF=(165, 38), aB=(165, 38), tilt=14, eyes='closed' if t < 11.4 else 'wide',
                   expr='frown' if t < 11.4 else 'o', brows='up', peci_lift=1 if t > 11.5 else 0)
    street(c, t, [rp], toko='kosong', shutter=sh, car=False)
    card(c, 1170, 640, show(t, 9.6, 11.3), "HAMPIR TUTUP", hx('#FFE14D'), 70)
    if t >= 11.4:
        G.uang_terbang(c, t, 11.4, 1500, 1200, 7)
        card(c, 1170, 640, show(t, 12.3, 13.4), "MODAL DIBAWA KABUR!", hx('#D7141A'), 56, fg=(1, 1, 1))

def sc_utang(c, t, t0):
    kab = clamp((t - 15.9) / 1.0)
    bpo = {'who': 'b2', 'x': lerp(1420, 2300, ease(kab)), 'y': YS, 'flip': kab <= 0, 'step': 1 if 0 < kab < 1 else 0,
           'aF': (120, -30) if kab > 0 else (40, 10), 'eyes': 'wide' if kab > 0 else 'open', 'expr': 'o' if kab > 0 else 'smile',
           'look': (6, 0) if kab > 0 else (-6, 0)}
    rpo = rahmat_po(x=1000, aF=(95, -10) if t > 15.5 else (40, 10), aB=(20, 0), eyes='open', expr='flat' if t < 15.5 else 'o',
                    brows='up', look=(6, 0))
    street(c, t, [rpo, bpo], toko='kosong', car=False)
    if 0 < kab < 1:
        for j in range(3):
            ph = (t * 2 + j / 3) % 1
            P.puff(c, bpo['x'] - 60 - ph * 90, YS - 10 - ph * 30, 14 + ph * 22, .4 * (1 - ph))
    card(c, 1650, 760, show(t, 16.3, 17.2), "KABUR!", hx('#FFE14D'), 70, rot=.06)

def sc_nyamber(c, t, t0):
    jx = lerp(2300, JX0, ease((t - 17.3) / 1.3))
    walking = t < 18.6
    m = talk(t, JULIT_SPEAK)
    jpo = julit_po(x=jx, step=1 if walking else 0, aF=(150, -40) if t > 20.3 else (40, 10), aB=(40, -100) if t > 20.3 else (20, 0),
                   eyes='squint' if t < 22.3 else 'happy', brows='smug', expr='grin' if t > 20.3 else 'pout', mouth=m, look=(-6, 0))
    fpo = {'who': 'friend', 'x': jx + 200, 'y': YS, 'flip': True, 'step': 1 if walking else 0, 'aF': (60, 80), 'eyes': 'happy',
           'expr': 'grin', 'look': (-6, 0)}
    street(c, t, [rahmat_po(x=1020, **LESU), jpo, fpo], toko='kosong', car=False)
    gloom(c, 1020, YS, 1.0, clamp((t - 20.5) / .5))
    tanya(c, JX0 - 20, 880, t, 21.3)
    card(c, 1300, 640, show(t, 21.3, 22.2), "JURAGAN?", hx('#FFE14D'), 70, rot=.06)
    card(c, 1170, 640, show(t, 22.4, 25.6), "KAYAK GUDANG KOSONG", (1, 1, 1), 48)

def sc_keluarga(c, t, t0):
    k = (25.7, 26.6)
    people = [rahmat_po(x=1000, aF=(40, 10), aB=(-10, 10), expr='smile', eyes='open', brows='up', look=(4, 0)),
              {'who': 'anak', 'x': 1180, 'y': YS + 10, 's': .8, 'aF': (60, 40), 'expr': 'smile', 'look': (-4, -3)},
              {'who': 'burahmat', 'x': 1360, 'y': YS, 'flip': True, 'aF': (40, 10), 'expr': 'smile', 'brows': 'up', 'look': (-5, 0)}]
    street(c, t, people, toko='kosong', car=False)
    hati(c, 1180, 900 - 20 * math.sin(t * 3), pop(t, 26.0, .35))

def sc_ojek(c, t, t0):
    """pagi: narik ojek (gambar di koordinat layar, kamera 'split')."""
    g = cairo.LinearGradient(0, 0, 0, 1400)
    g.add_color_stop_rgb(0, *hx('#58B2F2')); g.add_color_stop_rgb(1, *hx('#FFE3B8'))
    c.set_source(g); c.rectangle(-500, -500, 2100, 2500); c.fill()
    bulb_glow(c, 820, 520, 300, .45); ell(c, 820, 520, 80, 80); fill(c, hx('#FFE9A0'))
    off = (t - t0) * 900
    for i in range(-2, 12):
        bx = (i * 260 - off * 0.35) % 2600 - 600
        hh = i * 47 % 120
        c.rectangle(bx, 900 - hh, 200, 600); fs(c, hx(['#E8C27A', '#9CCFD8', '#F4A99B', '#C5E1A5'][i % 4]), 4)
        poly(c, [(bx - 20, 910 - hh), (bx + 220, 910 - hh), (bx + 100, 800 - hh)]); fs(c, hx('#A0522D'), 4)
    for i in range(-2, 10):
        tx = (i * 420 - off * .8) % 3000 - 800
        c.rectangle(tx - 10, 900, 20, 450); fs(c, hx('#6B4A33'), 4)
        ell(c, tx, 880, 110, 100); fs(c, hx('#3E8E4A'), 6)
    c.rectangle(-500, 1340, 2100, 90); fs(c, hx('#C9C3B6'), 5)
    c.rectangle(-500, 1430, 2100, 1400); fill(c, hx('#55585E'))
    for i in range(-2, 12):
        c.rectangle((i * 240 - off) % 2700 - 600, 1640, 130, 14); fill(c, hx('#F2F2F2'), .85)
    mx = 560; my = 1600 + 4 * math.sin(t * 20)
    lib.motor(c, mx, my, t, (t - t0) * 16)
    E.person(c, mx - 150, my - 40, 'b1', {'sit': True, 'aF': (60, 20), 'aB': (60, 20), 'expr': 'smile', 'bob': 0}, s=.95, t=t)
    E.person(c, mx - 30, my - 40, 'rahmat', {'sit': True, 'aF': (100, -10), 'aB': (95, -5), 'expr': 'flat', 'eyes': 'half',
                                             'brows': 'up', 'bob': 0}, s=1.0, t=t)
    for k in range(4):
        yy = 1200 + k * 80
        c.move_to(260 - k * 40, yy); c.line_to(90 - k * 40, yy); c.set_source_rgba(1, 1, 1, .8); c.set_line_width(8); c.stroke()

def sc_jaga(c, t, t0):
    rp = rahmat_po(x=1170, y=1400, sit=True, aF=(150, 20), aB=(20, 10), tilt=10 * math.sin(t * 1.2), eyes='half', expr='flat', look=(0, 2))
    street(c, t, [rp], toko='kosong', car=False)
    zzz(c, 1230, 920, t, 1.0, clamp((t - 29.6) / .4))

def sc_bensin(c, t, t0):
    rp = rahmat_po(x=1000, aF=(70, -10), aB=(20, 0), eyes='half', expr='flat', brows='up', look=(6, 0),
                   hold=lambda c, h: (rrect(c, h[0] - 14, h[1] - 60, 28, 70, 8), fs(c, hx('#F2A81D'), 4)))
    street(c, t, [rp], toko='kosong', shutter=.6, car=False, tod='night',
           fx=[lambda c: rak_bensin(c, 1300, 1440, 1.0, t, True)])

def sc_ejek(c, t, t0):
    jx = lerp(-300, 1560, ease((t - 32.9) / 2.2)) if t < 35.1 else 1560
    walking = t < 35.1
    m = talk(t, JULIT_SPEAK)
    laugh = t > 41.1
    jpo = julit_po(x=jx, flip=not walking, step=1 if walking else 0,
                   aF=(150, -40) if 35.5 < t < 41 else ((40, -100) if laugh else (40, 10)), aB=(40, -100) if t > 35.5 else (20, 0),
                   eyes='happy' if laugh or t > 39.6 else 'squint', brows='smug', expr='grin', mouth=m, look=(-6 if not walking else 6, 0))
    rp = rahmat_po(x=1000, **LESU)
    street(c, t, [rp, jpo], toko='kosong', shutter=.6, car=False, tod='night',
           fx=[lambda c: rak_bensin(c, 1300, 1440, 1.0, t, True)])
    gloom(c, 1000, YS, 1.0, clamp((t - 36.0) / .5))
    card(c, 1050, 600, show(t, 36.9, 41.0), "DULU: BERAS", (1, 1, 1), 54, rot=-.06)
    card(c, 1350, 760, show(t, 38.1, 41.0), "SEKARANG: BENSIN", hx('#F2A81D'), 54, rot=.05)
    tanya(c, 1560, 860, t, 39.7)
    if laugh:
        for j in range(2):
            card(c, 1500 + j * 170, 820 - j * 70, pop(t, 41.2 + j * .15, .2), "HA", hx('#FFE14D'), 50, rot=.1 - j * .2)

def sc_nangis(c, t, t0):
    m = talk(t, ISTRI_SPEAK)
    rp = rahmat_po(x=1060, y=1400, sit=True, aF=(30, 10), aB=(10, 5), eyes='half', expr='frown', brows='up', look=(5, 4))
    bp = {'who': 'burahmat', 'x': 1290, 'y': 1400, 'sit': True, 'flip': True, 'aF': (150, -150) if t < 45.6 else (60, 30),
          'aB': (150, -150) if t < 45.6 else (40, 20), 'eyes': 'closed' if t < 45.6 else 'half', 'expr': 'frown', 'brows': 'up',
          'mouth': m, 'look': (-5, 2), 'tilt': -8}
    street(c, t, [rp, bp], toko='kosong', shutter=.55, car=False, tod='night')
    air_mata(c, 1290, 1365, t, 1.0, clamp((t - 43.9) / .5))

def sc_genggam(c, t, t0):
    m = talk(t, RAHMAT_SPEAK)
    reach = ease((t - 49.4) / .8)
    rp = rahmat_po(x=1100, y=1400, sit=True, aF=(lerp(30, 88, reach), lerp(10, -4, reach)), aB=(10, 5),
                   eyes='open' if t > 51.2 else 'half', expr='smile' if t > 50.4 else 'frown', brows='normal' if t > 51.2 else 'up',
                   mouth=m, look=(6, 0))
    bp = {'who': 'burahmat', 'x': 1300, 'y': 1400, 'sit': True, 'flip': True, 'aF': (lerp(60, 88, reach), lerp(30, -4, reach)),
          'aB': (40, 20), 'eyes': 'half' if t < 53.5 else 'happy', 'expr': 'frown' if t < 52 else 'smile', 'brows': 'up', 'look': (-5, 0), 'tilt': -6}
    street(c, t, [rp, bp], toko='kosong', shutter=.55, car=False, tod='night')
    air_mata(c, 1300, 1365, t, 1.0, 1 - clamp((t - 53.0) / 1.0))
    if reach > .95:
        bulb_glow(c, 1200, 1150, 120, .5 * clamp((t - 50.2) / .4))
        hati(c, 1200, 960 - 15 * math.sin(t * 3), pop(t, 50.3, .35))

def sc_kumpul(c, t, t0):
    rp = rahmat_po(x=980, aF=(95, -10), aB=(20, 0), eyes='open', expr='smile', brows='normal', look=(6, 2))
    street(c, t, [rp], toko='kosong', car=False)
    isi = clamp((t - 56.0) / 3.8)
    kaleng_uang(c, 1250, 1300, 1.0, t, isi)
    for j, ta in enumerate((56.3, 56.9, 57.5, 58.1, 58.7, 59.3)):
        coin_pop(c, 1150 + (j % 3) * 90, 1120, t, ta)
    card(c, 1200, 700, show(t, 58.8, 59.95), "SEDIKIT DEMI SEDIKIT", hx('#FFE14D'), 52)

def sc_bangkit(c, t, t0):
    penuh = t >= 61.0
    busy = lambda ph: (120 + 40 * math.sin(t * 7 + ph), -40)
    people = [{'who': 'rahmat', 'x': 1040, 'y': 1370, 'aF': busy(0) if t > 62.4 else (40, 10), 'aB': (90, -20) if t > 62.4 else (-10, 10),
               'expr': 'grin', 'eyes': 'happy' if penuh else 'open', 'look': (5, 4)},
              {'who': 'burahmat', 'x': 1290, 'y': 1370, 'flip': True, 'aF': busy(2) if t > 62.4 else (40, 10), 'aB': (90, -20),
               'expr': 'grin', 'look': (-5, 4)}]
    q = [('b2', 1165, 62.45), ('b1', 760, 62.6), ('b4', 1560, 62.8), ('b3', 420, 63.3)]
    front = []
    for i, (who, x, ta) in enumerate(q):
        if t < ta: continue
        k = eout((t - ta) / .5)
        xx = lerp(x + (-500 if x < 1200 else 500), x, k)
        flip = x > 1200
        front.append({'who': who, 'x': xx, 'y': 1540 if i == 0 else 1480, 'flip': flip, 'step': 1 if k < 1 else 0,
                      'aF': (100, -20) if i % 2 else (40, 10), 'expr': 'smile', 'look': (-5 if flip else 5, -2), 's': .9 if i == 0 else .95})
    street(c, t, people, front=front, toko='normal' if penuh else 'kosong', car=False)
    if 61.0 <= t < 61.8:
        d = (t - 61.0) / .8
        for j in range(10):
            a = j * .63
            spark(c, 1170 + math.cos(a) * 420 * eout(d), 1000 + math.sin(a) * 260 * eout(d), 22, 1 - d)
    for j, ta in enumerate((62.9, 63.4, 63.9)):
        coin_pop(c, 1000 + j * 90, 1050, t, ta)
    card(c, 1170, 640, show(t, 61.1, 62.3), "RAK TERISI LAGI!", hx('#2EAD6B'), 60, fg=(1, 1, 1))
    card(c, 1170, 640, pop(t, 63.0, .3), "RAME LAGI!", hx('#FFE14D'), 80, rot=.06)

def sc_ngutang(c, t, t0):
    jx = lerp(2300, 1460, ease((t - 64.6) / 2.4))
    walking = t < 67.0
    rp = rahmat_po(x=1020, aF=(40, 10), aB=(-10, 10), expr='smile' if t < 67.9 else 'o', eyes='open' if t < 67.9 else 'wide',
                   brows='normal' if t < 67.9 else 'up', look=(6, 0))
    jpo = julit_po(x=jx, step=1 if walking else 0, aF=(26, 198) if t > 67.3 else (40, 10), aB=(20, 0),
                   eyes='happy', expr='grin', brows='up', mouth=.25 * abs(math.sin(t * 10)) if 67.4 < t < 69 else 0, look=(-6, 2))
    street(c, t, [rp, jpo], toko='normal', car=False, tod='morning')
    card(c, 1300, 640, show(t, 68.1, 69.25), "MAU NGUTANG?!", hx('#FFE14D'), 70, rot=.05)
    if t > 67.9: exclaim(c, 1030, 880, 1.0, pop(t, 67.95, .25))

def sc_lunas(c, t, t0):
    m = talk(t, RAHMAT_SPEAK)
    kaget = t > 73.6
    rp = rahmat_po(x=1020, aF=(95, -10) if t > 72.4 else (40, 10), aB=(-10, 10), expr='smile', eyes='happy' if t < 71.6 else 'open',
                   brows='normal', mouth=m, look=(6, 0), hold=None)
    jpo = julit_po(x=1460, aF=(26, 198) if not kaget else (150, -150), aB=(20, 0) if not kaget else (150, -150),
                   eyes='wide' if kaget else 'happy', expr='o' if kaget else 'grin', brows='up', mouth=.5 if kaget else 0, look=(-6, 0))
    street(c, t, [rp, jpo], toko='normal', car=False, tod='morning')
    if kaget:
        sweat(c, 1380, 1040, 1.0); sweat(c, 1540, 1060, .8)
        gloom(c, 1460, YS, 1.0, clamp((t - 73.8) / .4))

def sc_tanya(c, t, t0):
    rp = rahmat_po(x=1020, aF=(40, 10), aB=(-10, 10), expr='smile', eyes='open', brows='up', look=(6, 0))
    jpo = julit_po(x=1460, aF=(26, 198), aB=(20, 0), eyes='half', expr='pout', brows='up', look=(-6, 3))
    street(c, t, [rp, jpo], toko='normal', car=False, tod='morning')
    tanya(c, 1240, 820, t, 76.2)

SCENES = [
    (0.0, 4.95, sc_hook, [(0, 1050, 1150, 1.75), (2.0, 1060, 1150, 1.7), (3.3, 1300, 1140, 1.4), (4.95, 1310, 1140, 1.38)]),
    (4.95, 9.4, sc_dulu, cam_dulu),
    (9.4, 13.5, sc_tutup, [(9.4, 1170, 1050, 1.0), (11.3, 1150, 1100, 1.15), (13.5, 1150, 1100, 1.2)]),
    (13.5, 17.25, sc_utang, [(13.5, 1250, 1150, 1.2), (15.8, 1300, 1150, 1.15), (17.25, 1450, 1130, 1.05)]),
    (17.25, 25.7, sc_nyamber, [(17.25, 1300, 1150, 1.1), (19.8, 1300, 1150, 1.15), (20.3, 1500, 1120, 1.75), (22.2, 1500, 1120, 1.8),
                               (22.8, 1270, 1150, 1.2), (25.7, 1270, 1150, 1.22)]),
    (25.7, 27.5, sc_keluarga, [(25.7, 1180, 1150, 1.25), (27.5, 1180, 1150, 1.32)]),
    (27.5, 29.05, sc_ojek, 'split'),
    (29.05, 30.85, sc_jaga, [(29.05, 1170, 1080, 1.1), (30.85, 1170, 1090, 1.2)]),
    (30.85, 32.9, sc_bensin, [(30.85, 1150, 1120, 1.15), (32.9, 1160, 1120, 1.22)]),
    (32.9, 42.6, sc_ejek, [(32.9, 1150, 1100, 1.0), (35.3, 1280, 1130, 1.12), (39.5, 1300, 1130, 1.16), (40.0, 1520, 1110, 1.75),
                           (42.6, 1520, 1110, 1.8)]),
    (42.6, 48.85, sc_nangis, [(42.6, 1175, 1150, 1.2), (45.0, 1180, 1160, 1.3), (45.6, 1270, 1120, 1.85), (48.85, 1270, 1120, 1.9)]),
    (48.85, 55.8, sc_genggam, [(48.85, 1200, 1170, 1.4), (50.8, 1200, 1170, 1.5), (51.3, 1120, 1120, 1.9), (54.6, 1120, 1120, 1.95),
                               (55.8, 1200, 1150, 1.5)]),
    (55.8, 60.0, sc_kumpul, [(55.8, 1150, 1150, 1.15), (60.0, 1160, 1150, 1.22)]),
    (60.0, 64.25, sc_bangkit, [(60.0, 1170, 1050, .98), (64.25, 1180, 1040, 1.02)]),
    (64.25, 69.2, sc_ngutang, [(64.25, 1350, 1120, .95), (67.0, 1250, 1150, 1.2), (69.2, 1250, 1150, 1.25)]),
    (69.2, 75.2, sc_lunas, [(69.2, 1250, 1150, 1.25), (70.4, 1250, 1150, 1.3), (71.2, 1040, 1130, 1.85), (73.4, 1040, 1130, 1.9),
                            (73.6, 1420, 1100, 1.7), (75.2, 1420, 1100, 1.75)]),
    (75.2, DUR + 1, sc_tanya, [(75.2, 1240, 1150, 1.2), (DUR, 1240, 1150, 1.28)]),
]


# ------------------------------------------------------------ efek & label
def efek_bawah(c, t):
    E.focus_lines(c, t, 0.1, 0.9, cy=H * .45)
    E.focus_lines(c, t, 11.45, 12.2, cy=H * .45)
    E.focus_lines(c, t, 73.5, 74.3, cy=H * .45)
    lightning(c, t, 11.45, .35)

def efek_atas(c, t):
    if 7.4 <= t < 9.4: x_merah(c, t)
    if 5.0 <= t < 7.4: E.pill(c, "3 TAHUN LALU...", t, 5.1, y=330, col=hx('#D9B98A'))
    if 27.55 <= t < 29.05: E.pill(c, "PAGI: NARIK OJEK", t, 27.6, y=330, col=hx('#FFD08A'))
    if 29.1 <= t < 30.85: E.pill(c, "SIANG: JAGA TOKO", t, 29.15, y=330, col=hx('#FFE14D'))
    if 30.9 <= t < 32.9: E.pill(c, "MALAM: JUAL BENSIN", t, 30.95, y=330, col=hx('#7FB3FF'))
    if 42.7 <= t < 44.6: E.pill(c, "SUATU MALAM...", t, 42.75, y=330, col=hx('#7FB3FF'))
    if 64.3 <= t < 66.0: E.pill(c, "SUATU PAGI...", t, 64.35, y=330, col=hx('#FFD08A'))
    if 13.6 <= t < 16.2:
        buku_utang(c, W / 2 - 30, 760, show(t, 13.7, 15.9) * .95, t, n_baris=int(clamp((t - 13.9) / .3, 1, 6)))
    if 72.8 <= t < 75.2:
        buku_utang(c, 330, 600, show(t, 72.85, 75.0) * .68, t, n_baris=4, julit=True, stamp_t=73.45)
    if 76.1 <= t < VDUR + .2:
        card(c, W / 2 - 30, 560, pop(t, 76.2, .3), "KALAU KAMU?", hx('#FFE14D'), 80, rot=-.05)
    # label kilas balik kecil
    if FLASH0 + .3 <= t < VDUR:
        a = clamp((t - FLASH0 - .3) / .4)
        c.save(); c.translate(40, 275)
        rrect(c, 0, -20, 230, 40, 20); fill(c, hx('#D9B98A'), .85 * a)
        text(c, "3 TAHUN LALU", 115, 0, 22, OUT, alpha=a)
        c.restore()

def vignette(t):
    return .4 if 30.85 <= t < 55.8 else .34


# ------------------------------------------------------------ suara
def suara(S):
    S.musik([
        (0.0, 4.95, S.section(5.4, 84, S.Am, S.AmB, [0, 1, 2, 3], .8, padon=True, bright=.6)),        # hook tegang-lucu
        (4.95, 17.25, S.section(12.8, 70, S.SLOWAm, S.SLOWB, [0, 2], .75, padon=True, bright=.45)),     # kilas balik, hampir tutup
        (17.25, 25.7, S.section(8.9, 104, S.Am, S.AmB, S.FULL, .85, bright=.7)),                       # julit nyamber
        (25.7, 32.9, S.section(7.6, 96, S.F, S.FB, [0, 1, 2, 3], .85, padon=True, bright=.7)),         # kerja keras
        (32.9, 42.6, S.section(10.2, 104, S.Am, S.AmB, S.FULL, .85, bright=.7)),                       # julit ejek lagi
        (42.6, 55.8, S.section(13.6, 62, S.SLOWAm, S.SLOWB, [0, 2], .75, padon=True, bright=.4)),      # istri menangis, genggam tangan
        (55.8, 64.25, S.section(8.9, 112, S.C, S.CB, S.FULL, 1.0)),                                     # bangkit lagi
        (64.25, 75.2, S.section(11.4, 108, S.F, S.FB, S.FULL, .95)),                                    # julit mau ngutang
        (75.2, S.DUR, S.section(9.5, 108, S.C, S.CB, S.FULL, .9)),                                      # pertanyaan + CTA
    ])
    for c0 in [4.95, 9.4, 13.5, 17.25, 25.7, 27.5, 29.05, 30.85, 32.9, 42.6, 48.85, 55.8, 60.0, 64.25, 69.2, 75.2]:
        S.put(S.whoosh(.4), c0 - .2, .2)
    S.put(S.thud(), 0.15, .5); S.put(S.boing(), 0.2, .22)
    for k in range(4): S.put(S.boing(), 3.4 + k * .35, .08)                     # julit seneng
    S.put(S.tape(), 4.95, .3)                                                     # mundur ke masa lalu
    S.put(S.pop(), 7.5, .3)                                                       # belum punya Gran Max
    S.put(S.dun_dun(), 9.6, .4)                                                   # hampir tutup
    S.put(S.thunder(), 11.45, .3); S.put(S.wind(1.2), 11.5, .25)                  # modal kabur
    S.put(S.pop(), 12.3, .35)
    for k in range(5): S.put(S.flip(), 13.8 + k * .3, .3)                         # buku utang
    S.put(S.squeal(.3), 15.9, .12); S.put(S.pop(), 16.3, .3)                      # kabur
    for k in range(6): S.put(S.click()[:int(.08 * S.SR)], 17.3 + k * .22, .1)    # langkah julit
    S.put(S.boing(), 21.35, .18); S.put(S.pop(), 22.45, .3)
    S.put(S.ding(1568, .8), 26.0, .2)                                             # keluarga
    S.put(S.motorbike(1.5), 27.5, .3)
    S.put(S.snore(1.4), 29.5, .2)
    S.put(S.clink(), 31.3, .25)
    for k in range(9): S.put(S.click()[:int(.08 * S.SR)], 33.0 + k * .24, .1)
    S.put(S.pop(), 36.95, .3); S.put(S.pop(), 38.15, .3)
    for k in range(3): S.put(S.pop(), 39.75 + k * .12, .2)                        # ???
    for k in range(2): S.put(S.boing(), 41.2 + k * .15, .15)                      # HA HA
    S.put(S.heartbeat(3.0), 45.6, .25)
    S.put(S.chime(), 50.3, .35); S.put(S.sparkle(), 50.35, .25)                   # genggam tangan
    for at in (56.3, 56.9, 57.5, 58.1, 58.7, 59.3): S.put(S.kaching(), at, .2)
    S.put(S.pop(), 58.8, .3)
    S.put(S.sparkle(), 61.0, .4); S.put(S.chime(), 61.05, .35)                    # rak terisi
    for at in (62.9, 63.4, 63.9): S.put(S.kaching(), at, .2)
    S.put(S.pop(), 63.0, .35)
    for k in range(8): S.put(S.click()[:int(.08 * S.SR)], 64.6 + k * .3, .1)
    S.put(S.squeal(.3), 67.95, .1); S.put(S.pop(), 68.1, .3)                      # mau ngutang?!
    S.put(S.thud(), 73.45, .45); S.put(S.dun_dun(), 73.5, .4)                     # BELUM LUNAS
    for k in range(3): S.put(S.pop(), 76.3 + k * .12, .2)
    t_cta = VDUR + .25
    S.put(S.pop(), t_cta, .4); S.put(S.chime(), t_cta + .05, .35); S.put(S.pop(), t_cta + .85, .3); S.put(S.sparkle(), t_cta + .9, .3)
    S.put_amb(S.birds(17, 12), 0.0, .05); S.put_amb(S.birds(10, 8), 17.25, .05)
    S.put_amb(S.crickets(24.9), 30.85, .05)
    S.put_amb(S.lowpass(S.rng.standard_normal(int(4.2 * S.SR)), 700) * .3, 60.0, .07)   # keramaian pembeli
    S.put_amb(S.birds(11, 8), 64.25, .05)
    S.diam(4.95, 5.6)
