// "STAR in Four Stamps": a 49 s vertical Reel in the Mid-century Cartoon style.
// One timeline (120 bpm, 1 beat = 0.5 s) drives picture, captions, sound events and the score.
import { PAL, setClock, shape, plane, ink, ellipse, rrect, rect, spline, xform, move, text, fit, measure, star, sparkle, rays,
  dashed, paperFinish, clamp, lerp, seg, ss, eo, eio, back, twos, TAU, reg, path } from './engine/toon.js';
import { drawHand } from './engine/chars_base.js';
import { drawCand, CC } from './engine/cand.js';
import { icon } from './engine/icons.js';

export const W = 1080, H = 1920, BPM = 120, BEAT = 60 / BPM;
export const DUR = 49.0;

const COL = {
  paper: '#F4EAD5', paperD: '#E6D8BC', ink: '#2B2420',
  product: '#D9483B', productD: '#A8322A',          // the answer card's band and the book's red: one colour all film
  accent: '#E8B43A',                                // the caption stars and bullets
  hook: '#7F9CC0', wrong: '#E8B43A', turn: '#E6D8BC', payoff: '#6E4A6B', cta: '#7F9CC0', ray: '#F3D37F', block: '#B5C8DE',
  steps: ['#E8B43A', '#8FB0D6', '#A7AE5B', '#F0B4A8'],
};
const hx = c => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16));
const mix = (a, b, k) => { const A = hx(a), B = hx(b); return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * k).toString(16).padStart(2, '0')).join(''); };
const shade = (c, k) => mix(c, '#2B2420', k);

// ---------------------------------------------------------------- the timeline
export const SEC = [
  { id: 'hook', t0: 0, t1: 4 }, { id: 'wrong', t0: 4, t1: 10 }, { id: 'turn', t0: 10, t1: 13 },
  { id: 'step', i: 0, t0: 13, t1: 19 }, { id: 'step', i: 1, t0: 19, t1: 25 }, { id: 'step', i: 2, t0: 25, t1: 31 }, { id: 'step', i: 3, t0: 31, t1: 37 },
  { id: 'payoff', t0: 37, t1: 43 }, { id: 'cta', t0: 43, t1: DUR },
];
export const STEPS = [
  { L: 'S', name: 'Situation', detail: 'Final-year module · team of 5 · 3 weeks' },
  { L: 'T', name: 'Task', detail: '2 teammates kept missing deadlines' },
  { L: 'A', name: 'Action', detail: 'Split the work into dated milestones + a shared tracker' },
  { L: 'R', name: 'Result', detail: 'Submitted 2 days early · top marks' },
];
export const SHARE = [15, 10, 50, 25];
// narration: id, start, caption (what the viewer reads), burn = drawn on the caption card
export const VO = [
  { id: 'q', t: 0.35, cap: 'Tell me about a time you worked in a team.', burn: false },
  { id: 'weak', t: 4.25, cap: 'Most people say: “We did a group project, and it went pretty well.”', burn: true },
  { id: 'nothing', t: 8.6, cap: 'That tells them nothing.', burn: true },
  { id: 'turn', t: 10.75, cap: 'Use the STAR method instead.', burn: true },
  { id: 's', t: 13.25, cap: 'S is for Situation. Set the scene in one sentence.', burn: true },
  { id: 't', t: 19.25, cap: 'T is for Task. What were you responsible for?', burn: true },
  { id: 'a', t: 25.25, cap: 'A is for Action. What did you do? This is the longest part.', burn: true },
  { id: 'r', t: 31.25, cap: 'R is for Result. End on a number, or a lesson.', burn: true },
  { id: 'time', t: 38.0, cap: 'Keep it under a minute. Spend half of it on Action.', burn: true },
  { id: 'cta', t: 43.6, cap: 'Every common question, broken down. Get the Offer. Link in bio.', burn: true },
];
let DURS = {};
export function setup(durs) { DURS = durs || {}; }
const vdur = id => DURS[id] ?? 2.5;
export function cues() {
  return VO.map((v, k) => {
    const nx = VO[k + 1], d = vdur(v.id);
    let t1 = Math.max(v.t + 1.8, v.t + d + 0.6, v.t + v.cap.replace(/\s/g, '').length / 15 + 0.8);
    if (nx) t1 = Math.min(t1, nx.t - 0.08);
    t1 = Math.min(t1, 48.15);
    return { id: v.id, t0: v.t, t1, text: v.cap, burn: v.burn };
  });
}
const STAMP = i => SEC[3 + i].t0;               // the stamp lands on the downbeat of its step
const DETAIL = i => STAMP(i) + (i === 2 ? 2.0 : 2.0);

export const section = t => SEC.find(s => t >= s.t0 && t < s.t1) || SEC[SEC.length - 1];
const pop = (t, t0, d = 0.28) => back(seg(t, t0, t0 + d), 1.9);

// ---------------------------------------------------------------- shared pieces
function bg(ctx, col) { ctx.fillStyle = col; ctx.fillRect(-3000, -3000, 7080, 7920); }
function floor(ctx, col, y) {
  plane(ctx, rect(-2000, y, 5080, 3000), shade(col, 0.16));
  ink(ctx, [[-60, y], [W + 60, y]], 4, { seed: 31, breaks: 0.22, taper: false });
}
function polka(ctx, col, y0, y1, seed = 1) {
  ctx.save(); ctx.globalAlpha = 0.18; ctx.fillStyle = col;
  for (let y = y0, r = 0; y < y1; y += 70, r++) for (let x = (r % 2) * 35; x < W + 40; x += 70) { ctx.beginPath(); ctx.arc(x, y, 6, 0, TAU); ctx.fill(); }
  ctx.restore();
}
// world → screen camera
function cam(ctx, c) { ctx.translate(W / 2, H / 2); ctx.scale(c.z, c.z); ctx.rotate(c.r || 0); ctx.translate(-c.cx, -c.cy); }
const w2s = (x, y, c) => { const dx = x - c.cx, dy = y - c.cy, co = Math.cos(c.r || 0), si = Math.sin(c.r || 0); return [W / 2 + c.z * (co * dx - si * dy), H / 2 + c.z * (si * dx + co * dy)]; };
let TX = [];                                      // texts on screen this frame (for readcheck)
function reportText(id, str, box, c) {
  const a = c ? w2s(box[0], box[1], c) : [box[0], box[1]], b = c ? w2s(box[2], box[3], c) : [box[2], box[3]];
  TX.push({ id, text: str, x0: Math.min(a[0], b[0]), y0: Math.min(a[1], b[1]), x1: Math.max(a[0], b[0]), y1: Math.max(a[1], b[1]) });
}

