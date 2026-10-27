import {Easing} from 'remotion';
import L from '../lyrics.json';
import WAVE from '../wave.json';

export const FPS = 60;
export const DURATION = WAVE.frames;                 // whole song, 159.43 s
export const INK = '#0A0E0A', GREEN = '#38D100', GDEEP = '#1F7A00';
export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const prog = (t: number, at: number, dur: number) => clamp((t - at) / dur);
export const easeInOut = Easing.bezier(0.45, 0, 0.15, 1);
export const easeOut = Easing.bezier(0.22, 1, 0.36, 1);
export const easeIn = Easing.bezier(0.55, 0, 0.9, 0.4);

export const BEATS: number[] = L.beats;
export const DHOL: number[] = L.dhol;
export const INTRO_HITS: number[] = L.introHits;

/** decaying envelope after the most recent hit */
export const hitEnv = (t: number, times: number[], decay = 8) => {
  let v = 0;
  for (const h of times) {
    if (h > t) break;
    if (t - h < 0.8) v = Math.max(v, Math.exp(-(t - h) * decay));
  }
  return v;
};

/** 24 mel-band levels (0..1) for this frame, precomputed from the song */
export const bands = (frame: number): number[] =>
  Array.from(WAVE.bands[Math.min(Math.max(frame, 0), WAVE.frames - 1)], (c) => (c.charCodeAt(0) - 48) / 74);
export const loudness = (frame: number) => (WAVE.loud.charCodeAt(Math.min(Math.max(frame, 0), WAVE.frames - 1)) - 48) / 74;

export type Word = {text: string; t: number; end: number};
export type Item = {kind: 'line' | 'chant' | 'dots'; start: number; end: number; words: Word[]};

const raw = L.items as {kind: Item['kind']; start: number; end: number; words: [string, number][]}[];
// the lyrics screen ends when the final beat drops (~144 s); the outro (logo build + CTA) takes over from there
export const OUTRO_T = 144.2;
while (raw.length && raw[raw.length - 1].start >= OUTRO_T - 0.3) raw.pop();
const last = raw[raw.length - 1];
if (last.kind === 'dots') last.end = Math.min(last.end, OUTRO_T - 0.45);

export const ITEMS: Item[] = raw.map((it) => ({
  kind: it.kind, start: it.start, end: it.end,
  words: it.words.map(([text, t], i) => {
    const next = i + 1 < it.words.length ? it.words[i + 1][1] : it.end;
    return {text, t, end: t + clamp(next - t, 0.14, 0.9)};
  }),
}));
