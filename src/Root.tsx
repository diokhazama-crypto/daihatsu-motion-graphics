import { Composition } from "remotion";
import { GranMaxPromo } from "./GranMaxPromo";
import timeline from "./timeline.json";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="GranMaxPromo"
    component={GranMaxPromo}
    durationInFrames={timeline.durationInFrames}
    fps={timeline.fps}
    width={1080}
    height={1920}
  />
);
