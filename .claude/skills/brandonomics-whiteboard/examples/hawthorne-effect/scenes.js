// The Hawthorne effect, 60 s, captions only. Detailed line art drawn with the marker (IMG),
// text at handwriting pace, Brandonomics blue (#4D96FF) accents in every scene.
// Each scene runs on a cursor `c`: every item starts when the previous one ends (+ a short breath).
const GAP = .06;
function write(s, x, y, size, at, o = {}) {           // handwriting pace: ~0.082 s per character
  const d = Math.max(.5, s.length * (o.rate || .082));
  return { b: T(s, x, y, size, at, d, o), end: at + d + GAP };
}
function draw(name, x, y, w, at, d, o) { const r = IMG(name, x, y, w, at, d, o); r.end = at + d + GAP; return r; }
function path(dstr, at, d, o) { P(dstr, at, d, o); return at + d + GAP; }
function title(s, A) { return write(s, 960, 150, 96, A(0, 0), { rate: .09, font: TITLE_FONT }).end; }
const warn = (x, y) => poly([[x, y - 34], [x + 32, y + 24], [x - 32, y + 24]], true, 1) + line(x, y - 12, x, y + 6, 1) + circ(x, y + 15, 2.5);

window.SCENES = {
  intro(A) {
    let c = A(0, 0);
    const t = write('The Hawthorne Effect', 960, 215, 110, c, { rate: .08, font: TITLE_FONT }); c = t.end;
    c = path(wave(t.b.x + 20, t.b.x + t.b.width - 20, 252, 6, 110), c, .25, { c: BLUE, w: 10 });
    c = draw('worker-watched', 700, 300, 420, c, 1.6).end;
    c = draw('eye', 1230, 380, 380, c, 1.0).end;
    c = path(line(1225, 515, 1135, 495, 2) + line(1230, 555, 1135, 555, 2), c, .3, { c: GRAY, w: 4, label: 'sight lines' });
    write('watched', 1420, 720, 64, c, { c: BLUE });
  },

  what(A) {
    let c = title('What It Is', A);
    c = draw('worker-relaxed', 330, 360, 330, c, 1.4).end;
    c = path(arrow(760, 600, 1060, 600), c, .27, { w: 8 });
    c = draw('eye', 1500, 270, 220, c, .8).end;
    c = draw('worker-working', 1180, 360, 330, c, 1.4).end;
    c = path(arrow(1640, 800, 1640, 560), c, .25, { c: BLUE, w: 10 });
    write('watched  =  works harder', 960, 905, 58, c, { c: BLUE });
  },

  origin(A) {
    let c = title('Where It Started', A);
    c = draw('factory', 240, 330, 560, c, 1.6).end;
    c = write('Hawthorne Works', 520, 795, 62, c).end;
    c = write('near Chicago · 1920s', 520, 862, 48, c, { c: GRAY }).end;
    c = draw('bulb-on', 1000, 300, 150, c, .8).end;
    c = draw('chart-up', 1180, 290, 230, c, .8).end;
    c = write('brighter ↑', 1450, 410, 56, c, { c: BLUE, anchor: 'start' }).end;
    c = draw('bulb-off', 1000, 570, 150, c, .8).end;
    c = draw('chart-up', 1180, 560, 230, c, .8).end;
    write('still ↑', 1450, 680, 56, c, { c: BLUE, anchor: 'start' });
  },

  explain(A) {
    let c = title('The Explanation', A);
    c = draw('bulb-off', 520, 285, 200, c, .8).end;
    c = path(line(500, 290, 740, 530, 2) + line(740, 290, 500, 530, 2), c, .25, { c: RED, w: 11 });
    c = write('the lights', 620, 610, 58, c, { c: RED }).end;
    c = draw('eye', 1150, 300, 300, c, .8).end;
    c = path(icon.tick(1175, 590, 30), c, .25, { c: BLUE, fill: BLUE, fillOp: .15 });
    c = write('the attention', 1390, 610, 58, c, { c: BLUE }).end;
    c = path(rect(560, 690, 800, 200, 2), c, .4, { c: BLUE, fill: BLUE, fillOp: .06 });
    c = write('“the Hawthorne effect”', 960, 775, 70, c, { c: BLUE }).end;
    write('named by Henry Landsberger · 1958', 960, 850, 48, c, { c: GRAY });
  },

  matters(A) {
    let c = title('Why It Matters', A);
    c = draw('clipboard', 390, 330, 180, c, .8).end;
    c = write('studies', 480, 690, 60, c).end;
    c = draw('survey', 870, 330, 180, c, .8).end;
    c = write('surveys', 960, 690, 60, c).end;
    c = draw('review', 1310, 350, 260, c, .8).end;
    c = write('reviews', 1440, 690, 60, c).end;
    path(warn(600, 292) + warn(1080, 292) + warn(1590, 292), c, .4, { c: RED, fill: GOLD, fillOp: .25, label: 'warning signs' });
  },

  catch(A) {
    let c = title('The Catch', A);
    c = draw('chart-flat', 200, 360, 400, c, .8).end;
    c = draw('magnifier', 400, 290, 260, c, .7, { over: true }).end;   // deliberately over the chart
    c = write('?', 505, 452, 120, c, { c: RED, rate: .25, over: true }).end;   // inside the lens
    write('2011 re-analysis', 420, 800, 56, c);
    c = A(1, 0);
    c = path(icon.bubble(1320, 420, 480, 200), c, .4, { c: BLUE, w: 8, fill: BLUE, fillOp: .1 });
    c = write('LEGEND', 1320, 455, 100, c, { c: BLUE }).end;
    c = path(icon.bubble(1320, 720, 230, 90), c, .3, { c: GRAY, w: 6 });
    write('reality', 1320, 738, 54, c, { c: GRAY });
  },

  takeaway(A) {
    let c = title('Takeaway', A);
    c = draw('eye', 430, 330, 320, c, 1.0).end;
    c = path(line(760, 440, 1030, 405, 2) + line(760, 480, 1030, 515, 2), c, .3, { c: GRAY, w: 4, label: 'sight lines' });
    c = draw('worker-point', 1050, 290, 360, c, 1.6).end;
    const t = write('watching changes what you see', 960, 860, 72, c);
    path(wave(t.b.x + 20, t.b.x + t.b.width - 20, 902, 5, 110), t.end, .3, { c: BLUE, w: 9 });
  },
};
