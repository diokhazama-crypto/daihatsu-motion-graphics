// world.js — the night street (1887), the portal (the only thing that glows), and the dawn world of the end card (2026)
// World units: ground line at y = 0, the bank centred at x ≈ 80. Characters stand on y = 0.
import { clamp, lerp, hash, vnoise, TAU } from '/core/lib.js';
import { INK, push, pop, translate, rotate, scale, shape, fillOnly, stroke, ell, arc, spline, rr, rect, dot, text, bands } from './toon.js';

export const NIGHT = {
  sky: ['#0b1033', '#111a48', '#18245c', '#1f2e6c'], star: '#e9e6ff', moon: '#f3ecd0', moonS: '#d9cfae',
  far: '#141c4a', brick: '#4b3f7e', brickS: '#3b3168', brickL: '#3a3070', trim: '#8b86c8', wood: '#3d4a86', woodS: '#2f3a70', woodL: '#283262',
  win: '#1a2150', winHi: '#5d6ab0', door: '#1b1a3a', sign: '#2a2f62', signT: '#e9dfc0',
  walk: '#3a3f78', walkL: '#2a2e60', road: ['#4f5296', '#585ca0', '#6266aa', '#6b70b2'], pebble: '#41437e', pebbleHi: '#8b8fcc',
};
const PORTAL = { wash: 'rgba(255,70,190,.13)', wash2: 'rgba(255,70,190,.17)', rim: '#ff3fb4', inner: '#ff7ccc', a1: '#ffc4e8', a2: '#c4107f', core: '#ffe2f4', spark: '#ffb0e0' };

