import React from "react";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C, DROP, Grain, Paper, getEntrance, riseFrom } from "../shared/system";
import { ARIAL, tornClip } from "../shared/pieces";
import { PLAYFAIR, PT_SERIF, TYPEWRITER } from "../shared/fonts";
import { FitCheck, Label, Rise, clamp, ramp } from "./kit";

export { ARIAL, PLAYFAIR, PT_SERIF, TYPEWRITER, C, DROP };

const BG = "background.jpg";

/* ------------------------------------------------------------------ */
/* Frame: paper, a slow camera push on the content, grain, the audit.  */
/* ------------------------------------------------------------------ */
export const Frame: React.FC<{ children: React.ReactNode; push?: number }> = ({ children, push = 0.022 }) => {
  const frame = useCurrentFrame();
  const s = 1 + push * Math.min(1, frame / 420);
  return (
    <AbsoluteFill data-frame style={{ backgroundColor: C.paper, overflow: "hidden" }}>
      <Paper asset={BG} />
      <AbsoluteFill style={{ transform: `scale(${s})`, transformOrigin: "50% 46%" }}>{children}</AbsoluteFill>
      <Grain />
      <FitCheck />
    </AbsoluteFill>
  );
};

/* ------------------------------------------------------------------ */
/* Price tag: drops in on its string and settles with a damped swing.  */
/* ------------------------------------------------------------------ */
export type Tone = "paper" | "red" | "ink" | "amber";
const TONES: Record<Tone, { bg: string; fg: string; hl: string; stroke: string }> = {
  paper: { bg: C.card, fg: C.ink, hl: C.red, stroke: C.red },
  red: { bg: C.red, fg: "#FFF6EE", hl: C.amber, stroke: C.ink },
  ink: { bg: C.inkDeep, fg: C.card, hl: C.amber, stroke: C.red },
  amber: { bg: C.amber, fg: C.ink, hl: C.red, stroke: C.ink },
};
const TAG_CLIP = "polygon(17% 0, 100% 0, 100% 100%, 17% 100%, 0 50%)";

