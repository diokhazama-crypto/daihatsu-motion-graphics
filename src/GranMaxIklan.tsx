import "@fontsource/montserrat/300.css";
import "@fontsource/montserrat/500.css";
import "@fontsource/montserrat/600.css";
import "@fontsource/montserrat/700.css";
import "@fontsource/playfair-display/400-italic.css";
import "@fontsource/playfair-display/600-italic.css";
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
import data from "./iklan.json";

// Gaya iklan profesional: gerak pelan, dissolve, tipografi bersih.
const RED = "#D7001B";
const SANS = "Montserrat, Arial, sans-serif";
const SERIF = "'Playfair Display', Georgia, serif";

type Shot = { f: number; d: number; clip: string; t: number; in: string; ov: number; rate?: number; dim?: number; blur?: number };
type Txt = { f: number; d: number; style: string; [k: string]: unknown };
const shots = data.shots as Shot[];
const texts = data.texts as unknown as Txt[];
const cta = data.cta;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.inOut(Easing.cubic);
const outQuint = Easing.out(Easing.poly(5));

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load("300 60px Montserrat"),
      document.fonts.load("500 60px Montserrat"),
      document.fonts.load("600 60px Montserrat"),
      document.fonts.load("700 60px Montserrat"),
      document.fonts.load("italic 400 60px 'Playfair Display'"),
      document.fonts.load("italic 600 60px 'Playfair Display'"),
    ]).then(() => continueRender(h));
  }, [h]);
};

