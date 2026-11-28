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
import { H, Lamp, Light, W } from "./sigraFx";

// Gaya sinematik: footage sudah di-grade (scripts/prep_sigra.py), gerak kamera pelan,
// lampu menyala, transisi bervariasi yang berpusat di ketukan, teks gaya judul.
const SANS = "Montserrat, Arial, sans-serif";
const RED = "#E1061B";

type Pt = number[];
type Tin = { kind: string; n: number; dir: string };
type Shot = {
  f: number;
  d: number;
  t: number;
  rate: number;
  tin: Tin;
  fx: string[];
  zoom: number[];
  pan: number;
  pre: number;
  post: number;
  mask?: Pt;
  shade?: number;
  lights?: Light[];
};
type Txt = { f: number; d: number; main: string; sub: string; pos: string; big: boolean };
const shots = data.shots as Shot[];
const texts = data.texts as Txt[];

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const eio = Easing.inOut(Easing.cubic);
const ein = Easing.in(Easing.cubic);
const eout = Easing.out(Easing.cubic);
const c01 = (x: number) => Math.min(1, Math.max(0, x));
const bell = (p: number) => Math.sin(Math.PI * c01(p));
// kecepatan sesaat dari kurva eio (untuk motion blur)
const speed = (p: number) => (eio(c01(p + 0.02)) - eio(c01(p - 0.02))) / 0.04;

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

// terang = grading mendekati kecerahan asli (public/clips/sigra_terang.mp4) + vignette tipis
const Terang = createContext(false);

const Clip: React.FC<{ trim: number; rate: number }> = ({ trim, rate }) => (
  <OffthreadVideo
    src={staticFile(`clips/${data.clip}${useContext(Terang) ? "_terang" : ""}.mp4`)}
    trimBefore={trim}
    playbackRate={rate}
    muted
    style={{ width: "100%", height: "100%", objectFit: "cover" }}
  />
);

// ------------------------------------------------------------------ transisi
// Satu lapisan transisi: digabung dari efek masuk (shot ini) & efek keluar (transisi shot berikutnya)
type Tf = { x: number; y: number; s: number; r: number; o: number; bx: number; by: number; b: number; br: number };
const ID: Tf = { x: 0, y: 0, s: 1, r: 0, o: 1, bx: 0, by: 0, b: 0, br: 1 };
const DIRV: Record<string, [number, number]> = { l: [-1, 0], r: [1, 0], u: [0, -1], d: [0, 1] };

const tfIn = (t: Tin, p: number): Tf => {
  const o = { ...ID };
  if (p >= 1 || t.kind === "cut" || t.kind === "mask" || t.kind === "slice") return o;
  if (t.kind === "push") {
    const [vx, vy] = DIRV[t.dir] ?? DIRV.l;
    const e = eio(p);
    o.x = -vx * W * (1 - e);
    o.y = -vy * H * (1 - e);
    const v = Math.min(140, (speed(p) * (vx ? W : H)) / t.n * 0.45);
    if (vx) o.bx = v;
    else o.by = v;
  } else if (t.kind === "zoom") {
    const u = c01((p - 0.4) / 0.6);
    o.o = eio(c01((p - 0.4) / 0.2));
    o.s = 1 + 0.45 * (1 - eout(u));
    o.b = 18 * (1 - eout(u));
    o.br = 1 + 0.3 * (1 - u);
  } else if (t.kind === "spin") {
    const u = c01((p - 0.4) / 0.6);
    const sg = t.dir === "r" ? -1 : 1;
    o.o = eio(c01((p - 0.4) / 0.2));
    o.r = -sg * 14 * (1 - eout(u));
    o.s = 1 + 0.42 * (1 - eout(u));
    o.b = 14 * (1 - eout(u));
  } else if (t.kind === "leak") {
    o.o = eio(c01((p - 0.25) / 0.5));
    o.br = 1 + 0.6 * (1 - c01((p - 0.3) / 0.7));
    o.s = 1 + 0.05 * (1 - eout(p));
  } else if (t.kind === "blur") {
    o.o = eio(p);
    o.b = 14 * bell(p);
    o.s = 1 + 0.05 * (1 - eout(p));
  }
  return o;
};

