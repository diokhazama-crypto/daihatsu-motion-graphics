import "@fontsource/anton/400.css";
import "@fontsource/montserrat/800.css";
import "@fontsource/montserrat/900.css";
import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
} from "remotion";
import timeline from "./timeline.json";

// ------------------------------------------------------------------ konstanta
const RED = "#E50019";
const YELLOW = "#FFD21F";
const WA = "#25D366";
const HEAD = "Anton, Impact, sans-serif";
const BODY = "Montserrat, Arial, sans-serif";
const BEAT = (60 / timeline.bpm) * timeline.fps; // ~13.85 frame

type Shot = {
  f: number;
  d: number;
  clip: string;
  t?: number;
  in?: string;
  rate?: number;
  dim?: number;
  blur?: number;
};
type Txt = {
  f: number;
  d: number;
  style: string;
  lines: string[];
  sub?: string;
  head?: string;
};

const shots = timeline.shots as Shot[];
const texts = timeline.texts as Txt[];
const beats = timeline.beats as { f: number; w: number }[];
const drops = timeline.drops as number[];
const [stutterA, stutterB] = timeline.stutter as number[];

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const outExpo = Easing.out(Easing.exp);
const outBack = Easing.out(Easing.back(1.8));

// Denyut di setiap ketukan lagu -> w tepat di beat, turun cepat.
// w diambil dari timeline (jedug di awal bar paling kuat).
const beatPulse = (g: number) => {
  let b = beats[0];
  for (const x of beats) {
    if (x.f <= g) b = x;
    else break;
  }
  return g < b.f ? 0 : b.w * Math.exp(-(g - b.f) / 4.5);
};

// ------------------------------------------------------------------ font loader
const useFonts = () => {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load("400 100px Anton"),
      document.fonts.load("800 100px Montserrat"),
      document.fonts.load("900 100px Montserrat"),
    ]).then(() => continueRender(handle));
  }, [handle]);
};

// ------------------------------------------------------------------ shot video
// Transisi halus: shot baru mulai OV frame SEBELUM ketukan dan menimpa shot lama,
// sehingga tepat di ketukan shot baru sudah penuh (crossfade / push / zoom-through).
const TR_LEN: Record<string, number> = { whip: 9, zoom: 9, spin: 10, flash: 6, fade: 14, cut: 0 };
const smooth = Easing.inOut(Easing.cubic);

const overlapOf = (i: number) => {
  const s = shots[i];
  const prev = shots[i - 1];
  if (!prev || s.clip === "black" || prev.clip === "black") return 0;
  const want = TR_LEN[s.in ?? "cut"] ?? 0;
  return Math.max(0, Math.min(want, Math.floor(prev.d * 0.45), Math.floor(s.d * 0.45)));
};
const overlaps = shots.map((_, i) => overlapOf(i));
const dirOf = (i: number) => (i % 2 === 0 ? 1 : -1);

