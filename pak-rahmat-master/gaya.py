"""MESIN GAYA PRO PLUS (dulu: bagian render ep4.py + ep4pro.py + ep4plus.py).
Dipakai semua episode. Episode cukup mendefinisikan adegan + pengaturan (lihat episode/ep4.py & episode/TEMPLATE.py).

Yang diatur di sini (seragam semua episode):
  - teks narasi per kata (zona aman TikTok x~490 y~1330, maks 3 kata, kata aktif kuning)
  - hook detik pertama, kartu BERSAMBUNG, kartu penutup 2 pilihan + FOLLOW UNTUK EP N+1, watermark
  - kamera TENANG: hanya zoom hentak di waktu PUNCH (maks 2x), tanpa whip/handheld/dutch angle
  - depth of field saat close-up (zoom > 1,3), grading per suasana, bloom/grain/vignette (aset_pro.post)
  - akting tambahan per episode lewat EP.akting(who, t, po)

Variabel episode (modul EP) yang dibaca:
  N, VDUR, DUR, SCENES = [(t0, t1, fungsi(c,t,t0), kamera)], kamera = daftar key (t,cx,cy,zoom) | fungsi(t) | 'split'
  HOOK = ("TEKS HOOK", sampai_detik) atau None
  PUNCH = (detik, ...)                        maks 2 zoom hentak
  SUASANA = [(t0, t1, 'day'|'morning'|'tense'|'warm'|'freeze'|...)]   selain itu 'day'
  BERSAMBUNG = detik muncul kartu "BERSAMBUNG..." atau None
  CTA = dict(baris1=..., baris2=..., pilihan=[(teks, '#warna'), (teks, '#warna')])
  opsional: efek_bawah(c,t) [sebelum grading], efek_atas(c,t) [sesudah grading, sebelum teks],
            akting(who,t,po), vignette(t) -> kekuatan (default .34), sebelum_frame(t)
"""
import math, json, os
import numpy as np
import cairo
from PIL import Image, ImageFilter
import aset_kampung as E
import aset_pro as P
import aset_mbg as G
import aset_dasar as lib
import aset_dio as D
from aset_dasar import W, H, OUT, hx, clamp, eout, pop, fs, fill, rrect, ell, poly, text

FPS = 30
SERI = "PAK RAHMAT SERIES"
EP = None
CHUNKS = []

P.GRADE['tense'] = (.94, .99, 1.08)
P.GRADE['warm'] = (1.06, 1.0, .91)


def durasi_suara(path="audio.wav"):
    """Panjang narasi (detik) dari audio.wav di folder kerja."""
    import subprocess
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


def muat_kata(path="words.json"):
    """words.json = [[kata, mulai, selesai], ...] (sudah dikoreksi). Dipecah maks 3 kata / 15 huruf per baris."""
    global CHUNKS
    words = [list(w) for w in json.load(open(path))] if os.path.exists(path) else []
    CHUNKS = []; cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= 3 or w[0][-1] in ",.?!" or len(" ".join(x[0] for x in cur)) > 15:
            CHUNKS.append(cur); cur = []
    if cur: CHUNKS.append(cur)


def pasang(ep):
    """Hubungkan modul episode ke mesin. Dipanggil sekali oleh jalankan.py."""
    global EP
    EP = ep
    muat_kata()
    P.tod_at = suasana
    if hasattr(ep, 'akting'):
        _person = E.person
        def person_plus(c, x, y, who, po=None, s=1.0, t=0.0, flip=False):
            po = dict(po or {})
            ep.akting(who, t, po)
            return _person(c, x, y, who, po, s=s, t=t, flip=flip)
        E.person = person_plus


def suasana(t):
    for a, b, m in getattr(EP, 'SUASANA', []):
        if a <= t < b: return m
    return 'day'


# ------------------------------------------------------------ teks & kartu
def captions_safe(c, t, base_y=1330, cx=490, maxw=840):
    VDUR = EP.VDUR
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
    h = getattr(EP, 'HOOK', None)
    if not h: return
    lbl, until = h
    if t >= until: return
    k = max(pop(t, .1, .25), .02)
    a = clamp((until - t) / .25)
    c.save(); c.translate(W / 2 - 40, 520); c.scale(k, k); c.rotate(-.1)
    c.push_group()
    rrect(c, -390, -120, 780, 240, 26); fs(c, hx('#D7141A'), 12)
    c.select_font_face("Inter Black"); c.set_font_size(104)
    size = min(104, 104 * 780 / max(1, c.text_extents(lbl).x_advance))   # hook panjang otomatis mengecil
    text(c, lbl, 0, 0, size, (1, 1, 1), OUT, 14)
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()


def bersambung(c, t):
    t0 = getattr(EP, 'BERSAMBUNG', None)
    if t0 is None: return
    k = pop(t, t0, .35)
    if k > .03 and t < EP.VDUR + .3:
        c.set_source_rgba(0, 0, 0, .5 * clamp((t - t0) / .3)); c.paint()
        c.save(); c.translate(W / 2 - 30, 900); c.scale(k, k); c.rotate(-.05)
        rrect(c, -380, -100, 760, 200, 24); fs(c, hx('#FFE14D'), 10)
        text(c, "BERSAMBUNG...", 0, 0, 84, OUT)
        c.restore()


