// Efek cahaya & api untuk SigraSinematik (meniru video referensi):
// - Lamp: lampu menyala -> inti putih panas, bloom, garis flare horizontal, pantulan di lantai
// - Fire: semburan api knalpot (partikel di canvas, deterministik per frame) + asap + cahaya oranye
import React, { useLayoutEffect, useRef } from "react";
import { AbsoluteFill, interpolate, random } from "remotion";

export const W = 1080;
export const H = 1920;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export type Light = { x: number; y: number; c: string; size: number; at: number | null; hold: number; ground?: number };
export type FireSpec = { x: number; y: number; dir: number; size: number; bursts: number[][] };

const TINT: Record<string, { core: string; streak: string; glow: string }> = {
  white: { core: "255,255,255", streak: "190,220,255", glow: "235,240,255" },
  red: { core: "255,120,100", streak: "255,40,40", glow: "255,30,20" },
};

// intensitas lampu: mati -> menyala (overshoot) -> kedip -> menyala -> menetap
export const lampLevel = (l: Light, f: number) => {
  if (l.at === null) return l.hold * (0.95 + 0.05 * Math.sin(f * 0.35));
  return interpolate(f - l.at, [0, 1, 3, 4, 6, 16], [0, 1.3, 1.1, 0.35, 1.25, l.hold], clamp);
};

