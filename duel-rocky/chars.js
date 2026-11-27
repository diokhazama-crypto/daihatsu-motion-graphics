// chars.js — the cast with realistic human proportions (≈7.5 heads tall), drawn as flat-colour illustration with boiling outlines.
// Sheriff (deadpan), Bandit (panic), Mas Sales (the user, from their character sheet) + Rocky (real scale) + props.
// Body units: origin between the feet, y down, a figure is 600 units tall (1 m ≈ 350 units). face = 1 looks right, -1 mirrors.
import { clamp, lerp, hash, TAU } from '/core/lib.js';
import { INK, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, spline, rr, rect, noodle, quad, dot, text, zoom } from './toon.js';

export const PAL = {
  white: '#fbfaf7', mouthIn: '#5a1f2a', tongue: '#d86a78', teeth: '#f6f2e8', sweat: '#bfe9ff', lip: '#b9655a', iris: '#4a2e1e',
  skS: '#e7b68c', skSs: '#c99268', hatS: '#d9bf86', hatSs: '#b39a62', band: '#5a341c', coat: '#7d4f2c', coatS: '#5f3a1e',
  shirtS: '#2a8f84', shirtSs: '#1f6e66', pantS: '#6b7584', pantSs: '#525b69', boot: '#5a3420', bootS: '#3e2214', mus: '#4a3424', hairS: '#7a6a5c', straw: '#e8d36a', badge: '#f2c641', badgeS: '#c99a1e',
  skB: '#e0a97c', skBs: '#c08860', hatB: '#2a2632', hatBs: '#17141c', hatBand: '#c9963a', red: '#c4322b', redS: '#99231f', fringe: '#f0d6a2', hairB: '#2a2220', scarf: '#e0b43c',
  pantB: '#3a3546', pantBs: '#27232f', bootB: '#221d26', buckle: '#e0b43c',
  skM: '#d9a074', skMs: '#b97f58', hair: '#16141a', hairHi: '#3a3442', navy: '#1f3c8f', navyS: '#152c6b', pipe: '#f1ead8',
  lan: '#8fd3f4', lanP: '#f07aa8', chino: '#d8c6a6', chinoS: '#b9a685', shoe: '#26346a', sole: '#f4f0e6', soleR: '#d8333a', motif: '#7fc6f0', motif2: '#cdeefe',
  gun: '#8d96a3', gunS: '#5f6773', grip: '#6b3f22', leather: '#7a4a28', leatherS: '#5a3218',
  car: '#d6262e', carS: '#a81c23', carHi: '#ff6a6a', clad: '#2b2a33', glass: '#2c3e66', glassHi: '#6f86b8', rim: '#c9ced6', rimS: '#8e96a3', tire: '#1e1d24',
};
const LW = 4.5, FW = 3;   // body outline, face detail (screen px)

// —— two-bone IK ——
function ik(a, target, L1, L2, side) {
  let dx = target[0] - a[0], dy = target[1] - a[1], d = Math.hypot(dx, dy) || 1;
  const dd = clamp(d, Math.abs(L1 - L2) + 1, (L1 + L2) * .995), base = Math.atan2(dy, dx);
  const ang = Math.acos(clamp((L1 * L1 + dd * dd - L2 * L2) / (2 * L1 * dd), -1, 1));
  const e = [a[0] + Math.cos(base + side * ang) * L1, a[1] + Math.sin(base + side * ang) * L1];
  return [e, [a[0] + Math.cos(base) * dd, a[1] + Math.sin(base) * dd]];
}
const seg2 = (a, b, w0, w1, fill, o = {}) => shape(noodle(a, b, 0, w0, w1), { fill, lw: LW, ...o });

