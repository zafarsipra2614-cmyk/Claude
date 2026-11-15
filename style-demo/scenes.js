// Style demo: detailed characters drawn stroke by stroke with the marker.
window.SCENES = {
  meet(A) {
    const t = A(0, 0);
    const b = T('Meet Maya', 560, 520, 150, t, .9);
    P(wave(b.x + 10, b.x + b.width - 10, 560, 6, 110), t + .95, .3, { c: GOLD, w: 9 });
    IMG('worried', 1130, 150, 560, t + 1.35, 3.2);
    T('her shop is struggling', 560, 680, 66, t + 4.65, .8, { c: GRAY });
    P(arrow(560 + 260, 610, 560 + 300, 700), t + 5.5, .25, { c: RED, w: 7 });
  },
  idea(A) {
    const t = A(0, 0);
    IMG('happy', 1130, 150, 560, t, 3.0);
    const b = T('a simple fix!', 560, 520, 130, t + 3.1, .8, { c: GREEN });
    P(icon.tick(560, 660, 50), t + 3.95, .3, { c: GREEN, fill: GREEN, fillOp: .15 });
  },
};
