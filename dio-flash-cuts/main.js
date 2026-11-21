// "DIO — Sales Daihatsu": Text Flash Cuts, 5.0 s, 1080×1920, 30 fps, 150 BPM (12 frames a beat).
// Everything is code: cards, rail, road, bar, inversion, editing, and the Gran Max itself (car.js: flat faces projected front 3/4 and side, a headlamp).
import { lerp, seg, eo, eio, hash } from '/core/lib.js';
import { buildCar } from './car.js';

const W = 1080, H = 1920, FPS = 30, BEAT = 12;
const RED = '#d4162b', BLK = '#0a0a0c', WHT = '#f2efe8', PALE = '#d8d4cc', DK = '#26262a', INK = '#1b1b1f';
const SERIF = '"SerifX"', SANS = '"SansX"';
const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const OUT = document.getElementById('out'), go = OUT.getContext('2d');
const S = mk(W, H), g0 = S.getContext('2d');
const IMG = {}, TXT = [];
const fs = f => f / FPS;
const RAILW = 300;                                          // Dio's red rail at the left edge
const PX = RAILW, PW = W - RAILW;                           // the picture panel beside it

// ───────── Timeline (frames) ─────────
const T_RAIL = 36, T_BAR = 72, T_SIL = 78, T_REV = 84, END = 150;
const SH = [
  [0, 6, shotCard, { txt: 'DIO', bg: RED, fg: BLK, size: 760, x: 70, y: 1330 }],
  [6, 9, shotLamp, { z: 1.25 }],
  [9, 15, shotCard, { txt: 'SALES', bg: BLK, fg: WHT, size: 600, x: 820, y: 2050, rot: -Math.PI / 2 }],
  [15, 18, shotSide, {}],
  [18, 24, shotCard, { txt: 'DAIHATSU', bg: WHT, fg: RED, size: 470, x: 330, y: -60, rot: Math.PI / 2 }],
  [24, 27, shotLamp, { z: 1.6, dx: -120 }],
  [27, 30, shotCard, { txt: 'GRAN', bg: RED, fg: WHT, size: 560, x: -40, y: 760 }],
  [30, 33, shotCard, { txt: 'MAX', bg: BLK, fg: RED, size: 700, x: 110, y: 1780 }],
  [33, 36, shotSlit, {}],
  [36, T_REV, shotRoad, {}],
  [T_REV, END, shotReveal, {}],
];
const DUR = END / FPS; window.DUR = DUR;
const FLIPS = [[6, 9], [T_REV, T_REV + 2], [120, 121]];      // red-black swaps (frames)

// sound events (mix.py reads events.json)
const EV = [];
const ev = (f, type, o = {}) => EV.push({ t: fs(f), type, ...o });
ev(0, 'sec', { name: 'flash' }); ev(T_RAIL, 'sec', { name: 'road' }); ev(T_SIL, 'sec', { name: 'silence' }); ev(T_REV, 'sec', { name: 'reveal' }); ev(END, 'sec', { name: 'end' });
ev(0, 'hit', { p: 1 }); ev(6, 'blip'); ev(9, 'hit', { p: 1.12 }); ev(15, 'cut'); ev(18, 'hit', { p: 1.26 }); ev(24, 'blip');
ev(27, 'hit', { p: 1.42 }); ev(30, 'hit', { p: 1.6 }); ev(33, 'slit'); ev(T_RAIL - 2, 'rush'); ev(T_RAIL, 'rail');
for (let k = 0; k < 4; k++) ev(T_RAIL + k * BEAT, 'step', { k });
ev(T_BAR, 'bar'); ev(T_SIL, 'tick'); ev(T_REV - 2, 'pre'); ev(T_REV, 'reveal'); ev(120, 'blip');
window.EV = EV.sort((a, b) => a.t - b.t);

