// The Hawthorne effect, 60 s, captions only.
function eye(x, y, w) {
  const h = w * .32;
  return `M ${x - w / 2} ${y} Q ${x} ${y - h * 1.6} ${x + w / 2} ${y} Q ${x} ${y + h * 1.6} ${x - w / 2} ${y} ` + circ(x, y, h * .62);
}
const pupil = (x, y, w) => circ(x, y, w * .32 * .28);
function bulb(x, y, r, rays) {
  let d = circ(x, y, r) + rect(x - r * .42, y + r * .88, r * .84, r * .45, 1) + line(x - r * .3, y + r * 1.5, x + r * .3, y + r * 1.5, 1);
  if (rays) for (let a = -160; a <= -20; a += 35) {
    const c = Math.cos(a * Math.PI / 180), s = Math.sin(a * Math.PI / 180);
    d += line(x + c * r * 1.3, y + s * r * 1.3, x + c * r * 1.75, y + s * r * 1.75, 1);
  }
  return d;
}
function factory(x, y) {                                    // x = centre, y = ground
  let roof = [[x - 200, y - 120]];
  for (let i = 0; i < 4; i++) roof.push([x - 200 + i * 100, y - 190], [x - 100 + i * 100, y - 120]);
  let win = '';
  for (let i = 0; i < 4; i++) win += rect(x - 170 + i * 95, y - 85, 50, 40, 1);
  return rect(x - 200, y - 120, 400, 120, 2) + poly(roof, false, 1.5) + rect(x + 120, y - 280, 45, 120, 1) + win;
}
function clipboard(x, y) {
  let d = rect(x - 75, y - 95, 150, 190, 2) + rect(x - 30, y - 112, 60, 30, 1);
  for (let i = 0; i < 4; i++) d += line(x - 45, y - 35 + i * 35, x + (i === 3 ? 10 : 45), y - 35 + i * 35, 1);
  return d;
}
function form(x, y) {
  let d = rect(x - 75, y - 95, 150, 190, 2);
  for (let i = 0; i < 3; i++) d += rect(x - 50, y - 65 + i * 55, 28, 28, 1) + line(x - 5, y - 50 + i * 55, x + 50, y - 50 + i * 55, 1);
  return d + poly([[x - 46, y - 52], [x - 37, y - 42], [x - 20, y - 66]], false, 1);
}
function star(cx, cy, r) {
  const p = [];
  for (let i = 0; i < 10; i++) { const a = (-90 + i * 36) * Math.PI / 180, rr = i % 2 ? r * .45 : r; p.push([cx + rr * Math.cos(a), cy + rr * Math.sin(a)]); }
  return poly(p, true, 1);
}
function bars(x, y, vals, bw, gap, hmax, at, c, axisAt) {   // axis unfilled, bars filled
  P(poly([[x, y - hmax - 30], [x, y], [x + vals.length * (bw + gap) + gap, y]], false, 1), at, .2, { c });
  const m = Math.max(...vals);
  P(vals.map((v, i) => rect(x + gap + i * (bw + gap), y - v / m * hmax, bw, v / m * hmax, 1.5)).join(''), at + .2, .3, { c, fill: c, fillOp: .2 });
}
const warn = (x, y) => poly([[x, y - 34], [x + 32, y + 24], [x - 32, y + 24]], true, 1) + line(x, y - 12, x, y + 6, 1) + circ(x, y + 15, 2.5);
function title(s, A) { T(s, 960, 150, 104, A(0, 0), .6); }