export const Tag: React.FC<{
  x: number;
  y: number;
  w: number;
  price: string;
  start: number;
  tone?: Tone;
  label?: string;
  /** indices into `price` drawn in the highlight colour */
  hl?: number[];
  /** frame at which the highlighted characters turn on (default: always) */
  hlAt?: number;
  /** frame from which everything but the highlight fades back */
  dimAt?: number;
  strikeAt?: number;
  rot?: number;
  string?: boolean;
  exit?: number;
  z?: number;
  name?: string;
  layer?: "over";
  /** letter-spacing as a fraction of the font size (tight by default; use 0 for very large tags) */
  tracking?: number;
}> = ({ x, y, w, price, start, tone = "paper", label, hl = [], hlAt, dimAt, strikeAt, rot = 0, string = true, exit, z = 14, name, layer, tracking = -0.02 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame - start;
  const h = Math.round(w * 0.46);
  const drop = spring({ frame: t, fps, config: { damping: 14, mass: 0.8, stiffness: 120 }, durationInFrames: 34 });
  // a short drop: enough to read as hanging, never long enough to pass over other content.
  // tags with no string (sitting on something) pop in place instead.
  const swing = t > 0 && string ? 7 * Math.exp(-t / 13) * Math.sin(t / 3.6) : 0;
  const enterY = string ? interpolate(drop, [0, 1], [-90, 0]) : 0;
  const enterS = string ? 1 : interpolate(drop, [0, 1], [0.7, 1]);
  const o = interpolate(frame, [start, start + 8], [0, 1], clamp);
  const out = exit === undefined ? 0 : ramp(frame, exit, exit + 12, Easing.in(Easing.cubic));
  const tone_ = TONES[tone];
  const hlOn = hlAt === undefined ? 1 : ramp(frame, hlAt, hlAt + 8);
  const dim = dimAt === undefined ? 0 : ramp(frame, dimAt, dimAt + 14);
  const textW = w * 0.72;
  const fs = Math.min(h * (label ? 0.42 : 0.52), textW / (price.length * 0.66));
  const strikeW = strikeAt === undefined ? 0 : ramp(frame, strikeAt, strikeAt + 10, Easing.out(Easing.quad));
  const moving = t < 40 || out > 0;
  return (
    <div
      data-moving={moving ? "" : undefined}
      data-layer={layer}
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        height: h,
        opacity: o * (1 - out),
        transform: `translateY(${enterY - out * 60}px) rotate(${rot + swing}deg) scale(${enterS})`,
        transformOrigin: `${w * 0.1}px ${h / 2}px`,
        zIndex: z,
      }}
    >
      {string ? (
        <svg width={40} height={150} style={{ position: "absolute", left: w * 0.1 - 20, top: h / 2 - 150, overflow: "visible" }}>
          <path d="M 20 150 C 14 100, 28 60, 20 0" stroke="rgba(26,26,26,0.55)" strokeWidth={3} fill="none" />
        </svg>
      ) : null}
      <div style={{ position: "absolute", inset: 0, background: tone_.stroke, clipPath: TAG_CLIP, transform: "translate(12px, 9px)", opacity: 0.95 }} />
      <div
        data-fit={name ?? `tag ${price}`}
        style={{
          position: "absolute",
          inset: 0,
          background: tone_.bg,
          clipPath: TAG_CLIP,
          filter: DROP,
          paddingLeft: w * 0.22,
          paddingRight: w * 0.06,
          boxSizing: "border-box",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div style={{ position: "absolute", left: w * 0.1 - h * 0.08, top: h / 2 - h * 0.08, width: h * 0.16, height: h * 0.16, borderRadius: "50%", background: C.paper, boxShadow: "inset 0 2px 3px rgba(0,0,0,0.35)" }} />
        {label ? (
          <div style={{ fontFamily: ARIAL, fontSize: h * 0.14, letterSpacing: h * 0.03, color: tone_.fg, opacity: 0.7, whiteSpace: "nowrap", lineHeight: 1, marginBottom: h * 0.05 }}>{label}</div>
        ) : null}
        <div style={{ position: "relative", fontFamily: ARIAL, fontSize: fs, lineHeight: 1, letterSpacing: fs * tracking, whiteSpace: "nowrap", color: tone_.fg }}>
          {price.split("").map((ch, i) => {
            const isHl = hl.includes(i);
            return (
              <span key={i} style={{ color: isHl && hlOn > 0.5 ? tone_.hl : tone_.fg, opacity: isHl ? 1 : 1 - dim * 0.72 }}>
                {ch}
              </span>
            );
          })}
          {strikeAt !== undefined ? (
            <div aria-hidden data-mark style={{ position: "absolute", left: -10, right: -10, top: "48%", height: Math.max(6, fs * 0.09), background: C.red, borderRadius: 6, transformOrigin: "left center", transform: `scaleX(${strikeW}) rotate(-4deg)` }} />
          ) : null}
        </div>
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Paper card: a torn sheet that rises in, with the red offset stroke. */
/* ------------------------------------------------------------------ */
export const Card: React.FC<{
  start: number;
  left: number;
  top: number;
  width: number;
  height: number;
  name: string;
  rotate?: number;
  pad?: string;
  stroke?: number;
  tone?: "card" | "ink" | "red";
  exit?: number;
  layer?: "over";
  z?: number;
  dur?: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}> = ({ start, left, top, width, height, name, rotate = 0, pad = "40px 48px", stroke = -22, tone = "card", exit, layer, z = 12, dur = 30, style, children }) => (
  <Rise start={start} dur={dur} left={left} top={top} width={width} height={height} rotate={rotate} exit={exit} layer={layer} z={z} style={{ filter: "none" }}>
    {stroke ? <div aria-hidden style={{ position: "absolute", inset: 0, background: tone === "red" ? C.ink : C.red, clipPath: tornClip(width % 37, 18, 1.4), transform: `translate(${stroke}px, 10px)` }} /> : null}
    <div
      data-fit={name}
      style={{
        position: "absolute",
        inset: 0,
        background: tone === "ink" ? C.inkDeep : tone === "red" ? C.red : C.card,
        color: tone === "card" ? C.ink : C.card,
        clipPath: tornClip((width + height) % 41, 18, 1.4),
        padding: pad,
        boxSizing: "border-box",
        filter: DROP,
        ...style,
      }}
    >
      {children}
    </div>
  </Rise>
);

/* ------------------------------------------------------------------ */
/* Cut-paper icons. Flat shapes in the locked palette; the wrapper     */
/* adds the red offset silhouette and the shared drop shadow.          */
/* ------------------------------------------------------------------ */
const cutFilter = (id: string, dx: number) => (
  <defs>
    <filter id={id} x="-30%" y="-30%" width="160%" height="160%">
      <feOffset in="SourceAlpha" dx={dx} dy={4} result="o" />
      <feFlood floodColor={C.red} />
      <feComposite in2="o" operator="in" result="s" />
      <feMerge>
        <feMergeNode in="s" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
  </defs>
);

export const ICONS: Record<string, { vb: string; el: React.ReactNode }> = {
  car: {
    vb: "0 0 240 120",
    el: (
      <g>
        <path d="M 14 78 L 22 56 Q 26 48 36 46 L 70 42 L 96 18 Q 102 12 112 12 L 168 12 Q 178 12 184 20 L 204 44 L 222 50 Q 230 54 230 64 L 230 82 Q 230 88 224 88 L 18 88 Q 12 88 14 78 Z" fill={C.ink} />
        <path d="M 102 22 L 136 22 L 136 44 L 80 44 Z" fill={C.card} />
        <path d="M 144 22 L 172 22 Q 178 22 182 28 L 196 44 L 144 44 Z" fill={C.card} />
        <rect x={210} y={58} width={14} height={8} rx={3} fill={C.amber} />
        {[62, 182].map((cx) => (
          <g key={cx}>
            <circle cx={cx} cy={90} r={24} fill={C.inkDeep} />
            <circle cx={cx} cy={90} r={11} fill={C.card} />
          </g>
        ))}
      </g>
    ),
  },
  dress: {
    vb: "0 0 160 220",
    el: (
      <g>
        <path d="M 58 10 L 70 34 L 90 34 L 102 10 L 112 14 L 108 64 L 52 64 L 48 14 Z" fill={C.red} />
        <rect x={50} y={64} width={60} height={14} fill={C.ink} />
        <path d="M 52 78 L 108 78 L 148 206 Q 80 220 12 206 Z" fill={C.red} />
        <path d="M 80 78 L 80 210" stroke="rgba(0,0,0,0.12)" strokeWidth={4} />
        <path d="M 66 2 Q 80 -6 94 2" stroke={C.ink} strokeWidth={5} fill="none" />
      </g>
    ),
  },
  bag: {
    vb: "0 0 200 190",
    el: (
      <g>
        <path d="M 62 70 Q 62 14 100 14 Q 138 14 138 70" stroke={C.ink} strokeWidth={12} fill="none" />
        <path d="M 30 64 L 170 64 L 186 176 Q 186 184 178 184 L 22 184 Q 14 184 14 176 Z" fill={C.inkDeep} />
        <rect x={30} y={64} width={140} height={22} fill="#2C251E" />
        <rect x={88} y={80} width={24} height={20} rx={3} fill={C.amber} />
      </g>
    ),
  },
  register: {
    vb: "0 0 220 200",
    el: (
      <g>
        <rect x={70} y={6} width={80} height={40} rx={4} fill={C.ink} />
        <rect x={80} y={14} width={60} height={22} fill={C.amber} />
        <path d="M 30 50 L 190 50 L 206 140 L 14 140 Z" fill={C.ink} />
        {[0, 1, 2].map((r) =>
          [0, 1, 2, 3, 4].map((c) => <rect key={`${r}${c}`} x={46 + c * 28} y={64 + r * 22} width={18} height={14} rx={3} fill={r === 2 && c === 4 ? C.red : C.card} />),
        )}
        <rect x={10} y={142} width={200} height={48} rx={4} fill={C.inkDeep} />
        <rect x={92} y={160} width={36} height={8} rx={4} fill={C.amber} />
      </g>
    ),
  },
  drawer: {
    vb: "0 0 200 60",
    el: (
      <g>
        <rect x={0} y={0} width={200} height={56} rx={4} fill="#2C251E" />
        {[0, 1, 2, 3].map((i) => <rect key={i} x={14 + i * 46} y={10} width={36} height={30} rx={3} fill={C.card} />)}
        <circle cx={60} cy={26} r={9} fill={C.amber} />
        <circle cx={150} cy={26} r={9} fill={C.amber} />
      </g>
    ),
  },
  bottle: {
    vb: "0 0 100 260",
    el: (
      <g>
        <path d="M 40 6 L 60 6 L 60 70 Q 88 96 88 130 L 88 246 Q 88 254 80 254 L 20 254 Q 12 254 12 246 L 12 130 Q 12 96 40 70 Z" fill={C.ink} />
        <path d="M 38 4 L 62 4 L 64 60 L 36 60 Z" fill={C.amber} />
        <rect x={20} y={150} width={60} height={56} fill={C.card} />
        <rect x={28} y={170} width={44} height={6} fill={C.red} />
      </g>
    ),
  },
  calculator: {
    vb: "0 0 150 210",
    el: (
      <g>
        <rect x={4} y={4} width={142} height={202} rx={14} fill={C.ink} />
        <rect x={18} y={18} width={114} height={44} rx={4} fill={C.amber} />
        {[0, 1, 2, 3].map((r) =>
          [0, 1, 2].map((c) => <rect key={`${r}${c}`} x={20 + c * 38} y={78 + r * 30} width={30} height={22} rx={4} fill={c === 2 && r === 3 ? C.red : C.card} />),
        )}
      </g>
    ),
  },
  bill: {
    vb: "0 0 240 110",
    el: (
      <g>
        <rect x={2} y={2} width={236} height={106} rx={6} fill="#CFD6BF" />
        <rect x={12} y={12} width={216} height={86} rx={4} fill="none" stroke={C.ink} strokeWidth={3} opacity={0.6} />
        <circle cx={120} cy={55} r={30} fill="none" stroke={C.ink} strokeWidth={4} opacity={0.6} />
        <text x={30} y={46} fontFamily={ARIAL} fontSize={26} fill={C.ink}>1</text>
        <text x={196} y={94} fontFamily={ARIAL} fontSize={26} fill={C.ink}>1</text>
      </g>
    ),
  },
  pocket: {
    vb: "0 0 200 200",
    el: (
      <g>
        <path d="M 10 30 Q 100 70 190 30 L 190 150 Q 100 200 10 150 Z" fill="#3B4252" />
        <path d="M 22 44 Q 100 80 178 44" stroke={C.amber} strokeWidth={4} strokeDasharray="10 8" fill="none" />
        <path d="M 22 140 Q 100 182 178 140" stroke={C.amber} strokeWidth={4} strokeDasharray="10 8" fill="none" />
      </g>
    ),
  },
  coin: {
    vb: "0 0 120 120",
    el: (
      <g>
        <circle cx={60} cy={60} r={56} fill="#C8742E" />
        <circle cx={60} cy={60} r={44} fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth={4} />
        <text x={60} y={78} textAnchor="middle" fontFamily={ARIAL} fontSize={50} fill="#FFF3E6">1¢</text>
      </g>
    ),
  },
  heart: {
    vb: "0 0 200 180",
    el: <path d="M 100 172 C 20 116, 4 80, 4 52 C 4 22, 28 4, 56 4 C 78 4, 92 16, 100 32 C 108 16, 122 4, 144 4 C 172 4, 196 22, 196 52 C 196 80, 180 116, 100 172 Z" fill={C.red} />,
  },
  gear: {
    vb: "0 0 200 200",
    el: (
      <g>
        {Array.from({ length: 8 }).map((_, i) => (
          <rect key={i} x={86} y={2} width={28} height={40} rx={4} fill={C.ink} transform={`rotate(${i * 45} 100 100)`} />
        ))}
        <circle cx={100} cy={100} r={70} fill={C.ink} />
        <circle cx={100} cy={100} r={28} fill={C.card} />
      </g>
    ),
  },
  mask: {
    vb: "0 0 240 120",
    el: (
      <g>
        <path d="M 10 36 Q 60 4 120 30 Q 180 4 230 36 Q 226 96 170 104 Q 136 106 120 80 Q 104 106 70 104 Q 14 96 10 36 Z" fill={C.ink} />
        <ellipse cx={72} cy={58} rx={26} ry={16} fill={C.paper} />
        <ellipse cx={168} cy={58} rx={26} ry={16} fill={C.paper} />
        <path d="M 10 36 Q 60 4 120 30 Q 180 4 230 36" stroke={C.amber} strokeWidth={6} fill="none" />
      </g>
    ),
  },
  store: {
    vb: "0 0 200 190",
    el: (
      <g>
        <rect x={14} y={60} width={172} height={126} fill={C.card} />
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <path key={i} d={`M ${6 + i * 31.3} 30 L ${37.3 + i * 31.3} 30 L ${37.3 + i * 31.3} 66 Q ${21.6 + i * 31.3} 80 ${6 + i * 31.3} 66 Z`} fill={i % 2 ? C.card : C.red} />
        ))}
        <rect x={4} y={14} width={192} height={18} fill={C.ink} />
        <rect x={30} y={96} width={66} height={56} fill="#BFD0D6" />
        <rect x={118} y={96} width={48} height={90} fill={C.ink} />
      </g>
    ),
  },
  folder: {
    vb: "0 0 240 170",
    el: (
      <g>
        <path d="M 6 26 L 86 26 L 100 8 L 160 8 L 170 26 L 234 26 L 234 164 L 6 164 Z" fill="#C79A55" />
        <rect x={6} y={44} width={228} height={120} fill="#E0B86F" />
      </g>
    ),
  },
};

