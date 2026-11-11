// Parallel parking in 3 moves. Top-down view, right-hand traffic: you drive left-to-right, curb along the bottom.
const CURB = 768, CY = 680, CL = 300, CW = 130;            // curb line, parked-car centre line, car length/width
const BACK = [600, CY], FRONT = [1400, CY];                // the two parked cars (gap 750..1250)
const POS = {                                              // your car: [cx, cy, angle°] (angle = front tilted away from curb)
  start: [1400, 492, 0], m1: [1080, 548, 45], m2: [1030, 598, 45], m3: [950, CY, 0], end: [1000, CY, 0],
};

// local point on a car: s along its length (+ = front), t across (+ = curb side)
function carPt([cx, cy, deg], s, t) {
  const a = deg * Math.PI / 180, ux = Math.cos(a), uy = -Math.sin(a), vx = Math.sin(a), vy = Math.cos(a);
  return [cx + ux * s + vx * t, cy + uy * s + vy * t];
}
function car(p) {
  const q = (s, t) => carPt(p, s, t);
  return poly([q(-CL / 2, -CW / 2), q(CL / 2, -CW / 2), q(CL / 2, CW / 2), q(-CL / 2, CW / 2)], true, 1.5)
    + poly([q(CL * .2, -CW * .36), q(CL * .2, CW * .36)], false, 1)        // windscreen
    + poly([q(-CL * .3, -CW * .32), q(-CL * .3, CW * .32)], false, 1);     // rear window
}
function wheel(x, y, r) {
  const h = r * .24;
  return circ(x, y, r) + circ(x, y, h) + line(x - r, y, x - h, y, 1) + line(x + h, y, x + r, y, 1) + line(x, y + h, x, y + r, 1);
}
function turn(x, y, r, dir) {                              // dir 1 = clockwise (right), -1 = anticlockwise (left)
  const R = r + 34, [a0, a1] = dir > 0 ? [-140, -40] : [-40, -140], b = a1 - dir * 12;
  const pt = a => [x + R * Math.cos(a * Math.PI / 180), y + R * Math.sin(a * Math.PI / 180)];
  return arc(x, y, R, a0, a1) + head(...pt(b), ...pt(a1), 26);
}
function base(A, t = A(0, 0) + .65) {                       // title is drawn by each scene; this adds curb + parked cars
  P(line(70, CURB, 1850, CURB, 2), t, .35, { w: 8 });
  T('curb', 1790, CURB + 50, 44, t + .35, .25, { c: GRAY });
  P(car([...BACK, 0]) + car([...FRONT, 0]), t + .6, .7, { fill: GRAY, fillOp: .18 });
  return t + 1.3;                                          // when the base is finished
}
const WX = 230, WY = 440, WR = 80;                         // steering wheel spot, top-left
function title(s, A) { T(s, 960, 150, 104, A(0, 0), .6); }

