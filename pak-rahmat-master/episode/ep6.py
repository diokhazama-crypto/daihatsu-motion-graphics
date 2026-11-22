"""PAK RAHMAT EP 6 - JOGET ANTAR SEMBAKO (40 dtk, audio final pengguna: narasi + lagu 3,7-28,0 dtk).
Pak Rahmat joget mengikuti lagu sambil mengantar sembako dengan Gran Max; Bu Julit mengira stres & norak, ternyata orderan banjir.
Gerakan dikunci ke ketukan lagu (116,75 BPM, ketukan pertama 3,721 dtk). Tanpa suara(): audio final dipakai apa adanya.
Properti baru (kandidat aset): kios_bg (deretan kios/pasar), kabin (tampak depan kaca), speaker, not_musik, muatan bertingkat,
joget_po / nyetir_po (pose joget per ketukan)."""
from aset_dio import *
from aset_dasar import bulb_glow
import gaya

N = 6
VDUR = 39.7
DUR = 40.0
HOOK = ("DIKIRA STRES?!", 2.2)
PUNCH = (0.12, 21.0)
BERSAMBUNG = None
CTA = None                                  # penutup sendiri (tokoh tetap terlihat), lihat efek_atas
SUASANA = [(26.1, 28.7, 'warm'), (33.6, 99, 'warm')]
JULIT_SPEAK = [(28.76, 32.82)]

BPM = 116.75; BEAT = 60 / BPM; B0 = 3.721; SONG = (3.72, 28.0)

def beat(t):
    """(indeks ketukan, fase 0..1). Di luar lagu: ketukan tetap jalan pelan supaya gerak tidak berhenti mendadak."""
    u = (t - B0) / BEAT
    return int(math.floor(u)), u - math.floor(u)

def hentak(t):
    """0..1, puncak tepat di ketukan, turun cepat."""
    b, ph = beat(t)
    return math.exp(-ph * 5)

def lagu(t): return SONG[0] <= t < SONG[1]


# ------------------------------------------------------------ pose joget
JOGET = [((150, -40), (150, -40)),      # tangan ke atas
         ((100, -20), (40, -100)),      # kanan keluar, kiri di pinggang
         ((40, 70), (40, 70)),          # bahu naik, tangan turun
         ((40, -100), (100, -20))]      # kiri keluar

def joget_po(t, k=1.0, base=None, **kw):
    """joget per ketukan. k=1 heboh (tren TikTok), k~.35 goyang bahu kecil."""
    b, ph = beat(t)
    A = JOGET[b % 4]
    prev = JOGET[(b - 1) % 4]
    e = eout(clamp(ph / .3))
    aF = tuple(lerp(p, q, e) for p, q in zip(prev[0], A[0]))
    aB = tuple(lerp(p, q, e) for p, q in zip(prev[1], A[1]))
    if k < .6:                                  # goyang bahu kecil
        aF = (lerp(40, aF[0], k), lerp(10, aF[1], k)); aB = (lerp(-10, aB[0], k), lerp(10, aB[1], k))
    side = 1 if b % 2 == 0 else -1
    po = dict(aF=aF, aB=aB, eyes='happy', expr='grin', brows='up', tilt=side * 9 * k * (1 - ph * .6),
              mouth=.25 * abs(math.sin(t * 9)), look=(side * 3, -2))
    if base: po.update(base)
    po.update(kw)
    return po

def lompat(t, k=1.0):
    """offset y (negatif = naik) untuk badan memantul di ketukan."""
    b, ph = beat(t)
    return -22 * k * math.sin(math.pi * ph)

def nyetir_po(t, k=1.0):
    """di belakang setir: angguk kepala + goyang bahu ringan."""
    b, ph = beat(t)
    side = 1 if b % 2 == 0 else -1
    return {'aF': (110 + 8 * side * k, 20 - 6 * hentak(t) * k), 'aB': (100 - 8 * side * k, 15), 'eyes': 'happy', 'expr': 'grin',
            'brows': 'up', 'tilt': side * 6 * k * (1 - ph), 'look': (4, 3 * hentak(t) * k), 'mouth': .2 * abs(math.sin(t * 8)) * k}


