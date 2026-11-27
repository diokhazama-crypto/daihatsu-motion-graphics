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

// —— where everyone is (street world, real scale: people 600 units tall, 1 m ≈ 350 units) ——
const SX = { band: -430, sher: 430 }, PC = [0, -480], PR = 380, CAR = { x: 0, y: 420, s: 2.2 }, SALES2 = [820, 430];
function salesPos(t) {
  if (t < 11.6) return null;
  if (t < K.land) { const u = seg(t, 11.6, K.land); return { x: 0, y: lerp(-260, 150, ei(u)) - Math.sin(u * Math.PI) * 80, s: lerp(.45, 1, eo(u)), sq: lerp(1.2, 1.05, u), fly: 1 }; }
  if (t < 20.6) return { x: 0, y: 150, sq: land(t, K.land, .1) };
  if (t < K.hop) return { x: SALES2[0], y: SALES2[1], sq: 1 };
  return null;
}
function carPos(t) {
  if (t < K.snap + .1) return null;
  if (t < K.carLand) { const u = seg(t, K.snap + .1, K.carLand); return { x: 0, y: lerp(PC[1] + 100, CAR.y, ei(u)), s: CAR.s * lerp(.25, 1, eo(u)), sq: lerp(1.15, 1, u) }; }
  if (t < K.carHop) return { x: 0, y: CAR.y, s: CAR.s, sq: land(t, K.carLand, .1, .5) * (t > K.engine && t < K.engine + .5 ? 1 + .012 * Math.sin(t * 60) : 1) };
  if (t < K.suck0) { const u = seg(t, K.carHop, K.suck0); return { x: 0, y: CAR.y - Math.sin(u * Math.PI) * 80, s: CAR.s, sq: 1 + Math.sin(u * Math.PI) * .04 }; }
  if (t < K.suck1) { const u = ei(seg(t, K.suck0, K.suck1)); return { x: 0, y: lerp(CAR.y, PC[1] + 120, u), s: CAR.s * lerp(1, .04, u), sq: lerp(1, 1.5, u), sx: lerp(1, .6, u) }; }
  return null;
}
function portalOpen(t) {
  if (t < K.boom) return 0;
  if (t < K.close0) return popOpen(t - K.boom);
  return 1 - back(seg(t, K.close0, K.close1), 1.6);
}
const jitterH = (t, k, a) => (hash(Math.floor(t * 12) + k) - .5) * a;
const HOVER = [22, 176];   // the gun hand hovering above the holster

