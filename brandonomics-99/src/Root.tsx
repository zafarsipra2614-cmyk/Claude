import React from "react";
import { Composition } from "remotion";
import { NinetyNineFilm, SEQUENCE_DURATION } from "./scenes/Film";
import { THUMB_FRAME, Thumbnail } from "./scenes/Thumbnail";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="NinetyNineFilm" component={NinetyNineFilm} durationInFrames={SEQUENCE_DURATION} fps={30} width={1920} height={1080} defaultProps={{}} />
    <Composition id="Thumbnail" component={Thumbnail} durationInFrames={THUMB_FRAME + 1} fps={30} width={1920} height={1080} defaultProps={{}} />
  </>
);
