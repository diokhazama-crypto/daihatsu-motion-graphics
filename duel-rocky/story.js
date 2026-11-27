// story.js — single source of truth: voice start times, shots, key beats, music cues (read by main.js, mix.py, score.py via events.json)
export const DUR = 50.6;
export const q = t => Math.floor(t * 12 + 1e-6) / 12;      // drawing time on twos (12 fps)
export const VO = { s1: .7, b1: 4.35, m1: 12.0, b2: 15.65, m2: 16.75, m3: 20.75, m4: 25.75, b3: 30.75, s2: 32.75, m5: 35.7, m6: 45.3 };
export const SHOTS = [
  ['wide1', 0], ['cuSher', 2.4], ['cuBand', 4.2], ['hands', 6.6], ['eyes', 8.1], ['portal', 9.6], ['arrive', 11.6], ['cuBand2', 15.6],
  ['cuSales', 16.6], ['snap', 20.6], ['rocky', 25.6], ['cuBand3', 30.6], ['cuSher2', 32.6], ['cuSales2', 35.6], ['pause', 37.1], ['leave', 39.6], ['end', 44.6],
];
export function shotAt(t) { let s = SHOTS[0]; for (const x of SHOTS) if (t >= x[1]) s = x; const i = SHOTS.indexOf(s); return { id: s[0], t0: s[1], t1: (SHOTS[i + 1] || [0, DUR])[1] }; }
// key beats (seconds)
export const K = {
  whip1: 7.3, whip2: 8.75, boom: 9.6, land: 11.85, thumb: 12.35, shake2: 16.0, card: 17.4, snap: 23.55, carLand: 24.1, honk: 24.6, irit: 29.2,
  glare: 32.8, toSales: 34.2, thumb2: 35.75, nod: 38.5, relax: 38.9, engine: 39.7, hop: 40.0, riders: 40.6, carHop: 41.3, suck0: 41.7, suck1: 42.3,
  close0: 42.35, close1: 42.75, weed0: 42.9, weed1: 44.5, title: 44.6, stinger: 49.8,
};
// music sections: [id, start, end, bpm]; the ends are hard cuts (silences)
export const CUES = [['standoff', 0, 6.6, 100], ['sales', 11.6, 24.1, 120], ['rocky', 24.1, 37.1, 120], ['finale', 39.7, 50.6, 120]];
// silences (music and reverb tails cut): [start, end]
export const SILENCE = [[6.6, 9.6], [37.1, 39.7]];
