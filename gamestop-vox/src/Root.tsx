import React from "react";
import { Composition } from "remotion";
import { GameStopSequence, SEQUENCE_DURATION } from "./scenes/GameStopSequence";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="GameStopSequence"
    component={GameStopSequence}
    durationInFrames={SEQUENCE_DURATION}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{}}
  />
);
