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
  /** "over": an intentional overlay (allowed to sit on other boxes in the fit audit). */
  layer?: "over";
  style?: React.CSSProperties;
  children?: React.ReactNode;
}> = ({ start, dur = 30, dist = 390, left, top, bottom, width, height, rotate = 0, z = 12, stroke, exit, layer, style, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { opacity, progress } = getEntrance(frame, fps, start, start + dur);
  const out = exit === undefined ? 0 : ramp(frame, exit, exit + 14, Easing.in(Easing.cubic));
  const y = riseFrom(progress, dist) + out * 120;
  const box: React.CSSProperties = { position: "absolute", left, top, bottom, width, height };
  return (
    <div
      data-moving={progress < 0.995 || out > 0 ? "" : undefined}
      data-layer={layer}
      style={{ ...box, opacity: opacity * (1 - out), transform: `translateY(${y}px) rotate(${rotate}deg)`, zIndex: z }}
    >
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
 * Layout QC. Runs in the browser on every rendered frame and logs FIT errors
 * (see runFitCheck for the rules). Tags:
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

/**
 * The audit. Elements still entering or exiting (inside [data-moving]) are
 * skipped, so it judges the settled layout. It reports:
 *   CONTAIN  text crosses its container's padding, or a box leaves the frame
 *   COVERED  something painted sits on top of a run of text
 *   OVERLAP  two runs of text overlap, or two boxes collide
 *            (boxes marked data-layer="over" — stamps, pinned cards — are
 *            allowed to sit on other boxes, but still may not cover text)
 */
const runFitCheck = (frame: number, frameRect: Box) => {
  console.log("FITCHECK", frame);
  const report = (kind: string, msg: string) => console.error(`FIT frame=${frame} ${kind} ${msg}`);
  const sides = (inner: Box, outer: Box) =>
    Object.entries({ L: outer.left - inner.left, R: inner.right - outer.right, T: outer.top - inner.top, B: inner.bottom - outer.bottom })
      .filter(([, v]) => v > TOL)
      .map(([k, v]) => `${k}+${Math.round(v)}px`);
  const contain = (name: string, inner: Box, outer: Box) => {
    const bad = sides(inner, outer);
    if (bad.length) report("CONTAIN", `${name}: ${bad.join(" ")}`);
  };
  const inter = (a: Box, b: Box) => {
    const w = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const h = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    return w > TOL && h > TOL ? { w: Math.round(w), h: Math.round(h) } : null;
  };
  // checkVisibility walks ancestors, so faded-out elements are skipped.
  const visible = (el: Element) =>
    (el as Element & { checkVisibility: (o: object) => boolean }).checkVisibility({ checkOpacity: true, checkVisibilityCSS: true });
  const settled = (el: Element) => !el.closest("[data-moving]");
  const live = (el: Element) => visible(el) && settled(el);
  const describe = (el: Element) => {
    const fit = el.closest<HTMLElement>("[data-fit]")?.dataset.fit;
    const txt = el.textContent?.trim().slice(0, 20);
    return fit ? `[${fit}]` : txt ? `<${el.tagName.toLowerCase()} "${txt}">` : `<${el.tagName.toLowerCase()}>`;
  };
  const scene = document.querySelector("[data-frame]");
  if (!scene) return;

  // --- every visible, settled run of text, one rect per rendered line
  type Run = { el: Element; text: string; lines: DOMRect[]; box: Box };
  const runs: Run[] = [];
  const walker = document.createTreeWalker(scene, NodeFilter.SHOW_TEXT);
  let n: Node | null;
  while ((n = walker.nextNode())) {
    const text = n.textContent?.trim();
    const el = n.parentElement;
    if (!text || !el || !live(el)) continue;
    const range = document.createRange();
    range.selectNodeContents(n);
    const lines = Array.from(range.getClientRects()).filter((r) => r.width > 1 && r.height > 1);
    if (!lines.length) continue;
    runs.push({ el, text: text.slice(0, 24), lines, box: range.getBoundingClientRect() });
  }

  // --- CONTAIN: tagged boxes inside the frame, their text inside their padding
  const boxes = Array.from(scene.querySelectorAll<HTMLElement>("[data-fit]")).filter(live);
  for (const box of boxes) {
    const br = box.getBoundingClientRect();
    if (br.width === 0) continue;
    const name = box.dataset.fit!;
    contain(`${name} vs frame`, br, frameRect);
    const cs = getComputedStyle(box);
    const pad = (k: string) => Math.max(parseFloat(cs.getPropertyValue(`padding-${k}`)) || 0, 12);
    const content = { left: br.left + pad("left"), right: br.right - pad("right"), top: br.top + pad("top") * 0.5, bottom: br.bottom - pad("bottom") * 0.5 };
    runs.filter((r) => box.contains(r.el)).forEach((r) => contain(`${name} text "${r.text}"`, r.box, content));
  }
  // all text inside the frame, tagged or not
  runs.forEach((r) => contain(`text "${r.text}" vs frame`, r.box, frameRect));
  // text positioned over a separate backing card
  scene.querySelectorAll<HTMLElement>("[data-inside]").forEach((el) => {
    const card = scene.querySelector<HTMLElement>(`[data-box="${el.dataset.inside}"]`);
    if (!card || !live(el)) return;
    const cr = card.getBoundingClientRect();
    runs.filter((r) => el.contains(r.el)).forEach((r) => contain(`${el.dataset.inside} ← "${r.text}"`, r.box, cr));
  });

  // --- COVERED: hit-test points across every line of text
  const painted = (e: Element) => {
    if (e instanceof HTMLImageElement) return true;
    if (e instanceof SVGGeometryElement || e instanceof SVGTextElement) return true; // hit only where it paints
    if (e instanceof SVGElement) return false; // <svg>, <g>: transparent containers
    const cs = getComputedStyle(e);
    const bg = cs.backgroundColor;
    const hasBg = !(bg === "transparent" || /rgba\(.*,\s*0\)$/.test(bg));
    const hasBorder = parseFloat(cs.borderTopWidth) > 0 && cs.borderTopStyle !== "none" && !/rgba\(.*,\s*0\)$/.test(cs.borderTopColor);
    return hasBg || cs.backgroundImage !== "none" || hasBorder;
  };
  const covered = new Set<string>();
  for (const r of runs) {
    for (const line of r.lines) {
      for (const fx of [0.08, 0.3, 0.5, 0.7, 0.92]) {
        const x = line.left + line.width * fx;
        const y = line.top + line.height * 0.5;
        const stack = document.elementsFromPoint(x, y);
        const own = stack.indexOf(r.el);
        const above = own < 0 ? stack : stack.slice(0, own);
        for (const e of above) {
          if (e.contains(r.el) || r.el.contains(e)) continue; // ancestor, or a deliberate mark on the text (strike)
          if (!live(e) || !painted(e)) continue;
          covered.add(`text "${r.text}" covered by ${describe(e)}`);
          break;
        }
      }
    }
  }
  covered.forEach((m) => report("COVERED", m));

  // --- OVERLAP: text on text (different elements), and box on box
  const seen = new Set<string>();
  for (let i = 0; i < runs.length; i++)
    for (let j = i + 1; j < runs.length; j++) {
      const a = runs[i], b = runs[j];
      if (a.el === b.el || a.el.contains(b.el) || b.el.contains(a.el)) continue;
      for (const la of a.lines)
        for (const lb of b.lines) {
          // shrink line boxes to the glyph band so stacked lines don't touch
          const sh = (l: DOMRect) => ({ left: l.left, right: l.right, top: l.top + l.height * 0.2, bottom: l.bottom - l.height * 0.2 });
          const o = inter(sh(la), sh(lb));
          const key = `${a.text}|${b.text}`;
          if (o && !seen.has(key)) {
            seen.add(key);
            report("OVERLAP", `text "${a.text}" and "${b.text}" (${o.w}×${o.h}px)`);
          }
        }
    }
  for (let i = 0; i < boxes.length; i++)
    for (let j = i + 1; j < boxes.length; j++) {
      const a = boxes[i], b = boxes[j];
      if (a.contains(b) || b.contains(a)) continue;
      const over = (e: HTMLElement) => !!e.closest('[data-layer="over"]');
      if (over(a) || over(b)) continue;
      const o = inter(a.getBoundingClientRect(), b.getBoundingClientRect());
      if (o) report("OVERLAP", `boxes [${a.dataset.fit}] and [${b.dataset.fit}] (${o.w}×${o.h}px)`);
    }
};
