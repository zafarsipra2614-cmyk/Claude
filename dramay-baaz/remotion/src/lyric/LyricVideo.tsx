import React from 'react';
import {AbsoluteFill, Audio, Img, staticFile, useCurrentFrame} from 'remotion';
import {Background} from './Background';
import {Intro, INTRO_OUT} from './Intro';
import {Lyrics} from './Lyrics';
import {CARD, WaveCard} from './WaveCard';
import {DHOL, DURATION, FPS, bands, clamp, easeInOut, hitEnv, loudness, prog} from './data';

const TOTAL = DURATION / FPS;

export const LyricVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const loud = loudness(frame);
  const pulse = hitEnv(t, DHOL, 9);
  const player = easeInOut(prog(t, INTRO_OUT + 0.15, 1.4));
  const fadeIn = clamp(t / 0.6), fadeOut = 1 - clamp((t - (TOTAL - 0.7)) / 0.6);
  return (
    <AbsoluteFill style={{background: '#fff'}}>
      <Audio src={staticFile('song.mp3')} />
      <AbsoluteFill style={{opacity: fadeIn * fadeOut}}>
        <Background t={t} player={player} loud={loud} pulse={pulse} />
        <Intro t={t} />
        {player > 0 && (
          <>
            <div style={{position: 'absolute', left: 150, top: 150, opacity: player, transform: `translateX(${-90 * (1 - player)}px) scale(${0.96 + 0.04 * player})`, transformOrigin: 'left center'}}>
              <WaveCard t={t} levels={bands(frame)} loud={loud} total={TOTAL} />
            </div>
            <div style={{position: 'absolute', left: 150 + CARD + 150, top: 0, opacity: player, transform: `translateX(${80 * (1 - player)}px)`}}>
              <Lyrics t={t} />
            </div>
            <Img src={staticFile('wordmark_light.png')} style={{position: 'absolute', right: 70, top: 56, width: 190, opacity: 0.9 * player}} />
          </>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
