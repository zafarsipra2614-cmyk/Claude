import React from "react";
import { Composition } from "remotion";
import { Film, SEQUENCE_DURATION } from "./scenes/Film";

// The id must match package.json "video.composition" (used by qc/ and npm run release).
export const RemotionRoot: React.FC = () => (
  <Composition id="Film" component={Film} durationInFrames={SEQUENCE_DURATION} fps={30} width={1920} height={1080} defaultProps={{}} />
);