// ---------------------------------------------------------------- the question card (hook, then shrinks to the top)
const QTEXT = 'Tell me about a time you worked in a team.';
function questionCard(ctx, t, x, y, k, c) {
  if (k <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(k, k);
  const w = 900, h = 380;
  shape(ctx, rrect(-w / 2 + 14, -h / 2 + 14, w, h, 26), { fill: shade(COL.hook, 0.35), line: 0, off: [0, 0], grain: 0, alpha: 0.5 });
  shape(ctx, rrect(-w / 2, -h / 2, w, h, 26), { fill: COL.paper, line: 4.5, seed: 200, grain: 0.15, breaks: 0.08 });
  text(ctx, 'THE INTERVIEWER ASKS', 0, -h / 2 + 64, { font: '600 26px Jost', fill: COL.productD, align: 'center', track: 6 });
  text(ctx, '“', -w / 2 + 70, -h / 2 + 150, { font: '120px Slab', fill: COL.product, plate: COL.ink, off: [4, 4] });
  const f = fit(ctx, QTEXT, '600 {px}px Jost', 62, 700, 3, 44);
  f.lines.forEach((l, i) => text(ctx, l, 20, -h / 2 + 150 + i * f.px * 1.18 + (3 - f.lines.length) * f.px * 0.5, { font: f.font, fill: COL.ink, align: 'center' }));
  ctx.restore();
  reportText('question', QTEXT, [x - 450 * k, y - 190 * k, x + 450 * k, y + 190 * k], c);
}

// ---------------------------------------------------------------- the answer card (the product of the film)
const CARD = { x: 70, y: 470, w: 940, h: 860 };
const rowY = i => 596 + i * 178;
const slot = i => [176, rowY(i) + 82];
function answerCard(ctx, t, o = {}) {
  const { x, y, w, h } = CARD;
  plane(ctx, rrect(x + 16, y + 16, w, h, 28), shade(o.ground || COL.turn, 0.28));
  shape(ctx, rrect(x, y, w, h, 28), { fill: COL.paper, line: 5, seed: 300, grain: 0.18, breaks: 0.08 });
  // the red band
  const band = [[x + 4, y + 30], ...rrect(x + 4, y + 4, w - 8, 96, 24).slice(0, 12).filter(p => p[1] < y + 60), [x + w - 4, y + 30], [x + w - 4, y + 100], [x + 4, y + 100]];
  shape(ctx, rrect(x + 6, y + 6, w - 12, 92, 22), { fill: COL.product, line: 0, seed: 301, grain: 0.3 });
  ink(ctx, [[x, y + 100], [x + w, y + 100]], 4, { seed: 302, taper: false, breaks: 0.1 });
  text(ctx, 'MY ANSWER', x + 48, y + 70, { font: '46px Slab', fill: COL.paper, plate: COL.ink, off: [3, 3] });
  text(ctx, '“A time you worked in a team”', x + w - 40, y + 66, { font: '500 26px Jost', fill: COL.paper, align: 'right' });
  for (let i = 0; i < 4; i++) {
    const [sx, sy] = slot(i), y0 = rowY(i);
    if (i) ink(ctx, [[x + 40, y0 - 6], [x + w - 40, y0 - 6]], 2.4, { seed: 303 + i, color: shade(COL.paperD, 0.2), breaks: 0.35, taper: false });
    const st = o.stamped ? o.stamped(i) : 0;
    if (st <= 0) {   // the empty slot: dashed circle, ghost letter
      const k = o.slotK ? o.slotK(i) : 1;
      if (k > 0) {
        ctx.save(); ctx.translate(sx, sy); ctx.scale(k, k);
        dashed(ctx, ellipse(0, 0, 62, 62, 64), 3.4, 12, 10, 0, COL.ink);
        text(ctx, STEPS[i].L, 0, 24, { font: '68px Slab', fill: COL.ink, align: 'center', alpha: 0.18 });
        ctx.restore();
      }
    } else medallion(ctx, t, i, sx, sy, 62, st);
    // the label and detail arrive with the stamp
    const lk = o.label ? o.label(i) : 0;
    if (lk > 0) {
      text(ctx, STEPS[i].name.toUpperCase(), 270, y0 + 56, { font: '40px Slab', fill: COL.ink, plate: COL.steps[i], off: [4, 3], alpha: clamp(lk * 2) });
      reportText('row' + i, STEPS[i].name.toUpperCase(), [270, y0 + 18, 270 + 330, y0 + 64], o.cam);
    }
    const dk = o.detail ? o.detail(i) : 0;
    if (dk > 0) {
      const f = fit(ctx, STEPS[i].detail, '500 {px}px Jost', 36, 680, 2, 28);
      ctx.save(); ctx.translate(270, y0 + 82); ctx.scale(lerp(0.6, 1, back(dk, 1.6)), lerp(0.6, 1, back(dk, 1.6))); ctx.globalAlpha *= clamp(dk * 3);
      star(ctx, -2, 4 + f.px * 0.1, 0, {});
      f.lines.forEach((l, j) => text(ctx, l, 0, f.px * 0.95 + j * f.px * 1.18, { font: f.font, fill: COL.ink }));
      ctx.restore();
      if (dk >= 1) reportText('detail' + i, STEPS[i].detail, [270, y0 + 82, 270 + 680, y0 + 82 + f.lines.length * f.px * 1.2], o.cam);
    }
  }
}
function medallion(ctx, t, i, x, y, r, k) {
  if (k <= 0) return;
  ctx.save(); ctx.translate(x, y); ctx.scale(k, k); ctx.rotate((1 - Math.min(k, 1)) * 0.5);
  star(ctx, 0, 0, r * 1.24, { n: 16, inner: 0.82, fill: PAL.white, off: [0, 0], rot: i * 0.2 });
  shape(ctx, ellipse(0, 0, r, r, 60), { fill: COL.steps[i], line: 5, seed: 730 + i, grain: 0.3 });
  text(ctx, STEPS[i].L, 0, r * 0.4, { font: `${Math.round(r * 1.15)}px Slab`, fill: COL.ink, plate: PAL.white, off: [4, 4], align: 'center' });
  ctx.restore();
}

// the candidate's arm with a rubber stamp or a pointing hand, entering from the right edge
function rubberStamp(ctx, x, y, squash = 0) {
  // (x,y) = centre of the rubber face
  shape(ctx, rrect(x - 52, y - 30 + squash * 6, 104, 30 - squash * 6, 6), { fill: COL.productD, line: 4, seed: 410, grain: 0.2 });
  shape(ctx, rrect(x - 62, y - 54, 124, 26, 8), { fill: '#A2713F', line: 4, seed: 411, grain: 0.3 });
  shape(ctx, rrect(x - 16, y - 120, 32, 70, 8), { fill: '#C9955D', line: 4, seed: 412, grain: 0.3 });
  shape(ctx, ellipse(x, y - 132, 34, 26, 24), { fill: '#C9955D', line: 4, seed: 413, grain: 0.3, shade: [{ pts: ellipse(x + 10, y - 126, 30, 22, 20), color: '#A2713F', alpha: 0.5 }] });
}
function armFromRight(ctx, hx, hy, kind, a = Math.PI * 0.95) {
  // sleeve: from the right edge down to the wrist
  const sx = W + 160, sy = hy - 90;
  const P = spline([[sx, sy], [lerp(sx, hx, 0.55) + 40, lerp(sy, hy, 0.4) - 30], [hx + Math.cos(a + Math.PI) * 16, hy + Math.sin(a + Math.PI) * 16]], false, 8);
  ink(ctx, P, 44, { seed: 420, taper: false, wob: 0.06 });
  const o = reg(420, 1);
  ink(ctx, move(P, o[0] * 0.6, o[1] * 0.6), 33, { seed: 421, taper: false, wob: 0.05, color: CC.jacket });
  const e = P[P.length - 1]; ink(ctx, [[e[0] + Math.cos(a + 1.57) * 16, e[1] + Math.sin(a + 1.57) * 16], [e[0] - Math.cos(a + 1.57) * 16, e[1] - Math.sin(a + 1.57) * 16]], 8, { seed: 422, taper: false, color: CC.shirt });
  drawHand(ctx, hx, hy, a, kind, 1, 1.5, CC.skin);
}
// the stamping hand for step i (two-frame holds: limited animation)
function stampHand(ctx, t, i) {
  const ts = STAMP(i), u = twos(t);
  if (u < ts - 0.8 || u > ts + 1.1) return;
  const [sx, sy] = slot(i), up = [sx + 10, sy - 150], off = [W + 260, sy - 170];
  let p, squash = 0;
  if (u < ts - 0.3) p = [lerp(off[0], up[0], eo(seg(u, ts - 0.8, ts - 0.3))), lerp(off[1], up[1], eo(seg(u, ts - 0.8, ts - 0.3)))];
  else if (u < ts - 0.09) p = [up[0], up[1] - 40 * ss(seg(u, ts - 0.3, ts - 0.12))];                 // anticipation: lift
  else if (u < ts) p = [sx, lerp(up[1] - 40, sy - 6, seg(u, ts - 0.09, ts))];                       // strike
  else if (u < ts + 0.14) { p = [sx, sy - 6]; squash = 1; }                                          // hold, squash
  else if (u < ts + 0.42) p = [sx + 8, lerp(sy - 6, sy - 170, eo(seg(u, ts + 0.14, ts + 0.42)))];    // recoil
  else p = [lerp(sx + 8, off[0], ss(seg(u, ts + 0.5, ts + 1.1))), lerp(sy - 170, off[1], ss(seg(u, ts + 0.5, ts + 1.1)))];
  // stamp face centre = p; the hand grips the knob above it
  rubberStamp(ctx, p[0], p[1], squash);
  armFromRight(ctx, p[0] + 34, p[1] - 140, 'grip', Math.PI * 0.92);
}
// A step: the pointing finger leads the camera to the Action row
function pointHand(ctx, t) {
  const t0 = STAMP(2) + 1.0, u = twos(t);
  if (u < t0 || u > t0 + 3.6) return;
  const y = rowY(2) + 168, tgt = [1005, y], off = [W + 300, y + 260];
  let k = u < t0 + 0.5 ? eo(seg(u, t0, t0 + 0.5)) : u > t0 + 3.0 ? 1 - ss(seg(u, t0 + 3.0, t0 + 3.6)) : 1;
  const tap = u > t0 + 1.2 && u < t0 + 1.5 ? Math.sin(seg(u, t0 + 1.2, t0 + 1.5) * Math.PI) * 14 : 0;
  armFromRight(ctx, lerp(off[0], tgt[0], k) - tap, lerp(off[1], tgt[1], k) + tap * 0.3, 'point', Math.PI * 1.08);
}

// ---------------------------------------------------------------- step header (screen space, slides in on twos)
function stepHeader(ctx, t, i, t0) {
  const k = eo(seg(twos(t), t0 + 0.05, t0 + 0.4)); if (k <= 0) return;
  ctx.save(); ctx.translate(-(1 - k) * 700, 0);
  shape(ctx, ellipse(150, 322, 76, 76, 48), { fill: COL.ink, line: 0, seed: 700, grain: 0.1, off: [0, 0] });
  text(ctx, STEPS[i].L, 150, 356, { font: '92px Slab', fill: COL.paper, align: 'center', plate: COL.steps[i], off: [4, 4] });
  text(ctx, `STEP ${i + 1} OF 4`, 252, 284, { font: '600 28px Jost', fill: COL.ink, track: 6 });
  text(ctx, STEPS[i].name, 250, 378, { font: '84px Slab', fill: COL.ink, plate: PAL.white, off: [4, 4] });
  ctx.restore();
  if (k >= 1) reportText('header', STEPS[i].name, [74, 246, 900, 400]);
}

// ---------------------------------------------------------------- HOOK 0–4: the question lands
function sceneHook(ctx, t) {
  const c = { cx: 540, cy: 960, z: lerp(1.0, 1.06, ss(t / 4)), r: 0 };
  bg(ctx, COL.hook);
  ctx.save(); cam(ctx, c);
  rays(ctx, 540, 600, 30, 1500, PAL.white, { alpha: 0.12, rot: t * 0.05 });
  floor(ctx, COL.hook, 1440);
  const u = twos(t);
  const face = u < 0.6 ? 'neutral' : u < 2.5 ? 'wow' : 'worried';
  // tugging the tie: anticipation (arm drops) → reach → settle
  const tug = seg(u, 2.6, 3.1), back1 = seg(u, 3.4, 3.8);
  const armF = { a1: lerp(1.4, -2.2 + 0.0, ss(tug) * (1 - ss(back1))) , a2: lerp(1.52, -0.6, ss(tug) * (1 - ss(back1))) };
  drawCand(ctx, { x: 540, y: 1440, s: 1.08, view: 'front', face, look: u > 0.6 && u < 2.5 ? [0, -5] : [0, 0], blink: (u > 1.9 && u < 2.0) ? 1 : 0,
    armF: tug > 0 ? { a1: lerp(1.4, -1.95, ss(tug) * (1 - ss(back1))), a2: lerp(1.52, -2.9, ss(tug) * (1 - ss(back1))) } : undefined, handF: tug > 0.3 && back1 < 0.7 ? 'grip' : 'open' });
  // sweat drop when worried
  if (u > 2.5) { const d = seg(u, 2.5, 3.6); ctx.save(); ctx.globalAlpha = 1 - d * 0.6; shape(ctx, spline([[650, 900 + d * 40], [662, 924 + d * 40], [650, 936 + d * 40], [638, 924 + d * 40]], true, 4), { fill: PAL.white, line: 3, seed: 230 }); ctx.restore(); }
  ctx.restore();
  // the kicker writes on, the card pops (screen space so the push doesn't eat the margins)
  const wk = seg(t, 0.0, 0.5);
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 120 + 860 * wk, H); ctx.clip();
  text(ctx, 'Interview tip', 540, 300, { font: '700 92px Oleo', fill: COL.ink, plate: COL.ray, off: [5, 4], align: 'center' });
  ctx.restore();
  if (wk >= 1) reportText('kicker', 'Interview tip', [260, 220, 820, 320]);
  questionCard(ctx, t, 540, 600, pop(t, 0.25, 0.3), null);
}

