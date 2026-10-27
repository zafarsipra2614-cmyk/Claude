import React from 'react';
import {AbsoluteFill, Img, spring, staticFile} from 'remotion';
import {noise2D} from '@remotion/noise';
import P from './logo_parts.json';
import {BEATS, FPS, GREEN, INK, OUTRO_T, clamp, easeIn, easeInOut, easeOut, hitEnv, prog} from './data';

/* Final rise (144.2 s → 155.4 s): the official logo, split into its own layers, builds on the beat.
   - break: the three icon shapes drift in
   - shout 1 (146.77): they snap together
   - shout 2 (150.37): the icon steps aside and FLOSTOCKS types in letter by letter
   - shout 3 (154.02): punch; then the logo zooms through to a clean white CTA (155.83). */
export const SNAP = 146.77, REVEAL = 150.37, PUNCH = 154.02, ZOOM = 155.4;
export const CTA_T = BEATS.find((b) => b >= 155.8)!;
const HALF = (BEATS[BEATS.indexOf(CTA_T) + 1] - CTA_T) / 2;

const LW = 1350, LH = 375;                       // official logo canvas
const S0 = 1150 / LW;                              // full logo on screen = 1150 px wide
const SI = S0 * 2.5;                               // icon-only phase scale
const ICON_C = {x: 135, y: 141}, LOGO_C = {x: 674, y: 186};
const LETTERS = ['L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'L8'] as const;
const FROM: Record<'iconA' | 'iconB' | 'iconC', [number, number, number]> = {iconA: [430, -300, 32], iconB: [-520, 90, -26], iconC: [140, 400, 20]};

const Layer: React.FC<{name: string; tf: string; o?: number}> = ({name, tf, o = 1}) => {
  const m = (P as Record<string, {cx: number; cy: number}>)[name];
  return <Img src={staticFile(`logo_parts/${name}.png`)} style={{position: 'absolute', left: 0, top: 0, width: LW, height: LH, opacity: o,
    transform: tf, transformOrigin: `${m.cx}px ${m.cy}px`, willChange: 'transform'}} />;
};

const Ring: React.FC<{x: number; y: number; t: number; at: number; size: number; w?: number}> = ({x, y, t, at, size, w = 4}) => {
  const q = prog(t, at, 1.1);
  if (q <= 0 || q >= 1) return null;
  const r = easeOut(q) * size;
  return <div style={{position: 'absolute', left: x - r, top: y - r, width: 2 * r, height: 2 * r, borderRadius: '50%',
    border: `${w * (1 - q) + 1}px solid ${GREEN}`, opacity: 0.7 * (1 - q)}} />;
};

export const Outro: React.FC<{t: number; frame: number}> = ({t, frame}) => {
  if (t < OUTRO_T - 0.1) return null;
  const beat = hitEnv(t, BEATS, 7);
  // stage framing: icon-only close-up, then pull back to the full logo on the reveal
  const rv = easeInOut(prog(t, REVEAL, 0.8));
  const build = easeInOut(prog(t, REVEAL + 1, PUNCH - REVEAL - 1));
  const zoom = easeIn(prog(t, ZOOM, CTA_T - ZOOM));
  let s = SI + (S0 - SI) * rv;
  s *= 1 + 0.06 * build + (0.025 + 0.035 * build) * beat + 0.07 * hitEnv(t, [PUNCH], 5) + 0.05 * hitEnv(t, [SNAP], 6);
  s *= 1 + 7 * zoom * zoom;
  const cx = ICON_C.x + (LOGO_C.x - ICON_C.x) * rv, cy = ICON_C.y + (LOGO_C.y - ICON_C.y) * rv;
  const sx = 960 - cx * s, sy = 540 - cy * s;
  const iconScreen = {x: sx + ICON_C.x * s, y: sy + ICON_C.y * s};
  const snap = spring({frame: frame - SNAP * FPS, fps: FPS, config: {damping: 11, stiffness: 210}});
  const stageO = (1 - zoom) * clamp((t - OUTRO_T) / 0.5);

  const pieces = (['iconA', 'iconB', 'iconC'] as const).map((k, i) => {
    const arrive = easeOut(prog(t, OUTRO_T + 0.15 + i * 0.35, 1.9));
    const left = (1 - 0.8 * arrive) * (1 - snap);
    const [dx, dy, rot] = FROM[k];
    const nx = noise2D(k, t * 0.6, 0) * 14 * (1 - snap), ny = noise2D(k, 0, t * 0.6) * 14 * (1 - snap);
    return <Layer key={k} name={k} o={clamp(arrive * 1.6)} tf={`translate(${dx * left + nx}px, ${dy * left + ny}px) rotate(${rot * left}deg) scale(${1 + 0.25 * left})`} />;
  });
  const letters = LETTERS.map((k, i) => {
    const at = REVEAL + 0.18 + i * HALF / 2;
    const sp = spring({frame: frame - at * FPS, fps: FPS, config: {damping: 12, stiffness: 190}});
    const wave = hitEnv(t, [PUNCH + i * 0.045], 9);
    return <Layer key={k} name={k} o={clamp(sp * 2)} tf={`translateY(${(1 - sp) * 90 - 26 * wave}px) scale(${0.7 + 0.3 * sp})`} />;
  });
  const tag = easeOut(prog(t, REVEAL + 1.5, 0.8));
  return (
    <AbsoluteFill style={{overflow: 'hidden'}}>
      <AbsoluteFill style={{opacity: stageO, filter: zoom > 0.02 ? `blur(${(zoom * 14).toFixed(1)}px)` : undefined}}>
        <Ring x={iconScreen.x} y={iconScreen.y} t={t} at={SNAP} size={900} w={6} />
        {BEATS.filter((b) => b > SNAP + 0.2 && b < REVEAL - 0.2).map((b) => <Ring key={b} x={iconScreen.x} y={iconScreen.y} t={t} at={b} size={520} w={2} />)}
        <Ring x={960} y={540} t={t} at={PUNCH} size={1300} w={7} />
        <div style={{position: 'absolute', left: 0, top: 0, width: LW, height: LH, transform: `translate(${sx}px, ${sy}px) scale(${s})`, transformOrigin: '0 0'}}>
          {pieces}
          {t >= REVEAL && letters}
          <Layer name="tagline" o={tag} tf={`translateY(${(1 - tag) * 24}px)`} />
        </div>
      </AbsoluteFill>
      <Cta t={t} />
    </AbsoluteFill>
  );
};

/* CTA on clean white */
const Word: React.FC<{t: number; at: number; children: React.ReactNode; pop?: boolean}> = ({t, at, children, pop}) => {
  const p = pop ? spring({frame: (t - at) * FPS, fps: FPS, config: {damping: 10, stiffness: 230}}) : easeOut(prog(t, at, 0.45));
  return (
    <span style={{display: 'inline-block', overflow: pop ? 'visible' : 'hidden', verticalAlign: 'bottom', padding: '0 0.13em 0.1em'}}>
      <span style={{display: 'inline-block', opacity: clamp(p * 2.5),
        transform: pop ? `scale(${1.8 - 0.8 * p})` : `translateY(${(1 - p) * 105}%)`}}>{children}</span>
    </span>
  );
};

const Cta: React.FC<{t: number}> = ({t}) => {
  if (t < CTA_T - 0.05) return null;
  const line1 = ['Open', 'your', 'PSX', 'trading', 'account', 'today,'];
  const big = ['ab', 'NO', 'DRAMAY', 'BAAZI!'];
  const t1 = (i: number) => CTA_T + i * HALF / 2;
  const tBecause = CTA_T + 3 * HALF + HALF / 2;
  const tBig = (i: number) => CTA_T + 4 * HALF + i * HALF;
  const glow = hitEnv(t, [tBig(3)], 3);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', flexDirection: 'column', textAlign: 'center'}}>
      <div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 84, color: INK, letterSpacing: -1.5}}>
        {line1.map((w, i) => <Word key={w} t={t} at={t1(i)}>{w === 'PSX' ? <span style={{color: GREEN}}>{w}</span> : w}</Word>)}
      </div>
      <div style={{fontFamily: 'Manrope', fontWeight: 700, fontSize: 56, color: 'rgba(10,14,10,0.55)', marginTop: 18}}>
        <Word t={t} at={tBecause}>because</Word>
      </div>
      <div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 150, color: GREEN, letterSpacing: -4, lineHeight: 1.05, marginTop: 6,
        textShadow: `0 24px 70px rgba(56,209,0,${(0.18 + 0.3 * glow).toFixed(2)})`}}>
        {big.map((w, i) => <Word key={w} t={t} at={tBig(i)} pop>{w}</Word>)}
      </div>
    </AbsoluteFill>
  );
};
