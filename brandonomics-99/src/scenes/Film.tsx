import React from "react";
import { Audio, interpolate, staticFile, useCurrentFrame } from "remotion";
import { TransitionSeries, springTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";
import { D, SCENE_ORDER, SEQUENCE_DURATION, T } from "../shared/timing";
import * as A1 from "./act1";
import * as A2 from "./act2";
import * as A3 from "./act3";

export { SEQUENCE_DURATION };

const SCENES: Record<(typeof SCENE_ORDER)[number], React.FC> = {
  hook: A1.Hook, brain: A1.Brain, stakes: A1.Stakes, why99: A1.Why99, ch1: A1.Ch1,
  read: A1.Read, impatient: A1.Impatient, grabs: A1.Grabs, study1: A1.Study1, firstdigit: A1.FirstDigit,
  numberline: A1.NumberLine, strange: A1.Strange,
  ch2: A2.Ch2, catalog: A2.Catalog, dresstest: A2.DressTest, newitems: A2.NewItems, cars: A2.Cars,
  odometer: A2.OdometerScene, cliff: A2.Cliff, auction: A2.Auction, ch3: A2.Ch3,
  origin: A3.Origin, register: A3.Register, unproven: A3.Unproven, twenties: A3.Twenties, everywhere: A3.Everywhere,
  ch4: A3.Ch4, luxury: A3.Luxury, champagne: A3.Champagne, hearthead: A3.HeartHead, trick: A3.Trick,
  message: A3.Message, twist: A3.Twist, costume: A3.Costume, challenge: A3.Challenge, comments: A3.Comments,
};

/** Scenes that continue the previous scene's image cross-fade instead of pushing. */
const CONTINUES = new Set(["impatient", "grabs"]);

const Soundtrack: React.FC = () => {
  const frame = useCurrentFrame();
  const volume = interpolate(frame, [0, 6, SEQUENCE_DURATION - 45, SEQUENCE_DURATION], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <Audio src={staticFile("audio/mix.wav")} volume={volume} />;
};

export const NinetyNineFilm: React.FC = () => (
  <>
    <Soundtrack />
    <TransitionSeries>
      {SCENE_ORDER.map((name, i) => {
        const Scene = SCENES[name];
        const last = i === SCENE_ORDER.length - 1;
        const next = SCENE_ORDER[i + 1];
        return (
          <React.Fragment key={name}>
            <TransitionSeries.Sequence durationInFrames={D[name] + (last ? 0 : T)}>
              <Scene />
            </TransitionSeries.Sequence>
            {last ? null : (
              <TransitionSeries.Transition
                presentation={CONTINUES.has(next) ? fade() : slide({ direction: "from-right" })}
                timing={springTiming({ config: { damping: 200 }, durationInFrames: T })}
              />
            )}
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  </>
);