// —— hands (length L along the forearm direction) ——
export function hand(x, y, ang, L = 58, col = PAL.skS, mode = 'open') {
  push(); translate(x, y);
  if (mode === 'thumb') {   // thumbs up, screen-aligned
    const k = L / 58;
    shape(spline([[-6 * k, -6 * k], [-4 * k, -40 * k], [6 * k, -44 * k], [12 * k, -36 * k], [10 * k, -6 * k]]), { fill: col, lw: LW });
    shape(spline([[-16 * k, -8 * k], [20 * k, -10 * k], [24 * k, 6 * k], [22 * k, 26 * k], [-14 * k, 26 * k], [-20 * k, 8 * k]]), { fill: col, lw: LW });
    for (const yy of [2, 12]) stroke([[-12 * k, yy * k], [14 * k, yy * k]], FW);
    pop(); return;
  }
  rotate(ang); const s = L;
  if (mode === 'fist' || mode === 'grip') {
    shape(spline([[0, -.2 * s], [.42 * s, -.25 * s], [.62 * s, -.12 * s], [.62 * s, .16 * s], [.42 * s, .26 * s], [0, .2 * s]]), { fill: col, lw: LW });
    for (const yy of [-.08, .04, .14]) stroke([[.42 * s, yy * s], [.6 * s, yy * s]], FW);
    stroke([[.1 * s, .1 * s], [.4 * s, .18 * s]], FW);
  } else if (mode === 'point') {
    shape(spline([[0, -.2 * s], [.5 * s, -.2 * s], [1.05 * s, -.14 * s], [1.08 * s, -.04 * s], [.6 * s, -.02 * s], [.6 * s, .16 * s], [.42 * s, .26 * s], [0, .2 * s]]), { fill: col, lw: LW });
  } else {
    shape(spline([[0, -.19 * s], [.55 * s, -.22 * s], [.98 * s, -.14 * s], [1.02 * s, .02 * s], [.95 * s, .14 * s], [.56 * s, .17 * s], [.5 * s, .3 * s], [.4 * s, .42 * s], [.3 * s, .36 * s], [.2 * s, .24 * s], [0, .2 * s]]), { fill: col, lw: LW });
    for (const yy of [-.1, -.02, .06]) stroke([[.62 * s, yy * s], [.92 * s, yy * s]], FW * .8);
  }
  pop();
}
export const sweat = (x, y, s = 1) => shape(spline([[x, y - 11 * s], [x + 6 * s, y + 3 * s], [x, y + 8 * s], [x - 6 * s, y + 3 * s]]), { fill: PAL.sweat, lw: 3.5 });
const shadowBlob = (w = 95) => fillOnly(ell(0, 4, w, 14, 30), 'rgba(20,18,60,.35)', { boil: .3 });

// —— props ——
export function revolver(x, y, a = 0, s = 1) {
  push(); translate(x, y); rotate(a); scale(s);
  shape(rr(-4, -10, 66, 11, 4), { fill: PAL.gun, lw: LW, shade: () => fillOnly(rect(-8, -4, 80, 8), PAL.gunS, { boil: .3 }) });
  shape(rr(-8, -16, 28, 21, 7), { fill: PAL.gun, lw: LW });
  shape(spline([[-8, -8], [-4, 4], [-18, 36], [-34, 33], [-24, 0]]), { fill: PAL.grip, lw: LW });
  pop();
}
function holster(x, y, drawn) {
  push(); translate(x, y);
  shape(spline([[-14, -4], [16, -8], [20, 56], [6, 72], [-10, 56]]), { fill: PAL.leather, lw: LW, shade: () => fillOnly(rect(4, -16, 30, 100), PAL.leatherS, { boil: .3 }) });
  if (!drawn) shape(spline([[-8, -2], [-4, -30], [-20, -46], [-28, -34], [-14, -4]]), { fill: PAL.grip, lw: LW });
  pop();
}