// —— a building with a false front ——
function windowPane(x, y, w, h, lit = 0) {
  shape(rect(x, y, w, h), { fill: NIGHT.win, lw: 5, shade: () => { fillOnly([[x, y + h], [x + w * .5, y], [x + w * .8, y], [x + w * .3, y + h]], 'rgba(120,130,210,.25)', { boil: .2 }); } });
  stroke([[x + w / 2, y], [x + w / 2, y + h]], 4); stroke([[x, y + h / 2], [x + w, y + h / 2]], 4);
  shape(rect(x - 8, y + h, w + 16, 12), { fill: NIGHT.trim, lw: 4 });
}
function bank() {
  // brick façade x -300..460, stepped pediment
  const x0 = -300, x1 = 460;
  shape([[x0, 0], [x0, -880], [x0 + 60, -880], [x0 + 60, -930], [x1 - 60, -930], [x1 - 60, -880], [x1, -880], [x1, 0]], {
    fill: NIGHT.brick, lw: 7, shade: () => {
      fillOnly(rect(x1 - 120, -940, 140, 960), NIGHT.brickS, { boil: .3 });
      for (let r = 0; r < 34; r++) { const y = -880 + r * 26; stroke([[x0, y], [x1, y]], 2.5, { line: NIGHT.brickL, boil: .2 }); for (let c = 0; c < 12; c++) { const x = x0 + (c + (r % 2) * .5) * 68; stroke([[x, y], [x, y + 26]], 2.5, { line: NIGHT.brickL, boil: .2 }); } }
    }
  });
  // cornice
  shape(rect(x0 - 20, -880, x1 - x0 + 40, 26), { fill: NIGHT.trim, lw: 6 });
  shape(rect(x0 - 10, -600, x1 - x0 + 20, 18), { fill: NIGHT.trim, lw: 5 });
  // sign
  shape(rect(-170, -840, 500, 110), { fill: NIGHT.sign, lw: 6, shade: () => fillOnly(rect(-170, -760, 500, 30), '#22264f', { boil: .3 }) });
  text('FIRST BANK', 80, -784, { font: '400 66px Rye', fill: NIGHT.signT });
  // upper windows
  for (const wx of [-240, -80, 160, 320]) windowPane(wx, -720, 90, 120);
  // porch roof + columns
  shape([[x0 - 30, -420], [x1 + 30, -420], [x1 + 10, -380], [x0 - 10, -380]], { fill: NIGHT.wood, lw: 6, shade: () => fillOnly(rect(x0 - 40, -396, 900, 20), NIGHT.woodS, { boil: .3 }) });
  for (const cx of [-270, -120, 280, 430]) shape(rect(cx - 12, -380, 24, 380), { fill: NIGHT.trim, lw: 5, shade: () => fillOnly(rect(cx + 2, -390, 14, 400), '#6f6ab0', { boil: .3 }) });
  // door + lower windows
  shape(rect(30, -300, 120, 300), { fill: NIGHT.door, lw: 6, shade: () => { stroke([[90, -300], [90, 0]], 4); fillOnly(rect(36, -290, 48, 90), '#2a2c5a', { boil: .2 }); fillOnly(rect(96, -290, 48, 90), '#2a2c5a', { boil: .2 }); } });
  shape(rect(10, -322, 160, 22), { fill: NIGHT.trim, lw: 5 });
  for (const wx of [-220, 230]) windowPane(wx, -310, 110, 170);
}
function falseFront(x0, x1, h, label, { col = NIGHT.wood, colS = NIGHT.woodS, step = true, sign = true } = {}) {
  const pts = step ? [[x0, 0], [x0, -h], [x0 + 60, -h], [x0 + 60, -h - 50], [x1 - 60, -h - 50], [x1 - 60, -h], [x1, -h], [x1, 0]] : [[x0, 0], [x0, -h], [x1, -h], [x1, 0]];
  shape(pts, { fill: col, lw: 7, shade: () => { fillOnly(rect(x1 - 80, -h - 60, 100, h + 80), colS, { boil: .3 }); for (let x = x0 + 34; x < x1; x += 34) stroke([[x, -h - 50], [x, 0]], 2.5, { line: NIGHT.woodL, boil: .2 }); } });
  if (sign) { shape(rect((x0 + x1) / 2 - 170, -h + 30, 340, 80), { fill: NIGHT.sign, lw: 6 }); text(label, (x0 + x1) / 2, -h + 72, { font: '400 44px Rye', fill: NIGHT.signT }); }
  shape([[x0 - 20, -380], [x1 + 20, -380], [x1, -350], [x0, -350]], { fill: NIGHT.woodS, lw: 6 });
  for (const cx of [x0 + 20, x1 - 20]) shape(rect(cx - 10, -350, 20, 350), { fill: NIGHT.trim, lw: 5 });
  windowPane(x0 + 60, -h + 150, 90, 110); windowPane(x1 - 150, -h + 150, 90, 110);
}
// —— the street ——
export function street(t, { far = true } = {}) {
  bands(NIGHT.sky, -4400, -150);
  // stars (twinkle on twos)
  const tq = Math.floor(t * 12);
  for (let i = 0; i < 110; i++) { const x = -1900 + hash(i * 3.1) * 3800, y = -4300 + hash(i * 5.7) * 2900, tw = hash(i + tq * .37) > .85 ? 1.6 : 1; dot(x, y, (2 + hash(i * 9.1) * 2.4) * tw, NIGHT.star); }
  // moon (flat, no glow)
  push(); translate(-560, -2150); shape(ell(0, 0, 110, 110, 40), { fill: NIGHT.moon, lw: 6, shade: () => { fillOnly(ell(40, 20, 86, 98, 30), NIGHT.moonS, { boil: .3 }); dot(-30, -20, 14, NIGHT.moonS); dot(10, 50, 9, NIGHT.moonS); } }); pop();
  push(); scale(2.2);
  // far silhouettes: mesas
  if (far) fillOnly(spline([[-1600, -300], [-1300, -380], [-1100, -560], [-900, -560], [-760, -380], [-200, -380], [600, -420], [760, -620], [980, -640], [1100, -420], [1600, -400], [1600, 0], [-1600, 0]]), NIGHT.far, { boil: .3 });
  // buildings
  falseFront(-940, -330, 640, 'GUNSMITH');
  falseFront(490, 1100, 600, 'SALOON', { col: '#40508e', colS: '#32407a' });
  falseFront(1120, 1600, 520, '', { sign: false, step: false });
  falseFront(-1500, -960, 520, '', { sign: false, step: false, col: '#40508e', colS: '#32407a' });
  bank();
  pop();
  push(); scale(2.2, 1);
  // boardwalk
  shape(rect(-1600, -34, 3200, 34), { fill: NIGHT.walk, lw: 6, shade: () => { for (let x = -1600; x < 1600; x += 60) stroke([[x, -34], [x, 0]], 3, { line: NIGHT.walkL, boil: .2 }); } });
  pop();
  // road (flat colour bands toward the camera)
  bands(NIGHT.road, 0, 1700, -2600, 2600);
  for (let i = 0; i < 90; i++) { const x = -2000 + hash(i * 7.3) * 4000, y = 30 + Math.pow(hash(i * 2.9), 1.4) * 1600, r = 4 + y * .012; fillOnly(ell(x, y, r * 1.4, r * .8, 10), NIGHT.pebble, { boil: .3 }); fillOnly(ell(x - r * .3, y - r * .3, r * .5, r * .3, 8), NIGHT.pebbleHi, { boil: .2 }); }
  for (let i = 0; i < 12; i++) { const x = -1800 + hash(i * 1.9) * 3600, y = 80 + hash(i * 4.4) * 1300; stroke([[x - 10, y], [x - 2, y - 26], [x + 4, y - 4], [x + 12, y - 22], [x + 10, y]], 4, { line: '#7b6f9a', closed: false }); }
}

