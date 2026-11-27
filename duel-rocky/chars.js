// chars.js — the cast: Sheriff (deadpan), Bandit (panic), Mas Sales (the user, drawn from their character sheet) + Rocky + props
// Local coordinates: origin between the feet, y down. face = 1 looks right (3/4 view), -1 mirrors.
import { clamp, lerp, hash, TAU } from '/core/lib.js';
import { INK, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, spline, rr, rect, noodle, quad, dot, text } from './toon.js';

export const PAL = {
  white: '#ffffff', mouthIn: '#4a1a2a', tongue: '#e8637a', sweat: '#bfe9ff',
  skS: '#f2c9a0', skSs: '#d9a57c', hatS: '#e9d29a', hatSs: '#c4a666', band: '#6b3f22', coat: '#8a5530', coatS: '#6a3e20',
  shirtS: '#2a9d8f', shirtSs: '#1f7a70', pantS: '#6f7b8c', pantSs: '#56606f', boot: '#5a3420', bootS: '#3e2214', mus: '#3a2416', straw: '#e8d36a', badge: '#f2c641', badgeS: '#c99a1e',
  skB: '#f0c094', skBs: '#d39a6c', hatB: '#2a2632', hatBs: '#17141c', hatBand: '#d9a63a', red: '#d0342c', redS: '#a32420', fringe: '#f2d8a8',
  pantB: '#3b3648', pantBs: '#2a2635', bootB: '#1f1b24', buckle: '#e0b43c',
  skM: '#e2ac80', skMs: '#c58b5e', hair: '#1d1a22', hairS: '#3a3442', navy: '#1f3c8f', navyS: '#152c6b', pipe: '#f1ead8',
  lan: '#8fd3f4', lanP: '#f07aa8', chino: '#dccbad', chinoS: '#bfac8b', shoe: '#26346a', sole: '#f4f0e6', soleR: '#d8333a', motif: '#7fc6f0', motif2: '#cdeefe',
  gun: '#8d96a3', gunS: '#5f6773', grip: '#6b3f22', leather: '#7a4a28', leatherS: '#5a3218',
  car: '#d6262e', carS: '#a81c23', carHi: '#ff6a6a', clad: '#2b2a33', glass: '#2c3e66', glassHi: '#6f86b8', rim: '#c9ced6', rimS: '#8e96a3', tire: '#1e1d24',
};

