/*
 * Camera moves for 16:9 voiceover films.
 *
 * Adapted from papercut-explainer's camera kit (library/papercut/kit/paper/camera.tsx,
 * https://github.com/0xS4N4TG/papercut-explainer, MIT, (c) 2026 sanat): rewritten for a
 * 1920×1080 frame, without papercut's depth-layer context, and marking themselves
 * `data-moving` while they move so the layout audit judges only settled frames.
 *
 * Wrap a scene's content (inside <Frame>) in one move. Every `at` is a scene-local
 * frame from CUE, so the move lands on a word:
 *   SnapZoom   punch in on a number or a punchline as it is said
 *   PullBack   start tight on a detail, ease out to reveal the whole layout (scale)
 *   Pan        glide between stops on a set wider or taller than the frame (lists,
 *              timelines, "meanwhile, below"): the crab track and the crane in one
 *   RackFocus  defocus the layer behind while a card in front is read
 *   FocusPulse a quick soft-and-snap-back on a static shot, for a reveal
 *   FocusHunt  push in on a key prop while the lens hunts for focus
 *   Handheld   a slow, locked-off-able drift for tense or "on the ground" beats
 * Use one move per scene at most, and not in consecutive scenes; most scenes need none.
 */
import React, { useId } from "react";
import { AbsoluteFill, Easing, interpolate, random, useCurrentFrame } from "remotion";

const W = 1920;
const H = 1080;
const CX = W / 2;
const CY = H / 2;
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const rad = (d: number) => (d * Math.PI) / 180;

/** Marks the subtree as moving (skipped by the audit) while `moving` is true. */
const Mover: React.FC<{ moving: boolean; style?: React.CSSProperties; children: React.ReactNode }> = ({ moving, style, children }) => (
  <AbsoluteFill data-moving={moving ? "" : undefined} style={style}>
    {children}
  </AbsoluteFill>
);

// ---------- zoom smear: motion blur on fast zooms ----------
// The sharp frame sits underneath; on top, sub-frame samples of the same transform are averaged,
// blurred by the zoom speed, and masked so the middle of the zoom stays sharp.
const Smear: React.FC<{ n: number; shutter: number; blur: number; center: [number, number]; at: (t: number) => string; origin: string; children: React.ReactNode }> = ({
  n,
  shutter,
  blur,
  center,
  at,
  origin,
  children,
}) => {
  const f = useCurrentFrame();
  const cur = { transform: at(f), transformOrigin: origin };
  if (n <= 1) return <AbsoluteFill style={cur}>{children}</AbsoluteFill>;
  const mask = `radial-gradient(circle at ${center[0]}px ${center[1]}px, transparent 0px, transparent 140px, #000 620px)`;
  return (
    <>
      <AbsoluteFill style={cur}>{children}</AbsoluteFill>
      <AbsoluteFill aria-hidden style={{ filter: `blur(${blur.toFixed(1)}px)`, WebkitMaskImage: mask, maskImage: mask, pointerEvents: "none" }}>
        {Array.from({ length: n }).map((_, i) => {
          const t = f - (shutter * (n - 1 - i)) / (n - 1);
          return (
            <AbsoluteFill key={i} style={{ transform: at(t), transformOrigin: origin, opacity: i === 0 ? 1 : 1 / (i + 1) }}>
              {children}
            </AbsoluteFill>
          );
        })}
      </AbsoluteFill>
    </>
  );
};
const samplesFor = (speed: number, on: boolean) => (!on ? 1 : speed > 0.05 ? 12 : speed > 0.02 ? 7 : speed > 0.008 ? 4 : 1);
const blurFor = (speed: number) => Math.min(12, speed * 85);

