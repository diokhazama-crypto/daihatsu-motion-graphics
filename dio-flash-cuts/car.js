// The Gran Max drawn in code: a small cab-over pick-up built from flat faces (metres), projected two ways
// (front three-quarter low angle, pure side profile), plus a frame-filling headlamp. Hard-edged polygons only:
// off-white body, one shadow tone, black line, red accents. Returns canvases with transparent backgrounds.
const RED = '#d4162b', BLK = '#0a0a0c', WHT = '#f2efe8', PALE = '#cfcac0', DK = '#26262a', GLASS = '#1b1b1f';
const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };

const L = 4.2, Z = .83;                       // length, half width
const circ = (x0, y0, r, z, n = 28) => Array.from({ length: n }, (_, i) => [x0 + r * Math.cos(i / n * 2 * Math.PI), y0 + r * Math.sin(i / n * 2 * Math.PI), z]);
function wheel(P, x0) {
  P.push({ p: circ(x0, .36, .42, Z + .01), f: BLK });             // arch
  P.push({ p: circ(x0, .33, .33, Z + .02), f: BLK });             // tyre
  P.push({ p: circ(x0, .33, .19, Z + .03), f: DK, s: 1 });
  P.push({ p: circ(x0, .33, .08, Z + .04), f: PALE, s: 1 });
}
function parts(view) {
  const P = [];
  // chassis and bed
  P.push({ p: [[1.4, .30, Z - .08], [4.0, .30, Z - .08], [4.0, .50, Z - .08], [1.4, .50, Z - .08]], f: BLK });
  P.push({ p: [[1.6, .48, Z], [L, .48, Z], [L, 1.02, Z], [1.6, 1.02, Z]], f: WHT, s: 1 });
  P.push({ p: [[1.6, .94, Z + .005], [L, .94, Z + .005], [L, 1.02, Z + .005], [1.6, 1.02, Z + .005]], f: PALE, s: 1 });
  for (const x of [2.5, 3.4]) P.push({ p: [[x - .02, .5, Z + .006], [x + .02, .5, Z + .006], [x + .02, .94, Z + .006], [x - .02, .94, Z + .006]], f: BLK });
  P.push({ p: [[L - .06, .62, Z + .007], [L, .62, Z + .007], [L, .86, Z + .007], [L - .06, .86, Z + .007]], f: RED });     // tail lamp
  P.push({ p: [[1.6, .64, Z + .008], [L - .06, .64, Z + .008], [L - .06, .70, Z + .008], [1.6, .70, Z + .008]], f: RED });
  wheel(P, 3.3);
  // cab side
  P.push({ p: [[0, .42, Z], [1.5, .42, Z], [1.5, 1.86, Z], [.18, 1.9, Z], [0, 1.1, Z]], f: WHT, s: 1 });
  P.push({ p: [[.14, 1.16, Z + .005], [1.28, 1.16, Z + .005], [1.28, 1.74, Z + .005], [.27, 1.76, Z + .005]], f: GLASS });
  P.push({ p: [[.16, 1.2, Z + .006], [.5, 1.2, Z + .006], [.36, 1.7, Z + .006], [.28, 1.72, Z + .006]], f: DK });          // one hard reflection band
  P.push({ p: [[1.33, .5, Z + .005], [1.37, .5, Z + .005], [1.37, 1.8, Z + .005], [1.33, 1.8, Z + .005]], f: BLK });
  P.push({ p: [[1.12, 1.04, Z + .006], [1.28, 1.04, Z + .006], [1.28, 1.08, Z + .006], [1.12, 1.08, Z + .006]], f: BLK });
  P.push({ p: [[0, .64, Z + .008], [1.5, .64, Z + .008], [1.5, .70, Z + .008], [0, .70, Z + .008]], f: RED });
  P.push({ p: [[.2, .44, Z + .006], [1.5, .44, Z + .006], [1.5, .52, Z + .006], [.2, .52, Z + .006]], f: PALE });          // shadow step
  wheel(P, .78);
  if (view === 'front') {
    // front face, raked above the belt line
    P.push({ p: [[0, .42, -Z], [0, .42, Z], [0, 1.1, Z], [.18, 1.9, Z], [.18, 1.9, -Z], [0, 1.1, -Z]], f: PALE, s: 1 });
    P.push({ p: [[-.002, 1.18, -.76], [-.002, 1.18, .76], [.15, 1.82, .76], [.15, 1.82, -.76]], f: GLASS, s: 1 });
    P.push({ p: [[-.004, 1.22, .1], [-.004, 1.22, .32], [.13, 1.78, .0], [.13, 1.78, -.2]], f: DK });
    P.push({ p: [[-.004, .70, -.46], [-.004, .70, .46], [-.004, .90, .46], [-.004, .90, -.46]], f: BLK });                // grille
    for (const s of [-1, 1]) {
      P.push({ p: [[-.006, .70, s * .50], [-.006, .70, s * .80], [-.006, .92, s * .80], [-.006, .92, s * .50]], f: WHT, s: 1 });   // lamp
      P.push({ p: [[-.008, .75, s * .56], [-.008, .75, s * .68], [-.008, .87, s * .68], [-.008, .87, s * .56]], f: PALE, s: 1 });
      P.push({ p: [[-.008, .94, s * .52], [-.008, .94, s * .80], [-.008, 1.0, s * .80], [-.008, 1.0, s * .52]], f: RED });
    }
    P.push({ p: [[-.05, .34, -.86], [-.05, .34, .86], [-.05, .50, .86], [-.05, .50, -.86]], f: BLK });                  // bumper
    P.push({ p: [[-.06, .40, -.2], [-.06, .40, .2], [-.06, .46, .2], [-.06, .46, -.2]], f: DK });
  } else {
    P.push({ p: [[-.05, .34, Z + .01], [.05, .34, Z + .01], [.05, .50, Z + .01], [-.05, .50, Z + .01]], f: BLK });
    P.push({ p: [[-.01, .70, Z + .01], [.05, .70, Z + .01], [.05, .92, Z + .01], [-.01, .92, Z + .01]], f: WHT, s: 1 });
  }
  P.push({ p: [[.22, 1.3, Z + .05], [.3, 1.3, Z + .18], [.3, 1.55, Z + .18], [.22, 1.55, Z + .05]], f: BLK });   // mirror
  return P;
}

