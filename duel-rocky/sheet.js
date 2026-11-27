// Model sheet (render with --q 'sheet=1'): full-body line-up, real-scale Rocky, and expressions at close-up size
import { W, H, init, frame, g, reset, push, pop, translate, scale, fillOnly, stroke, rect, text } from './toon.js';
import { sheriff, bandit, sales, rocky, sheriffHead, banditHead, salesHead } from './chars.js';
init(document.getElementById('c'));
await document.fonts.load('800 40px "Baloo 2"'); await document.fonts.load('40px Rye');
const cam = (cx, cy, z) => { reset(); translate(W / 2, H / 2); scale(z); translate(-cx, -cy); };
window.DUR = 1;
window.render = t => {
  frame(t); reset(); fillOnly(rect(0, 0, W, H), '#f3ead8', { boil: 0 });
  // line-up with a height grid (one head = 80 units)
  cam(0, -420, 1.25);
  for (let k = 0; k <= 8; k++) stroke([[-430, -k * 80], [430, -k * 80]], 1.5, { line: 'rgba(0,0,0,.12)', boil: 0 });
  bandit({ x: -280, face: 1, t, nerv: .4, grin: 1, sweat: t });
  sales({ x: 0, armR: { h: [60, -40], end: 'thumb' } });
  sheriff({ x: 280, face: -1, lid: .45 });
  // expressions
  const heads = [
    [sheriffHead, { lid: .45 }, 'Sheriff datar'], [sheriffHead, { lid: .6, look: [-.8, 0], browIn: 1, mouth: { o: .4 } }, 'Sheriff melirik'], [banditHead, { grin: 1, look: [.3, 0] }, 'Bandit gugup'],
    [banditHead, { eyeS: 1.4, pupil: 1, brow: 1.4, mouth: { o: .8 } }, 'Bandit panik'], [salesHead, { turn: .2, mouth: { o: .55 } }, 'Sales bicara'], [salesHead, { turn: .4, happy: true, mouth: { sm: 1.2 } }, 'Sales senang'],
  ];
  heads.forEach(([fn, P, lab], i) => {
    const cx = 180 + (i % 3) * 360, cy = 200 + Math.floor(i / 3) * 270;
    reset(); translate(cx, cy); scale(2.1); fn(P);
    reset(); text(lab, cx, cy + 105, { font: '800 28px "Baloo 2"', fill: '#1b1422' });
  });
};
window.READY = true;
