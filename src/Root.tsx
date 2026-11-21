import { Composition } from "remotion";
import { GranMaxPromo } from "./GranMaxPromo";
import { GranMaxIklan } from "./GranMaxIklan";
import { GranMaxTanjakan } from "./GranMaxTanjakan";
import { GranMaxKelebihan } from "./GranMaxKelebihan";
import { GranMaxPickup } from "./GranMaxPickup";
import { SerahTerima, SerahTerimaPolos, SERAH_DUR, SERAH_FPS } from "./SerahTerima";
import timeline from "./timeline.json";
import iklan from "./iklan.json";
import tanjakan from "./tanjakan.json";
import kelebihan from "./kelebihan.json";
import pickup from "./pickup.json";

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
    {/* Versi 4: cinematic TikTok tanjakan muatan 2.900 kg, 60 fps */}
    <Composition
      id="GranMaxTanjakan"
      component={GranMaxTanjakan}
      durationInFrames={tanjakan.durationInFrames}
      fps={tanjakan.fps}
      width={1080}
      height={1920}
    />
    {/* Versi 5: iklan profesional 5 kelebihan Gran Max, 60 fps */}
    <Composition
      id="GranMaxKelebihan"
      component={GranMaxKelebihan}
      durationInFrames={kelebihan.durationInFrames}
      fps={kelebihan.fps}
      width={1080}
      height={1920}
    />
    {/* Versi 6: dari showroom sampai kebun (4 klip), 30 fps */}
    <Composition
      id="GranMaxPickup"
      component={GranMaxPickup}
      durationInFrames={pickup.durationInFrames}
      fps={pickup.fps}
      width={1080}
      height={1920}
    />
    {/* Serah terima unit dari 1 foto, 30 fps: dengan lagu & tanpa musik (lagu ditambah di TikTok) */}
    <Composition id="SerahTerima" component={SerahTerima} durationInFrames={SERAH_DUR} fps={SERAH_FPS} width={1080} height={1920} />
    <Composition id="SerahTerimaPolos" component={SerahTerimaPolos} durationInFrames={SERAH_DUR} fps={SERAH_FPS} width={1080} height={1920} />
  </>
);
