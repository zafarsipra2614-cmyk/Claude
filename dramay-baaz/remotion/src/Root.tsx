import React from 'react';
import {Composition} from 'remotion';
import {Hello} from './Hello';
import {Probe} from './Probe';
import {Sample, SAMPLE_FRAMES} from './reel/Sample';

// 1920x1080 @ 60 fps, full song length (159.42 s)
export const RemotionRoot: React.FC = () => (
  <>
  <Composition id="Sample" component={Sample} durationInFrames={SAMPLE_FRAMES} fps={60} width={1920} height={1080} />
  <Composition id="Probe" component={Probe} durationInFrames={70} fps={60} width={1920} height={1080} />
  <Composition id="Hello" component={Hello} durationInFrames={180} fps={60} width={1920} height={1080} />
  </>
);
