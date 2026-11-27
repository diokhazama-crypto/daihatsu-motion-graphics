// Duel di Depan Bank — Sci-Fi Sitcom Toon, vertical 1080×1920
import { clamp, lerp, seg, ss, eo, ei, eio, back, hash, TAU } from '/core/lib.js';
import { W, H, INK, init, frame, g, reset, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, rr, rect, spline, dot, text, S } from './toon.js';
import { sheriff, bandit, sales, rocky, tumbleweed, sheriffHead, banditHead, PAL } from './chars.js';
import { street, portal, dawn } from './world.js';
import { DUR, q, VO, SHOTS, shotAt, K, CUES, SILENCE } from './story.js';

init(document.getElementById('c'));
const J = async f => { try { const r = await fetch(f); if (r.ok) return await r.json(); } catch (e) { } return null; };
const LINES = await J('lines.json'), DURS = (await J('voices/dur.json')) || {}, LIPS = (await J('voices/lips.json')) || {};
const LINE = Object.fromEntries(LINES.map(l => [l.id, l]));
const vdur = id => DURS[id] ?? LINE[id].text.length * .07;

// —— lip sync (sampled at the 12 fps drawing time) ——
function talk(who, t) {
  const tq = q(t);
  for (const [id, t0] of Object.entries(VO)) {
    if (LINE[id].who !== who) continue;
    if (tq >= t0 && tq < t0 + vdur(id)) {
      const k = Math.floor((tq - t0) * 24), lp = LIPS[id];
      const o = lp ? (lp.o[k] ?? 0) : .5, b = lp ? (lp.b[k] ?? .5) : .5;
      return { o: o * (who === 'BANDIT' ? 1.2 : 1), w: .8 + .45 * b - .2 * o, talking: true };
    }
  }
  return { o: 0, w: 1, talking: false };
}
const blink = (t, seed) => { const k = Math.floor(t * 12), c = Math.floor(k / 30); return hash(c * 7.1 + seed) > .35 && (k % 30 === Math.floor(hash(c + seed) * 20) || k % 30 === Math.floor(hash(c + seed) * 20) + 1); };
const land = (t, t0, a = .24, d = .45) => { const u = (t - t0) / d; return u < 0 || u > 1 ? 1 : 1 - a * Math.cos(u * Math.PI * 2.5) * (1 - u); };
const popOpen = x => x <= 0 ? 0 : back(clamp(x / .32), 1.4);

// —— camera ——
let CAM = { cx: 0, cy: 0, z: 1 };
function cam(cx, cy, z, t = 0, shake = 0, rot = 0) {
  CAM = { cx, cy, z }; reset(); translate(W / 2, H / 2);
  if (shake) { const f = Math.floor(t * 24); translate((hash(f) - .5) * shake * 2, (hash(f + 77) - .5) * shake * 2); }
  scale(z); if (rot) rotate(rot); translate(-cx, -cy);
}
const toScreen = (x, y) => [(x - CAM.cx) * CAM.z + W / 2, (y - CAM.cy) * CAM.z + H / 2];
function whipLines(u) {   // speed lines during a whip pan (screen space)
  if (u <= .05 || u >= .95) return;
  const a = Math.sin(u * Math.PI);
  reset();
  for (let i = 0; i < 16; i++) { const y = hash(i * 3.3) * H, x = hash(i * 7.7) * W * .6; stroke([[x, y], [x + 300 + hash(i) * 400, y]], 6 + hash(i * 2) * 10, { line: `rgba(255,255,255,${.35 * a})`, boil: .3 }); }
}

