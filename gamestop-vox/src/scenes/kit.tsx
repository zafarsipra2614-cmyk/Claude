import React from "react";
import { continueRender, delayRender, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
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

/**
 * Layout QC. Runs in the browser on every rendered frame and logs a FIT error
 * when content spills out of the box it is meant to sit in:
 *   data-fit="name"          every text run and child element must stay inside it
 *   data-box="id"            a backing card…
 *   data-inside="id"         …that this separately positioned element must sit on
 * and every data-fit / data-box element must stay inside the 1920×1080 frame.
 * Run scripts in qc/ to collect the report for the scenes' fullest frames.
 */
export const FitCheck: React.FC = () => {
  const frame = useCurrentFrame();
  React.useLayoutEffect(() => {
    // Measure after the browser has laid the frame out, before the screenshot.
    // Wait until the paper background (and so the frame) is laid out.
    const handle = delayRender("fit check");
    let raf = 0;
    let tries = 0;
    let done = false;
    const finish = () => {
      if (!done) {
        done = true;
        continueRender(handle);
      }
    };
    const tick = () => {
      const paper = document.querySelector("[data-frame] img")?.getBoundingClientRect();
      if (paper && paper.width > 0) {
        try {
          runFitCheck(frame, paper);
        } finally {
          finish();
        }
      } else if (++tries > 600) {
        console.error(`FIT frame=${frame} check could not run: frame never laid out`);
        finish();
      } else {
        raf = requestAnimationFrame(tick);
      }
    };
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      finish();
    };
  });
  return null;
};

type Box = { left: number; top: number; right: number; bottom: number };
const TOL = 6;

const runFitCheck = (frame: number, frameRect: Box) => {
  console.log("FITCHECK", frame);
  const out = (name: string, inner: Box, outer: Box) => {
    const o = { L: outer.left - inner.left, R: inner.right - outer.right, T: outer.top - inner.top, B: inner.bottom - outer.bottom };
    const bad = Object.entries(o)
      .filter(([, v]) => v > TOL)
      .map(([k, v]) => `${k}+${Math.round(v)}px`);
    if (bad.length) console.error(`FIT frame=${frame} ${name}: ${bad.join(" ")}`);
  };
  // checkVisibility walks ancestors, so faded-out (exited) elements are skipped.
  const visible = (el: Element) =>
    (el as Element & { checkVisibility: (o: object) => boolean }).checkVisibility({ checkOpacity: true, checkVisibilityCSS: true });
  const textRects = (el: Element) => {
    const rects: { text: string; r: DOMRect }[] = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n: Node | null;
    while ((n = walker.nextNode())) {
      const text = n.textContent?.trim();
      if (!text) continue;
      const range = document.createRange();
      range.selectNodeContents(n);
      const r = range.getBoundingClientRect();
      if (r.width) rects.push({ text: text.slice(0, 24), r });
    }
    return rects;
  };
  document.querySelectorAll<HTMLElement>("[data-fit]").forEach((box) => {
    if (!visible(box)) return;
    const br = box.getBoundingClientRect();
    if (br.width === 0) return;
    const name = box.dataset.fit!;
    out(`${name} vs frame`, br, frameRect);
    // Text must stay inside the padding, not just inside the border, or it reads as crammed.
    const cs = getComputedStyle(box);
    const pad = (k: string) => Math.max(parseFloat(cs.getPropertyValue(`padding-${k}`)) || 0, 12);
    const content = { left: br.left + pad("left"), right: br.right - pad("right"), top: br.top + pad("top") * 0.5, bottom: br.bottom - pad("bottom") * 0.5 };
    textRects(box).forEach(({ text, r }) => out(`${name} text "${text}"`, r, content));
  });
  document.querySelectorAll<HTMLElement>("[data-inside]").forEach((el) => {
    const box = document.querySelector<HTMLElement>(`[data-box="${el.dataset.inside}"]`);
    if (!box || !visible(el)) return;
    const br = box.getBoundingClientRect();
    textRects(el).forEach(({ text, r }) => out(`${el.dataset.inside} ← "${text}"`, r, br));
  });
};
