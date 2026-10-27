import React from 'react';
import {AbsoluteFill, Audio, Img, staticFile, useCurrentFrame} from 'remotion';
import {Background} from './Background';
import {Intro, INTRO_OUT} from './Intro';
import {Lyrics} from './Lyrics';
import {Outro, ZOOM, CTA_T} from './Outro';
import {CARD, WaveCard} from './WaveCard';
import {DHOL, DURATION, FPS, OUTRO_T, bands, clamp, easeIn, easeInOut, hitEnv, loudness, prog} from './data';

const TOTAL = DURATION / FPS;

export const LyricVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const loud = loudness(frame);
  const pulse = hitEnv(t, DHOL, 9);
  const playerIn = easeInOut(prog(t, INTRO_OUT + 0.15, 1.4));
  const playerOut = easeIn(prog(t, OUTRO_T - 0.4, 0.6));          // lyrics screen leaves when the final beat drops
  const player = playerIn * (1 - playerOut);
  const blobHome = playerIn * (1 - easeInOut(prog(t, OUTRO_T - 0.4, 1.6)));   // blobs drift back to centre for the logo
  const white = 1 - easeInOut(prog(t, ZOOM + 0.1, CTA_T - ZOOM));               // CTA sits on clean white
  const fadeIn = clamp(t / 0.6), fadeOut = 1 - clamp((t - (TOTAL - 0.35)) / 0.3);
  return (
    <AbsoluteFill style={{background: '#fff'}}>
      <Audio src={staticFile('song.mp3')} />
      <AbsoluteFill style={{opacity: fadeIn * fadeOut}}>
        <Background t={t} player={blobHome} loud={loud} pulse={pulse} fade={white} />
        <Intro t={t} />
        {player > 0 && (
          <>
            <div style={{position: 'absolute', left: 150, top: 150, opacity: player, transform: `translateX(${-90 * (1 - playerIn) - 60 * playerOut}px) scale(${0.96 + 0.04 * player})`, transformOrigin: 'left center'}}>
              <WaveCard t={t} levels={bands(frame)} loud={loud} total={TOTAL} />
            </div>
            <div style={{position: 'absolute', left: 150 + CARD + 150, top: 0, opacity: player, transform: `translateX(${80 * (1 - playerIn) + 60 * playerOut}px)`}}>
              <Lyrics t={t} />
            </div>
            <Img src={staticFile('wordmark_light.png')} style={{position: 'absolute', right: 70, top: 56, width: 190, opacity: 0.9 * player}} />
          </>
        )}
        <Outro t={t} frame={frame} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