// ---------------------------------------------------------------- WRONG 4–10: the flat answer, then what they hear
const WEAK = ['We did a group project…', 'it went pretty well.'];
function sceneWrong(ctx, t) {
  bg(ctx, COL.wrong);
  polka(ctx, COL.paper, 1000, 1440);
  floor(ctx, COL.wrong, 1440);
  const u = twos(t);
  const talking = u > 4.25 && u < 4.25 + vdur('weak');
  const talk = talking ? (Math.floor(u * 12) % 3 === 0 ? 0.2 : Math.floor(u * 12) % 3 === 1 ? 0.9 : 0.55) : 0;
  // shrug on "pretty well": both hands open, palms up
  const sh = ss(seg(u, 6.4, 6.7)) * (1 - ss(seg(u, 7.6, 8.0)));
  const face = u > 8.5 ? 'worried' : u > 6.4 && u < 8 ? 'happy' : 'neutral';
  drawCand(ctx, { x: 300, y: 1440, s: 1.12, view: 'q', face, talk, blink: (u > 5.4 && u < 5.5) ? 1 : 0,
    armF: { a1: lerp(1.3, 0.55, sh), a2: lerp(1.52, -0.35, sh) }, armB: { a1: lerp(1.86, 2.55, sh), a2: lerp(1.7, 3.6, sh) }, handF: sh > 0.5 ? 'open' : 'open' });
  // speech balloon
  const bk = pop(t, 4.35, 0.3);
  if (bk > 0) {
    ctx.save(); ctx.translate(720, 720); ctx.scale(bk, bk); ctx.translate(-720, -720);
    const bx = 430, by = 560, bw = 600, bh = 260;
    shape(ctx, [...rrect(bx, by, bw, bh, 40).slice(0, 18), [bx + 120, by + bh], [bx + 30, by + bh + 120], [bx + 60, by + bh], ...rrect(bx, by, bw, bh, 40).slice(18)], { fill: COL.paper, line: 4.5, seed: 240, grain: 0.15, breaks: 0.06 });
    WEAK.forEach((l, i) => text(ctx, l, bx + bw / 2, by + 108 + i * 64, { font: 'italic 500 46px Jost', fill: COL.ink, align: 'center' }));
    ctx.restore();
    if (bk >= 1) reportText('balloon', WEAK.join(' '), [430, 560, 1030, 820]);
  }
  // the question shrinks to the top and stays as the context
  const qk = lerp(1, 0.62, eio(seg(t, 4.0, 4.45)));
  questionCard(ctx, t, 540, lerp(600, 330, eio(seg(t, 4.0, 4.45))), qk, null);
  // split frame at 6.6: a colour block rises — what the interviewer hears
  const kb = eio(seg(t, 6.6, 6.9));
  if (kb > 0) {
    const yb = lerp(H, 990, kb);
    ctx.save(); ctx.beginPath(); ctx.rect(0, yb, W, H); ctx.clip();
    bg(ctx, COL.block); polka(ctx, PAL.white, yb + 40, H, 3);
    text(ctx, 'WHAT THE INTERVIEWER HEARS', 540, 1070, { font: '600 30px Jost', fill: COL.ink, align: 'center', track: 5 });
    shape(ctx, rrect(170, 1110, 740, 240, 18), { fill: COL.paper, line: 4, seed: 250, grain: 0.15 });
    for (let k = 0; k < 4; k++) dashed(ctx, [[200, 1170 + k * 48], [880, 1170 + k * 48]], 2, 8, 10, 0, shade(COL.block, 0.2));
    text(ctx, 'group project… fine?', 220, 1160, { font: '400 44px Oleo', fill: COL.inkSoft || COL.ink, alpha: 0.75 });
    // the X stamp
    const xk = pop(t, 8.5, 0.24);
    if (xk > 0) {
      ctx.save(); ctx.translate(540, 1240); ctx.scale(xk, xk); ctx.rotate(-0.08);
      ink(ctx, [[-120, -100], [120, 100]], 30, { seed: 260, taper: false, color: COL.ink });
      ink(ctx, [[120, -100], [-120, 100]], 30, { seed: 261, taper: false, color: COL.ink });
      ctx.restore();
    }
    ctx.restore();
    ink(ctx, [[-10, yb], [W + 10, yb]], 6, { seed: 262 });
    if (kb >= 1) reportText('hears', 'WHAT THE INTERVIEWER HEARS', [120, 1036, 960, 1080]);
  }
}