const ShotView: React.FC<{ s: Shot; idx: number }> = ({ s, idx }) => {
  const local = useCurrentFrame();
  const ov = overlaps[idx];
  const f = local - ov; // 0 = tepat di ketukan
  const g = s.f + f;
  if (s.clip === "black") return <AbsoluteFill style={{ background: "#000" }} />;

  const tr = s.in ?? "cut";
  let scale = 1;
  let tx = 0;
  let rot = 0;
  let blur = s.blur ?? 0;
  let opacity = 1;
  let glow = 1;

  // ---- masuk (f dari -ov sampai 0)
  if (ov > 0) {
    const p = interpolate(f, [-ov, 0], [0, 1], { ...clamp, easing: smooth });
    const bump = Math.sin(Math.PI * p);
    const dir = dirOf(idx);
    if (tr === "whip") {
      tx = (1 - p) * 100 * dir;
      blur += 7 * bump;
    } else if (tr === "zoom") {
      scale *= 1.45 - 0.45 * p;
      blur += 9 * (1 - p);
      opacity = interpolate(f, [-ov, -ov * 0.35], [0, 1], { ...clamp, easing: smooth });
    } else if (tr === "spin") {
      scale *= 1.45 - 0.45 * p;
      rot = -12 * dir * (1 - p);
      blur += 8 * (1 - p);
      opacity = interpolate(f, [-ov, -ov * 0.35], [0, 1], { ...clamp, easing: smooth });
    } else if (tr === "flash") {
      opacity = p;
      glow = 1 + 0.5 * (1 - p);
    } else if (tr === "fade") {
      opacity = p;
    }
  } else if (tr === "fade") {
    opacity = interpolate(f, [0, 12], [0, 1], { ...clamp, easing: smooth });
  }
  // sedikit "settle" setelah ketukan supaya mendarat lembut
  if (tr !== "cut") scale *= interpolate(f, [0, 12], [1.04, 1], { ...clamp, easing: outExpo });

  // ---- keluar: ikut gerak transisi shot berikutnya
  const next = shots[idx + 1];
  const nov = overlaps[idx + 1] ?? 0;
  if (next && nov > 0) {
    const e = interpolate(f, [s.d - nov, s.d], [0, 1], { ...clamp, easing: smooth });
    const nt = next.in ?? "cut";
    const ndir = dirOf(idx + 1);
    if (nt === "whip") {
      tx += -e * 100 * ndir;
      blur += 7 * Math.sin(Math.PI * e);
    } else if (nt === "zoom" || nt === "spin") {
      scale *= 1 + 0.35 * e;
      blur += 7 * e;
      if (nt === "spin") rot += 10 * ndir * e;
    } else if (nt === "flash") {
      glow *= 1 + 0.5 * e;
    }
  }

  // Ken burns pelan + denyut beat (lebih lembut)
  scale *= 1 + (f + ov) * 0.0012;
  const pl = beatPulse(g);
  scale *= 1 + 0.032 * pl;
  const bright = (1 + 0.08 * pl) * glow;

  const fps = timeline.fps;
  const trim = Math.max(0, Math.round((s.t ?? 0) * fps - ov * (s.rate ?? 1)));
  return (
    <AbsoluteFill style={{ overflow: "hidden", opacity }}>
      <AbsoluteFill
        style={{
          transform: `translateX(${tx}%) scale(${scale}) rotate(${rot}deg)`,
          filter: `blur(${blur.toFixed(2)}px) contrast(1.1) saturate(1.2) brightness(${bright * (s.dim ? 1 - s.dim : 1)})`,
        }}
      >
        <OffthreadVideo
          src={staticFile(`clips/${s.clip}.mp4`)}
          trimBefore={trim}
          playbackRate={s.rate ?? 1}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ overlay global
const Flash: React.FC = () => {
  const g = useCurrentFrame();
  let a = 0;
  for (const s of shots) {
    if (s.in === "flash" && g >= s.f && g < s.f + 10) {
      const big = drops.includes(s.f);
      a = Math.max(a, interpolate(g - s.f, [0, big ? 10 : 8], [big ? 0.55 : 0.28, 0], { ...clamp, easing: outExpo }));
    }
  }
  // kilat kecil di stutter sebelum drop
  for (const s of shots) {
    if (s.f >= stutterA && s.f < stutterB && s.clip !== "black" && g === s.f) a = Math.max(a, 0.3);
  }
  return <AbsoluteFill style={{ background: "#fff", opacity: a, pointerEvents: "none" }} />;
};

const LightLeak: React.FC = () => {
  const g = useCurrentFrame();
  const starts = timeline.leaks as number[];
  let el: React.ReactNode = null;
  for (const st of starts) {
    const l = g - st;
    if (l >= 0 && l < 26) {
      const x = interpolate(l, [0, 26], [-40, 140]);
      const o = interpolate(l, [0, 4, 18, 26], [0, 0.85, 0.5, 0]);
      el = (
        <AbsoluteFill
          style={{
            mixBlendMode: "screen",
            opacity: o,
            background: `radial-gradient(ellipse 55% 80% at ${x}% 40%, rgba(255,120,30,0.95), rgba(229,0,25,0.55) 40%, transparent 70%)`,
          }}
        />
      );
    }
  }
  return <>{el}</>;
};

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(ellipse 85% 70% at 50% 45%, transparent 55%, rgba(0,0,0,0.55) 100%), linear-gradient(to bottom, rgba(0,0,0,0.35), transparent 18%, transparent 70%, rgba(0,0,0,0.45))",
    }}
  />
);

