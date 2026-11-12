import React from "react";
import { AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame } from "remotion";
import { Paper } from "../shared/system";
import { TransitionSeries, springTiming, type TransitionPresentation } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";
import { tornWipe } from "./transitions";
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
  endcard: A3.EndCard,
};

/**
 * How each scene arrives. The transition says what kind of step it is:
 *   torn   a new chapter (or the end screen): a fresh sheet torn across the old one
 *   rise   the first scene of a chapter, a new study or section: the paper rises
 *   right  the next step forward within a section: the camera pans along the sheet
 *   left   going back to something already seen
 *   tear   the twist: the sheet is torn upward instead of across
 *   fade   the same image continues and builds
 */
type Kind = "torn" | "tear" | "rise" | "right" | "left" | "fade";
const ARRIVAL: Record<(typeof SCENE_ORDER)[number], Kind> = {
  hook: "right", brain: "right", stakes: "right", why99: "rise",
  ch1: "torn", read: "rise", impatient: "fade", grabs: "fade", study1: "right", firstdigit: "right", numberline: "right", strange: "rise",
  ch2: "torn", catalog: "rise", dresstest: "right", newitems: "right", cars: "rise", odometer: "right", cliff: "right", auction: "right",
  ch3: "torn", origin: "rise", register: "right", unproven: "left", twenties: "rise", everywhere: "right",
  ch4: "torn", luxury: "rise", champagne: "right", hearthead: "right", trick: "rise", message: "right",
  twist: "tear", costume: "right", challenge: "rise", comments: "right", endcard: "torn",
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const presentation = (k: Kind): TransitionPresentation<any> => {
  switch (k) {
    case "torn":
      return tornWipe({ direction: "right" });
    case "rise":
      return slide({ direction: "from-bottom" });
    case "left":
      return slide({ direction: "from-left" });
    case "tear":
      return tornWipe({ direction: "up" });
    case "fade":
      return fade();
    default:
      return slide({ direction: "from-right" });
  }
};

const Soundtrack: React.FC = () => {
  const frame = useCurrentFrame();
  const volume = interpolate(frame, [0, 6, SEQUENCE_DURATION - 45, SEQUENCE_DURATION], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <Audio src={staticFile("audio/mix.wav")} volume={volume} />;
};

export const NinetyNineFilm: React.FC = () => (
  <>
    <Soundtrack />
    {/* paper under everything, so no transition can ever reveal a bare background */}
    <AbsoluteFill>
      <Paper asset="background.jpg" />
    </AbsoluteFill>
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
                presentation={presentation(ARRIVAL[next])}
                timing={springTiming({ config: { damping: 200 }, durationInFrames: T })}
              />
            )}
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  </>
);