def cta(c, t):
    VDUR = EP.VDUR
    if t < VDUR + .2: return
    cfg = EP.CTA
    d = t - (VDUR + .2)
    c.set_source_rgba(.04, .01, .03, min(.92, d * 4)); c.paint()
    k = max(pop(t, VDUR + .25, .35), .02)
    c.save(); c.translate(W / 2 - 30, 640); c.scale(k, k)
    rrect(c, -410, -190, 820, 380, 34); fs(c, (1, 1, 1), 10)
    text(c, cfg['baris1'], 0, -140, 46, OUT)
    text(c, cfg['baris2'], 0, -84, 52, hx('#D7141A'))
    for i, (lbl, col) in enumerate(cfg['pilihan'][:2]):
        c.save(); c.translate(-195 + i * 390, 60); c.rotate(.04 * math.sin(t * 6 + i * 2))
        rrect(c, -180, -70, 360, 140, 26); fs(c, hx(col), 8)
        c.select_font_face("Inter Black"); c.set_font_size(42)
        size = min(42, 42 * 320 / max(1, c.text_extents(lbl).x_advance))
        text(c, lbl, 0, 0, size, (1, 1, 1), OUT, 6)
        c.restore()
    c.restore()
    k2 = pop(t, VDUR + .7, .3)
    if k2 > .03:
        c.save(); c.translate(W / 2 - 30, 940); c.scale(k2, k2)
        text(c, "Tulis jawabanmu di komentar!", 0, 0, 46, (1, 1, 1), OUT, 8)
        c.restore()
    k3 = pop(t, VDUR + 1.1, .35)
    if k3 > .03:
        c.save(); c.translate(W / 2 - 30, 1120); c.scale(k3, k3); c.rotate(-.03)
        rrect(c, -350, -70, 700, 140, 70); fs(c, hx('#FFE14D'), 9)
        text(c, f"FOLLOW UNTUK EP {EP.N + 1}", -42, 0, 48, OUT)
        bx = 290 + 10 * math.sin(t * 8)
        poly(c, [(bx - 22, -26), (bx + 20, 0), (bx - 22, 26)]); fs(c, OUT, 2)
        c.restore()


def watermark(c, t):
    c.save(); c.translate(40, 215)
    rrect(c, 0, -26, 410, 52, 26); fill(c, (0, 0, 0), .32)
    ell(c, 30, 0, 16, 16); fill(c, hx('#D8312B'), .95)
    text(c, f"{SERI} • EP {EP.N}", 56, 0, 24, (1, 1, 1), align='l', alpha=.92)
    c.restore()


# ------------------------------------------------------------ kamera tenang + zoom hentak
def camera(t, keys):
    cx, cy, z = keys(t) if callable(keys) else lib.cam_keys(keys, t)
    punch = getattr(EP, 'PUNCH', ())
    for p in punch:
        if t >= p: z *= 1 + .07 * math.exp(-7 * (t - p))
    amp = 0
    for s in punch:
        if 0 <= t - s < .3: amp = max(amp, 10 * (1 - (t - s) / .3))
    return cx, cy, z, amp


def apply_cam(c, t, cam):
    cx, cy, z, amp = cam
    c.translate(W / 2 + amp * math.sin(t * 97), H / 2 + amp * math.cos(t * 73)); c.scale(z, z); c.translate(-cx, -cy)


def scene_draw(surf, c, t):
    """Gambar adegan; saat close-up (zoom > 1,3) latar diblur, tokoh & efek tetap tajam."""
    t0, t1, fn, keys = next(s for s in EP.SCENES if s[0] <= t < s[1])
    if keys == 'split':
        fn(c, t, t0); return
    cam = camera(t, keys)
    k = clamp((cam[2] - 1.3) / .4)
    if k <= 0.01:
        c.save(); apply_cam(c, t, cam); fn(c, t, t0); c.restore(); return
    D.MODE[0] = 'bg'
    c.save(); apply_cam(c, t, cam)
    try:
        fn(c, t, t0)
    except D.StopBG:
        pass
    c.restore()
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    sm = Image.fromarray(a[:, :, :3].copy()).resize((W // 4, H // 4), Image.BILINEAR)
    bl = np.asarray(sm.filter(ImageFilter.GaussianBlur(.8 + 2.6 * k)).resize((W, H), Image.BILINEAR)).astype(np.float32)
    mix = a[:, :, :3].astype(np.float32) * (1 - k) + bl * k
    np.copyto(a[:, :, :3], np.clip(mix, 0, 255).astype(np.uint8))
    surf.mark_dirty()
    D.MODE[0] = 'fg'
    try:
        c.save(); apply_cam(c, t, cam); fn(c, t, t0); c.restore()
    finally:
        D.MODE[0] = 'full'


# ------------------------------------------------------------ satu frame
def render(fi):
    t = fi / FPS
    DUR, VDUR = EP.DUR, EP.VDUR
    D.reset_tokoh()
    if hasattr(EP, 'sebelum_frame'): EP.sebelum_frame(t)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    scene_draw(surf, c, t)
    if hasattr(EP, 'efek_bawah'): EP.efek_bawah(c, t)
    P.post(surf, min(t, VDUR), 0.0)
    c = cairo.Context(surf)
    if hasattr(EP, 'efek_atas'): EP.efek_atas(c, t)
    hook(c, t)
    vg = EP.vignette(t) if hasattr(EP, 'vignette') else .34
    gr = cairo.RadialGradient(W / 2, H / 2, H * .32, W / 2, H / 2, H * .78)
    gr.add_color_stop_rgba(0, 0, 0, 0, 0); gr.add_color_stop_rgba(1, 0, 0, .04, vg)
    c.set_source(gr); c.paint()
    bersambung(c, t)
    captions_safe(c, t)
    cta(c, t)
    watermark(c, t)
    if t < .25: c.set_source_rgba(0, 0, 0, 1 - t / .25); c.paint()
    if t > DUR - .3: c.set_source_rgba(0, 0, 0, clamp((t - (DUR - .3)) / .3)); c.paint()
    surf.flush()
    return bytes(surf.get_data())