// acting (arm targets h are hand offsets from the shoulder, reach ≈ 200)
function sheriffP(t) {
  const tk = talk('SHERIFF', t), tq = q(t);
  const P = { x: SX.sher, face: -1, lid: .45, look: [.3, 0], mouth: { o: tk.o, w: tk.w, sm: -.1 }, blink: blink(t, 3), straw: Math.sin(tq * 2.2) * .1, armR: { h: HOVER.slice() }, armL: { h: [-12, 190] } };
  if (t < 6.6 && tk.talking) P.straw = Math.sin(tq * 9) * .12;
  if (t >= 6.6 && t < 9.6) { P.armR.h = [HOVER[0] + jitterH(t, 0, 6), HOVER[1] + jitterH(t, 5, 4)]; P.lid = .55; P.browIn = .6; }
  if (t >= K.boom && t < 11.6) { P.lid = 0; P.eyeS = 1.3; P.look = [0, -.2]; P.straw = .6; P.sq = land(t, K.boom + .05, .06, .4); P.brow = 1; }
  if (t >= 11.6 && t < 20.6) { P.lid = .25; P.look = [-.5, .1]; P.straw = -.2; }
  if (t >= 20.6 && t < 30.6) { P.lid = .4; P.look = [-.8, .2]; }
  if (t >= K.carLand && t < K.carLand + 1.2) { P.lid = 0; P.eyeS = 1.2; P.straw = .5; }
  if (t >= 32.6 && t < 37.1) { const toS = t >= K.toSales; P.look = toS ? [-1, 0] : [.9, 0]; P.lid = toS ? .4 : .6; P.browIn = toS ? 0 : 1; P.straw = toS ? Math.sin(tq * 6) * .2 : 0; P.turn = .4; }
  if (t >= 37.1) { P.look = [.9, 0]; P.lid = .5; if (t > K.nod) { P.straw = -.3; P.mouth.sm = .5; } if (t > K.relax) P.armR = { h: [8, 192] }; if (t > K.nod && t < K.nod + .4) P.headTilt = Math.sin(seg(t, K.nod, K.nod + .4) * Math.PI) * .1; }
  return P;
}
function banditP(t) {
  const tk = talk('BANDIT', t);
  const P = { x: SX.band, face: 1, t, nerv: .5, grin: !tk.talking, look: [.4, 0], mouth: { o: tk.o, w: tk.w }, sweat: t * .7, blink: blink(t, 11), armR: { h: HOVER.slice() }, armL: { h: [-12, 188] }, brow: .6 };
  if (t >= 6.6 && t < 9.6) { P.nerv = .9; P.armR.h = [HOVER[0] + jitterH(t, 2, 10), HOVER[1]]; }
  if (t >= K.boom && t < 11.6) { P.eyeS = 1.45; P.pupil = 1; P.brow = 1.5; P.grin = false; P.mouth = { o: .7, w: .7 }; P.look = [.2, -.3]; const u = seg(t, K.boom, K.boom + .45); P.bob = -Math.sin(u * Math.PI) * 60; P.sq = land(t, K.boom + .45, .08, .4); P.armL = { h: [-90, -60] }; }
  if (t >= 11.6 && t < 15.6) { P.look = [1, .1]; P.eyeS = 1.2; P.nerv = .7; }
  if (t >= 15.6 && t < 16.6) { P.eyeS = 1.45; P.pupil = 1; P.brow = 1.6; P.look = [.6, 0]; P.nerv = 1.2; }
  if (t >= K.carLand && t < 30.6) { P.eyeS = 1.2; P.look = [1, .3]; }
  if (t >= 30.6 && t < 32.6) { P.look = t < 31.6 ? [-.7, -.5] : [.8, -.2]; P.brow = -.4; P.nerv = .3; P.armL = { h: [70, 120] }; P.armR = { h: [-20, 120], fist: true }; }
  if (t >= 32.6 && t < 37.1) { P.look = [.8, 0]; P.brow = 1.2; }
  if (t >= 37.1) { P.look = [1, 0]; P.nerv = .25; P.brow = .6; if (t > K.nod) { P.grin = true; P.brow = -.3; } if (t > K.relax) P.armR = { h: [8, 190] }; }
  return P;
}
function salesP(t) {
  const p = salesPos(t); if (!p) return null;
  const tk = talk('SALES', t);
  const P = { x: p.x, y: p.y, s: p.s ?? 1, sq: p.sq, face: 1, turn: .2, mouth: { o: tk.o, w: tk.w, sm: .6 }, blink: blink(t, 23), look: [0, .05], armR: { h: [10, 192] }, armL: { h: [-10, 192] } };
  if (p.fly) { P.armR = { h: [60, -170] }; P.armL = { h: [-60, -170] }; P.legL = [-10, -60]; P.legR = [24, -24]; P.shadow = false; }
  if (t >= K.land && t < 15.6) { const u = seg(t, K.thumb - .2, K.thumb); P.armR = { h: [lerp(10, 34, u), lerp(192, 92, u)], end: u > .5 ? 'thumb' : 'open', bend: u > .5 ? -1 : 1 }; P.happy = t > K.land + .1 && t < K.thumb + .3; P.look = [-.3, 0]; }
  if (t >= 16.6 && t < 20.6) { P.turn = .1; const u = seg(t, K.card - .25, K.card); P.armR = { h: [lerp(10, -54, u), lerp(192, 96, u)], fist: u > .5 }; }
  if (t >= 20.6 && t < 25.6) {
    P.face = -1; P.turn = .5; P.look = [.6, -.4];
    const u = seg(t, K.snap - .3, K.snap);
    P.armR = { h: [lerp(10, 80, u), lerp(192, -110, u)], fist: u > .5 };
    if (t > K.carLand) { P.happy = true; P.armR = { h: [34, 92], end: 'thumb', bend: -1 }; }
  }
  if (t >= 25.6 && t < 35.6) { P.face = -1; P.turn = .45; P.look = [.7, .1]; P.armR = { h: [170, 70] }; if (t > K.irit) P.armL = { h: [30, 92], end: 'thumb' }; }
  if (t >= 32 && t < 35.6) P.look = [-.4, 0];
  if (t >= 35.6) { P.face = -1; P.turn = .3; P.happy = t > K.thumb2 + .1 && t < 37.1; P.armR = { h: [34, 92], end: 'thumb', bend: -1 }; P.armL = { h: [-10, 192] }; P.look = [-.5, 0]; }
  return P;
}