// —— the portal: vertical oval, pink, the only glowing thing ——
export function portal(cx, cy, r, t, { open = 1, sx = .78, spin = 1, washScreen = null } = {}) {
  if (open <= .001) return;
  const R = r * open;
  push(); translate(cx, cy); scale(sx, 1);
  fillOnly(ell(0, 0, R * 1.6, R * 1.5, 48), PORTAL.wash, { boil: .6 });
  fillOnly(ell(0, 0, R * 1.3, R * 1.24, 48), PORTAL.wash2, { boil: .6 });
  const rim = [], N = 22;
  for (let i = 0; i < N; i++) { const a = i / N * TAU, k = 1 + .08 * (vnoise(i * 1.7 + t * 3) - .5) * 2 + .05 * Math.sin(a * 5 + t * 6); rim.push([Math.cos(a) * R * k, Math.sin(a) * R * k]); }
  shape(spline(rim), {
    fill: PORTAL.rim, lw: 8, shade: () => {
      fillOnly(ell(0, 0, R * .9, R * .9, 40), PORTAL.inner, { boil: .3 });
      for (let k = 0; k < 5; k++) {
        const pts = [], pts2 = [];
        for (let j = 0; j <= 22; j++) { const u = j / 22, rr_ = R * (1 - u) * .95, a = k / 5 * TAU + u * 3.6 + t * 2.6 * spin; pts.push([Math.cos(a) * rr_, Math.sin(a) * rr_]); const a2 = a + .55 * (1 - u * .7); pts2.push([Math.cos(a2) * rr_, Math.sin(a2) * rr_]); }
        fillOnly([...pts, ...pts2.reverse()], k % 2 ? PORTAL.a1 : PORTAL.a2, { boil: .4 });
      }
      fillOnly(ell(0, 0, R * .3, R * .3, 24), PORTAL.core, { boil: .5 });
      fillOnly(ell(0, 0, R * .14, R * .14, 16), '#ffffff', { boil: .5 });
    }
  });
  for (let i = 0; i < 12; i++) { const a = hash(i) * TAU + t * (1.5 + hash(i + 4) * 2), d = R * (1.05 + .25 * ((t * .8 + hash(i + 9)) % 1)); dot(Math.cos(a) * d, Math.sin(a) * d, 5 + hash(i + 2) * 4, i % 3 ? PORTAL.spark : '#ffffff'); }
  pop();
}

// —— the dawn world of the end card (2026): warm, suspiciously calm ——
export const DAWN = { sky: ['#ff9a5a', '#ffb46b', '#ffca85', '#ffdea6'], sun: '#fff1c8', ground: ['#e6cfa6', '#eed9b3', '#f3e2c0', '#f7ead0'], hill: '#d98a5a', hillS: '#c4744a', line: '#c9a87a' };
export function dawn(t) {
  bands(DAWN.sky, -2400, -100);
  shape(ell(0, -700, 260, 260, 48), { fill: DAWN.sun, lw: 7 });
  for (let i = 0; i < 6; i++) stroke([[-700, -1000 - i * 120], [700, -1000 - i * 120]], 3, { line: 'rgba(255,255,255,.25)', boil: .3 });
  fillOnly(spline([[-1400, -200], [-900, -360], [-500, -300], [-100, -420], [300, -300], [700, -380], [1400, -220], [1400, 0], [-1400, 0]]), DAWN.hill, { boil: .3 });
  fillOnly(spline([[-1400, -100], [-600, -180], [200, -120], [900, -200], [1400, -120], [1400, 0], [-1400, 0]]), DAWN.hillS, { boil: .3 });
  bands(DAWN.ground, 0, 1500, -1700, 1700);
  for (let i = 0; i < 5; i++) stroke([[-1500, 60 + i * i * 40], [1500, 60 + i * i * 40]], 3, { line: DAWN.line, boil: .3 });
}