// —— face parts ——
export function eye(cx, cy, rx, ry, { lid = 0, look = [0, 0], pupil = 4.5, skin = PAL.skS, closed = false, lw = 6, jitter = 0, lower = 0 } = {}) {
  if (closed) { stroke(arc(cx, cy + ry * .15, rx * .8, ry * .45, Math.PI * .1, Math.PI * .9, 14), lw); return; }
  shape(ell(cx, cy, rx, ry, 36), {
    fill: PAL.white, lw, shade: () => {
      dot(cx + look[0] * rx * .55 + jitter, cy + look[1] * ry * .5, pupil);
      if (lid > 0) {
        const yl = cy - ry + lid * 2 * ry;
        fillOnly([[cx - rx * 1.3, cy - ry * 1.4], [cx + rx * 1.3, cy - ry * 1.4], [cx + rx * 1.3, yl], [cx - rx * 1.3, yl + ry * .08]], skin, { boil: .5 });
        stroke([[cx - rx * 1.2, yl + ry * .08], [cx + rx * 1.2, yl]], lw);
      }
      if (lower > 0) { const yb = cy + ry - lower * 2 * ry; fillOnly([[cx - rx * 1.3, yb], [cx + rx * 1.3, yb], [cx + rx * 1.3, cy + ry * 1.4], [cx - rx * 1.3, cy + ry * 1.4]], skin, { boil: .5 }); stroke([[cx - rx * 1.2, yb], [cx + rx * 1.2, yb]], lw * .8); }
    }
  });
}
export function mouth(cx, cy, mw, { o = 0, w = 1, sm = 0, skew = 0, lw = 6, teeth = true, tongue = true } = {}) {
  const hw = mw * w / 2, k = mw * .22, lc = [cx - hw, cy - sm * k + skew * k], rc = [cx + hw, cy - sm * k - skew * k];
  if (o < .07) { stroke(quad(lc, [cx, cy + sm * k * 1.2], rc, 12), lw); return; }
  const h = o * mw * .62;
  const up = quad(lc, [cx, cy - h * .25 + sm * k * .4], rc, 12), dn = quad(rc, [cx, cy + h + sm * k * .6], lc, 14);
  shape([...up, ...dn], {
    fill: PAL.mouthIn, lw, shade: () => {
      if (teeth && o > .22) fillOnly(rect(cx - hw * 1.2, cy - h, hw * 2.4, h * .32 + 6), PAL.white, { boil: .3 });
      if (tongue) fillOnly(ell(cx + hw * .15, cy + h * .95, hw * .6, h * .45, 20), PAL.tongue, { boil: .3 });
    }
  });
}
// gritted-teeth grin (bandit): a white bar with tooth lines, corners pulled
function grit(cx, cy, mw, mh, lw = 6) {
  shape(rr(cx - mw / 2, cy - mh / 2, mw, mh, mh * .45), { fill: PAL.white, lw, shade: () => { stroke([[cx - mw / 2, cy], [cx + mw / 2, cy]], 4); for (let i = 1; i < 6; i++) stroke([[cx - mw / 2 + i * mw / 6, cy - mh / 2], [cx - mw / 2 + i * mw / 6, cy + mh / 2]], 4); } });
}
export function hand(x, y, ang, r = 19, col = PAL.skS, { fist = false, lw = 6 } = {}) {
  push(); translate(x, y); rotate(ang);
  const pts = fist ? spline([[-r * .6, -r * .8], [r * .7, -r * .9], [r * 1.1, -r * .1], [r * .8, r * .8], [-r * .5, r * .9], [-r * .9, 0]])
    : spline([[-r * .5, -r * .85], [r * .5, -r * 1.05], [r * 1.35, -r * .75], [r * 1.05, -r * .3], [r * 1.5, -r * .1], [r * 1.1, r * .3], [r * 1.35, r * .7], [r * .6, r * .95], [-r * .6, r * .8], [-r * .95, 0]]);
  shape(pts, { fill: col, lw });
  stroke([[r * .2, -r * .15], [r * .75, -r * .45]], lw * .6);
  pop();
}
// thumbs up: a fist with the thumb pointing up (screen up, whatever the arm angle)
export function thumbUp(x, y, r = 20, col = PAL.skM, lw = 6) {
  push(); translate(x, y);
  shape(spline([[-r * .2, -r * .5], [r * .15, -r * 2.0], [r * .7, -r * 2.05], [r * .75, -r * .6]]), { fill: col, lw });
  shape(spline([[-r * .9, -r * .55], [r * 1.0, -r * .7], [r * 1.15, r * .2], [r * .8, r * .95], [-r * .8, r * .95], [-r * 1.05, r * .2]]), { fill: col, lw });
  for (const yy of [-.05, .4]) stroke([[-r * .7, r * yy], [r * .2, r * yy]], lw * .55);
  pop();
}
export const sweat = (x, y, s = 1) => shape(spline([[x, y - 16 * s], [x + 9 * s, y + 4 * s], [x, y + 12 * s], [x - 9 * s, y + 4 * s]]), { fill: PAL.sweat, lw: 5 });
const shadowBlob = (w = 110) => fillOnly(ell(0, 4, w, 16, 30), 'rgba(20,18,60,.35)', { boil: .3 });

// —— props ——
export function revolver(x, y, a = 0, s = 1) {
  push(); translate(x, y); rotate(a); scale(s);
  shape(rr(-6, -16, 92, 16, 5), { fill: PAL.gun, lw: 5, shade: () => fillOnly(rect(-10, -6, 110, 12), PAL.gunS, { boil: .3 }) });   // barrel
  shape(rr(-10, -24, 40, 30, 10), { fill: PAL.gun, lw: 5, shade: () => fillOnly(rect(-12, -2, 50, 12), PAL.gunS, { boil: .3 }) });  // cylinder
  shape(spline([[-12, -12], [-6, 6], [-26, 52], [-50, 48], [-34, 0]]), { fill: PAL.grip, lw: 5 });                                    // grip
  stroke(arc(-2, 10, 12, 12, 0, Math.PI, 8), 4, { closed: false });
  pop();
}
function holster(x, y, drawn, s = 1) {
  push(); translate(x, y); scale(s);
  shape(spline([[-20, -6], [22, -10], [26, 70], [6, 92], [-14, 72]]), { fill: PAL.leather, lw: 6, shade: () => fillOnly(rect(4, -20, 40, 120), PAL.leatherS, { boil: .3 }) });
  if (!drawn) shape(spline([[-10, -4], [-4, -40], [-26, -62], [-36, -46], [-18, -6]]), { fill: PAL.grip, lw: 5 });
  pop();
}