// ---------------------------------------------------------------- TURN 10–13: an empty card, four empty circles
function sceneTurn(ctx, t, groundOverride) {
  bg(ctx, groundOverride || COL.turn);
  polka(ctx, COL.paper, 0, H, 5);
  answerCard(ctx, t, { ground: COL.turn, slotK: i => pop(t, 11.0 + i * 0.5, 0.26) });
  const wk = seg(t, 10.55, 10.9);
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, 100 + 900 * wk, 300); ctx.clip();
  text(ctx, 'The fix', 540, 262, { font: '700 76px Oleo', fill: COL.ink, plate: COL.paper, off: [4, 4], align: 'center' });
  ctx.restore();
  const hk = pop(t, 10.7, 0.3);
  if (hk > 0) { ctx.save(); ctx.translate(540, 370); ctx.scale(hk, hk); text(ctx, 'S · T · A · R', 0, 0, { font: '86px Slab', fill: COL.ink, plate: COL.product, off: [5, 4], align: 'center' }); ctx.restore(); }
  if (wk >= 1) reportText('fix', 'The fix', [380, 190, 700, 280]);
  if (hk >= 1) reportText('star', 'S · T · A · R', [250, 300, 830, 390]);
}

// ---------------------------------------------------------------- STEPS 13–37
function stepCam(t) {
  // A step: the finger leads a tilt + push to the Action row, then back
  const a0 = STAMP(2) + 1.0, k = ss(seg(t, a0, a0 + 0.6)) * (1 - ss(seg(t, a0 + 4.4, a0 + 5.2)));
  return { cx: 540, cy: lerp(960, 940, k), z: lerp(1, 1.12, k), r: 0 };
}
function sceneStep(ctx, t, s) {
  const i = s.i, c = stepCam(t);
  bg(ctx, COL.steps[i]);
  ctx.save(); cam(ctx, c);
  polka(ctx, COL.paper, -200, H + 200, 7 + i);
  answerCard(ctx, t, {
    ground: COL.steps[i], cam: c,
    stamped: j => j < i ? 1 : j === i ? pop(t, STAMP(j), 0.24) : 0,
    slotK: () => 1,
    label: j => j < i ? 1 : j === i ? seg(t, STAMP(j) + 0.1, STAMP(j) + 0.35) : 0,
    detail: j => j < i ? 1 : j === i ? seg(t, DETAIL(j), DETAIL(j) + 0.3) : 0,
  });
  // burst sparkles round the fresh medallion
  const [sx, sy] = slot(i), sp = seg(t, STAMP(i), STAMP(i) + 0.5);
  if (sp > 0 && sp < 1) for (let k = 0; k < 5; k++) { const a = k * TAU / 5 + 0.3; sparkle(ctx, sx + Math.cos(a) * (80 + sp * 60), sy + Math.sin(a) * (80 + sp * 60), 22 * (1 - sp), { fill: PAL.white }); }
  if (i === 2) pointHand(ctx, t);
  ctx.restore();
  stepHeader(ctx, t, i, s.t0);
  return { focus: w2s(sx, sy, c) };
}

