import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {BEATS, GREEN, INK, INTRO_HITS, clamp, easeIn, easeOut, hitEnv, prog} from './data';

// 0-15 s: official logo, then "FloStocks presents", then "A PSX story starring YOU!", each landing on the shouts of the build-up
const H = INTRO_HITS; // [0.72, 4.6, 5.09, 6.5, 8.87, 10.26, 11.22, 11.68, 12.14, 12.63, 13.1]
const beatAfter = (x: number, n: number) => BEATS.filter((b) => b >= x - 0.05)[n];
export const INTRO_OUT = 13.75;

const Rise: React.FC<{t: number; at: number; children: React.ReactNode; style?: React.CSSProperties}> = ({t, at, children, style}) => {
  const p = easeOut(prog(t, at, 0.7));
  return (
    <span style={{display: 'inline-block', overflow: 'hidden', verticalAlign: 'bottom', padding: '0 0.04em 0.12em', ...style}}>
      <span style={{display: 'inline-block', transform: `translateY(${(1 - p) * 110}%)`, opacity: clamp(p * 2)}}>{children}</span>
    </span>
  );
};

const exitStyle = (t: number, a: number, d = 0.45): React.CSSProperties => {
  const q = easeIn(prog(t, a, d));
  return {opacity: 1 - q, transform: `translateY(${-40 * q}px) scale(${1 - 0.04 * q})`, filter: q > 0.01 ? `blur(${(q * 12).toFixed(1)}px)` : undefined};
};

export const Intro: React.FC<{t: number}> = ({t}) => {
  if (t > INTRO_OUT + 1) return null;
  const logoIn = easeOut(prog(t, H[0], 1.1));
  const s1 = beatAfter(H[4], 1), s2 = beatAfter(H[4], 2);
  const you = easeOut(prog(t, H[6], 0.5));
  const youPulse = hitEnv(t, H.slice(7), 7);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      {/* 1. logo */}
      {t < H[1] + 0.2 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', ...exitStyle(t, H[1] - 0.45)}}>
          <div style={{clipPath: `inset(0 ${(1 - logoIn) * 100}% 0 0)`, transform: `scale(${1.06 - 0.06 * logoIn})`}}>
            <Img src={staticFile('logo_light.png')} style={{width: 860}} />
          </div>
        </AbsoluteFill>
      )}
      {/* 2. FloStocks presents */}
      {t > H[1] - 0.1 && t < H[4] + 0.2 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', ...exitStyle(t, H[4] - 0.5)}}>
          <div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 104, color: INK, letterSpacing: -2,
            transform: `scale(${1 + 0.025 * hitEnv(t, [H[3]], 6)})`}}>
            <Rise t={t} at={H[1]}><span style={{color: GREEN}}>FloStocks</span></Rise> <Rise t={t} at={H[2]}>presents</Rise>
          </div>
        </AbsoluteFill>
      )}
      {/* 3. A PSX story starring YOU! */}
      {t > H[4] - 0.1 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', ...exitStyle(t, INTRO_OUT, 0.7)}}>
          <div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 92, color: INK, letterSpacing: -1.5, marginBottom: -10}}>
            <Rise t={t} at={H[4]}>A</Rise> <Rise t={t} at={s1}><span style={{color: GREEN}}>PSX</span></Rise> <Rise t={t} at={s2}>story</Rise>{' '}
            <Rise t={t} at={H[5]}>starring</Rise>
          </div>
          <div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 330, lineHeight: 1, color: GREEN, letterSpacing: -10,
            opacity: clamp(you * 2), transform: `scale(${(1.5 - 0.5 * you) * (1 + 0.06 * youPulse)})`,
            textShadow: `0 30px 80px rgba(56,209,0,${0.25 + 0.3 * youPulse})`}}>YOU!</div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