# ------------------------------------------------------------ properti baru
def not_musik(c, x, y, t, n=4, a=1.0, s=1.0):
    """not balok melayang dari (x,y)."""
    for i in range(n):
        ph = (t * .7 + i / n) % 1
        xx = x + 60 * ph * s + 30 * math.sin(t * 3 + i * 2) * s; yy = y - 260 * ph * s
        al = a * (1 - ph) * min(1, ph * 5)
        if al <= .02: continue
        c.save(); c.translate(xx, yy); c.scale(s, s); c.rotate(.2 * math.sin(t * 4 + i))
        col = hx(['#FFE14D', '#F07AA8', '#7FD6FF', '#9BE36B'][i % 4])
        c.push_group()
        ell(c, 0, 0, 18, 13); fs(c, col, 4)
        c.rectangle(14, -62, 8, 62); fs(c, col, 3)
        if i % 2:
            ell(c, 52, -8, 18, 13); fs(c, col, 4); c.rectangle(66, -70, 8, 62); fs(c, col, 3)
            c.rectangle(14, -70, 60, 12); fs(c, col, 3)
        else:
            c.move_to(22, -62); c.curve_to(48, -50, 50, -30, 36, -18); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
        c.pop_group_to_source(); c.paint_with_alpha(al)
        c.restore()

def speaker(c, x, y, s, t):
    """speaker mobil berdenyut di ketukan."""
    p = hentak(t) if lagu(t) else 0
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -170, -170, 340, 340, 40); fs(c, hx('#2B2D33'), 8)
    for r in range(4):
        ell(c, 0, 0, 150 - r * 4, 150 - r * 4); c.set_source_rgba(1, 1, 1, .06); c.set_line_width(2); c.stroke()
    ell(c, 0, 0, 128 + 10 * p, 128 + 10 * p); fs(c, hx('#3B3F47'), 6)
    ell(c, 0, 0, 92 + 14 * p, 92 + 14 * p); fs(c, hx('#1B1C20'), 5)
    ell(c, 0, 0, 40 + 8 * p, 40 + 8 * p); fs(c, hx('#5A5F69'), 5)
    ell(c, -12, -14, 12, 9); fill(c, (1, 1, 1), .3)
    for k in range(3):
        rr = 170 + 60 * ((t * 2 + k / 3) % 1)
        ell(c, 0, 0, rr, rr); c.set_source_rgba(1, .9, .3, .35 * (1 - ((t * 2 + k / 3) % 1)) * (p + .3)); c.set_line_width(6); c.stroke()
    c.restore()

MUAT = [('k', 30, -250), ('k', 155, -250), ('k', 280, -250), ('k', 405, -250), ('s', 90, -320), ('s', 205, -320), ('s', 320, -320),
        ('k', 60, -390), ('k', 185, -390), ('s', 380, -390), ('k', 470, -330), ('s', 250, -440)]

def muatan(c, x, y, level):
    n = int(round(level * len(MUAT)))
    for kind, dx, dy in MUAT[:n]:
        if kind == 'k': E.kardus(c, x + dx, y + dy, 118, 78)
        else: lib.sack(c, x + dx + 55, y + dy + 30, 112, 72)

WIN = (557, -391, 782, -291)      # jendela kabin (koordinat lokal gran_max)

def mobil(c, t, x, y, level=1.0, driver=True, dpo=None, roda=0.0, notes=True):
    muatan(c, x, y, level)
    lib.gran_max(c, x, y, t, roda, False, 0, cargo=False)
    if driver:                                   # sopir dinaikkan sedikit supaya wajah & joget terlihat di jendela
        c.save(); c.translate(x, y)
        c.rectangle(WIN[0], WIN[1], WIN[2] - WIN[0], WIN[3] - WIN[1]); c.clip()
        person(c, 690, -8 + 6 * hentak(t) * lagu(t), 'rahmat', dpo or {'aF': (110, 20)}, s=.95, t=t)
        c.rectangle(WIN[0], WIN[1], WIN[2] - WIN[0], WIN[3] - WIN[1]); fill(c, (.8, .92, 1), .16)
        c.restore()
    if notes and driver and lagu(t):
        not_musik(c, x + 760, y - 330, t, 4, .95)

KIOS = [('WARUNG BU SITI', '#E5473B', '#FFF1D6'), ('KIOS BERKAH', '#2E86DE', '#E8F4FF'), ('TOKO MAKMUR', '#2EAD6B', '#E9FBEF'),
        ('KIOS PASAR 7', '#F07D2B', '#FFF0E0'), ('WARUNG MBAK ANI', '#9B4DCA', '#F5E9FF'), ('GROSIR JAYA', '#D7141A', '#FFF5D6')]