function lookAt(C, T, F) {
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const nrm = a => { const l = Math.hypot(...a); return a.map(v => v / l); };
  const f = nrm(sub(T, C)), r = nrm([-f[2], 0, f[0]]), u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
  return p => { const d = sub(p, C), zc = dot(d, f); return [F * dot(d, r) / zc, -F * dot(d, u) / zc]; };
}

function render(view, width) {
  const proj = view === 'front' ? lookAt([-3.4, .5, 3.4], [1.6, 1.0, 0], 1) : p => [p[0], -p[1]];
  const P = parts(view).map(o => ({ ...o, q: o.p.map(proj) }));
  const xs = P.flatMap(o => o.q.map(q => q[0])), ys = P.flatMap(o => o.q.map(q => q[1]));
  const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
  const pad = 12, s = (width - 2 * pad) / (x1 - x0), c = mk(width, Math.ceil((y1 - y0) * s + 2 * pad)), g = c.getContext('2d');
  g.lineJoin = 'round'; g.lineWidth = Math.max(3, width / 300);
  for (const o of P) {
    g.beginPath(); o.q.forEach(([x, y], i) => { const X = pad + (x - x0) * s, Y = pad + (y - y0) * s; i ? g.lineTo(X, Y) : g.moveTo(X, Y); }); g.closePath();
    g.fillStyle = o.f; g.fill(); if (o.s) { g.strokeStyle = BLK; g.stroke(); }
  }
  return c;
}

// frame-filling headlamp: body panel, black grille edge, the lamp with one hard shadow tone, red indicator
function lamp(W = 1080, H = 1920) {
  const c = mk(W, H), g = c.getContext('2d');
  const rr = (x, y, w, h, r) => { g.beginPath(); g.roundRect(x, y, w, h, r); };
  g.fillStyle = WHT; g.fillRect(0, 0, W, H);
  g.fillStyle = PALE; g.beginPath(); g.moveTo(0, 1500); g.lineTo(W, 1260); g.lineTo(W, H); g.lineTo(0, H); g.fill();
  g.fillStyle = BLK; g.fillRect(0, 1560, W, 120);
  for (let i = 0; i < 5; i++) { g.fillStyle = DK; g.fillRect(0, 1580 + i * 20, W, 6); }
  g.save(); g.translate(W / 2, 820); g.rotate(-.06);
  g.fillStyle = BLK; rr(-560, -560, 1120, 1080, 120); g.fill();
  g.fillStyle = RED; rr(-520, -520, 1040, 170, 60); g.fill();
  g.fillStyle = WHT; rr(-520, -320, 1040, 800, 80); g.fill();
  g.fillStyle = PALE; g.beginPath(); g.moveTo(-520, 200); g.lineTo(520, -60); g.lineTo(520, 400); g.quadraticCurveTo(520, 480, 440, 480); g.lineTo(-440, 480); g.quadraticCurveTo(-520, 480, -520, 400); g.fill();
  g.strokeStyle = BLK; g.lineWidth = 8;
  for (const r of [300, 220]) { g.beginPath(); g.arc(-40, 80, r, 0, Math.PI * 2); g.stroke(); }
  g.fillStyle = WHT; g.beginPath(); g.arc(-40, 80, 140, 0, Math.PI * 2); g.fill(); g.stroke();
  g.fillStyle = BLK; g.beginPath(); g.arc(-40, 80, 44, 0, Math.PI * 2); g.fill();
  g.lineWidth = 6; for (let i = -3; i <= 3; i++) { g.beginPath(); g.moveTo(-500, -300 + 0); g.moveTo(-40 + i * 120, -300); g.lineTo(-40 + i * 120, -230); g.stroke(); }
  g.restore();
  return c;
}

export function buildCar() {
  return { front: render('front', 1400), side: render('side', 1600), lamp: lamp() };
}
