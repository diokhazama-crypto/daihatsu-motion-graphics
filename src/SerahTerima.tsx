import "@fontsource/anton/400.css";
import "@fontsource/montserrat/600.css";
import "@fontsource/montserrat/700.css";
import "@fontsource/montserrat/800.css";
import "@fontsource/playfair-display/400-italic.css";
import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  random,
  staticFile,
  useCurrentFrame,
} from "remotion";

// Video TikTok serah terima unit dari 1 foto. Foto SELALU full layar (tidak dijadikan kartu/tempelan),
// teks putih polos. Efek: zoom halus, teks di belakang orang (orang dipisah dari latar), kilatan di hentakan,
// confetti, kembang api, shockwave, lens flare, glitch sesaat, partikel cahaya.
// Waktu dikunci ke lagu 150 BPM (2 putaran): 0.05 bass | 2.04 break | 6.76 DROP | 14.355 putaran 2
export const SERAH_FPS = 30;
const SONG = 14.355;
export const SERAH_DUR = Math.round(2 * SONG * SERAH_FPS);

const NAME = "BAPAK HAMID";
const PHONE = "0811-549-6949";
const DEALER = "DIO DAIHATSU";
const RED = "#E1001E";
const GOLD = "#F5C451";
const SANS = "Montserrat, Arial, sans-serif";
const BIG = "Anton, Impact, sans-serif";
const SERIF = "'Playfair Display', Georgia, serif";
const BG = staticFile("serah/bg.jpg");
const FG = staticFile("serah/fg.png");
const PHOTO = staticFile("serah/foto.jpg");

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.inOut(Easing.cubic);
const outQuint = Easing.out(Easing.poly(5));
const outBack = Easing.out(Easing.back(1.7));
const S = (s: number) => Math.round(s * SERAH_FPS);
const T = (pass: number, s: number) => S(pass * SONG + s); // detik lagu di putaran -> frame
const ramp = (f: number, a: number, b: number, e = outQuint) => interpolate(f, [a, b], [0, 1], { ...clamp, easing: e });
const KICKS = [6.82, 7.02, 7.42, 7.72, 8.01, 8.42, 9.02, 9.32, 9.61, 9.81, 10.01, 10.61, 10.91, 11.22, 11.61, 12.21, 12.52, 12.7, 13.01, 13.21, 13.83, 14.12];
const HITS: [number, number][] = [];
for (const p of [0, 1]) for (const [t, k] of [[0.05, 1], [6.78, 1], [8.21, 0.5], [9.98, 0.5], [10.44, 0.4], [10.59, 0.5], [12.19, 0.6]] as const) HITS.push([T(p, t), k]);

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all(
      ["400 60px Anton", "600 60px Montserrat", "700 60px Montserrat", "800 60px Montserrat", "italic 400 60px 'Playfair Display'"].map((x) => document.fonts.load(x)),
    ).then(() => continueRender(h));
  }, [h]);
};

const Reveal: React.FC<{ p: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ p, children, style }) => (
  <div style={{ overflow: "hidden", ...style }}>
    <div style={{ transform: `translateY(${(1 - p) * 105}%)` }}>{children}</div>
  </div>
);
const shadow = "0 6px 30px rgba(0,0,0,0.6)";