// —— the body rig ——
// C: costume {skin, skinS, top, topS, sleeve:'short'|'long', sleeveCol, pant, pantS, shoe:'boot'|'sneaker', bootCol, bootS, hemY, coat?}
const SH = 72, SHY = -486, HIPY = -300, L_UA = 106, L_FA = 94, L_TH = 142, L_SH = 134;
function rig(P, C, extras) {
  const f = P.face ?? 1;
  push(); translate(P.x, (P.y || 0) + (P.bob || 0)); if (P.shadow !== false) shadowBlob(90 * (P.s ?? 1));
  scale((P.s ?? 1) * f, (P.s ?? 1) * (P.sq ?? 1));
  // legs
  const lg = [P.legL || [0, 0], P.legR || [0, 0]];
  [-1, 1].forEach((sx, i) => {
    const hip = [sx * 30, HIPY], ank = [sx * 30 + lg[i][0] + 4, -26 + lg[i][1]];
    const [knee, a2] = ik(hip, ank, L_TH, L_SH, sx > 0 ? -1 : 1);
    seg2(hip, knee, 52, 40, C.pant, { shade: () => fillOnly(rect(sx * 30 + 6, -400, 40, 420), C.pantS, { boil: .3 }) });
    seg2(knee, a2, 40, 30, C.pant, { shade: () => fillOnly(rect(sx * 30 + 6, -400, 40, 420), C.pantS, { boil: .3 }) });
    shoe(a2, C);
  });
  push(); rotate(P.lean ?? 0);
  const aL = P.armL || { h: [-10, 192] }, aR = P.armR || { h: [10, 192] };
  arm([-SH + 8, SHY + 8], aL, C, -1, P);
  extras.back && extras.back();
  // torso
  const hem = C.hemY ?? -270;
  shape(spline([[-18, -512], [-62, -500], [-SH - 4, -478], [-70, -430], [-58, -372], [-62, hem], [0, hem + 6], [62, hem], [58, -372], [70, -430], [SH + 4, -478], [62, -500], [18, -512]]), {
    fill: C.top, lw: LW, shade: () => { fillOnly(spline([[30, -520], [90, -490], [90, hem + 20], [40, hem + 20], [52, -400]]), C.topS, { boil: .4 }); extras.torso && extras.torso(hem); }
  });
  extras.front && extras.front(hem);
  // neck + head
  shape([[-13, -534], [13, -534], [17, -494], [-17, -494]], { fill: C.skin, lw: LW, shade: () => fillOnly(rect(-24, -536, 48, 9), C.skinS, { boil: .3 }) });
  extras.collar && extras.collar();
  push(); translate(4, -568); rotate(P.headTilt ?? 0); extras.head(P); pop();
  arm([SH - 8, SHY + 8], aR, C, 1, P);
  pop();
  extras.after && extras.after();
  pop();
}
function arm(sh, A, C, side, P) {
  const tgt = [sh[0] + A.h[0], sh[1] + A.h[1]];
  const [el, hp] = ik(sh, tgt, L_UA, L_FA, (A.bend ?? (side > 0 ? 1 : -1)) >= 0 ? -1 : 1);
  const ang = Math.atan2(hp[1] - el[1], hp[0] - el[0]);
  const long = C.sleeve === 'long', sc = C.sleeveCol || C.top;
  seg2(sh, el, 32, 26, long ? sc : C.skin);
  seg2(el, hp, 26, 20, long ? sc : C.skin);
  if (!long) { const m = [lerp(sh[0], el[0], .5), lerp(sh[1], el[1], .5)]; seg2(sh, m, 40, 38, sc); const nx = -(m[1] - sh[1]), ny = m[0] - sh[0], l = Math.hypot(nx, ny) || 1; if (C.pipe) stroke([[m[0] + nx / l * 18, m[1] + ny / l * 18], [m[0] - nx / l * 18, m[1] - ny / l * 18]], 4, { line: C.pipe }); }
  else { const c = [hp[0] - Math.cos(ang) * 6, hp[1] - Math.sin(ang) * 6]; fillOnly(ell(c[0], c[1], 13, 13, 12), C.cuff || sc, { boil: .3 }); }
  const mode = A.end || (A.fist ? 'fist' : 'open');
  if (mode === "gun") { hand(hp[0], hp[1], ang, 48, C.skin, 'grip'); revolver(hp[0] + Math.cos(ang) * 22, hp[1] + Math.sin(ang) * 22 - 6, ang - Math.PI / 2 + .2, .8); }
  else hand(hp[0], hp[1], ang, 48, C.skin, mode);
}
function shoe(a, C) {
  const [x, y] = a;
  if (C.shoe === 'sneaker') shape(spline([[x - 22, y + 22], [x - 20, y - 4], [x + 6, y - 6], [x + 40, y + 6], [x + 48, y + 24]]), {
    fill: PAL.shoe, lw: LW, shade: () => { fillOnly(rect(x - 40, y + 14, 110, 20), PAL.sole, { boil: .3 }); fillOnly(rect(x - 40, y + 14, 110, 4), PAL.soleR, { boil: .2 }); }
  });
  else shape(spline([[x - 20, y + 24], [x - 18, y - 22], [x + 12, y - 22], [x + 14, y], [x + 46, y + 8], [x + 48, y + 26]]), { fill: C.bootCol, lw: LW, shade: () => fillOnly(rect(x - 40, y + 16, 110, 20), C.bootS, { boil: .3 }) });
}

