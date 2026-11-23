# Drawing API for scenes.js

`scenes.js` assigns `window.SCENES`, an object with one function per scene id from `script.json`:

```js
window.SCENES = {
  intro(A, { W, H }) {
    const b = T('Big title', W / 2, 400, 150, A(0, 0), .9);
    P(wave(b.x, b.x + b.width, 450), A(0, .5), .3, { c: GOLD, w: 9 });
  },
};
```

## Timing

- `A(line, fraction)` returns the moment `fraction` of the way through spoken line `line` of this scene. `A(0, 0)` is when the first sentence starts; `A(1, .5)` is halfway through the second sentence.
- Every item has a start (`at`) and a duration in seconds. Pictures draw fast and text is written at a readable handwriting pace: about 0.1 s per character for text (a two-word title 1.0 to 1.2, a short phrase 1.2 to 1.5), icons 0.25 to 0.4, an `IMG` character 1.8.
- Items in the same scene should not overlap in time; the marker can only be in one place. Stagger them.
- Everything must finish before the board slides away, about 0.45 s before the scene ends. `render.js check` warns about anything that ends too late.
- Time drawings to the word they illustrate. Listen for the word's position in the sentence and pick the fraction accordingly.

## Drawing items

| Call | Draws |
|---|---|
| `P(d, at, dur, {c, w, fill, fillOp})` | a path, stroked progressively. `c` color, `w` stroke width (default 7), `fill` color that fades in after the stroke, `fillOp` its opacity (default 0.3). Returns the SVG element. |
| `T(text, x, y, size, at, dur, {c, anchor, weight, font})` | handwritten text, revealed left to right. `anchor`: `middle` (default), `start`, `end`. `y` is the baseline. Returns the text's bounding box `{x, y, width, height}`, useful for placing things next to it. |

## Detailed illustrations: `IMG`

`IMG(name, x, y, width, at, dur)` draws a line-art picture (a character, a storefront, a phone) the way a person would: the marker traces the lines first, then colours in solid areas with diagonal strokes, and the finished picture stays on the board. It returns `{x, y, width, height}`.

1. Put the art in `<project>/assets/<name>.svg` (or `.png` / `.jpg`): black line art on white or transparent works best.
2. Run `node scripts/prep.js <project>` once. It traces every new or changed image into `<name>.strokes.json`.
3. Call `IMG('<name>', ...)` in `scenes.js`. Give it about 1.8 s for a character (2.5 s for a busy scene). It draws in three stages, like an illustrator: a light pencil **sketch** of the outline, then the whole picture **inked** as black line art in one continuous pass, then **colour**, one colour group at a time (all the blue, then all the black), with the marker cap taking that colour. The pencil sketch is erased during colouring. The default time split is 15% sketch, 45% ink, 40% colour; change it with a seventh argument, for example `IMG('eye', x, y, w, at, 1.8, { phases: [.1, .5, .4] })`.

Characters: `scripts/peep.js` builds Open Peeps characters (free hand-drawn people, CC0) from a body, face and hair: `node scripts/peep.js <project>/assets/maya.svg '{"body":"PointingUp","face":"SmileBig","hair":"Long"}'`. Keep `hair` the same across scenes so a character stays recognisable. Run it with no arguments to list every body, face, hair and accessory.

## Path builders (return path strings; concatenate with `+`)

| Builder | Shape |
|---|---|
| `line(x1, y1, x2, y2, jitter)` | wobbly straight line |
| `poly([[x,y], ...], closed, jitter)` | polyline or polygon |
| `rect(x, y, w, h, jitter)` | rectangle (top-left corner, width, height) |
| `circ(cx, cy, rx, ry, startDeg, sweepDeg)` | circle or ellipse, slightly overshooting like a real marker |
| `arc(cx, cy, r, fromDeg, toDeg, move)` | arc; pass `move=false` to continue the current path (pie slices) |
| `arrow(x1, y1, x2, y2)` / `head(x1, y1, x2, y2, size)` | arrow, or just an arrowhead pointing at x2,y2 |
| `wave(x1, x2, y, amp, period)` | wavy underline or sound wave |

Ready-made icons: `icon.tick(x,y,r)`, `icon.cross(x,y,r)`, `icon.coin(x,y,r)`, `icon.clock(x,y,r)`, `icon.bubble(x,y,w,h)` (speech bubble), `icon.person(x,y,scale)`, `icon.building(x,y,w)` (columned institution), `icon.bars(x,baseY,[values],barW,gap,maxH)` (bar chart with axes).

A pie slice: `circ(cx, cy, r) ` for the outline, then a second path `` `M ${cx} ${cy} L ${cx} ${cy - r} ` + arc(cx, cy, r, -90, -90 + share * 360, false) + ` L ${cx} ${cy}` `` with a fill.

Topic-specific logos: write a small helper at the top of `scenes.js` that returns path strings (see `eth()` in `examples/rwa-on-ethereum/scenes.js`).

## Colors and board

`INK`, `BLUE`, `GOLD`, `RED`, `GREEN`, `GRAY`; override them in `config.json` under `palette`. `W` and `H` are the board size.

## Layout rules that keep boards readable

- Safe area: stay 60 px from the edges. Keep everything above `H - 150` so the captions never cover a drawing.
- Text sizes on a 1920x1080 board: title 110 to 170, labels 56 to 70, small notes 42 to 50. Below 40 is unreadable on a phone.
- Caveat at size S is roughly 0.45 x S px per character wide. Check long labels against the space you give them; `check` warns when text leaves the board, not when it overlaps a shape.
- Every board gets a title at the top (size 90 to 110, around `y = 150`), drawn at the start of its first line. Without one the viewer loses track of where they are, especially with the sound off. The cover and a pure title card are the only exceptions, because the title is the whole board. Leave room for it: start the rest of the content around `y = 260`.
- Give each scene one focal point. Three to six drawn elements per board is plenty.
- Position with fractions of `W` and `H` if the same project may be rendered vertically.
- Dashed lines are not available (the reveal animation uses the dash pattern). Use a lighter color or thinner stroke instead.
- Do not put text inside a shape without measuring: the `T` return value tells you the width.

## Common fixes

| Symptom in the preview | Fix |
|---|---|
| Text overlaps a drawing | move it, shrink it, or split the label into two `T` calls on two baselines |
| Scene looks empty for seconds while the voice talks | add a drawing timed to that part of the line, or split the line |
| Everything appears at once | stagger `at` values across the line with different fractions |
| Warning "ends after the scene cut" | start earlier, shorten `dur`, or move it to the next scene |
