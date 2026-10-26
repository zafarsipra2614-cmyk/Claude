import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame} from 'remotion';
import {Starburst} from '@remotion/starburst';
import {ThreeCanvas} from '@remotion/three';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {pushCut} from '@remotion/transitions/push-cut';
import {Chip} from './Chip';
import {D, FPS, GREEN, INK, WHITE, beatHit, clamp, expoOut, hit, lastIndex} from './lib';

const T0 = 41.33;                       // song time where the sample starts (build-up tail)
const DROP = D.drop;                    // 43.14: first "DRAMAY BAAZ" shout
const CH = D.chants.find((c) => Math.abs(c.hits[0] - DROP) < 0.01)!;
const GREEN_LINE = D.lines.find((l) => l.key === 45.5)!;
const T_GREEN = GREEN_LINE.words[0].t - 0.12;
const T_END = 47.25;
const f = (t: number) => Math.round((t - T0) * FPS);
const XF = 16;                          // shader transition length (frames), centred on the cut

/* ---------------- 1. build-up: letters spring in on half-beats, starburst spins faster and faster */
const Build: React.FC = () => {
  const fr = useCurrentFrame(); const t = T0 + fr / FPS;
  const k = clamp((t - T0) / (DROP - T0));
  const title = 'FLOSTOCKS × REMOTION';
  const halfBeats = D.beats.flatMap((b, i) => [b, (b + (D.beats[i + 1] ?? b + 0.46)) / 2]).filter((h) => h >= T0 - 0.05 && h < DROP);
  const strobe = t > DROP - 0.47 && lastIndex(t, halfBeats.concat(D.beats.filter((b) => b > DROP - 0.47).map((b) => b + 0.115))) % 2 === 1;
  return (
    <AbsoluteFill style={{background: strobe ? WHITE : INK, overflow: 'hidden'}}>
      <AbsoluteFill style={{opacity: 0.18 + 0.5 * k, transform: `scale(${1 + k * 0.6})`}}>
        <Starburst rays={24} colors={[strobe ? '#d9ffd0' : '#103a00', strobe ? WHITE : INK]} rotation={Math.pow(k, 3) * 540 + fr * 0.4} />
      </AbsoluteFill>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', flexDirection: 'row'}}>
        {title.split('').map((ch, i) => {
          const at = halfBeats[Math.floor(i * halfBeats.length / title.length)] ?? T0;
          const s = spring({frame: fr - (at - T0) * FPS, fps: FPS, config: {damping: 9, stiffness: 180}});
          return (
            <span key={i} style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 132, color: ch === '×' ? GREEN : strobe ? INK : WHITE,
              display: 'inline-block', width: ch === ' ' ? 40 : undefined, transform: `translateY(${(1 - s) * 160}px) scale(${s})`,
              opacity: clamp(s * 3)}}>{ch}</span>
          );
        })}
      </AbsoluteFill>
      <div style={{position: 'absolute', left: 64, top: 64, fontFamily: 'Plex', fontWeight: 700, fontSize: 30, color: strobe ? INK : GREEN}}>
        frame {String(fr).padStart(4, '0')} · beat {lastIndex(t, D.beats) - lastIndex(T0, D.beats) + 1}
      </div>
      <div style={{position: 'absolute', left: 0, bottom: 0, height: 10, width: `${k * 100}%`, background: GREEN}} />
      <Chip text="spring() · interpolate() · <Starburst />" p={expoOut((t - T0) / 0.4)} dark={!strobe} />
    </AbsoluteFill>
  );
};

/* ---------------- 2. the drop: shouted words slam on each hit, GPU effects spike on the beat */
const Drop: React.FC<{from: number}> = ({from}) => {
  const fr = useCurrentFrame(); const t = from + fr / FPS;
  const k = Math.max(0, lastIndex(t, CH.hits)); const h = CH.hits[k];
  const e = hit(t, CH.hits, 7);
  const word = ['DRAMAY', 'BAAZ!'][k % 2];
  const s = spring({frame: (t - h) * FPS, fps: FPS, config: {damping: 11, stiffness: 260}});
  const bg = k % 2 ? INK : GREEN, fg = k % 2 ? GREEN : INK;
  return (
    <AbsoluteFill style={{background: bg}}>
      <AbsoluteFill style={{transform: `scale(${1.2 + e * 0.3})`}}>
        <Starburst rays={18} colors={[bg, k % 2 ? '#122a08' : '#2fb400']} rotation={t * 40 + k * 20} />
      </AbsoluteFill>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', filter: `blur(${e * 3}px)`}}>
        {/* RGB split: red + cyan copies pushed apart on each hit */}
        {([['#ff2a2a', 1], ['#00e5ff', -1]] as const).map(([c, d]) => (
          <div key={c} style={{position: 'absolute', fontFamily: 'Manrope', fontWeight: 800, fontSize: 330, letterSpacing: -8, color: c,
            mixBlendMode: k % 2 ? 'screen' : 'multiply', opacity: 0.85 * clamp(s * 4),
            transform: `translate(${d * (4 + e * 34)}px, ${d * e * 6}px) scale(${interpolate(s, [0, 1], [2.6, 1])}) rotate(${(1 - s) * (k % 2 ? 8 : -8)}deg)`}}>{word}</div>
        ))}
        <div style={{position: 'absolute', fontFamily: 'Manrope', fontWeight: 800, fontSize: 330, letterSpacing: -8, color: fg,
          textShadow: k % 2 ? `0 0 ${30 + e * 60}px rgba(56,209,0,${0.5 + e * 0.5})` : 'none',
          transform: `scale(${interpolate(s, [0, 1], [2.6, 1])}) rotate(${(1 - s) * (k % 2 ? 8 : -8)}deg)`, opacity: clamp(s * 4)}}>{word}</div>
        {/* zoom ghosts */}
        {[0, 1, 2].map((r) => (
          <div key={r} style={{position: 'absolute', fontFamily: 'Manrope', fontWeight: 800, fontSize: 330, letterSpacing: -8, color: 'transparent',
            WebkitTextStroke: `4px ${fg}`, opacity: clamp(1 - (t - h) * 2.2 - r * 0.15), transform: `scale(${1 + (t - h) * (1.2 + r * 0.6)})`}}>{word}</div>
        ))}
      </AbsoluteFill>
      <Img src={staticFile(k % 2 ? 'wordmark_dark.png' : 'wordmark_light.png')} style={{position: 'absolute', left: 64, top: 48, width: 230}} />
      <Chip text="spring() per hit · <Starburst /> · beat data from JSON" dark={k % 2 === 1} />
    </AbsoluteFill>
  );
};

