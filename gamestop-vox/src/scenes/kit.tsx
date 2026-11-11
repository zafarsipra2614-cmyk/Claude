import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { C, DROP, getEntrance, riseFrom } from "../shared/system";
import { ARIAL } from "../shared/pieces";

export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Linear 0..1 progress between two frames, eased. */
export const ramp = (frame: number, a: number, b: number, ease = Easing.inOut(Easing.cubic)) =>
  interpolate(frame, [a, b], [0, 1], { ...clamp, easing: ease });

/**
 * The one entrance, as a wrapper: absolutely placed, springs up from below,
 * optional red marker block offset behind it (the signature stroke, for
 * rectangular code-drawn subjects).
 */
export const Rise: React.FC<{
  start: number;
  dur?: number;
  dist?: number;
  left: number;
  top?: number;
  bottom?: number;
  width: number;
  height?: number;
  rotate?: number;
  z?: number;
  stroke?: { x: number; y: number; radius?: number };
  exit?: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}> = ({ start, dur = 30, dist = 390, left, top, bottom, width, height, rotate = 0, z = 12, stroke, exit, style, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, start, start + dur);
  const out = exit === undefined ? 0 : ramp(frame, exit, exit + 14, Easing.in(Easing.cubic));
  const y = riseFrom(progress, dist) + out * 120;
  const box: React.CSSProperties = { position: "absolute", left, top, bottom, width, height };
  return (
    <div style={{ ...box, opacity: opacity * (1 - out), transform: `translateY(${y}px) rotate(${rotate}deg)`, zIndex: z }}>
      {stroke ? (
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: 0,
            background: C.red,
            borderRadius: stroke.radius ?? 0,
            transform: `translate(${stroke.x}px, ${stroke.y}px)`,
            opacity: 0.95,
          }}
        />
      ) : null}
      <div style={{ position: "relative", width: "100%", height: "100%", filter: DROP, ...style }}>{children}</div>
    </div>
  );
};

/** Small tracked uppercase label. */
export const Label: React.FC<{ children: React.ReactNode; size?: number; color?: string; spacing?: number; style?: React.CSSProperties }> = ({
  children,
  size = 26,
  color = "rgba(26,26,26,0.62)",
  spacing = 6,
  style,
}) => (
  <div style={{ fontFamily: ARIAL, fontSize: size, letterSpacing: spacing, color, whiteSpace: "nowrap", ...style }}>{children}</div>
);

/** A caption that rises into the top-left, the film's running headline slot. */
export const Kicker: React.FC<{ start: number; text: string; sub?: string; left?: number; top?: number }> = ({
  start,
  text,
  sub,
  left = 110,
  top = 86,
}) => (
  <Rise start={start} dur={22} dist={60} left={left} top={top} width={1100} z={22} style={{ filter: "none" }}>
    <div style={{ height: 6, width: 90, background: C.red, marginBottom: 16 }} />
    <div style={{ fontFamily: ARIAL, fontSize: 64, letterSpacing: -1.5, color: C.ink, lineHeight: 1, whiteSpace: "nowrap" }}>{text}</div>
    {sub ? <Label style={{ marginTop: 14 }}>{sub}</Label> : null}
  </Rise>
);

/** Polyline helpers for the self-drawing charts. */
export type Pt = { x: number; y: number };
export const pathOf = (pts: Pt[]) => pts.map((p, i) => `${i ? "L" : "M"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
/** Point and segment index at fraction t of the polyline's length. */
export const along = (pts: Pt[], t: number) => {
  const seg = pts.slice(1).map((p, i) => Math.hypot(p.x - pts[i].x, p.y - pts[i].y));
  const total = seg.reduce((a, b) => a + b, 0);
  let d = t * total;
  for (let i = 0; i < seg.length; i++) {
    if (d <= seg[i] || i === seg.length - 1) {
      const f = seg[i] ? Math.min(1, d / seg[i]) : 0;
      return { x: pts[i].x + (pts[i + 1].x - pts[i].x) * f, y: pts[i].y + (pts[i + 1].y - pts[i].y) * f, i, f };
    }
    d -= seg[i];
  }
  return { ...pts[pts.length - 1], i: seg.length - 1, f: 1 };
};