// —— where everyone is (street world), as a function of time ——
const SX = { band: -300, sher: 300 };
function salesPos(t) {
  if (t < 11.6) return null;
  if (t < K.land) { const u = seg(t, 11.6, K.land); return { x: 0, y: lerp(-180, 120, ei(u)) - Math.sin(u * Math.PI) * 60, s: lerp(.55, 1, eo(u)), sq: lerp(1.35, 1.1, u), fly: 1 }; }
  if (t < 20.6) return { x: 0, y: 120, sq: land(t, K.land) };
  if (t < K.hop) return { x: 380, y: 300, sq: 1 };
  return null;
}
function carPos(t) {
  if (t < K.snap + .1) return null;
  if (t < K.carLand) { const u = seg(t, K.snap + .1, K.carLand); return { x: 0, y: lerp(-430, 300, ei(u)), s: lerp(.25, 1, eo(u)), sq: lerp(1.25, 1, u) }; }
  if (t < K.carHop) return { x: 0, y: 300, s: 1, sq: land(t, K.carLand, .22, .5) * (t > K.engine && t < K.engine + .5 ? 1 + .02 * Math.sin(t * 60) : 1) };
  if (t < K.suck0) { const u = seg(t, K.carHop, K.suck0); return { x: 0, y: 300 - Math.sin(u * Math.PI) * 60, s: 1, sq: 1 + Math.sin(u * Math.PI) * .06 }; }
  if (t < K.suck1) { const u = ei(seg(t, K.suck0, K.suck1)); return { x: 0, y: lerp(300, -430, u), s: lerp(1, .05, u), sq: lerp(1, 1.5, u), sx: lerp(1, .6, u) }; }
  return null;
}
function portalOpen(t) {
  if (t < K.boom) return 0;
  if (t < K.close0) return popOpen(t - K.boom);
  return 1 - back(seg(t, K.close0, K.close1), 1.6) * 1;
}

// acting
function sheriffP(t, shot) {
  const tk = talk('SHERIFF', t), tq = q(t);
  const P = { x: SX.sher, face: -1, lid: .5, look: [.2, 0], mouth: { o: tk.o, w: tk.w, sm: -.2 }, blink: blink(t, 3), straw: Math.sin(tq * 3) * .08, armR: { h: [40, 118], bend: 14 }, armL: { h: [-22, 148], bend: -10 } };
  if (t < 6.6) P.straw = tk.talking ? Math.sin(tq * 9) * .12 : Math.sin(tq * 2.2) * .1;
  if (t >= 6.6 && t < 9.6) { P.armR.h = [40 + (hash(Math.floor(t * 12)) - .5) * 6, 118 + (hash(Math.floor(t * 12) + 5) - .5) * 4]; P.lid = .58; }
  if (t >= K.boom && t < 11.6) { P.lid = 0; P.look = [0, -.2]; P.straw = .6; P.sq = land(t, K.boom + .05, .12, .4); P.brow = 1; }
  if (t >= 11.6 && t < 20.6) { P.lid = .25; P.look = [-.6, .1]; P.straw = -.2; }
  if (t >= 20.6 && t < 30.6) { P.lid = .4; P.look = [-.8, 0]; }
  if (t >= K.carLand && t < K.carLand + 1.2) { P.lid = .05; P.straw = .5; }
  if (t >= 32.6 && t < 37.1) {
    const toS = t >= K.toSales;
    P.look = toS ? [-1, 0] : [.9, 0]; P.lid = toS ? .4 : .62; P.browIn = toS ? 0 : 1; P.straw = toS ? Math.sin(tq * 6) * .2 : 0;
  }
  if (t >= 37.1) { P.look = [.9, 0]; P.lid = .5; P.straw = t > K.nod ? -.3 : 0; if (t > K.relax) P.armR = { h: [20, 150], bend: 8 }; if (t > K.nod && t < K.nod + .4) P.headTilt = Math.sin(seg(t, K.nod, K.nod + .4) * Math.PI) * .12; }
  return P;
}
function banditP(t, shot) {
  const tk = talk('BANDIT', t), tq = q(t);
  const P = { x: SX.band, face: 1, t, nerv: .55, grin: tk.talking ? 0 : 1, look: [.3, 0], mouth: { o: tk.o, w: tk.w }, sweat: t * .7, blink: blink(t, 11), armR: { h: [36, 120], bend: 12 }, armL: { h: [-24, 140], bend: -12 } };
  if (t >= 6.6 && t < 9.6) { P.nerv = .9; P.armR.h = [36 + (hash(Math.floor(t * 12) + 2) - .5) * 10, 120]; }
  if (t >= K.boom && t < 11.6) { P.eyeS = 1.25; P.pupil = 2.4; P.brow = 1.5; P.grin = 0; P.mouth = { o: .7, w: .7 }; P.look = [.2, -.3]; const u = seg(t, K.boom, K.boom + .45); P.bob = -Math.sin(u * Math.PI) * 70; P.sq = land(t, K.boom + .45, .2, .4); }
  if (t >= 11.6 && t < 15.6) { P.look = [1, .1]; P.eyeS = 1.12; P.nerv = .7; }
  if (t >= 15.6 && t < 16.6) { P.eyeS = 1.25; P.pupil = 2.4; P.brow = 1.6; P.look = [.6, 0]; P.nerv = 1.2; }
  if (t >= K.carLand && t < 30.6) { P.eyeS = 1.15; P.look = [1, .3]; P.grin = tk.talking ? 0 : 1; }
  if (t >= 30.6 && t < 32.6) { P.look = t < 31.6 ? [-.7, -.7] : [.8, -.2]; P.brow = -.4; P.nerv = .3; P.grin = tk.talking ? 0 : 1; }
  if (t >= 32.6 && t < 37.1) { P.look = [.8, 0]; P.brow = 1.2; }
  if (t >= 37.1) { P.look = [1, 0]; P.nerv = .25; P.brow = .6; if (t > K.nod) { P.grin = 1; P.brow = -.3; } if (t > K.relax) P.armR = { h: [10, 150], bend: 6 }; }
  return P;
}
function salesP(t) {
  const p = salesPos(t); if (!p) return null;
  const tk = talk('SALES', t), tq = q(t);
  const P = { x: p.x, y: p.y, s: p.s ?? 1, sq: p.sq, face: 1, turn: .15, mouth: { o: tk.o, w: tk.w, sm: .7 }, blink: blink(t, 23), look: [0, .05], armR: { h: [24, 146], bend: 12 }, armL: { h: [-16, 146], bend: -10 } };
  if (p.fly) { P.armR = { h: [60, -120], bend: -10 }; P.armL = { h: [-70, -110], bend: 10 }; P.legL = [-10, -30]; P.legR = [20, -10]; P.shadow = false; }
  if (t >= K.land && t < 15.6) { const u = seg(t, K.thumb - .2, K.thumb); P.armR = { h: [lerp(24, 70, u), lerp(146, -40, u)], bend: lerp(12, -30, u), end: u > .5 ? 'thumb' : 'hand' }; if (t < K.thumb) P.happy = t > K.land + .1; P.look = [-.4, 0]; }
  if (t >= 16.6 && t < 20.6) { P.turn = .1; const u = seg(t, K.card - .25, K.card); P.armR = { h: [lerp(24, -30, u), lerp(146, 110, u)], bend: lerp(12, 30, u), fist: u > .5 }; P.armL = { h: [-30, 150], bend: -14 }; }
  if (t >= 20.6 && t < 25.6) {
    P.face = -1; P.turn = .5; P.look = [.6, -.3];
    const u = seg(t, K.snap - .3, K.snap);
    P.armR = { h: [lerp(40, 70, u), lerp(120, -150, u)], bend: lerp(10, -20, u), fist: u > .5 };
    if (t > K.carLand) { P.happy = true; P.armR = { h: [80, -40], bend: -30, end: 'thumb' }; }
  }
  if (t >= 25.6 && t < 35.6) { P.face = -1; P.turn = .45; P.look = [.7, .1]; P.armR = { h: [120, 40], bend: -20 }; if (t > K.irit) P.armL = { h: [70, -60], bend: -30, end: 'thumb' }; }
  if (t >= 30.6 && t < 35.6 && t > 32) P.look = [-.4, 0];
  if (t >= 35.6) { P.face = -1; P.turn = .3; P.happy = t > K.thumb2 + .1 && t < 37.1; P.armR = { h: [50, -60], bend: -30, end: 'thumb' }; P.armL = { h: [-16, 146], bend: -10 }; P.look = [-.6, 0]; }
  return P;
}