// ───────── Helpers ─────────
const poly = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); };
const fl = lt => Math.floor(lt * FPS + 1e-6);
function jitter(t, amp, seed = 1) { const f = Math.round(t * FPS); return [Math.round((hash(f * 7.1 + seed) - .5) * 2 * amp), Math.round((hash(f * 3.3 + seed * 5) - .5) * 2 * amp)]; }
function sbox(g, x0, y0, x1, y1) {
  const m = g.getTransform(), P = [[x0, y0], [x1, y0], [x0, y1], [x1, y1]].map(([x, y]) => [m.a * x + m.c * y + m.e, m.b * x + m.d * y + m.f]);
  return { x0: Math.min(...P.map(p => p[0])), y0: Math.min(...P.map(p => p[1])), x1: Math.max(...P.map(p => p[0])), y1: Math.max(...P.map(p => p[1])) };
}
function text(g, s, x, y, font, col, id, align = 'left') {
  g.font = font; g.fillStyle = col; g.textAlign = align; g.textBaseline = 'alphabetic'; g.fillText(s, x, y);
  if (id) { const m = g.measureText(s); const x0 = align === 'left' ? x : align === 'right' ? x - m.width : x - m.width / 2; TXT.push({ id, text: s, ...sbox(g, x0, y - m.actualBoundingBoxAscent, x0 + m.width, y + m.actualBoundingBoxDescent) }); }
}
function img(name) { return IMG[name]; }
function drawImg(g, im, x, y, w, ax = .5, ay = 1) {
  const h = w * im.height / im.width; g.drawImage(im, x - w * ax, y - h * ay, w, h);
}
function silOf(im, col) { const c = mk(im.width, im.height), x = c.getContext('2d'); x.drawImage(im, 0, 0); x.globalCompositeOperation = 'source-in'; x.fillStyle = col; x.fillRect(0, 0, c.width, c.height); return c; }

// ───────── Flash card: solid field, one giant word (bleeds), slam + jitter. Not in the reading check: every word is also held in full ─────────
function shotCard(g, t, lt, o) {
  const f = fl(lt);
  g.fillStyle = o.bg; g.fillRect(0, 0, W, H);
  const sc = f === 0 ? 1.08 : f === 1 ? 1.02 : 1, [jx, jy] = jitter(t, f < 2 ? 13 : 2, o.size);
  g.save(); g.translate(o.x + jx, o.y + jy); if (o.rot) g.rotate(o.rot); g.scale(sc, sc);
  text(g, o.txt, 0, 0, `900 ${o.size}px ${SERIF}`, o.fg, null);
  g.restore();
}

// headlamp insert, frame-filling, slammed
function shotLamp(g, t, lt, o) {
  const im = img('lamp'), f = fl(lt), [jx, jy] = jitter(t, f < 2 ? 12 : 2, 9);
  g.fillStyle = BLK; g.fillRect(0, 0, W, H);
  const s = Math.max(W / im.width, H / im.height) * (o.z + lt * .4) * (f === 0 ? 1.05 : 1);
  g.drawImage(im, W / 2 + (o.dx || 0) + jx - im.width * s / 2, H / 2 + jy - im.height * s / 2, im.width * s, im.height * s);
}

// side silhouette, black on paper, pressed against the bottom edge; the top half is empty
function shotSide(g, t, lt) {
  g.fillStyle = WHT; g.fillRect(0, 0, W, H);
  const [jx, jy] = jitter(t, 6, 4);
  g.fillStyle = RED; g.fillRect(0, 1520, W, 14);
  drawImg(g, IMG.sideSil, 560 + jx, 1880 + jy, 1250, .5, 1);
}

// red slit opening on black (the transition; never a fully black frame)
function shotSlit(g, t, lt) {
  g.fillStyle = BLK; g.fillRect(0, 0, W, H);
  const k = eo((lt + fs(1)) / fs(3));
  g.fillStyle = RED; g.fillRect(W / 2 - 3, H / 2 - H / 2 * k, 6, H * k);
  g.fillRect(W / 2 - W / 2 * k, H / 2 - 3, W * k, 6);
}