// ---------------------------------------------------------------- PAYOFF 37–43: four stamps become the star
const RING = { x: 540, y: 900 };
function wedgeAngles() { let a = -Math.PI / 2; return SHARE.map(p => { const a0 = a; a += p / 100 * TAU; return [a0, a]; }); }
function scenePayoff(ctx, t) {
  const s0 = 37.0;
  const c = { cx: RING.x, cy: RING.y + 40, z: lerp(1.22, 1.0, eio(seg(t, s0, s0 + 4.0))), r: lerp(-0.14, 0, eio(seg(t, s0, s0 + 4.0))) };
  bg(ctx, COL.payoff);
  ctx.save(); cam(ctx, c);
  rays(ctx, RING.x, RING.y, 30, 1700, PAL.white, { alpha: 0.08, rot: -t * 0.04 });
  // the answer card drops away under the ring
  const dk = eio(seg(t, s0, s0 + 0.6));
  if (dk < 1) { ctx.save(); ctx.translate(0, dk * 1400); answerCard(ctx, s0, { ground: COL.payoff, stamped: () => 0, slotK: () => 0, label: () => 1, detail: () => 1 }); ctx.restore(); }
  // the big four-point star grows behind the dial
  const sk = back(seg(t, 41.0, 41.6), 1.4);
  if (sk > 0) {
    const pts = []; for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4 - Math.PI / 2 + (1 - sk) * 0.6, r = k % 2 ? 175 : 470; pts.push([RING.x + Math.cos(a) * r * sk, RING.y + Math.sin(a) * r * sk]); }
    shape(ctx, pts, { fill: COL.paper, line: 5, seed: 500, grain: 0.2, breaks: 0.12 });
  }
  // the timing dial: wedges sweep in, one colour per step
  const A = wedgeAngles(), sw = seg(t, 38.8, 40.0);
  const R0 = 150, R1 = 262;
  A.forEach(([a0, a1], i) => {
    const e = a0 + (a1 - a0) * clamp(sw * 4 - i * (SHARE.slice(0, i).reduce((x, y) => x + y, 0) / 100) * 4 / 1);
    const end = Math.min(a1, -Math.PI / 2 + sw * TAU);
    if (end <= a0) return;
    const pts = [...ellipse(RING.x, RING.y, R1, R1, 40, a0, end), ...ellipse(RING.x, RING.y, R0, R0, 40, end, a0)];
    shape(ctx, pts, { fill: COL.steps[i], line: 4.5, seed: 510 + i, grain: 0.3, breaks: 0.06 });
    if (end >= a1 - 1e-3) {
      const m = (a0 + a1) / 2, lx = RING.x + Math.cos(m) * (R0 + R1) / 2, ly = RING.y + Math.sin(m) * (R0 + R1) / 2;
      text(ctx, SHARE[i] + '%', lx, ly + 14, { font: `${i === 1 ? 34 : 40}px Slab`, fill: COL.ink, plate: PAL.white, off: [3, 3], align: 'center' });
      reportText('pct' + i, SHARE[i] + '%', [lx - 40, ly - 24, lx + 40, ly + 18], c);
    }
  });
  // centre disc
  const ck = pop(t, 38.6, 0.3);
  if (ck > 0) {
    ctx.save(); ctx.translate(RING.x, RING.y); ctx.scale(ck, ck);
    shape(ctx, ellipse(0, 0, R0 - 8, R0 - 8, 48), { fill: COL.paper, line: 4, seed: 520, grain: 0.15 });
    text(ctx, '45–60', 0, 6, { font: '64px Slab', fill: COL.ink, align: 'center', plate: COL.product, off: [3, 3] });
    text(ctx, 'SECONDS', 0, 52, { font: '600 26px Jost', fill: COL.ink, align: 'center', track: 5 });
    ctx.restore();
    if (ck >= 1) reportText('secs', '45–60 SECONDS', [RING.x - 110, RING.y - 50, RING.x + 110, RING.y + 60], c);
  }
  // the four medallions: lift off the card, land on the ring, then ride out to the star's points
  A.forEach(([a0, a1], i) => {
    const tl = s0 + 0.5 + i * 0.5, fly = eio(seg(t, tl - 0.5, tl));
    const [sx, sy] = slot(i), m = (a0 + a1) / 2;
    const ring = [RING.x + Math.cos(m) * 340, RING.y + Math.sin(m) * 340];
    const pa = -Math.PI / 2 + i * Math.PI / 2, tip = [RING.x + Math.cos(pa) * 470, RING.y + Math.sin(pa) * 470];
    const go = eio(seg(t, 41.0, 41.6));
    let p = [lerp(sx, ring[0], fly), lerp(sy, ring[1], fly) - Math.sin(fly * Math.PI) * 160];
    p = [lerp(p[0], tip[0], go), lerp(p[1], tip[1], go)];
    medallion(ctx, t, i, p[0], p[1], lerp(62, 70, go), 1);
  });
  if (t > 41.6) for (let k = 0; k < 6; k++) { const a = k * TAU / 6 + t * 0.4, r = 560 + 20 * Math.sin(t * 3 + k); sparkle(ctx, RING.x + Math.cos(a) * r, RING.y + Math.sin(a) * r, 22, { fill: COL.ray }); }
  ctx.restore();
  // header (screen)
  const hk = eo(seg(twos(t), 37.6, 38.0));
  if (hk > 0) { ctx.save(); ctx.translate(-(1 - hk) * 800, 0);
    text(ctx, 'How long?', 540, 290, { font: '700 80px Oleo', fill: COL.paper, plate: COL.ink, off: [4, 4], align: 'center' }); ctx.restore();
    if (hk >= 1) reportText('howlong', 'How long?', [330, 220, 750, 300]); }
}

