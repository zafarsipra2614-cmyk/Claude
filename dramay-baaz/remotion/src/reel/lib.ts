import data from '../data.json';
export const D = data;
export const FPS = 60;
export const GREEN = '#38D100', INK = '#0A0E0A', WHITE = '#FFFFFF', RED = '#E5484D', GOLD = '#E6A817';
/** decaying envelope after the most recent hit in `times` */
export const hit = (t: number, times: number[], decay = 9) => {
  let v = 0;
  for (const h of times) if (h <= t && t - h < 0.6) v = Math.max(v, Math.exp(-(t - h) * decay));
  return v;
};
export const beatHit = (t: number, decay = 9) => hit(t, D.beats, decay);
export const dholHit = (t: number) => hit(t, D.dhol.map((d) => d[0]), 10);
export const lastIndex = (t: number, times: number[]) => times.filter((h) => h <= t).length - 1;
export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const expoOut = (x: number) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * clamp(x)));