// ───────── Dio's rail: full height, red, black type. Slams in from the left in 3 frames; reported only once complete ─────────
function rail(g, t, lt) {
  const k = eo(seg(lt, 0, fs(3))), x0 = -RAILW * (1 - k);
  g.fillStyle = RED; g.fillRect(x0, 0, RAILW, H);
  g.fillStyle = BLK; g.fillRect(x0 + RAILW - 10, 0, 10, H);
  const f = fl(lt), [jx, jy] = jitter(t + 3, f < 3 ? 9 : 1, 2), sc = f < 2 ? 1.05 : 1;
  g.save(); g.translate(x0 + jx, jy);
  g.save(); g.translate(RAILW / 2, 120); g.scale(sc, sc);
  // DIO stacked letter by letter (a vertical column)
  const size = 190;
  g.font = `900 ${size}px ${SERIF}`; g.fillStyle = BLK; g.textAlign = 'center'; g.textBaseline = 'alphabetic';
  [...'DIO'].forEach((ch, i) => g.fillText(ch, 0, size * .78 + i * size * .96));
  if (k >= 1) TXT.push({ id: 'dio', text: 'DIO', ...sbox(g, -size * .4, 0, size * .4, size * 2.9) });
  g.restore();
  // SALES DAIHATSU turned 90°, reading top to bottom
  g.save(); g.translate(RAILW / 2 - 28, 730); g.rotate(Math.PI / 2);
  text(g, 'SALES DAIHATSU', 0, 0, `900 70px ${SERIF}`, BLK, k >= 1 ? 'sales' : null);
  g.restore();
  g.restore();
}

// ───────── One-point road at night, symmetric in the panel; lamps scaled by depth; dashes rush toward us ─────────
const VPX = PX + PW / 2, VPY = 800;
function road(g, lt, z) {
  g.save(); g.beginPath(); g.rect(PX, 0, PW, H); g.clip();
  g.translate(VPX, VPY); g.scale(z, z); g.translate(-VPX, -VPY);
  g.fillStyle = BLK; g.fillRect(PX - 400, -400, PW + 800, H + 800);
  // road surface: a dark trapezoid from the vanishing point
  g.fillStyle = DK; poly(g, [[VPX - 8, VPY], [VPX + 8, VPY], [VPX + 1100, H + 300], [VPX - 1100, H + 300]]); g.fill();
  // kerb lines in paper white
  g.strokeStyle = WHT; g.lineWidth = 6;
  for (const s of [-1, 1]) { g.beginPath(); g.moveTo(VPX + s * 8, VPY); g.lineTo(VPX + s * 1100, H + 300); g.stroke(); }
  // centre dashes and lamps on a depth loop
  const sp = 2.4, ph = (lt * sp) % 1;
  for (let i = 14; i >= 0; i--) {
    const zz = i + 1 - ph; if (zz <= .15) continue;
    const k = 1 / (zz * .35 + .05), k2 = 1 / ((zz + .45) * .35 + .05);
    const y = VPY + 52 * k, y2 = VPY + 52 * k2;
    g.fillStyle = WHT; poly(g, [[VPX - 2.2 * k, y], [VPX + 2.2 * k, y], [VPX + 2.2 * k2, y2], [VPX - 2.2 * k2, y2]]); g.fill();
    if (i % 2 === 0) for (const s of [-1, 1]) {
      const lx = VPX + s * 70 * k, ly = VPY + 54 * k, hgt = 210 * k;
      g.fillStyle = INK; g.fillRect(lx - 2.2 * k, ly - hgt, 4.4 * k, hgt);
      g.fillStyle = RED; g.fillRect(lx - (s > 0 ? 14 : 2) * k, ly - hgt - 4 * k, 16 * k, 5 * k);
    }
  }
  g.restore();
}

// the approach: the car silhouette is redrawn larger once per beat, never tweened; the WA bar slams in on the last step
const STEPS = [[150, 960], [260, 1030], [430, 1150], [700, 1380]];   // [width, ground y] per beat
function shotRoad(g, t, lt) {
  const f = fl(lt), k = Math.min(3, Math.floor(f / BEAT));
  const z = 1 + lt * .05;
  road(g, lt, z);
  g.save(); g.beginPath(); g.rect(PX, 0, PW, H); g.clip();
  const [w, gy] = STEPS[k], fk = f - k * BEAT, [jx, jy] = jitter(t, fk < 2 ? 8 : 1, 6);
  const sc = fk === 0 ? 1.06 : 1;
  drawImg(g, IMG.frontWht, VPX + 20 + jx, gy + jy, w * sc, .5, 1);
  g.restore();
  rail(g, t, lt);
  if (t >= fs(T_BAR) - 1e-6) bar(g, t, t - fs(T_BAR));
}