// —— shared body parts ——
function legs(P, hipY, pant, pantS, shoeFn, w = 26) {
  const lg = [P.legL || [0, 0], P.legR || [0, 0]];
  [-1, 1].forEach((sx, i) => {
    const hip = [sx * 28, hipY], ank = [sx * 32 + lg[i][0], -22 + lg[i][1]];
    shape(noodle(hip, ank, sx * -4, w, w * .85), { fill: pant, lw: 6, shade: () => fillOnly(rect(sx * 28 + 4, hipY - 10, 30, 400), pantS, { boil: .3 }) });
    shoeFn(ank);
  });
}
const boot = (col, colS) => ank => shape(spline([[ank[0] - 22, ank[1] + 22], [ank[0] - 18, ank[1] - 14], [ank[0] + 12, ank[1] - 12], [ank[0] + 16, ank[1] + 2], [ank[0] + 44, ank[1] + 10], [ank[0] + 44, ank[1] + 24]]), { fill: col, lw: 6, shade: () => fillOnly(rect(ank[0] - 40, ank[1] + 14, 100, 20), colS, { boil: .3 }) });
const sneaker = ank => shape(spline([[ank[0] - 22, ank[1] + 20], [ank[0] - 20, ank[1] - 8], [ank[0] + 8, ank[1] - 8], [ank[0] + 44, ank[1] + 6], [ank[0] + 46, ank[1] + 22]]), {
  fill: PAL.shoe, lw: 6, shade: () => { fillOnly(rect(ank[0] - 40, ank[1] + 12, 100, 20), PAL.sole, { boil: .3 }); fillOnly(rect(ank[0] - 40, ank[1] + 12, 100, 4), PAL.soleR, { boil: .2 }); }
});
function arm(sh, h, bend, sleeve, skin, { w = 20, sleeveTo = 1, pipe = null, end = 'hand', fist = false } = {}) {
  const hp = [sh[0] + h[0], sh[1] + h[1]], ang = Math.atan2(h[1], h[0]);
  if (sleeveTo < 1) {
    const el = [sh[0] + h[0] * sleeveTo, sh[1] + h[1] * sleeveTo];
    shape(noodle(sh, hp, bend, w * .8, w * .7), { fill: skin, lw: 6 });
    shape(noodle(sh, el, bend * sleeveTo, w * 1.6, w * 1.5), { fill: sleeve, lw: 6 });
    if (pipe) { const nx = -Math.sin(ang), ny = Math.cos(ang); stroke([[el[0] + nx * w * .75, el[1] + ny * w * .75], [el[0] - nx * w * .75, el[1] - ny * w * .75]], 5, { line: pipe }); }
  } else shape(noodle(sh, hp, bend, w * 1.25, w * 1.1), { fill: sleeve, lw: 6 });
  if (end === 'hand') hand(hp[0], hp[1], ang, 18, skin, { fist });
  else if (end === 'thumb') thumbUp(hp[0], hp[1] - 4, 19, skin);
  else if (end === 'gun') { hand(hp[0], hp[1], ang, 18, skin, { fist: true }); revolver(hp[0] + 6, hp[1] - 6, ang - .1, .85); }
  return hp;
}