const Shake: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const g = useCurrentFrame();
  let amp = 0;
  for (const st of drops) {
    const l = g - st;
    if (l >= 0 && l < 14) amp = Math.max(amp, interpolate(l, [0, 14], [10, 0]));
  }
  for (const s of shots) {
    if (s.in === "flash" && g - s.f >= 0 && g - s.f < 8) amp = Math.max(amp, interpolate(g - s.f, [0, 8], [4, 0]));
  }
  const x = (random(`x${g}`) - 0.5) * amp;
  const y = (random(`y${g}`) - 0.5) * amp;
  return <AbsoluteFill style={{ transform: `translate(${x}px, ${y}px) scale(${amp ? 1.015 : 1})` }}>{children}</AbsoluteFill>;
};

// Label brand kecil di atas (di bawah area UI TikTok)
const BrandTag: React.FC = () => {
  const g = useCurrentFrame();
  if (g < drops[0] || g >= timeline.cta.f) return null;
  const inA = interpolate(g - drops[0], [6, 18], [0, 1], { ...clamp, easing: outExpo });
  const outA = interpolate(g, [timeline.cta.f - 8, timeline.cta.f], [1, 0], clamp);
  return (
    <div
      style={{
        position: "absolute",
        top: 250,
        left: 60,
        display: "flex",
        alignItems: "stretch",
        opacity: inA * outA,
        transform: `translateX(${(1 - inA) * -60}px)`,
        fontFamily: BODY,
        fontWeight: 900,
        fontSize: 34,
        letterSpacing: 3,
        boxShadow: "0 6px 24px rgba(0,0,0,0.35)",
      }}
    >
      <div style={{ background: RED, color: "#fff", padding: "10px 18px" }}>DAIHATSU</div>
      <div style={{ background: "#fff", color: "#111", padding: "10px 18px" }}>GRAN MAX</div>
    </div>
  );
};

// ------------------------------------------------------------------ teks
const shadow = "0 10px 0 rgba(0,0,0,0.35), 0 0 40px rgba(0,0,0,0.55)";

