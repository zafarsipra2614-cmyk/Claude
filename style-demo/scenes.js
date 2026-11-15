// Style demo: pictures drawn fast and naturally, text written at a readable handwriting pace.
window.SCENES = {
  meet(A) {
    const t = A(0, 0);
    const b = T('Meet Maya', 560, 520, 150, t, 1.2);
    P(wave(b.x + 10, b.x + b.width - 10, 560, 6, 110), t + 1.22, .3, { c: GOLD, w: 9 });
    IMG('worried', 1130, 150, 560, t + 1.6, 1.8);
    T('her shop is struggling', 560, 680, 66, t + 3.5, 1.4, { c: GRAY });
    P(arrow(820, 610, 860, 700), t + 5.0, .25, { c: RED, w: 7 });
  },
  idea(A) {
    const t = A(0, 0);
    IMG('happy', 1130, 150, 560, t, 1.8);
    T('a simple fix!', 560, 520, 130, t + 1.9, 1.1, { c: GREEN });
    P(icon.tick(560, 660, 50), t + 3.05, .25, { c: GREEN, fill: GREEN, fillOp: .15 });
  },
};
