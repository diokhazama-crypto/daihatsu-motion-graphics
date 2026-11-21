import "@fontsource/anton/400.css";
import "@fontsource/montserrat/600.css";
import "@fontsource/montserrat/700.css";
import "@fontsource/playfair-display/400-italic.css";
import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  continueRender,
  delayRender,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
} from "remotion";

// Video TikTok serah terima unit dari 1 foto. Waktu dikunci ke lagu (150 BPM):
// 0.05 bass masuk | 2.04 break | 6.76 DROP | hentakan 8.21 9.98 10.44 10.59 12.19 | selesai 14.36
export const SERAH_FPS = 30;
export const SERAH_DUR = Math.round(14.36 * SERAH_FPS);

const RED = "#E1001E";
const GOLD = "#F5C451";
const SANS = "Montserrat, Arial, sans-serif";
const BIG = "Anton, Impact, sans-serif";
const SERIF = "'Playfair Display', Georgia, serif";
const PHONE = "0811-549-6949";
const DEALER = "DIO DAIHATSU";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.inOut(Easing.cubic);
const outQuint = Easing.out(Easing.poly(5));
const outBack = Easing.out(Easing.back(1.6));
const S = (s: number) => Math.round(s * SERAH_FPS);
const DROP = S(6.76);
const HITS = [6.78, 8.21, 9.98, 10.44, 10.59, 12.19].map(S);
const shadow = "0 6px 30px rgba(0,0,0,0.55)";
const PHOTO = staticFile("serah/foto.jpg");

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load("400 60px Anton"),
      document.fonts.load("600 60px Montserrat"),
      document.fonts.load("700 60px Montserrat"),
      document.fonts.load("italic 400 60px 'Playfair Display'"),
    ]).then(() => continueRender(h));
  }, [h]);
};

const Reveal: React.FC<{ p: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ p, children, style }) => (
  <div style={{ overflow: "hidden", ...style }}>
    <div style={{ transform: `translateY(${(1 - p) * 105}%)` }}>{children}</div>
  </div>
);

// ------------------------------------------------------------------ bagian 1: foto penuh, zoom dari emblem
// foto 2400x3200 -> cover 1080x1920: skala 0.6, lebar 1440, geser -180. Emblem ~ (50%, 59.5%) -> layar (540, 1142)
const FullPhoto: React.FC = () => {
  const f = useCurrentFrame();
  const z = interpolate(f, [0, S(6.0)], [2.3, 1.04], { ...clamp, easing: Easing.out(Easing.cubic) });
  const build = interpolate(f, [S(6.05), DROP], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const scale = z * (1 + 0.35 * build);
  const op = interpolate(f, [0, S(0.25)], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: op, overflow: "hidden" }}>
      <Img
        src={PHOTO}
        style={{
          position: "absolute",
          width: 1440,
          height: 1920,
          left: -180,
          top: 0,
          transformOrigin: "720px 1142px",
          transform: `scale(${scale})`,
          filter: `blur(${build * 12}px) brightness(${1.04 + build * 0.6}) contrast(1.05) saturate(1.08)`,
        }}
      />
      <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.45), transparent 26%, transparent 55%, rgba(0,0,0,0.7))" }} />
    </AbsoluteFill>
  );
};

const IntroText: React.FC = () => {
  const f = useCurrentFrame();
  const at = (s: number, len = 0.45) => interpolate(f, [S(s), S(s + len)], [0, 1], { ...clamp, easing: outQuint });
  const out = interpolate(f, [S(6.2), S(6.7)], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out, textShadow: shadow }}>
      <div style={{ position: "absolute", top: 190, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, letterSpacing: 16, color: "#fff", marginLeft: 16, opacity: at(0.2) }}>SERAH TERIMA UNIT</div>
        <div style={{ width: 160 * at(0.4, 0.6), height: 5, background: RED, marginTop: 18 }} />
      </div>
      <div style={{ position: "absolute", bottom: 300, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Reveal p={at(2.1, 0.5)}>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 150, color: "#fff", lineHeight: 1.15 }}>Selamat!</div>
        </Reveal>
        <Reveal p={at(2.9, 0.5)}>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 52, color: "#fff" }}>atas mobil barunya</div>
        </Reveal>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 36, color: "rgba(255,255,255,0.9)", marginTop: 22, opacity: at(4.1, 0.6), transform: `translateY(${(1 - at(4.1, 0.6)) * 16}px)` }}>
          Terima kasih atas kepercayaannya
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ bagian 2: kartu polaroid
const BlurBg: React.FC = () => (
  <AbsoluteFill style={{ overflow: "hidden" }}>
    <Img src={PHOTO} style={{ position: "absolute", width: 1440, height: 1920, left: -180, top: 0, transform: "scale(1.25)", filter: "blur(26px) brightness(0.55) saturate(1.2)" }} />
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, rgba(225,0,30,0.25), rgba(0,0,0,0.55) 75%)" }} />
  </AbsoluteFill>
);