def kios_bg(c, t, start=0, n=6):
    """deretan kios/warung pasar (koordinat dunia sama dengan street: trotoar y 1340, jalan 1460-1760)."""
    g = cairo.LinearGradient(0, -900, 0, 1340)
    g.add_color_stop_rgb(0, *hx('#4FA8EE')); g.add_color_stop_rgb(1, *hx('#CFEFFF'))
    c.set_source(g); c.rectangle(-3000, -3000, 9000, 4340); c.fill()
    for k in range(6):
        cx_ = (k * 620 + t * 14) % 4400 - 1200; cy_ = 80 + (k * 97 % 280)
        for dx, dy, r in [(0, 0, 50), (55, -20, 60), (115, 0, 48), (60, 20, 50)]:
            ell(c, cx_ + dx, cy_ + dy, r, r * .85); fill(c, (1, 1, 1), .9)
    for i in range(-6, 14):                    # rumah latar
        bx = i * 300 + 40; hh = 180 + (i * 53 % 140)
        c.rectangle(bx, 680 - hh, 240, hh + 200); fs(c, hx(['#E8C27A', '#9CCFD8', '#F4A99B', '#C5E1A5'][i % 4]), 4)
        poly(c, [(bx - 20, 680 - hh), (bx + 260, 680 - hh), (bx + 120, 590 - hh)]); fs(c, hx('#A0522D'), 4)
    for j in range(n):
        name, col, wall = KIOS[(start + j) % len(KIOS)]
        x0 = -1000 + j * 470
        c.rectangle(x0, 760, 440, 580); fs(c, hx(wall), 5)
        rrect(c, x0 + 20, 560, 400, 110, 10); fs(c, hx('#FFFFFF'), 5)
        text(c, name, x0 + 220, 615, 40 if len(name) < 13 else 34, hx(col))
        for s_ in range(8):                    # kanopi bergaris + lekuk
            xx = x0 - 20 + s_ * 60
            c.rectangle(xx, 680, 60, 90); fill(c, hx(col) if s_ % 2 == 0 else (1, 1, 1))
            c.arc(xx + 30, 770, 30, 0, math.pi); fill(c, hx(col) if s_ % 2 == 0 else (1, 1, 1))
        c.rectangle(x0 - 20, 680, 480, 90); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
        for r in range(3):                     # rak barang
            yb = 900 + r * 110
            c.rectangle(x0 + 30, yb, 380, 10); fs(c, hx('#A8743F'), 3)
            for q in range(7):
                kind = ['botol', 'mie', 'gula', 'kaleng', 'box'][(q + r + j) % 5]
                E.product(c, x0 + 40 + q * 52, yb, kind, ['#E5473B', '#F2C230', '#2E86DE', '#2EAD6B', '#F07D2B'][(q + j) % 5])
        c.rectangle(x0 + 10, 1200, 420, 140); fs(c, hx('#B98550'), 5)       # meja depan
        for q in range(3):
            lib.sack(c, x0 + 90 + q * 130, 1190, 110, 66, rot=.05 * (q - 1))
    c.rectangle(-3000, 1340, 9000, 90); fs(c, hx('#C9C3B6'), 5)
    for r in range(3):
        for k in range(-60, 200):
            rrect(c, k * 46 + (r % 2) * 23, 1344 + r * 28, 44, 26, 4); c.set_source_rgba(0, 0, 0, .12); c.set_line_width(2); c.stroke()
    c.rectangle(-3000, 1430, 9000, 30); fill(c, hx('#5A5F66'))
    c.rectangle(-3000, 1460, 9000, 300); fill(c, hx('#55585E'))
    for k in range(-20, 60):
        c.rectangle(k * 240, 1600, 130, 14); fill(c, hx('#F2F2F2'), .85)
    c.rectangle(-3000, 1760, 9000, 3000); fill(c, hx('#6DBF5B'))
    for i in range(-20, 80):
        ell(c, i * 140 + 40, 1800 + (i * 31 % 50), 50, 22); fill(c, hx('#4FA343'))

def kotak(c, h):
    """kardus sembako dipegang (tengah kardus di tangan)."""
    c.rectangle(h[0] - 75, h[1] - 50, 150, 100); fs(c, hx('#D08F4C'), 6)
    c.rectangle(h[0] - 75, h[1] - 12, 150, 14); fill(c, hx('#F0CF8A'))
    c.rectangle(h[0] - 75, h[1] - 50, 150, 100); c.set_source_rgb(*OUT); c.set_line_width(6); c.stroke()

def orang(c, t, who, x, y=YS, s=1.0, flip=False, **po):
    po = dict(po); po.setdefault('who', who)
    E.person(c, x, y, who, po, s=s, t=t, flip=flip)

def uang(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-.2)
    rrect(c, -55, -28, 110, 56, 6); fs(c, hx('#F07AA8'), 4)
    ell(c, 0, 0, 16, 16); c.set_source_rgba(1, 1, 1, .6); c.set_line_width(3); c.stroke()
    c.restore()