// —— the street world with actors ——
function drawStreet(t, shot, { noSales = false } = {}) {
  street(t);
  const tq = q(t), sP = noSales ? null : salesP(t), car = carPos(t), po = portalOpen(t);
  // tumbleweed behind actors in the opening; in front at the end
  if (t < 3) tumbleweed(lerp(-800, 900, seg(t, 0, 3)), 60 - Math.abs(Math.sin(t * 5)) * 50, 56, t * 5);
  portal(0, -430, 210, t, { open: po });
  // hop into the car: actors arc toward the car and vanish
  const hopU = seg(t, K.hop, K.riders);
  const hopTo = (P, x0, y0) => { if (t < K.hop) return P; if (t >= K.riders) return null; const u = eio(hopU); P.x = lerp(x0, 0, u); P.y = lerp(y0, 200, u) - Math.sin(u * Math.PI) * 260; P.s = lerp(1, .45, u); P.shadow = false; P.legL = [-10, -30]; P.legR = [10, -24]; return P; };
  const bP = hopTo(banditP(t, shot), SX.band, 0), shP = hopTo(sheriffP(t, shot), SX.sher, 0);
  let sp = sP; if (!sp && t >= K.hop && t < K.riders) { sp = salesP(K.hop - .01); sp = hopTo(sp, 380, 300); }
  const actors = [];
  if (bP) actors.push([bP.y || 0, () => bandit(bP)]);
  if (shP) actors.push([shP.y || 0, () => sheriff(shP)]);
  if (sp) actors.push([sp.y || 0, () => sales(sp)]);
  if (car) actors.push([299, () => rocky({ x: car.x, y: car.y, s: car.s, sq: car.sq, sx: car.sx, riders: t >= K.riders, wheelRot: t > K.carHop ? t * 18 : 0, hatBounce: Math.sin(t * 20) * .05, shadow: car.s > .8 })]);
  actors.sort((a, b) => a[0] - b[0]).forEach(a => a[1]());
  // puffs where people pop into the car
  if (t >= K.riders - .05 && t < K.riders + .35) { const u = seg(t, K.riders - .05, K.riders + .35); for (let i = 0; i < 7; i++) { const a = i / 7 * TAU; fillOnly(ell(-60 + Math.cos(a) * 180 * u, 120 + Math.sin(a) * 60 * u, 40 * (1 - u) + 6, 30 * (1 - u) + 6, 14), '#e9e6ff', { boil: .5 }); } }
  // landing dust for the car
  if (t >= K.carLand && t < K.carLand + .5) { const u = seg(t, K.carLand, K.carLand + .5); for (let i = 0; i < 8; i++) { const sx = i < 4 ? -1 : 1, k = i % 4; shape(ell(sx * (300 + u * 160 + k * 40), 290 - k * 18 - u * 30, 40 * (1 - u) + 10, 26 * (1 - u) + 6, 14), { fill: '#8f8fc8', lw: 5, alpha: 1 - u }); } }
  if (t >= K.weed0 && t < K.weed1) tumbleweed(lerp(-700, 700, seg(t, K.weed0, K.weed1)), 200 - Math.abs(Math.sin(t * 5)) * 50, 60, t * 5);
}

