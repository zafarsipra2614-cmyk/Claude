import React from "react";
import { Audio, interpolate, Series, staticFile, useCurrentFrame } from "remotion";
import { D, SEQUENCE_DURATION } from "../shared/timing";
import { CloserScene, ForumScene, HaltScene, HookScene, MechanismScene, MelvinScene, SqueezeScene, StoreScene } from "./Scenes";

export { SEQUENCE_DURATION };

/**
 * Scene lengths and every cue come from src/shared/timing.ts, generated from
 * vo/timing.json + cues.json. Re-voice, re-run sync_timing.py, re-render.
 */
const BAKE_AUDIO = true;
const AUDIO_TRACK = "audio/mix.mp3";

const Soundtrack: React.FC = () => {
  const frame = useCurrentFrame();
  const volume = interpolate(frame, [0, 10, SEQUENCE_DURATION - 40, SEQUENCE_DURATION], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return <Audio src={staticFile(AUDIO_TRACK)} volume={volume} />;
};

export const GameStopSequence: React.FC = () => (
  <>
    {BAKE_AUDIO ? <Soundtrack /> : null}
    <Series>
      <Series.Sequence durationInFrames={D.hook}><HookScene /></Series.Sequence>
      <Series.Sequence durationInFrames={D.store}><StoreScene /></Series.Sequence>
      <Series.Sequence durationInFrames={D.mechanism}><MechanismScene /></Series.Sequence>
      <Series.Sequence durationInFrames={D.forum}><ForumScene /></Series.Sequence>
      <Series.Sequence durationInFrames={D.squeeze}><SqueezeScene /></Series.Sequence>
      <Series.Sequence durationInFrames={D.melvin}><MelvinScene /></Series.Sequence>
      <Series.Sequence durationInFrames={D.halt}><HaltScene /></Series.Sequence>
      <Series.Sequence durationInFrames={D.closer}><CloserScene /></Series.Sequence>
    </Series>
  </>
);