// —— SHERIFF ——
// P: {x,y,s,face,sq,bob,lean, lid,look,brow,mouth:{o,w},blink, straw, armR:{h,bend}, armL, gun:0|1 (drawn), hatTip}
export function sheriff(P) {
  const f = P.face ?? 1;
  push(); translate(P.x, (P.y || 0) + (P.bob || 0)); if (P.shadow !== false) shadowBlob(100);
  scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  legs(P, -196, PAL.pantS, PAL.pantSs, boot(PAL.boot, PAL.bootS), 26);
  push(); rotate(P.lean ?? 0);
  const shB = [-56, -352], shF = [52, -350];
  arm(shB, (P.armL || { h: [-18, 150] }).h, (P.armL || {}).bend ?? -10, PAL.coat, PAL.skS, { w: 19 });
  // coat
  shape(spline([[-40, -378], [-82, -350], [-92, -250], [-98, -150], [-20, -140], [10, -190], [40, -140], [96, -150], [86, -260], [74, -352], [40, -378]]), {
    fill: PAL.coat, lw: 7, shade: () => {
      fillOnly(spline([[-130, -390], [-50, -370], [-70, -250], [-66, -120], [-140, -120]]), PAL.coatS, { boil: .4 });
      fillOnly([[-22, -378], [36, -378], [14, -196], [2, -196]], PAL.shirtS, { boil: .4 });
    }
  });
  stroke([[-22, -378], [2, -196]], 6); stroke([[36, -378], [14, -196]], 6);
  stroke(spline([[-34, -376], [-14, -330], [-6, -290]], false), 5);
  stroke(spline([[44, -376], [26, -330], [20, -290]], false), 5);
  // belt + holster
  shape(rr(-96, -206, 192, 22, 6), { fill: PAL.band, lw: 6 });
  shape(rr(-14, -208, 26, 26, 5), { fill: PAL.badge, lw: 5 });
  holster(80, -190, P.gun, 1);
  // star badge
  push(); translate(-48, -300); rotate(.1);
  const st = []; for (let i = 0; i < 10; i++) { const r_ = i % 2 ? 11 : 26, a = -Math.PI / 2 + i / 10 * TAU; st.push([Math.cos(a) * r_, Math.sin(a) * r_]); }
  shape(st, { fill: PAL.badge, lw: 5, shade: () => fillOnly(rect(0, -30, 30, 60), PAL.badgeS, { boil: .3 }) });
  pop();
  shape(noodle([10, -372], [16, -400], 3, 32, 32), { fill: PAL.skS, lw: 6 });
  push(); translate(18, -480); rotate(P.headTilt ?? 0); sheriffHead(P); pop();
  const armF = P.armR || { h: [30, 140], bend: 16 };
  arm(shF, armF.h, armF.bend ?? 16, PAL.coat, PAL.skS, { w: 19, end: P.gun ? 'gun' : 'hand', fist: armF.fist });
  pop(); pop();
}
export function sheriffHead(P) {
  shape(ell(-74, 8, 15, 24, 18), { fill: PAL.skS, lw: 6, shade: () => fillOnly(ell(-70, 10, 6, 12, 12), PAL.skSs, { boil: .3 }) });
  shape(spline([[-6, -104], [58, -94], [90, -40], [92, 30], [70, 90], [10, 108], [-50, 92], [-82, 40], [-86, -30], [-60, -90]]), { fill: PAL.skS, lw: 7, shade: () => fillOnly(spline([[-100, 10], [-60, 70], [10, 120], [-90, 130]]), PAL.skSs, { boil: .3 }) });
  const lid = P.blink ? 1 : clamp(P.lid ?? .48, 0, 1), look = P.look || [0, 0];
  eye(8, -14, 30, 33, { lid, look, pupil: 4.5, skin: PAL.skS });
  eye(58, -16, 23, 29, { lid, look, pupil: 4, skin: PAL.skS });
  const br = P.brow ?? 0;
  stroke([[-22, -54 - br * 8 + (P.browIn ?? 0) * 0], [34, -50 + br * 4 + (P.browIn ?? 0) * 10]], 9);
  stroke([[44, -52 + (P.browIn ?? 0) * 10], [84, -58 - br * 8]], 8);
  // nose
  shape(spline([[36, -6], [50, 16], [76, 30], [70, 48], [42, 46], [30, 30]]), { fill: PAL.skS, lw: 6, shade: () => fillOnly(ell(64, 42, 14, 8, 12), PAL.skSs, { boil: .3 }) });
  // mouth (under the moustache)
  const m = P.mouth || {};
  mouth(44, 78, 50, { o: (m.o || 0) * .8, w: m.w ?? 1, sm: m.sm ?? -.2, lw: 6, teeth: false });
  // straw
  const sa = P.straw ?? 0;
  push(); translate(70, 76); rotate(-.35 + sa);
  stroke([[0, 0], [86, -6]], 6, { line: INK }); stroke([[0, 0], [86, -6]], 3, { line: PAL.straw, boil: .3 });
  stroke([[80, -6], [98, -18]], 4, { line: PAL.straw }); stroke([[80, -6], [100, 0]], 4, { line: PAL.straw });
  pop();
  // moustache
  shape(spline([[4, 70], [20, 48], [46, 54], [74, 46], [96, 66], [104, 96], [86, 82], [70, 70], [46, 72], [22, 72], [6, 92], [-6, 86]]), { fill: PAL.mus, lw: 6 });
  // hat: brim then crown
  const tip = P.hatTip ?? 0;
  push(); translate(4, -92); rotate(-.06 + tip);
  shape(spline([[-170, 6], [-120, -14], [0, -22], [120, -16], [176, 0], [150, 22], [0, 26], [-150, 22]]), { fill: PAL.hatS, lw: 7, shade: () => fillOnly(rect(-200, 8, 400, 30), PAL.hatSs, { boil: .3 }) });
  shape(spline([[-86, -6], [-84, -70], [-50, -100], [-10, -84], [30, -100], [72, -76], [86, -6]]), { fill: PAL.hatS, lw: 7, shade: () => { fillOnly(rect(30, -110, 80, 120), PAL.hatSs, { boil: .3 }); fillOnly(rect(-100, -32, 200, 24), PAL.band, { boil: .3 }); } });
  stroke(quad([-10, -84], [-6, -60], [-14, -40], 8), 5);
  pop();
}