export const Lamp: React.FC<{ l: Light; f: number }> = ({ l, f }) => {
  const v = lampLevel(l, f);
  if (v <= 0.01) return null;
  const t = TINT[l.c] ?? TINT.white;
  const px = l.x * W;
  const py = l.y * H;
  const s = l.size;
  const streakW = s * 11 * Math.min(1, v);
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", pointerEvents: "none" }}>
      {/* bloom lebar */}
      <AbsoluteFill
        style={{
          opacity: Math.min(1, 0.55 * v),
          background: `radial-gradient(circle ${s * 6}px at ${px}px ${py}px, rgba(${t.glow},0.9), rgba(${t.glow},0.25) 30%, rgba(${t.glow},0) 100%)`,
        }}
      />
      {/* inti lampu putih panas */}
      <AbsoluteFill
        style={{
          opacity: Math.min(1, v),
          background: `radial-gradient(ellipse ${s * 1.3}px ${s}px at ${px}px ${py}px, rgba(255,255,255,1), rgba(${t.core},0.85) 40%, rgba(${t.core},0) 100%)`,
        }}
      />
      {/* flare horizontal (anamorphic streak) */}
      <div
        style={{
          position: "absolute",
          left: px - streakW / 2,
          top: py - s * 0.09,
          width: streakW,
          height: s * 0.18,
          opacity: Math.min(1, 0.85 * v),
          background: `linear-gradient(to right, rgba(${t.streak},0), rgba(${t.streak},0.9) 42%, rgba(255,255,255,1) 50%, rgba(${t.streak},0.9) 58%, rgba(${t.streak},0))`,
          filter: "blur(2px)",
        }}
      />
      <div
        style={{
          position: "absolute",
          left: px - streakW * 0.35,
          top: py - s * 0.35,
          width: streakW * 0.7,
          height: s * 0.7,
          opacity: Math.min(1, 0.3 * v),
          background: `radial-gradient(ellipse 50% 50% at 50% 50%, rgba(${t.streak},0.8), rgba(${t.streak},0))`,
        }}
      />
      {/* pantulan cahaya di lantai */}
      {l.ground ? (
        <AbsoluteFill
          style={{
            opacity: Math.min(1, 0.45 * v),
            background: `radial-gradient(ellipse ${s * 3.2}px ${s * 1.1}px at ${px}px ${py + l.ground * H}px, rgba(${t.glow},0.8), rgba(${t.glow},0) 100%)`,
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ api
// selubung semburan: naik cepat, berdenyut, padam
const burstEnv = (b: number[], t: number) => {
  const [at, len] = b;
  const u = t - at;
  if (u < 0 || u > len + 6) return 0;
  const shape = interpolate(u, [0, 2, len, len + 6], [0, 1, 0.8, 0], clamp);
  return shape * (0.8 + 0.2 * Math.sin(u * 2.3));
};
export const fireEnv = (fs: FireSpec | undefined, f: number) => (fs ? Math.max(0, ...fs.bursts.map((b) => burstEnv(b, f))) : 0);

const RATE = 40; // partikel per frame

// warna menurut umur partikel: putih panas -> kuning -> oranye -> merah tua
const COL = (u: number): string => {
  if (u < 0.08) return "255,235,190";
  if (u < 0.32) return "255,150,40";
  if (u < 0.68) return "255,85,15";
  return "170,30,5";
};

const blob = (ctx: CanvasRenderingContext2D, x: number, y: number, r: number, c: string, a: number, mid = 0.55) => {
  if (r <= 0.5 || a <= 0.003) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(${c},${a})`);
  g.addColorStop(0.45, `rgba(${c},${a * mid})`);
  g.addColorStop(1, `rgba(${c},0)`);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
};

export const Fire: React.FC<{ spec: FireSpec; f: number }> = ({ spec, f }) => {
  const fire = useRef<HTMLCanvasElement>(null);
  const smoke = useRef<HTMLCanvasElement>(null);
  const S = spec.size;
  const nx = spec.x * W;
  const ny = spec.y * H;
  const env = fireEnv(spec, f);

  useLayoutEffect(() => {
    const cf = fire.current?.getContext("2d");
    const cs = smoke.current?.getContext("2d");
    if (!cf || !cs) return;
    cf.clearRect(0, 0, W, H);
    cs.clearRect(0, 0, W, H);
    // blending normal: partikel muda (kuning) digambar di atas yang tua (merah) -> warna api tetap terjaga
    cf.globalCompositeOperation = "source-over";

    spec.bursts.forEach((b, bi) => {
      const [at, len] = b;
      const n = Math.round(len * RATE);
      for (let j = 0; j < n; j++) {
        const e = at + j / RATE;
        if (e > f) break;
        const a = f - e;
        const k = `${bi}-${j}`;
        const strength = burstEnv(b, e);

        // ---- asap abu tipis: muncul belakangan, membesar & naik pelan
        if (j % 4 === 0 && a > 3 && a < 30) {
          const su = (a - 3) / 27;
          const sang = spec.dir + (random(`sa${k}`) - 0.5) * 1.4;
          const sd = (7 + 6 * random(`sv${k}`)) * S * Math.min(a, 12);
          const sx = nx + Math.cos(sang) * sd + Math.sin(a * 0.2 + j) * 6 * S;
          const sy = ny + Math.sin(sang) * sd - a * a * 0.18 * S;
          const sr = (34 + 40 * random(`sr${k}`)) * S * (0.7 + 1.4 * su);
          blob(cs, sx, sy, sr, "58,52,50", 0.1 * Math.sin(Math.PI * su) * strength, 0.6);
        }

        // ---- percikan bunga api: kecil, terbang jauh, jatuh
        if (j % 9 === 0 && a < 14) {
          const u = a / 14;
          const ang = spec.dir + (random(`ka${k}`) - 0.5) * 1.8;
          const v = (22 + 22 * random(`kv${k}`)) * S;
          const px = nx + Math.cos(ang) * v * a * (1 - 0.3 * u);
          const py = ny + Math.sin(ang) * v * a * (1 - 0.3 * u) + a * a * 0.5 * S;
          blob(cf, px, py, 2.2 * S, "255,215,130", (1 - u) * 0.95, 0.9);
        }

        // ---- lidah api
        const life = 5 + 6 * random(`l${k}`);
        if (a > life || strength <= 0.02) continue;
        const u = a / life;
        const ang = spec.dir + (random(`a${k}`) - 0.5) * 1.5;
        const v = (6 + 16 * random(`v${k}`)) * S;
        const dist = v * a * (1 - 0.4 * u);
        const perp = Math.sin(a * 1.4 + random(`p${k}`) * 6.28) * a * 2.2 * S;
        const px = nx + Math.cos(ang) * dist - Math.sin(ang) * perp;
        const py = ny + Math.sin(ang) * dist + Math.cos(ang) * perp - a * a * 0.45 * S;
        const r = (7 + 20 * random(`r${k}`)) * S * (0.6 + 1.6 * u) * strength;
        const c = random(`c${k}`) < 0.05 && u < 0.4 ? "160,130,255" : COL(u);
        blob(cf, px, py, r, c, Math.pow(1 - u, 0.8) * 0.55, 0.7);
        if (a < 1.5) blob(cf, px, py, r * 0.35, "255,245,225", 0.25 * (1 - a / 1.5), 0.7); // titik paling panas
      }
    });

    // inti panas di mulut knalpot
    if (env > 0.02) {
      cf.globalCompositeOperation = "lighter";
      blob(cf, nx, ny, 24 * S * env, "255,250,235", 0.75 * env, 0.7);
      blob(cf, nx, ny, 60 * S * env, "255,150,50", 0.3 * env, 0.5);
    }
  }, [f, spec, S, nx, ny, env]);

  const canvasStyle: React.CSSProperties = { position: "absolute", inset: 0, width: "100%", height: "100%" };
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {/* cahaya oranye menerangi bodi & lantai */}
      {env > 0.01 && (
        <AbsoluteFill
          style={{
            mixBlendMode: "screen",
            opacity: Math.min(1, env),
            background: `radial-gradient(ellipse ${560 * S}px ${420 * S}px at ${nx}px ${ny}px, rgba(255,140,50,0.55), rgba(255,90,20,0.18) 45%, rgba(255,80,20,0) 100%)`,
          }}
        />
      )}
      <canvas ref={smoke} width={W} height={H} style={{ ...canvasStyle, filter: "blur(8px)" }} />
      <canvas ref={fire} width={W} height={H} style={{ ...canvasStyle, mixBlendMode: "screen", filter: "blur(1.2px)" }} />
    </AbsoluteFill>
  );
};