/** A cut-paper icon that rises in. */
export const Icon: React.FC<{
  kind: keyof typeof ICONS;
  start: number;
  left: number;
  top: number;
  width: number;
  height?: number;
  dx?: number;
  rotate?: number;
  exit?: number;
  spin?: number;
  name?: string;
  z?: number;
}> = ({ kind, start, left, top, width, height, dx = -12, rotate = 0, exit, spin = 0, name, z = 12 }) => {
  const frame = useCurrentFrame();
  const id = `cut-${React.useId().replace(/:/g, "")}`;
  const ic = ICONS[kind];
  const [, , vw, vh] = ic.vb.split(" ").map(Number);
  const h = height ?? Math.round((width * vh) / vw);
  return (
    <Rise start={start} dur={30} dist={220} left={left} top={top} width={width} height={h} rotate={rotate} exit={exit} z={z} style={{ filter: DROP }}>
      <svg data-fit={name ?? `icon ${kind}`} viewBox={ic.vb} width={width} height={h} style={{ overflow: "visible", transform: spin ? `rotate(${(frame - start) * spin}deg)` : undefined }}>
        {cutFilter(id, dx * (vw / width))}
        <g filter={`url(#${id})`}>{ic.el}</g>
      </svg>
    </Rise>
  );
};

/* ------------------------------------------------------------------ */
/* Chapter card.                                                       */
/* ------------------------------------------------------------------ */
export const ChapterCard: React.FC<{ n: string; title: React.ReactNode; numAt: number; titleAt: number; top?: number; small?: string; smallAt?: number }> = ({
  n,
  title,
  numAt,
  titleAt,
  top = 260,
  small,
  smallAt = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const num = spring({ frame: frame - numAt, fps, config: { damping: 12, mass: 0.7, stiffness: 160 }, durationInFrames: 28 });
  const rule = ramp(frame, titleAt + 6, titleAt + 26, Easing.out(Easing.cubic));
  const tt = getEntrance(frame, fps, titleAt, titleAt + 26);
  return (
    <>
      {small ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: top - 90, textAlign: "center", opacity: ramp(frame, smallAt, smallAt + 12), zIndex: 20 }}>
          <Label size={26} spacing={10}>{small}</Label>
        </div>
      ) : null}
      <Card start={0} dur={26} left={260} top={top} width={1400} height={460} name="chapter card" rotate={-0.8} pad="0" stroke={-26}>
        <div
          style={{
            position: "absolute",
            left: 60,
            top: 40,
            width: 340,
            height: 380,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: ARIAL,
            fontSize: 360,
            lineHeight: 1,
            color: C.red,
            opacity: interpolate(frame, [numAt, numAt + 6], [0, 1], clamp),
            transform: `scale(${interpolate(num, [0, 1], [1.4, 1])})`,
          }}
        >
          {n}
        </div>
        <div style={{ position: "absolute", left: 430, top: 60, bottom: 60, width: 6, background: C.ink, opacity: 0.85 }} />
        <div style={{ position: "absolute", left: 480, top: 0, bottom: 0, right: 60, display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div style={{ opacity: ramp(frame, numAt, numAt + 12) }}>
            <Label size={30} spacing={12} color={C.red}>CHAPTER {n}</Label>
          </div>
          <div style={{ opacity: tt.opacity, transform: `translateY(${riseFrom(tt.progress, 40)}px)`, marginTop: 22 }}>
            <div style={{ fontFamily: ARIAL, fontSize: 76, lineHeight: 1.04, letterSpacing: -2, color: C.ink }}>{title}</div>
          </div>
          <div style={{ height: 8, width: 300, background: C.red, marginTop: 28, transformOrigin: "left center", transform: `scaleX(${rule})` }} />
        </div>
      </Card>
    </>
  );
};

