---
name: ytwb
description: Make Brandonomics hand-drawn whiteboard explainer videos in the locked house style - detailed line-art characters (James and the cast) and objects that sketch, ink and colour themselves, bold black outlines, hatched pencil shadows, Brandonomics blue (#4D96FF) in every scene, Permanent Marker titles and Indie Flower labels, captions, MP4. Use whenever the user wants an explainer video, a whiteboard or "drawn" animation, a short video that explains a concept, or asks to turn a topic, script or article into a video, even if they don't say "whiteboard".
---

# ytwb · Brandonomics whiteboard video

Turn a topic into a whiteboard explainer: every picture sketches itself in pencil, inks itself in bold black line art and colours itself in, text writes itself in a handwritten font, the board slides to the next scene, captions run along the bottom, and the result is a 1920x1080 MP4.

Paths below are relative to this skill's folder. Engine and tools are in `scripts/`, the starter project in `assets/template/`, fonts in `assets/fonts/`, the object library in `assets/library/`, a complete finished video project in `examples/hawthorne-effect/`.

## House style (locked: every video follows all of it)

**Look**
- **Sketch, ink, colour.** Every picture (`IMG`) draws in three stages: a loose pencil sketch of its outline, then the whole picture as black line art, then colour one colour group at a time. The sketch is erased during colouring.
- **Bold black outlines.** Every picture gets a bold black outline around its whole shape. Coloured lines and shapes drawn with `P` (arrows, underlines, bubbles, cards, ticks, warning signs) get a bold black edge too. Both are automatic.
- **Hand-drawn shadows.** Every picture gets a hatched pencil shadow offset down-right, shaded in during colouring. Automatic.
- **No marker, no hand.** The content draws itself (`"pen": false`).
- **Brandonomics blue `#4D96FF` in every scene**: clothes, key words, underlines, ticks, arrows. Black ink for lines, red only for "wrong/warning".
- **Fonts: Permanent Marker for titles, Indie Flower for everything else** (`"titleFont"` / `"font"` in the template). Every board has a title written with `{ font: TITLE_FONT }`. Pictures draw fast (about 1.6-1.8 s for a character, 0.8 s for an object); text is written at handwriting pace (about 0.08-0.1 s per character).

**Characters**
- Detailed hand-drawn people from Open Peeps, built with `scripts/peep.js`, always with `"accent": "#4D96FF"` (clothes blue, head black). Never stick figures.
- **James is the recurring lead**: a 25-year-old Gen Z man, dark volume quiff, clean-shaven, no glasses, blue clothes. Build him only with `"cast":"james"`; only `body` (pose) and `face` (expression) may change, and `peep.js` refuses anything else. Reference: `references/cast-james.png`.
- **Men and women.** Alternate the lead's gender across videos when James is not the lead, and include both when a video has more than one character. Ready-made cast: `james`, `man2`-`man4`, `woman1`-`woman4`.
- **No expressions that show teeth.** `peep.js` refuses them and suggests one without teeth.

**Objects**
- Bold line art in the same style: black strokes 11-16 px on a ~600 px canvas, white and `#4D96FF` fills, grey `#8a8f98` for "off/old". Start from `assets/library/` (eye, bulb-on, bulb-off, factory, chart-up, chart-flat, clipboard, survey, review, magnifier); draw new ones the same way (see `scripts/library_art.py`), with at least 20 px of empty canvas around the art.

**Layout**
- Nothing overlaps; nothing touches the board edges or the caption strip. A deliberate overlap (a red X over a picture, a magnifier over a chart, a "?" in a lens) is marked `{ over: true }`.
- No crossings inside one picture either (a trend line cutting a bar, a label crossing a shape).
- One idea per board, three to six elements.

## Quality gate (before any full render and again before delivery)

1. `node scripts/prep.js <project>` prints no `WARNING` (art cut off at its canvas edge, or ink the marker would never reach).
2. `node scripts/render.js <project> check` prints no `WARN` (overlaps, edges, caption strip, scene without a title in the title font, scene without brand blue, marker on, items running past a scene cut).
3. Look at `previews/sheet.png` (`render.js sheet`): every board finished neatly, nothing crossing inside a picture, James looking like James, no teeth, blue in every scene.
4. After the full render, grab the last frame of every scene from the MP4 and look at them once more.

## Workflow

A video is cheap to re-render and expensive to re-think, so the order is: context, script approval, voice choice, then drawing.

### 0. One-time setup

```bash
node --version              # 18 or newer
python3 --version           # 3.9 or newer
ffmpeg -version             # brew install ffmpeg / apt install ffmpeg
cd scripts && npm install   # puppeteer-core (uses the local Chrome) and the Open Peeps characters
pip install scikit-image    # line-art tracing for IMG
```

Chrome, Chromium or Edge must be installed; set `CHROME_PATH` if it is somewhere unusual. When running as root (containers), the scripts add `--no-sandbox` themselves.

### 1. Gather context

Read `references/interview.md`. Take everything the user already said; ask only for what is missing (use the question tool): topic and the one idea to remember, audience, length, format (16:9 default; 9:16 for Reels/Shorts), language, facts to include or avoid, voice or captions only. Write the answers into `<project>/brief.md`. Research changing facts in two independent sources and list them with links.

### 2. Script, approved before drawing

Read `references/script-writing.md`. Show a table: scene, board title, seconds, caption/voice-over text, what gets drawn (name the characters and library objects). Add the facts and sources and the total duration. About 140 words per minute. Do not draw before approval unless the user asked to go straight to a video.

### 3. Voice

Read `references/voice-options.md`. Options: captions only (no voice), the user's own recordings, OpenAI or ElevenLabs (keys via a credential form or `<project>/.env`, never in chat), or macOS voices on a Mac. For captions only, run `python3 scripts/silent_audio.py <project>`: it writes a silent clip per line sized for reading and sets `voice.json`; give a line `"secs"` in `script.json` when its scene needs more time for drawings.

### 4. Build

```bash
scripts/new_project.sh <project-dir>              # 1920x1080 (or --vertical for 1080x1920)
```

- Characters: `node scripts/peep.js <project>/assets/<name>.svg '{"cast":"james","body":"Paper","face":"Suspicious"}'` (run with no arguments for every body, face and cast member).
- Objects: copy from `assets/library/` into `<project>/assets/`, or draw new ones in the same style.
- `node scripts/prep.js <project>` traces every picture (sketch, line-art, colour, outline and shadow layers).
- `script.json`: one entry per scene, one sentence per line. `scenes.js`: one function per scene; read `references/drawing-api.md` first and copy the patterns in `examples/hawthorne-effect/scenes.js` (a cursor `c` that runs items one after another, `title()`, `write()`, `draw()`).
- Audio and timing: `python3 scripts/make_audio.py <project>` writes `narration.wav` and `timeline.json`.

### 5. Check, preview, render

```bash
node scripts/render.js <project> check     # must print no WARN
node scripts/render.js <project> sheet     # previews/sheet.png: the end of every scene
node scripts/render.js <project> full      # <project>/out/<name>.mp4
```

Then run the quality gate above.

### 6. Deliver

Send the MP4 (and the final-frames still). Say its length, the voice or captions-only, and anything assumed. Offer the cheap changes: a line, a drawing, a font, a pose.

## Reference

- `references/drawing-api.md`: `IMG`, `T`, `P`, path builders, icons, fonts, layout rules.
- `references/font-options.png`: all 21 built-in fonts. `references/cast-james.png`: James.
- `examples/hawthorne-effect/`: a complete 63-second video in the house style (run `prep.js` on it first; its assets are the source SVGs).

Based on [whiteboard-video-skill](https://github.com/Matteoikarieth96/whiteboard-video-skill) by Matteoikarieth96 (MIT, see `LICENSE`). Characters: Open Peeps by Pablo Stanley (CC0). Fonts: see `assets/fonts/` licence files.
