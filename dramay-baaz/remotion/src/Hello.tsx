import React from 'react';
import {AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// Smoke test: brand colours + official wordmark + a spring-in title.
export const Hello: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, config: {damping: 12}});
  return (
    <AbsoluteFill style={{background: '#0A0E0A', alignItems: 'center', justifyContent: 'center'}}>
      <Img src={staticFile('wordmark_dark.png')} style={{position: 'absolute', top: 40, left: 64, width: 230}} />
      <div style={{color: '#38D100', fontFamily: 'Manrope, sans-serif', fontWeight: 800, fontSize: 220,
        transform: `scale(${s})`, opacity: interpolate(frame, [0, 10], [0, 1])}}>
        DRAMAY BAAZ
      </div>
    </AbsoluteFill>
  );
};