// ------------------------------------------------------------------ partikel & efek cahaya
const Bokeh: React.FC<{ n?: number; seed?: string }> = ({ n = 26, seed = "bk" }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "screen" }}>
      {Array.from({ length: n }).map((_, i) => {
        const r = (s: string) => random(`${seed}${i}${s}`);
        const size = 30 + r("s") * 110;
        const x = ((r("x") * 1200 + f * (0.4 + r("v")) * 1.5) % 1300) - 110;
        const y = 1920 - ((r("y") * 2000 + f * (0.6 + r("u") * 1.4)) % 2100);
        const tw = 0.25 + 0.35 * Math.abs(Math.sin(f / (12 + r("t") * 20) + r("p") * 6));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: 999,
              background: r("c") > 0.5 ? "radial-gradient(circle, rgba(255,214,120,0.9), rgba(255,180,60,0) 70%)" : "radial-gradient(circle, rgba(255,255,255,0.8), rgba(255,255,255,0) 70%)",
              filter: `blur(${2 + r("b") * 6}px)`,
              opacity: tw,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const COLORS = [RED, "#ffffff", GOLD, "#ff5a6e", "#ffd86b"];
// confetti 3D: tiap kertas berputar di sumbu X/Y (kelihatan membalik)
const Confetti3D: React.FC<{ start: number; seed: string; n: number; x0?: number; y0?: number }> = ({ start, seed, n, x0 = 540, y0 = 760 }) => {
  const f = useCurrentFrame();
  const k = f - start;
  if (k < 0 || k > S(5)) return null;
  const t = k / SERAH_FPS;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", perspective: 800 }}>
      {Array.from({ length: n }).map((_, i) => {
        const r = (s: string) => random(`${seed}${i}${s}`);
        const ang = -Math.PI / 2 + (r("a") - 0.5) * 2.8;
        const sp = 800 + r("v") * 1500;
        const decay = (1 - Math.exp(-1.7 * t)) / 1.7;
        const x = x0 + Math.cos(ang) * sp * decay + Math.sin(t * 3 + r("p") * 6) * 50 * t;
        const y = y0 + Math.sin(ang) * sp * decay + 430 * t * t;
        const w = 16 + r("w") * 16;
        const op = interpolate(t, [0, 0.04, 3.5, 4.6], [0, 1, 1, 0], clamp);
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
              borderRadius: r("s") > 0.75 ? 999 : 2,
              opacity: op,
              transform: `rotateZ(${t * (150 + r("r") * 400)}deg) rotateX(${t * (300 + r("x") * 500)}deg) rotateY(${t * (200 + r("y") * 300)}deg)`,
              boxShadow: "0 0 6px rgba(255,255,255,0.3)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// kembang api: partikel memancar + ekor + gravitasi
const Firework: React.FC<{ start: number; x: number; y: number; seed: string; color?: string; n?: number }> = ({ start, x, y, seed, color = GOLD, n = 70 }) => {
  const f = useCurrentFrame();
  const k = f - start;
  if (k < -S(0.4) || k > S(2.2)) return null;
  // roket naik sebelum meledak
  if (k < 0) {
    const p = 1 + k / S(0.4);
    return (
      <div style={{ position: "absolute", left: x - 3, top: y + (1 - p) * 700, width: 6, height: 60, borderRadius: 3, background: `linear-gradient(to bottom, #fff, ${color}00)`, opacity: 0.9, mixBlendMode: "screen" }} />
    );
  }
  const t = k / SERAH_FPS;
  return (
    <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "screen" }}>
      <div
        style={{
          position: "absolute",
          left: x - 160,
          top: y - 160,
          width: 320,
          height: 320,
          borderRadius: 999,
          background: `radial-gradient(circle, ${color}cc, transparent 65%)`,
          opacity: interpolate(t, [0, 0.05, 0.4], [0, 1, 0], clamp),
        }}
      />
      {Array.from({ length: n }).map((_, i) => {
        const r = (s: string) => random(`${seed}${i}${s}`);
        const ang = (i / n) * Math.PI * 2 + r("j") * 0.2;
        const sp = 380 + r("v") * 260;
        const decay = (1 - Math.exp(-2.2 * t)) / 2.2;
        const px = x + Math.cos(ang) * sp * decay;
        const py = y + Math.sin(ang) * sp * decay + 160 * t * t;
        const vx = Math.cos(ang) * sp * Math.exp(-2.2 * t);
        const vy = Math.sin(ang) * sp * Math.exp(-2.2 * t) + 320 * t;
        const len = Math.min(70, Math.hypot(vx, vy) * 0.12) + 4;
        const op = interpolate(t, [0, 0.05, 1.2, 1.9], [0, 1, 0.8, 0], clamp) * (0.6 + 0.4 * Math.abs(Math.sin(t * 30 + i)));
        const c = r("c") > 0.7 ? "#ffffff" : color;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: px,
              top: py,
              width: len,
              height: 4,
              borderRadius: 2,
              background: `linear-gradient(to left, ${c}, ${c}00)`,
              transformOrigin: "0 50%",
              transform: `rotate(${(Math.atan2(vy, vx) * 180) / Math.PI + 180}deg)`,
              opacity: op,
              boxShadow: `0 0 8px ${c}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const Shockwave: React.FC<{ start: number; y?: number }> = ({ start, y = 960 }) => {
  const f = useCurrentFrame();
  const k = f - start;
  if (k < 0 || k > S(0.9)) return null;
  const p = ramp(k, 0, S(0.9), Easing.out(Easing.cubic));
  const r = 60 + p * 1300;
  return (
    <div
      style={{
        position: "absolute",
        left: 540 - r,
        top: y - r,
        width: r * 2,
        height: r * 2,
        borderRadius: 999,
        border: `${(1 - p) * 26 + 2}px solid rgba(255,235,190,${(1 - p) * 0.9})`,
        boxShadow: `0 0 60px rgba(255,200,120,${(1 - p) * 0.8}), inset 0 0 60px rgba(255,200,120,${(1 - p) * 0.6})`,
      }}
    />
  );
};

const LensFlare: React.FC<{ start: number; dur?: number }> = ({ start, dur = S(1.6) }) => {
  const f = useCurrentFrame();
  const k = f - start;
  if (k < 0 || k > dur) return null;
  const p = k / dur;
  const x = -300 + p * 1700;
  const y = 380 + p * 260;
  const a = Math.sin(p * Math.PI);
  const ghost = (m: number, size: number, col: string) => (
    <div style={{ position: "absolute", left: 540 + (540 - x) * m - size / 2, top: 960 + (960 - y) * m - size / 2, width: size, height: size, borderRadius: 999, background: col, opacity: a * 0.5 }} />
  );
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: x - 420, top: y - 6, width: 840, height: 12, borderRadius: 6, background: "linear-gradient(to right, transparent, rgba(160,200,255,0.9), transparent)", opacity: a, filter: "blur(2px)" }} />
      <div style={{ position: "absolute", left: x - 200, top: y - 200, width: 400, height: 400, borderRadius: 999, background: "radial-gradient(circle, rgba(255,250,230,1), rgba(255,200,120,0.4) 25%, transparent 60%)", opacity: a }} />
      {ghost(0.5, 90, "radial-gradient(circle, rgba(120,200,255,0.6), transparent 70%)")}
      {ghost(0.9, 160, "radial-gradient(circle, rgba(255,160,80,0.4), transparent 70%)")}
      {ghost(1.4, 60, "radial-gradient(circle, rgba(180,255,180,0.6), transparent 70%)")}
    </AbsoluteFill>
  );
};

const Flash: React.FC = () => {
  const f = useCurrentFrame();
  let a = 0;
  for (const [h, k] of HITS) a = Math.max(a, k * interpolate(f, [h - 1, h, h + S(0.3)], [0, 0.95, 0], { ...clamp, easing: Easing.out(Easing.quad) }));
  let pulse = 0;
  for (const p of [0, 1])
    for (const kk of KICKS) {
      const d = f - T(p, kk);
      if (d >= -1 && d < S(0.2)) pulse = Math.max(pulse, interpolate(d, [-1, 0, S(0.2)], [0, 1, 0], clamp));
    }
  return (
    <>
      <AbsoluteFill style={{ background: "#fff", mixBlendMode: "soft-light", opacity: pulse * 0.35 }} />
      <AbsoluteFill style={{ background: "#fff", opacity: a }} />
    </>
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

// glitch RGB sesaat (dipakai di hentakan 9.98 & 10.44)
const ChannelDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter id="st-r"><feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="st-g"><feColorMatrix type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="st-b"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" /></filter>
  </svg>
);
const Glitch: React.FC<{ amount: number; children: React.ReactNode }> = ({ amount, children }) => {
  if (amount < 0.02) return <>{children}</>;
  const off = 30 * amount;
  const L = (id: string, dx: number): React.CSSProperties => ({ transform: `translateX(${dx}px)`, filter: `url(#${id})`, mixBlendMode: "screen" });
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <AbsoluteFill style={L("st-r", off)}>{children}</AbsoluteFill>
      <AbsoluteFill style={L("st-g", 0)}>{children}</AbsoluteFill>
      <AbsoluteFill style={L("st-b", -off)}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ teks putih polos (pop per huruf, tanpa 3D)
const WhiteText: React.FC<{ text: string; size: number; p: number; stagger?: number; spacing?: number; color?: string }> = ({ text, size, p, stagger = 0.05, spacing = 4, color = "#fff" }) => (
  <div style={{ display: "flex", justifyContent: "center", whiteSpace: "pre" }}>
    {text.split("").map((ch, i) => {
      const q = interpolate(p, [i * stagger, i * stagger + 0.3], [0, 1], { ...clamp, easing: outBack });
      return (
        <div
          key={i}
          style={{
            fontFamily: BIG,
            fontSize: size,
            lineHeight: 1.05,
            letterSpacing: spacing,
            color,
            textShadow: "0 6px 26px rgba(0,0,0,0.55)",
            opacity: Math.min(1, q * 2),
            transform: `translateY(${(1 - q) * 50}px) scale(${0.6 + 0.4 * q})`,
          }}
        >
          {ch}
        </div>
      );
    })}
  </div>
);

// ------------------------------------------------------------------ foto full layar
// zoom: skala; cx/cy: titik fokus zoom (piksel layar); pop: orang sedikit lebih dekat dari latar
const FullPhoto: React.FC<{ zoom: number; cx?: number; cy?: number; pop?: number; blur?: number; bright?: number; behind?: React.ReactNode; glitch?: number }> = ({
  zoom,
  cx = 540,
  cy = 1150,
  pop = 0,
  blur = 0,
  bright = 1,
  behind,
  glitch = 0,
}) => {
  const filter = `blur(${blur}px) brightness(${bright}) contrast(1.05) saturate(1.08)`;
  const img = (src: string, extra = 1): React.CSSProperties => ({
    position: "absolute",
    width: 1440,
    height: 1920,
    left: -180,
    top: 0,
    transformOrigin: `${cx + 180}px ${cy}px`,
    transform: `scale(${zoom * extra})`,
    filter,
  });
  const body = (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      <Img src={behind ? BG : PHOTO} style={img(behind ? BG : PHOTO)} />
      {behind}
      {behind && <Img src={FG} style={img(FG, 1 + pop)} />}
      <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.4), transparent 24%, transparent 58%, rgba(0,0,0,0.6))" }} />
    </AbsoluteFill>
  );
  return <Glitch amount={glitch}>{body}</Glitch>;
};

const LightLeak: React.FC = () => {
  const f = useCurrentFrame();
  const x = interpolate(f, [0, SERAH_DUR], [-20, 120]);
  return <AbsoluteFill style={{ background: `radial-gradient(ellipse 60% 40% at ${x}% 12%, rgba(255,200,140,0.35), transparent 70%)`, mixBlendMode: "screen" }} />;
};

const Line: React.FC<{ p: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ p, children, style }) => (
  <div style={{ opacity: p, transform: `translateY(${(1 - p) * 24}px)`, textShadow: shadow, ...style }}>{children}</div>
);

// ------------------------------------------------------------------ adegan (semua foto full)
const Pass1: React.FC = () => {
  const f = useCurrentFrame();
  const at = (s: number, len = 0.45) => ramp(f, S(s), S(s + len));
  const drop = f >= S(6.76);
  const intro = ramp(f, 0, S(2.0), Easing.out(Easing.cubic));
  const push = ramp(f, S(2.04), S(6.05), ease);
  const build = ramp(f, S(6.05), S(6.76), Easing.in(Easing.cubic));
  const dk = f - S(6.76);
  const settle = interpolate(dk, [0, S(0.5)], [1.25, 1.06], { ...clamp, easing: Easing.out(Easing.cubic) });
  const dropPush = ramp(f, S(7.3), S(14.3), Easing.linear);
  const zoom = drop ? settle + 0.06 * dropPush : (1.3 - 0.25 * intro + 0.06 * push) * (1 + 0.5 * build);
  const g = f >= S(9.98) ? Math.max(interpolate(f, [S(9.98), S(10.12)], [1, 0], clamp), interpolate(f, [S(10.44), S(10.56)], [0.8, 0], clamp)) : 0;
  const behindOut = interpolate(f, [S(5.8), S(6.3)], [1, 0], clamp);
  const ty = ramp(f, S(12.19), S(12.7));
  return (
    <>
      <FullPhoto
        zoom={zoom}
        pop={drop ? 0 : 0.05 * intro}
        blur={drop ? 0 : build * 12}
        bright={drop ? 1 : 1 + build * 0.8}
        glitch={g}
        behind={
          !drop ? (
            <div style={{ position: "absolute", top: 340, left: 0, right: 0, opacity: behindOut }}>
              <WhiteText text="SELAMAT" size={235} p={ramp(f, S(0.15), S(1.5), Easing.linear)} stagger={0.1} spacing={2} />
            </div>
          ) : undefined
        }
      />
      <LightLeak />
      <Bokeh n={16} />
      {!drop ? (
        <AbsoluteFill style={{ opacity: interpolate(f, [S(5.9), S(6.4)], [1, 0], clamp) }}>
          <div style={{ position: "absolute", top: 190, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Line p={at(0.1)} style={{ fontFamily: SANS, fontWeight: 800, fontSize: 32, letterSpacing: 16, color: "#fff", marginLeft: 16 }}>SERAH TERIMA UNIT</Line>
            <div style={{ width: 170 * at(0.3, 0.6), height: 5, background: RED, marginTop: 16 }} />
          </div>
          <div style={{ position: "absolute", bottom: 250, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Line p={at(2.1)} style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 92, color: "#fff" }}>Selamat</Line>
            <WhiteText text={NAME} size={140} p={ramp(f, S(2.5), S(3.8), Easing.linear)} stagger={0.05} spacing={3} />
            <Line p={at(3.9)} style={{ fontFamily: SANS, fontWeight: 700, fontSize: 46, color: "#fff", marginTop: 6 }}>atas mobil barunya</Line>
            <Line p={at(4.7, 0.6)} style={{ fontFamily: SANS, fontWeight: 600, fontSize: 34, color: "rgba(255,255,255,0.92)", marginTop: 14 }}>Semoga berkah & lancar selalu</Line>
          </div>
        </AbsoluteFill>
      ) : (
        <AbsoluteFill>
          <div style={{ position: "absolute", top: 170, left: 0, right: 0, transform: `scale(${interpolate(dk, [0, S(0.3)], [1.5, 1], { ...clamp, easing: Easing.out(Easing.cubic) })})` }}>
            <WhiteText text="SELAMAT!" size={200} p={ramp(dk, 0, S(0.8), Easing.linear)} stagger={0.07} />
          </div>
          <div style={{ position: "absolute", bottom: 230, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <WhiteText text={NAME} size={140} p={ramp(dk, S(0.4), S(1.5), Easing.linear)} stagger={0.05} spacing={3} />
            <div style={{ position: "relative", height: 60, width: 1000, marginTop: 6 }}>
              <Line p={at(8.2) * (1 - ty)} style={{ position: "absolute", inset: 0, textAlign: "center", fontFamily: SANS, fontWeight: 700, fontSize: 44, color: "#fff" }}>atas mobil barunya 🎉</Line>
              <Line p={ty} style={{ position: "absolute", inset: 0, textAlign: "center", fontFamily: SANS, fontWeight: 700, fontSize: 40, color: "#fff" }}>Terima kasih atas kepercayaannya</Line>
            </div>
          </div>
        </AbsoluteFill>
      )}
      {drop && (
        <>
          <Firework start={S(8.21)} x={220} y={330} seed="fw1" color={GOLD} />
          <Firework start={S(9.98)} x={870} y={420} seed="fw2" color="#ff5a6e" />
          <Firework start={S(10.59)} x={540} y={260} seed="fw3" color="#ffffff" n={90} />
          <Firework start={S(12.19)} x={300} y={480} seed="fw4" color={GOLD} />
          <Shockwave start={S(6.76)} y={1000} />
          <Confetti3D start={S(6.76)} seed="c1" n={110} y0={900} />
          <LensFlare start={S(12.19)} />
        </>
      )}
    </>
  );
};

const Pass2: React.FC = () => {
  const f = useCurrentFrame();
  const k = f - T(1, 0);
  const at = (s: number, len = 0.45) => ramp(k, S(s), S(s + len));
  const drop = k >= S(6.76);
  const dk = k - S(6.76);
  // zoom keluar dari wajah Pak Hamid (kiri) lalu geser pelan ke tengah
  const intro = ramp(k, 0, S(2.0), Easing.out(Easing.cubic));
  const drift = ramp(k, S(2.04), S(6.05), ease);
  const build = ramp(k, S(6.05), S(6.76), Easing.in(Easing.cubic));
  const settle = interpolate(dk, [0, S(0.5)], [1.25, 1.04], { ...clamp, easing: Easing.out(Easing.cubic) });
  const zoom = drop ? settle + 0.05 * ramp(dk, S(0.5), S(7.5), Easing.linear) : (1.7 - 0.6 * intro + 0.08 * drift) * (1 + 0.5 * build);
  const cx = drop ? 540 : interpolate(intro, [0, 1], [330, 540]);
  const cy = drop ? 1150 : interpolate(intro, [0, 1], [640, 1150]);
  const g = Math.max(interpolate(f, [T(1, 9.98), T(1, 10.1)], [1, 0], clamp), interpolate(f, [T(1, 10.44), T(1, 10.56)], [0.8, 0], clamp)) * (f >= T(1, 9.98) ? 1 : 0);
  const cta = ramp(f, T(1, 10.59), T(1, 11.1), outBack);
  return (
    <>
      <FullPhoto
        zoom={zoom}
        cx={cx}
        cy={cy}
        pop={drop ? 0 : 0.04 * intro}
        blur={drop ? 0 : build * 12}
        bright={drop ? 1 : 1 + build * 0.8}
        glitch={g}
        behind={
          !drop && k >= S(0.3) ? (
            <div style={{ position: "absolute", top: 330, left: 0, right: 0, opacity: interpolate(k, [S(5.8), S(6.3)], [1, 0], clamp) }}>
              <WhiteText text="HAMID" size={300} p={ramp(k, S(0.3), S(1.4), Easing.linear)} stagger={0.12} />
            </div>
          ) : undefined
        }
      />
      <LightLeak />
      <Bokeh n={16} seed="p2" />
      {!drop ? (
        <AbsoluteFill style={{ opacity: interpolate(k, [S(5.9), S(6.4)], [1, 0], clamp) }}>
          <div style={{ position: "absolute", bottom: 250, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Line p={at(0.5)} style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 84, color: "#fff" }}>Terima kasih, Pak Hamid</Line>
            <Line p={at(2.2)} style={{ fontFamily: BIG, fontSize: 110, color: "#fff", letterSpacing: 3, marginTop: 10 }}>MOBIL BARU,</Line>
            <Line p={at(2.7)} style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 80, color: "#fff" }}>semangat baru!</Line>
            <Line p={at(3.8, 0.6)} style={{ fontFamily: SANS, fontWeight: 700, fontSize: 38, color: "#fff", marginTop: 14 }}>Semoga lancar rezekinya 🙏</Line>
          </div>
        </AbsoluteFill>
      ) : (
        <AbsoluteFill>
          <div style={{ position: "absolute", top: 160, left: 0, right: 0, transform: `scale(${interpolate(dk, [0, S(0.3)], [1.5, 1], { ...clamp, easing: Easing.out(Easing.cubic) })})` }}>
            <WhiteText text="SELAMAT" size={190} p={ramp(dk, 0, S(0.8), Easing.linear)} stagger={0.07} />
            <div style={{ marginTop: 6 }}>
              <WhiteText text={NAME} size={120} p={ramp(dk, S(0.4), S(1.4), Easing.linear)} stagger={0.05} spacing={3} />
            </div>
          </div>
          <div style={{ position: "absolute", bottom: 90, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
            <Line p={cta} style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, color: "#fff", marginBottom: 14 }}>Giliran Anda berikutnya!</Line>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 18,
                padding: "16px 36px",
                borderRadius: 999,
                background: RED,
                boxShadow: "0 16px 40px rgba(0,0,0,0.45)",
                opacity: Math.min(1, cta * 2),
                transform: `translateY(${(1 - cta) * 40}px) scale(${0.8 + 0.2 * cta})`,
              }}
            >
              <div style={{ fontFamily: BIG, fontSize: 54, color: "#fff", letterSpacing: 3 }}>{DEALER}</div>
              <div style={{ width: 2, height: 46, background: "rgba(255,255,255,0.6)" }} />
              <svg width={46} height={46} viewBox="0 0 100 100">
                <path d="M50 8a42 42 0 0 0-36 63.6L8 92l21-5.6A42 42 0 1 0 50 8z" fill="#fff" />
                <path d="M36 30c-2 0-5 2-5 7 0 6 5 13 11 19s13 11 19 11c5 0 7-3 7-5v-4c0-1-1-2-2-2l-8-3c-1 0-2 0-3 1l-3 3c-5-2-10-7-12-12l3-3c1-1 1-2 1-3l-3-8c0-1-1-2-2-2z" fill={RED} />
              </svg>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 46, color: "#fff" }}>{PHONE}</div>
            </div>
          </div>
          <Firework start={T(1, 7.2)} x={200} y={420} seed="fw5" color={GOLD} />
          <Firework start={T(1, 8.21)} x={880} y={360} seed="fw6" color="#ff5a6e" />
          <Firework start={T(1, 9.0)} x={540} y={230} seed="fw7" color="#ffffff" n={90} />
          <Firework start={T(1, 9.98)} x={260} y={300} seed="fw8" color="#7fd3ff" />
          <Firework start={T(1, 10.59)} x={820} y={500} seed="fw9" color={GOLD} n={90} />
          <Firework start={T(1, 12.19)} x={540} y={380} seed="fw10" color="#ff5a6e" n={100} />
          <Shockwave start={T(1, 6.76)} y={1000} />
          <Confetti3D start={T(1, 6.76)} seed="c2" n={110} y0={900} />
          <Confetti3D start={T(1, 10.59)} seed="c3" n={90} y0={700} />
          <LensFlare start={T(1, 12.3)} dur={S(1.8)} />
        </AbsoluteFill>
      )}
    </>
  );
};

// ------------------------------------------------------------------ komposisi
const SerahTerimaBase: React.FC<{ music: boolean }> = ({ music }) => {
  useFonts();
  const f = useCurrentFrame();
  const endFade = interpolate(f, [SERAH_DUR - S(0.6), SERAH_DUR], [1, 0], clamp);
  const fadeIn = interpolate(f, [0, S(0.2)], [0, 1], clamp);
  const scene = f < T(1, 0) ? <Pass1 /> : <Pass2 />;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <ChannelDefs />
      <AbsoluteFill style={{ opacity: endFade * fadeIn }}>{scene}</AbsoluteFill>
      <Flash />
      <Grain />
      {music && (
        <>
          <Audio src={staticFile("serah/lagu.mp3")} />
          <Sequence from={T(1, 0)} layout="none">
            <Audio src={staticFile("serah/lagu.mp3")} volume={(fr) => interpolate(fr, [S(SONG) - S(0.8), S(SONG)], [1, 0], clamp)} />
          </Sequence>
        </>
      )}
    </AbsoluteFill>
  );
};

export const SerahTerima: React.FC = () => <SerahTerimaBase music />;
export const SerahTerimaPolos: React.FC = () => <SerahTerimaBase music={false} />;