// —— the street world with actors ——
function drawStreet(t, shot, { noSales = false } = {}) {
  street(t);
  const sP = noSales ? null : salesP(t), car = carPos(t), po = portalOpen(t);
  if (t < 3) tumbleweed(lerp(-1300, 1300, seg(t, 0, 3)), 160 - Math.abs(Math.sin(t * 4)) * 70, 90, t * 4);
  portal(PC[0], PC[1], PR, t, { open: po });
  const win = [CAR.x, CAR.y - 150 * CAR.s];
  const hopTo = (P, x0, y0) => { if (!P || t < K.hop) return P; if (t >= K.riders) return null; const u = eio(seg(t, K.hop, K.riders)); P.x = lerp(x0, win[0], u); P.y = lerp(y0, win[1], u) - Math.sin(u * Math.PI) * 320; P.s = lerp(1, .3, u); P.shadow = false; P.legL = [-10, -60]; P.legR = [20, -40]; return P; };
  const bP = hopTo(banditP(t), SX.band, 0), shP = hopTo(sheriffP(t), SX.sher, 0);
  let sp = sP; if (!noSales && !sp && t >= K.hop && t < K.riders) sp = hopTo(salesP(K.hop - .01), SALES2[0], SALES2[1]);
  const actors = [];
  if (bP) actors.push([bP.y || 0, () => bandit(bP)]);
  if (shP) actors.push([shP.y || 0, () => sheriff(shP)]);
  if (sp) actors.push([sp.y || 0, () => sales(sp)]);
  if (car) actors.push([CAR.y - 1, () => rocky({ x: car.x, y: car.y, s: car.s, sq: car.sq, sx: car.sx, riders: t >= K.riders, wheelRot: t > K.carHop ? t * 18 : 0, hatBounce: Math.sin(t * 20) * .05, shadow: car.s > CAR.s * .8 })]);
  actors.sort((a, b) => a[0] - b[0]).forEach(a => a[1]());
  if (t >= K.riders - .05 && t < K.riders + .35) { const u = seg(t, K.riders - .05, K.riders + .35); for (let i = 0; i < 8; i++) { const a = i / 8 * TAU; fillOnly(ell(win[0] + Math.cos(a) * 380 * u, win[1] + Math.sin(a) * 120 * u, 70 * (1 - u) + 10, 50 * (1 - u) + 8, 14), '#e9e6ff', { boil: .5 }); } }
  if (t >= K.carLand && t < K.carLand + .5) { const u = seg(t, K.carLand, K.carLand + .5); for (let i = 0; i < 8; i++) { const sx = i < 4 ? -1 : 1, k = i % 4; shape(ell(sx * (680 + u * 260 + k * 70), CAR.y - 10 - k * 30 - u * 40, 70 * (1 - u) + 16, 44 * (1 - u) + 10, 14), { fill: '#8f8fc8', lw: 4, alpha: 1 - u }); } }
  if (t >= K.weed0 && t < K.weed1) tumbleweed(lerp(-1200, 1200, seg(t, K.weed0, K.weed1)), 260 - Math.abs(Math.sin(t * 4)) * 70, 90, t * 4);
}

