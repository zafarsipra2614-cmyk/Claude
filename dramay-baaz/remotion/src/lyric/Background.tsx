import React from 'react';
import {AbsoluteFill} from 'remotion';
import {noise2D} from '@remotion/noise';

// soft green "fluid" blobs on white: stacked radial gradients drifting on noise paths (no blur filters, cheap to render)
const BLOBS = [
  {seed: 'a', r: 860, rgb: '56,209,0', a: 0.30, intro: [960, 470], player: [420, 520]},
  {seed: 'b', r: 700, rgb: '140,232,90', a: 0.36, intro: [620, 300], player: [180, 220]},
  {seed: 'c', r: 760, rgb: '31,122,0', a: 0.15, intro: [1320, 760], player: [640, 900]},
  {seed: 'd', r: 640, rgb: '56,209,0', a: 0.16, intro: [1450, 250], player: [1560, 140]},
  {seed: 'e', r: 980, rgb: '195,246,160', a: 0.42, intro: [480, 860], player: [1640, 960]},
];
const Q = 4; // render scale divisor
const g = (rgb: string, a: number) => `rgba(${rgb},${a.toFixed(3)})`;

export const Background: React.FC<{t: number; player: number; loud: number; pulse: number; fade?: number}> = ({t, player, loud, pulse, fade = 1}) => {
  const layers = BLOBS.map((b) => {
    const hx = b.intro[0] + (b.player[0] - b.intro[0]) * player, hy = b.intro[1] + (b.player[1] - b.intro[1]) * player;
    const x = hx + noise2D(b.seed, t * 0.06, 0) * 280, y = hy + noise2D(b.seed, 0, t * 0.06) * 210;
    const R = b.r * (1 + 0.05 * pulse + 0.07 * loud + 0.06 * noise2D(b.seed + 'r', t * 0.1, 3));
    const a = b.a * (0.85 + 0.25 * loud) * fade;
    return `radial-gradient(circle ${(R / Q).toFixed(1)}px at ${(x / Q).toFixed(1)}px ${(y / Q).toFixed(1)}px, ${g(b.rgb, a)} 0%, ${g(b.rgb, a * 0.72)} 30%, ${g(b.rgb, a * 0.38)} 56%, ${g(b.rgb, a * 0.12)} 80%, ${g(b.rgb, 0)} 100%)`;
  });
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <div style={{width: 1920 / Q, height: 1080 / Q, transform: `scale(${Q})`, transformOrigin: '0 0', willChange: 'transform',
        background: layers.join(', ') + ', #FFFFFF'}} />
    </AbsoluteFill>
  );
};