// —— faces (head units: 100 wide, drawn at 0.62) ——
const HS = .62;
function face(P, o) {
  const tu = P.turn ?? .55, ox = tu * 9, detail = zoom() > .75;
  // back ear
  shape(ell(-44 + ox * .2, 4, 8, 14, 14), { fill: o.skin, lw: FW + .5, shade: () => fillOnly(ell(-42, 6, 4, 8, 10), o.skinS, { boil: .3 }) });
  if (tu < .3) shape(ell(48, 4, 8, 14, 14), { fill: o.skin, lw: FW + .5 });
  // head + jaw
  shape(spline([[-46, -22], [-42, -54], [-18, -68], [14, -68], [40, -54], [50, -20], [50 + ox * .2, 12], [42 + ox * .4, 40], [24 + ox * .6, 60], [6 + ox * .6, 68], [-14, 64], [-34, 48], [-46, 20]]), {
    fill: o.skin, lw: LW, shade: () => { fillOnly(spline([[-60, -10], [-40, 40], [-10, 76], [-60, 80]]), o.skinS, { boil: .3 }); o.stubble && fillOnly(spline([[-40, 30], [0, 44], [48, 30], [40, 60], [6, 74], [-30, 56]]), o.stubble, { boil: .3 }); }
  });
  o.hairBack && o.hairBack(ox);
  const lk = P.look || [0, 0], es = P.eyeS ?? 1, lid = P.blink ? 1 : clamp(P.lid ?? .25, 0, 1);
  const eyes = [[-17 + ox, -4, 1 - tu * .18], [20 + ox * 1.2, -4, 1]];
  // brows
  const br = P.brow ?? 0, bi = P.browIn ?? 0;
  for (const [ex, ey, k] of eyes) {
    const inner = ex < ox ? 1 : -1;   // which end is toward the nose
    const yi = ey - 16 - br * 4 + bi * 4, yo = ey - 17 - br * 2 - bi * 1;
    shape([[ex - 11 * k, inner > 0 ? yo : yi], [ex + 11 * k, inner > 0 ? yi : yo], [ex + 11 * k, (inner > 0 ? yi : yo) + 4], [ex - 11 * k, (inner > 0 ? yo : yi) + 4]], { fill: o.brow, lw: FW * .7, line: o.brow });
  }
  // eyes
  for (const [ex, ey, k] of eyes) {
    const w = 10 * k, h = 5.5 * es;
    if (!detail) { if (lid < .8) dot(ex + lk[0] * 2, ey, 3.2, INK); else stroke([[ex - w, ey], [ex + w, ey]], FW); continue; }
    if (P.happy) { stroke(arc(ex, ey + 3, w, 6, Math.PI * 1.1, Math.PI * 1.9, 10), FW + .5); continue; }
    const E = [...arc(ex, ey, w, h * 1.2, Math.PI, TAU, 12), ...arc(ex, ey, w, h * .8, 0, Math.PI, 12).slice(1, -1)];
    shape(E, {
      fill: PAL.white, lw: FW, shade: () => {
        const ir = (P.pupil ? 3.6 : 5) * (es > 1.15 ? .8 : 1), px = ex + lk[0] * w * .45 + (P.jitter || 0), py = ey + lk[1] * h * .4;
        fillOnly(ell(px, py, ir, ir, 14), o.iris || PAL.iris, { boil: .2 }); dot(px, py, ir * .45, '#120d0c'); dot(px + ir * .35, py - ir * .35, ir * .25, '#ffffff');
        if (lid > 0) { const yl = ey - h * 1.2 + lid * h * 2.2; fillOnly([[ex - w - 4, ey - h * 2], [ex + w + 4, ey - h * 2], [ex + w + 4, yl], [ex - w - 4, yl]], o.skin, { boil: .3 }); stroke([[ex - w - 2, yl], [ex + w + 2, yl]], FW); }
      }
    });
    stroke(arc(ex, ey - .5, w + 1, h * 1.3, Math.PI * 1.05, Math.PI * 1.95, 10), FW + 1);   // upper lash line
  }
  if (o.bags) for (const [ex, ey, k] of eyes) stroke(arc(ex, ey + 6, 9 * k, 4, Math.PI * .2, Math.PI * .8, 6), FW * .7, { line: o.skinS });
  // nose
  stroke(spline([[ox + 4, -2], [ox + 7, 16], [ox + 11, 24]], false), FW);
  stroke(spline([[ox - 4, 25], [ox + 3, 28], [ox + 11, 24]], false), FW);
  // mouth
  const m = P.mouth || {}, mo = clamp(m.o || 0, 0, 1), mw = 13 * (m.w ?? 1), sm = m.sm ?? .2, mx = ox + 3, my = 42;
  if (P.grit) {
    shape(rr(mx - 15, my - 6, 30, 12, 5), { fill: PAL.teeth, lw: FW, shade: () => { stroke([[mx - 15, my], [mx + 15, my]], 2); for (let i = 1; i < 5; i++) stroke([[mx - 15 + i * 6, my - 6], [mx - 15 + i * 6, my + 6]], 2); } });
  } else if (mo < .08) {
    stroke(quad([mx - mw, my - sm * 3], [mx, my + sm * 4], [mx + mw, my - sm * 3], 10), FW + .5);
    if (detail) stroke(arc(mx, my + 7, mw * .55, 3, Math.PI * .15, Math.PI * .85, 6), FW * .7, { line: o.skinS });
  } else {
    const h = mo * 15;
    shape([...quad([mx - mw, my - sm * 2], [mx, my - 3], [mx + mw, my - sm * 2], 10), ...quad([mx + mw, my - sm * 2], [mx, my + h], [mx - mw, my - sm * 2], 10)], {
      fill: PAL.mouthIn, lw: FW, shade: () => { if (mo > .25) fillOnly(rect(mx - mw, my - 6, mw * 2, 5), PAL.teeth, { boil: .2 }); fillOnly(ell(mx, my + h * .9, mw * .55, h * .4, 12), PAL.tongue, { boil: .2 }); }
    });
  }
  o.front && o.front(ox, mx, my);
}

