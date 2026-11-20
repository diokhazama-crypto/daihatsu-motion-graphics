import { Composition } from "remotion";
import { GranMaxPromo } from "./GranMaxPromo";
import { GranMaxIklan } from "./GranMaxIklan";
import { GranMaxTanjakan } from "./GranMaxTanjakan";
import { GranMaxKelebihan } from "./GranMaxKelebihan";
import timeline from "./timeline.json";
import iklan from "./iklan.json";
import tanjakan from "./tanjakan.json";
import kelebihan from "./kelebihan.json";

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
  </>
);