window.SCENES = {
  intro(A) {
    const b = T('The Hawthorne Effect', 960, 215, 140, A(0, 0), .9);
    P(wave(b.x + 20, b.x + b.width - 20, 252, 6, 110), A(0, .25), .3, { c: GOLD, w: 9 });
    P(icon.person(820, 650, 1.2), A(0, .4), .5);
    P(line(880, 700, 1140, 700, 1) + line(900, 700, 900, 800, 1) + line(1120, 700, 1120, 800, 1) + rect(930, 640, 120, 60, 1), A(0, .55), .4);
    P(eye(1480, 440, 280), A(0, .72), .5, { c: BLUE, fill: BLUE, fillOp: .08 });
    P(pupil(1480, 440, 280), A(0, .85), .15, { c: BLUE, fill: BLUE, fillOp: 1 });
    P(line(1340, 470, 880, 560, 2) + line(1350, 500, 1050, 640, 2), A(1, .05), .35, { c: GRAY, w: 3 });
    P(icon.tick(1480, 680, 40), A(1, .45), .3, { c: GOLD, fill: GOLD, fillOp: .15 });
    T('watched', 1545, 700, 56, A(1, .55), .3, { c: GOLD, anchor: 'start' });
  },

  what(A) {
    title('What It Is', A);
    P(eye(520, 330, 200), A(0, .1), .35, { c: BLUE, fill: BLUE, fillOp: .08 });
    P(pupil(520, 330, 200), A(0, .17), .1, { c: BLUE, fill: BLUE, fillOp: 1 });
    P(icon.person(520, 640, 1.1), A(0, .22), .45);
    P(arrow(760, 600, 1080, 600), A(0, .38), .25);
    P(icon.person(1340, 640, 1.1), A(0, .46), .45);
    P(circ(1405, 545, 7) + circ(1420, 575, 6) + circ(1270, 555, 6), A(0, .58), .15, { c: BLUE, fill: BLUE, fillOp: .6, w: 3 });
    P(arrow(1500, 760, 1500, 520), A(0, .62), .25, { c: GREEN, w: 8 });
    T('observed  →  acts differently', 960, 890, 60, A(0, .7), .55, { c: BLUE });
  },

  origin(A) {
    title('Where It Started', A);
    P(factory(520, 620), A(0, .1), .8);
    P(wave(640, 700, 310, 10, 40), A(0, .3), .2, { c: GRAY, w: 4 });
    T('Hawthorne Works', 520, 700, 60, A(0, .45), .5);
    T('near Chicago · 1920s', 520, 770, 48, A(0, .62), .5, { c: GRAY });
    P(bulb(1060, 410, 52, true), A(1, 0), .45, { c: GOLD, fill: GOLD, fillOp: .35 });
    T('brighter', 1060, 545, 44, A(1, .1), .3, { c: GOLD });
    bars(1180, 520, [2, 3, 4], 50, 20, 170, A(1, .17), GREEN);
    T('output ↑', 1440, 450, 56, A(1, .3), .3, { c: GREEN, anchor: 'start' });
    P(bulb(1060, 690, 52, false), A(1, .5), .4, { c: GRAY, fill: GRAY, fillOp: .15 });
    T('dimmer', 1060, 825, 44, A(1, .6), .25, { c: GRAY });
    bars(1180, 800, [2, 3, 4], 50, 20, 170, A(1, .66), GREEN);
    T('still ↑', 1440, 730, 56, A(1, .8), .3, { c: GREEN, anchor: 'start' });
  },

  explain(A) {
    title('The Explanation', A);
    P(bulb(620, 400, 70, true), A(0, .1), .45, { c: GRAY });
    P(line(530, 300, 710, 520, 2) + line(710, 300, 530, 520, 2), A(0, .3), .25, { c: RED, w: 9 });
    T('the lights', 620, 600, 56, A(0, .4), .3, { c: RED });
    P(eye(1300, 410, 280), A(0, .55), .4, { c: BLUE, fill: BLUE, fillOp: .08 });
    P(pupil(1300, 410, 280), A(0, .65), .1, { c: BLUE, fill: BLUE, fillOp: 1 });
    P(icon.tick(1150, 582, 30), A(0, .72), .25, { c: GREEN, fill: GREEN, fillOp: .15 });
    T('the attention', 1330, 600, 56, A(0, .78), .35, { c: GREEN });
    P(rect(560, 690, 800, 200, 2), A(1, .05), .4, { c: BLUE, fill: BLUE, fillOp: .06 });
    T('“the Hawthorne effect”', 960, 775, 70, A(1, .25), .5, { c: BLUE });
    T('named by Henry Landsberger · 1958', 960, 850, 48, A(1, .55), .5, { c: GRAY });
  },

  matters(A) {
    title('Why It Matters', A);
    [[clipboard, 480, 'studies'], [form, 960, 'surveys'], [null, 1440, 'reviews']].forEach(([fn, x, lab], i) => {
      const at = A(0, .08 + i * .2);
      if (fn) P(fn(x, 480), at, .4);
      else P(rect(x - 75, 385, 150, 190, 2) + star(x - 38, 450, 24) + star(x + 2, 450, 24) + star(x + 42, 450, 24) + line(x - 45, 520, x + 45, 520, 1), at, .4, { c: INK, fill: GOLD, fillOp: .15 });
      T(lab, x, 680, 60, at + .4, .25);
    });
    P(warn(575, 380) + warn(1055, 380) + warn(1535, 380), A(0, .72), .4, { c: RED, fill: GOLD, fillOp: .25 });
  },

  catch(A) {
    title('The Catch', A);
    bars(330, 700, [3, 3.2, 2.9, 3.1], 60, 25, 250, A(0, .05), GRAY);
    P(circ(560, 470, 110) + line(640, 550, 730, 640, 1), A(0, .25), .45, { w: 9 });
    T('?', 560, 510, 130, A(0, .4), .25, { c: RED });
    T('2011 re-analysis', 520, 800, 54, A(0, .55), .45);
    P(icon.bubble(1320, 420, 480, 200), A(1, .05), .45, { c: GOLD, fill: GOLD, fillOp: .12 });
    T('LEGEND', 1320, 450, 100, A(1, .2), .4, { c: GOLD });
    P(icon.bubble(1320, 720, 230, 90), A(1, .5), .3, { c: BLUE, fill: BLUE, fillOp: .12 });
    T('reality', 1320, 738, 54, A(1, .62), .3, { c: BLUE });
  },

  takeaway(A) {
    title('Takeaway', A);
    P(eye(700, 460, 320), A(0, .1), .45, { c: BLUE, fill: BLUE, fillOp: .08 });
    P(pupil(700, 460, 320), A(0, .2), .1, { c: BLUE, fill: BLUE, fillOp: 1 });
    P(line(870, 470, 1150, 500, 2) + line(870, 500, 1150, 560, 2), A(0, .25), .25, { c: GRAY, w: 3 });
    P(icon.person(1230, 600, 1.1), A(0, .32), .45);
    const t = T('watching changes what you see', 960, 850, 76, A(0, .5), .7);
    P(wave(t.x + 20, t.x + t.width - 20, 880, 5, 110), A(0, .78), .3, { c: GOLD, w: 8 });
  },
};