const tfOut = (t: Tin, p: number): Tf => {
  const o = { ...ID };
  if (p <= 0 || t.kind === "cut" || t.kind === "mask") return o;
  if (t.kind === "push") {
    const [vx, vy] = DIRV[t.dir] ?? DIRV.l;
    const e = eio(p);
    o.x = vx * W * e;
    o.y = vy * H * e;
    const v = Math.min(140, (speed(p) * (vx ? W : H)) / t.n * 0.45);
    if (vx) o.bx = v;
    else o.by = v;
  } else if (t.kind === "zoom") {
    const u = c01(p / 0.6);
    o.s = 1 + 0.7 * ein(u);
    o.b = 18 * ein(u);
    o.br = 1 + 0.3 * ein(u);
  } else if (t.kind === "spin") {
    const u = c01(p / 0.6);
    const sg = t.dir === "r" ? -1 : 1;
    o.r = sg * 14 * ein(u);
    o.s = 1 + 0.42 * ein(u);
    o.b = 14 * ein(u);
  } else if (t.kind === "slice") {
    o.s = 1 + 0.06 * eio(p);
    o.br = 1 - 0.25 * eio(p);
  } else if (t.kind === "leak") {
    o.br = 1 + 0.6 * eio(c01(p / 0.6));
  } else if (t.kind === "blur") {
    o.b = 14 * bell(p);
  }
  return o;
};

const join = (a: Tf, b: Tf): Tf => ({
  x: a.x + b.x,
  y: a.y + b.y,
  s: a.s * b.s,
  r: a.r + b.r,
  o: a.o * b.o,
  bx: Math.max(a.bx, b.bx),
  by: Math.max(a.by, b.by),
  b: Math.max(a.b, b.b),
  br: a.br * b.br,
});

// bilah-bilah vertikal naik dari bawah berurutan kiri -> kanan (wipe bertangga)
const SLICES = 5;
const SliceClip: React.FC<{ id: string; p: number }> = ({ id, p }) => {
  const w = W / SLICES;
  return (
    <svg width={0} height={0} style={{ position: "absolute" }}>
      <clipPath id={id} clipPathUnits="userSpaceOnUse">
        {Array.from({ length: SLICES }, (_, j) => {
          const q = eio(c01((p - j * 0.1) / (1 - 0.1 * (SLICES - 1))));
          const h = q * H;
          return <rect key={j} x={j * w - 0.5} y={H - h} width={w + 1} height={h} />;
        })}
      </clipPath>
    </svg>
  );
};

// garis cahaya di ujung atas tiap bilah slice
const SliceEdges: React.FC<{ p: number }> = ({ p }) => {
  const w = W / SLICES;
  return (
    <svg width={W} height={H} style={{ position: "absolute", inset: 0, mixBlendMode: "screen", filter: "blur(2px)" }}>
      {Array.from({ length: SLICES }, (_, j) => {
        const q = eio(c01((p - j * 0.1) / (1 - 0.1 * (SLICES - 1))));
        if (q <= 0.01 || q >= 0.99) return null;
        return <rect key={j} x={j * w} y={H - q * H - 3} width={w} height={6} fill="rgba(255,245,235,0.9)" />;
      })}
    </svg>
  );
};

// cahaya hangat menyapu layar (transisi leak)
const Leak: React.FC<{ p: number }> = ({ p }) => {
  const k = bell(p);
  if (k < 0.01) return null;
  const x = -20 + 140 * eio(p);
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: "screen",
        opacity: k,
        background: `radial-gradient(ellipse 900px 1400px at ${x}% 40%, rgba(255,175,95,0.85), rgba(255,110,60,0.35) 45%, rgba(255,80,40,0) 75%), radial-gradient(ellipse 600px 900px at ${x + 25}% 75%, rgba(255,215,160,0.6), rgba(255,215,160,0) 70%), rgba(255,240,225,${0.25 * k})`,
      }}
    />
  );
};