/* ---------------- 3. lyric line over 3D candles that bounce on the beat */
const Candles: React.FC<{t: number}> = ({t}) => {
  const n = 13;
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[4, 8, 6]} intensity={2.2} />
      <pointLight position={[0, 2, 4]} intensity={30} color={GREEN} />
      <group rotation={[0.3, -0.35 + (t - T_GREEN) * 0.18, 0]} position={[0, -3.1, -3]}>
        {new Array(n).fill(0).map((_, i) => {
          const p = beatHit(t - i * 0.025, 6);
          const grow = expoOut((t - T_GREEN - i * 0.04) / 0.5);
          const h = (0.4 + (i / n) * 1.7 + p * 0.7) * grow + 0.01;
          const x = (i - (n - 1) / 2) * 0.62;
          const red = i % 4 === 2;
          return (
            <group key={i} position={[x, 0, 0]}>
              <mesh position={[0, h / 2, 0]}><boxGeometry args={[0.38, h, 0.38]} /><meshStandardMaterial color={red ? '#E5484D' : GREEN} roughness={0.35} metalness={0.2} /></mesh>
              <mesh position={[0, h / 2, 0]}><boxGeometry args={[0.05, h + 0.6, 0.05]} /><meshStandardMaterial color={red ? '#E5484D' : GREEN} /></mesh>
            </group>
          );
        })}
      </group>
    </>
  );
};

const Green: React.FC<{from: number}> = ({from}) => {
  const fr = useCurrentFrame(); const t = from + fr / FPS;
  const W = GREEN_LINE.words;
  const word = (i: number) => spring({frame: (t - W[i].t) * FPS, fps: FPS, config: {damping: 10, stiffness: 200}});
  return (
    <AbsoluteFill style={{background: INK}}>
      <ThreeCanvas width={1920} height={1080} camera={{position: [0, 1.2, 7], fov: 45}}><Candles t={t} /></ThreeCanvas>
      <AbsoluteFill style={{alignItems: 'center', paddingTop: 120}}>
        <div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: 300, color: GREEN, letterSpacing: -6, lineHeight: 1,
          transform: `scale(${interpolate(word(0), [0, 1], [3, 1])})`, opacity: clamp(word(0) * 3), textShadow: '0 0 60px rgba(56,209,0,0.45)'}}>GREEN</div>
        <div style={{display: 'flex', gap: 28, marginTop: 24}}>
          {['DEKHA', 'TOH', 'NAACH', 'LIYA'].map((w_, j) => {
            const s = word(j + 1); const big = j >= 2;
            return <span key={j} style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: big ? 120 : 80, color: WHITE, alignSelf: 'flex-end',
              display: 'inline-block', opacity: clamp(s * 3), transform: `translateY(${(1 - s) * 120}px) rotate(${big ? Math.sin(t * 9 + j) * 6 * clamp(s) : 0}deg)`}}>{w_}</span>;
          })}
        </div>
      </AbsoluteFill>
      <Img src={staticFile('wordmark_dark.png')} style={{position: 'absolute', left: 64, top: 48, width: 230}} />
      <Chip text="<ThreeCanvas> · word-synced lyrics from JSON" p={expoOut(fr / 20)} />
    </AbsoluteFill>
  );
};

export const SAMPLE_FRAMES = f(T_END);

export const Sample: React.FC = () => {
  const dropF = f(DROP), greenF = f(T_GREEN);
  return (
    <AbsoluteFill style={{background: INK}}>
      <Audio src={staticFile('song.mp3')} trimBefore={Math.round(T0 * FPS)} />
      <Sequence durationInFrames={dropF}><Build /></Sequence>
      <Sequence from={dropF} durationInFrames={SAMPLE_FRAMES - dropF}>
        <TransitionSeries>
          <TransitionSeries.Sequence durationInFrames={greenF - dropF + XF / 2}><Drop from={DROP} /></TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={pushCut({flashColor: '#FFFFFF'})} timing={linearTiming({durationInFrames: XF})} />
          <TransitionSeries.Sequence durationInFrames={SAMPLE_FRAMES - greenF + XF / 2}><Green from={T_GREEN - XF / 2 / FPS} /></TransitionSeries.Sequence>
        </TransitionSeries>
      </Sequence>
      {/* white flash on the drop */}
      <Sequence from={dropF} durationInFrames={14}><Flash /></Sequence>
    </AbsoluteFill>
  );
};
const Flash: React.FC = () => <AbsoluteFill style={{background: WHITE, opacity: interpolate(useCurrentFrame(), [0, 14], [1, 0])}} />;