# ------------------------------------------------------------ adegan
def sc_hook(c, t, t0):
    """Bu Julit melongo melihat Pak Rahmat joget di dalam Gran Max."""
    jpo = {'who': 'julit', 'x': 2470, 'y': YS, 'flip': True, 'aF': (38, -100), 'aB': (38, -100),
           'eyes': 'wide' if t < 1.4 else 'squint', 'expr': 'o' if t < 1.4 else 'pout', 'brows': 'up' if t < 1.4 else 'smug',
           'mouth': .5 if t < 1.4 else 0, 'look': (-6, 0), 'tilt': 0 if t < 1.4 else 6 * math.sin(t * 7)}
    dp = joget_po(t, .8, base={'aF': (150, -40 + 30 * math.sin(t * 9)), 'aB': (150, -40 - 30 * math.sin(t * 9))})
    street(c, t, [jpo], car=False)
    mobil(c, t, 1450, 1640, 1.0, True, dp)
    if t > 1.5: tanya(c, 2470, 880, t, 1.6)

def sc_speaker(c, t, t0):
    """lagu mulai: speaker di dasbor (koordinat layar)."""
    c.set_source_rgb(*hx('#2A2C31')); c.paint()
    rrect(c, -40, 1180, 1160, 900, 60); fs(c, hx('#3A3D44'), 8)                 # dasbor
    rrect(c, 120, 1260, 420, 150, 18); fs(c, hx('#16171A'), 6)                  # radio
    text(c, "LAGU ON", 330, 1335, 44, hx('#7FFFB0'), font="Inter Black")
    for k in range(8):
        hh = 20 + 60 * abs(math.sin(t * 7 + k * 1.3)) * (hentak(t) * .6 + .4)
        c.rectangle(170 + k * 46, 1395 - hh, 30, hh); fill(c, hx('#7FFFB0'), .8)
    speaker(c, 740, 900, 1.25 + .05 * hentak(t), t)
    not_musik(c, 760, 700, t, 5, clamp((t - t0) / .3), 1.3)

def kabin(c, t, dpo, ofs=0.0):
    """tampak depan kaca: Pak Rahmat menyetir (koordinat layar)."""
    g = cairo.LinearGradient(0, 0, 0, 1900)
    g.add_color_stop_rgb(0, *hx('#BFD9E8')); g.add_color_stop_rgb(1, *hx('#8DA9BA'))
    c.set_source(g); c.paint()
    rrect(c, 140, 380, 800, 420, 30); fs(c, hx('#9FD3F0'), 8)                  # kaca belakang -> bak muatan
    for k in range(5):
        E.kardus(c, 190 + k * 140, 760, 130, 90)
    lib.sack(c, 330, 650, 130, 80); lib.sack(c, 620, 650, 130, 80)
    rrect(c, 60, 820, 960, 900, 80); fs(c, hx('#6B4A3A'), 8)                  # jok
    rrect(c, 120, 880, 840, 120, 40); fill(c, hx('#7E5847'))
    person(c, 540, 1980 + ofs, 'rahmat', dpo, s=2.5, t=t)
    c.save(); c.translate(540, 1560)                                            # setir (proporsional dgn sopir)
    c.rotate(.12 * math.sin(t * 1.3))
    c.set_line_width(30); c.arc(0, 0, 175, 0, 2 * math.pi); c.set_source_rgb(*OUT); c.stroke()
    c.set_line_width(19); c.arc(0, 0, 175, 0, 2 * math.pi); c.set_source_rgb(*hx('#2B2D33')); c.stroke()
    for a in (math.pi / 2, math.pi * 1.15, -math.pi * .15):
        line(c, [(0, 0), (163 * math.cos(a), 163 * math.sin(a))], 22, hx('#2B2D33'))
    ell(c, 0, 0, 46, 46); fs(c, hx('#3A3D44'), 6)
    text(c, "D", 0, 0, 32, hx('#D7141A'))
    c.restore()
    c.rectangle(-50, 1680, 1180, 400); fs(c, hx('#3A3D44'), 8)                # dasbor
    speaker(c, 900, 1790, .42, t)
    for sx in (-40, 1040):                                                      # pilar kaca depan
        poly(c, [(sx - 60, -50), (sx + 60, -50), (sx + 120 * (1 if sx < 0 else -1) + 60, 1650), (sx - 60, 1650)]); fs(c, hx('#E9ECEF'), 8)
    c.rectangle(-50, -50, 1180, 170); fs(c, hx('#E9ECEF'), 8)
    text(c, "GRAN MAX", 540, 60, 54, hx('#D7141A'), OUT, 6)
    for k in range(3):                                                          # kilau kaca
        x0 = (t * 260 + k * 420) % 1700 - 300
        poly(c, [(x0, 140), (x0 + 60, 140), (x0 - 240, 1600), (x0 - 300, 1600)]); fill(c, (1, 1, 1), .07)
    if lagu(t): not_musik(c, 880, 1560, t, 3, .9)

