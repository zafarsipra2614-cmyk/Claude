import React from "react";
import { AbsoluteFill } from "remotion";
import type { TransitionPresentation, TransitionPresentationComponentProps } from "@remotion/transitions";
import { C } from "../shared/system";

/**
 * Torn-paper wipe: the incoming scene is a sheet torn along a ragged edge,
 * pulled across the old one, with the film's red marker line riding the tear.
 */
type TornProps = { direction: "right" | "up" };

const rnd = (i: number) => {
  const x = Math.sin(i * 91.7 + 13.1) * 43758.5453;
  return x - Math.floor(x);
};

const W = 1920;
const H = 1080;
const JAG = 46; // depth of the tear
const STEPS = 22;

/** Polygon covering everything behind a ragged edge positioned at `pos`. */
const tornPolygon = (dir: "right" | "up", pos: number, extra = 0) => {
  const pts: string[] = [];
  if (dir === "right") {
    // covered region: x from 0 to the edge
    pts.push("0px 0px");
    for (let i = 0; i <= STEPS; i++) {
      const y = (i / STEPS) * H;
      const x = pos + extra + (rnd(i) - 0.5) * JAG;
      pts.push(`${x.toFixed(1)}px ${y.toFixed(1)}px`);
    }
    pts.push(`0px ${H}px`);
  } else {
    // covered region: y from the edge down to the bottom
    pts.push(`0px ${H}px`);
    for (let i = 0; i <= STEPS; i++) {
      const x = (i / STEPS) * W;
      const y = pos - extra + (rnd(i + 40) - 0.5) * JAG;
      pts.push(`${x.toFixed(1)}px ${y.toFixed(1)}px`);
    }
    pts.push(`${W}px ${H}px`);
  }
  return `polygon(${pts.join(", ")})`;
};

const TornWipe: React.FC<TransitionPresentationComponentProps<TornProps>> = ({ children, presentationDirection, presentationProgress, passedProps }) => {
  if (presentationDirection === "exiting") return <AbsoluteFill>{children}</AbsoluteFill>;
  const dir = passedProps.direction;
  const p = presentationProgress;
  const span = dir === "right" ? W : H;
  // edge travels from just outside one side to just past the other
  const pos = dir === "right" ? -JAG + p * (span + 2 * JAG) : span + JAG - p * (span + 2 * JAG);
  return (
    <AbsoluteFill>
      {/* the red marker stroke that rides just ahead of the tear */}
      <AbsoluteFill style={{ background: C.red, clipPath: tornPolygon(dir, pos, 12) }} />
      <AbsoluteFill style={{ filter: "drop-shadow(0 0 14px rgba(55,45,31,0.35))" }}>
        <AbsoluteFill style={{ clipPath: tornPolygon(dir, pos) }}>{children}</AbsoluteFill>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const tornWipe = (props: TornProps = { direction: "right" }): TransitionPresentation<TornProps> => ({ component: TornWipe, props });