// —— shots ——
function shot(t) {
  const sh = shotAt(t), u = (t - sh.t0) / (sh.t1 - sh.t0);
  switch (sh.id) {
    case 'wide1': cam(0, -430, lerp(.95, 1.02, ss(u))); return drawStreet(t, sh);
    case 'cuSher': cam(300, -450, lerp(2.6, 2.7, u)); return drawStreet(t, sh);
    case 'cuBand': cam(-300, -440, lerp(2.6, 2.75, u), t, talk('BANDIT', t).talking && t > 5.5 && t < 6.1 ? 10 : 0); return drawStreet(t, sh);
    case 'hands': {
      const w = seg(t, K.whip1, K.whip1 + .22), e = eio(w);
      cam(lerp(-216, 214, e), lerp(-215, -222, e), 4.6); drawStreet(t, sh); whipLines(w); return;
    }
    case 'eyes': {
      const w = seg(t, K.whip2, K.whip2 + .2), e = eio(w);
      cam(lerp(-292, 250, e), lerp(-458, -494, e), 5.6); drawStreet(t, sh); whipLines(w); return;
    }
    case 'portal': cam(0, -400, .95, t, t < K.boom + .35 ? 26 * (1 - seg(t, K.boom, K.boom + .35)) : 0); return drawStreet(t, sh);
    case 'arrive': cam(0, lerp(-300, -240, ss(seg(t, 11.6, 12.2))), 1.25); return drawStreet(t, sh);
    case 'cuBand2': cam(-300, -440, 2.8, t, t > K.shake2 && t < K.shake2 + .3 ? 16 : 0); return drawStreet(t, sh);
    case 'cuSales': cam(0, -170, lerp(2.1, 2.3, ss(u))); return drawStreet(t, sh);
    case 'snap': { const f = seg(t, K.snap, K.carLand + .2); cam(lerp(40, 60, f), lerp(-330, -120, eio(f)), lerp(1.05, .98, f), t, t > K.carLand && t < K.carLand + .3 ? 22 : 0); return drawStreet(t, sh); }
    case 'rocky': cam(lerp(80, 100, u), lerp(-20, -40, u), lerp(1.12, 1.18, u)); return drawStreet(t, sh);
    case 'cuBand3': cam(-300, -440, 2.7); return drawStreet(t, sh);
    case 'cuSher2': cam(300, -450, lerp(2.6, 2.75, u)); return drawStreet(t, sh, { noSales: true });
    case 'cuSales2': cam(380, -120, 2.35, t, 0); return drawStreet(t, sh);
    case 'pause': cam(0, -320, lerp(.98, 1.08, ss(u))); return drawStreet(t, sh);
    case 'leave': cam(0, lerp(-260, -320, ss(u)), lerp(.98, .86, ss(seg(t, K.carHop, K.close1)))); return drawStreet(t, sh);
    case 'end': return endCard(t);
  }
}