// ------------------------------------------------------------------ shot
const ShotView: React.FC<{ s: Shot; i: number }> = ({ s, i }) => {
  const terang = useContext(Terang);
  const g = useCurrentFrame();
  const f = g - s.pre; // 0 = titik potong (ketukan)
  const trim = Math.max(0, Math.round(s.t * data.fps - s.pre * s.rate));
  const next = shots[i + 1]?.tin ?? { kind: "cut", n: 0, dir: "l" };

  // progres transisi masuk & keluar (0..1)
  const pIn = s.tin.n > 0 ? c01((f + s.pre) / s.tin.n) : 1;
  const nPre = next.kind === "mask" ? 0 : Math.floor(next.n / 2);
  const pOut = next.n > 0 && next.kind !== "mask" ? c01((f - (s.d - nPre)) / next.n) : 0;
  const tf = join(tfIn(s.tin, pIn), tfOut(next, pOut));

  // gerak kamera pelan di dalam shot
  const life = interpolate(f, [0, s.d], [0, 1], clamp);
  const cam = interpolate(life, [0, 1], [s.zoom[0], s.zoom[1]], { easing: Easing.inOut(Easing.sin) });
  const pan = s.pan * (life - 0.5) * 2;

  // efek khusus
  let bright = tf.br;
  let blur = tf.b;
  let flashO = 0;
  if (s.fx.includes("lightOn")) bright *= interpolate(f, [0, 3, 4, 5, 9], [0.35, 0.45, 0.85, 0.5, 1], clamp);
  if (s.fx.includes("focus")) blur = Math.max(blur, interpolate(f, [0, 16], [22, 0], { ...clamp, easing: eio }));
  if (s.fx.includes("flash") && f >= 0) {
    flashO = interpolate(f, [0, 1, 8], [0.85, 0.6, 0], { ...clamp, easing: eout });
    bright *= interpolate(f, [0, 10], [1.5, 1], clamp);
  }

  // transisi mask: shot ini muncul kecil di dalam lampu shot sebelumnya, lalu membesar
  let maskStyle: React.CSSProperties = {};
  if (s.tin.kind === "mask" && s.mask && f < 0) {
    const p = interpolate(f, [-s.tin.n, 0], [0, 1], { ...clamp, easing: ein });
    const k = interpolate(p, [0, 1], [0.08, 1]);
    const cx = interpolate(p, [0, 1], [s.mask[0], 0.5]);
    const cy = interpolate(p, [0, 1], [s.mask[1], 0.5]);
    maskStyle = {
      transform: `translate(${(cx - 0.5) * W}px, ${(cy - 0.5) * H}px) scale(${k})`,
      borderRadius: 60 / k,
      overflow: "hidden",
    };
  }

  const sliceId = `slice${i}`;
  const blurId = `dblur${i}`;
  const filters = [
    tf.bx > 0.5 || tf.by > 0.5 ? `url(#${blurId})` : "",
    blur > 0.1 ? `blur(${blur}px)` : "",
    Math.abs(bright - 1) > 0.001 ? `brightness(${bright})` : "",
  ].join(" ");
  const slicing = s.tin.kind === "slice" && pIn < 1;

  return (
    <AbsoluteFill style={{ overflow: "hidden", opacity: tf.o, clipPath: slicing ? `url(#${sliceId})` : undefined }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id={blurId} x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur stdDeviation={`${tf.bx} ${tf.by}`} edgeMode="duplicate" />
        </filter>
      </svg>
      {slicing && <SliceClip id={sliceId} p={pIn} />}
      <AbsoluteFill style={maskStyle}>
        <AbsoluteFill
          style={{
            transform: `translate(${tf.x}px, ${tf.y}px) rotate(${tf.r}deg) scale(${tf.s * (slicing ? 1 + 0.08 * (1 - eout(pIn)) : 1)})`,
            filter: filters || undefined,
          }}
        >
          <AbsoluteFill style={{ transform: `translateX(${pan}%) scale(${cam})` }}>
            <Clip trim={trim} rate={s.rate} />
            {(s.lights ?? []).map((l, k) => (
              <Lamp key={k} l={l} f={f} />
            ))}
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
      {s.tin.kind === "leak" && pIn < 1 && <Leak p={pIn} />}
      {slicing && <SliceEdges p={pIn} />}
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

// ------------------------------------------------------------------ teks gaya judul
// huruf muncul satu per satu (naik + blur hilang), tracking merapat pelan, garis merah memanjang,
// keluar dengan blur + tracking melebar
const Caption: React.FC<{ t: Txt }> = ({ t }) => {
  const f = useCurrentFrame();
  const size = t.big ? 104 : 74;
  const lsFrom = t.big ? 46 : 34;
  const lsTo = t.big ? 22 : 16;
  const outP = interpolate(f, [t.d - 10, t.d], [0, 1], { ...clamp, easing: ein });
  const ls = interpolate(f, [0, t.d], [lsFrom, lsTo]) + outP * 18;
  const line = interpolate(f, [8, 28], [0, 1], { ...clamp, easing: eout }) * (1 - outP);
  const sub = interpolate(f, [14, 32], [0, 1], { ...clamp, easing: eout });
  const top = t.pos === "top";
  const back = interpolate(f, [0, 12, t.d - 8, t.d], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill>
      {/* bayangan lembut supaya teks terbaca di footage terang */}
      <AbsoluteFill
        style={{
          opacity: back,
          background: top
            ? "linear-gradient(to bottom, rgba(0,0,0,0.55), rgba(0,0,0,0.42) 14%, transparent 30%)"
            : "linear-gradient(to bottom, transparent 70%, rgba(0,0,0,0.42) 84%, rgba(0,0,0,0.58))",
        }}
      />
      <AbsoluteFill
        style={{
          alignItems: "center",
          paddingTop: top ? 250 : t.big ? 1580 : 1600,
          opacity: 1 - outP,
          filter: outP > 0 ? `blur(${outP * 10}px)` : undefined,
          transform: `translateY(${-outP * 14}px)`,
          textShadow: "0 0 40px rgba(0,0,0,0.6)",
        }}
      >
        <div style={{ display: "flex", fontFamily: SANS, fontWeight: 300, fontSize: size, color: "#fff", whiteSpace: "pre", marginLeft: ls }}>
          {t.main.split("").map((ch, k) => {
            const p = interpolate(f, [2 + k * 1.3, 16 + k * 1.3], [0, 1], { ...clamp, easing: eout });
            return (
              <span
                key={k}
                style={{
                  display: "inline-block",
                  marginRight: ls,
                  opacity: p,
                  transform: `translateY(${(1 - p) * 34}px)`,
                  filter: p < 1 ? `blur(${(1 - p) * 10}px)` : undefined,
                }}
              >
                {ch}
              </span>
            );
          })}
        </div>
        <div style={{ width: (t.big ? 220 : 160) * line, height: 3, background: RED, margin: t.big ? "26px 0 24px" : "20px 0 20px", boxShadow: "0 0 18px rgba(255,30,30,0.8)" }} />
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 500,
            fontSize: t.big ? 28 : 26,
            letterSpacing: 9,
            marginLeft: 9,
            color: "rgba(255,255,255,0.9)",
            opacity: sub,
            transform: `translateY(${(1 - sub) * 12}px)`,
          }}
        >
          {t.sub}
        </div>
      </AbsoluteFill>
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
          <Sequence key={i} from={s.f - s.pre} durationInFrames={s.pre + s.d + s.post} layout="none">
            <ShotView s={s} i={i} />
          </Sequence>
        ))}
        <Grade />
        {texts.map((t, i) => (
          <Sequence key={`t${i}`} from={t.f} durationInFrames={t.d} layout="none">
            <Caption t={t} />
          </Sequence>
        ))}
        <Grain />
        <Audio src={staticFile(data.music)} />
      </AbsoluteFill>
    </Terang.Provider>
  );
};
