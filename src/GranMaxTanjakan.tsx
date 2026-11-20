import "@fontsource/anton/400.css";
import "@fontsource/montserrat/500.css";
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
import data from "./tanjakan.json";

// Cinematic TikTok: Gran Max angkut 2.900 kg sawit di tanjakan. Potongan dikunci ke hentakan lagu.
const FPS = data.fps;
const RED = "#E1001E";
const SANS = "Montserrat, Arial, sans-serif";
const BIG = "Anton, Impact, sans-serif";
const SERIF = "'Playfair Display', Georgia, serif";
const BAR = 104; // tinggi letterbox

type Shot = { f: number; d: number; in: string; zoom?: number; blur?: number; dim?: number; build?: number };
type Txt = { f: number; d: number; style: string; [k: string]: unknown };
const shots = data.shots as Shot[];
const texts = data.texts as unknown as Txt[];
const fmap = data.map as number[];
const cta = data.cta;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.inOut(Easing.cubic);
const outQuint = Easing.out(Easing.poly(5));
const outCubic = Easing.out(Easing.cubic);
const sec = (s: number) => Math.round(s * FPS);
const srcFile = (i: number) => staticFile(`tanjakan/${String(i).padStart(4, "0")}.jpg`);

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load("400 60px Anton"),
      document.fonts.load("500 60px Montserrat"),
      document.fonts.load("600 60px Montserrat"),
      document.fonts.load("700 60px Montserrat"),
      document.fonts.load("800 60px Montserrat"),
      document.fonts.load("italic 400 60px 'Playfair Display'"),
    ]).then(() => continueRender(h));
  }, [h]);
};

// ------------------------------------------------------------------ gambar dengan frame blending
const Frame: React.FC<{ pos: number; style?: React.CSSProperties }> = ({ pos, style }) => {
  const i0 = Math.floor(pos);
  const a = pos - i0;
  const img: React.CSSProperties = { position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" };
  return (
    <AbsoluteFill style={style}>
      <Img src={srcFile(i0)} style={img} />
      {a > 0.04 && <Img src={srcFile(i0 + 1)} style={{ ...img, opacity: a }} />}
    </AbsoluteFill>
  );
};

// pisah kanal RGB (glitch) lewat filter SVG
const ChannelDefs: React.FC = () => (
  <svg width={0} height={0} style={{ position: "absolute" }}>
    <filter id="ch-r"><feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="ch-g"><feColorMatrix type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
    <filter id="ch-b"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" /></filter>
  </svg>
);

const shotAt = (f: number) => {
  let i = 0;
  while (i + 1 < shots.length && shots[i + 1].f <= f) i++;
  return i;
};

const Picture: React.FC = () => {
  const f = useCurrentFrame();
  const i = shotAt(f);
  const s = shots[i];
  const k = f - s.f; // frame sejak potongan
  const nx = shots[i + 1];
  const left = nx ? nx.f - f : 99; // frame menuju potongan berikut
  const dir = i % 2 === 0 ? 1 : -1;

  let scale = 1.12 * (1 + 0.06 * (k / s.d)); // push-in pelan sepanjang shot
  let tx = 0;
  let blur = s.blur ?? 0;
  let bright = 1 - (s.dim ?? 0);
  let opacity = 1;
  let glitch = 0;

  // ---- masuk
  const z = s.zoom ?? 1;
  if (s.in === "black") opacity = interpolate(k, [0, sec(0.5)], [0, 1], { ...clamp, easing: ease });
  if (s.in === "flash" || s.in === "punch") {
    const len = s.in === "punch" ? sec(0.22) : sec(0.45);
    scale *= interpolate(k, [0, len], [z, 1], { ...clamp, easing: outCubic });
    if (s.in === "punch") bright *= interpolate(k, [0, sec(0.15)], [1.35, 1], clamp);
  }
  if (s.in === "whip") {
    const p = interpolate(k, [0, sec(0.16)], [1, 0], { ...clamp, easing: outCubic });
    tx += p * 38 * dir;
    blur += p * 26;
  }
  if (s.in === "glitch") {
    glitch = interpolate(k, [0, sec(0.12)], [1, 0], clamp);
    scale *= z;
  }
  // ---- build-up menuju drop: zoom makin dekat + kabur + terang
  if (s.build) {
    const p = interpolate(k, [0, s.d], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
    scale *= 1 + 0.5 * p;
    blur += 14 * p;
    bright *= 1 + 0.6 * p;
  }
  // ---- keluar (mengikuti transisi shot berikutnya)
  if (nx && nx.in === "whip") {
    const p = interpolate(left, [0, sec(0.14)], [1, 0], { ...clamp, easing: Easing.out(Easing.cubic) }) ** 3;
    tx -= p * 38 * (dir * -1);
    blur += p * 26;
  }

  const pos = fmap[f] ?? fmap[fmap.length - 1];
  const tf = `translateX(${tx}%) scale(${scale})`;
  const grade = `blur(${blur}px) contrast(1.12) saturate(1.08) brightness(${bright})`;
  if (glitch > 0.02) {
    const off = 26 * glitch;
    const layer = (id: string, dx: number): React.CSSProperties => ({ transform: `translateX(${dx}px)`, filter: `url(#${id})`, mixBlendMode: "screen" });
    return (
      <AbsoluteFill style={{ background: "#000", opacity, overflow: "hidden" }}>
        <AbsoluteFill style={{ transform: tf, filter: grade }}>
          <AbsoluteFill style={{ background: "#000" }} />
          <Frame pos={pos} style={layer("ch-r", off)} />
          <Frame pos={pos} style={layer("ch-g", 0)} />
          <Frame pos={pos} style={layer("ch-b", -off)} />
        </AbsoluteFill>
        <AbsoluteFill
          style={{
            opacity: glitch * 0.5,
            background: "repeating-linear-gradient(0deg, rgba(0,0,0,0.5) 0 3px, transparent 3px 7px)",
            transform: `translateY(${random(`gl${f}`) * 40}px)`,
          }}
        />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ background: "#000", opacity, overflow: "hidden" }}>
      <Frame pos={pos} style={{ transform: tf, filter: grade }} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ grading, letterbox, tekstur
const Grade: React.FC = () => (
  <>
    {/* kedalaman: latar atas (pohon jauh) sedikit kabur, seperti lensa tele */}
    <AbsoluteFill
      style={{
        backdropFilter: "blur(13px)",
        WebkitMaskImage: "linear-gradient(to bottom, transparent 6%, #000 12%, #000 33%, transparent 39%)",
        maskImage: "linear-gradient(to bottom, transparent 6%, #000 12%, #000 33%, transparent 39%)",
      }}
    />
    {/* teal & orange */}
    <AbsoluteFill style={{ background: "linear-gradient(170deg, rgba(255,150,60,0.22), rgba(0,0,0,0) 50%, rgba(0,95,120,0.28))", mixBlendMode: "soft-light" }} />
    <AbsoluteFill style={{ background: "rgba(10,40,60,0.18)", mixBlendMode: "multiply" }} />
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 85% 70% at 50% 50%, transparent 45%, rgba(0,0,0,0.55) 100%), linear-gradient(to bottom, rgba(0,0,0,0.45), rgba(0,0,0,0.12) 38%, transparent 55%, rgba(0,0,0,0.55))",
      }}
    />
  </>
);