// —— end card: dawn, 2026 ——
function endCard(t) {
  cam(0, -200, 1);
  dawn(t);
  const c = land(t, 44.6, .1, .5);
  rocky({ x: 170, y: 80, s: .95, sq: c, riders: 'cowboys', hatBounce: Math.sin(t * 6) * .04 });
  const tk = talk('SALES', t), u = seg(t, 46.4, 46.7);
  sales({ x: -250, y: 760, s: 1.55, face: 1, turn: .15, mouth: { o: tk.o, w: tk.w, sm: .8 }, blink: blink(t, 29), look: [0, .05], happy: !tk.talking && t > 49.6,
    armR: { h: [lerp(24, 70, u), lerp(146, -40, u)], bend: lerp(12, -30, u), end: u > .5 ? 'thumb' : 'hand' }, armL: { h: [-16, 146], bend: -10 } });
  // title
  const a = seg(q(t), K.title, K.title + .3), s = a < 1 ? back(a, 2.2) : 1;
  reset(); translate(W / 2, 330); rotate(-.04); scale(s);
  text('DAIHATSU', 8, 8, { font: '400 112px Rye', fill: PAL.car, outlineW: 20, outlineCol: INK });
  text('DAIHATSU', 0, 0, { font: '400 112px Rye', fill: '#fff3d6', outlineW: 20, outlineCol: INK });
  text('ROCKY', 10, 150, { font: '400 168px Rye', fill: PAL.car, outlineW: 24, outlineCol: INK });
  text('ROCKY', 0, 140, { font: '400 168px Rye', fill: '#fff3d6', outlineW: 24, outlineCol: INK });
  for (let i = 0; i < 4; i++) {
    const x = [-430, 420, -380, 390][i], y = [-40, -30, 190, 200][i], r = 18 + 9 * Math.sin(q(t) * 5 + i * 1.7);
    shape([[x, y - r], [x + r * .28, y - r * .28], [x + r, y], [x + r * .28, y + r * .28], [x, y + r], [x - r * .28, y + r * .28], [x - r, y], [x - r * .28, y - r * .28]], { fill: '#ffe066', lw: 5 });
  }
}

// —— world tag (VT323, typed in) ——
const TAGS = [{ id: 'tag1', t0: .2, t1: 4.2, s: 'WILD WEST · 1887' }, { id: 'tag2', t0: 45.0, t1: 50.4, s: 'INDONESIA · 2026' }];
function tags(t) {
  for (const T of TAGS) {
    if (t < T.t0 || t >= T.t1) continue;
    const n = Math.min(T.s.length, Math.floor((t - T.t0) * 24)), str = T.s.slice(0, n) + (Math.floor(t * 4) % 2 ? '_' : ' ');
    reset(); g.font = '400 54px VT323'; const w = g.measureText(T.s + '_').width + 44;
    shape(rr(36, 150, w, 70, 12), { fill: 'rgba(12,14,40,.82)', lw: 5 });
    text(str, 58, 187, { font: '400 54px VT323', fill: '#ffd27a', align: 'left' });
  }
}