// —— SHERIFF ——
const C_SH = { skin: PAL.skS, skinS: PAL.skSs, top: PAL.coat, topS: PAL.coatS, sleeve: 'long', pant: PAL.pantS, pantS: PAL.pantSs, shoe: 'boot', bootCol: PAL.boot, bootS: PAL.bootS, hemY: -232 };
export function sheriffHead(P) {
  push(); scale(HS);
  face({ turn: .55, lid: .45, ...P }, {
    skin: PAL.skS, skinS: PAL.skSs, brow: '#5a4636', stubble: 'rgba(120,90,70,.25)', bags: true,
    hairBack: () => fillOnly(spline([[-48, -40], [-50, 0], [-42, 10], [-40, -30]]), PAL.hairS, { boil: .3 }),
    front: (ox, mx, my) => {
      const sa = P.straw ?? 0;   // straw from the mouth corner
      push(); translate(mx + 11, my + 1); rotate(-.25 + sa); stroke([[0, 0], [58, -4]], 5); stroke([[0, 0], [58, -4]], 2.5, { line: PAL.straw }); stroke([[52, -4], [64, -12]], 2.5, { line: PAL.straw }); stroke([[52, -4], [66, 0]], 2.5, { line: PAL.straw }); pop();
      shape(spline([[mx - 22, my - 4], [mx - 10, my - 13], [mx + 3, my - 10], [mx + 16, my - 13], [mx + 26, my - 4], [mx + 28, my + 12], [mx + 20, my + 4], [mx + 3, my - 1], [mx - 14, my + 4], [mx - 24, my + 12]]), { fill: PAL.mus, lw: FW });
    }
  });
  // hat
  const tip = P.hatTip ?? 0;
  push(); translate(2, -46); rotate(-.05 + tip);
  shape(spline([[-118, 6], [-80, -8], [0, -12], [80, -8], [122, 2], [100, 14], [0, 18], [-100, 14]]), { fill: PAL.hatS, lw: LW, shade: () => fillOnly(rect(-140, 6, 280, 20), PAL.hatSs, { boil: .3 }) });
  shape(spline([[-60, -4], [-58, -54], [-32, -76], [-4, -66], [26, -76], [52, -56], [60, -4]]), { fill: PAL.hatS, lw: LW, shade: () => { fillOnly(rect(20, -90, 60, 100), PAL.hatSs, { boil: .3 }); fillOnly(rect(-70, -22, 140, 16), PAL.band, { boil: .3 }); } });
  stroke(quad([-4, -66], [-2, -48], [-8, -32], 8), FW);
  pop();
  pop();
}
export function sheriff(P) {
  rig(P, C_SH, {
    torso: hem => {
      fillOnly([[-20, -520], [24, -520], [16, hem], [-12, hem]], PAL.shirtS, { boil: .3 });   // shirt between the open coat
      fillOnly([[-14, -505], [18, -505], [12, -440], [-8, -440]], PAL.shirtSs, { boil: .3 });
      stroke([[-20, -512], [-12, hem]], LW); stroke([[24, -512], [16, hem]], LW);
      stroke(spline([[-26, -510], [-40, -460], [-22, -420]], false), FW + 1); stroke(spline([[30, -510], [44, -460], [24, -420]], false), FW + 1);
    },
    front: hem => {
      shape(rr(-64, -322, 128, 16, 4), { fill: PAL.band, lw: LW }); shape(rr(-9, -324, 18, 20, 3), { fill: PAL.badge, lw: FW });
      holster(66, -308, P.gun);
      push(); translate(-38, -446); rotate(.1);
      const st = []; for (let i = 0; i < 10; i++) { const r_ = i % 2 ? 7 : 16, a = -Math.PI / 2 + i / 10 * TAU; st.push([Math.cos(a) * r_, Math.sin(a) * r_]); }
      shape(st, { fill: PAL.badge, lw: FW, shade: () => fillOnly(rect(0, -20, 20, 40), PAL.badgeS, { boil: .3 }) }); pop();
    },
    head: sheriffHead,
  });
}