window.SCENES = {
  intro(A) {
    const b = T('Parallel Parking', 960, 225, 150, A(0, 0), .8);
    P(wave(b.x + 20, b.x + b.width - 20, 262, 6, 110), A(0, .2), .3, { c: GOLD, w: 9 });
    const t = base(A, A(0, .3) + .35);
    P(car(POS.end), t, .6, { c: BLUE, fill: BLUE, fillOp: .2 });
    [['RIGHT', 560], ['STRAIGHT', 960], ['LEFT', 1360]].forEach(([w, x], i) => {
      const at = A(1, .05 + i * .28);
      P(rect(x - 150, 340, 300, 112, 2), at, .3, { c: [BLUE, GREEN, RED][i], fill: [BLUE, GREEN, RED][i], fillOp: .1 });
      T(w, x, 418, 64, at + .3, .3, { c: [BLUE, GREEN, RED][i] });
      if (i < 2) P(arrow(x + 162, 396, x + 238, 396), at + .6, .2);
    });
  },

  setup(A) {
    title('Set Up', A);
    base(A);
    P(line(762, 830, 1238, 830, 1) + head(1238, 830, 762, 830, 22) + head(762, 830, 1238, 830, 22), A(0, .3), .45, { c: GOLD });
    T('≈ 1.5 car lengths', 1000, 893, 52, A(0, .45), .5, { c: GOLD });
    P(car(POS.start), A(1, .05), .7, { c: BLUE, fill: BLUE, fillOp: .2 });
    const [bx, by] = carPt(POS.start, CL / 2 - 20, CW / 2 - 18);
    P(circ(bx, by, 13), A(1, .3), .25, { c: GOLD, fill: GOLD, fillOp: .8, w: 5 });
    T('signal →', 1590, 470, 46, A(1, .38), .35, { c: GOLD, anchor: 'start' });
    P(line(1585, 562, 1585, 610, 1) + line(1572, 562, 1598, 562, 1) + line(1572, 610, 1598, 610, 1), A(1, .62), .25, { w: 4 });
    T('2–3 ft', 1612, 600, 48, A(1, .7), .3, { anchor: 'start' });
    P(line(1250, 405, 1250, CURB + 5, 1), A(2, .05), .4, { c: RED, w: 4 });
    T('rear bumpers line up', 1232, 390, 50, A(2, .25), .55, { c: RED, anchor: 'end' });
  },

  move1(A) {
    title('Move 1: Full Right', A);
    const t = base(A);
    P(car(POS.start), t, .4, { c: GRAY, w: 3 });
    P(wheel(WX, WY, WR), A(0, .4), .5);
    P(turn(WX, WY, WR, 1), A(0, .55), .35, { c: BLUE });
    T('full right', WX, WY + WR + 80, 56, A(0, .65), .35, { c: BLUE });
    P('M 1400 492 Q 1180 470 1080 548' + head(1180, 470, 1080, 548, 24), A(1, 0), .35, { c: BLUE, w: 4 });
    P(car(POS.m1), A(1, .12), .55, { c: BLUE, fill: BLUE, fillOp: .2 });
    const [rx, ry] = carPt(POS.m1, -CL / 2, 0);             // angle drawn at the rear, against a curb-parallel line
    P(line(rx, ry, rx - 150, ry, 1) + line(rx, ry, rx - 99, ry + 99, 1) + arc(rx, ry, 110, 135, 180, true), A(1, .45), .4, { c: GOLD, w: 4 });
    T('45°', rx - 70, CURB + 62, 56, A(1, .62), .3, { c: GOLD });
  },

  move2(A) {
    title('Move 2: Straight', A);
    const t = base(A);
    P(car(POS.m1), t, .4, { c: GRAY, w: 3 });
    P(wheel(WX, WY, WR), A(0, .3), .5);
    P(line(WX, WY - WR - 18, WX, WY - WR - 70, 1), A(0, .42), .2, { c: GREEN, w: 8 });
    T('straight', WX, WY + WR + 80, 56, A(0, .5), .35, { c: GREEN });
    P(arrow(1030, 442, 924, 548), A(0, .62), .3, { c: GREEN, w: 5 });
    P(car(POS.m2), A(0, .72), .5, { c: BLUE, fill: BLUE, fillOp: .2 });
    P(circ(1250, 614, 26), A(1, .1), .3, { c: RED, w: 5 });
    T('front clears this corner', 1300, 560, 50, A(1, .3), .55, { c: GREEN, anchor: 'start' });
  },

  move3(A) {
    title('Move 3: Full Left', A);
    const t = base(A);
    P(car(POS.m2), t, .4, { c: GRAY, w: 3 });
    P(wheel(WX, WY, WR), A(0, .3), .5);
    P(turn(WX, WY, WR, -1), A(0, .45), .35, { c: RED });
    T('full left', WX, WY + WR + 80, 56, A(0, .55), .35, { c: RED });
    P('M 1030 598 Q 985 668 950 680' + head(985, 668, 950, 680, 24), A(0, .75), .3, { c: RED, w: 4 });
    P(car(POS.m3), A(1, .05), .55, { c: BLUE, fill: BLUE, fillOp: .2 });
    P(icon.tick(800, 850, 30), A(1, .4), .3, { c: GREEN, fill: GREEN, fillOp: .15 });
    T('parallel to the curb', 850, 868, 52, A(1, .5), .45, { c: GREEN, anchor: 'start' });
  },

  finish(A) {
    title('Finish', A);
    const t = base(A);
    P(car(POS.m3), t, .4, { c: GRAY, w: 3 });
    P(arrow(880, 585, 1080, 585), A(0, .3), .3, { c: BLUE, w: 5 });
    T('pull forward', 980, 555, 46, A(0, .4), .35, { c: BLUE });
    P(car(POS.end), A(0, .6), .5, { c: BLUE, fill: BLUE, fillOp: .2 });
    P(line(1000, 836, 1000, 778, 1) + head(1000, 836, 1000, 778, 20), A(1, .05), .25, { c: GOLD, w: 4 });
    T('≈ 1 ft (30 cm) from the curb', 1000, 893, 52, A(1, .2), .55, { c: GOLD });
  },

  remember(A) {
    title('Remember', A);
    const boxes = [];
    [['RIGHT', 520, 1], ['STRAIGHT', 960, 0], ['LEFT', 1400, -1]].forEach(([w, x, d], i) => {
      const c = [BLUE, GREEN, RED][i], at = A(0, .08 + i * .14);
      P(wheel(x, 400, 62), at, .35);
      if (d) P(turn(x, 400, 62, d), at + .35, .2, { c });
      else P(line(x, 320, x, 285, 1), at + .35, .15, { c, w: 8 });
      boxes.push(T(w, x, 580, 80, at + .55, .3, { c }));
    });
    for (let i = 0; i < 2; i++) {
      const a = boxes[i].x + boxes[i].width + 22, b = boxes[i + 1].x - 22;
      P(arrow(a, 555, b, 555), A(0, .5) + i * .17, .15);
    }
    P(icon.tick(640, 760, 34), A(0, .58), .3, { c: GREEN, fill: GREEN, fillOp: .15 });
    T('go slow', 700, 780, 60, A(0, .62), .3, { anchor: 'start' });
    P(icon.tick(1060, 760, 34), A(0, .72), .3, { c: GREEN, fill: GREEN, fillOp: .15 });
    T('check your mirrors', 1120, 780, 60, A(0, .76), .4, { anchor: 'start' });
  },
};
