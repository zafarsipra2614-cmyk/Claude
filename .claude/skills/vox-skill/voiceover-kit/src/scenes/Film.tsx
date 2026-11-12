import React from "react";
import { AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame } from "remotion";
import { TransitionSeries, springTiming, type TransitionPresentation } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { fade } from "@remotion/transitions/fade";
import { Paper } from "../shared/system";
import { D, SCENE_ORDER, SEQUENCE_DURATION, T } from "../shared/timing";
import { tornWipe } from "./transitions";
import * as S from "./example";

export { SEQUENCE_DURATION };

/** One component per scene in timeline.json, keyed by scene name. */
const SCENES: Record<(typeof SCENE_ORDER)[number], React.FC> = {
  hook: S.Hook,
  ch1: S.Ch1,
  doc: S.Doc,
  endcard: S.End,
};

/**
 * How each scene arrives. The transition says what kind of step it is:
 *   torn   a new chapter card, or the end screen: a fresh sheet torn across
 *   tear   a reveal / twist: the sheet torn upward
 *   rise   the first scene of a chapter, a new study or section
 *   right  the next step forward within a section
 *   left   going back to something already seen
 *   fade   the same image continues and builds (same layout both sides)
 * The first scene's entry is unused.
 */
type Kind = "torn" | "tear" | "rise" | "right" | "left" | "fade";
const ARRIVAL: Record<(typeof SCENE_ORDER)[number], Kind> = {
  hook: "right",
  ch1: "torn",
  doc: "rise",
  endcard: "torn",
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const presentation = (k: Kind): TransitionPresentation<any> => {
  switch (k) {
    case "torn":
      return tornWipe({ direction: "right" });
    case "tear":
      return tornWipe({ direction: "up" });
    case "rise":
      return slide({ direction: "from-bottom" });
    case "left":
      return slide({ direction: "from-left" });
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

export const Film: React.FC = () => (
  <>
    <Soundtrack />
    {/* paper under everything, so no transition can reveal a bare background */}
    <AbsoluteFill>
      <Paper asset="background.jpg" />
    </AbsoluteFill>
    <TransitionSeries>
      {SCENE_ORDER.map((name, i) => {
        const Scene = SCENES[name];
        const last = i === SCENE_ORDER.length - 1;
        return (
          <React.Fragment key={name}>
            {/* every scene but the last is lengthened by T so, with the overlap, it still starts on its word */}
            <TransitionSeries.Sequence durationInFrames={D[name] + (last ? 0 : T)}>
              <Scene />
            </TransitionSeries.Sequence>
            {last ? null : (
              <TransitionSeries.Transition presentation={presentation(ARRIVAL[SCENE_ORDER[i + 1]])} timing={springTiming({ config: { damping: 200 }, durationInFrames: T })} />
            )}
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  </>
);