/* ------------------------------------------------------------------ */
/* Odometer: dark drum with rolling digits.                            */
/* ------------------------------------------------------------------ */
export const Odometer: React.FC<{ from: number; to: number; at: number; dur?: number; width: number; hlFirst?: boolean; digits?: number }> = ({ from, to, at, dur = 24, width, hlFirst, digits = 6 }) => {
  const frame = useCurrentFrame();
  const v = from + (to - from) * ramp(frame, at, at + dur, Easing.inOut(Easing.cubic));
  const cellW = width / digits;
  const h = cellW * 1.5;
  const cells = [];
  for (let i = 0; i < digits; i++) {
    const place = 10 ** (digits - 1 - i);
    const d = Math.floor(v / place) % 10;
    // a wheel turns only while every wheel to its right is rolling from 9 to 0
    const lower = v % place;
    const frac = Math.max(0, lower - (place - 1));
    cells.push(
      <div key={i} style={{ position: "relative", width: cellW - 8, height: h, overflow: "hidden", background: i === 0 && hlFirst ? C.red : "#26201A", borderRadius: 6 }}>
        {[0, 1].map((k) => (
          <div
            key={k}
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: (k - frac) * h,
              height: h,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: ARIAL,
              fontSize: h * 0.62,
              color: C.card,
            }}
          >
            {(d + k) % 10}
          </div>
        ))}
      </div>,
    );
  }
  return (
    <div data-fit="odometer" style={{ display: "flex", gap: 8, padding: 14, background: C.inkDeep, borderRadius: 12, width: width + 28, boxSizing: "border-box", filter: DROP }}>
      {cells}
    </div>
  );
};

