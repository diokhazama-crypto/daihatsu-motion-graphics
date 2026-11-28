import { Composition } from "remotion";
import { GranMaxPromo } from "./GranMaxPromo";
import { GranMaxIklan } from "./GranMaxIklan";
import { SigraSinematik } from "./SigraSinematik";
import timeline from "./timeline.json";
import iklan from "./iklan.json";
import sigra from "./sigra.json";

export const RemotionRoot: React.FC = () => (
  <>
    {/* Versi 1-2: jedag jedug TikTok, sinkron lagu */}
    <Composition
      id="GranMaxPromo"
      component={GranMaxPromo}
      durationInFrames={timeline.durationInFrames}
      fps={timeline.fps}
      width={1080}
      height={1920}
    />
    {/* Versi 3: iklan profesional, musik cinematic */}
    <Composition
      id="GranMaxIklan"
      component={GranMaxIklan}
      durationInFrames={iklan.durationInFrames}
      fps={iklan.fps}
      width={1080}
      height={1920}
    />
    {/* Sigra: gaya sinematik malam (meniru video referensi) */}
    <Composition
      id="SigraSinematik"
      component={SigraSinematik}
      durationInFrames={sigra.durationInFrames}
      fps={sigra.fps}
      width={1080}
      height={1920}
    />
    {/* Sigra versi terang: efek & potongan sama, grading tidak segelap */}
    <Composition
      id="SigraTerang"
      component={SigraSinematik}
      defaultProps={{ terang: true }}
      durationInFrames={sigra.durationInFrames}
      fps={sigra.fps}
      width={1080}
      height={1920}
    />
  </>
);
