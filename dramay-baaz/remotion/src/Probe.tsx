import React from 'react';
import {AbsoluteFill, HtmlInCanvas, useCurrentFrame} from 'remotion';
import {chromaticAberration} from '@remotion/effects/chromatic-aberration';
import {glow} from '@remotion/effects/glow';
import {LightLeak} from '@remotion/light-leaks';
import {Starburst} from '@remotion/starburst';
import {ThreeCanvas} from '@remotion/three';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {crossZoom} from '@remotion/transitions/cross-zoom';

const Box = () => {
  const f = useCurrentFrame();
  return (
    <mesh rotation={[f / 20, f / 30, 0]}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#38D100" />
    </mesh>
  );
};
const Card: React.FC<{c: string; t: string}> = ({c, t}) => (
  <AbsoluteFill style={{background: c, alignItems: 'center', justifyContent: 'center', fontFamily: 'Manrope', fontWeight: 800, fontSize: 200, color: '#fff'}}>{t}</AbsoluteFill>
);

export const Probe: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#0A0E0A'}}>
      <div style={{position: 'absolute', left: 0, top: 0, width: 960, height: 540}}>
        <Starburst rays={16} colors={['#38D100', '#0A0E0A']} rotation={f} />
      </div>
      <div style={{position: 'absolute', left: 960, top: 0, width: 960, height: 540, overflow: 'hidden'}}>
        <ThreeCanvas width={960} height={540}>
          <ambientLight intensity={0.6} /><pointLight position={[5, 5, 5]} intensity={80} />
          <Box />
        </ThreeCanvas>
      </div>
      <div style={{position: 'absolute', left: 0, top: 540, width: 960, height: 540}}>
        <HtmlInCanvas width={960} height={540} effects={[chromaticAberration({amount: 20}), glow({radius: 30})]}>
          <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: 'Manrope', fontWeight: 800, fontSize: 140, color: '#38D100'}}>FX</AbsoluteFill>
        </HtmlInCanvas>
        <LightLeak seed={3} />
      </div>
      <div style={{position: 'absolute', left: 960, top: 540, width: 960, height: 540, overflow: 'hidden'}}>
        <TransitionSeries>
          <TransitionSeries.Sequence durationInFrames={40}><Card c="#E5484D" t="A" /></TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={crossZoom({})} timing={linearTiming({durationInFrames: 30})} />
          <TransitionSeries.Sequence durationInFrames={60}><Card c="#38D100" t="B" /></TransitionSeries.Sequence>
        </TransitionSeries>
      </div>
    </AbsoluteFill>
  );
};