// —— BANDIT ——
// P: {x,y,s,face,sq,bob,nerv,t, look,eyeS,pupil,brow,mouth:{o,w},grin(0..1),blink, sweat, armR, armL, gun}
export function bandit(P) {
  const f = P.face ?? 1, ner = P.nerv ?? 0;
  const jit = ner ? (hash(Math.floor((P.t || 0) * 12) * 3.3) - .5) * 7 * ner : 0;
  push(); translate(P.x + jit, (P.y || 0) + (P.bob || 0)); if (P.shadow !== false) shadowBlob(90);
  scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  legs(P, -190, PAL.pantB, PAL.pantBs, boot(PAL.bootB, '#000000'), 22);
  push(); rotate(P.lean ?? 0);
  const shB = [-50, -330], shF = [48, -330];
  arm(shB, (P.armL || { h: [-20, 140] }).h, (P.armL || {}).bend ?? -12, PAL.red, PAL.skB, { w: 17 });
  shape(spline([[-36, -352], [-70, -330], [-80, -250], [-74, -186], [0, -176], [74, -186], [80, -250], [70, -330], [36, -352]]), {
    fill: PAL.red, lw: 7, shade: () => {
      fillOnly(spline([[20, -360], [90, -330], [100, -250], [90, -170], [40, -170], [56, -250]]), PAL.redS, { boil: .4 });
      // fringe yoke
      fillOnly(spline([[-90, -300], [0, -282], [90, -300], [90, -284], [0, -266], [-90, -284]]), PAL.fringe, { boil: .3 });
      for (let i = 0; i < 11; i++) { const x = -70 + i * 14, y = -280 + Math.abs(x) * .12 - 6; stroke([[x, y], [x + 1, y + 20]], 4, { line: PAL.fringe }); }
    }
  });
  stroke([[0, -350], [0, -196]], 4);
  for (let i = 0; i < 3; i++) dot(-8, -244 + i * 22, 4.5, PAL.fringe);
  shape([[-24, -356], [-2, -338], [-14, -322], [-34, -340]], { fill: PAL.red, lw: 5 });
  shape([[24, -356], [2, -338], [14, -322], [34, -340]], { fill: PAL.red, lw: 5 });
  shape(rr(-80, -198, 160, 22, 6), { fill: '#3b2416', lw: 6 });
  shape(ell(0, -187, 20, 15, 18), { fill: PAL.buckle, lw: 5, shade: () => dot(0, -187, 5, '#a8801e') });
  holster(70, -178, P.gun, .95);
  shape(noodle([4, -350], [8, -378], 2, 28, 28), { fill: PAL.skB, lw: 6 });
  push(); translate(8, -452); rotate(P.headTilt ?? 0); banditHead(P, ner); pop();
  const armF = P.armR || { h: [30, 130], bend: 14 };
  arm(shF, armF.h, armF.bend ?? 14, PAL.red, PAL.skB, { w: 17, end: P.gun ? 'gun' : 'hand', fist: armF.fist });
  pop();
  if (P.sweat != null) { const u = P.sweat % 1; sweat(-70, -540 + u * 40, 1); sweat(96, -520 + ((u + .5) % 1) * 40, .8); }
  pop();
}
export function banditHead(P, ner = 0) {
  for (const sx of [-1, 1]) shape(ell(sx * 84, 8, 14, 21, 16), { fill: PAL.skB, lw: 6 });
  shape(ell(0, 0, 88, 86, 60), { fill: PAL.skB, lw: 7, shade: () => fillOnly(ell(50, 34, 56, 64, 30), PAL.skBs, { boil: .3 }) });
  const br = P.brow ?? 1;
  stroke([[-62, -40 + br * 2], [-24, -50 - br * 9]], 8); stroke([[62, -40 + br * 2], [24, -50 - br * 9]], 8);
  const look = P.look || [0, 0], shake = ner ? (hash(Math.floor((P.t || 0) * 24) * 1.7) - .5) * 3 * ner : 0, es = P.eyeS ?? 1;
  for (const ex of [-34, 34]) eye(ex, -6, 30 * es, 34 * es, { lid: P.blink ? 1 : (P.lid ?? 0), look, pupil: P.pupil ?? 3.4, skin: PAL.skB, jitter: shake });
  shape(ell(4, 30, 9, 8, 12), { fill: PAL.skBs, lw: 5 });
  const m = P.mouth || {};
  if ((m.o || 0) > .08 || !P.grin) mouth(2, 60, 56, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? -.4, lw: 6 });
  else grit(2, 60, 70 * (.8 + P.grin * .2), 26);
  // hat
  push(); translate(0, -72); rotate(P.hatTilt ?? -.08);
  shape(spline([[-120, 4], [-60, -8], [60, -8], [124, 2], [100, 16], [-100, 16]]), { fill: PAL.hatB, lw: 7 });
  shape(spline([[-62, -2], [-58, -62], [-20, -78], [24, -66], [60, -58], [62, -2]]), { fill: PAL.hatB, lw: 7, shade: () => { fillOnly(rect(20, -90, 60, 100), PAL.hatBs, { boil: .3 }); fillOnly(rect(-80, -22, 160, 16), PAL.hatBand, { boil: .3 }); } });
  pop();
}

