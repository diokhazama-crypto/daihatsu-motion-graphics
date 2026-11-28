import "@fontsource/montserrat/300.css";
import "@fontsource/montserrat/500.css";
import "@fontsource/montserrat/600.css";
import React, { createContext, useContext, useEffect, useState } from "react";
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
import data from "./sigra.json";
import { Fire, FireSpec, H, Lamp, Light, W, fireEnv } from "./sigraFx";

// Gaya sinematik malam: grading gelap (sudah dibakar di public/clips/sigra.mp4, lihat
// scripts/prep_sigra.py), gerak kamera pelan, efek cahaya & transisi dikunci ke ketukan.
const SANS = "Montserrat, Arial, sans-serif";

type Pt = number[];
type Shot = {
  f: number;
  d: number;
  t: number;
  rate: number;
  inn: string;
  out: string;
  ov: number;
  zoom: number[];
  pan: number;
  mask?: Pt;
  flash?: boolean;
  lights?: Light[];
  fire?: FireSpec;
  shade?: number;
};
const shots = data.shots as Shot[];
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ease = Easing.inOut(Easing.cubic);
const outCubic = Easing.out(Easing.cubic);
const inCubic = Easing.in(Easing.cubic);

const useFonts = () => {
  const [h] = useState(() => delayRender("fonts"));
  useEffect(() => {
    Promise.all([
      document.fonts.load("300 60px Montserrat"),
      document.fonts.load("500 60px Montserrat"),
      document.fonts.load("600 60px Montserrat"),
    ]).then(() => continueRender(h));
  }, [h]);
};

// ------------------------------------------------------------------ varian
// terang = grading mendekati kecerahan asli (public/clips/sigra_terang.mp4) + vignette tipis
const Terang = createContext(false);

// ------------------------------------------------------------------ video
const Clip: React.FC<{ trim: number; rate: number; style?: React.CSSProperties }> = ({ trim, rate, style }) => (
  <OffthreadVideo
    src={staticFile(`clips/${data.clip}${useContext(Terang) ? "_terang" : ""}.mp4`)}
    trimBefore={trim}
    playbackRate={rate}
    muted
    style={{ width: "100%", height: "100%", objectFit: "cover", ...style }}
  />
);

const Shot: React.FC<{ s: Shot; i: number }> = ({ s, i }) => {
  const terang = useContext(Terang);
  const local = useCurrentFrame();
  const f = local - s.ov; // 0 = titik potong (ketukan)
  const left = s.d - f; // sisa frame sampai potongan berikutnya
  const trim = Math.max(0, Math.round(s.t * data.fps - s.ov * s.rate));

  // --- gerak kamera pelan
  const life = interpolate(f, [0, s.d], [0, 1], clamp);
  let scale = interpolate(life, [0, 1], [s.zoom[0], s.zoom[1]], { easing: Easing.inOut(Easing.sin) });
  let tx = s.pan * (life - 0.5) * 2;
  let ty = 0;

  // --- kecerahan / efek masuk
  let bright = 1;
  let blur = 0;
  let whip = 0; // px blur horizontal
  if (s.inn === "fromBlack") bright = interpolate(f, [0, 10], [0, 1], { ...clamp, easing: outCubic });
  if (s.inn === "lightOn") {
    // gelap -> kedip -> menyala (sinkron dengan lampu di sigraFx.lampLevel)
    bright = interpolate(f, [0, 3, 4, 5, 9], [0.35, 0.45, 0.85, 0.5, 1], clamp);
  }
  if (s.inn === "focus") blur = interpolate(f, [0, 16], [22, 0], { ...clamp, easing: ease });
  if (s.inn === "whip") {
    const p = interpolate(f, [0, 5], [1, 0], { ...clamp, easing: outCubic });
    tx += p * 14;
    whip = Math.max(whip, p * 110);
  }

  // --- efek keluar
  if (s.out === "dim") bright *= interpolate(left, [0, 14], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) });
  if (s.out === "whip") {
    const p = interpolate(left, [0, 5], [1, 0], { ...clamp, easing: outCubic });
    tx -= p * 14;
    whip = Math.max(whip, p * 110);
  }
  const stretchP = s.out === "stretch" ? interpolate(left, [0, 7], [1, 0], clamp) : 0;

  // --- drop: flash + lampu hero menyala
  let flashO = 0;
  if (s.flash && f >= 0) {
    flashO = interpolate(f, [0, 1, 8], [0.85, 0.6, 0], { ...clamp, easing: outCubic });
    bright *= interpolate(f, [0, 10], [1.5, 1], clamp);
  }
  // semburan api menerangi seluruh frame
  bright *= 1 + 0.3 * fireEnv(s.fire, f);

  // --- transisi mask: shot ini muncul kecil di dalam lampu shot sebelumnya, lalu membesar
  let maskStyle: React.CSSProperties = {};
  if (s.inn === "mask" && s.mask && f < 0) {
    const p = interpolate(f, [-s.ov, 0], [0, 1], { ...clamp, easing: inCubic });
    const k = interpolate(p, [0, 1], [0.08, 1]);
    const cx = interpolate(p, [0, 1], [s.mask[0], 0.5]);
    const cy = interpolate(p, [0, 1], [s.mask[1], 0.5]);
    maskStyle = {
      transform: `translate(${(cx - 0.5) * W}px, ${(cy - 0.5) * H}px) scale(${k})`,
      borderRadius: 60 / k,
      overflow: "hidden",
    };
  }

  const filterId = `whip${i}`;
  const filters = [
    whip > 0.5 ? `url(#${filterId})` : "",
    blur > 0.1 ? `blur(${blur}px)` : "",
    `brightness(${bright})`,
  ].join(" ");

  // pixel-stretch: satu baris piksel ditarik ke bawah, garisnya naik dari bawah frame
  const sy = interpolate(stretchP, [0, 1], [H * 0.98, H * 0.52], { easing: outCubic });

  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id={filterId} x="-20%" y="0" width="140%" height="100%">
          <feGaussianBlur stdDeviation={`${whip} 0`} edgeMode="duplicate" />
        </filter>
      </svg>
      <AbsoluteFill style={maskStyle}>
        <AbsoluteFill style={{ filter: filters }}>
          <AbsoluteFill style={{ transform: `translate(${tx}%, ${ty}%) scale(${scale})` }}>
            <Clip trim={trim} rate={s.rate} />
            {stretchP > 0 && (
              <AbsoluteFill
                style={{
                  clipPath: `inset(${sy}px 0 ${H - sy - 2}px 0)`,
                  transformOrigin: `50% ${sy}px`,
                  transform: `scaleY(${(H - sy) / 2 + 1})`,
                }}
              >
                <Clip trim={trim} rate={s.rate} />
              </AbsoluteFill>
            )}
            {/* cahaya & api ikut gerak kamera */}
            {(s.lights ?? []).map((l, k) => (
              <Lamp key={k} l={l} f={f} />
            ))}
            {s.fire && <Fire spec={s.fire} f={f} />}
          </AbsoluteFill>
          {s.shade ? (
            <AbsoluteFill
              style={{
                background: `linear-gradient(to bottom, rgba(0,0,0,${s.shade * (terang ? 0.6 : 1)}) 0%, rgba(0,0,0,${s.shade * (terang ? 0.45 : 0.85)}) 30%, transparent 48%)`,
              }}
            />
          ) : null}
        </AbsoluteFill>
      </AbsoluteFill>
      {flashO > 0 && <AbsoluteFill style={{ background: "#fff", opacity: flashO }} />}
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ grading akhir & tekstur
const Grade: React.FC = () => {
  const terang = useContext(Terang);
  return terang ? (
    <>
      {/* vignette tipis saja, gambar tetap terang */}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 95% 75% at 50% 50%, transparent 55%, rgba(0,0,0,0.30) 100%), linear-gradient(to bottom, rgba(0,0,0,0.18), transparent 18%, transparent 78%, rgba(0,0,0,0.30))",
        }}
      />
      <AbsoluteFill style={{ background: "rgba(20,60,70,0.06)", mixBlendMode: "soft-light" }} />
    </>
  ) : (
  <>
    {/* vignette kuat + atas/bawah gelap, seperti lampu parkiran */}
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(ellipse 85% 62% at 50% 52%, transparent 35%, rgba(0,0,0,0.55) 80%, rgba(0,0,0,0.85) 100%), linear-gradient(to bottom, rgba(0,0,0,0.55), transparent 26%, transparent 70%, rgba(0,0,0,0.55))",
      }}
    />
    {/* bayangan sedikit teal */}
    <AbsoluteFill style={{ background: "rgba(20,60,70,0.10)", mixBlendMode: "soft-light" }} />
  </>
  );
};