// ---------------------------------------------------------------- CTA 43–49: the book
function book(ctx, x, y, s, rot) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  const w = 470, h = 640;
  plane(ctx, rrect(-w / 2 + 18, -h / 2 + 18, w, h, 12), shade(COL.cta, 0.35));
  shape(ctx, rrect(-w / 2 - 14, -h / 2 + 6, 30, h - 6, 8), { fill: '#3A3431', line: 4, seed: 600, grain: 0.2 });   // spine edge
  shape(ctx, rrect(-w / 2, -h / 2, w, h, 12), { fill: '#24201E', line: 5, seed: 601, grain: 0.35 });
  REGoff(() => {
    text(ctx, 'A CANDIDATE CO. CAREER PLAYBOOK', 0, -h / 2 + 120, { font: '600 17px Jost', fill: COL.paper, align: 'center', track: 4 });
    ink(ctx, [[-36, -h / 2 + 160], [36, -h / 2 + 160]], 5, { color: COL.product, taper: false, seed: 602 });
    text(ctx, 'GET THE', 0, -h / 2 + 262, { font: '86px Slab', fill: COL.paper, align: 'center', plate: COL.product, off: [4, 4] });
    text(ctx, 'OFFER', 0, -h / 2 + 360, { font: '96px Slab', fill: COL.paper, align: 'center', plate: COL.product, off: [4, 4] });
    ink(ctx, [[-22, -h / 2 + 404], [22, -h / 2 + 404]], 5, { color: COL.product, taper: false, seed: 603 });
    text(ctx, 'The No-BS Guide to Outperforming', 0, -h / 2 + 450, { font: '500 22px Jost', fill: COL.paper, align: 'center' });
    text(ctx, 'Every Other Candidate', 0, -h / 2 + 480, { font: '500 22px Jost', fill: COL.paper, align: 'center' });
    ctx.save(); ctx.font = '500 34px Jost'; const wa = ctx.measureText('Candidate').width, wb = ctx.measureText('Co.').width; ctx.restore();
    text(ctx, 'Candidate', -(wa + wb) / 2, h / 2 - 60, { font: '500 34px Jost', fill: COL.paper });
    text(ctx, 'Co.', -(wa + wb) / 2 + wa, h / 2 - 60, { font: '500 34px Jost', fill: COL.product });
  });
  ctx.restore();
}
function REGoff(fn) { fn(); }
function sceneCta(ctx, t) {
  bg(ctx, COL.cta);
  const bx = 600, by = 680;
  rays(ctx, bx, by, 30, 1600, COL.ray, { alpha: 0.55, rot: 0.02 });
  star(ctx, bx, by, 430 * back(seg(t, 43.5, 43.85), 1.6), { n: 16, inner: 0.84, fill: COL.paper, off: [0, 0], rot: 0.1 });
  floor(ctx, COL.cta, 1330);
  const bk = back(seg(t, 43.3, 43.62), 1.7);
  if (bk > 0) book(ctx, bx, by, bk * 0.95, -0.05);
  if (bk >= 1) reportText('book', 'GET THE OFFER', [bx - 200, by - 260, bx + 200, by + 60]);
  // the candidate, happy, pointing up at the book
  const u = twos(t), pk = ss(seg(u, 44.0, 44.4));
  drawCand(ctx, { x: 190, y: 1330, s: 0.7, view: 'front', face: 'happy', blink: (u > 46.2 && u < 46.3) ? 1 : 0,
    armF: { a1: lerp(1.4, -0.75, pk), a2: lerp(1.52, -0.9, pk) }, handF: pk > 0.5 ? 'point' : 'open' });
  // "Link in bio" ribbon + bouncing arrow
  const rk = pop(t, 44.0, 0.3);
  if (rk > 0) {
    ctx.save(); ctx.translate(650, 1150); ctx.scale(rk, rk);
    shape(ctx, [[-250, -52], [250, -52], [218, 0], [250, 52], [-250, 52], [-218, 0]], { fill: COL.product, line: 4.5, seed: 620, grain: 0.25 });
    text(ctx, 'Link in bio', 0, 22, { font: '700 64px Oleo', fill: COL.paper, plate: COL.ink, off: [4, 3], align: 'center' });
    ctx.restore();
    if (rk >= 1) reportText('bio', 'Link in bio', [400, 1098, 900, 1202]);
  }
}

