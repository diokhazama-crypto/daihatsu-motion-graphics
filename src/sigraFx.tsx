// Efek cahaya untuk SigraSinematik (meniru video referensi):
// Lamp: lampu menyala -> inti putih panas, bloom, garis flare horizontal, pantulan di lantai
import React from "react";
import { AbsoluteFill, interpolate } from "remotion";

export const W = 1080;
export const H = 1920;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export type Light = { x: number; y: number; c: string; size: number; at: number | null; hold: number; ground?: number };

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