const Letterbox: React.FC = () => {
  const f = useCurrentFrame();
  const h = BAR * interpolate(f, [0, sec(0.6), cta.f, cta.f + sec(0.6)], [1.6, 1, 1, 0], { ...clamp, easing: ease });
  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: h, background: "#000" }} />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: h, background: "#000" }} />
    </>
  );
};

const Flashes: React.FC = () => {
  const f = useCurrentFrame();
  let a = 0;
  let warm = 0;
  for (const im of data.impacts) {
    const k = f - im.f;
    if (k >= -2 && k < sec(0.5)) {
      a = Math.max(a, im.k * interpolate(k, [-2, 0, sec(0.28)], [0, 0.95, 0], { ...clamp, easing: Easing.out(Easing.quad) }));
      warm = Math.max(warm, im.k * interpolate(k, [0, sec(0.5)], [0.7, 0], clamp));
    }
  }
  return (
    <>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 30% 20%, rgba(255,140,40,0.9), rgba(255,60,0,0) 65%)", mixBlendMode: "screen", opacity: warm }} />
      <AbsoluteFill style={{ background: "#fff", opacity: a }} />
    </>
  );
};

const Grain: React.FC = () => {
  const g = useCurrentFrame();
  const x = Math.floor(random(`gx${Math.floor(g / 2)}`) * 512);
  const y = Math.floor(random(`gy${Math.floor(g / 2)}`) * 512);
  return (
    <AbsoluteFill style={{ backgroundImage: `url(${staticFile("grain.png")})`, backgroundPosition: `${x}px ${y}px`, opacity: 0.08, mixBlendMode: "overlay" }} />
  );
};