const Grain: React.FC = () => {
  const g = useCurrentFrame();
  const x = Math.floor(random(`gx${g}`) * 512);
  const y = Math.floor(random(`gy${g}`) * 512);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile("grain.png")})`,
        backgroundPosition: `${x}px ${y}px`,
        opacity: 0.09,
        mixBlendMode: "overlay",
      }}
    />
  );
};

// ------------------------------------------------------------------ judul di drop
const Title: React.FC = () => {
  const f = useCurrentFrame();
  const d = data.title.d;
  const p = interpolate(f, [4, 26], [0, 1], { ...clamp, easing: outCubic });
  const out = interpolate(f, [d - 10, d], [1, 0], { ...clamp, easing: ease });
  const ls = interpolate(f, [4, d], [46, 22]);
  const sub = interpolate(f, [14, 32], [0, 1], { ...clamp, easing: outCubic });
  return (
    <AbsoluteFill style={{ alignItems: "center", paddingTop: 1580, opacity: out, textShadow: "0 0 40px rgba(0,0,0,0.6)" }}>
      {/* bayangan lembut di belakang judul supaya terbaca di lantai terang */}
      <AbsoluteFill style={{ background: "linear-gradient(to bottom, transparent 72%, rgba(0,0,0,0.5) 86%, rgba(0,0,0,0.55))", opacity: p }} />
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 300,
          fontSize: 104,
          letterSpacing: ls,
          marginLeft: ls,
          color: "#fff",
          opacity: p,
          filter: `blur(${(1 - p) * 10}px)`,
          whiteSpace: "nowrap",
        }}
      >
        {data.title.main}
      </div>
      <div style={{ width: 220 * sub, height: 3, background: "#E1061B", margin: "26px 0 24px", boxShadow: "0 0 18px rgba(255,30,30,0.8)" }} />
      <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 28, letterSpacing: 9, marginLeft: 9, color: "rgba(255,255,255,0.85)", opacity: sub }}>
        {data.title.sub}
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ komposisi
export const SigraSinematik: React.FC<{ terang?: boolean }> = ({ terang = false }) => {
  useFonts();
  return (
    <Terang.Provider value={terang}>
    <AbsoluteFill style={{ background: "#000" }}>
      {shots.map((s, i) => (
        <Sequence key={i} from={s.f - s.ov} durationInFrames={s.d + s.ov} layout="none">
          <Shot s={s} i={i} />
        </Sequence>
      ))}
      <Grade />
      <Sequence from={data.title.f} durationInFrames={data.title.d} layout="none">
        <Title />
      </Sequence>
      <Grain />
      <Audio src={staticFile(data.music)} />
    </AbsoluteFill>
    </Terang.Provider>
  );
};
