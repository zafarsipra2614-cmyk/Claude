import React from "react";
import { Composition } from "remotion";
import { NinetyNineFilm, SEQUENCE_DURATION } from "./scenes/Film";

export const RemotionRoot: React.FC = () => (
  <Composition id="NinetyNineFilm" component={NinetyNineFilm} durationInFrames={SEQUENCE_DURATION} fps={30} width={1920} height={1080} defaultProps={{}} />
);