// ---------------------------------------------------------------- captions (paper slab, bottom, above the Reels UI)
function caption(ctx, t) {
  const cue = cues().find(s => t >= s.t0 && t < s.t1); if (!cue || !cue.burn) return;
  const a = Math.min(ss(seg(t, cue.t0, cue.t0 + 0.16)), 1 - ss(seg(t, cue.t1 - 0.16, cue.t1)));
  const f = fit(ctx, cue.text, '500 {px}px Jost', 40, 820, 2, 30);
  const w = Math.max(...f.lines.map(l => measure(ctx, l, f.font))) + 130, h = 36 + f.lines.length * f.px * 1.22;
  const x = W / 2 - w / 2, y = 1500 - h;
  ctx.save(); ctx.globalAlpha = a; ctx.translate(0, (1 - a) * 10);
  shape(ctx, rrect(x, y, w, h, 16), { fill: COL.paper, line: 3.2, seed: 901, grain: 0.15, breaks: 0.08, off: [5, 5] });
  star(ctx, x + 32, y + h / 2, 14, { n: 8, inner: 0.4, fill: COL.accent, off: [0, 0], rot: t * 0.8 });
  star(ctx, x + w - 32, y + h / 2, 14, { n: 8, inner: 0.4, fill: COL.accent, off: [0, 0], rot: -t * 0.8 });
  f.lines.forEach((l, i) => text(ctx, l, W / 2, y + 18 + f.px * 0.95 + i * f.px * 1.22, { font: f.font, fill: COL.ink, align: 'center' }));
  ctx.restore();
}