// ------------------------------------------------------------------ teks
const shadow = "0 6px 36px rgba(0,0,0,0.55)";

const useInOut = (d: number, outLen = sec(0.2)) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [d - outLen, d], [1, 0], { ...clamp, easing: ease });
  const at = (start: number, len = 0.35) => interpolate(f, [sec(start), sec(start + len)], [0, 1], { ...clamp, easing: outQuint });
  return { f, out, at };
};

const Reveal: React.FC<{ p: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ p, children, style }) => (
  <div style={{ overflow: "hidden", ...style }}>
    <div style={{ transform: `translateY(${(1 - p) * 105}%)` }}>{children}</div>
  </div>
);

const TextBlock: React.FC<{ t: Txt }> = ({ t }) => {
  const { f, out, at } = useInOut(t.d);
  const s = (k: string) => String(t[k] ?? "");

  if (t.style === "pov") {
    return (
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 400, opacity: out, textShadow: shadow }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: 10, color: RED, opacity: at(0, 0.3), marginLeft: 10, background: "#fff", padding: "6px 16px" }}>
          ● REC
        </div>
        <Reveal p={at(0.1, 0.4)} style={{ marginTop: 22 }}>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 62, color: "#fff", whiteSpace: "nowrap" }}>{s("a")}</div>
        </Reveal>
        <Reveal p={at(0.3, 0.4)}>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 64, color: "#fff" }}>{s("b")}</div>
        </Reveal>
      </AbsoluteFill>
    );
  }

  if (t.style === "counter") {
    const v = Number(t.value);
    const p = interpolate(f, [sec(0.05), sec(1.1)], [0, 1], { ...clamp, easing: Easing.out(Easing.exp) });
    const num = Math.round(v * p).toLocaleString("id-ID");
    const pop = interpolate(f, [0, sec(0.25)], [1.35, 1], { ...clamp, easing: outCubic });
    return (
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 330, opacity: out, textShadow: shadow }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 32, letterSpacing: 14, color: "#fff", opacity: at(0.15, 0.3), marginLeft: 14 }}>MUATAN</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 18, transform: `scale(${pop})` }}>
          <div style={{ fontFamily: BIG, fontSize: 250, color: "#fff", lineHeight: 1.05, fontVariantNumeric: "tabular-nums" }}>{num}</div>
          <div style={{ fontFamily: BIG, fontSize: 120, color: RED }}>{s("unit")}</div>
        </div>
        <div style={{ width: 520 * at(0.3, 0.5), height: 6, background: RED, margin: "6px 0 20px" }} />
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 30, letterSpacing: 7, color: "#fff", opacity: at(0.45, 0.4), marginLeft: 7 }}>{s("sub")}</div>
      </AbsoluteFill>
    );
  }

  if (t.style === "lower") {
    const line = at(0, 0.3);
    return (
      <div style={{ position: "absolute", left: 78, top: 400, opacity: out, textShadow: shadow }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16, opacity: at(0.05, 0.3) }}>
          <div style={{ width: 60 * line, height: 6, background: RED }} />
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: 9, color: "#fff" }}>{s("cat")}</div>
        </div>
        <Reveal p={at(0.1, 0.4)} style={{ marginTop: 8 }}>
          <div style={{ fontFamily: BIG, fontSize: 132, color: "#fff", lineHeight: 1.1, whiteSpace: "nowrap", letterSpacing: 2 }}>{s("main")}</div>
        </Reveal>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 38, color: "rgba(255,255,255,0.9)", opacity: at(0.25, 0.4), transform: `translateY(${(1 - at(0.25, 0.4)) * 16}px)` }}>
          {s("sub")}
        </div>
      </div>
    );
  }

  if (t.style === "suspense") {
    const sp = interpolate(f, [0, t.d], [4, 16]);
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: -440, opacity: out * at(0, 0.5), textShadow: shadow }}>
        <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 92, color: "#fff", letterSpacing: sp, whiteSpace: "nowrap" }}>{s("a")}</div>
      </AbsoluteFill>
    );
  }

  if (t.style === "punch") {
    const p = interpolate(f, [0, sec(0.18)], [1.6, 1], { ...clamp, easing: outCubic });
    const drift = interpolate(f, [0, t.d], [1, 1.08]);
    const o = interpolate(f, [0, sec(0.06)], [0, 1], clamp);
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: -470, opacity: o * out }}>
        <div
          style={{
            fontFamily: BIG,
            fontSize: 250,
            color: "#fff",
            letterSpacing: 6,
            transform: `scale(${p * drift})`,
            textShadow: "0 10px 50px rgba(0,0,0,0.6)",
            whiteSpace: "nowrap",
          }}
        >
          {s("w")}
        </div>
        <div style={{ width: 300 * at(0.05, 0.3), height: 8, background: RED, marginTop: -10 }} />
      </AbsoluteFill>
    );
  }

  if (t.style === "statement") {
    return (
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: -450, opacity: out, textShadow: shadow }}>
        <Reveal p={at(0, 0.45)}>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 84, color: "#fff", whiteSpace: "nowrap" }}>{s("a")}</div>
        </Reveal>
        <Reveal p={at(0.2, 0.45)}>
          <div style={{ fontFamily: BIG, fontSize: 190, color: "#fff", letterSpacing: 6, lineHeight: 1.08, whiteSpace: "nowrap" }}>{s("b")}</div>
        </Reveal>
      </AbsoluteFill>
    );
  }

  if (t.style === "hero") {
    const ls = interpolate(f, [0, t.d], [30, 14]);
    return (
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 300, opacity: out, textShadow: shadow }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 38, letterSpacing: 20, color: "#fff", opacity: at(0.05, 0.4), marginLeft: 20 }}>{s("top")}</div>
        <Reveal p={at(0.1, 0.5)}>
          <div style={{ fontFamily: BIG, fontSize: 196, letterSpacing: ls, marginLeft: ls, color: "#fff", lineHeight: 1.1, whiteSpace: "nowrap" }}>{s("main")}</div>
        </Reveal>
        <div style={{ width: 340 * at(0.3, 0.5), height: 6, background: RED, margin: "4px 0 22px" }} />
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 32, letterSpacing: 10, color: "#fff", opacity: at(0.45, 0.4), marginLeft: 10 }}>{s("sub")}</div>
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
  const fadeOut = interpolate(f, [cta.d - sec(0.8), cta.d], [1, 0], { ...clamp, easing: ease });
  const rise = (p: number) => ({ opacity: p, transform: `translateY(${(1 - p) * 26}px)` });
  const [brand1, brand2] = [cta.brand.split(" ")[0], cta.brand.split(" ").slice(1).join(" ")];
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 330, opacity: fadeOut, textShadow: shadow }}>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 36, letterSpacing: 20, color: "#fff", marginLeft: 20, ...rise(at(0.1, 0.4)) }}>{brand1}</div>
      <Reveal p={at(0.15, 0.5)}>
        <div style={{ fontFamily: BIG, fontSize: 200, letterSpacing: 14, color: "#fff", marginLeft: 14, lineHeight: 1.1 }}>{brand2}</div>
      </Reveal>
      <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 56, color: "#fff", ...rise(at(0.35, 0.4)) }}>{cta.tag}</div>

      <div style={{ width: 700 * at(0.5, 0.6), height: 3, background: "rgba(255,255,255,0.6)", margin: "54px 0 44px" }} />

      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 32, letterSpacing: 5, color: "#fff", background: RED, padding: "12px 28px", ...rise(at(0.65, 0.4)) }}>
        {cta.promo[0].toUpperCase()}
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 48, color: "#fff", marginTop: 22, ...rise(at(0.75, 0.4)) }}>{cta.promo.slice(1).join("  ·  ")}</div>

      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 28, letterSpacing: 7, color: "rgba(255,255,255,0.8)", marginTop: 70, ...rise(at(0.95, 0.4)) }}>
        {cta.contact.toUpperCase()}
      </div>
      <div style={{ fontFamily: BIG, fontSize: 110, letterSpacing: 6, color: "#fff", marginTop: 4, ...rise(at(1.05, 0.4)) }}>{cta.name}</div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 20,
          marginTop: 18,
          padding: "16px 42px 16px 22px",
          border: "2px solid rgba(255,255,255,0.85)",
          borderRadius: 999,
          background: "rgba(0,0,0,0.3)",
          ...rise(at(1.15, 0.4)),
        }}
      >
        <WaIcon size={66} />
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 58, letterSpacing: 3, color: "#fff" }}>{cta.phone}</div>
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 24, color: "rgba(255,255,255,0.65)", marginTop: 40, ...rise(at(1.3, 0.4)) }}>{cta.fine}</div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ komposisi
export const GranMaxTanjakan: React.FC = () => {
  useFonts();
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <ChannelDefs />
      <Picture />
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
      <Letterbox />
      <Flashes />
      <Grain />
      <Audio src={staticFile(data.audio)} />
    </AbsoluteFill>
  );
};