def sc_kabin(c, t, t0):
    k = .6 if t < 5.2 else 1.0
    kabin(c, t, nyetir_po(t, k), 8 * hentak(t))

def cam_jalan(t):
    x = car_x_jalan(t)
    return (x + 640, 1150, 1.0)

def car_x_jalan(t): return lerp(-500, 1500, (t - 7.2) / 1.9)

def sc_jalan(c, t, t0):
    """Gran Max dari samping melaju di depan deretan kios."""
    x = car_x_jalan(t)
    kios_bg(c, t, 2)
    mobil(c, t, x, 1640, 1.0, True, nyetir_po(t), roda=x / 55)
    for k in range(6):
        ph = (t * 3 + k / 6) % 1
        P.puff(c, x + 60 - ph * 300, 1610 - ph * 50, 14 + ph * 40, .35 * (1 - ph))

PARK = (-520, 1640)          # Gran Max berhenti di kiri, pintu sopir ~x 330

def sc_antar1(c, t, t0):
    """pengantaran pertama: turun bawa kardus sambil joget, pemilik warung tertawa & bayar."""
    kios_bg(c, t, 0)
    mobil(c, t, *PARK, .85, driver=t < 9.5, dpo=nyetir_po(t))
    walk = ease((t - 9.5) / 1.5)
    rx = lerp(380, 900, walk)
    kasih = t > 11.0
    rpo = joget_po(t, .55, step=1 if 9.5 < t < 11.0 else 0,
                   hold=None if kasih else kotak,
                   aF=(95, -10) if (t < 11.0 and t > 9.5) else None)
    if rpo['aF'] is None: del rpo['aF']
    if t >= 9.5: orang(c, t, 'rahmat', rx, YS + lompat(t, .5), **rpo)
    opo = dict(aF=(95, -10) if kasih else (40, 10), aB=(20, 0), eyes='happy', expr='grin', brows='up', look=(-6, 0),
               mouth=.35 * abs(math.sin(t * 10)), hold=(lambda c, h: uang(c, h[0], h[1], .9)) if t > 11.4 else
               (kotak if kasih else None))
    orang(c, t, 'b3', 1170, flip=True, **opo)
    for j, ta in enumerate((11.5, 11.75)):
        coin_pop(c, 1130 + j * 60, 1000, t, ta)

def sc_balik(c, t, t0):
    """kembali ke mobil sambil joget, jempol, lalu berangkat."""
    kios_bg(c, t, 0)
    pergi = clamp((t - 14.2) / .9)
    cx = PARK[0] + 1800 * pergi ** 2
    mobil(c, t, cx, PARK[1], .65, driver=t >= 14.2, dpo=nyetir_po(t), roda=cx / 55)
    if t < 14.2:
        rx = lerp(900, 400, ease((t - 12.1) / 1.4))
        jempol = t > 13.5
        po = joget_po(t, .7, step=1 if t < 13.5 else 0)
        if jempol: po.update(aF=(100, -15), thumb=True, eyes='happy', expr='grin', tilt=0)
        orang(c, t, 'rahmat', rx, YS + lompat(t, .6), flip=not jempol, **po)
        if jempol: spark(c, rx + 150, 1010, 24, pop(t, 13.55, .2))
    orang(c, t, 'b3', 1170, flip=True, aF=(100, -30) if t > 13.4 else (40, 10), aB=(20, 0), eyes='happy', expr='grin', look=(-6, 0),
          hold=kotak)

def car_x_julit(t): return lerp(400, 2700, (t - 15.1) / 2.9)

def sc_lewat_julit(c, t, t0):
    """Gran Max lewat depan rumah Bu Julit; dia melipat tangan, geleng-geleng."""
    x = car_x_julit(t)
    jpo = {'who': 'julit', 'x': 2350, 'y': YS, 'flip': True, 'aF': (38, -100), 'aB': (38, -100), 'eyes': 'squint', 'brows': 'smug',
           'expr': 'pout', 'tilt': 9 * math.sin(t * 9), 'look': (-6 if x + 700 < 2350 else 6, 0)}
    street(c, t, [jpo], car=False)
    mobil(c, t, x, 1640, .65, True, nyetir_po(t), roda=x / 55)

def cam_lewat(t):
    x = car_x_julit(t)
    return (clamp(x + 700, 1500, 2350), 1150, 1.05)