// —— MAS SALES (the user) ——
// P: {x,y,s,face,sq,bob,lean, turn(-1..1 3/4 → front), lid,look,brow,mouth:{o,w,sm},blink, armR:{h,bend,end}, armL, stretch}
export function sales(P) {
  const f = P.face ?? 1;
  push(); translate(P.x, (P.y || 0) + (P.bob || 0)); if (P.shadow !== false) shadowBlob(100);
  scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  legs(P, -196, PAL.chino, PAL.chinoS, sneaker, 30);
  push(); rotate(P.lean ?? 0);
  const shB = [-60, -350], shF = [58, -350];
  const aL = P.armL || { h: [-16, 146], bend: -10 };
  arm(shB, aL.h, aL.bend ?? -10, PAL.navy, PAL.skM, { w: 19, sleeveTo: .36, pipe: PAL.pipe, end: aL.end || 'hand', fist: aL.fist });
  // shirt (untucked), side motif panel
  shape(spline([[-40, -376], [-78, -352], [-82, -260], [-78, -182], [0, -174], [78, -182], [82, -260], [78, -352], [40, -376]]), {
    fill: PAL.navy, lw: 7, shade: () => {
      fillOnly(spline([[30, -390], [100, -350], [110, -250], [100, -160], [50, -160], [62, -260]]), PAL.navyS, { boil: .4 });
      fillOnly([[58, -236], [90, -250], [90, -160], [62, -160], [74, -196]], PAL.motif, { boil: .3 });
      fillOnly([[72, -216], [90, -226], [90, -176], [80, -176]], PAL.motif2, { boil: .3 });
      fillOnly([[-96, -220], [-72, -200], [-66, -160], [-96, -160]], PAL.motif, { boil: .3 });
    }
  });
  stroke([[4, -372], [4, -176]], 4, { line: '#0f2150' });
  for (let i = 0; i < 4; i++) dot(-4, -320 + i * 36, 3.5, '#e8e4ff');
  // collar
  shape([[-30, -382], [-2, -360], [-20, -334], [-44, -360]], { fill: PAL.navy, lw: 5 });
  shape([[30, -382], [2, -360], [20, -334], [44, -360]], { fill: PAL.navy, lw: 5 });
  // chest print
  text('DAIHATSU', 58, -326, { font: '800 15px "Baloo 2"', fill: '#f4f1ea' });
  // pocket
  shape(rr(-70, -316, 40, 44, 4), { lw: 4, line: '#0f2150' });
  // lanyard + ID card
  stroke([[-24, -366], [-14, -280], [-2, -246]], 8, { line: INK }); stroke([[-24, -366], [-14, -280], [-2, -246]], 5, { line: PAL.lan, boil: .3 });
  stroke([[24, -366], [12, -280], [2, -246]], 8, { line: INK }); stroke([[24, -366], [12, -280], [2, -246]], 5, { line: PAL.lan, boil: .3 });
  dot(-16, -300, 3.5, PAL.lanP); dot(14, -312, 3.5, PAL.lanP);
  shape(rr(-18, -246, 36, 48, 4), { fill: '#ffffff', lw: 5, shade: () => { fillOnly(rect(-12, -238, 24, 14), '#8fb4e8', { boil: .2 }); fillOnly(rect(-12, -218, 24, 4), '#c9c9d6', { boil: .2 }); } });
  shape(noodle([6, -374], [8, -400], 2, 32, 32), { fill: PAL.skM, lw: 6 });
  push(); translate(8, -482); rotate(P.headTilt ?? 0); salesHead(P); pop();
  const aR = P.armR || { h: [24, 146], bend: 12 };
  arm(shF, aR.h, aR.bend ?? 12, PAL.navy, PAL.skM, { w: 19, sleeveTo: .36, pipe: PAL.pipe, end: aR.end || 'hand', fist: aR.fist });
  pop(); pop();
}
export function salesHead(P) {
  const tu = P.turn ?? .4, ox = tu * 26;   // feature shift: 0 = front, 1 = 3/4
  shape(ell(-78 + ox * .3, 8, 14, 22, 16), { fill: PAL.skM, lw: 6, shade: () => fillOnly(ell(-74, 10, 6, 11, 10), PAL.skMs, { boil: .3 }) });
  if (tu < .5) shape(ell(80 + ox * .3, 8, 14, 22, 16), { fill: PAL.skM, lw: 6 });
  shape(spline([[0, -100], [56, -90], [84, -40], [84, 30], [62, 82], [14, 104], [-36, 92], [-70, 46], [-82, -20], [-62, -82]]), { fill: PAL.skM, lw: 7, shade: () => fillOnly(spline([[-100, 0], [-66, 64], [10, 120], [-90, 120]]), PAL.skMs, { boil: .3 }) });
  // hair: full black top, side part on the left, fringe sweeping right
  shape(spline([[-84, -8], [-90, -60], [-62, -112], [-6, -132], [52, -124], [92, -88], [96, -40], [84, -20], [74, -56], [40, -72], [0, -70], [-30, -62], [-56, -66], [-70, -30]]), {
    fill: PAL.hair, lw: 7, shade: () => { fillOnly(spline([[-40, -120], [10, -128], [60, -110], [20, -100], [-20, -104]]), PAL.hairS, { boil: .3 }); }
  });
  stroke(quad([-40, -118], [-34, -96], [-44, -70], 8), 4, { line: '#6a6274' });   // parting
  const lid = P.blink ? 1 : clamp(P.lid ?? .12, 0, 1), look = P.look || [0, 0], br = P.brow ?? 0;
  const e1 = -24 + ox, e2 = 30 + ox;
  stroke([[e1 - 24, -46 - br * 6], [e1 + 20, -50 - br * 8]], 9); stroke([[e2 - 18, -50 - br * 8], [e2 + 24, -46 - br * 6]], 9);
  if (P.happy) { stroke(arc(e1, -8, 18, 14, Math.PI * 1.1, Math.PI * 1.9, 10), 6); stroke(arc(e2, -8, 17, 14, Math.PI * 1.1, Math.PI * 1.9, 10), 6); }
  else { eye(e1, -12, 24, 28, { lid, look, pupil: 5, skin: PAL.skM }); eye(e2, -12, 22 - tu * 2, 27, { lid, look, pupil: 5, skin: PAL.skM }); }
  stroke(spline([[ox + 6, 0], [ox + 14, 28], [ox + 2, 36]], false), 5);
  const m = P.mouth || {};
  mouth(ox + 4, 64, 54, { o: m.o || 0, w: m.w ?? 1, sm: m.sm ?? .7, lw: 6 });
}