// —— subtitles: Baloo 2 ExtraBold, white, thick black outline, speaker pill ——
const WHO_COL = { SHERIFF: '#a8743a', BANDIT: '#d0342c', SALES: '#1f3c8f' };
const CLIPS = [6.6, 37.1, 44.6, 50.4];
export const SUBS = Object.entries(VO).map(([id, t0]) => {
  const L = LINE[id], text_ = L.sub || L.text, d = vdur(id);
  let t1 = t0 + Math.max(d + .5, .9 + text_.length / 17, 1.8);
  const cut = CLIPS.find(c => c > t0 + .1); if (cut && t1 > cut) t1 = Math.max(cut - .02, t0 + d + .2);
  return { id, t0, t1, who: L.who, text: text_ };
});
const FS = 58;
function wrapSub(str) {
  g.setTransform(1, 0, 0, 1, 0, 0); g.font = `800 ${FS}px "Baloo 2"`;
  if (g.measureText(str).width < 700) return [str];
  const mid = str.length / 2; let best = -1;
  for (let i = 0; i < str.length; i++) if (str[i] === ' ' && (best < 0 || Math.abs(i - mid) < Math.abs(best - mid))) best = i;
  return [str.slice(0, best), str.slice(best + 1)];
}
function subs(t) {
  const act = SUBS.filter(s => t >= s.t0 && t < s.t1).slice(-2);
  let y = H - 300;
  for (let i = act.length - 1; i >= 0; i--) {
    const s = act[i], a = i === act.length - 1 ? 1 : .7, lines = wrapSub(s.text);
    const pp = back(seg(t, s.t0, s.t0 + .12), 2);
    g.setTransform(1, 0, 0, 1, 0, 0); g.font = `800 ${FS}px "Baloo 2"`;
    const tw = Math.max(...lines.map(l => g.measureText(l).width)); g.font = '800 28px "Baloo 2"'; const nw = g.measureText(s.who).width + 36;
    const y0 = y - (lines.length - 1) * 72;
    reset(); g.globalAlpha = a;
    push(); translate(W / 2, y0 - 70); scale(pp); translate(-nw / 2, 0);
    shape(rr(0, -24, nw, 48, 16), { fill: WHO_COL[s.who], lw: 5 });
    text(s.who, nw / 2, 2, { font: '800 28px "Baloo 2"', fill: '#fff' });
    pop();
    lines.forEach((l, k) => text(l, W / 2, y0 + k * 72, { font: `800 ${FS}px "Baloo 2"`, fill: '#fff', outlineW: 12 }));
    g.globalAlpha = 1;
    y = y0 - 170;
  }
}

function render(t) {
  frame(t);
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = '#0b1033'; g.fillRect(0, 0, W, H);
  shot(t);
  tags(t);
  subs(t);
}

// —— events for the mixer and the score ——
function events() {
  const E = [];
  for (const [id, t0] of Object.entries(VO)) E.push({ t: t0, type: 'vo', id, who: LINE[id].who });
  const fx = (t, name, x = {}) => E.push({ t, type: 'sfx', name, ...x });
  for (const [id, t0, t1, bpm] of CUES) E.push({ t: t0, type: 'cue', id, end: t1, bpm });
  for (const [a, b] of SILENCE) E.push({ t: a, type: 'silence', end: b });
  for (const [id, t0] of SHOTS) E.push({ t: t0, type: 'cut', id });
  fx(.0, 'weed', { dur: 3 });
  for (let k = 0; k < 5; k++) fx(6.6 + k * .6, 'tick');
  fx(7.0, 'gulp'); fx(K.whip1, 'whip'); fx(K.whip2, 'whip'); fx(8.3, 'twitch');
  fx(K.boom, 'boom'); fx(K.boom, 'portalHum', { end: K.close1 });
  fx(11.6, 'whoosh'); fx(K.land, 'land'); fx(K.thumb, 'ding');
  fx(K.shake2, 'boing'); fx(K.card, 'click');
  fx(K.snap, 'snap'); fx(K.snap + .1, 'fall'); fx(K.carLand, 'carLand'); fx(K.honk, 'honk');
  fx(K.irit, 'ding'); fx(31.6, 'gulp'); fx(K.toSales, 'blip'); fx(K.thumb2, 'ding');
  fx(38.2, 'gulp'); fx(K.nod, 'nod'); fx(K.relax, 'leather');
  fx(K.engine, 'engine'); fx(K.hop, 'hop'); fx(K.riders, 'pop'); fx(K.riders + .1, 'door'); fx(K.carHop, 'boing'); fx(K.suck0, 'suck'); fx(K.close0, 'close');
  fx(K.weed0, 'weed', { dur: 1.6 }); fx(K.title, 'title'); fx(K.stinger, 'stinger');
  return E.sort((a, b) => a.t - b.t);
}
// texts for readcheck (subtitles are checked through the .srt)
function TEXTS(t) {
  const out = [];
  for (const T of TAGS) if (t >= T.t0 + T.s.length / 24 && t < T.t1) out.push({ id: T.id, text: T.s, x0: 36, y0: 150, x1: 560, y1: 220 });
  if (t >= K.title + .3) out.push({ id: 'title', text: 'DAIHATSU ROCKY', x0: 80, y0: 200, x1: 1000, y1: 560 });
  return out;
}

await document.fonts.load(`800 ${FS}px "Baloo 2"`); await document.fonts.load('40px Rye'); await document.fonts.load('40px VT323');
window.render = render; window.DUR = DUR; window.EV = events(); window.TEXTS = TEXTS; window.SUBS = SUBS;
window.READY = true;