def sc_pasar(c, t, t0):
    """area pasar: kios-kios menunggu, barang diserahkan per 2 ketukan."""
    kios_bg(c, t, 3)
    mobil(c, t, -900, 1640, .5, driver=False)
    stops = [(18.0, 'b1', 330, 'k'), (19.0, 'b2', 790, 's'), (20.0, 'b4', 1250, 'm')]
    i = max(j for j, s_ in enumerate(stops) if t >= s_[0] or j == 0)
    tgt = stops[i][2] - 170
    rx = lerp(stops[i - 1][2] - 170 if i > 0 else -100, tgt, eout((t - stops[i][0]) / .45))
    bawa = {'k': kotak,
            's': lambda c, h: lib.sack(c, h[0], h[1] - 10, 130, 80),
            'm': lambda c, h: (E.product(c, h[0] - 50, h[1] + 40, 'botol', '#F2C230', 50, 100), E.product(c, h[0] + 4, h[1] + 40, 'gula', '#2E86DE', 54, 100))}
    for j, (ta, who, x, kind) in enumerate(stops):
        got = t >= ta + .4
        orang(c, t, who, x, flip=True, aF=(95, -10) if got else (40, 10), aB=(20, 0), eyes='happy' if got else 'open',
              expr='grin' if got else 'smile', look=(-6, 0), hold=bawa[kind] if got else None, step=0)
        if got: coin_pop(c, x - 20, 1000, t, ta + .5)
    hold_now = None if t >= stops[i][0] + .4 else bawa[stops[i][3]]
    po = joget_po(t, .5, aF=(95, -10), hold=hold_now, step=1 if (t - stops[i][0]) < .45 else 0)
    orang(c, t, 'rahmat', rx, YS + lompat(t, .4), **po)

def sc_joget(c, t, t0):
    """PUNCAK: joget paling heboh, dua pelanggan ikut menirukan."""
    kios_bg(c, t, 4)
    mobil(c, t, -1100, 1640, .4, driver=False)
    orang(c, t, 'b1', 740, YS + lompat(t - BEAT * .25, .8), flip=False, **joget_po(t - BEAT * .25, .85, eyes='happy', expr='grin'))
    orang(c, t, 'b4', 1440, YS + lompat(t - BEAT * .25, .8), flip=True, **joget_po(t - BEAT * .25, .85, eyes='happy', expr='grin'))
    orang(c, t, 'rahmat', 1090, YS + lompat(t, 1.2), **joget_po(t, 1.0, step=beat(t)[0] % 2))
    if t > 21.4:
        for j in range(2):
            card(c, 700 + j * 780, 760 - 40 * j, pop(t, 21.5 + j * .5, .2), "HA HA", hx('#FFE14D'), 46, rot=.1 - j * .2)
    not_musik(c, 1250, 900, t, 4, .9)

MONT = [(24.0, 5, 'serah'), (24.51, 1, 'bayar'), (25.03, 2, 'serah'), (25.54, 0, 'senyum')]

def sc_montase(c, t, t0):
    """potongan cepat tiap ketukan: berhenti, serahkan, bayar, senyum."""
    i = max(j for j, m in enumerate(MONT) if t >= m[0])
    ta, kio, kind = MONT[i]
    kios_bg(c, t, kio)
    mobil(c, t, -560, 1640, .25 - .05 * i, driver=False)
    if kind == 'serah':
        orang(c, t, 'rahmat', 860, **joget_po(t, .45, aF=(95, -10), hold=kotak))
        orang(c, t, ['b2', 'b3'][i % 2], 1240, flip=True, aF=(95, -10), eyes='happy', expr='grin', look=(-6, 0))
    elif kind == 'bayar':
        orang(c, t, 'rahmat', 860, aF=(95, -10), eyes='happy', expr='grin', look=(6, 0))
        orang(c, t, 'b1', 1240, flip=True, aF=(95, -10), eyes='happy', expr='grin', look=(-6, 0),
              hold=lambda c, h: uang(c, h[0], h[1], .9))
        coin_pop(c, 1050, 1000, t, ta + .1)
    else:
        orang(c, t, 'rahmat', 1000, **joget_po(t, .45, aF=(100, -15), thumb=True))
        spark(c, 1150, 1000, 24, pop(t, ta + .05, .2))

def cam_montase(t):
    i = max(j for j, m in enumerate(MONT) if t >= m[0])
    return [(1050, 1150, 1.2), (1050, 1120, 1.45), (1050, 1150, 1.2), (1000, 1120, 1.5)][i]

def sc_menang(c, t, t0):
    """pesanan terakhir: bak hampir kosong."""
    kios_bg(c, t, 5)
    mobil(c, t, -560, 1640, .08, driver=False)
    orang(c, t, 'rahmat', 860, **joget_po(t, .4, aF=(95, -10) if t < 26.9 else (100, -15), thumb=t >= 26.9,
                                          hold=kotak if t < 26.6 else None))
    orang(c, t, 'b2', 1240, flip=True, aF=(95, -10), eyes='happy', expr='grin', look=(-6, 0),
          hold=kotak if t >= 26.6 else None)
    card(c, 180, 820, show(t, 26.2, 27.3), "PESANAN TERAKHIR!", hx('#2EAD6B'), 44, fg=(1, 1, 1), rot=.05)