const CARD_W = 800;
const PHOTO_W = 752;
const PHOTO_H = Math.round(PHOTO_W * 4 / 3);

const Polaroid: React.FC<{ k: number }> = ({ k }) => {
  // k = frame sejak drop
  const pIn = interpolate(k, [0, S(0.7)], [0, 1], { ...clamp, easing: outBack });
  const rot = interpolate(pIn, [0, 1], [-14, -2.5]) + Math.sin(k / 30) * 0.6;
  const scale = interpolate(pIn, [0, 1], [1.5, 1]);
  const y = Math.sin(k / 22) * 6;
  // kilau cahaya menyapu foto di tiap hentakan besar
  const sweep = (start: number) => interpolate(k, [start, start + S(0.8)], [-60, 160], clamp);
  const sw = [S(1.45), S(5.43)].map(sweep).find((v) => v > -60 && v < 160) ?? -100;
  return (
    <div
      style={{
        position: "absolute",
        left: (1080 - CARD_W) / 2,
        top: 470,
        width: CARD_W,
        background: "#fbfaf7",
        padding: `${(CARD_W - PHOTO_W) / 2}px ${(CARD_W - PHOTO_W) / 2}px 0`,
        boxShadow: "0 40px 80px rgba(0,0,0,0.55)",
        opacity: interpolate(k, [0, S(0.15)], [0, 1], clamp),
        transform: `translateY(${y}px) rotate(${rot}deg) scale(${scale})`,
      }}
    >
      <div style={{ position: "relative", width: PHOTO_W, height: PHOTO_H, overflow: "hidden" }}>
        <Img src={PHOTO} style={{ width: "100%", height: "100%", objectFit: "cover", transform: "scale(1.32)", transformOrigin: "52% 60%", filter: "contrast(1.05) saturate(1.08) brightness(1.04)" }} />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `linear-gradient(115deg, transparent ${sw - 12}%, rgba(255,255,255,0.55) ${sw}%, transparent ${sw + 12}%)`,
            mixBlendMode: "screen",
          }}
        />
      </div>
      <div style={{ height: 108, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SERIF, fontStyle: "italic", fontSize: 50, color: "#2a2a2a" }}>
        Selamat & sukses selalu!
      </div>
    </div>
  );
};

