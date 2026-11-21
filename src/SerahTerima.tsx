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
// teks putih polos. Gaya modern/premium: zoom halus, teks di belakang orang (orang dipisah dari latar),
// garis cahaya anamorfik, light leak, bingkai sudut tipis. Tanpa blur (supaya potongan orang tetap rapi).
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
// garis cahaya anamorfik (gaya lensa sinema): garis horizontal tipis biru-putih + inti lembut
const Anamorphic: React.FC<{ start: number; dur?: number; y?: number }> = ({ start, dur = S(1.4), y = 560 }) => {
  const f = useCurrentFrame();
  const k = f - start;
  if (k < 0 || k > dur) return null;
  const p = k / dur;
  const x = interpolate(p, [0, 1], [-200, 1280], { easing: Easing.inOut(Easing.sin) });
  const a = Math.sin(p * Math.PI);
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen", pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: x - 900, top: y - 3, width: 1800, height: 6, background: "linear-gradient(to right, transparent, rgba(120,180,255,0.85) 40%, rgba(255,255,255,1) 50%, rgba(120,180,255,0.85) 60%, transparent)", opacity: a, filter: "blur(1.5px)" }} />
      <div style={{ position: "absolute", left: x - 900, top: y - 18, width: 1800, height: 36, background: "linear-gradient(to right, transparent, rgba(90,150,255,0.35) 45%, rgba(90,150,255,0.35) 55%, transparent)", opacity: a, filter: "blur(10px)" }} />
      <div style={{ position: "absolute", left: x - 140, top: y - 140, width: 280, height: 280, borderRadius: 999, background: "radial-gradient(circle, rgba(255,255,255,0.9), rgba(160,200,255,0.25) 35%, transparent 65%)", opacity: a }} />
    </AbsoluteFill>
  );
};

const Flash: React.FC = () => {
  const f = useCurrentFrame();
  let a = 0;
  for (const [h, k] of HITS) a = Math.max(a, k * interpolate(f, [h - 1, h, h + S(0.3)], [0, 0.7, 0], { ...clamp, easing: Easing.out(Easing.quad) }));
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

// ------------------------------------------------------------------ teks putih polos: muncul dari balik masker, blur -> tajam
const WhiteText: React.FC<{ text: string; size: number; p: number; stagger?: number; spacing?: number; color?: string }> = ({ text, size, p, stagger = 0.05, spacing = 4, color = "#fff" }) => (
  <div style={{ display: "flex", justifyContent: "center", whiteSpace: "pre", filter: "drop-shadow(0 6px 22px rgba(0,0,0,0.5))" }}>
    {text.split("").map((ch, i) => {
      const q = interpolate(p, [i * stagger, i * stagger + 0.4], [0, 1], { ...clamp, easing: outQuint });
      return (
        <div key={i} style={{ overflow: "hidden", padding: "0 1px" }}>
          <div
            style={{
              fontFamily: BIG,
              fontSize: size,
              lineHeight: 1.08,
              letterSpacing: spacing,
              color,
              opacity: Math.min(1, q * 1.5),
              transform: `translateY(${(1 - q) * 100}%)`,
              filter: `blur(${(1 - q) * 10}px)`,
            }}
          >
            {ch}
          </div>
        </div>
      );
    })}
  </div>
);

// bingkai sudut tipis (gaya editorial / viewfinder)
const Corners: React.FC = () => {
  const f = useCurrentFrame();
  const p = ramp(f, S(0.2), S(1.0));
  const arm = 70 * p;
  const m = 46;
  const st = (pos: React.CSSProperties, bt: string, bl: string): React.CSSProperties => ({ position: "absolute", width: arm, height: arm, [bt]: "2px solid rgba(255,255,255,0.7)", [bl]: "2px solid rgba(255,255,255,0.7)", ...pos });
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={st({ left: m, top: m }, "borderTop", "borderLeft")} />
      <div style={st({ right: m, top: m }, "borderTop", "borderRight")} />
      <div style={st({ left: m, bottom: m }, "borderBottom", "borderLeft")} />
      <div style={st({ right: m, bottom: m }, "borderBottom", "borderRight")} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ foto full layar
// zoom: skala; cx/cy: titik fokus zoom (piksel layar); pop: orang sedikit lebih dekat dari latar
const FullPhoto: React.FC<{ zoom: number; cx?: number; cy?: number; pop?: number; blur?: number; bright?: number; behind?: React.ReactNode }> = ({
  zoom,
  cx = 540,
  cy = 1150,
  pop = 0,
  blur = 0,
  bright = 1,
  behind,
}) => {
  const layered = !!behind;
  const filter = (extraBlur = 0) => `blur(${blur + extraBlur}px) brightness(${bright}) contrast(1.05) saturate(1.08)`;
  const img = (extra = 1, extraBlur = 0): React.CSSProperties => ({
    position: "absolute",
    width: 1440,
    height: 1920,
    left: -180,
    top: 0,
    transformOrigin: `${cx + 180}px ${cy}px`,
    transform: `scale(${zoom * extra})`,
    filter: filter(extraBlur),
  });
  const body = (z = 1) => (
    <AbsoluteFill style={{ overflow: "hidden", transform: `scale(${z})` }}>
      {layered ? (
        <>
          <Img src={PHOTO} style={img()} />
          {behind}
          <Img src={FG} style={img(1 + pop)} />
        </>
      ) : (
        <Img src={PHOTO} style={img()} />
      )}
    </AbsoluteFill>
  );
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {body()}
      <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.4), transparent 24%, transparent 58%, rgba(0,0,0,0.6))" }} />
    </AbsoluteFill>
  );
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
  const behindOut = interpolate(f, [S(5.8), S(6.3)], [1, 0], clamp);
  const ty = ramp(f, S(12.19), S(12.7));
  return (
    <>
      <FullPhoto
        zoom={zoom}
        pop={drop ? 0 : 0.05 * intro}
        bright={drop ? 1 : 1 + build * 0.8}
        behind={
          !drop ? (
            <div style={{ position: "absolute", top: 340, left: 0, right: 0, opacity: behindOut }}>
              <WhiteText text="SELAMAT" size={235} p={ramp(f, S(0.15), S(1.5), Easing.linear)} stagger={0.1} spacing={2} />
            </div>
          ) : undefined
        }
      />
      <LightLeak />
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
          <Anamorphic start={S(12.19)} />
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
  const cta = ramp(f, T(1, 10.59), T(1, 11.1), outBack);
  return (
    <>
      <FullPhoto
        zoom={zoom}
        cx={cx}
        cy={cy}
        pop={drop ? 0 : 0.04 * intro}
        bright={drop ? 1 : 1 + build * 0.8}
        behind={
          !drop && k >= S(0.3) ? (
            <div style={{ position: "absolute", top: 330, left: 0, right: 0, opacity: interpolate(k, [S(5.8), S(6.3)], [1, 0], clamp) }}>
              <WhiteText text="HAMID" size={300} p={ramp(k, S(0.3), S(1.4), Easing.linear)} stagger={0.12} />
            </div>
          ) : undefined
        }
      />
      <LightLeak />
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
          <Anamorphic start={T(1, 12.3)} />
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
      <AbsoluteFill style={{ opacity: endFade * fadeIn }}>{scene}</AbsoluteFill>
      <AbsoluteFill style={{ opacity: endFade }}>
        <Corners />
      </AbsoluteFill>
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
