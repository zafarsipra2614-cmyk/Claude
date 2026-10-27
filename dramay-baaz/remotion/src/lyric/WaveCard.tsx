import React from 'react';
import {Img, staticFile} from 'remotion';
import {GREEN, INK, clamp} from './data';

// the "album art" slot: a premium card with a live, mirrored bar wave (shape after the reference, driven by the real song)
const NB = 37;
const gauss = (v: number, m: number, s: number) => Math.exp(-(((v - m) / s) ** 2));
const env = (x: number) => 0.2 + 0.8 * Math.max(gauss(x, -0.17, 0.15), gauss(x, 0.17, 0.15)) + 0.36 * gauss(Math.abs(x), 0.62, 0.14);
const fmt = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
export const CARD = 560;

export const WaveCard: React.FC<{t: number; levels: number[]; loud: number; total: number}> = ({t, levels, loud, total}) => {
  const W = 470, H = 400, step = W / NB, bw = step * 0.56;
  const bars = new Array(NB).fill(0).map((_, i) => {
    const x = (i / (NB - 1)) * 2 - 1;
    const b = Math.min(23, 1 + Math.round(Math.abs(x) * 15));
    const lvl = 0.5 * levels[b] + 0.2 * levels[Math.min(23, b + 3)] + 0.3 * loud;
    const h = 12 + env(x) * (34 + 300 * lvl);
    return <rect key={i} x={i * step + (step - bw) / 2} y={H / 2 - h / 2} width={bw} height={h} rx={bw / 2} fill={GREEN} />;
  });
  return (
    <div style={{width: CARD, position: 'relative'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: CARD, height: CARD, borderRadius: 40, willChange: 'transform',
        boxShadow: '0 60px 110px -30px rgba(31,122,0,0.38), 0 0 0 1.5px rgba(56,209,0,0.16)'}} />
      <div style={{width: CARD, height: CARD, borderRadius: 40, position: 'relative', overflow: 'hidden',
        background: 'linear-gradient(155deg, rgba(255,255,255,0.94) 0%, rgba(244,253,239,0.9) 60%, rgba(228,248,218,0.9) 100%)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.9)'}}>
        <Img src={staticFile('icon_light.png')} style={{position: 'absolute', left: 38, top: 34, height: 44}} />
        <div style={{position: 'absolute', right: 40, top: 44, fontFamily: 'Manrope', fontWeight: 700, fontSize: 18, letterSpacing: 3, color: 'rgba(10,14,10,0.45)'}}>PSX · 125 BPM</div>
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: (CARD - W) / 2, top: (CARD - H) / 2 + 6}}>{bars}</svg>
        <div style={{position: 'absolute', left: 40, bottom: 34, fontFamily: 'Manrope', fontWeight: 700, fontSize: 20, color: 'rgba(10,14,10,0.5)'}}>Pakistan's First PSX Themed Song</div>
      </div>
      <div style={{marginTop: 40, fontFamily: 'Manrope', fontWeight: 800, fontSize: 46, color: INK, letterSpacing: -0.5}}>Dramay Baaz</div>
      <div style={{marginTop: 4, fontFamily: 'Manrope', fontWeight: 700, fontSize: 26, color: 'rgba(10,14,10,0.5)'}}>FloStocks</div>
      <div style={{marginTop: 30, height: 6, borderRadius: 3, background: 'rgba(10,14,10,0.12)', position: 'relative'}}>
        <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${clamp(t / total) * 100}%`, borderRadius: 3, background: INK}} />
        <div style={{position: 'absolute', top: -5, left: `calc(${clamp(t / total) * 100}% - 8px)`, width: 16, height: 16, borderRadius: 8, background: INK}} />
      </div>
      <div style={{marginTop: 12, display: 'flex', justifyContent: 'space-between', fontFamily: 'Manrope', fontWeight: 700, fontSize: 19, color: 'rgba(10,14,10,0.5)'}}>
        <span>{fmt(t)}</span><span>-{fmt(Math.max(0, total - t))}</span>
      </div>
    </div>
  );
};
