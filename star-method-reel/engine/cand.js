// The candidate: a geometric 1950s-style graduate in a turquoise blazer, built on the style's rig
// (held body, moving arms/hands/eyes/mouth). Feet at (0,0); hair top ≈ -580. Angles: 0 = right, π/2 = down.
import { PAL, shape, ink, ellipse, spline, xform, move, rrect, rect, TAU, reg, path } from './toon.js';
import { drawHand } from './chars_base.js';

export const CC = {
  jacket: '#2F2D33', jacketD: '#1F1D22', lapel: '#6A6570', shirt: '#FBF6EA', tie: '#C8372D', tieD: '#9A2620',
  trousers: '#2F2D33', trousersD: '#1F1D22', hair: '#2E211C', skin: '#E9B98E', shoe: '#141214',
};
const UA = 100, FA = 92;
export function armJoints(pose, which) {
  const view = pose.view || 'q';
  const sh = view === 'front' ? [which === 'F' ? 50 : -50, -384] : (which === 'F' ? [42, -384] : [-38, -386]);
  const rest = view === 'front' ? (which === 'F' ? { a1: 1.4, a2: 1.52 } : { a1: 1.74, a2: 1.62 }) : (which === 'F' ? { a1: 1.3, a2: 1.52 } : { a1: 1.86, a2: 1.7 });
  const arm = pose[which === 'F' ? 'armF' : 'armB'] || rest;
  const el = [sh[0] + Math.cos(arm.a1) * UA, sh[1] + Math.sin(arm.a1) * UA];
  const ha = [el[0] + Math.cos(arm.a2) * FA, el[1] + Math.sin(arm.a2) * FA];
  return { sh, el, ha, a2: arm.a2 };
}
export function toScreen(pose, p) { const s = pose.s ?? 1, d = pose.dir ?? 1; return [pose.x + p[0] * s * d, pose.y + p[1] * s]; }

function sleeve(ctx, J, seed) {
  const P = spline([J.sh, [(J.sh[0] + J.el[0]) / 2, (J.sh[1] + J.el[1]) / 2], J.el, [(J.el[0] + J.ha[0]) / 2, (J.el[1] + J.ha[1]) / 2], J.ha], false, 6);
  ink(ctx, P, 28, { seed, taper: false, wob: 0.08 });
  const o = reg(seed, 1);
  ink(ctx, move(P, o[0] * 0.6, o[1] * 0.6), 19, { seed: seed + 1, taper: false, wob: 0.05, color: CC.jacket });
  // white shirt cuff
  const a = J.a2, cx = J.ha[0] - Math.cos(a) * 6, cy = J.ha[1] - Math.sin(a) * 6;
  ink(ctx, [[cx + Math.cos(a + 1.57) * 11, cy + Math.sin(a + 1.57) * 11], [cx - Math.cos(a + 1.57) * 11, cy - Math.sin(a + 1.57) * 11]], 6, { seed: seed + 2, taper: false, color: CC.shirt });
}
function drawArm(ctx, pose, which, seed) {
  const J = armJoints(pose, which);
  const prop = pose.prop && (pose.prop.hand || 'F') === which ? pose.prop : null;
  if (prop && prop.behind) prop.draw(ctx, J);
  sleeve(ctx, J, seed);
  const hk = pose[which === 'F' ? 'handF' : 'handB'] || 'open';
  drawHand(ctx, J.ha[0], J.ha[1], J.a2, hk, which === 'F' ? -1 : 1, 1, CC.skin);
  if (prop && !prop.behind) prop.draw(ctx, J);
  return J;
}

