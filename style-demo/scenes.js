// Style demo: detailed characters drawn in one continuous pass with the marker.
window.SCENES = {
  meet(A) {
    const t = A(0, 0);
    const b = T('Meet Maya', 560, 520, 150, t, .6);
    P(wave(b.x + 10, b.x + b.width - 10, 560, 6, 110), t + .62, .2, { c: GOLD, w: 9 });
    IMG('worried', 1130, 150, 560, t + .9, 1.8);
    T('her shop is struggling', 560, 680, 66, t + 2.8, .55, { c: GRAY });
    P(arrow(820, 610, 860, 700), t + 3.4, .2, { c: RED, w: 7 });
  },
  idea(A) {
    const t = A(0, 0);
    IMG('happy', 1130, 150, 560, t, 1.8);
    T('a simple fix!', 560, 520, 130, t + 1.9, .55, { c: GREEN });
    P(icon.tick(560, 660, 50), t + 2.5, .25, { c: GREEN, fill: GREEN, fillOp: .15 });
  },
};