// —— BANDIT ——
const C_BA = { skin: PAL.skB, skinS: PAL.skBs, top: PAL.red, topS: PAL.redS, sleeve: 'long', pant: PAL.pantB, pantS: PAL.pantBs, shoe: 'boot', bootCol: PAL.bootB, bootS: '#000000', hemY: -300 };
export function banditHead(P) {
  push(); scale(HS);
  face({ turn: .5, lid: 0, ...P, grit: P.grin && !((P.mouth || {}).o > .08) }, {
    skin: PAL.skB, skinS: PAL.skBs, brow: PAL.hairB, stubble: 'rgba(60,40,30,.28)',
    hairBack: () => { fillOnly(spline([[-50, -36], [-54, 4], [-44, 16], [-40, -20]]), PAL.hairB, { boil: .3 }); fillOnly(spline([[50, -36], [54, 0], [46, 6], [44, -24]]), PAL.hairB, { boil: .3 }); },
  });
  push(); translate(0, -48); rotate(P.hatTilt ?? -.06);
  shape(spline([[-92, 4], [-50, -6], [50, -6], [94, 2], [76, 12], [-76, 12]]), { fill: PAL.hatB, lw: LW });
  shape(spline([[-52, -2], [-48, -48], [-18, -60], [18, -52], [50, -46], [52, -2]]), { fill: PAL.hatB, lw: LW, shade: () => { fillOnly(rect(16, -70, 50, 80), PAL.hatBs, { boil: .3 }); fillOnly(rect(-60, -18, 120, 12), PAL.hatBand, { boil: .3 }); } });
  pop();
  if (P.sweat != null) { const u = P.sweat % 1; sweat(-46, -40 + u * 30, 1); sweat(52, -30 + ((u + .5) % 1) * 30, .8); }
  pop();
}
export function bandit(P) {
  const ner = P.nerv ?? 0, jit = ner ? (hash(Math.floor((P.t || 0) * 12) * 3.3) - .5) * 6 * ner : 0;
  const shake = ner ? (hash(Math.floor((P.t || 0) * 24) * 1.7) - .5) * 1.5 * ner : 0;
  rig({ ...P, x: P.x + jit, s: (P.s ?? 1) * .97, jitter: shake }, C_BA, {
    torso: hem => {
      fillOnly(spline([[-80, -470], [0, -452], [80, -470], [80, -456], [0, -438], [-80, -456]]), PAL.fringe, { boil: .3 });
      for (let i = 0; i < 13; i++) { const x = -60 + i * 10, y = -450 + Math.abs(x) * .2; stroke([[x, y], [x + 1, y + 16]], 2.5, { line: PAL.fringe }); }
      stroke([[2, -508], [2, hem]], FW); for (let i = 0; i < 4; i++) dot(-6, -420 + i * 30, 3, PAL.fringe);
    },
    collar: () => shape(spline([[-20, -516], [20, -516], [12, -496], [0, -486], [-12, -496]]), { fill: PAL.scarf, lw: FW }),
    front: hem => { shape(rr(-62, -312, 124, 16, 4), { fill: '#3b2416', lw: LW }); shape(ell(0, -304, 12, 10, 14), { fill: PAL.buckle, lw: FW }); holster(60, -296, P.gun); },
    head: banditHead,
  });
}