// pose: { x, y, s, dir, view:'q'|'front', face:'neutral'|'happy'|'wow'|'worried'|'focus', talk 0..1, blink, look:[dx,dy],
//         armF/armB:{a1,a2}, handF/handB, prop:{hand, behind, draw(ctx, J)} }
export function drawCand(ctx, pose) {
  const view = pose.view || 'q', front = view === 'front';
  ctx.save(); ctx.translate(pose.x, pose.y); ctx.scale((pose.s ?? 1) * (pose.dir ?? 1), pose.s ?? 1);
  if (pose.shadow !== false) { ctx.save(); ctx.globalAlpha = 0.16; ctx.fillStyle = PAL.ink; ctx.beginPath(); ctx.ellipse(6, 2, 92, 11, 0, 0, TAU); ctx.fill(); ctx.restore(); }
  drawArm(ctx, pose, 'B', 70);
  // straight-leg trousers + shoes
  const legs = front ? [[[-46, -290], [-2, -290], [-8, -24], [-38, -24]], [[2, -290], [46, -290], [38, -24], [8, -24]]]
    : [[[-42, -290], [4, -290], [-4, -24], [-34, -24]], [[-2, -290], [46, -290], [36, -24], [8, -24]]];
  legs.forEach((L, i) => {
    const ax = (L[2][0] + L[3][0]) / 2;
    shape(ctx, L, { fill: CC.trousers, line: 3.8, seed: 42 + i, grain: 0.3, breaks: 0.15,
      shade: i === 1 && !front ? [{ pts: [[24, -292], [60, -292], [60, 0], [20, 0]], color: CC.trousersD, alpha: 0.7 }] : null });
    const sh = front ? ellipse(ax, -9, 21, 10, 16) : spline([[ax - 18, -16], [ax + 6, -20], [ax + 34, -8], [ax + 30, 0], [ax - 18, 0]], true, 4);
    shape(ctx, sh, { fill: CC.shoe, line: 0, off: [0, 0], grain: 0 });
  });
  // blazer: boxy trapezoid, hem below the hips; white shirt V with a mustard tie; lapel lines
  const torso = spline([[-56, -382], [-44, -402], [44, -402], [56, -382], [54, -300], [58, -258], [-58, -258], [-54, -300]], true, 6);
  shape(ctx, torso, { fill: CC.jacket, line: 4.2, seed: 50, grain: 0.35, breaks: 0.2,
    shade: front ? null : [{ pts: [[24, -404], [72, -404], [72, -250], [28, -250]], color: CC.jacketD, alpha: 0.55 }] });
  const vx = front ? 0 : 12;
  shape(ctx, [[vx - 24, -400], [vx + 24, -400], [vx, -322]], { fill: CC.shirt, line: 3, seed: 54, grain: 0.1, breaks: 0.2 });
  shape(ctx, [[vx - 7, -394], [vx + 7, -394], [vx + 9, -346], [vx, -330], [vx - 9, -346]], { fill: CC.tie, line: 2.6, seed: 55, grain: 0.15, breaks: 0.1 });
  ink(ctx, [[vx - 30, -398], [vx - 4, -318], [vx - 8, -262]], 3, { seed: 56, taper: true, breaks: 0.2, color: CC.lapel });
  ink(ctx, [[vx + 30, -398], [vx + 4, -318]], 3, { seed: 57, taper: true, breaks: 0.2, color: CC.lapel });
  [[-292], [-276]].forEach(([y], i) => shape(ctx, ellipse(vx - 14, y, 4, 4, 8), { fill: CC.lapel, line: 0, off: [0, 0], grain: 0, seed: 58 + i }));
  // neck
  shape(ctx, rect(-13, -424, 26, 26), { fill: CC.skin, line: 0, seed: 52, grain: 0 });
  drawHead(ctx, pose, view);
  drawArm(ctx, pose, 'F', 60);
  ctx.restore();
}

