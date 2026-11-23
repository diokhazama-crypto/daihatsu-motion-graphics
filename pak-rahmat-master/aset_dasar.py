import cairo, math, json, random, sys, subprocess
import numpy as np

W, H, FPS = 1080, 1920, 30
DUR = 71.64
NF = int(DUR * FPS)
OUT = (0.09, 0.07, 0.09)

def hx(s):
    s = s.lstrip('#'); return tuple(int(s[i:i+2], 16) / 255 for i in (0, 2, 4))

def clamp(x, a=0, b=1): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def lerp(a, b, k): return a + (b - a) * k
def pop(t, t0, d=0.3):
    if t < t0: return 0.0
    x = (t - t0) / d
    if x >= 1: return 1.0
    c1 = 2.2; c3 = c1 + 1
    return max(0.02, 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2)

# ---------------------------------------------------------------- audio envelope
raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", "audio.wav", "-ac", "1", "-ar", "24000", "-f", "s16le", "-"],
                     capture_output=True).stdout
A = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
hop = 24000 // FPS
# master: amplop dihitung sepanjang audio episode (dulu dipotong ke DUR ep 1 = 71,64 dtk; audio yang lebih
# pendek menghasilkan NaN sehingga gerak mulut saat bicara selalu 0).
_nfa = max(1, len(A) // hop + 2)
ENV = np.array([np.sqrt(np.mean(A[i*hop:(i+1)*hop] ** 2) + 1e-9) if i * hop < len(A) else 0.0 for i in range(_nfa)])
ENV = ENV / max(float(np.percentile(ENV, 95)), 1e-6)
ENV = np.clip(np.nan_to_num(ENV), 0, 1)

def env(t):
    i = int(t * FPS)
    return float(ENV[min(i, len(ENV) - 1)])

JULIT_TALK = [(0.6, 7.2), (19.1, 22.4), (49.0, 53.95), (54.1, 56.9)]
def julit_mouth(t):
    for a, b in JULIT_TALK:
        if a <= t <= b:
            e = env(t)
            return clamp((e - 0.12) * 1.4) * (0.6 + 0.4 * abs(math.sin(t * 19)))
    return 0.0

# ---------------------------------------------------------------- drawing helpers
SHADE = False
def fs(c, fill, lw=6, alpha=1.0):
    if len(fill) == 4: c.set_source_rgba(*fill)
    else: c.set_source_rgba(*fill, alpha)
    c.fill_preserve()
    if SHADE and alpha > 0.6:
        x0, y0, x1, y1 = c.fill_extents()
        if x1 - x0 > 6:
            g = cairo.LinearGradient(x0, y0, x0 + (x1 - x0) * .6, y1)
            g.add_color_stop_rgba(0, 1, .97, .9, .22); g.add_color_stop_rgba(.45, 1, 1, 1, 0)
            g.add_color_stop_rgba(.7, .1, .05, .2, 0); g.add_color_stop_rgba(1, .12, .04, .2, .26)
            c.set_source(g); c.fill_preserve()
    c.set_source_rgb(*OUT); c.set_line_width(lw); c.stroke()

def fill(c, col, a=1.0):
    c.set_source_rgba(*col, a); c.fill()

def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()

def ell(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(rx, ry); c.new_sub_path(); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()

def poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.close_path()

def line(c, pts, w, col, outline=True):
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    if outline:
        c.move_to(*pts[0])
        for p in pts[1:]: c.line_to(*p)
        c.set_source_rgb(*OUT); c.set_line_width(w + 11); c.stroke()
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.set_source_rgb(*col); c.set_line_width(w); c.stroke()

def text(c, s, x, y, size, col=(1, 1, 1), stroke=OUT, sw=0, font="Inter Black", align='c', alpha=1.0):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    ext = c.text_extents(s)
    if align == 'c': tx = x - ext.width / 2 - ext.x_bearing
    elif align == 'l': tx = x
    else: tx = x - ext.width
    ty = y - ext.height / 2 - ext.y_bearing
    c.new_path(); c.move_to(tx, ty); c.text_path(s)
    if sw:
        c.set_source_rgba(*stroke, alpha); c.set_line_width(sw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    c.set_source_rgba(*col, alpha); c.fill()
    return ext.x_advance

SKIN_A = hx('#D39B6B'); SKIN_B = hx('#F1C6A0'); SKIN_C = hx('#E3AE85')

CH = {
 'rahmat': dict(skin=SKIN_A, shirt=hx('#2F8F5B'), pants=hx('#5A4232'), hair='peci', mus=True, kind='man'),
 'julit': dict(skin=SKIN_B, dress=hx('#9B4DCA'), dots=hx('#F7A8D8'), hair='rollers', lips=True, kind='daster'),
 'friend': dict(skin=SKIN_C, dress=hx('#2EAD6B'), dots=hx('#FFF3B0'), hair='hijab', hij=hx('#F5C02E'), kind='daster'),
 'anak': dict(skin=SKIN_A, shirt=hx('#E5473B'), pants=hx('#2C3E66'), hair='spiky', kind='man'),
 'b1': dict(skin=SKIN_C, shirt=hx('#F2C230'), pants=hx('#34495E'), hair='short', kind='man'),
 'b2': dict(skin=SKIN_B, dress=hx('#3B82D6'), dots=hx('#BFE3FF'), hair='hijab', hij=hx('#F07AA8'), kind='daster'),
 'b3': dict(skin=SKIN_A, shirt=hx('#F07D2B'), pants=hx('#3D3D3D'), hair='cap', kind='man'),
 'b4': dict(skin=SKIN_B, dress=hx('#E5473B'), dots=hx('#FFD1C8'), hair='hijab', hij=hx('#7A4FD1'), kind='daster'),
}
# Pak Bos (ep 7+): tokoh orisinal, baju safari krem, badan agak gendut, rambut hitam disisir rapi
CH['pakbos'] = dict(skin=hx('#D7A07A'), shirt=hx('#D8C9A2'), pants=hx('#B9A87F'), hair='slick', kind='man', safari=True,
                    collar=True, collar_col=hx('#CDBD93'), long=True, foot='shoe', shoe_col=hx('#3B2A1E'), cuff=hx('#CDBD93'))

def arm(c, sx, sy, a1, a2, sleeve, skin, L=70, w=24, long=False, watch=None, gelang=False, cuff=None, hd=False):
    r1 = math.radians(a1); r2 = math.radians(a1 + a2)
    ex, ey = sx + L * math.sin(r1), sy + L * math.cos(r1)
    hx_, hy_ = ex + L * math.sin(r2), ey + L * math.cos(r2)
    line(c, [(sx, sy), (ex, ey), (hx_, hy_)], w + (8 if long else 0), sleeve if long else skin)
    mx, my = sx + 0.62 * (ex - sx), sy + 0.62 * (ey - sy)
    if not long:
        line(c, [(sx, sy), (mx, my)], w + 10, sleeve)
        if cuff:
            m2x, m2y = sx + 0.55 * (ex - sx), sy + 0.55 * (ey - sy)
            c.move_to(m2x, m2y); c.line_to(mx, my); c.set_source_rgb(*cuff); c.set_line_width(w + 10); c.set_line_cap(cairo.LINE_CAP_BUTT); c.stroke()
            c.set_line_cap(cairo.LINE_CAP_ROUND)
    wx, wy = ex + .78 * (hx_ - ex), ey + .78 * (hy_ - ey)
    ang = math.atan2(hy_ - ey, hx_ - ex)
    if watch:
        c.save(); c.translate(wx, wy); c.rotate(ang)
        rrect(c, -6, -15, 12, 30, 3); fs(c, hx('#2B2B2B'), 3)
        ell(c, 0, -10, 8, 8); fs(c, watch, 3)
        c.restore()
    if gelang:
        c.save(); c.translate(wx, wy); c.rotate(ang)
        for k in (-4, 4):
            rrect(c, k - 2.5, -15, 5, 30, 2.5); fs(c, hx('#F2C230'), 2)
        c.restore()
    ell(c, hx_, hy_, 17, 17); fs(c, skin, 5)
    if hd:
        ang2 = math.atan2(hy_ - ey, hx_ - ex)
        c.save(); c.translate(hx_, hy_); c.rotate(ang2 - math.pi / 2)
        for k in (-7, 0, 7):
            c.move_to(k, 4); c.line_to(k * 1.1, 14); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(2); c.stroke()
        c.restore()
        # elbow crease on skin + sleeve hem stitch
        c.move_to(ex - 6, ey - 3); c.curve_to(ex - 2, ey + 2, ex + 2, ey + 2, ex + 6, ey - 3); c.set_source_rgba(0, 0, 0, .22); c.set_line_width(2); c.stroke()
        mx2, my2 = sx + 0.58 * (ex - sx), sy + 0.58 * (ey - sy)
        c.save(); c.translate(mx2, my2); c.rotate(math.atan2(ey - sy, ex - sx) + math.pi / 2)
        c.move_to(-16, 0); c.line_to(16, 0); c.set_source_rgba(1, 1, 1, .35); c.set_line_width(1.5); c.set_dash([3, 3]); c.stroke(); c.set_dash([])
        for k in (-10, 4):
            c.move_to(k, -18); c.curve_to(k + 4, -10, k + 2, -6, k + 6, -2); c.set_source_rgba(0, 0, 0, .25); c.set_line_width(2); c.stroke()
        c.restore()
    else:
        c.move_to(hx_ - 8, hy_ + 2); c.line_to(hx_ + 4, hy_ + 6); c.set_source_rgba(0, 0, 0, .25); c.set_line_width(2); c.stroke()
    return hx_, hy_

def foot(c, x, y, P, ex):
    kind = P.get('foot', 'sandal' if ex else 'shoe')
    if kind == 'sneaker':
        ell(c, x + 4, y + 2, 30, 14); fs(c, hx('#1F2F6B'), 5)
        c.rectangle(x - 26, y + 6, 62, 6); fill(c, (1, 1, 1))
        c.rectangle(x - 26, y + 11, 62, 3); fill(c, hx('#E23A3A'))
        c.rectangle(x - 26, y + 14, 62, 4); fill(c, hx('#B97A3E'))
        for k in range(3):
            c.move_to(x - 6 + k * 9, y - 9); c.line_to(x + 4 + k * 9, y + 6); c.set_source_rgb(1, 1, 1); c.set_line_width(3.5); c.stroke()
        ell(c, x - 20, y - 2, 6, 6); fill(c, (1, 1, 1), .9)
        for k in range(3):
            c.move_to(x - 16 + k * 6, y - 11 + k); c.line_to(x - 10 + k * 6, y - 7 + k); c.set_source_rgb(1, 1, 1); c.set_line_width(2); c.stroke()
        if P.get('hd'):
            rrect(c, x - 27, y - 8, 5, 10, 2); fill(c, hx('#E23A3A'))                       # heel tab
            c.move_to(x - 18, y - 13); c.curve_to(x - 14, y - 20, x - 6, y - 20, x - 2, y - 13); c.set_source_rgb(*hx('#1F2F6B')); c.set_line_width(4); c.stroke()  # tongue
            for k in range(2):
                c.move_to(x - 18 + k * 7, y - 12); c.line_to(x - 9 + k * 7, y - 8); c.move_to(x - 18 + k * 7, y - 8); c.line_to(x - 9 + k * 7, y - 12)
                c.set_source_rgb(1, 1, 1); c.set_line_width(1.5); c.stroke()
            for k in range(8):
                c.move_to(x - 24 + k * 7, y + 18); c.line_to(x - 22 + k * 7, y + 15); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(1.5); c.stroke()
        return
    if kind == 'sandal':
        ell(c, x + 2, y + 4, 28, 9); fs(c, P.get('sandal_col', hx('#3B6EA8')), 4)
        ell(c, x - 2, y - 3, 20, 10); fs(c, P['skin'], 3)
        c.move_to(x - 8, y + 2); c.curve_to(x - 2, y - 12, x + 6, y - 12, x + 10, y + 2)
        c.set_source_rgb(*P.get('sandal_col', hx('#3B6EA8'))); c.set_line_width(5); c.stroke()
        for k in range(4):
            ell(c, x + 14 + k * 3, y - 2 - k * .5, 3, 3); fill(c, (0, 0, 0), .18)
    else:
        ell(c, x, y, 26, 13); fs(c, P.get('shoe_col', hx('#2B2B2B')), 5)
        c.rectangle(x - 26, y + 6, 52, 6); fill(c, hx('#111111'))
        for k in range(3):
            c.move_to(x - 2 + k * 6, y - 10); c.line_to(x + 4 + k * 6, y - 4); c.set_source_rgba(1, 1, 1, .6); c.set_line_width(2); c.stroke()

def face(c, P, hy, po, t):
    fx = 12
    skin = P['skin']
    mouth = po.get('mouth', 0); eyes = po.get('eyes', 'open'); brows = po.get('brows', 'normal')
    lx, ly = po.get('look', (3, 0))
    expr = po.get('expr', 'smile')
    hair = P.get('hair')
    if hair == 'hijab':
        hc = P['hij']
        sw = 7 * math.sin(t * 2.2) if SHADE else 0
        c.move_to(-70, hy + 40); c.curve_to(-110 + sw, hy + 120, -60 + sw, hy + 140, 0 + sw, hy + 130)
        c.curve_to(70 + sw, hy + 140, 110 + sw, hy + 120, 75, hy + 40); c.close_path(); fs(c, hc, 6)
        ell(c, 0, hy, 82, 84); fs(c, hc, 6)
        ell(c, fx * 0.6, hy + 8, 56, 60); fs(c, skin, 4)
        c.save(); ell(c, fx * 0.6, hy + 8, 56, 60); c.clip()
        c.rectangle(-70, hy - 60, 140, 16); fill(c, P.get('ciput', hx('#FFFFFF')), .95)
        c.restore()
        c.move_to(-50, hy + 30); c.curve_to(-40, hy + 80, 40, hy + 80, 56, hy + 30)
        c.set_source_rgba(0, 0, 0, .18); c.set_line_width(4); c.stroke()
        if P.get('bros'):
            ell(c, fx + 4, hy + 78, 10, 10); fs(c, P['bros'], 3)
            ell(c, fx + 2, hy + 75, 3, 3); fill(c, (1, 1, 1), .9)
    else:
        ell(c, -54, hy + 6, 15, 18); fs(c, skin, 5)
        if hair == 'rollers':
            ell(c, -62, hy - 28, 30, 30); fs(c, hx('#3A2418'), 6)
        ell(c, 0, hy, 66, 66); fs(c, skin, 6)
    # hair on top
    if hair == 'peci':
        pl = po.get('peci_lift', 0) * (18 + 4 * math.sin(t * 30))
        c.save(); c.translate(0, -pl); c.rotate(po.get('peci_lift', 0) * .08)
        poly(c, [(-60, hy - 30), (60, hy - 30), (54, hy - 82), (-54, hy - 82)]); fs(c, hx('#1B1B1F'), 6)
        c.rectangle(-55, hy - 46, 108, 6); fill(c, hx('#3A3A44'))
        if P.get('peci_band'):
            c.rectangle(-58, hy - 40, 116, 8); fill(c, P['peci_band'], .9)
            for k in range(-5, 6):
                poly(c, [(k * 10, hy - 40), (k * 10 + 5, hy - 36), (k * 10, hy - 32), (k * 10 - 5, hy - 36)]); fill(c, (0, 0, 0), .35)
        c.restore()
        c.move_to(-62, hy - 28); c.curve_to(-66, hy - 5, -62, hy + 10, -58, hy + 14); c.set_source_rgb(*OUT); c.set_line_width(7); c.stroke()
    elif hair == 'rollers':
        c.move_to(-66, hy + 2); c.curve_to(-70, hy - 80, 60, hy - 90, 66, hy - 12); c.curve_to(30, hy - 40, -20, hy - 40, -66, hy + 2)
        c.close_path(); fs(c, hx('#3A2418'), 6)
        jg = po.get('jiggle', 0)
        for i_r, (rx, ry) in enumerate([(-34, -66), (2, -78), (38, -62)]):
            ry = ry + jg * 6 * math.sin(t * 38 + i_r * 2); rx = rx + jg * 3 * math.cos(t * 31 + i_r)
            rrect(c, rx - 19, hy + ry - 13, 38, 26, 12); fs(c, hx('#FF7FB5'), 5)
            c.move_to(rx - 6, hy + ry - 12); c.line_to(rx - 6, hy + ry + 12); c.set_source_rgba(1, 1, 1, .6); c.set_line_width(3); c.stroke()
    elif hair == 'spiky':
        pts = [(-64, hy - 5)]
        for i in range(7):
            x = -64 + i * 21
            pts += [(x + 10, hy - 88 + (i % 2) * 8), (x + 21, hy - 52)]
        pts += [(66, hy - 8), (40, hy - 40), (-40, hy - 40)]
        poly(c, pts); fs(c, hx('#1E1A1A'), 5)
    elif hair == 'slick':
        c.move_to(-68, hy + 4); c.curve_to(-78, hy - 70, -30, hy - 98, 30, hy - 88); c.curve_to(70, hy - 80, 74, hy - 40, 68, hy - 10)
        c.curve_to(50, hy - 50, 0, hy - 58, -20, hy - 44); c.curve_to(-40, hy - 30, -58, hy - 20, -68, hy + 4); c.close_path(); fs(c, hx('#121214'), 6)
        c.move_to(-30, hy - 80); c.curve_to(0, hy - 92, 30, hy - 86, 50, hy - 70); c.set_source_rgba(1, 1, 1, .5); c.set_line_width(5); c.stroke()
        if P.get('peci'):
            poly(c, [(-62, hy - 34), (62, hy - 34), (56, hy - 92), (-56, hy - 92)]); fs(c, hx('#1B1B1F'), 6)
    elif hair == 'caping':
        c.move_to(-66, hy); c.curve_to(-72, hy - 85, 66, hy - 92, 66, hy - 15); c.curve_to(30, hy - 45, -30, hy - 50, -66, hy)
        c.close_path(); fs(c, hx('#22191A'), 6)
        poly(c, [(-125, hy - 28), (125, hy - 28), (0, hy - 120)]); fs(c, hx('#E2C27A'), 6)
        for k in range(1, 4):
            c.move_to(-125 + k * 22, hy - 28 - k * 18); c.line_to(125 - k * 22, hy - 28 - k * 18)
            c.set_source_rgba(*OUT, .35); c.set_line_width(3); c.stroke()
    elif hair == 'dio':
        hc = hx('#141012')
        # base cap of hair, short at the sides
        c.move_to(-66, hy + 10); c.curve_to(-74, hy - 40, -60, hy - 82, -20, hy - 92)
        c.curve_to(20, hy - 100, 60, hy - 86, 68, hy - 36); c.curve_to(66, hy - 26, 64, hy - 20, 62, hy - 16)
        c.curve_to(56, hy - 40, 40, hy - 52, 14, hy - 54); c.curve_to(-14, hy - 50, -38, hy - 44, -52, hy - 28)
        c.curve_to(-58, hy - 12, -60, hy, -66, hy + 10); c.close_path(); fs(c, hc, 6)
        # swept quiff toward the front
        c.move_to(-30, hy - 84); c.curve_to(-10, hy - 118, 40, hy - 122, 74, hy - 92); c.curve_to(84, hy - 82, 80, hy - 66, 66, hy - 60)
        c.curve_to(50, hy - 76, 20, hy - 82, -8, hy - 74); c.close_path(); fs(c, hc, 6)
        for k in range(4):
            c.move_to(-14 + k * 18, hy - 100 + k * 2); c.curve_to(6 + k * 18, hy - 108, 30 + k * 16, hy - 100, 50 + k * 8, hy - 84 + k * 3)
            c.set_source_rgba(1, 1, 1, .28); c.set_line_width(3); c.stroke()
        # side part line + fade at temple
        c.move_to(-40, hy - 80); c.curve_to(-36, hy - 66, -28, hy - 58, -16, hy - 52); c.set_source_rgba(1, 1, 1, .25); c.set_line_width(3); c.stroke()
        c.move_to(-60, hy - 6); c.curve_to(-64, hy + 8, -62, hy + 18, -58, hy + 24); c.set_source_rgb(*hc); c.set_line_width(8); c.stroke()
    elif hair == 'dio2':
        hc = hx('#17110E')
        c.move_to(-67, hy + 12); c.curve_to(-76, hy - 46, -56, hy - 88, -6, hy - 90)
        c.curve_to(44, hy - 92, 70, hy - 64, 68, hy - 22); c.line_to(64, hy - 18)
        c.curve_to(52, hy - 30, 36, hy - 40, 20, hy - 44)                 # fringe edge swept to the side
        c.curve_to(0, hy - 46, -24, hy - 54, -40, hy - 50)
        c.curve_to(-52, hy - 40, -58, hy - 18, -60, hy + 2); c.curve_to(-62, hy + 8, -64, hy + 10, -67, hy + 12); c.close_path(); fs(c, hc, 6)
        # fringe tips falling down-front
        poly(c, [(28, hy - 46), (58, hy - 30), (40, hy - 26)]); fs(c, hc, 3)
        poly(c, [(6, hy - 48), (30, hy - 38), (14, hy - 32)]); fs(c, hc, 3)
        # part line + strands
        c.move_to(-34, hy - 84); c.curve_to(-30, hy - 72, -28, hy - 62, -30, hy - 52); c.set_source_rgba(1, 1, 1, .3); c.set_line_width(3); c.stroke()
        for k in range(5):
            c.move_to(-22 + k * 16, hy - 82 + k * 2); c.curve_to(-4 + k * 16, hy - 80, 18 + k * 12, hy - 66, 34 + k * 7, hy - 44 + k * 3)
            c.set_source_rgba(1, 1, 1, .2); c.set_line_width(2.5); c.stroke()
        c.move_to(-62, hy - 6); c.curve_to(-65, hy + 8, -63, hy + 18, -59, hy + 26); c.set_source_rgb(*hc); c.set_line_width(7); c.stroke()
        if P.get('hd'):
            for k in range(7):
                c.move_to(-50 + k * 14, hy - 76 + abs(k - 3) * 3); c.curve_to(-36 + k * 14, hy - 84, -16 + k * 12, hy - 70, 0 + k * 9, hy - 50 + k * 2)
                c.set_source_rgba(.45, .35, .3, .35); c.set_line_width(1.5); c.stroke()
            g = cairo.LinearGradient(-70, 0, -50, 0)
            g.add_color_stop_rgba(0, .3, .25, .22, .5); g.add_color_stop_rgba(1, .3, .25, .22, 0)
            c.set_source(g); c.rectangle(-70, hy - 30, 22, 50); c.fill()
            ell(c, 20, hy - 78, 26, 7); fill(c, (1, 1, 1), .18)
    elif hair == 'dio_slick':
        hc = hx('#17110E')
        c.move_to(-67, hy + 10); c.curve_to(-76, hy - 50, -50, hy - 92, 0, hy - 92)
        c.curve_to(48, hy - 92, 70, hy - 64, 68, hy - 24); c.curve_to(56, hy - 40, 34, hy - 50, 6, hy - 50)
        c.curve_to(-22, hy - 50, -42, hy - 44, -52, hy - 30); c.curve_to(-58, hy - 14, -62, hy, -67, hy + 10); c.close_path(); fs(c, hc, 6)
        c.move_to(30, hy - 88); c.curve_to(10, hy - 80, -10, hy - 78, -30, hy - 84); c.set_source_rgba(1, 1, 1, .3); c.set_line_width(3); c.stroke()
        for k in range(5):
            c.move_to(46 - k * 4, hy - 70 - k * 4); c.curve_to(20 - k * 4, hy - 84 - k * 2, -20, hy - 84 + k, -50 + k * 2, hy - 56 + k * 4)
            c.set_source_rgba(1, 1, 1, .18); c.set_line_width(2.5); c.stroke()
        c.move_to(-62, hy - 6); c.curve_to(-65, hy + 8, -63, hy + 18, -59, hy + 26); c.set_source_rgb(*hc); c.set_line_width(7); c.stroke()
    elif hair == 'dio_fringe':
        hc = hx('#1A1310')
        c.move_to(-68, hy + 14); c.curve_to(-78, hy - 50, -50, hy - 96, 0, hy - 94)
        c.curve_to(50, hy - 94, 76, hy - 60, 70, hy - 10)
        # straight fringe edge across forehead with small points
        pts = [(70, hy - 10)]
        for k in range(9):
            x = 64 - k * 15
            pts += [(x - 7, hy - 22 + (k % 2) * 6), (x - 15, hy - 30)]
        c.line_to(*pts[0])
        for pp in pts[1:]: c.line_to(*pp)
        c.line_to(-60, hy - 10); c.curve_to(-62, hy + 4, -64, hy + 10, -68, hy + 14); c.close_path(); fs(c, hc, 6)
        for k in range(6):
            c.move_to(-40 + k * 18, hy - 86); c.curve_to(-38 + k * 18, hy - 60, -36 + k * 17, hy - 44, -34 + k * 17, hy - 32)
            c.set_source_rgba(1, 1, 1, .2); c.set_line_width(2.5); c.stroke()
        c.move_to(-64, hy - 4); c.curve_to(-66, hy + 10, -64, hy + 20, -60, hy + 28); c.set_source_rgb(*hc); c.set_line_width(7); c.stroke()
    elif hair == 'short':
        c.move_to(-66, hy); c.curve_to(-72, hy - 85, 66, hy - 92, 66, hy - 15); c.curve_to(30, hy - 45, -30, hy - 50, -66, hy)
        c.close_path(); fs(c, hx('#22191A'), 6)
    elif hair == 'cap':
        c.move_to(-64, hy - 18); c.curve_to(-64, hy - 95, 64, hy - 95, 64, hy - 18); c.close_path(); fs(c, hx('#2E6BD6'), 6)
        rrect(c, 30, hy - 30, 70, 16, 8); fs(c, hx('#2E6BD6'), 5)
    # eyes
    for i, ex in enumerate((fx - 22, fx + 24)):
        ey = hy - 4
        if eyes == 'closed':
            c.move_to(ex - 12, ey + 2); c.curve_to(ex - 5, ey + 9, ex + 5, ey + 9, ex + 12, ey + 2)
            c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
        elif eyes == 'happy':
            c.move_to(ex - 12, ey + 4); c.curve_to(ex - 5, ey - 9, ex + 5, ey - 9, ex + 12, ey + 4)
            c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
        elif P.get('eye_style') == 'almond' and eyes in ('open', 'wide', 'squint'):
            ry = 13 if eyes == 'wide' else 9
            rx = 15
            c.move_to(ex - rx, ey + 1); c.curve_to(ex - rx * .5, ey - ry * 1.5, ex + rx * .6, ey - ry * 1.5, ex + rx, ey - 2)
            c.curve_to(ex + rx * .5, ey + ry * 1.2, ex - rx * .5, ey + ry * 1.2, ex - rx, ey + 1); c.close_path(); fs(c, (1, 1, 1), 3)
            c.save(); c.move_to(ex - rx, ey + 1); c.curve_to(ex - rx * .5, ey - ry * 1.5, ex + rx * .6, ey - ry * 1.5, ex + rx, ey - 2)
            c.curve_to(ex + rx * .5, ey + ry * 1.2, ex - rx * .5, ey + ry * 1.2, ex - rx, ey + 1); c.close_path(); c.clip()
            ell(c, ex + lx * .8, ey + ly * .6, 7.5, 7.5); fill(c, hx('#2A1A12'))
            ell(c, ex + lx * .8, ey + ly * .6, 3.5, 3.5); fill(c, OUT)
            ell(c, ex + lx * .8 + 2.5, ey + ly * .6 - 2.5, 2, 2); fill(c, (1, 1, 1))
            c.restore()
            c.move_to(ex - rx - 2, ey + 1); c.curve_to(ex - rx * .5, ey - ry * 1.55, ex + rx * .6, ey - ry * 1.55, ex + rx + 2, ey - 3)
            c.set_source_rgb(*OUT); c.set_line_width(4.5); c.stroke()
            c.move_to(ex - rx * .6, ey - ry * 1.55 - 4); c.curve_to(ex - rx * .1, ey - ry * 1.9 - 4, ex + rx * .5, ey - ry * 1.85 - 4, ex + rx * .9, ey - ry * 1.2 - 4)
            c.set_source_rgba(*OUT, .35); c.set_line_width(2); c.stroke()
        else:
            ry = 21 if eyes == 'wide' else 16
            rx = 16 if eyes == 'wide' else 13
            ell(c, ex, ey, rx, ry); fs(c, (1, 1, 1), 4)
            pr = 5 if eyes == 'wide' else 7
            ell(c, ex + lx, ey + ly + 2, pr, pr); fill(c, OUT)
            ell(c, ex + lx + 2, ey + ly - 1, 2, 2); fill(c, (1, 1, 1))
            if eyes == 'half':
                c.rectangle(ex - rx - 2, ey - ry - 2, 2 * rx + 4, ry + 2); fill(c, skin)
                c.move_to(ex - rx, ey); c.line_to(ex + rx, ey); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
            if eyes == 'squint':
                c.rectangle(ex - rx - 2, ey - ry - 2, 2 * rx + 4, ry * 0.8); fill(c, skin)
                c.move_to(ex - rx, ey - ry * 0.2); c.line_to(ex + rx, ey - ry * 0.35 * (1 if i else -1) - ry * 0.2)
                c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
        # brows
        by = hy - 30 - (8 if brows == 'up' or eyes == 'wide' else 0)
        c.set_source_rgb(*OUT); c.set_line_width(13 if P.get('thick') else 6); c.set_line_cap(cairo.LINE_CAP_ROUND)
        if P.get('eye_style') == 'almond' and brows == 'normal':
            c.set_line_width(6)
            c.move_to(ex - 15, by + 4); c.curve_to(ex - 5, by - 2, ex + 6, by - 2, ex + 15, by + 1)
        elif brows == 'angry':
            d = 8 if i == 0 else -8
            c.move_to(ex - 12, by - d); c.line_to(ex + 12, by + d)
        elif brows == 'smug':
            d = -6 if i == 0 else 4
            c.move_to(ex - 12, by + d); c.line_to(ex + 12, by + d - 4)
        else:
            c.move_to(ex - 12, by + 3); c.curve_to(ex - 4, by - 4, ex + 4, by - 4, ex + 12, by + 3)
        c.stroke()
    if P.get('kacamata') == 'tipis':
        for ex2 in (fx - 22, fx + 24):
            rrect(c, ex2 - 20, hy - 18, 40, 28, 9); c.set_source_rgba(.85, .92, 1, .18); c.fill_preserve()
            c.set_source_rgb(*hx('#3A3A44')); c.set_line_width(2.5); c.stroke()
            c.move_to(ex2 - 12, hy - 12); c.line_to(ex2 - 4, hy - 4); c.set_source_rgba(1, 1, 1, .7); c.set_line_width(2); c.stroke()
        c.move_to(fx - 2, hy - 8); c.curve_to(fx, hy - 11, fx + 2, hy - 11, fx + 4, hy - 8); c.set_source_rgb(*hx('#3A3A44')); c.set_line_width(2.5); c.stroke()
        c.move_to(fx - 42, hy - 6); c.line_to(fx - 58, hy - 2); c.stroke()
    elif P.get('kacamata'):
        for ex2 in (fx - 22, fx + 24):
            rrect(c, ex2 - 19, hy - 22, 38, 34, 10); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
        c.move_to(fx - 3, hy - 8); c.line_to(fx + 5, hy - 8); c.stroke()
    if P.get('hd'):
        c.move_to(-58, hy - 2); c.curve_to(-50, hy + 2, -50, hy + 12, -56, hy + 16); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(2.5); c.stroke()
        ell(c, fx + 10, hy + 18, 2.2, 1.6); fill(c, (0, 0, 0), .35)
        c.save(); ell(c, 0, hy, 66, 66); c.clip()
        g = cairo.LinearGradient(0, hy + 30, 0, hy + 66)
        g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, .3, .1, .05, .16)
        c.set_source(g); c.rectangle(-70, hy + 30, 140, 40); c.fill()
        c.restore()
        if mouth <= .06 and expr in ('smile', 'grin'):
            c.move_to(fx - 4, hy + 50); c.curve_to(fx, hy + 52, fx + 6, hy + 52, fx + 10, hy + 50); c.set_source_rgba(.5, .2, .2, .35); c.set_line_width(2); c.stroke()
        if eyes in ('open', 'wide') and P.get('eye_style') == 'almond':
            for ex3 in (fx - 22, fx + 24):
                c.move_to(ex3 + 15, hy - 7); c.line_to(ex3 + 20, hy - 11); c.set_source_rgb(*OUT); c.set_line_width(2.5); c.stroke()
        if brows == 'normal':
            for ex3 in (fx - 22, fx + 24):
                by3 = hy - 30
                for k in range(4):
                    c.move_to(ex3 - 12 + k * 7, by3 + 3 - k * .5); c.line_to(ex3 - 8 + k * 7, by3 - 2 - k * .5)
                    c.set_source_rgba(.3, .2, .15, .6); c.set_line_width(1.5); c.stroke()
    # blush
    ell(c, fx - 40, hy + 20, 12, 7); fill(c, hx('#FF8A8A'), .45)
    ell(c, fx + 46, hy + 20, 12, 7); fill(c, hx('#FF8A8A'), .45)
    # nose
    c.move_to(fx + 4, hy + 6); c.curve_to(fx + 14, hy + 12, fx + 12, hy + 20, fx + 2, hy + 20)
    c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
    # mouth
    mx, my = fx + 2, hy + 36
    if mouth > 0.06:
        hgt = 6 + mouth * 26
        vw = (0.72 + 0.4 * abs(math.sin(t * 6.3 + 1.3 * math.sin(t * 2.1)))) if SHADE else 1.0
        ell(c, mx, my + hgt / 3, (15 + mouth * 4) * vw, hgt / 1.6 * (1.15 - .3 * (vw - .72))); fs(c, hx('#7A1F2B'), 4)
        if mouth > .35:
            c.rectangle(mx - 10 * vw, my + hgt / 3 - hgt / 1.6 + 2, 20 * vw, 5); fill(c, (1, 1, 1), .9)
        ell(c, mx, my + hgt * 0.65, 9, 5); fill(c, hx('#E86A7A'))
        if P.get('lips'):
            ell(c, mx, my + hgt / 3, 16 + mouth * 4, hgt / 1.6 + 1); c.set_source_rgb(*hx('#D81E3A')); c.set_line_width(4); c.stroke()
    else:
        c.set_line_width(5); c.set_source_rgb(*(hx('#C8102E') if P.get('lips') else OUT))
        if expr == 'smile':
            c.move_to(mx - 16, my - 2); c.curve_to(mx - 6, my + 10, mx + 6, my + 10, mx + 16, my - 2); c.stroke()
        elif expr == 'grin':
            c.move_to(mx - 20, my - 4); c.curve_to(mx - 8, my + 16, mx + 8, my + 16, mx + 20, my - 4); c.close_path()
            fs(c, (1, 1, 1), 4)
        elif expr == 'frown':
            c.move_to(mx - 14, my + 6); c.curve_to(mx - 4, my - 4, mx + 4, my - 4, mx + 14, my + 6); c.stroke()
        elif expr == 'pout':
            ell(c, mx + 4, my + 2, 9, 7); fs(c, hx('#D81E3A'), 4)
        elif expr == 'o':
            ell(c, mx, my + 6, 10, 14); fs(c, hx('#7A1F2B'), 4)
        else:
            c.move_to(mx - 12, my + 2); c.line_to(mx + 12, my + 2); c.stroke()
    if P.get('mus'):
        for sgn in (-1, 1):
            c.move_to(mx, my - 8); c.curve_to(mx + sgn * 10, my - 14, mx + sgn * 22, my - 10, mx + sgn * 26, my - 2)
            c.curve_to(mx + sgn * 16, my - 4, mx + sgn * 8, my - 2, mx, my - 2); c.close_path(); fill(c, hx('#1B1414'))

def safari_badan(c, P, sh, hip, sit):
    """baju safari badan gendut (Pak Bos): perut membulat, 4 saku bertutup, epolet, kancing, pin emas."""
    col = P['shirt']; dk = tuple(v * .82 for v in col)
    bot = hip + (4 if sit else 22)
    c.new_path(); c.move_to(-60, sh + 14); c.curve_to(-60, sh - 10, -40, sh - 10, -24, sh - 10); c.line_to(24, sh - 10)
    c.curve_to(40, sh - 10, 60, sh - 10, 60, sh + 14)
    c.curve_to(64, sh + 60, 92, hip - 70, 86, hip - 20); c.curve_to(84, bot - 6, 74, bot, 62, bot)
    c.curve_to(20, bot + 6, -20, bot + 6, -62, bot); c.curve_to(-74, bot, -84, bot - 6, -86, hip - 20)
    c.curve_to(-92, hip - 70, -64, sh + 60, -60, sh + 14); c.close_path(); fs(c, col, 6)
    c.move_to(-76, hip - 60); c.curve_to(-70, hip - 20, -60, bot - 6, -40, bot - 2); c.set_source_rgba(0, 0, 0, .12); c.set_line_width(8); c.stroke()
    c.move_to(60, sh + 30); c.curve_to(78, hip - 80, 80, hip - 40, 70, hip - 10); c.set_source_rgba(1, 1, 1, .18); c.set_line_width(6); c.stroke()
    c.move_to(0, sh - 6); c.line_to(0, bot + 2); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(3); c.stroke()      # belahan kancing
    for k in range(5):
        yy = sh + 22 + k * ((bot - sh - 40) / 4)
        ell(c, 6, yy, 4.5, 4.5); fs(c, hx('#8A7A55'), 2)
    for sgn in (-1, 1):                                                         # saku dada bertutup
        x0 = sgn * 32 - 19
        rrect(c, x0, sh + 34, 38, 40, 4); fs(c, col, 3)
        c.move_to(sgn * 32, sh + 38); c.line_to(sgn * 32, sh + 72); c.set_source_rgba(0, 0, 0, .2); c.set_line_width(2); c.stroke()
        poly(c, [(x0 - 1, sh + 30), (x0 + 39, sh + 30), (x0 + 39, sh + 42), (sgn * 32, sh + 48), (x0 - 1, sh + 42)]); fs(c, dk, 3)
        ell(c, sgn * 32, sh + 42, 3.5, 3.5); fs(c, hx('#8A7A55'), 1.5)
        x1 = sgn * 44 - 24                                                       # saku bawah besar
        rrect(c, x1, hip - 52, 48, 50, 5); fs(c, col, 3)
        poly(c, [(x1 - 1, hip - 58), (x1 + 49, hip - 58), (x1 + 49, hip - 44), (sgn * 44, hip - 38), (x1 - 1, hip - 44)]); fs(c, dk, 3)
        ell(c, sgn * 44, hip - 44, 3.5, 3.5); fs(c, hx('#8A7A55'), 1.5)
        c.save(); c.translate(sgn * 44, sh - 4); c.rotate(sgn * .18)                # epolet
        rrect(c, -20, -7, 40, 14, 5); fs(c, dk, 3); ell(c, -sgn * 12, 0, 3.5, 3.5); fs(c, hx('#8A7A55'), 1.5)
        c.restore()
    ell(c, 34, sh + 20, 7, 7); fs(c, hx('#E8B53A'), 2.5); ell(c, 34, sh + 20, 3, 3); fill(c, hx('#9C6B12'))   # pin emas

def person(c, x, y, who, po=None, s=1.0, t=0.0, flip=False):
    P = CH[who]; po = dict(po or {})
    seed = (sum(map(ord, who)) * 0.137) % 1
    if SHADE:
        if ((t * 0.42 + seed) % 1) < 0.04 and po.get('eyes', 'open') in ('open', 'wide', 'squint', 'half'):
            po['eyes'] = 'closed'
        po['tilt'] = po.get('tilt', 0) + 1.8 * math.sin(t * 1.7 + seed * 6)
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    if SHADE and not po.get('sit') and not po.get('noshadow'):
        g = cairo.RadialGradient(0, 0, 5, 0, 0, 95)
        g.add_color_stop_rgba(0, 0, 0, .05, .35); g.add_color_stop_rgba(1, 0, 0, .05, 0)
        c.save(); c.scale(1, .18); c.set_source(g); c.arc(0, 0, 95, 0, 2 * math.pi); c.fill(); c.restore()
    bob = po.get('bob', 1.0) * 3 * math.sin(t * 5 + x)
    sit = po.get('sit', False)
    hip = -150 if sit else -120
    hip += bob * 0.3
    sh = hip - 148
    hy = hip - 230 + bob
    skin = P['skin']
    aF = po.get('aF', (12, 18)); aB = po.get('aB', (-10, -14))
    ex = P['kind'] == 'daster'
    sleeve = P.get('shirt', P.get('dress'))
    # back arm
    sleeve = P.get('jacket', sleeve)
    arm(c, -40, sh + 12, aB[0], aB[1], sleeve, skin, long=P.get('long', False), gelang=P.get('gelang', False), cuff=P.get('cuff'), hd=P.get('hd', False))
    # legs
    if sit:
        legc = P.get('pants', skin)
        for dx in (-14, 14):
            line(c, [(dx, hip), (dx + 80, hip + 6), (dx + 82, -14)], 30, legc)
            foot(c, dx + 96, -8, P, False)
    else:
        legc = skin if ex else P['pants']
        top = -48 if ex else hip
        st = po.get('step', 0)
        for dx, ph in ((-22, 0), (22, math.pi)):
            fxo = st * 18 * math.sin(t * 9 + ph)
            line(c, [(dx, top), (dx + fxo, -12)], 26 if ex else 32, legc)
            if P.get('chino') and not ex:
                c.move_to(dx + 4, top + 8); c.line_to(dx + fxo + 4, -26); c.set_source_rgba(1, 1, 1, .35); c.set_line_width(2); c.stroke()
                if P.get('hd'):
                    ky = (top - 12) / 2
                    for k in range(2):
                        c.move_to(dx - 12 + fxo * .5, ky - 4 + k * 8); c.curve_to(dx - 4, ky - 8 + k * 8, dx + 4, ky + k * 8, dx + 12 + fxo * .5, ky - 2 + k * 8)
                        c.set_source_rgba(0, 0, 0, .18); c.set_line_width(2); c.stroke()
                    for k in range(2):
                        c.move_to(dx - 14 + fxo, -40 + k * 6); c.curve_to(dx - 4 + fxo, -44 + k * 6, dx + 4 + fxo, -36 + k * 6, dx + 14 + fxo, -40 + k * 6)
                        c.set_source_rgba(0, 0, 0, .2); c.set_line_width(2); c.stroke()
                c.move_to(dx - 15 + fxo, -30); c.line_to(dx + 15 + fxo, -30); c.set_source_rgba(0, 0, 0, .28); c.set_line_width(3); c.stroke()
                if dx > 0:
                    c.move_to(dx + 4, top + 4); c.line_to(dx + 14, top + 28); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(2.5); c.stroke()
            foot(c, dx + fxo + 9, -8, P, ex)
    if SHADE:
        br = 1 + 0.014 * math.sin(t * 2.6 + seed * 9)
        c.translate(0, hip); c.scale(1, br); c.translate(0, -hip)
    # torso
    hs = 6 * math.sin(t * 2.4 + x * .01) if SHADE else 0
    if ex and not sit:
        c.move_to(-50, sh - 4); c.curve_to(-62, sh + 80, -84 + hs, -90, -88 + hs, -46); c.curve_to(-30 + hs, -36, 30 + hs, -36, 88 + hs, -46)
        c.curve_to(84 + hs, -90, 62, sh + 80, 50, sh - 4); c.curve_to(20, sh - 14, -20, sh - 14, -50, sh - 4); c.close_path()
        fs(c, P['dress'], 6)
        c.save(); c.move_to(-50, sh - 4); c.curve_to(-62, sh + 80, -84 + hs, -90, -88 + hs, -46); c.curve_to(-30 + hs, -36, 30 + hs, -36, 88 + hs, -46)
        c.curve_to(84 + hs, -90, 62, sh + 80, 50, sh - 4); c.close_path(); c.clip()
        rnd = random.Random(who)
        for _ in range(16):
            px_, py_ = rnd.uniform(-85, 85), rnd.uniform(sh, -40)
            for k in range(5):
                a = k * 2 * math.pi / 5
                ell(c, px_ + 7 * math.cos(a), py_ + 7 * math.sin(a), 5, 5); fill(c, P['dots'], .9)
            ell(c, px_, py_, 3.5, 3.5); fill(c, (1, 1, 1))
        if P.get('celemek'):
            rrect(c, -46, sh + 60, 92, -40 - sh - 60, 14); fs(c, P['celemek'], 4)
            rrect(c, -26, sh + 120, 52, 40, 6); fs(c, P['celemek'], 3)
            c.move_to(-40, sh + 60); c.line_to(-30, sh); c.move_to(40, sh + 60); c.line_to(30, sh)
            c.set_source_rgb(*P['celemek']); c.set_line_width(6); c.stroke()
        c.restore()
        c.move_to(-50, sh - 4); c.curve_to(-20, sh + 22, 20, sh + 22, 50, sh - 4)
        c.set_source_rgb(*P.get('trim', hx('#FFFFFF'))); c.set_line_width(5); c.stroke()
        c.move_to(-88, -50); c.curve_to(-30, -40, 30, -40, 88, -50); c.set_source_rgb(*P.get('trim', hx('#FFFFFF'))); c.set_line_width(5); c.stroke()
        if P.get('kalung') and P.get('hair') != 'hijab':
            c.move_to(-34, sh - 2); c.curve_to(-20, sh + 38, 20, sh + 38, 34, sh - 2)
            c.set_source_rgb(*hx('#F2C230')); c.set_line_width(3); c.stroke()
            ell(c, 0, sh + 30, 6, 8); fs(c, hx('#F2C230'), 2)
    else:
        col = P.get('shirt', P.get('dress'))
        tl = hip - sh + 26
        if P.get('short_shirt') and not sit:
            rrect(c, -44, hip - 20, 88, 30, 6); fs(c, P.get('pants', col), 4)          # chino waist
            for sgn in (-1, 1):
                c.rectangle(sgn * 26 - 3, hip - 18, 6, 12); fill(c, (0, 0, 0), .18)      # belt loops
            tl = hip - sh - 10
        if P.get('safari'):
            safari_badan(c, P, sh, hip, sit)
        elif P.get('hd') and not P.get('short_shirt') and not sit:
            bt = sh - 8 + tl
            c.new_path(); c.move_to(-56, sh + 22); c.curve_to(-56, sh - 8, -40, sh - 8, -26, sh - 8); c.line_to(26, sh - 8)
            c.curve_to(40, sh - 8, 56, sh - 8, 56, sh + 22); c.line_to(56, bt - 22)
            c.curve_to(52, bt - 30, 46, bt - 26, 42, bt - 18); c.curve_to(30, bt + 2, -30, bt + 2, -42, bt - 18)
            c.curve_to(-46, bt - 26, -52, bt - 30, -56, bt - 22); c.close_path(); fs(c, P.get('jacket', col), 6)
            for sgn in (-1, 1):
                c.move_to(sgn * 56, bt - 22); c.line_to(sgn * 50, bt - 36); c.set_source_rgba(0, 0, 0, .35); c.set_line_width(2.5); c.stroke()
            for k, (x0, y0) in enumerate(((-40, hip - 30), (-34, hip - 14), (30, hip - 24))):
                c.move_to(x0, y0); c.curve_to(x0 + 8, y0 - 6, x0 + 16, y0 + 2, x0 + 22, y0 - 4); c.set_source_rgba(0, 0, 0, .2); c.set_line_width(2.5); c.stroke()
            c.move_to(-50, sh + 4); c.curve_to(-46, sh + 30, -48, sh + 60, -44, sh + 80); c.set_source_rgba(1, 1, 1, .12); c.set_line_width(5); c.stroke()
        else:
            rrect(c, -56, sh - 8, 112, tl, 30); fs(c, P.get('jacket', col), 6)
        if P.get('jacket'):
            poly(c, [(-26, sh - 6), (26, sh - 6), (0, sh + 70)]); fs(c, col, 4)
        if P.get('tie'):
            poly(c, [(-9, sh - 4), (9, sh - 4), (6, sh + 10), (-6, sh + 10)]); fs(c, P['tie'], 3)
            poly(c, [(-6, sh + 10), (6, sh + 10), (12, sh + 78), (0, sh + 92), (-12, sh + 78)]); fs(c, P['tie'], 3)
        if P.get('badge'):
            rrect(c, 14, sh + 26, 34, 18, 4); fs(c, P['badge'], 3)
        pat = P.get('pattern')
        if pat:
            c.save(); rrect(c, -56, sh - 8, 112, tl, 30); c.clip()
            pc = P.get('pat_col', (0, 0, 0))
            if pat == 'kotak':
                for k in range(-6, 7):
                    c.rectangle(k * 18 - 3, sh - 10, 6, 200); fill(c, pc, .35)
                    c.rectangle(-60, sh + k * 18 + 60, 120, 6); fill(c, pc, .35)
            elif pat == 'batik':
                for i in range(-4, 5):
                    for j in range(0, 9):
                        bx, by = i * 26 + (j % 2) * 13, sh + j * 24
                        poly(c, [(bx, by - 9), (bx + 9, by), (bx, by + 9), (bx - 9, by)]); fill(c, pc, .55)
                        ell(c, bx, by, 3, 3); fill(c, (1, .95, .8), .8)
            elif pat == 'garis':
                for k in range(-6, 7):
                    c.rectangle(k * 16, sh - 10, 5, 200); fill(c, pc, .3)
            c.restore()
        if P.get('collar'):
            cc = P.get('collar_col', col)
            poly(c, [(-34, sh - 10), (-4, sh - 8), (-14, sh + 22)]); fs(c, cc, 4)
            poly(c, [(34, sh - 10), (4, sh - 8), (14, sh + 22)]); fs(c, cc, 4)
            if P.get('collar_pipe'):
                c.move_to(-30, sh - 7); c.line_to(-14, sh + 17); c.move_to(30, sh - 7); c.line_to(14, sh + 17)
                c.set_source_rgb(*P['collar_pipe']); c.set_line_width(2.5); c.stroke()
                c.move_to(-20, sh - 9); c.curve_to(-8, sh - 4, 8, sh - 4, 20, sh - 9); c.stroke()
        if P.get('placket'):
            c.rectangle(-7, sh + 4, 14, tl - 18); fill(c, (0, 0, 0), .12)
            c.move_to(-7, sh + 4); c.line_to(-7, sh - 8 + tl - 4); c.move_to(7, sh + 4); c.line_to(7, sh - 8 + tl - 4)
            c.set_source_rgba(1, 1, 1, .18); c.set_line_width(1.5); c.stroke()
        if P.get('seams'):
            for sgn in (-1, 1):
                c.move_to(sgn * 34, sh - 6); c.curve_to(sgn * 44, sh + 10, sgn * 50, sh + 24, sgn * 56, sh + 30)
                c.set_source_rgba(1, 1, 1, .2); c.set_line_width(2); c.set_dash([5, 4]); c.stroke(); c.set_dash([])
            c.move_to(-54, sh - 8 + tl - 10); c.line_to(54, sh - 8 + tl - 10); c.set_source_rgba(1, 1, 1, .15); c.set_line_width(2); c.set_dash([5, 4]); c.stroke(); c.set_dash([])
        if P.get('buttons'):
            c.move_to(0, sh + 6); c.line_to(0, sh - 8 + tl - 6); c.set_source_rgba(0, 0, 0, .3); c.set_line_width(3); c.stroke()
            for k in range(3):
                ell(c, 6, sh + 24 + k * 30, 4, 4); fs(c, (1, 1, 1), 2)
                if P.get('hd'):
                    ell(c, 5, sh + 23 + k * 30, 1, 1); fill(c, OUT); ell(c, 7, sh + 25 + k * 30, 1, 1); fill(c, OUT)
        if P.get('pocket'):
            rrect(c, 16, sh + 28, 28, 30, 4); c.set_source_rgba(0, 0, 0, .35); c.set_line_width(3); c.stroke()
            if P.get('pocket_flap'):
                poly(c, [(15, sh + 27), (45, sh + 27), (45, sh + 36), (30, sh + 40), (15, sh + 36)]); fill(c, (0, 0, 0), .18)
                ell(c, 30, sh + 35, 2.5, 2.5); fill(c, (1, 1, 1), .8)
            c.move_to(16, sh + 36); c.line_to(44, sh + 36); c.stroke()
            rrect(c, 24, sh + 18, 5, 18, 2); fs(c, hx('#2E6BD6'), 2)
        if P.get('side_panel'):
            c.save(); rrect(c, -56, sh - 8, 112, tl, 30); c.clip()
            hb = sh - 8 + tl - 18
            for sgn in (-1, 1):
                poly(c, [(sgn * 58, hip - 70), (sgn * 30, hip - 20), (sgn * 44, hip + 20), (sgn * 58, hip + 20)]); fill(c, hx('#7FB8E8'))
                poly(c, [(sgn * 58, hip - 40), (sgn * 40, hip - 6), (sgn * 50, hip + 20), (sgn * 58, hip + 20)]); fill(c, hx('#E8F0D8'))
                c.move_to(sgn * 54, hip - 60); c.line_to(sgn * 36, hip + 10); c.set_source_rgb(*hx('#2E6BD6')); c.set_line_width(3); c.stroke()
            c.restore()
        if P.get('chest_text'):
            c.save(); c.translate(-36, sh + 18)
            if c.get_matrix().xx < 0: c.scale(-1, 1)
            text(c, P['chest_text'], 0, 0, 8.5, (1, 1, 1), font="Inter Black")
            c.restore()
        if P.get('lanyard'):
            lo = -26 if P.get('short_shirt') else 0
            for sgn in (-1, 1):
                c.move_to(sgn * 12, sh - 6); c.line_to(sgn * 5, sh + 78 + lo)
                c.set_source_rgb(*hx('#8FD0F0')); c.set_line_width(7); c.stroke()
                for k in range(3 if lo else 4):
                    yy = sh + 6 + k * 18; xx = lerp(sgn * 12, sgn * 5, (yy - sh + 6) / 84)
                    ell(c, xx, yy, 3, 3); fill(c, hx('#F07AA8'))
            c.save(); c.translate(0, lo)
            rrect(c, -18, sh + 76, 36, 10, 3); fs(c, hx('#9AA1A9'), 2)
            if P.get('hd'):
                c.arc(0, sh + 72, 6, 0, 2 * math.pi); c.set_source_rgb(*hx('#C9CED4')); c.set_line_width(3); c.stroke()
                rrect(c, -4, sh + 62, 8, 10, 2); fs(c, hx('#9AA1A9'), 1.5)
            rrect(c, -24, sh + 84, 48, 60, 5); fs(c, (1, 1, 1), 3)
            c.rectangle(-18, sh + 92, 36, 6); fill(c, hx('#1F2F6B'))
            rrect(c, -10, sh + 102, 20, 22, 3); fill(c, hx('#C9D6E6'))
            ell(c, 0, sh + 108, 5, 5); fill(c, hx('#5A6375')); ell(c, 0, sh + 121, 8, 5); fill(c, hx('#5A6375'))
            c.save(); c.translate(0, sh + 133)
            if c.get_matrix().xx < 0: c.scale(-1, 1)
            text(c, P.get('id_name', ''), 0, 0, 8, hx('#1F2F6B'), font="Inter Black")
            c.restore()
            c.restore()
        if P.get('belt'):
            c.rectangle(-56, hip - 6, 112, 14); fs(c, P['belt'], 3)
            rrect(c, -8, hip - 8, 16, 18, 3); fs(c, hx('#C9CED4'), 3)
    if P.get('hd'):
        rrect(c, -20, hy + 40, 40, 40, 10); fs(c, skin, 4)
        c.rectangle(-18, hy + 58, 36, 12); fill(c, (0, 0, 0), .12)
    # head (with tilt)
    c.save(); c.translate(0, hy + 60); c.rotate(math.radians(po.get('tilt', 0))); c.translate(0, -(hy + 60))
    face(c, P, hy, po, t)
    c.restore()
    hand = arm(c, 40, sh + 12, aF[0], aF[1], sleeve, skin, long=P.get('long', False), watch=P.get('watch'), cuff=P.get('cuff'), hd=P.get('hd', False))
    if po.get('thumb'):
        ell(c, hand[0] + 2, hand[1] - 20, 7, 13); fs(c, skin, 3)
    if po.get('hold'):
        po['hold'](c, hand)
    c.restore()

# ---------------------------------------------------------------- props
def sack(c, x, y, w=120, h=78, label=True, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.move_to(-w / 2, -h / 2 + 8); c.curve_to(-w / 2 - 6, h / 4, -w / 2, h / 2, -w / 2 + 10, h / 2)
    c.line_to(w / 2 - 10, h / 2); c.curve_to(w / 2, h / 2, w / 2 + 6, h / 4, w / 2, -h / 2 + 8)
    c.curve_to(w / 4, -h / 2 - 4, -w / 4, -h / 2 - 4, -w / 2, -h / 2 + 8); c.close_path()
    fs(c, hx('#F6F1E4'), 5)
    c.rectangle(-w / 2 + 6, -6, w - 12, 8); fill(c, hx('#E23A3A'), .9)
    if label: text(c, "BERAS", 0, 16, 20, hx('#2050B0'))
    c.restore()

def bulb_glow(c, x, y, r, a=0.55):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, 1, .9, .55, a); g.add_color_stop_rgba(1, 1, .85, .4, 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()

RNG = random.Random(7)
SHELF = []
PAL = [hx(p) for p in ['#E5473B', '#F2C230', '#2E86DE', '#2EAD6B', '#F07D2B', '#9B4DCA', '#FFFFFF', '#F07AA8', '#7AC74F']]
for row, yb in enumerate([820, 930, 1040]):
    x = 775
    while x < 1620:
        w = RNG.choice([34, 40, 46, 30]); h = RNG.choice([44, 56, 70, 82])
        kind = RNG.random()
        SHELF.append((x, yb, w, min(h, 92), RNG.choice(PAL), 'bottle' if kind < 0.25 else 'box'))
        x += w + RNG.choice([3, 5, 8])

SACHET = [(RNG.choice(PAL)) for _ in range(30)]

def gran_max(c, x, y, t, wheel_ang=0, driver=False, door=0.0, cargo=True, s=1.0, driver_po=None):
    c.save(); c.translate(x, y); c.scale(s, s)
    WH = hx('#F7F7F4'); SH = hx('#D9DCE0')
    # shadow
    ell(c, 430, 2, 470, 22); fill(c, (0, 0, 0), .22)
    # cargo
    if cargo:
        for i, (sx, sy, r) in enumerate([(90, -275, -.05), (205, -280, .04), (320, -275, -.03), (430, -272, .05),
                                          (150, -345, .06), (270, -350, -.04), (385, -342, .03)]):
            sack(c, sx, sy, 118, 74, True, r)
        rrect(c, 60, -405, 80, 60, 6); fs(c, hx('#C98B4A'), 5)
        text(c, "MINYAK", 100, -375, 15, OUT, font="Inter Black")
    # bed
    rrect(c, 8, -255, 540, 165, 10); fs(c, WH, 6)
    c.rectangle(16, -246, 524, 10); fill(c, SH)
    for bx in (150, 290, 420):
        c.move_to(bx, -246); c.line_to(bx, -100); c.set_source_rgba(*SH, 1); c.set_line_width(4); c.stroke()
    rrect(c, 8, -228, 18, 44, 4); fs(c, hx('#E23A3A'), 4)
    # sticker stripe
    c.rectangle(30, -150, 820, 14); fill(c, hx('#F5C02E'))
    c.rectangle(30, -136, 820, 7); fill(c, hx('#E23A3A'))
    text(c, "GRAN MAX", 270, -196, 34, hx('#8C939C'), font="Inter Black")
    # cab
    c.move_to(540, -92); c.line_to(540, -405); c.curve_to(540, -418, 548, -420, 560, -420)
    c.line_to(752, -420); c.curve_to(790, -420, 800, -400, 812, -370); c.line_to(852, -250)
    c.curve_to(860, -228, 866, -200, 866, -160); c.line_to(866, -92); c.close_path(); fs(c, WH, 6)
    # window
    win = [(566, -398), (748, -398), (800, -300), (566, -300)]
    if driver:
        c.save(); poly(c, win); c.clip()
        poly(c, win); fill(c, hx('#8FC6E8'))
        person(c, 690, 40, 'rahmat', driver_po or {'aF': (110, 20)}, s=0.95, t=t)
        poly(c, win); fill(c, hx('#BFE4F7'), .25)
        c.restore(); poly(c, win); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    else:
        poly(c, win); fs(c, hx('#8FC6E8'), 5)
    c.move_to(600, -398); c.line_to(640, -300); c.line_to(670, -300); c.line_to(630, -398); c.close_path(); fill(c, (1, 1, 1), .45)
    # windshield edge
    c.move_to(760, -410); c.line_to(840, -260); c.set_source_rgb(*hx('#6FA7C9')); c.set_line_width(10); c.stroke()
    # door
    c.move_to(556, -295); c.line_to(556, -104); c.line_to(790, -104); c.line_to(806, -295)
    c.set_source_rgb(*OUT); c.set_line_width(3.5); c.stroke()
    rrect(c, 580, -268, 40, 10, 5); fs(c, SH, 3)
    # mirror
    rrect(c, 806, -330, 26, 40, 8); fs(c, hx('#2B2B2B'), 4)
    # light + bumper
    rrect(c, 836, -240, 30, 44, 8); fs(c, hx('#FFF6C9'), 4)
    rrect(c, 830, -125, 52, 40, 8); fs(c, hx('#9AA1A9'), 5)
    rrect(c, -4, -110, 40, 26, 6); fs(c, hx('#9AA1A9'), 4)
    c.rectangle(30, -96, 800, 14); fill(c, hx('#3A3D42'))
    # arches + wheels
    for wx in (150, 690):
        c.arc(wx, -60, 78, math.pi, 2 * math.pi); c.close_path(); fill(c, hx('#2A2A2E'))
        ell(c, wx, -60, 62, 62); fs(c, hx('#1C1C1F'), 5)
        ell(c, wx, -60, 38, 38); fs(c, hx('#C9CED4'), 4)
        for k in range(5):
            a = wheel_ang + k * 2 * math.pi / 5
            c.move_to(wx, -60); c.line_to(wx + 34 * math.cos(a), -60 + 34 * math.sin(a))
            c.set_source_rgb(*hx('#7D848C')); c.set_line_width(8); c.stroke()
        ell(c, wx, -60, 10, 10); fs(c, hx('#E6E9EC'), 3)
    if door > 0:
        dx = 806 + 120 * door
        poly(c, [(806, -400), (dx, -385 + 10 * door), (dx, -118), (806, -104)]); fs(c, WH, 6)
        poly(c, [(812, -385), (dx - 8, -372 + 10 * door), (dx - 8, -300), (812, -300)]); fs(c, hx('#8FC6E8'), 4)
    c.restore()

def motor(c, x, y, t, wheel_ang):
    c.save(); c.translate(x, y)
    for wx in (-150, 150):
        ell(c, wx, -55, 55, 55); fs(c, hx('#1C1C1F'), 5)
        ell(c, wx, -55, 26, 26); fs(c, hx('#C9CED4'), 4)
        for k in range(3):
            a = wheel_ang + k * 2 * math.pi / 3
            c.move_to(wx, -55); c.line_to(wx + 24 * math.cos(a), -55 + 24 * math.sin(a)); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    c.move_to(-170, -110); c.curve_to(-120, -170, 40, -170, 90, -130); c.line_to(170, -120); c.line_to(150, -60)
    c.line_to(-60, -70); c.curve_to(-120, -60, -160, -70, -170, -110); c.close_path(); fs(c, hx('#D63A2F'), 6)
    rrect(c, -150, -185, 190, 30, 14); fs(c, hx('#2B2B2B'), 5)
    line(c, [(110, -130), (140, -230)], 14, hx('#5D6166'))
    line(c, [(125, -235), (175, -235)], 12, hx('#2B2B2B'))
    rrect(c, 150, -215, 36, 30, 10); fs(c, hx('#FFF6C9'), 4)
    c.restore()

def tiang(c, x, top=280, bot=1360):
    c.rectangle(x - 12, top, 24, bot - top); fs(c, hx('#8D8F93'), 5)
    c.rectangle(x - 110, top + 40, 220, 16); fs(c, hx('#6F7276'), 4)

def wires(c, x0, x1, ys):
    for i, yy in enumerate(ys):
        c.move_to(x0, yy); c.curve_to(lerp(x0, x1, .3), yy + 70, lerp(x0, x1, .7), yy + 70, x1, yy)
        c.set_source_rgb(*hx('#2B2B30')); c.set_line_width(4); c.stroke()

def zzz(c, x, y, t, s=1.0, a=1.0):
    for k in range(3):
        ph = (t * 0.7 + k / 3) % 1
        text(c, "Z", x + ph * 60 * s + k * 10, y - ph * 140 * s, (30 + 22 * ph) * s, (1, 1, 1), OUT, 8 * s, alpha=a * (1 - ph) ** 0.5)

def sweat(c, x, y, s=1):
    c.move_to(x, y - 30 * s); c.curve_to(x + 20 * s, y, x + 18 * s, y + 22 * s, x, y + 22 * s)
    c.curve_to(x - 18 * s, y + 22 * s, x - 20 * s, y, x, y - 30 * s); fs(c, hx('#8FD3FF'), 4)

def spark(c, x, y, r, a=1):
    c.move_to(x, y - r); c.curve_to(x, y, x, y, x + r, y); c.curve_to(x, y, x, y, x, y + r)
    c.curve_to(x, y, x, y, x - r, y); c.curve_to(x, y, x, y, x, y - r); c.close_path()
    c.set_source_rgba(1, 1, .7, a); c.fill_preserve(); c.set_source_rgba(*OUT, a); c.set_line_width(3); c.stroke()

def exclaim(c, x, y, s=1, a=1):
    if s < 0.02: return
    c.save(); c.translate(x, y); c.scale(s, s)
    text(c, "!", 0, 0, 120, hx('#FF3B30'), (1, 1, 1), 14, alpha=a)
    c.restore()

# ---------------------------------------------------------------- street world
SKIES = {
 'night': (hx('#0D1640'), hx('#2B3A78')),
 'dawn': (hx('#4C6FC4'), hx('#FFB38A')),
 'day': (hx('#3FA2F0'), hx('#BFE7FF')),
 'morning': (hx('#58B2F2'), hx('#FFE3B8')),
}
STARS = [(RNG.uniform(-1500, 4500), RNG.uniform(-1200, 600), RNG.uniform(2, 5)) for _ in range(140)]
CLOUDS = [(RNG.uniform(-1500, 4500), RNG.uniform(-300, 380), RNG.uniform(.7, 1.4)) for _ in range(12)]

def cloud(c, x, y, s):
    for dx, dy, r in [(0, 0, 50), (55, -20, 60), (115, 0, 48), (60, 20, 50)]:
        ell(c, x + dx * s, y + dy * s, r * s, r * s * .85); fill(c, (1, 1, 1), .9)

def draw_street(c, t, st):
    tod = st.get('tod', 'day')
    night = tod == 'night'
    top, bot = SKIES[tod]
    g = cairo.LinearGradient(0, -1200, 0, 1340)
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
    c.set_source(g); c.rectangle(-3000, -3000, 9000, 4340); c.fill()
    if night:
        for sx, sy, r in STARS:
            tw = .6 + .4 * math.sin(t * 3 + sx)
            ell(c, sx, sy, r, r); fill(c, (1, 1, .9), tw)
        ell(c, 380, 120, 70, 70); fill(c, hx('#FFF6D8'))
        ell(c, 410, 100, 62, 62); fill(c, top)
    else:
        if tod == 'dawn':
            sy = st.get('sun_y', 560)
            bulb_glow(c, 1500, sy, 420, .6)
            ell(c, 1500, sy, 95, 95); fill(c, hx('#FFE07A'))
        else:
            ell(c, 2900, 60, 90, 90); fill(c, hx('#FFE36E'))
            bulb_glow(c, 2900, 60, 260, .4)
        for cx_, cy_, s in CLOUDS:
            cloud(c, (cx_ + t * 12) % 6000 - 1500, cy_, s)
    # far background houses / trees
    for i in range(-6, 16):
        bx = i * 300 + 40
        hh = 180 + (i * 37 % 90)
        c.rectangle(bx, 1340 - 660 - hh, 240, hh + 200); fill(c, hx('#9FB7C9') if not night else hx('#1D2550'))
        ell(c, bx + 270, 700 - (i * 53 % 80), 90, 90); fill(c, hx('#7DBF7A') if not night else hx('#1A2A44'))
    # left house
    c.rectangle(-500, 760, 1100, 600); fs(c, hx('#7EC8E3'), 6)
    poly(c, [(-560, 770), (660, 770), (380, 520), (-280, 520)]); fs(c, hx('#B5562F'), 6)
    rrect(c, 120, 880, 220, 200, 6); fs(c, hx('#FFE9A6') if (night and st.get('left_lit')) else hx('#2E4A66'), 6)
    c.move_to(230, 880); c.line_to(230, 1080); c.move_to(120, 980); c.line_to(340, 980); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    rrect(c, -200, 980, 160, 380, 6); fs(c, hx('#8A5A3B'), 6)
    # sidewalk / road
    c.rectangle(-3000, 1340, 9000, 90); fs(c, hx('#C9C3B6'), 5)
    for i in range(-30, 60):
        c.move_to(i * 110, 1340); c.line_to(i * 110 - 20, 1430); c.set_source_rgba(*OUT, .25); c.set_line_width(3); c.stroke()
    c.rectangle(-3000, 1430, 9000, 330); fill(c, hx('#55585E'))
    c.rectangle(-3000, 1430, 9000, 12); fill(c, hx('#3B3D42'))
    for i in range(-20, 40):
        c.rectangle(i * 240, 1590, 130, 14); fill(c, hx('#F2F2F2'), .85)
    c.rectangle(-3000, 1760, 9000, 3000); fill(c, hx('#6DBF5B') if not night else hx('#244A2A'))
    for i in range(-20, 60):
        ell(c, i * 140 + 40, 1800 + (i * 31 % 50), 50, 22); fill(c, hx('#4FA343') if not night else hx('#1C3A20'))
    # tiang
    tiang(c, 650); tiang(c, 2780)
    wires(c, -1500, 650, [330, 360]); wires(c, 650, 2780, [330, 360]); wires(c, 2780, 4500, [330, 360])
    # ---------------- TOKO
    c.rectangle(700, 560, 1000, 790); fs(c, hx('#F5E6C8'), 6)
    rrect(c, 715, 455, 970, 145, 14); fs(c, hx('#D8312B'), 7)
    text(c, "TOKO SEMBAKO", 1200, 507, 66, hx('#FFE14D'), OUT, 10)
    text(c, "RAHMAT", 1200, 568, 42, (1, 1, 1), OUT, 8)
    # opening
    c.rectangle(760, 700, 880, 640); fs(c, hx('#7A4E2E') if not night else hx('#8A5A30'), 6)
    c.rectangle(770, 705, 860, 120); fill(c, hx('#6A4026'))
    for yb in (830, 940, 1050):
        c.rectangle(765, yb, 870, 14); fs(c, hx('#B98A56'), 3)
    for (sx, yb, w, h, col, kind) in SHELF:
        if kind == 'bottle':
            rrect(c, sx + 6, yb - h, w - 12, h, 8); fs(c, hx('#F4C430'), 3)
            c.rectangle(sx + w / 2 - 5, yb - h - 10, 10, 12); fill(c, hx('#2EAD6B'))
        else:
            c.rectangle(sx, yb - h, w, h); fs(c, col, 3)
            c.rectangle(sx + 4, yb - h * .6, w - 8, h * .2); fill(c, (1, 1, 1), .6)
    # lamp
    c.move_to(1200, 705); c.line_to(1200, 760); c.set_source_rgb(*OUT); c.set_line_width(3); c.stroke()
    ell(c, 1200, 775, 18, 22); fs(c, hx('#FFF3B0'), 3)
    # rahmat behind counter
    rp = st.get('rahmat_counter')
    if rp is not None:
        person(c, rp.get('x', 1225), 1370, 'rahmat', rp, t=t)
    # counter (etalase)
    c.rectangle(890, 1150, 680, 26); fs(c, hx('#A8763E'), 5)
    c.rectangle(900, 1176, 660, 165); fs(c, hx('#BFE4F2'), 5, .85)
    for i in range(10):
        rrect(c, 915 + i * 64, 1250, 48, 70, 6); fs(c, PAL[i % len(PAL)], 3)
    c.move_to(940, 1190); c.line_to(1010, 1330); c.set_source_rgba(1, 1, 1, .6); c.set_line_width(10); c.stroke()
    # hanging sachets
    for gi, gx in enumerate((790, 1530)):
        for k in range(3):
            xx = gx + k * 30
            c.move_to(xx + 12, 700); c.line_to(xx + 12, 720); c.set_source_rgb(*OUT); c.set_line_width(2); c.stroke()
            for j in range(6):
                rrect(c, xx, 720 + j * 34, 24, 30, 3); fs(c, SACHET[(gi * 18 + k * 6 + j) % 30], 2.5)
    # awning
    poly(c, [(680, 640), (1720, 640), (1770, 715), (630, 715)]); fs(c, hx('#2F7FD1'), 6)
    for i in range(12):
        x0 = 680 + i * 87
        poly(c, [(x0, 640), (x0 + 43, 640), (x0 + 43 + 4, 715), (x0 + 4, 715)]); fill(c, (1, 1, 1), .85)
    poly(c, [(680, 640), (1720, 640), (1770, 715), (630, 715)]); c.set_source_rgb(*OUT); c.set_line_width(6); c.stroke()
    # sacks stack
    for (sx, sy) in [(790, 1320), (900, 1328), (1010, 1324), (845, 1250), (955, 1256), (900, 1182)]:
        if sx > 880 and sy > 1300: continue
        sack(c, sx - 20, sy, 120, 78)
    # galon & gas
    rrect(c, 1600, 1215, 66, 110, 18); fs(c, hx('#5BB8F5'), 5, .9)
    rrect(c, 1616, 1192, 34, 26, 6); fs(c, hx('#2E86DE'), 4)
    rrect(c, 1585, 1300, 100, 50, 10); fs(c, hx('#7AC74F'), 5)
    text(c, "3kg", 1635, 1325, 26, (1, 1, 1), OUT, 5)
    # wall sign
    rrect(c, 1652, 760, 40, 300, 6)
    # extras behind (boxes pile)
    nbox = st.get('boxes', 0)
    for i in range(int(nbox)):
        bx = 1720 + (i % 2) * 105; by = 1345 - (i // 2) * 72
        sc = pop(t, st.get('box_t0', 0) + i * 0.25, .3)
        if sc <= 0: continue
        c.save(); c.translate(bx + 50, by - 34); c.scale(sc, sc)
        c.rectangle(-50, -34, 100, 68); fs(c, hx('#C98B4A'), 5)
        c.rectangle(-50, -6, 100, 10); fill(c, hx('#E8C27A'))
        c.restore()
    # chair + child
    if st.get('child'):
        cx_ = 640
        rrect(c, cx_ - 10, 1180, 120, 20, 6); fs(c, hx('#E5473B'), 5)
        rrect(c, cx_ - 20, 1030, 22, 160, 8); fs(c, hx('#E5473B'), 5)
        for lx_ in (cx_ - 5, cx_ + 95):
            line(c, [(lx_, 1200), (lx_, 1345)], 10, hx('#C0392B'), False)
        person(c, cx_ + 20, 1340, 'anak', {'sit': True, 'eyes': 'closed', 'tilt': -18, 'expr': 'o', 'aF': (20, 30), 'aB': (10, 20), 'bob': 0.3}, s=0.62, t=t)
        zzz(c, cx_ + 60, 1000, t)
    # ---------------- NEIGHBOR HOUSE
    c.rectangle(1850, 700, 800, 650); fs(c, hx('#BFE3B4'), 6)
    poly(c, [(1800, 715), (2700, 715), (2250, 430)]); fs(c, hx('#C9452E'), 6)
    for k in range(1, 6):
        yy = 430 + k * 50; half = (yy - 430) / 285 * 450
        c.move_to(2250 - half, yy); c.line_to(2250 + half, yy); c.set_source_rgba(*OUT, .35); c.set_line_width(3); c.stroke()
    # window with neighbor
    wx0, wy0, ww, wh = 2060, 860, 290, 250
    win_lit = st.get('win_lit', False)
    c.rectangle(wx0, wy0, ww, wh); fill(c, hx('#FFE9A6') if win_lit else hx('#3C5468'))
    jp = st.get('julit_win')
    if jp is not None and not jp.get('peek'):
        c.save(); c.rectangle(wx0, wy0, ww, wh); c.clip()
        person(c, jp.get('x', 2205), 1335 + jp.get('dy', 0), 'julit', jp, t=t, flip=jp.get('flip', True))
        c.restore()
    # curtains
    cl = st.get('curtain', 0.0)
    for side in (0, 1):
        if side == 0:
            c.move_to(wx0, wy0); c.line_to(wx0 + 60 + cl * 70, wy0); c.curve_to(wx0 + 40 + cl * 70, wy0 + 120, wx0 + 70 + cl * 60, wy0 + 200, wx0 + 30, wy0 + wh); c.line_to(wx0, wy0 + wh)
        else:
            c.move_to(wx0 + ww, wy0); c.line_to(wx0 + ww - 60 - cl * 90, wy0); c.curve_to(wx0 + ww - 40 - cl * 90, wy0 + 120, wx0 + ww - 70 - cl * 80, wy0 + 200, wx0 + ww - 30, wy0 + wh); c.line_to(wx0 + ww, wy0 + wh)
        c.close_path(); fs(c, hx('#F28AA8'), 4)
        if side == 0 and jp is not None and jp.get('peek'):
            c.save(); c.rectangle(wx0, wy0, ww, wh); c.clip()
            person(c, jp.get('x', 2205), 1335 + jp.get('dy', 0), 'julit', jp, t=t, flip=True)
            c.restore()
    c.rectangle(wx0, wy0, ww, wh); c.set_source_rgb(*hx('#FFFFFF')); c.set_line_width(16); c.stroke()
    c.rectangle(wx0, wy0, ww, wh); c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
    rrect(c, wx0 - 20, wy0 + wh, ww + 40, 24, 6); fs(c, (1, 1, 1), 5)
    rrect(c, 2420, 1000, 150, 350, 8); fs(c, hx('#8A5A3B'), 6)
    ell(c, 2545, 1180, 9, 9); fs(c, hx('#F5C02E'), 3)
    # pots
    for px_ in (1900, 2000):
        poly(c, [(px_, 1290), (px_ + 70, 1290), (px_ + 58, 1350), (px_ + 12, 1350)]); fs(c, hx('#C0703A'), 5)
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * .45
            c.move_to(px_ + 35, 1290); c.curve_to(px_ + 35 + 30 * math.cos(a), 1290 + 60 * math.sin(a), px_ + 35 + 60 * math.cos(a), 1290 + 70 * math.sin(a), px_ + 35 + 70 * math.cos(a), 1290 + 80 * math.sin(a))
            c.set_source_rgb(*hx('#3E9B47')); c.set_line_width(9); c.stroke()
    # ---------------- messy yard
    for px_ in (2720, 3180):
        c.rectangle(px_ - 8, 900, 16, 450); fs(c, hx('#7A5230'), 4)
    c.move_to(2720, 930); c.curve_to(2850, 990, 3050, 990, 3180, 930); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
    clothes = [(2770, hx('#E5473B'), 'shirt', .2), (2880, hx('#2E86DE'), 'pants', -.15), (2990, hx('#F2C230'), 'shirt', .35), (3090, hx('#9B4DCA'), 'sock', -.3)]
    for cx_, col, kd, rot in clothes:
        yy = 930 + 60 * math.sin((cx_ - 2720) / 460 * math.pi) * .9
        c.save(); c.translate(cx_, yy); c.rotate(rot + .05 * math.sin(t * 2 + cx_))
        if kd == 'shirt':
            poly(c, [(-45, 0), (45, 0), (60, 30), (38, 40), (38, 120), (-38, 120), (-38, 40), (-60, 30)]); fs(c, col, 4)
        elif kd == 'pants':
            poly(c, [(-35, 0), (35, 0), (40, 150), (8, 150), (0, 50), (-8, 150), (-40, 150)]); fs(c, col, 4)
        else:
            poly(c, [(-10, 0), (14, 0), (14, 60), (34, 76), (24, 92), (-10, 70)]); fs(c, col, 4)
        c.restore()
    for bx, by, r in [(2800, 1310, 50), (2870, 1320, 42)]:
        ell(c, bx, by, r, r * .85); fs(c, hx('#26262A'), 5)
        c.move_to(bx - 8, by - r * .85); c.line_to(bx, by - r - 18); c.line_to(bx + 8, by - r * .85); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
    for k, (cx_, rot) in enumerate([(2960, .4), (3010, -1.2), (3080, .9)]):
        c.save(); c.translate(cx_, 1335); c.rotate(rot); rrect(c, -14, -22, 28, 44, 5); fs(c, PAL[k], 4); c.restore()
    # cat
    cx_ = 3120; cy_ = 1330
    ell(c, cx_, cy_ - 25, 45, 28); fs(c, hx('#F07D2B'), 5)
    ell(c, cx_ + 40, cy_ - 55, 28, 26); fs(c, hx('#F07D2B'), 5)
    poly(c, [(cx_ + 24, cy_ - 72), (cx_ + 30, cy_ - 98), (cx_ + 42, cy_ - 78)]); fs(c, hx('#F07D2B'), 4)
    poly(c, [(cx_ + 46, cy_ - 78), (cx_ + 60, cy_ - 98), (cx_ + 62, cy_ - 70)]); fs(c, hx('#F07D2B'), 4)
    c.move_to(cx_ - 42, cy_ - 25); c.curve_to(cx_ - 90, cy_ - 30 + 20 * math.sin(t * 3), cx_ - 80, cy_ - 80, cx_ - 70, cy_ - 90)
    c.set_source_rgb(*OUT); c.set_line_width(14); c.stroke()
    c.move_to(cx_ - 42, cy_ - 25); c.curve_to(cx_ - 90, cy_ - 30 + 20 * math.sin(t * 3), cx_ - 80, cy_ - 80, cx_ - 70, cy_ - 90)
    c.set_source_rgb(*hx('#F07D2B')); c.set_line_width(7); c.stroke()
    for ex_ in (32, 50):
        ell(c, cx_ + ex_, cy_ - 58, 3, 5); fill(c, OUT)
    # ---------------- street characters
    for ch in st.get('people', []):
        person(c, ch['x'], ch['y'], ch['who'], ch, s=ch.get('s', 1.0), t=t, flip=ch.get('flip', False))
    car = st.get('car')
    if car:
        if car.get('smoke'):
            for k in range(4):
                ph = (t * 1.6 + k / 4) % 1
                ell(c, car['x'] - 30 - ph * 160, car['y'] - 100 - ph * 50, 20 + ph * 40, 20 + ph * 40); fill(c, (.85, .85, .85), .6 * (1 - ph))
            for k in range(3):
                yy = car['y'] - 330 + k * 90
                c.move_to(car['x'] - 80 - k * 30, yy); c.line_to(car['x'] - 260 - k * 30, yy)
                c.set_source_rgba(1, 1, 1, .8); c.set_line_width(8); c.stroke()
        c.save(); c.translate(car['x'] + 690, car['y']); c.rotate(car.get('pitch', 0)); c.translate(-(car['x'] + 690), -car['y'])
        gran_max(c, car['x'], car['y'], t, car.get('ang', 0), car.get('driver', False), car.get('door', 0), driver_po=car.get('dpo'))
        c.restore()
        if car.get('after'): car['after'](c)
    for ch in st.get('people_front', []):
        person(c, ch['x'], ch['y'], ch['who'], ch, s=ch.get('s', 1.0), t=t, flip=ch.get('flip', False))
    for f in st.get('fx', []):
        f(c)
    # night tint
    if night:
        c.save()
        c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        c.rectangle(-3000, -3000, 9000, 9000)
        c.rectangle(760, 700, 880, 650)
        if win_lit: c.rectangle(wx0, wy0, ww, wh)
        c.set_source_rgba(.03, .05, .18, .5); c.fill()
        c.restore()
        bulb_glow(c, 1200, 775, 480, .45)
        if win_lit: bulb_glow(c, 2205, 980, 260, .35)
        for f in st.get('fx_night', []):
            f(c)

# ---------------------------------------------------------------- vignettes
def draw_motor_scene(c, t, t0):
    g = cairo.LinearGradient(0, 0, 0, 1400)
    g.add_color_stop_rgb(0, *hx('#FF8A4C')); g.add_color_stop_rgb(1, *hx('#FFD9A0'))
    c.set_source(g); c.rectangle(-500, -500, 2100, 2000); c.fill()
    bulb_glow(c, 760, 760, 400, .6); ell(c, 760, 760, 120, 120); fill(c, hx('#FFE07A'))
    off = (t - t0) * 900
    for i in range(-2, 12):
        bx = (i * 260 - off * 0.35) % 2600 - 600
        c.rectangle(bx, 900 - (i * 47 % 120), 200, 600); fill(c, hx('#C9765A'))
        poly(c, [(bx - 20, 910 - (i * 47 % 120)), (bx + 220, 910 - (i * 47 % 120)), (bx + 100, 800 - (i * 47 % 120))]); fill(c, hx('#A55A44'))
    for i in range(-2, 10):
        tx = (i * 420 - off * .8) % 3000 - 800
        c.rectangle(tx - 10, 900, 20, 450); fs(c, hx('#6B4A33'), 4)
        ell(c, tx, 880, 110, 100); fs(c, hx('#3E8E4A'), 6)
    c.rectangle(-500, 1340, 2100, 90); fs(c, hx('#C9C3B6'), 5)
    c.rectangle(-500, 1430, 2100, 1400); fill(c, hx('#55585E'))
    for i in range(-2, 12):
        c.rectangle((i * 240 - off) % 2700 - 600, 1640, 130, 14); fill(c, hx('#F2F2F2'), .85)
    mx = 540; my = 1600 + 4 * math.sin(t * 20)
    ang = (t - t0) * 16
    # boxes on back
    for k, (bx, by) in enumerate([(-200, -230), (-120, -230), (-160, -300)]):
        rrect(c, mx + bx - 40, my + by - 35, 84, 70, 4); fs(c, hx('#C98B4A'), 5)
    motor(c, mx, my, t, ang)
    person(c, mx - 50, my - 40, 'rahmat', {'sit': True, 'aF': (100, -10), 'aB': (95, -5), 'expr': 'grin', 'bob': 0}, s=1.0, t=t)
    for k in range(4):
        yy = 1200 + k * 80
        c.move_to(250 - k * 40, yy); c.line_to(80 - k * 40, yy); c.set_source_rgba(1, 1, 1, .8); c.set_line_width(8); c.stroke()

def draw_count_scene(c, t, t0):
    c.rectangle(-500, -500, 2100, 3000); fill(c, hx('#5A3B2A'))
    for i in range(-3, 10):
        c.rectangle(i * 180, -500, 6, 3000); fill(c, hx('#4D3223'))
    # clock
    ell(c, 820, 520, 90, 90); fs(c, (1, 1, 1), 7)
    for k in range(12):
        a = k * math.pi / 6
        c.move_to(820 + 72 * math.cos(a), 520 + 72 * math.sin(a)); c.line_to(820 + 80 * math.cos(a), 520 + 80 * math.sin(a))
        c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
    line(c, [(820, 520), (820, 460)], 8, OUT, False); line(c, [(820, 520), (820 + 55 * math.sin(t * 2), 520 - 55 * math.cos(t * 2))], 5, OUT, False)
    # lamp
    c.move_to(540, -500); c.line_to(540, 640); c.set_source_rgb(*OUT); c.set_line_width(4); c.stroke()
    poly(c, [(470, 690), (610, 690), (580, 630), (500, 630)]); fs(c, hx('#2E6B4A'), 5)
    ell(c, 540, 700, 24, 22); fill(c, hx('#FFF3B0'))
    bulb_glow(c, 540, 760, 650, .5)
    person(c, 540, 1420, 'rahmat', {'aF': (130 + 15 * math.sin(t * 8), -60), 'aB': (120, -50), 'eyes': 'half', 'expr': 'smile', 'look': (0, 6)}, s=1.15, t=t)
    # table
    c.rectangle(-100, 1230, 1300, 60); fs(c, hx('#A8763E'), 6)
    c.rectangle(-100, 1290, 1300, 900); fill(c, hx('#8A5E30'))
    # notebook
    rrect(c, 120, 1170, 220, 70, 6); fs(c, hx('#F6F1E4'), 5)
    text(c, "BUKU KAS", 230, 1200, 26, hx('#2050B0'))
    # coins
    for k, (cx_, n) in enumerate([(620, 6), (700, 4), (780, 8), (860, 3)]):
        for j in range(n):
            ell(c, cx_, 1222 - j * 14, 34, 11); fs(c, hx('#F2C230'), 4)
    for k in range(3):
        rrect(c, 380 + k * 18, 1196 - k * 8, 150, 34, 4); fs(c, hx('#8FD18A'), 4)
    # flying coins
    for k in range(3):
        ph = ((t - t0) * 1.4 + k / 3) % 1
        x = 560 + 60 * k; y = 1100 - ph * 300
        ell(c, x, y, 26 * (1 - .5 * ph), 26); fs(c, hx('#F2C230'), 4, 1 - ph)

# ---------------------------------------------------------------- screen overlays
def label_pill(c, s, t, t0, y=300, col=hx('#FFE14D')):
    k = pop(t, t0, .35)
    if k <= 0: return
    c.save(); c.translate(W / 2, y); c.scale(k, k); c.rotate(-0.04)
    c.select_font_face("Inter Black"); c.set_font_size(78)
    w = c.text_extents(s).width + 90
    rrect(c, -w / 2, -62, w, 124, 30); fs(c, col, 9)
    text(c, s, 0, 0, 78, OUT)
    c.restore()

def name_tag(c, t, t0):
    k = pop(t, t0, .4)
    if k <= 0: return
    c.save(); c.translate(W / 2, 330); c.scale(k, k)
    rrect(c, -300, -80, 600, 160, 30); fs(c, hx('#2F8F5B'), 10)
    text(c, "PAK RAHMAT", 0, -10, 84, (1, 1, 1), OUT, 12)
    text(c, "juragan sembako", 0, 50, 36, hx('#FFE14D'), OUT, 6)
    c.restore()

def clock_bubble(c, t, t0, s_, y=330, x=W / 2):
    k = pop(t, t0, .3)
    if k <= 0: return
    c.save(); c.translate(x, y); c.scale(k, k)
    rrect(c, -190, -75, 380, 150, 40); fs(c, (1, 1, 1), 9)
    ell(c, -110, 0, 46, 46); fs(c, hx('#FFE14D'), 6)
    line(c, [(-110, 0), (-110, -28)], 6, OUT, False); line(c, [(-110, 0), (-88, 8)], 6, OUT, False)
    text(c, s_, 40, 0, 84, OUT)
    c.restore()

def calendar(c, t, t0, t1, y0=2021, y1=2026):
    k = pop(t, t0, .3)
    if k <= 0: return
    yr = int(lerp(y0, y1 + 0.999, clamp((t - t0 - .3) / (t1 - t0 - .6))))
    c.save(); c.translate(W / 2, 330); c.scale(k, k)
    rrect(c, -170, -150, 340, 300, 26); fs(c, (1, 1, 1), 9)
    c.save(); rrect(c, -170, -150, 340, 300, 26); c.clip(); c.rectangle(-170, -150, 340, 90); fill(c, hx('#E23A3A')); c.restore()
    rrect(c, -170, -150, 340, 300, 26); c.set_source_rgb(*OUT); c.set_line_width(9); c.stroke()
    for rx in (-90, 90):
        rrect(c, rx - 12, -180, 24, 60, 10); fs(c, hx('#9AA1A9'), 5)
    text(c, "TAHUN", 0, -102, 40, (1, 1, 1))
    flip = ((t - t0) * (y1 - y0 + 1) / (t1 - t0)) % 1
    c.save(); c.translate(0, 40); c.scale(1, 1 - 0.0 * flip)
    text(c, str(yr), 0, 0, 104, OUT)
    c.restore()
    c.restore()

# ---------------------------------------------------------------- captions
WORDS = []   # master: narasi episode dibaca di gaya.py
FIX = {12: "sembako", 15: "nyaingin", 16: "Alfamart?", 17: "Kenalin", 28: "nganterin", 29: "pesenan,",
       64: "banget,", 73: "tidur", 74: "nyenyak,", 105: "Gran", 113: "tokonya.", 142: "Gran", 146: "nyinyir",
       167: "Bubuhanmu", 103: "Daihatsu", 121: "diantar"}
DROP = {104, 114, 122}
words = []
for i, (w, a, b) in enumerate(WORDS):
    if i in DROP:
        words[-1][2] = b; continue
    words.append([FIX.get(i, w), a, b])
CHUNKS = []
cur = []
for w in words:
    cur.append(w)
    txt = " ".join(x[0] for x in cur)
    if len(cur) >= 3 or w[0][-1] in ",.?!" or len(txt) > 15:
        CHUNKS.append(cur); cur = []
if cur: CHUNKS.append(cur)

def captions(c, t):
    for ci, ch in enumerate(CHUNKS):
        a = ch[0][1] - 0.05
        b = CHUNKS[ci + 1][0][1] - 0.05 if ci + 1 < len(CHUNKS) else DUR
        b = min(b, ch[-1][2] + 0.6)
        if not (a <= t < b): continue
        k = pop(t, a, .18)
        size = 104
        c.select_font_face("Inter Black"); c.set_font_size(size)
        strs = [w[0].upper() for w in ch]
        sp = c.text_extents(" ").x_advance
        tot = sum(c.text_extents(s).x_advance for s in strs) + sp * (len(strs) - 1)
        if tot > 980:
            size = size * 980 / tot; c.set_font_size(size)
            tot = sum(c.text_extents(s).x_advance for s in strs) + sp * (len(strs) - 1) * size / 104
            sp = c.text_extents(" ").x_advance
        c.save(); c.translate(W / 2, 1390); c.scale(k, k); c.rotate(-0.02)
        x = -tot / 2
        for w, s in zip(ch, strs):
            cur_w = [x for x in ch if x[1] - 0.03 <= t]
            col = hx('#FFE14D') if (cur_w and w is cur_w[-1]) else (1, 1, 1)
            if s.startswith('§'):
                c.set_font_size(size); adv = c.text_extents(s[1:]).x_advance
                rrect(c, x - 6, -size * 0.52, adv + 12, size * 1.04, 14); fs(c, (0.05, 0.05, 0.06), 7)
                text(c, "TIIIT", x + adv / 2, 0, size * 0.42, (1, 1, 1))
            else:
                adv = text(c, s, x, 0, size, col, OUT, size * 0.2, align='l')
            x += adv + sp
        c.restore()

# ---------------------------------------------------------------- scenes
def cam_keys(keys, t):
    if t <= keys[0][0]: return keys[0][1:]
    for (ta, *pa), (tb, *pb) in zip(keys, keys[1:]):
        if ta <= t <= tb:
            k = ease((t - ta) / (tb - ta))
            return tuple(lerp(p, q, k) for p, q in zip(pa, pb))
    return keys[-1][1:]

def J(**kw):  # julit window pose helper
    d = {'flip': True}
    d.update(kw); return d

def street_state(t):
    st = {'people': [], 'people_front': [], 'fx': [], 'fx_night': []}
    m = julit_mouth(t)
    if t < 7.3:
        st['tod'] = 'night'; st['win_lit'] = True
        st['rahmat_counter'] = {'aF': (150 + 10 * math.sin(t * 6), -40), 'aB': (40, 20), 'expr': 'smile', 'look': (-4, -2)}
        st['julit_win'] = J(mouth=m, eyes='squint', brows='angry', aF=(160, -100), aB=(20, 10), expr='frown', look=(4, 0))
        st['curtain'] = 0.6
        if t > 4.7:
            st['fx'].append(lambda c: exclaim(c, 2330, 820, pop(t, 4.75, .3)))
    elif t < 15.2:
        st['tod'] = 'dawn' if t < 9.3 else 'day'
        st['sun_y'] = 420
        if t < 9.3:
            st['tod'] = 'day'
            wave = 150 + 25 * math.sin(t * 10)
            st['people'].append({'who': 'rahmat', 'x': 1240, 'y': 1395, 'aF': (wave, 20), 'expr': 'grin', 'eyes': 'happy'})
        elif t < 10.6:
            st['tod'] = 'dawn'; st['sun_y'] = 380
            def hold(c, hnd):
                sack(c, hnd[0] - 30, hnd[1] - 60, 150, 92, True, .15)
            st['people'].append({'who': 'rahmat', 'x': 820 + (t - 9.3) * 120, 'y': 1395, 'aF': (165, -10), 'aB': (-20, -10), 'expr': 'grin', 'brows': 'up', 'step': 1, 'hold': hold})
            st['fx'].append(lambda c: sweat(c, 760 + (t - 9.3) * 120, 1030))
        else:
            def bag(c, hnd):
                c.move_to(hnd[0] - 30, hnd[1]); c.curve_to(hnd[0] - 30, hnd[1] - 30, hnd[0] + 30, hnd[1] - 30, hnd[0] + 30, hnd[1])
                c.set_source_rgb(*OUT); c.set_line_width(5); c.stroke()
                rrect(c, hnd[0] - 45, hnd[1], 90, 100, 10); fs(c, hx('#F2F2F2'), 5, .95)
                rrect(c, hnd[0] - 30, hnd[1] - 30 + 40, 26, 50, 6); fs(c, hx('#F4C430'), 3)
            k = ease((t - 10.6) / 0.6)
            st['rahmat_counter'] = {'x': 1225, 'aF': (lerp(40, 75, k), lerp(20, 10, k)), 'aB': (30, 20), 'expr': 'grin', 'flip': True}
            st['people_front'].append({'who': 'b2', 'x': 1000, 'y': 1420, 'aF': (80, -10), 'expr': 'smile', 'eyes': 'happy'})
            st['fx'].append(lambda c: bag(c, (1225 + 60 + lerp(40, 75, k) * 1.8, 1170)))
        st['julit_win'] = None
    elif t < 28.6:
        st['tod'] = 'day'
        st['rahmat_counter'] = {'aF': (150 + 10 * math.sin(t * 6), -40), 'aB': (40, 20), 'expr': 'smile'}
        if t < 19.1:
            # gossip
            hand = (150, -120)
            st['people'].append({'who': 'friend', 'x': 2360, 'y': 1400, 'flip': True, 'aF': (60, 80), 'expr': 'o', 'look': (5, 0), 'brows': 'up', 'mouth': 0.4 * abs(math.sin(t * 9)) if t > 17 else 0})
            st['people'].append({'who': 'julit', 'x': 2100, 'y': 1400, 'flip': True, 'aF': hand, 'aB': (20, 10), 'expr': 'pout', 'eyes': 'squint', 'brows': 'angry', 'look': (6, 0)})
        else:
            shocked = t >= 22.85
            if not shocked:
                wave = (120 + 30 * math.sin(t * 7), -30)
                st['people'].append({'who': 'friend', 'x': 2360, 'y': 1400, 'flip': True, 'aF': (60, 80), 'expr': 'smile', 'eyes': 'squint', 'look': (5, 0)})
                st['people'].append({'who': 'julit', 'x': 2100, 'y': 1400, 'flip': True, 'aF': wave, 'aB': (20, 10), 'mouth': m, 'eyes': 'squint', 'brows': 'smug', 'look': (4, 0)})
            else:
                st['people'].append({'who': 'friend', 'x': 2360, 'y': 1400, 'flip': True, 'aF': (150, -90), 'expr': 'grin', 'eyes': 'happy'})
                st['people'].append({'who': 'julit', 'x': 2100, 'y': 1400, 'flip': True, 'aF': (170, -150), 'aB': (160, -140), 'expr': 'o', 'eyes': 'wide', 'look': (0, 0)})
                st['fx'].append(lambda c: sweat(c, 2010, 1000, 1.2))
                st['fx'].append(lambda c: exclaim(c, 2100, 860, pop(t, 22.9, .3) * 1.3))
    elif t < 36.1:
        st['tod'] = 'night'
        st['rahmat_counter'] = {'aF': (160 + 15 * math.sin(t * 5), -50), 'aB': (40, 20), 'expr': 'smile', 'eyes': 'half', 'look': (-6, -4)}
        st['child'] = True
        st['curtain'] = 0.0
        st['fx_night'].append(lambda c: zzz(c, 2280, 880, t, 1.2))
        st['fx_night'].append(lambda c: zzz(c, 300, 860, t + .4, 1.0))
    elif t < 40.4:
        st['tod'] = 'day'
        st['rahmat_counter'] = {'aF': (90 + 50 * math.sin(t * 9), 10), 'aB': (100 + 40 * math.sin(t * 9 + 2), 0), 'expr': 'grin', 'look': (-4, 0)}
        q = [('b1', 1080), ('b2', 900), ('b3', 720), ('b4', 540), ('friend', 360)]
        for i, (w, x) in enumerate(q):
            if t > 37.6 + i * .15:
                st['people_front'].append({'who': w, 'x': x + 40 * eout((t - 37.6 - i * .15) / .5) - 40, 'y': 1440 + (i % 2) * 20, 'expr': 'smile', 'aF': (20, 20)})
        st['boxes'] = 6; st['box_t0'] = 38.8
    elif t < 42.2:
        st['tod'] = 'dawn'
        st['sun_y'] = lerp(700, 380, eout((t - 40.4) / 1.8))
    else:
        st['tod'] = 'morning'
        st['boxes'] = 6; st['box_t0'] = -10
        # car
        if t < 44.9:
            k = eout((t - 42.2) / 2.7)
            cx_ = lerp(-1500, 760, k)
            smoke = True
        else:
            cx_ = 760; smoke = False
        ang = (cx_ + 1500) / 62
        car = {'x': cx_, 'y': 1580, 'ang': ang, 'smoke': smoke, 'driver': t < 55.6, 'dpo': {'aF': (110, 20), 'expr': 'smile'}}
        if t >= 54.9: car['door'] = ease((t - 54.9) / .4)
        st['car'] = car
        # rahmat outside
        if t >= 55.6:
            k = eout((t - 55.6) / .5)
            if t < 64:
                arm_f = (165, -15) if t > 57.6 else (120, -20)
                def keys(c, hnd, tt=t):
                    for kk in range(2):
                        ell(c, hnd[0] + 10 + kk * 12, hnd[1] - 30 + 8 * math.sin(tt * 18 + kk), 12, 12); c.set_source_rgb(*hx('#F2C230')); c.set_line_width(6); c.stroke()
                st['people_front'].append({'who': 'rahmat', 'x': lerp(1560, 1760, k), 'y': 1620, 'aF': arm_f, 'aB': (-15, -10), 'expr': 'grin', 'eyes': 'happy' if t > 57.6 else 'open', 'hold': keys})
            else:
                st['people_front'].append({'who': 'rahmat', 'x': 1760, 'y': 1620, 'aF': (175, -60), 'aB': (-15, -10), 'expr': 'grin', 'eyes': 'happy', 'tilt': 4 * math.sin(t * 3)})
        # neighbor window
        if t >= 46.7:
            up = eout((t - 46.75) / .45)
            if t < 49:
                st['julit_win'] = J(dy=lerp(330, 0, up), eyes='wide', expr='o', aF=(20, 10), look=(-6, 0))
                st['fx'].append(lambda c: exclaim(c, 2330, 820, pop(t, 47.2, .3)))
            elif t < 54.1:
                st['julit_win'] = J(mouth=m, eyes='squint', brows='smug', aF=(100, -10), look=(-6, 2))
                st['curtain'] = 0.4
            elif t < 57.6:
                big = t >= 56.3
                st['julit_win'] = J(mouth=m if not big else 0, eyes='wide', brows='up', expr='o', aF=(170, -150) if big else (20, 10), look=(-6, 2))
                if big:
                    st['fx'].append(lambda c: sweat(c, 2130, 950, 1.0))
                    st['fx'].append(lambda c: exclaim(c, 2330, 820, pop(t, 56.35, .3) * 1.2))
            else:
                # peeking from behind curtain
                st['curtain'] = 0.9
                st['curtain'] = 0.3
                st['julit_win'] = J(x=2236, dy=40, peek=True, eyes='open', brows='angry', expr='frown', aF=(20, 10), look=(-8, 2), tilt=-10)
                def front(c):
                    pass
                if t > 61.2:
                    st['fx'].append(lambda c: sweat(c, 2310, 930, .8))
        if t > 57.6 and t < 64:
            for k in range(6):
                ph = (t * .8 + k / 6) % 1
                a = k * 1.1
                st['fx'].append(lambda c, ph=ph, a=a: spark(c, 1200 + 520 * math.cos(a) * .9, 1300 + 260 * math.sin(a), 26 * math.sin(ph * math.pi), math.sin(ph * math.pi)))
    return st

SCENES = [
 # (t0, t1, kind, camkeys)
 (0.0, 7.3, 'street', [(0, 1500, 980, .62), (1.7, 1250, 1010, .95), (4.6, 1260, 1000, 1.0), (5.3, 2200, 1000, 1.45), (7.3, 2200, 990, 1.6)]),
 (7.3, 9.3, 'street', [(7.3, 1240, 1080, 1.3), (9.3, 1240, 1060, 1.5)]),
 (9.3, 10.6, 'street', [(9.3, 860, 1100, 1.35), (10.6, 940, 1080, 1.45)]),
 (10.6, 12.0, 'street', [(10.6, 1120, 1120, 1.25), (12.0, 1130, 1100, 1.4)]),
 (12.0, 13.25, 'motor', [(12.0, 540, 1330, 1.0), (13.25, 560, 1330, 1.08)]),
 (13.25, 15.2, 'count', [(13.25, 540, 1050, 1.0), (15.2, 540, 1080, 1.18)]),
 (15.2, 19.1, 'street', [(15.2, 1900, 1050, .85), (19.1, 2200, 1080, 1.15)]),
 (19.1, 22.85, 'street', [(19.1, 2110, 1020, 1.9), (22.85, 2100, 1010, 2.1)]),
 (22.85, 26.8, 'street', [(22.85, 2150, 1030, 1.4), (24.8, 2150, 1030, 1.5), (26.8, 2150, 1030, 1.6)]),
 (26.8, 28.6, 'street', [(26.8, 2800, 1130, 1.2), (28.6, 2950, 1150, 1.35)]),
 (28.6, 36.1, 'street', [(28.6, 1500, 950, .6), (30.8, 1300, 1000, .85), (32.2, 1150, 1040, 1.05), (33.0, 760, 1150, 1.7), (36.1, 760, 1160, 1.85)]),
 (36.1, 40.4, 'street', [(36.1, 1200, 1060, .9), (38.7, 1250, 1080, .95), (40.4, 1550, 1100, 1.05)]),
 (40.4, 42.2, 'street', [(40.4, 1450, 820, .7), (42.2, 1400, 900, .75)]),
 (42.2, 46.7, 'car', None),
 (46.7, 49.0, 'street', [(46.7, 2205, 1000, 1.6), (49.0, 2205, 990, 1.75)]),
 (49.0, 54.1, 'street', [(49.0, 1750, 1100, .8), (54.1, 1800, 1100, .88)]),
 (54.1, 56.35, 'street', [(54.1, 1500, 1180, 1.1), (56.35, 1650, 1200, 1.25)]),
 (56.35, 57.6, 'street', [(56.35, 2205, 990, 1.7), (57.6, 2205, 990, 1.9)]),
 (57.6, 61.25, 'street', [(57.6, 1400, 1150, .95), (61.25, 1550, 1180, 1.1)]),
 (61.25, 64.1, 'street', [(61.25, 2250, 985, 1.8), (64.1, 2250, 985, 2.0)]),
 (64.1, 70.5, 'street', [(64.1, 1650, 1050, .7), (67.0, 1700, 1080, .78), (70.5, 1800, 1080, .85)]),
 (70.5, DUR + 1, 'street', [(70.5, 2230, 990, 1.6), (71.6, 2230, 990, 2.0)]),
]

def car_cam(t):
    k = eout((t - 42.2) / 2.7)
    cx_ = lerp(-1500, 760, k) + 430
    z = 0.9 if t < 44.9 else lerp(0.9, 1.0, ease((t - 44.9) / 1.8))
    return (cx_, 1180, z)

def render(fi):
    t = fi / FPS
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    sc = next(s for s in SCENES if s[0] <= t < s[1])
    t0, t1, kind, keys = sc
    cam = car_cam(t) if kind == 'car' else cam_keys(keys, t)
    cx_, cy_, z = cam
    shake = 0
    if 22.85 <= t < 23.3 or 56.35 <= t < 56.8 or 4.75 <= t < 5.0:
        shake = 14 * (1 - ((t % 1) * 3 % 1))
    c.save()
    c.translate(W / 2 + shake * math.sin(t * 90), H / 2 + shake * math.cos(t * 77))
    c.scale(z, z); c.translate(-cx_, -cy_)
    if kind in ('street', 'car'):
        draw_street(c, t, street_state(t))
    elif kind == 'motor':
        draw_motor_scene(c, t, t0)
    elif kind == 'count':
        draw_count_scene(c, t, t0)
    c.restore()
    # overlays
    if t < 4.7:
        clock_bubble(c, t, 1.6, "04.30" if t < 2.95 else "23.59")
    if 7.6 <= t < 9.3: name_tag(c, t, 7.9)
    if 9.3 <= t < 10.6: label_pill(c, "PAGI", t, 9.35)
    if 10.6 <= t < 12.0: label_pill(c, "SIANG", t, 10.65)
    if 12.0 <= t < 13.25: label_pill(c, "SORE", t, 12.05, col=hx('#FF9F43'))
    if 13.25 <= t < 15.2: label_pill(c, "MALAM", t, 13.3, col=hx('#7FB3FF'))
    if 15.3 <= t < 19.1: label_pill(c, "TETANGGA JULIT", t, 16.1, col=hx('#F7A8D8'))
    if 36.1 <= t < 40.4: calendar(c, t, 36.1, 39.6)
    if 40.4 <= t < 42.2: label_pill(c, "SUATU PAGI...", t, 40.5, col=hx('#FFD08A'))
    # vignette
    g = cairo.RadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * .75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, .28)
    c.set_source(g); c.paint()
    # flash at cuts
    for s in SCENES[1:]:
        d = t - s[0]
        if 0 <= d < 0.12:
            c.set_source_rgba(1, 1, 1, .5 * (1 - d / .12)); c.paint()
    captions(c, t)
    surf.flush()
    return bytes(surf.get_data())