const TextLayer: React.FC<{ t: Txt }> = ({ t }) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [t.d - 7, t.d], [1, 0], { ...clamp, easing: smooth });
  const outScale = interpolate(f, [t.d - 7, t.d], [1, 1.08], { ...clamp, easing: smooth });

  if (t.style === "kicker") {
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out, top: -120 }}>
        {t.lines.map((ln, i) => {
          const p = interpolate(f, [i * 7, i * 7 + 9], [0, 1], { ...clamp, easing: outExpo });
          return (
            <div key={i} style={{ overflow: "hidden", padding: "0 10px" }}>
              <div
                style={{
                  fontFamily: HEAD,
                  fontSize: 132,
                  lineHeight: 1.08,
                  color: i === 1 ? "#111" : "#fff",
                  background: i === 1 ? YELLOW : "transparent",
                  padding: i === 1 ? "0 26px" : 0,
                  transform: `translateY(${(1 - p) * 110}%)`,
                  textShadow: i === 1 ? "none" : shadow,
                  letterSpacing: 2,
                }}
              >
                {ln}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    );
  }

  if (t.style === "title" || t.style === "hero") {
    const hero = t.style === "hero";
    const sc = interpolate(f, [0, 10], [1.6, 1], { ...clamp, easing: outExpo });
    const glitch = f < 9 ? interpolate(f, [0, 9], [18, 0]) : 0;
    const subP = interpolate(f, [8, 18], [0, 1], { ...clamp, easing: outExpo });
    const bar = interpolate(f, [4, 20], [0, 1], { ...clamp, easing: outExpo });
    const word = t.lines[0];
    const size = word.length > 8 ? 190 : 230;
    const base: React.CSSProperties = {
      fontFamily: HEAD,
      fontSize: size,
      lineHeight: 1,
      letterSpacing: interpolate(f, [0, 30], [6, 12], clamp),
      whiteSpace: "nowrap",
    };
    return (
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          opacity: hero ? 1 : out,
          top: hero ? -260 : -80,
          transform: `scale(${hero ? 1 : outScale})`,
        }}
      >
        <div style={{ position: "relative", transform: `scale(${sc})` }}>
          <div style={{ ...base, position: "absolute", color: "rgba(0,255,255,0.8)", transform: `translate(${-glitch}px, 0)`, mixBlendMode: "screen" }}>{word}</div>
          <div style={{ ...base, position: "absolute", color: "rgba(255,0,60,0.8)", transform: `translate(${glitch}px, 0)`, mixBlendMode: "screen" }}>{word}</div>
          <div style={{ ...base, position: "relative", color: "#fff", textShadow: shadow }}>{word}</div>
        </div>
        <div style={{ width: 640 * bar, height: 10, background: RED, margin: "18px 0 22px", boxShadow: "0 0 30px rgba(229,0,25,0.8)" }} />
        {t.sub && (
          <div style={{ overflow: "hidden" }}>
            <div
              style={{
                fontFamily: BODY,
                fontWeight: 900,
                fontSize: 56,
                letterSpacing: 8,
                color: "#fff",
                background: RED,
                padding: "10px 30px",
                transform: `translateY(${(1 - subP) * 120}%)`,
              }}
            >
              {t.sub}
            </div>
          </div>
        )}
      </AbsoluteFill>
    );
  }

  if (t.style === "word") {
    // tiap baris masuk di ketukan berbeda
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out, top: -60, transform: `scale(${outScale})` }}>
        {t.lines.map((ln, i) => {
          const st = i * (t.d >= 60 ? 15 : 5);
          const sc = interpolate(f, [st, st + 8], [1.45, 1], { ...clamp, easing: outBack });
          const o = interpolate(f, [st, st + 4], [0, 1], clamp);
          const skew = interpolate(f, [st, st + 6], [-12, 0], clamp);
          const grow = 1 + Math.max(0, f - st) * 0.003;
          return (
            <div
              key={i}
              style={{
                fontFamily: HEAD,
                fontSize: ln.length > 9 ? 170 : 210,
                lineHeight: 1.02,
                color: i % 2 === 1 ? YELLOW : "#fff",
                textShadow: shadow,
                WebkitTextStroke: "3px rgba(0,0,0,0.25)",
                opacity: o,
                transform: `scale(${sc * grow}) skewX(${skew}deg)`,
                letterSpacing: 4,
                whiteSpace: "nowrap",
              }}
            >
              {ln}
            </div>
          );
        })}
      </AbsoluteFill>
    );
  }

  if (t.style === "chip") {
    const p = interpolate(f, [0, 8], [0, 1], { ...clamp, easing: outExpo });
    const hp = interpolate(f, [3, 10], [0, 1], { ...clamp, easing: outExpo });
    return (
      <div style={{ position: "absolute", left: 70, top: 1060, opacity: out }}>
        <div
          style={{
            display: "inline-block",
            fontFamily: BODY,
            fontWeight: 900,
            fontSize: 34,
            letterSpacing: 6,
            color: "#fff",
            background: RED,
            padding: "8px 18px",
            transform: `translateX(${(1 - hp) * -120}%)`,
          }}
        >
          {t.head}
        </div>
        <div style={{ overflow: "hidden" }}>
          <div
            style={{
              fontFamily: HEAD,
              fontSize: 128,
              lineHeight: 1.1,
              color: "#111",
              background: "#fff",
              padding: "6px 30px 2px",
              display: "inline-block",
              transform: `translateX(${(1 - p) * -105}%)`,
              boxShadow: "12px 12px 0 rgba(229,0,25,0.95)",
              letterSpacing: 2,
              whiteSpace: "nowrap",
            }}
          >
            {t.lines[0]}
          </div>
        </div>
      </div>
    );
  }

  if (t.style === "type") {
    const full = t.lines[0];
    const n = Math.floor(interpolate(f, [4, 34], [0, full.length], clamp));
    const cursor = Math.floor(f / 8) % 2 === 0;
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: -40, opacity: out }}>
        <div style={{ fontFamily: HEAD, fontSize: 120, color: "#fff", textShadow: shadow, letterSpacing: 4, whiteSpace: "nowrap" }}>
          {full.slice(0, n)}
          <span style={{ color: RED, opacity: cursor ? 1 : 0 }}>|</span>
        </div>
      </AbsoluteFill>
    );
  }
  return null;
};

