import React from 'react';
import {GREEN} from './lib';
/** small mono "code chip" naming the Remotion API on screen */
export const Chip: React.FC<{text: string; dark?: boolean; p?: number}> = ({text, dark = true, p = 1}) => (
  <div style={{position: 'absolute', right: 64, bottom: 56, fontFamily: 'Plex', fontWeight: 700, fontSize: 30,
    padding: '12px 22px', borderRadius: 12, background: dark ? 'rgba(10,14,10,0.85)' : 'rgba(255,255,255,0.9)',
    color: dark ? GREEN : '#0A0E0A', border: `2px solid ${GREEN}`, opacity: p, transform: `translateY(${(1 - p) * 40}px)`}}>
    {text}
  </div>
);