// —— shots (1080×1920) ——
function shot(t) {
  const sh = shotAt(t), u = (t - sh.t0) / (sh.t1 - sh.t0);
  switch (sh.id) {
    case 'wide1': cam(0, -720, lerp(.8, .86, ss(u))); return drawStreet(t, sh);
    case 'cuSher': cam(430, -470, lerp(4.2, 4.35, u)); return drawStreet(t, sh);
    case 'cuBand': cam(-430, -470, lerp(4.2, 4.4, u), t, talk('BANDIT', t).talking && t > 5.5 && t < 6.1 ? 10 : 0); return drawStreet(t, sh);
    case 'hands': { const w = seg(t, K.whip1, K.whip1 + .22), e = eio(w); cam(lerp(-350, 346, e), -300, 6.2); drawStreet(t, sh); whipLines(w); return; }
    case 'eyes': { const w = seg(t, K.whip2, K.whip2 + .2), e = eio(w); cam(lerp(-422, 421, e), lerp(-552, -556, e), 11); drawStreet(t, sh); whipLines(w); return; }
    case 'portal': cam(0, -640, .8, t, t < K.boom + .35 ? 26 * (1 - seg(t, K.boom, K.boom + .35)) : 0); return drawStreet(t, sh);
    case 'arrive': cam(0, lerp(-460, -380, ss(seg(t, 11.6, 12.2))), .95); return drawStreet(t, sh);
    case 'cuBand2': cam(-430, -475, 4.6, t, t > K.shake2 && t < K.shake2 + .3 ? 16 : 0); return drawStreet(t, sh);
    case 'cuSales': cam(0, -330, lerp(3.5, 3.75, ss(u))); return drawStreet(t, sh);
    case 'snap': { const f = seg(t, K.snap, K.carLand + .2); cam(lerp(220, 250, f), lerp(-520, -300, eio(f)), lerp(.6, .57, f), t, t > K.carLand && t < K.carLand + .3 ? 22 : 0); return drawStreet(t, sh); }
    case 'rocky': cam(lerp(150, 170, u), lerp(-80, -100, u), lerp(.6, .64, u)); return drawStreet(t, sh);
    case 'cuBand3': cam(-430, -470, 4.3); return drawStreet(t, sh);
    case 'cuSher2': cam(430, -470, lerp(4.2, 4.4, u)); return drawStreet(t, sh, { noSales: true });
    case 'cuSales2': cam(SALES2[0], SALES2[1] - 490, 3.6); return drawStreet(t, sh);
    case 'pause': cam(0, -380, lerp(.74, .82, ss(u))); return drawStreet(t, sh);
    case 'leave': cam(0, lerp(-520, -600, ss(u)), lerp(.62, .52, ss(seg(t, K.carHop, K.close1)))); return drawStreet(t, sh);
    case 'end': return endCard(t);
  }
}

// —— end card: dawn, 2026 ——
function endCard(t) {
  cam(0, -200, 1);
  dawn(t);
  const c = land(t, 44.6, .06, .5);
  rocky({ x: 260, y: 170, s: 1.9, sq: c, riders: 'cowboys', hatBounce: Math.sin(t * 6) * .04 });
  const tk = talk('SALES', t), u = seg(t, 46.4, 46.7);
  sales({ x: -210, y: 1080, s: 2.6, face: 1, turn: .2, mouth: { o: tk.o, w: tk.w, sm: .7 }, blink: blink(t, 29), look: [0, .05], happy: !tk.talking && t > 49.6, shadow: false,
    armR: { h: [lerp(10, 34, u), lerp(192, 92, u)], end: u > .5 ? 'thumb' : 'open', bend: u > .5 ? -1 : 1 }, armL: { h: [-10, 192] } });
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