// —— MAS SALES (the user) ——
const C_SA = { skin: PAL.skM, skinS: PAL.skMs, top: PAL.navy, topS: PAL.navyS, sleeve: 'short', pipe: PAL.pipe, pant: PAL.chino, pantS: PAL.chinoS, shoe: 'sneaker', hemY: -262 };
export function salesHead(P) {
  push(); scale(HS);
  face({ turn: .3, lid: .12, ...P, mouth: { sm: .6, ...(P.mouth || {}) } }, {
    skin: PAL.skM, skinS: PAL.skMs, brow: PAL.hair,
    hairBack: () => {
      // short black hair, side part on his right, volume swept to the left; short sides
      shape(spline([[-50, -12], [-54, -42], [-40, -72], [-6, -86], [30, -82], [52, -62], [56, -30], [50, -10], [44, -34], [26, -48], [-4, -50], [-26, -46], [-40, -36], [-44, -14]]), {
        fill: PAL.hair, lw: LW, shade: () => fillOnly(spline([[-30, -80], [10, -84], [44, -66], [10, -70], [-20, -70]]), PAL.hairHi, { boil: .3 })
      });
      stroke(quad([-26, -80], [-22, -62], [-28, -48], 8), FW * .8, { line: '#5a5266' });
    },
  });
  pop();
}
export function sales(P) {
  rig(P, C_SA, {
    torso: hem => {
      fillOnly([[46, -340], [70, -350], [70, hem], [50, hem], [58, -300]], PAL.motif, { boil: .3 });
      fillOnly([[58, -320], [70, -326], [70, -280], [62, -280]], PAL.motif2, { boil: .3 });
      fillOnly([[-72, -330], [-52, -316], [-50, hem], [-72, hem]], PAL.motif, { boil: .3 });
      stroke([[3, -505], [3, hem]], FW, { line: '#0f2150' }); for (let i = 0; i < 4; i++) dot(-3, -470 + i * 50, 2.6, '#e8e4ff');
      shape(rr(-54, -462, 30, 34, 3), { lw: FW, line: '#0f2150' });
      text('DAIHATSU', 38, -476, { font: '800 9.5px "Baloo 2"', fill: '#f4f1ea' });
    },
    collar: () => {
      shape([[-24, -520], [0, -500], [-14, -480], [-34, -500]], { fill: PAL.navy, lw: FW });
      shape([[24, -520], [0, -500], [14, -480], [34, -500]], { fill: PAL.navy, lw: FW });
      for (const sx of [-1, 1]) { const pts = [[sx * 20, -512], [sx * 12, -450], [sx * 2, -410]]; stroke(pts, 6, { line: INK }); stroke(pts, 3.5, { line: PAL.lan, boil: .3 }); }
      dot(-14, -470, 2.5, PAL.lanP); dot(12, -480, 2.5, PAL.lanP);
      shape(rr(-13, -410, 26, 36, 3), { fill: '#ffffff', lw: FW, shade: () => { fillOnly(rect(-9, -404, 18, 10), '#8fb4e8', { boil: .2 }); fillOnly(rect(-9, -390, 18, 3), '#c9c9d6', { boil: .2 }); } });
    },
    head: salesHead,
  });
}