const DropText: React.FC<{ k: number }> = ({ k }) => {
  const at = (s: number, len = 0.45) => interpolate(k, [S(s), S(s + len)], [0, 1], { ...clamp, easing: outQuint });
  const pop = interpolate(k, [0, S(0.25)], [1.5, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <div style={{ position: "absolute", top: 120, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", textShadow: shadow }}>
      <div style={{ fontFamily: BIG, fontSize: 190, color: "#fff", lineHeight: 1, letterSpacing: 4, transform: `scale(${pop})`, opacity: at(0, 0.1) }}>SELAMAT</div>
      <Reveal p={at(0.2, 0.45)}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 46, letterSpacing: 14, color: GOLD, marginLeft: 14 }}>SERAH TERIMA UNIT</div>
      </Reveal>
    </div>
  );
};

const Cta: React.FC<{ k: number }> = ({ k }) => {
  const start = S(10.59) - DROP;
  const p = interpolate(k, [start, start + S(0.5)], [0, 1], { ...clamp, easing: outQuint });
  const q = interpolate(k, [start + S(0.25), start + S(0.75)], [0, 1], { ...clamp, easing: outQuint });
  return (
    <div style={{ position: "absolute", bottom: 70, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", textShadow: shadow }}>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 32, color: "#fff", opacity: p, transform: `translateY(${(1 - p) * 20}px)` }}>Giliran Anda berikutnya!</div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 18,
          marginTop: 14,
          padding: "14px 34px",
          borderRadius: 999,
          background: RED,
          boxShadow: "0 10px 30px rgba(0,0,0,0.35)",
          opacity: q,
          transform: `translateY(${(1 - q) * 24}px)`,
        }}
      >
        <div style={{ fontFamily: BIG, fontSize: 52, color: "#fff", letterSpacing: 3 }}>{DEALER}</div>
        <div style={{ width: 2, height: 44, background: "rgba(255,255,255,0.6)" }} />
        <svg width={44} height={44} viewBox="0 0 100 100">
          <path d="M50 8a42 42 0 0 0-36 63.6L8 92l21-5.6A42 42 0 1 0 50 8z" fill="#fff" />
          <path d="M36 30c-2 0-5 2-5 7 0 6 5 13 11 19s13 11 19 11c5 0 7-3 7-5v-4c0-1-1-2-2-2l-8-3c-1 0-2 0-3 1l-3 3c-5-2-10-7-12-12l3-3c1-1 1-2 1-3l-3-8c0-1-1-2-2-2z" fill={RED} />
        </svg>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 44, color: "#fff", letterSpacing: 1 }}>{PHONE}</div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ confetti
const COLORS = [RED, "#ffffff", GOLD, "#ff5a6e"];
const Confetti: React.FC<{ k: number; seed: string; n: number }> = ({ k, seed, n }) => {
  if (k < 0) return null;
  const t = k / SERAH_FPS;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: n }).map((_, i) => {
        const r = (s: string) => random(`${seed}${i}${s}`);
        const ang = -Math.PI / 2 + (r("a") - 0.5) * 2.4;
        const sp = 900 + r("v") * 1300;
        const drag = 1.6;
        const decay = (1 - Math.exp(-drag * t)) / drag;
        const x = 540 + Math.cos(ang) * sp * decay + Math.sin(t * 3 + r("p") * 6) * 40 * t;
        const y = 760 + Math.sin(ang) * sp * decay + 420 * t * t;
        const w = 14 + r("w") * 14;
        const op = interpolate(t, [0, 0.05, 3.2, 4.2], [0, 1, 1, 0], clamp);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: w,
              height: w * (0.45 + r("h") * 0.4),
              background: COLORS[Math.floor(r("c") * COLORS.length)],
              borderRadius: r("s") > 0.7 ? 999 : 2,
              opacity: op,
              transform: `rotate(${t * (200 + r("r") * 500)}deg) scaleX(${Math.cos(t * (6 + r("f") * 8))})`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ kilatan & tekstur
const Flash: React.FC = () => {
  const f = useCurrentFrame();
  let a = interpolate(f, [S(0.0), S(0.05), S(0.35)], [0, 0.8, 0], clamp);
  for (const h of HITS) {
    const big = h === HITS[0] ? 1 : 0.35;
    a = Math.max(a, big * interpolate(f, [h - 1, h, h + S(0.3)], [0, 0.95, 0], { ...clamp, easing: Easing.out(Easing.quad) }));
  }
  return <AbsoluteFill style={{ background: "#fff", opacity: a }} />;
};

const LightLeak: React.FC = () => {
  const f = useCurrentFrame();
  const x = interpolate(f, [0, SERAH_DUR], [-20, 120]);
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 60% 40% at ${x}% 15%, rgba(255,190,120,0.35), transparent 70%)`,
        mixBlendMode: "screen",
      }}
    />
  );
};

const Grain: React.FC = () => {
  const g = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile("grain.png")})`,
        backgroundPosition: `${Math.floor(random(`sx${g}`) * 512)}px ${Math.floor(random(`sy${g}`) * 512)}px`,
        opacity: 0.06,
        mixBlendMode: "overlay",
      }}
    />
  );
};

// ------------------------------------------------------------------ komposisi
const SerahTerimaBase: React.FC<{ music: boolean }> = ({ music }) => {
  useFonts();
  const f = useCurrentFrame();
  const k = f - DROP;
  const endFade = interpolate(f, [SERAH_DUR - S(0.5), SERAH_DUR], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <AbsoluteFill style={{ opacity: endFade }}>
        {k < 0 ? (
          <>
            <FullPhoto />
            <IntroText />
          </>
        ) : (
          <>
            <BlurBg />
            <Confetti k={k} seed="a" n={90} />
            <Polaroid k={k} />
            <DropText k={k} />
            <Confetti k={f - S(10.59)} seed="b" n={60} />
            <Cta k={k} />
          </>
        )}
        <LightLeak />
      </AbsoluteFill>
      <Flash />
      <Grain />
      {music && <Audio src={staticFile("serah/lagu.mp3")} />}
    </AbsoluteFill>
  );
};

export const SerahTerima: React.FC = () => <SerahTerimaBase music />;
export const SerahTerimaPolos: React.FC = () => <SerahTerimaBase music={false} />;
