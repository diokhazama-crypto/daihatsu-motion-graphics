import { W, H, init, frame, g, reset, push, pop, translate, scale, fillOnly, rect, text, screenRect } from './toon.js';
import { sheriff, bandit, sales, rocky, sheriffHead, banditHead, salesHead } from './chars.js';
import { street, portal } from './world.js';
init(document.getElementById('c'));
await document.fonts.load('800 40px "Baloo 2"'); await document.fonts.load('40px Rye');
const cam = (cx, cy, z) => { reset(); translate(W / 2, H / 2); scale(z); translate(-cx, -cy); };
window.DUR = 1;
window.render = t => {
  frame(t); g.fillStyle = '#000'; g.fillRect(0, 0, W, H);
  g.save(); g.beginPath(); g.rect(0, 0, W, 1150); g.clip();
  cam(0, -520, .82);
  street(t); portal(0, -430, 210, t, { open: 1 });
  rocky({ x: -40, riders: false });
  bandit({ x: -380, face: 1, t, nerv: .6, grin: 1, sweat: t, armR: { h: [36, 120], bend: 10 } });
  sheriff({ x: 380, face: -1, lid: .5, gun: 0 });
  sales({ x: 120, turn: .2, armR: { h: [40, -120], bend: -20, end: 'thumb' } });
  g.restore();
  reset(); fillOnly(rect(0, 1150, W, 770), '#f3ead8', { boil: 0 });
  const heads = [
    [sheriffHead, { lid: .5 }, 'SHERIFF datar'], [sheriffHead, { lid: .62, look: [-.8, 0], browIn: 1, mouth: { o: .5 } }, 'SHERIFF melirik'], [banditHead, { grin: 1, t, look: [.3, 0] }, 'BANDIT gugup'],
    [banditHead, { eyeS: 1.25, pupil: 2.5, brow: 1.4, mouth: { o: .8 } }, 'BANDIT panik'], [salesHead, { turn: .1, mouth: { o: .55 } }, 'SALES bicara'], [salesHead, { turn: .5, happy: true, mouth: { sm: 1.1 } }, 'SALES senang'],
  ];
  heads.forEach(([fn, P, lab], i) => {
    const cx = 180 + (i % 3) * 360, cy = 1370 + Math.floor(i / 3) * 330;
    reset(); translate(cx, cy); scale(1.1); fn(P);
    reset(); text(lab, cx, cy + 150, { font: '800 30px "Baloo 2"', fill: '#1b1422' });
  });
};
window.READY = true;