// ---------- snap zoom ----------
const noise = (seed: string, t: number) => {
  const k = Math.floor(t);
  const a = random(`${seed}${k}`) * 2 - 1;
  const b = random(`${seed}${k + 1}`) * 2 - 1;
  return a + (b - a) * (t - k);
};
const snapAt = (t: number, to: number, settle: number) => {
  if (t < 0) return 1;
  const up = interpolate(t, [0, 4], [1, to], { ...clamp, easing: Easing.out(Easing.cubic) });
  const relax = interpolate(t, [4, 18], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  return t <= 4 ? up : to + (settle - to) * relax;
};

/** Punch in on (x, y) as a number or punchline lands at `at`: a 4-frame zoom with blur, a short shake, then it settles at `settle`. */
export const SnapZoom: React.FC<{ at: number; x?: number; y?: number; to?: number; settle?: number; shake?: number; roll?: number; blur?: boolean; children: React.ReactNode }> = ({
  at,
  x = CX,
  y = CY,
  to = 1.22,
  settle = 1.14,
  shake = 14,
  roll = 1.1,
  blur = true,
  children,
}) => {
  const f = useCurrentFrame();
  const tf = (t: number) => {
    const u = t - at;
    const s = snapAt(u, to, settle);
    const k = Math.max(0, u - 2.5);
    const amp = u < 2.5 ? 0 : shake * Math.exp(-k / 1.3);
    const dx = amp * noise("sz-x", u);
    const dy = amp * 0.8 * noise("sz-y", u);
    const rr = u < 2.5 ? 0 : roll * Math.exp(-k / 2.6) * Math.sin(k * 1.9);
    const pull = (s - 1) * 0.3; // the focal point drifts a little toward the middle of the frame
    return `translate(${dx + (CX - x) * pull}px, ${dy + (CY - y) * pull}px) rotate(${rr}deg) scale(${s})`;
  };
  const speed = Math.abs(snapAt(f - at, to, settle) - snapAt(f - at - 1, to, settle));
  return (
    <Mover moving={f >= at - 1 && f < at + 20}>
      <Smear n={samplesFor(speed, blur)} shutter={0.9} blur={blurFor(speed)} center={[x, y]} at={tf} origin={`${x}px ${y}px`}>
        {children}
      </Smear>
    </Mover>
  );
};

// ---------- pull-back reveal ----------
const pullAt = (t: number, dur: number, from: number) => interpolate(t, [0, Math.max(1, dur)], [from, 1], { ...clamp, easing: Easing.bezier(0.16, 0.84, 0.3, 1) });

/** Start `from`× tight on the detail at (x, y) and ease out to the whole layout over `dur` frames. Edges stay covered. */
export const PullBack: React.FC<{ dur: number; x: number; y: number; from?: number; at?: number; blur?: boolean; children: React.ReactNode }> = ({ dur, x, y, from = 2.4, at = 0, blur = true, children }) => {
  const f = useCurrentFrame();
  const t0x = Math.min(0, Math.max(W * (1 - from), CX - from * x));
  const t0y = Math.min(0, Math.max(H * (1 - from), CY - from * y));
  const tf = (t: number) => {
    const s = pullAt(t - at, dur, from);
    const u = (s - 1) / Math.max(0.001, from - 1);
    return `translate(${t0x * u}px, ${t0y * u}px) scale(${s})`;
  };
  const speed = Math.abs(pullAt(f - at, dur, from) - pullAt(f - at - 1, dur, from));
  return (
    <Mover moving={f < at + dur}>
      <Smear n={samplesFor(speed / 2, blur)} shutter={0.8} blur={blurFor(speed / 2)} center={[-t0x / (from - 1), -t0y / (from - 1)]} at={tf} origin="0px 0px">
        {children}
      </Smear>
    </Mover>
  );
};

// ---------- pan: crab track (x) and crane (y) ----------
const TrackBlur: React.FC<{ axis: "x" | "y"; amount: number; children: React.ReactNode }> = ({ axis, amount, children }) => {
  const id = useId().replace(/:/g, "");
  const on = amount > 0.4;
  return (
    <AbsoluteFill style={{ filter: on ? `url(#tb${id})` : undefined }}>
      {on ? (
        <svg width={0} height={0} style={{ position: "absolute" }}>
          <filter id={`tb${id}`} x="-5%" y="-5%" width="110%" height="110%">
            <feGaussianBlur stdDeviation={axis === "x" ? `${amount.toFixed(1)} 0` : `0 ${amount.toFixed(1)}`} />
          </filter>
        </svg>
      ) : null}
      {children}
    </AbsoluteFill>
  );
};

/** Total frames a Pan takes: a hold at every stop and a move between stops. */
export const panFrames = (stops: number[], hold = 30, move = 16) => stops.length * hold + (stops.length - 1) * move;

/**
 * Glide along a set wider (axis "x") or taller (axis "y") than the frame, easing to each
 * stop and holding `hold` frames. A stop is the world coordinate that should sit at the
 * frame's centre. Lay the set out in world pixels (e.g. x from 0 to 4000). Elements fully
 * off-screen at a hold are ignored by the audit; anything partly on screen must fit.
 */
export const Pan: React.FC<{ stops: number[]; axis?: "x" | "y"; hold?: number; move?: number; at?: number; blur?: boolean; children: React.ReactNode }> = ({
  stops,
  axis = "x",
  hold = 30,
  move = 16,
  at = 0,
  blur = true,
  children,
}) => {
  const f = useCurrentFrame();
  const centre = axis === "x" ? CX : CY;
  const offAt = (ff: number) => {
    const k = Math.max(0, ff - at);
    const period = hold + move;
    const i = Math.min(stops.length - 1, Math.floor(k / period));
    if (i >= stops.length - 1) return stops[stops.length - 1] - centre;
    const u = interpolate(k - i * period, [hold, hold + move], [0, 1], { ...clamp, easing: Easing.bezier(0.6, 0, 0.2, 1) });
    return stops[i] + (stops[i + 1] - stops[i]) * u - centre;
  };
  const off = offAt(f);
  const speed = Math.abs(off - offAt(f - 1));
  const k = Math.max(0, f - at);
  const phase = k % (hold + move);
  const moving = f >= at && k < panFrames(stops, hold, move) - hold && phase >= hold - 1;
  return (
    <Mover moving={moving} style={{ transform: axis === "x" ? `translateX(${-off}px)` : `translateY(${-off}px)` }}>
      <TrackBlur axis={axis} amount={blur ? Math.min(18, speed * 0.13) : 0}>
        {children}
      </TrackBlur>
    </Mover>
  );
};

// ---------- focus ----------
/** Defocus everything inside from `from` to `to` px of blur, from `at` over `dur` frames (optionally back again at `returnAt`). Wrap the layer BEHIND the card being read. */
export const RackFocus: React.FC<{ from?: number; to?: number; at?: number; dur?: number; returnAt?: number; children: React.ReactNode }> = ({ from = 0, to = 10, at = 0, dur = 14, returnAt, children }) => {
  const f = useCurrentFrame();
  let u = interpolate(f, [at, at + Math.max(1, dur)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  if (returnAt !== undefined) u *= 1 - interpolate(f, [returnAt, returnAt + Math.max(1, dur)], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const b = from + (to - from) * u;
  const s = 1 + b * 0.0006;
  const moving = (f >= at && f < at + dur) || (returnAt !== undefined && f >= returnAt && f < returnAt + dur);
  return (
    <Mover moving={moving} style={{ filter: b > 0.05 ? `blur(${b.toFixed(2)}px)` : undefined, transform: s > 1.0001 ? `scale(${s})` : undefined }}>
      {children}
    </Mover>
  );
};

const huntBlur = (k: number) => 0.7 * interpolate(k, [0, 4 / 18, 8 / 18, 13 / 18, 1], [0, 8, 18, 5, 0], clamp);

/** On a static shot, go soft and snap back over `dur` frames from `at`: emphasis for a reveal without moving the camera. */
export const FocusPulse: React.FC<{ at: number; dur?: number; children: React.ReactNode }> = ({ at, dur = 18, children }) => {
  const f = useCurrentFrame();
  const b = huntBlur(Math.min(1, Math.max(0, (f - at) / Math.max(2, dur))));
  return (
    <Mover moving={f >= at && f < at + dur} style={{ filter: b > 0.05 ? `blur(${b.toFixed(2)}px)` : undefined, transform: b > 0.05 ? `scale(${1 + b * 0.0045})` : undefined }}>
      {children}
    </Mover>
  );
};

/** Push in on a key prop at (x, y) from 1× to 1+`amount` over `dur` frames while the lens hunts for focus part-way through. */
export const FocusHunt: React.FC<{ at: number; dur?: number; amount?: number; x?: number; y?: number; children: React.ReactNode }> = ({ at, dur = 30, amount = 0.35, x = CX, y = CY, children }) => {
  const f = useCurrentFrame();
  const z = interpolate(f, [at, at + Math.max(1, dur)], [0, 1], { ...clamp, easing: Easing.bezier(0.8, 0, 0.2, 1) });
  const start = at + Math.round((10 * dur) / 30);
  const len = Math.max(2, Math.round((18 * dur) / 30));
  return (
    <Mover moving={f >= at && f < at + dur} style={{ transformOrigin: `${x}px ${y}px`, transform: `scale(${1 + amount * z})` }}>
      <FocusPulse at={start} dur={len}>
        {children}
      </FocusPulse>
    </Mover>
  );
};

/** A slow deterministic drift (x, y, roll) plus a faint breath; `settleAt` eases to a locked-off shot. Keep key content out of the outer ~20 px. */
export const Handheld: React.FC<{ amount?: number; roll?: number; rate?: number; settleAt?: number; children: React.ReactNode }> = ({ amount = 5, roll = 0.3, rate = 60, settleAt, children }) => {
  const f = useCurrentFrame();
  const k = settleAt === undefined ? 1 : 1 - interpolate(f, [settleAt, settleAt + 10], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const w = (ph: number) =>
    (0.6 * Math.sin((2 * Math.PI * f) / rate + ph) + 0.3 * Math.sin((2 * Math.PI * f) / (rate * 0.47) + ph * 1.7 + 1.3) + 0.15 * Math.sin((2 * Math.PI * f) / (rate * 0.23) + ph * 2.3 + 2.1)) / 1.05;
  const dx = amount * w(0.4) * k;
  const dy = amount * 0.8 * w(2.5) * k;
  const dr = roll * w(4.4) * k;
  const r = rad(roll);
  const need = Math.max(1.01, Math.cos(r) + (H / W) * Math.sin(r) + (2 * amount) / W + 0.004);
  const sc = 1 + (need - 1) * k;
  // handheld never settles on its own, so it is not marked moving: content must fit with the drift applied
  return <AbsoluteFill style={{ transformOrigin: "50% 50%", transform: `translate(${dx.toFixed(2)}px, ${dy.toFixed(2)}px) rotate(${dr.toFixed(3)}deg) scale(${sc.toFixed(4)})` }}>{children}</AbsoluteFill>;
};