// ------------------------------------------------------------------ CTA penutup
const CTA: React.FC = () => {
  const f = useCurrentFrame();
  const c = timeline.cta;
  const at = (i: number) => c.steps[i] ?? i * BEAT;
  const step = (i: number) => interpolate(f, [at(i), at(i) + 9], [0, 1], { ...clamp, easing: outExpo });
  const pop = (i: number) => interpolate(f, [at(i), at(i) + 8], [0.4, 1], { ...clamp, easing: outBack });
  const pulse = 1 + 0.08 * beatPulse(f + c.f);
  const waGlow = 0.5 + 0.5 * Math.sin(f / 5);
  const endFade = interpolate(f, [c.d - 20, c.d], [1, 0.0], clamp);

  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 300, opacity: endFade }}>
      <div style={{ overflow: "hidden" }}>
        <div
          style={{
            fontFamily: BODY,
            fontWeight: 900,
            fontSize: 44,
            letterSpacing: 8,
            color: "#fff",
            background: RED,
            padding: "12px 34px",
            transform: `translateY(${(1 - step(0)) * 120}%)`,
          }}
        >
          {c.head}
        </div>
      </div>
      <div
        style={{
          fontFamily: HEAD,
          fontSize: 210,
          lineHeight: 1,
          marginTop: 40,
          color: "#fff",
          textShadow: shadow,
          transform: `scale(${pop(1) * pulse})`,
          opacity: step(1),
          letterSpacing: 6,
        }}
      >
        {c.line1}
      </div>
      <div
        style={{
          fontFamily: HEAD,
          fontSize: 96,
          lineHeight: 1.1,
          color: "#111",
          background: YELLOW,
          padding: "4px 28px",
          marginTop: 18,
          transform: `scale(${pop(2)})`,
          opacity: step(2),
          letterSpacing: 3,
        }}
      >
        {c.line2}
      </div>

      <div style={{ width: 760 * step(3), height: 6, background: "rgba(255,255,255,0.85)", margin: "60px 0 40px" }} />

      <div style={{ fontFamily: BODY, fontWeight: 800, fontSize: 42, color: "#ddd", letterSpacing: 10, opacity: step(4) }}>
        HUBUNGI
      </div>
      <div
        style={{
          fontFamily: HEAD,
          fontSize: 150,
          color: "#fff",
          textShadow: shadow,
          letterSpacing: 6,
          opacity: step(4),
          transform: `translateY(${(1 - step(4)) * 40}px)`,
        }}
      >
        {c.name}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 22,
          marginTop: 26,
          background: WA,
          borderRadius: 999,
          padding: "20px 46px 20px 26px",
          transform: `scale(${pop(5) * pulse})`,
          opacity: step(5),
          boxShadow: `0 0 ${30 + 40 * waGlow}px rgba(37,211,102,${0.45 + 0.4 * waGlow})`,
        }}
      >
        <WaIcon />
        <div style={{ fontFamily: BODY, fontWeight: 900, fontSize: 70, color: "#fff", letterSpacing: 2 }}>{c.phone}</div>
      </div>
      <div style={{ fontFamily: BODY, fontWeight: 800, fontSize: 44, color: "#fff", marginTop: 34, opacity: step(6), letterSpacing: 2 }}>
        {c.note}
      </div>
    </AbsoluteFill>
  );
};

// Ikon chat sederhana (gelembung + gagang telepon), digambar sendiri
const WaIcon: React.FC = () => (
  <svg width={86} height={86} viewBox="0 0 100 100">
    <path d="M50 8a42 42 0 0 0-36 63.6L8 92l21-5.6A42 42 0 1 0 50 8z" fill="#fff" />
    <path
      d="M36 30c-2 0-5 2-5 7 0 6 5 13 11 19s13 11 19 11c5 0 7-3 7-5v-4c0-1-1-2-2-2l-8-3c-1 0-2 0-3 1l-3 3c-5-2-10-7-12-12l3-3c1-1 1-2 1-3l-3-8c0-1-1-2-2-2z"
      fill={WA}
    />
  </svg>
);

// ------------------------------------------------------------------ komposisi
export const GranMaxPromo: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Shake>
        {shots.map((s, i) => (
          <Sequence key={i} from={s.f - overlaps[i]} durationInFrames={s.d + overlaps[i]} layout="none">
            <ShotView s={s} idx={i} />
          </Sequence>
        ))}
        <LightLeak />
      </Shake>
      <Vignette />
      <BrandTag />
      {texts.map((t, i) => (
        <Sequence key={`t${i}`} from={t.f} durationInFrames={t.d} layout="none">
          <AbsoluteFill>
            <TextLayer t={t} />
          </AbsoluteFill>
        </Sequence>
      ))}
      <Sequence from={timeline.cta.f} durationInFrames={timeline.cta.d} layout="none">
        <CTA />
      </Sequence>
      <Flash />
      <Audio src={staticFile("music.wav")} />
    </AbsoluteFill>
  );
};