// ---------------------------------------------------------------- frame
function drawSection(ctx, t, s) {
  ctx.save(); let r = {};
  if (s.id === 'hook') sceneHook(ctx, t);
  else if (s.id === 'wrong') sceneWrong(ctx, t);
  else if (s.id === 'turn') sceneTurn(ctx, t);
  else if (s.id === 'step') r = sceneStep(ctx, t, s) || {};
  else if (s.id === 'payoff') scenePayoff(ctx, t);
  else sceneCta(ctx, t);
  ctx.restore(); return r;
}
export function renderFilm(ctx, t, Q) {
  setClock(t); TX = [];
  const s = section(t), idx = SEC.indexOf(s), pv = SEC[idx - 1];
  ctx.save();
  if (s.id === 'step' && s.i === 0 && t < s.t0 + 0.45) {
    // iris through the S slot: the empty circle opens into the step's colour
    const k = eio(seg(t, s.t0 + 0.02, s.t0 + 0.45)), [fx, fy] = slot(0);
    drawSection(ctx, Math.min(t, s.t0 - 1e-3), pv);
    const r = lerp(62, 2300, k * k);
    ctx.save(); ctx.beginPath(); ctx.arc(fx, fy, r, 0, TAU); ctx.clip(); TX = []; drawSection(ctx, t, s); ctx.restore();
    ink(ctx, ellipse(fx, fy, r, r, 90), 7, { closed: true, seed: 960 });
  } else if (s.id === 'cta' && t < s.t0 + 0.3) {
    const k = eio(seg(t, s.t0, s.t0 + 0.3)), y = H * (1 - k);
    drawSection(ctx, s.t0 - 1e-3, pv); TX = [];
    ctx.save(); ctx.beginPath(); ctx.rect(0, y, W, H); ctx.clip(); drawSection(ctx, t, s); ctx.restore();
    ink(ctx, [[-10, y], [W + 10, y]], 6, { seed: 963 });
  } else drawSection(ctx, t, s);
  // wipes INTO steps T, A, R happen at the end of the previous step
  const nx = SEC[idx + 1];
  if (nx && nx.id === 'step' && nx.i > 0 && t >= nx.t0 - 0.45) {
    const k = eio(seg(t, nx.t0 - 0.45, nx.t0 - 0.1));
    ctx.save(); ctx.beginPath();
    let line;
    if (nx.i === 1) { const y = H * (1 - k); ctx.rect(0, y, W, H); line = [[-10, y], [W + 10, y]]; }
    else if (nx.i === 2) { const x = W * (1 - k); ctx.rect(x, 0, W, H); line = [[x, -10], [x, H + 10]]; }
    else { const x = W * k; ctx.rect(0, 0, x, H); line = [[x, -10], [x, H + 10]]; }
    ctx.clip(); if (k >= 1) TX = []; drawSection(ctx, t, nx); ctx.restore();
    if (k < 1) ink(ctx, line, 6, { seed: 964 });
  }
  // the stamping hand rides on top of every cut and wipe (steps share one camera at rest)
  STEPS.forEach((_, i) => { if (t > STAMP(i) - 0.8 && t < STAMP(i) + 1.1) stampHand(ctx, t, i); });
  // iris-out on the book at the very end
  if (t > 48.2) {
    const k = eio(seg(t, 48.2, 48.95)), r = lerp(1300, 0, k);
    ctx.save(); ctx.fillStyle = COL.ink; ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.arc(600, 680, Math.max(0.1, r), 0, TAU, true); ctx.fill(); ctx.restore();
    if (r > 1) ink(ctx, ellipse(600, 680, r, r, 90), 6, { closed: true, seed: 965 });
  }
  ctx.restore();
  paperFinish(ctx, W, H, 1);
  if (!(Q && Q.has('nosubs'))) caption(ctx, t);
}
export const texts = () => TX;

// ---------------------------------------------------------------- sound events (same numbers as the picture)
export function events() {
  const E = [], ev = (t, type, o = {}) => E.push({ t: +t.toFixed(4), type, ...o });
  VO.forEach(v => ev(v.t, 'vo', { id: v.id }));
  ev(0.0, 'pen', { dur: 0.5 }); ev(0.25, 'pop', { gain: 1 }); ev(2.6, 'cloth', {}); ev(2.5, 'gulp', {});
  ev(4.0, 'swish', {}); ev(4.35, 'balloon', {}); ev(6.4, 'cloth', {}); ev(6.6, 'swish', {}); ev(8.5, 'stamp', { gain: 1.1 });
  [0, 1, 2, 3].forEach(i => ev(11.0 + i * 0.5, 'pip', { n: i })); ev(10.75, 'pen', { dur: 0.45 });
  ev(13.02, 'iris', { dur: 0.45 });
  STEPS.forEach((_, i) => {
    const ts = STAMP(i);
    if (i > 0) ev(ts - 0.45, 'swish', {});
    ev(ts - 0.8, 'whoosh', { dur: 0.45, gain: 0.6 }); ev(ts, 'stamp', {}); ev(ts + 0.05, 'slide', {});
    ev(ts + 0.6, 'whoosh', { dur: 0.4, gain: 0.4 }); ev(DETAIL(i), 'pen', { dur: 0.7 });
  });
  ev(STAMP(2) + 1.0, 'whistle', {}); ev(STAMP(2) + 1.3, 'tap', {});
  ev(37.0, 'swish', {}); [0, 1, 2, 3].forEach(i => { ev(37.0 + i * 0.5, 'whoosh', { dur: 0.45, gain: 0.5 }); ev(37.5 + i * 0.5, 'stamp', { gain: 0.6 }); });
  ev(38.6, 'pop', {}); ev(38.8, 'pen', { dur: 1.2 }); ev(41.0, 'iris', { dur: 0.6 }); ev(41.6, 'ting', {});
  ev(43.0, 'swish', {}); ev(43.3, 'thump', {}); ev(43.5, 'ting', { gain: 0.6 }); ev(44.0, 'pop', { gain: 0.7 }); ev(48.2, 'iris', { dur: 0.75 });
  E.sort((a, b) => a.t - b.t); return E;
}