// ───────── WA bar: black, full width, slams up from below; the number is held from 2.4 s to the end ─────────
function bar(g, t, lt) {
  const k = eo(seg(lt, 0, fs(3))), y0 = 1400 + (1 - k) * 600, f = fl(lt);
  const [jx, jy] = jitter(t + 7, f < 3 ? 8 : 1, 3);
  g.fillStyle = BLK; g.fillRect(0, y0, W, 250);
  g.fillStyle = RED; g.fillRect(0, y0, W * k, 10);
  g.save(); g.translate(jx, jy);
  text(g, 'WA', 64, y0 + 88, `900 56px ${SANS}`, RED, k >= 1 ? 'wa' : null);
  text(g, '0822-5699-6949', 60, y0 + 206, `900 116px ${SERIF}`, WHT, k >= 1 ? 'phone' : null);
  g.restore();
}

// ───────── Reveal: low angle, the car in colour on a red field above a black ground band ─────────
function shotReveal(g, t, lt) {
  const z = 1 + eio(seg(lt, 0, 2.2)) * .06;
  g.save(); g.beginPath(); g.rect(PX, 0, PW, H); g.clip();
  g.translate(VPX, 1180); g.scale(z, z); g.translate(-VPX, -1180);
  g.fillStyle = RED; g.fillRect(PX - 200, -200, PW + 400, H + 400);
  g.fillStyle = BLK; g.fillRect(PX - 200, 1120, PW + 400, 900);
  // light rails running along the ground
  for (let i = 0; i < 3; i++) {
    const u = ((lt * .9 + i / 3) % 1), x = lerp(PX - 300, W + 300, u);
    g.fillStyle = i === 1 ? RED : WHT; g.fillRect(x, 1150 + i * 26, 220, 6);
  }
  const f = fl(lt), [jx, jy] = jitter(t, f < 2 ? 10 : 0, 8);
  drawImg(g, IMG.front, VPX + 110 + jx, 1235 + jy, 880, .5, 1);
  g.restore();
  // GRAN MAX: a small vertical note at the top right
  g.save(); g.translate(W - 46, 70); g.rotate(Math.PI / 2);
  text(g, 'GRAN MAX', 0, 0, `900 54px ${SANS}`, BLK, 'granmax');
  g.restore();
  rail(g, t, 1);
  bar(g, t, 1);
}

// ───────── Red-black swap (never RGB inversion): grayscale → contrast → invert → multiply red ─────────
const TMP = mk(W, H), gt = TMP.getContext('2d');
function flipRB() {
  gt.globalCompositeOperation = 'source-over';
  gt.filter = 'grayscale(1) contrast(5) invert(1)'; gt.drawImage(S, 0, 0); gt.filter = 'none';
  gt.globalCompositeOperation = 'multiply'; gt.fillStyle = RED; gt.fillRect(0, 0, W, H); gt.globalCompositeOperation = 'source-over';
  g0.setTransform(1, 0, 0, 1, 0, 0); g0.drawImage(TMP, 0, 0);
}

function draw(t) {
  TXT.length = 0;
  const g = g0; g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.filter = 'none';
  const fn0 = Math.min(t * FPS, END - 1);
  const sh = SH.find(s => fn0 >= s[0] - 1e-6 && fn0 < s[1] - 1e-6) || SH[SH.length - 1];
  const [f0, , fn, o] = sh;
  g.save(); fn(g, t, t - fs(f0), o); g.restore();
  if (FLIPS.some(([a, b]) => fn0 >= a - 1e-6 && fn0 < b - 1e-6)) flipRB();
}
window.render = t => { draw(t); go.drawImage(S, 0, 0); };
window.TEXTS = t => { draw(t); return TXT.slice(); };

(async () => {
  await Promise.all([`900 300px ${SERIF}`, `900 50px ${SANS}`].map(f => document.fonts.load(f, 'DIOSALESDAIHATSUGRANMAXWA0123456789-')));
  Object.assign(IMG, buildCar());
  IMG.frontWht = silOf(IMG.front, WHT); IMG.sideSil = silOf(IMG.side, BLK);
  window.render(0);
  window.READY = true;
})();