// —— Rocky (side view, faces right; origin at ground centre). Real scale: draw with s ≈ 2.2 next to the 600-unit people ——
export function rocky(P) {
  const f = P.face ?? 1, S_ = (P.s ?? 1);
  push(); translate(P.x, P.y || 0);
  if (P.shadow !== false) fillOnly(ell(0, 6, 330 * S_, 26, 40), 'rgba(20,18,60,.38)', { boil: .3 });
  scale(S_ * f * (P.sx ?? 1), S_ * (P.sq ?? 1));
  const wr = P.wheelRot || 0;
  shape(spline([[-318, -52], [-326, -150], [-300, -206], [-262, -258], [80, -266], [116, -256], [214, -176], [306, -158], [330, -120], [330, -56], [250, -40], [-250, -40]]), {
    fill: PAL.car, lw: 6, shade: () => {
      fillOnly(rect(-360, -120, 720, 30), PAL.carS, { boil: .3 });
      fillOnly(spline([[-300, -200], [100, -210], [220, -170], [300, -150], [300, -142], [100, -196], [-300, -188]]), PAL.carHi, { boil: .3 });
      fillOnly(rect(-360, -78, 720, 60), PAL.clad, { boil: .3 });
    }
  });
  shape([[-262, -236], [86, -246], [174, -180], [-252, -176]], {
    fill: PAL.glass, lw: 5, shade: () => {
      if (P.riders) {   // real-size heads inside (undo the car scale)
        const k = 1 / 2.2;
        push(); translate(-150, -150); scale(k); sheriffHead({ lid: .45, mouth: { sm: .5 }, look: [.6, 0], hatTip: P.hatBounce || 0 }); pop();
        push(); translate(-20, -152); scale(k); banditHead({ look: [.6, 0], grin: 1, brow: -.3, lid: .1 }); pop();
        if (P.riders !== 'cowboys') { push(); translate(105, -150); scale(k); salesHead({ turn: .9, happy: true, mouth: { sm: 1.2 } }); pop(); }
      }
      fillOnly([[-200, -250], [-150, -250], [-220, -160], [-270, -160]], 'rgba(255,255,255,.2)', { boil: .2 });
      fillOnly([[40, -250], [70, -250], [10, -160], [-20, -160]], 'rgba(255,255,255,.14)', { boil: .2 });
    }
  });
  stroke([[-60, -244], [-60, -176]], 10); stroke([[-200, -238], [-205, -176]], 8);
  shape(rr(-250, -280, 300, 12, 5), { fill: PAL.clad, lw: 4 });
  stroke([[-60, -176], [-62, -60]], 3.5); stroke([[176, -176], [168, -64]], 3.5);
  shape(rr(-110, -160, 34, 9, 4), { fill: PAL.clad, lw: 3.5 }); shape(rr(110, -160, 34, 9, 4), { fill: PAL.clad, lw: 3.5 });
  shape(spline([[160, -190], [196, -196], [200, -172], [168, -170]]), { fill: PAL.car, lw: 4 });
  shape(spline([[268, -160], [326, -146], [322, -132], [272, -142]]), { fill: '#fff6d0', lw: 4 });
  shape(rr(-326, -168, 22, 36, 6), { fill: '#a01018', lw: 4 });
  text('ROCKY', -10, -100, { font: '800 26px "Baloo 2"', fill: '#f1f1f4' });
  for (const wx of [-196, 200]) {
    shape(arc(wx, -50, 84, 80, Math.PI, TAU, 18).concat([[wx + 84, -40], [wx - 84, -40]]), { fill: PAL.clad, lw: 5 });
    shape(ell(wx, -38, 64, 64, 36), {
      fill: PAL.tire, lw: 6, shade: () => {
        fillOnly(ell(wx, -38, 40, 40, 28), PAL.rim, { boil: .2 });
        for (let k = 0; k < 5; k++) { const a = wr + k / 5 * TAU; stroke([[wx, -38], [wx + Math.cos(a) * 36, -38 + Math.sin(a) * 36]], 6, { line: PAL.rimS }); }
        dot(wx, -38, 8, PAL.rimS);
      }
    });
  }
  pop();
}

export function tumbleweed(x, y, r, rot) {
  push(); translate(x, y); rotate(rot);
  shape(ell(0, 0, r, r * .92, 26), { fill: 'rgba(196,160,110,.25)', lw: 4, line: '#c9a46c' });
  for (let i = 0; i < 7; i++) { const a = hash(i) * TAU; stroke(arc(Math.cos(a) * r * .3, Math.sin(a) * r * .3, r * .7, r * .55, a, a + 2.4, 10), 3.5, { line: '#c9a46c' }); }
  pop();
}