/** A red check that draws itself. */
export const Tick: React.FC<{ at: number; size?: number; color?: string }> = ({ at, size = 60, color = C.red }) => {
  const frame = useCurrentFrame();
  const t = ramp(frame, at, at + 10, Easing.out(Easing.cubic));
  return (
    <svg width={size} height={size} viewBox="0 0 60 60" style={{ overflow: "visible" }}>
      <path d="M 8 32 L 24 48 L 54 12" stroke={color} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />
    </svg>
  );
};

/** A big headline that rises in; optional red rule under it. */
export const Headline: React.FC<{ at: number; text: string; left?: number; top: number; size?: number; color?: string; align?: "left" | "center"; width?: number; rule?: boolean; exit?: number }> = ({
  at,
  text,
  left = 0,
  top,
  size = 72,
  color = C.ink,
  align = "center",
  width = 1920,
  rule,
  exit,
}) => {
  const frame = useCurrentFrame();
  const r = ramp(frame, at + 8, at + 26, Easing.out(Easing.cubic));
  return (
    <Rise start={at} dur={24} dist={70} left={left} top={top} width={width} exit={exit} z={22} style={{ filter: "none" }}>
      <div style={{ textAlign: align, fontFamily: ARIAL, fontSize: size, lineHeight: 1.06, letterSpacing: -size * 0.025, color, whiteSpace: "nowrap" }}>{text}</div>
      {rule ? <div style={{ height: 8, width: 220, background: C.red, margin: align === "center" ? "22px auto 0" : "22px 0 0", transform: `scaleX(${r})`, transformOrigin: align === "center" ? "center" : "left center" }} /> : null}
    </Rise>
  );
};

/** A static cut-paper icon (for use inside cards). */
export const Glyph: React.FC<{ kind: keyof typeof ICONS; width: number; dx?: number; style?: React.CSSProperties }> = ({ kind, width, dx = -10, style }) => {
  const id = `g-${React.useId().replace(/:/g, "")}`;
  const ic = ICONS[kind];
  const [, , vw, vh] = ic.vb.split(" ").map(Number);
  return (
    <svg viewBox={ic.vb} width={width} height={(width * vh) / vw} style={{ overflow: "visible", filter: DROP, ...style }}>
      {cutFilter(id, dx * (vw / width))}
      <g filter={`url(#${id})`}>{ic.el}</g>
    </svg>
  );
};

/** Fade-in helper for plain elements. */
export const useIn = (at: number, dur = 12) => {
  const frame = useCurrentFrame();
  return ramp(frame, at, at + dur, Easing.out(Easing.cubic));
};

export { Rise, Label, ramp, clamp };
