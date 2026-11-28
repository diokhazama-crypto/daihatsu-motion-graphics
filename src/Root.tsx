import { Composition } from "remotion";
import { GranMaxPromo } from "./GranMaxPromo";
import { GranMaxIklan } from "./GranMaxIklan";
import { Data, Sinematik, SigraSinematik } from "./SigraSinematik";
import timeline from "./timeline.json";
import iklan from "./iklan.json";
import sigra from "./sigra.json";
import ayla from "./ayla.json";

const AylaTerang: React.FC = () => <Sinematik data={ayla as Data} terang />;

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
    {/* Ayla: gaya sama dengan SigraTerang, lagu mp3 14 dtk */}
    <Composition id="AylaTerang" component={AylaTerang} durationInFrames={ayla.durationInFrames} fps={ayla.fps} width={1080} height={1920} />
  </>
);