// —— Rocky (side view, faces right; origin at ground centre) ——
// P: {x,y,s,sq,face,riders:bool,t, wheelRot, lights}
export function rocky(P) {
  const f = P.face ?? 1;
  push(); translate(P.x, P.y || 0);
  if (P.shadow !== false) fillOnly(ell(0, 6, 330 * (P.s ?? 1), 22, 40), 'rgba(20,18,60,.38)', { boil: .3 });
  scale((P.s ?? 1) * f * (P.sx ?? 1), (P.s ?? 1) * (P.sq ?? 1));
  const wr = P.wheelRot || 0;
  // body
  const body = spline([[-318, -52], [-326, -150], [-300, -206], [-262, -258], [80, -266], [116, -256], [214, -176], [306, -158], [330, -120], [330, -56], [250, -40], [-250, -40]]);
  shape(body, {
    fill: PAL.car, lw: 7, shade: () => {
      fillOnly(rect(-360, -120, 720, 30), PAL.carS, { boil: .3 });
      fillOnly(spline([[-300, -200], [100, -210], [220, -170], [300, -150], [300, -142], [100, -196], [-300, -188]]), PAL.carHi, { boil: .3 });
      fillOnly(rect(-360, -78, 720, 60), PAL.clad, { boil: .3 });
    }
  });
  // windows (+ riders inside)
  const win = [[-262, -236], [86, -246], [174, -180], [-252, -176]];
  shape(win, {
    fill: PAL.glass, lw: 6, shade: () => {
      if (P.riders) {
        push(); translate(-150, -120); scale(.42); sheriffHead({ lid: .5, mouth: { sm: .3 }, look: [.6, 0], hatTip: P.hatBounce || 0 }); pop();
        push(); translate(-10, -126); scale(.42); banditHead({ look: [.6, 0], grin: 1, brow: -.3 }); pop();
        if (P.riders !== 'cowboys') { push(); translate(110, -128); scale(.42); salesHead({ turn: 1, happy: true, mouth: { sm: 1 } }); pop(); }
      }
      fillOnly([[-200, -250], [-150, -250], [-220, -160], [-270, -160]], 'rgba(255,255,255,.22)', { boil: .2 });
      fillOnly([[40, -250], [70, -250], [10, -160], [-20, -160]], 'rgba(255,255,255,.16)', { boil: .2 });
    }
  });
  stroke([[-60, -244], [-60, -176]], 12); stroke([[-200, -238], [-205, -176]], 10);   // pillars
  // roof rails
  shape(rr(-250, -280, 300, 12, 5), { fill: PAL.clad, lw: 5 });
  // door lines + handles
  stroke([[-60, -176], [-62, -60]], 4); stroke([[176, -176], [168, -64]], 4);
  shape(rr(-110, -160, 34, 9, 4), { fill: PAL.clad, lw: 4 }); shape(rr(110, -160, 34, 9, 4), { fill: PAL.clad, lw: 4 });
  // mirror
  shape(spline([[160, -190], [196, -196], [200, -172], [168, -170]]), { fill: PAL.car, lw: 5 });
  // lights
  shape(spline([[268, -160], [326, -146], [322, -132], [272, -142]]), { fill: '#fff6d0', lw: 5 });
  shape(rr(-326, -168, 22, 36, 6), { fill: '#a01018', lw: 5 });
  text('ROCKY', -10, -100, { font: '800 30px "Baloo 2"', fill: '#f1f1f4' });
  // wheels
  for (const wx of [-196, 200]) {
    shape(arc(wx, -50, 84, 80, Math.PI, TAU, 18).concat([[wx + 84, -40], [wx - 84, -40]]), { fill: PAL.clad, lw: 6 });
    shape(ell(wx, -38, 64, 64, 36), {
      fill: PAL.tire, lw: 7, shade: () => {
        fillOnly(ell(wx, -38, 40, 40, 28), PAL.rim, { boil: .2 });
        for (let k = 0; k < 5; k++) { const a = wr + k / 5 * TAU; stroke([[wx, -38], [wx + Math.cos(a) * 36, -38 + Math.sin(a) * 36]], 7, { line: PAL.rimS }); }
        dot(wx, -38, 9, PAL.rimS);
      }
    });
  }
  pop();
}

// —— small props ——
export function tumbleweed(x, y, r, rot) {
  push(); translate(x, y); rotate(rot);
  shape(ell(0, 0, r, r * .92, 26), { fill: 'rgba(196,160,110,.25)', lw: 5, line: '#c9a46c' });
  for (let i = 0; i < 7; i++) { const a = hash(i) * TAU; stroke(arc(Math.cos(a) * r * .3, Math.sin(a) * r * .3, r * .7, r * .55, a, a + 2.4, 10), 4, { line: '#c9a46c' }); }
  pop();
}