def sc_julit_jauh(c, t, t0):
    """Bu Julit melihat dari jendela, mata membesar."""
    jp = {'x': 2160, 'dy': 0, 'aF': (60, 80), 'aB': (40, 10), 'eyes': 'wide', 'expr': 'o', 'brows': 'up', 'mouth': .5, 'look': (-6, 0)}
    street(c, t, [], car=False, toko='normal')
    E.rumah_julit(c, t, {'julit_win': jp, 'curtain': .5})
    exclaim(c, 2140, 860, 1.0, pop(t, 27.6, .25))

def show(t, t0, t1, d=.3): return pop(t, t0, d) * (1 - ease((t - t1) / d))

def sc_nyinyir(c, t, t0):
    """'Halah... norak banget!': Bu Julit ketus, menunjuk mobil."""
    m = talk(t, JULIT_SPEAK)
    jpo = {'who': 'julit', 'x': 2350, 'y': YS, 'flip': True, 'aF': (100, -15) if t > 29.2 else (38, -100), 'aB': (38, -100),
           'eyes': 'squint', 'brows': 'smug', 'expr': 'pout', 'mouth': m,
           'tilt': 5 * math.sin(t * 6), 'look': (-6, 0)}
    street(c, t, [jpo], car=False, toko='normal')
    mobil(c, t, 400, 1640, .05, True, nyetir_po(t, .4), notes=False)
    card(c, 2300, 700, show(t, 31.9, 33.5), "NORAK!", hx('#F07AA8'), 80, rot=.08)

def sc_ending(c, t, t0):
    """pesanan baru berdatangan; Bu Julit bengong & iri; Pak Rahmat goyang bahu kecil."""
    people = [{'who': 'b1', 'x': 640, 'y': YS, 'aF': (40, 10), 'expr': 'grin', 'eyes': 'happy', 'look': (5, 0),
               'hold': lambda c, h: E.kresek(c, h[0], h[1], hx('#E5473B'))},
              dict(joget_po(t, .35, aF=(100, -15), thumb=t > 37.0), who='rahmat', x=1100, y=YS),
              {'who': 'julit', 'x': 1480, 'y': YS, 'flip': True, 'aF': (38, -100), 'aB': (38, -100),
               'eyes': 'wide' if t < 36.0 else 'squint', 'expr': 'o' if t < 36.0 else 'pout', 'brows': 'up' if t < 36.0 else 'angry',
               'mouth': .4 if t < 36.0 else 0, 'look': (-6, 0), 'tilt': 4 * math.sin(t * 5)}]
    street(c, t, people, car=False, toko='normal')
    if t > 36.0: gloom(c, 1480, YS, 1.0, .7)

def efek_ending_hp(c, t):
    if not (33.6 <= t < 36.0): return
    k = eout((t - 33.7) / .35) * (1 - ease((t - 35.7) / .3))
    msgs = [(33.9, "Toko Makmur", "Pak, besok kirim\n20 dus mie ya", False), (34.4, "Warung Bu Siti", "Beras 10 karung!", False),
            (34.9, "Kios Berkah", "Minyak 5 dus pak", False), (35.3, "Grosir Jaya", "Tambah orderan!", False)]
    if k > .03:
        c.save(); c.translate(W / 2 - 40, lerp(2400, 820, k)); c.rotate(-.04)
        E.phone(c, 0, 0, .95, msgs, t, header="ORDERAN SEMBAKO", group=False)
        c.restore()
        for j, ta in enumerate((34.0, 34.5, 35.0, 35.4)):
            card(c, 860, 360 + j * 0, pop(t, ta, .2) * (1 - ease((t - ta - .4) / .2)), "+1 ORDER", hx('#2EAD6B'), 40, fg=(1, 1, 1))

