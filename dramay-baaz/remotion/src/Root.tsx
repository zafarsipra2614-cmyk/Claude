import React from 'react';
import {Composition} from 'remotion';
import {Hello} from './Hello';

// 1920x1080 @ 60 fps, full song length (159.42 s)
export const RemotionRoot: React.FC = () => (
  <Composition id="Hello" component={Hello} durationInFrames={180} fps={60} width={1920} height={1080} />
);
