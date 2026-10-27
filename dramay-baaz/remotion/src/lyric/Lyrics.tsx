import React, {useEffect, useState} from 'react';
import {continueRender, delayRender, interpolate} from 'remotion';
import {fontsReady} from '../fonts';
import {BEATS, CTA_ACCENT_FROM, GREEN, INK, ITEMS, Item, clamp, easeInOut, easeOut, hitEnv} from './data';

// Apple/Spotify-style synced lyrics: active line on an anchor, words fill as they are sung,
// the list glides up with a slight stagger, distant lines fade and soften.
const FS = 72, LH = 1.12, GAP = 62, MAXW = 900, ANCHOR = 352, LEAD = 0.3, SCROLL = 0.62;

const measure = (() => {
  let ctx: CanvasRenderingContext2D | null = null;
  return (s: string) => {
    if (!ctx) { ctx = document.createElement('canvas').getContext('2d')!; ctx.font = `800 ${FS}px Manrope`; }
    return ctx.measureText(s).width;
  };
})();

type Laid = Item & {rows: number[][]; h: number; y: number};
/** split word indices into rows that fit MAXW, balanced so no row is left with a lonely word */
const breakRows = (widths: number[], space: number): number[][] => {
  const total = widths.reduce((a, b) => a + b, 0) + space * (widths.length - 1);
  const n = Math.max(1, Math.ceil(total / MAXW));
  if (n === 1) return [widths.map((_, i) => i)];
  const target = total / n;
  const rows: number[][] = [[]]; let w = 0;
  widths.forEach((ww, i) => {
    const cur = rows[rows.length - 1];
    const next = w + (cur.length ? space : 0) + ww;
    const remainingRows = n - rows.length;
    if (cur.length && remainingRows > 0 && (next > MAXW || Math.abs(w - target) < Math.abs(next - target))) { rows.push([i]); w = ww; }
    else { cur.push(i); w = next; }
  });
  return rows;
};
const layout = (): Laid[] => {
  let y = 0;
  const space = measure(' ');
  return ITEMS.map((it) => {
    const rows = breakRows(it.words.map((w) => measure(w.text)), space);
    const h = it.kind === 'dots' ? 40 : rows.length * FS * LH;
    const out = {...it, rows, h, y};
    y += h + GAP;
    return out;
  });
};

const useLayout = () => {
  const [laid, setLaid] = useState<Laid[] | null>(null);
  const [handle] = useState(() => delayRender('Lyric layout'));
  useEffect(() => { fontsReady.then(() => { setLaid(layout()); continueRender(handle); }); }, [handle]);
  return laid;
};

const Dots: React.FC<{it: Laid; t: number}> = ({it, t}) => {
  const k = clamp((t - it.start) / Math.max(0.5, it.end - it.start));
  const breathe = 1 + 0.14 * hitEnv(t, BEATS, 6);
  const out = easeOut(clamp((t - it.end + 0.25) / 0.3));
  return (
    <div style={{display: 'flex', gap: 22, height: 40, alignItems: 'center', transform: `scale(${breathe * (1 - out)})`, transformOrigin: 'left center'}}>
      {[0, 1, 2].map((d) => (
        <div key={d} style={{width: 20, height: 20, borderRadius: 10, background: INK, opacity: 0.22 + 0.78 * clamp(k * 3 - d)}} />
      ))}
    </div>
  );
};

const Words: React.FC<{it: Laid; t: number; active: boolean}> = ({it, t, active}) => {
  // chant lines are green; in the closing line only "because ab NO DRAMAY BAAZI!" is green
  const isAccent = (i: number) => it.kind === 'chant' || (it.kind === 'cta' && i >= CTA_ACCENT_FROM);
  return (
    <div style={{fontFamily: 'Manrope', fontWeight: 800, fontSize: FS, lineHeight: LH, letterSpacing: -0.6, whiteSpace: 'nowrap'}}>
      {it.rows.map((row, r) => <div key={r}>{row.map((i) => { const w = it.words[i];
        const accent = isAccent(i), on = accent ? GREEN : INK, off = accent ? 'rgba(56,209,0,0.32)' : 'rgba(10,14,10,0.26)';
        const p = clamp((t - w.t) / (w.end - w.t));
        const lift = active ? easeOut(clamp((t - w.t) / 0.25)) * (1 - 0.6 * clamp((t - w.end) / 0.4)) : 0;
        const style: React.CSSProperties = {display: 'inline-block', marginRight: '0.26em', transform: `translateY(${-3 * lift}px)`};
        if (!active) return <span key={i} style={{...style, color: on}}>{w.text}</span>;
        const edge = p * 112;
        return (
          <span key={i} style={{...style, color: 'transparent', WebkitBackgroundClip: 'text', backgroundClip: 'text',
            backgroundImage: `linear-gradient(90deg, ${on} ${edge - 12}%, ${off} ${edge}%)`}}>{w.text}</span>
        );
      })}</div>)}
    </div>
  );
};

export const Lyrics: React.FC<{t: number}> = ({t}) => {
  const laid = useLayout();
  if (!laid) return null;
  // active item = last one whose (start - LEAD) has passed
  let a = -1;
  for (let i = 0; i < laid.length; i++) if (laid[i].start - LEAD <= t) a = i;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: MAXW + 40, height: 1080}}>
      {laid.map((it, j) => {
        if (j - Math.max(a, 0) > 4 || Math.max(a, 0) - j > 3) return null;
        // continuous position: each scroll step eases in, lines further below lag slightly
        let y = ANCHOR + it.y, aEff = 0;
        for (let i = 1; i < laid.length; i++) {
          const t0 = laid[i].start - LEAD;
          if (t0 > t) break;
          const lag = 0.035 * clamp(j - i + 1, 0, 6);
          const e = easeInOut(clamp((t - t0 - lag) / SCROLL));
          y -= (laid[i].h + GAP) * e;
          aEff += easeInOut(clamp((t - t0) / SCROLL));
        }
        if (a < 0) aEff = -1 + 0; // before the first line, everything is "upcoming"
        const dist = j - aEff;
        const opacity = dist >= 0 ? interpolate(dist, [0, 1, 2, 2.8], [1, 0.36, 0.14, 0], {extrapolateRight: 'clamp'})
          : interpolate(dist, [-1.7, -1, 0], [0, 0.2, 1], {extrapolateLeft: 'clamp'});
        const blur = Math.min(5, Math.max(0, Math.abs(dist) - 0.3) * 2.2);
        const scale = 1 - 0.055 * clamp(Math.abs(dist));
        const active = j === a && t < it.end + 0.6;
        return (
          <div key={j} style={{position: 'absolute', left: 0, top: 0, opacity, transform: `translate3d(0, ${y.toFixed(2)}px, 0) scale(${scale})`,
            transformOrigin: 'left center', willChange: 'transform, opacity',
            filter: blur > 0.2 ? `blur(${blur.toFixed(2)}px)` : undefined}}>
            {it.kind === 'dots' ? <Dots it={it} t={t} /> : <Words it={it} t={t} active={active} />}
          </div>
        );
      })}
    </div>
  );
};