def penutup(c, t):
    """TIM JOGET ATAU TIM NYINYIR? + TULIS DI KOMENTAR! + FOLLOW UNTUK EP 7 (tokoh tetap terlihat)."""
    if t < 35.86: return
    c.set_source_rgba(0, 0, 0, .3 * clamp((t - 35.86) / .3)); c.paint()
    k = max(pop(t, 35.9, .35), .02)
    c.save(); c.translate(W / 2 - 30, 560); c.scale(k, k); c.rotate(-.04)
    rrect(c, -450, -150, 900, 300, 34); fs(c, (1, 1, 1), 10)
    text(c, "ATAU", 0, -40, 30, OUT)
    for i, (lbl, col) in enumerate((("TIM JOGET", '#2EAD6B'), ("TIM NYINYIR?", '#D7141A'))):
        ki = max(pop(t, 36.4 + i * .9, .3), .02)
        c.save(); c.translate(-240 + i * 480, -40); c.scale(ki, ki); c.rotate(.05 * math.sin(t * 6 + i * 2))
        rrect(c, -170, -66, 340, 132, 26); fs(c, hx(col), 8)
        text(c, lbl, 0, 0, 44 if i == 0 else 40, (1, 1, 1), OUT, 6)
        c.restore()
    text(c, "KAMU TIM YANG MANA?", 0, 90, 40, hx('#D7141A'))
    c.restore()
    k2 = pop(t, 38.3, .3)
    if k2 > .03:
        c.save(); c.translate(W / 2 - 30, 820); c.scale(k2, k2); c.rotate(.03)
        rrect(c, -360, -66, 720, 132, 30); fs(c, hx('#FFE14D'), 9)
        text(c, "TULIS DI KOMENTAR!", 0, 0, 62, OUT)
        c.restore()
    k3 = pop(t, 38.8, .3)
    if k3 > .03:
        c.save(); c.translate(W / 2 - 30, 980); c.scale(k3 * .8, k3 * .8)
        rrect(c, -330, -60, 660, 120, 60); fs(c, (1, 1, 1), 8)
        text(c, "FOLLOW UNTUK EP 7", -30, 0, 46, OUT)
        bx = 270 + 10 * math.sin(t * 8)
        poly(c, [(bx - 22, -26), (bx + 20, 0), (bx - 22, 26)]); fs(c, OUT, 2)
        c.restore()

SCENES = [
    (0.0, 3.72, sc_hook, [(0, 2170, 1330, 1.6), (1.4, 2190, 1320, 1.55), (3.72, 2150, 1300, 1.35)]),
    (3.72, 4.75, sc_speaker, 'split'),
    (4.75, 7.2, sc_kabin, 'split'),
    (7.2, 9.1, sc_jalan, cam_jalan),
    (9.1, 12.1, sc_antar1, [(9.1, 560, 1150, 1.0), (10.6, 800, 1150, 1.08), (12.1, 860, 1150, 1.12)]),
    (12.1, 15.1, sc_balik, [(12.1, 820, 1150, 1.1), (13.6, 600, 1150, 1.18), (15.1, 760, 1150, 1.0)]),
    (15.1, 18.0, sc_lewat_julit, cam_lewat),
    (18.0, 21.0, sc_pasar, [(18.0, 640, 1120, .92), (21.0, 760, 1120, .95)]),
    (21.0, 24.0, sc_joget, [(21.0, 1090, 1140, 1.05), (22.5, 1090, 1150, 1.12), (24.0, 1090, 1150, 1.15)]),
    (24.0, 26.1, sc_montase, cam_montase),
    (26.1, 27.4, sc_menang, [(26.1, 900, 1150, 1.1), (27.4, 900, 1150, 1.15)]),
    (27.4, 28.7, sc_julit_jauh, [(27.4, 2150, 1020, 1.5), (28.7, 2150, 1020, 1.6)]),
    (28.7, 33.6, sc_nyinyir, [(28.7, 1700, 1150, 1.0), (29.4, 2320, 1110, 1.7), (33.6, 2320, 1110, 1.78)]),
    (33.6, DUR + 1, sc_ending, [(33.6, 1120, 1150, 1.05), (DUR, 1120, 1150, 1.12)]),
]


# ------------------------------------------------------------ efek & label
def efek_bawah(c, t):
    E.focus_lines(c, t, 0.1, 0.9, cy=H * .45)
    E.focus_lines(c, t, 21.0, 21.9, cy=H * .5)
    E.focus_lines(c, t, 29.4, 30.1, cy=H * .42)

def efek_atas(c, t):
    if 3.75 <= t < 4.75: E.pill(c, "PLAY LAGU!", t, 3.8, y=330, col=hx('#7FFFB0'))
    if 9.15 <= t < 10.6: E.pill(c, "ANTAR PERTAMA", t, 9.2, y=330, col=hx('#FFE14D'))
    if 18.05 <= t < 19.6: E.pill(c, "PESANAN RAME!", t, 18.1, y=330, col=hx('#2EAD6B'), fg=(1, 1, 1))
    if 21.0 <= t < 24.0: E.pill(c, "GOYANG DULU!", t, 21.05, y=330, col=hx('#F07AA8'))
    if 27.45 <= t < 28.7: E.pill(c, "LHO, LARIS?!", t, 27.5, y=330, col=hx('#FFE14D'))
    efek_ending_hp(c, t)
    penutup(c, t)

def vignette(t): return .34
# tanpa suara(): audio final pengguna dipakai apa adanya