function drawHead(ctx, pose, view) {
  const face = pose.face || 'neutral', blink = pose.blink ?? 0, look = pose.look || [0, 0], talk = pose.talk ?? 0;
  if (view === 'front') {
    shape(ctx, ellipse(-58, -472, 11, 16, 12), { fill: CC.skin, line: 3.4, seed: 71, grain: 0 });
    shape(ctx, ellipse(58, -472, 11, 16, 12), { fill: CC.skin, line: 3.4, seed: 72, grain: 0 });
    shape(ctx, spline([[-56, -500], [-50, -540], [0, -556], [50, -540], [56, -500], [50, -440], [24, -414], [-24, -414], [-50, -440]], true, 6), { fill: CC.skin, line: 4, seed: 61, grain: 0.15, breaks: 0.25 });
    // short crop with a quiff
    shape(ctx, spline([[-60, -500], [-62, -540], [-30, -572], [10, -584], [40, -592], [52, -572], [64, -536], [60, -500], [50, -522], [20, -538], [-14, -530], [-46, -518]], true, 6), { fill: CC.hair, line: 0, seed: 62, grain: 0.3 });
    [-21, 21].forEach((x, i) => eye(ctx, x + look[0], -486 + look[1], face, blink, i));
    ink(ctx, spline([[2, -484], [-7, -460], [5, -457]], false, 4), 3.4, { seed: 64 });
    mouth(ctx, 0, -438, face, talk);
    cheeks(ctx, [[-34, -458], [34, -458]]);
    return;
  }
  // 3/4 (facing +x): one outline round the skull out to the nose tip
  shape(ctx, ellipse(-34, -472, 11, 16, 12), { fill: CC.skin, line: 3.4, seed: 73, grain: 0 });
  const chain = [[52, -488], [50, -514], [34, -540], [-6, -554], [-44, -538], [-60, -498], [-56, -456], [-38, -426], [-8, -412], [22, -414], [38, -426], [44, -444], [52, -460]];
  const head = [...spline(chain, false, 6), [86, -472]];
  shape(ctx, head, { fill: CC.skin, line: 4, seed: 66, grain: 0.15, breaks: 0.12 });
  // ear again on top of the outline for readability, then the crop + quiff sweeping forward
  ink(ctx, ellipse(-34, -472, 8, 12, 12, 0.4, TAU - 0.6), 2.6, { seed: 74 });
  shape(ctx, spline([[-62, -498], [-64, -540], [-34, -568], [8, -580], [44, -590], [62, -566], [56, -530], [36, -540], [6, -534], [-22, -524], [-40, -500], [-50, -478]], true, 6), { fill: CC.hair, line: 0, seed: 68, grain: 0.3 });
  [[6, -492], [38, -495]].forEach(([x, y], i) => eye(ctx, x + look[0], y + look[1], face, blink, i, i === 1 ? 0.78 : 1));
  mouth(ctx, 28, -434, face, talk);
  cheeks(ctx, [[-12, -460]]);
}
function eye(ctx, x, y, face, blink, i, sx = 1) {
  if (face === 'happy' || blink > 0.5) {
    const up = face === 'happy';
    ink(ctx, up ? [[x - 8 * sx, y + 3], [x, y - 5], [x + 8 * sx, y + 3]] : [[x - 8 * sx, y], [x + 8 * sx, y]], 4, { seed: 80 + i, taper: false });
  } else {
    const r = face === 'wow' ? 8.5 : 6.8;
    shape(ctx, ellipse(x, y, r * 0.8 * sx, r * 1.3, 14), { fill: PAL.ink, line: 0, grain: 0, off: [0, 0] });
    shape(ctx, ellipse(x + 1.5, y - 3.5, 2.2, 2.6, 8), { fill: PAL.white, line: 0, grain: 0, off: [0, 0] });
  }
  // brows: worried = inner ends up, focus = inner ends down
  const by = face === 'wow' ? y - 26 : y - 19;
  const tilt = face === 'worried' ? (i ? 4 : -4) : face === 'focus' ? (i ? -3 : 3) : 0;
  ink(ctx, [[x - 9 * sx, by - tilt], [x + 9 * sx, by + tilt - 1]], 3.6, { seed: 90 + i, taper: true });
}
function mouth(ctx, x, y, face, talk) {
  if (talk > 0.15) { shape(ctx, ellipse(x - 1, y + 2, 9, 3 + talk * 9, 16), { fill: '#8E3B2A', line: 3, seed: 96, grain: 0, breaks: 0 }); return; }
  if (face === 'happy') shape(ctx, spline([[x - 16, y - 6], [x + 12, y - 8], [x + 4, y + 11], [x - 10, y + 9]], true, 6), { fill: '#8E3B2A', line: 3.2, seed: 95, grain: 0, breaks: 0 });
  else if (face === 'wow') shape(ctx, ellipse(x - 2, y + 2, 7, 10, 16), { fill: '#8E3B2A', line: 3.2, seed: 96, grain: 0, breaks: 0 });
  else if (face === 'worried') ink(ctx, spline([[x - 12, y + 4], [x - 1, y - 2], [x + 10, y + 4]], false, 5), 3.4, { seed: 97 });
  else ink(ctx, spline([[x - 12, y - 2], [x - 1, y + 4], [x + 9, y - 3]], false, 5), 3.4, { seed: 100 });
}
function cheeks(ctx, pts) { pts.forEach(([x, y], i) => shape(ctx, ellipse(x, y, 11, 7.5, 14), { fill: PAL.pink, line: 0, grain: 0, seed: 101 + i, alpha: 0.8 })); }