// ------------------------------------------------------------------ video
const Shot: React.FC<{ s: Shot; i: number }> = ({ s, i }) => {
  const local = useCurrentFrame();
  const ov = s.ov;
  const f = local - ov; // 0 = titik potong
  const dir = i % 2 === 0 ? 1 : -1;
  let opacity = 1;
  let tx = 0;
  let scale = 1;

  // masuk
  if (ov > 0) {
    if (s.in === "black") {
      opacity = interpolate(f, [-ov / 2, 0], [0, 1], { ...clamp, easing: ease });
    } else {
      const p = interpolate(f, [-ov, 0], [0, 1], { ...clamp, easing: ease });
      opacity = p;
      if (s.in === "slide") tx = (1 - p) * 18 * dir;
      if (s.in === "zoom") scale *= 1.12 - 0.12 * p;
    }
  } else if (i === 0) {
    opacity = interpolate(f, [0, 30], [0, 1], { ...clamp, easing: ease });
  }

  // keluar (mengikuti transisi shot berikutnya)
  const nx = shots[i + 1];
  if (nx && nx.ov > 0) {
    const e = interpolate(f, [s.d - nx.ov, s.d], [0, 1], { ...clamp, easing: ease });
    if (nx.in === "black") {
      opacity *= interpolate(f, [s.d - nx.ov, s.d - nx.ov / 2], [1, 0], { ...clamp, easing: ease });
    } else if (nx.in === "slide") {
      tx += -e * 18 * (i % 2 === 0 ? -1 : 1);
    } else if (nx.in === "zoom") {
      scale *= 1 + 0.06 * e;
    }
  }

  // gerak kamera pelan: push-in + geser tipis bergantian
  const life = (f + ov) / (s.d + ov);
  scale *= 1.04 + 0.07 * life;
  const pan = (life - 0.5) * 2.2 * dir;

  const trim = Math.max(0, Math.round(s.t * data.fps - ov * (s.rate ?? 1)));
  return (
    <AbsoluteFill style={{ opacity, overflow: "hidden" }}>
      <AbsoluteFill
        style={{
          transform: `translateX(${tx + pan}%) scale(${scale})`,
          filter: `blur(${s.blur ?? 0}px) contrast(1.08) saturate(0.9) brightness(${s.dim ? 1 - s.dim : 1})`,
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

// ------------------------------------------------------------------ grading & tekstur
const Grade: React.FC = () => (
  <>
    {/* tone sinematik: bayangan dingin, highlight hangat */}
    <AbsoluteFill style={{ background: "linear-gradient(160deg, rgba(255,170,90,0.10), rgba(0,0,0,0) 45%, rgba(20,70,110,0.16))", mixBlendMode: "soft-light" }} />
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 90% 75% at 50% 45%, transparent 50%, rgba(0,0,0,0.5) 100%), linear-gradient(to bottom, rgba(0,0,0,0.30), transparent 22%, transparent 55%, rgba(0,0,0,0.62))",
      }}
    />
  </>
);

const Grain: React.FC = () => {
  const g = useCurrentFrame();
  const x = Math.floor(random(`gx${g}`) * 512);
  const y = Math.floor(random(`gy${g}`) * 512);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile("grain.png")})`,
        backgroundPosition: `${x}px ${y}px`,
        opacity: 0.07,
        mixBlendMode: "overlay",
      }}
    />
  );
};

// ------------------------------------------------------------------ helper animasi teks
const useInOut = (d: number, inLen = 18, outLen = 14) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [d - outLen, d], [1, 0], { ...clamp, easing: ease });
  const at = (start: number, len = inLen) => interpolate(f, [start, start + len], [0, 1], { ...clamp, easing: outQuint });
  return { f, out, at };
};

// teks muncul dari balik garis (mask reveal)
const Reveal: React.FC<{ p: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ p, children, style }) => (
  <div style={{ overflow: "hidden", ...style }}>
    <div style={{ transform: `translateY(${(1 - p) * 105}%)`, opacity: Math.min(1, p * 1.6) }}>{children}</div>
  </div>
);

const shadow = "0 4px 30px rgba(0,0,0,0.45)";

const Words: React.FC<{ text: string; start: number; style: React.CSSProperties }> = ({ text, start, style }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0 0.28em", ...style }}>
      {text.split(" ").map((w, k) => {
        const p = interpolate(f, [start + k * 4, start + k * 4 + 16], [0, 1], { ...clamp, easing: outQuint });
        return (
          <span key={k} style={{ display: "inline-block", opacity: p, transform: `translateY(${(1 - p) * 26}px)`, filter: `blur(${(1 - p) * 6}px)` }}>
            {w}
          </span>
        );
      })}
    </div>
  );
};

// ------------------------------------------------------------------ gaya teks
const TextBlock: React.FC<{ t: Txt }> = ({ t }) => {
  const { f, out, at } = useInOut(t.d);
  const s = (k: string) => String(t[k] ?? "");

  if (t.style === "intro") {
    return (
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 640, opacity: out, textShadow: shadow }}>
        <Words text={s("a")} start={0} style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 400, fontSize: 76, color: "#fff" }} />
        <Words text={s("b")} start={14} style={{ fontFamily: SANS, fontWeight: 600, fontSize: 54, color: "#fff", maxWidth: 900, textAlign: "center", lineHeight: 1.3, marginTop: 14 }} />
      </AbsoluteFill>
    );
  }

  if (t.style === "title") {
    const ls = interpolate(f, [0, t.d], [26, 14]);
    return (
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 470, opacity: out, textShadow: shadow }}>
        <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 36, letterSpacing: 18, color: "#fff", opacity: at(0, 24), marginLeft: 18 }}>{s("top")}</div>
        <Reveal p={at(6, 24)} style={{ marginTop: 6 }}>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 132, letterSpacing: ls, color: "#fff", marginLeft: ls, lineHeight: 1.1, whiteSpace: "nowrap" }}>{s("main")}</div>
        </Reveal>
        <div style={{ width: 260 * at(16, 26), height: 4, background: RED, margin: "22px 0 26px" }} />
        <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 32, letterSpacing: 10, color: "#eee", opacity: at(24, 22), marginLeft: 10 }}>{s("sub")}</div>
      </AbsoluteFill>
    );
  }

  if (t.style === "lower") {
    const line = at(0, 16);
    const exitY = (1 - out) * 24;
    return (
      <div style={{ position: "absolute", left: 80, top: 1170, opacity: out, transform: `translateY(${exitY}px)`, textShadow: shadow }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, opacity: at(4, 16) }}>
          <div style={{ width: 54 * line, height: 4, background: RED }} />
          <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 28, letterSpacing: 8, color: "#fff" }}>{s("cat")}</div>
        </div>
        <Reveal p={at(7, 20)} style={{ marginTop: 14 }}>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 74, color: "#fff", lineHeight: 1.12, whiteSpace: "nowrap" }}>{s("main")}</div>
        </Reveal>
        <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 36, color: "rgba(255,255,255,0.82)", marginTop: 10, opacity: at(14, 20), transform: `translateY(${(1 - at(14, 20)) * 14}px)` }}>
          {s("sub")}
        </div>
      </div>
    );
  }

  if (t.style === "statement") {
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out, textShadow: shadow, top: -60 }}>
        <Reveal p={at(0, 24)}>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 400, fontSize: 80, color: "#fff", whiteSpace: "nowrap" }}>{s("a")}</div>
        </Reveal>
        <Reveal p={at(10, 24)} style={{ marginTop: 4 }}>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 92, letterSpacing: 6, color: "#fff", textTransform: "uppercase", marginLeft: 6, whiteSpace: "nowrap" }}>{s("b")}</div>
        </Reveal>
        <div style={{ width: 200 * at(20, 24), height: 4, background: RED, marginTop: 26 }} />
      </AbsoluteFill>
    );
  }

  if (t.style === "tagline") {
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out, textShadow: shadow, top: -280 }}>
        <Reveal p={at(0, 22)}>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 120, letterSpacing: 16, color: "#fff", marginLeft: 16, whiteSpace: "nowrap" }}>{s("main")}</div>
        </Reveal>
        <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 56, color: "#fff", opacity: at(10, 22), marginTop: 8 }}>{s("sub")}</div>
      </AbsoluteFill>
    );
  }
  return null;
};

// ------------------------------------------------------------------ end card
const WaIcon: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path d="M50 8a42 42 0 0 0-36 63.6L8 92l21-5.6A42 42 0 1 0 50 8z" fill="#25D366" />
    <path
      d="M36 30c-2 0-5 2-5 7 0 6 5 13 11 19s13 11 19 11c5 0 7-3 7-5v-4c0-1-1-2-2-2l-8-3c-1 0-2 0-3 1l-3 3c-5-2-10-7-12-12l3-3c1-1 1-2 1-3l-3-8c0-1-1-2-2-2z"
      fill="#fff"
    />
  </svg>
);

const EndCard: React.FC = () => {
  const { f, at } = useInOut(cta.d);
  const fadeOut = interpolate(f, [cta.d - 22, cta.d], [1, 0], { ...clamp, easing: ease });
  const rise = (p: number) => ({ opacity: p, transform: `translateY(${(1 - p) * 22}px)` });
  const [brand1, brand2] = [cta.brand.split(" ")[0], cta.brand.split(" ").slice(1).join(" ")];
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 360, opacity: fadeOut, textShadow: shadow }}>
      <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 34, letterSpacing: 18, color: "#fff", marginLeft: 18, ...rise(at(10, 24)) }}>{brand1}</div>
      <Reveal p={at(14, 26)} style={{ marginTop: 4 }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 136, letterSpacing: 16, color: "#fff", marginLeft: 16, lineHeight: 1.1 }}>{brand2}</div>
      </Reveal>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 54, color: "#fff", marginTop: 6, ...rise(at(24, 24)) }}>{cta.tag}</div>

      <div style={{ width: 700 * at(32, 30), height: 2, background: "rgba(255,255,255,0.55)", margin: "56px 0 44px" }} />

      <div style={{ display: "flex", alignItems: "center", gap: 18, ...rise(at(40, 22)) }}>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 30, letterSpacing: 4, color: "#fff", background: RED, padding: "10px 24px" }}>
          {cta.promo[0].toUpperCase()}
        </div>
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 46, color: "#fff", marginTop: 22, ...rise(at(46, 22)) }}>
        {cta.promo.slice(1).join("  ·  ")}
      </div>

      <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 28, letterSpacing: 6, color: "rgba(255,255,255,0.75)", marginTop: 70, ...rise(at(56, 22)) }}>
        {cta.contact.toUpperCase()}
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 84, letterSpacing: 6, color: "#fff", marginTop: 8, ...rise(at(60, 22)) }}>{cta.name}</div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 20,
          marginTop: 24,
          padding: "16px 40px 16px 22px",
          border: "2px solid rgba(255,255,255,0.85)",
          borderRadius: 999,
          background: "rgba(0,0,0,0.25)",
          ...rise(at(66, 22)),
        }}
      >
        <WaIcon size={64} />
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 56, letterSpacing: 3, color: "#fff" }}>{cta.phone}</div>
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 24, color: "rgba(255,255,255,0.6)", marginTop: 40, ...rise(at(74, 20)) }}>{cta.fine}</div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ komposisi
export const GranMaxIklan: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {shots.map((s, i) => (
        <Sequence key={i} from={s.f - s.ov} durationInFrames={s.d + s.ov} layout="none">
          <Shot s={s} i={i} />
        </Sequence>
      ))}
      <Grade />
      {texts.map((t, i) => (
        <Sequence key={`t${i}`} from={t.f} durationInFrames={t.d} layout="none">
          <AbsoluteFill>
            <TextBlock t={t} />
          </AbsoluteFill>
        </Sequence>
      ))}
      <Sequence from={cta.f} durationInFrames={cta.d} layout="none">
        <EndCard />
      </Sequence>
      <Grain />
      <Audio src={staticFile("iklan_music.wav")} />
    </AbsoluteFill>
  );
};
