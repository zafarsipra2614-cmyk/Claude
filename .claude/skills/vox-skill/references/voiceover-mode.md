# Voiceover mode — client script + voiceover → paper-cut explainer

The client hands over a **script** and a **recorded voiceover** (MP3/WAV). The
voiceover always comes from the client: never generate one (no TTS, no scratch
voice), and skip any voice stage in the borrowed skills. You
make a long-form (2–10 min), horizontal 1920×1080 paper-cut film timed to their
recording, ending on a YouTube end screen. Nothing is narrated by TTS; the
client's voice is the clock.

Reference build: `brandonomics-99` ("Why do prices end in .99?", 5:20, 37 scenes).

## The standard the client expects

These came from client review and are not optional:

- **No overlapping and no misfitting content.** Text sits inside its card or tag,
  inside the padding, never touching a border; nothing covers text; nothing leaves
  the frame. Enforced by the audit, then checked by eye.
- **No clutter.** Two to four elements per settled frame. One idea per scene.
- **No footers of any kind** (no dark desk band, no pale paper strip across the
  bottom). Use the whole 16:9 frame; put labels next to what they label.
- **Varied transitions with meaning**, never one push for everything (table below).
- **No whoosh on every transition** — it repeats into noise. A soft thud on a
  stamp is fine.
- **End on a YouTube end screen**: two 16:9 video placeholders, left and right,
  channel circle + SUBSCRIBE button in the middle.
- **Apply audio edits to the recording itself** ("remove 'Part two'") and
  re-time from the edited file.
- **Never ship unaudited.** Only `npm run release` produces the deliverable.

## Pipeline

### 1. Scaffold

```bash
bash ~/.claude/skills/vox-skill/scripts/scaffold_vo.sh <project-dir> <voiceover.mp3> [script.txt] [deliverable.mp4]
cd <project-dir> && npm install
```

Fonts render offline only as **system fonts** (Chromium in a sandbox often
cannot reach Google Fonts, and `@remotion/fonts` loading can hang a render):

```bash
pip install -q fonttools brotli
mkdir -p ~/.fonts && for f in public/fonts/*.woff2; do python3 -c "
import sys; from fontTools.ttLib import TTFont
t=TTFont(sys.argv[1]); t.flavor=None; t.save(sys.argv[2])" $f ~/.fonts/$(basename $f .woff2).ttf; done && fc-cache -f
```

Archivo Black stands in for Arial Black where Arial is not installed.

### 2. Edit and transcribe the voiceover

Apply client edits in `vo/edit_vo.sh` (it writes `vo/voiceover_edit.wav`; with no
edits it just converts). Find cut points from an **energy profile**, not from the
transcript — word boundaries around filler phrases are low-confidence:

```bash
ffmpeg -v error -ss 181 -t 3.6 -i vo/voiceover.mp3 -ac 1 -ar 16000 -f s16le - | python3 -c "
import sys,numpy as np
a=np.frombuffer(sys.stdin.buffer.read(),np.int16).astype(float); n=320
for i in range(len(a)//n):
  db=20*np.log10(np.sqrt((a[i*n:(i+1)*n]**2).mean())/32768+1e-9)
  if i%2==0: print(f'{181+i*0.02:7.2f} {db:6.1f} '+'#'*max(0,int((db+60)/2)))"
```

Cut inside digital silence (~-85 dB) with 10 ms fades, leaving a natural pause
(~0.5–0.7 s). Then:

```bash
pip install -q faster-whisper           # model downloads from huggingface.co
printf 'Manoj Thomas\nVicki Morwitz\n' > vo/names.txt   # proper names in the script
python3 vo/transcribe.py vo/voiceover_edit.wav small.en
```

`small.en` on 4 CPUs transcribes 5 minutes in about a minute. Numbers come out
split (`$9` `.99`); cue phrases are matched on normalised tokens, so `"9 99"`.

### 3. Timeline: scenes and cues on words

Copy `timeline.example.json` to `timeline.json`. Each scene names the phrase it
starts on; each cue names the word it lands on (`off` in frames, `word: "end"`
for when a word finishes). Name every stamp cue `<scene>.stamp…` — the audio
build gives each one a thud.

```bash
python3 vo/build_timing.py --check     # scene table; a bad phrase fails loudly with context
python3 vo/build_timing.py             # src/shared/timing.ts + vo/scenes.txt
```

`vo/scenes.txt` lists every scene's words with scene-local frames: author cues
from it. Rules that matter:

- **About one scene per 5–15 s** (≈35 scenes for 5 min). Split long beats; merge
  short ones.
- **A chapter card needs ≥ 3 s.** If the chapter line is followed straight away
  by narration, run the card scene into that narration (card on top, the line's
  visual underneath), as `ch2`/`ch4` did.
- The last scene is the end screen, starting on the sign-off line
  ("Tell me in the comments…"). Set `tail` so it lasts 10–20 s (YouTube: 5–20 s).

### 4. Design and build the scenes

One component per scene in `src/scenes/` (split into act files), registered in
`SCENES` and `ARRIVAL` in `src/scenes/Film.tsx`. Building blocks in
`src/scenes/lib.tsx`:

| Piece | Use |
|---|---|
| `Frame` | every scene: paper, slow camera push, grain, the audit hook |
| `Tag` | hanging price/number tag; `hl` highlights characters, `strikeAt` strikes it, `label` adds a small line above, `tone` paper/red/ink/amber |
| `Card` | torn-paper card with the red offset stroke; children laid out inside its padding |
| `Icon` / `Glyph` | cut-paper icons that rise in / sit inside cards: car, dress, bag, register, drawer, bottle, calculator, bill, pocket, coin, heart, gear, mask, store, folder. Add new ones to `ICONS` in the same flat style |
| `ChapterCard` | numbered chapter card; title may take a `<br />` |
| `Headline`, `Kicker` | centred headline with optional rule; top-left running head |
| `Odometer`, `Tick`, `Stamp`, `Strike`, `Typewriter` | rolling digits, drawn check, rubber stamp, red strike, typed text |
| `EndCard` (`endcard.tsx`) | the YouTube end screen |
| `SnapZoom`, `PullBack`, `Pan`, `RackFocus`, `FocusPulse`, `FocusHunt`, `Handheld` (`camera.tsx`) | camera moves adapted from **papercut-explainer** for 16:9 (see "Camera" below) |
| `ArchivePhoto`, `NewsClipping`, `Halftone` (`archive.tsx`) | the documentary layer: a taped, halftone archival print with caption + credit; a torn newsprint clipping with a highlighted headline; gbro's halftone screen |

**Before writing scenes, load the `remotion-best-practices` skill** (official,
installed in this repo) and follow its routing: `remotion-markup` for animation
and effects, `remotion-maps` for any route or map scene, `remotion-captions` if
captions are asked for.

**Camera** (`camera.tsx`, from papercut-explainer). Wrap a scene's content inside
`<Frame push={0}>` in at most one move, timed on a CUE word; most scenes need none,
and never use moves in consecutive scenes.

| Move | Use it for |
|---|---|
| `SnapZoom` | a number or punchline landing ("demand jumped by **a third**"); keep `to` ≤ 1.2 so the rest of the layout stays in frame |
| `PullBack` | open tight on a detail, ease out to the whole layout (scale, "and that's just one…") |
| `Pan` | a timeline, a lineup or a list laid out wider (`axis="x"`) or taller (`axis="y"`) than the frame; a stop is the world coordinate centred at each hold; `panFrames()` gives its length |
| `RackFocus` | blur the layer behind while a card in front is read |
| `FocusPulse` / `FocusHunt` | emphasis on a reveal without / with a push-in |
| `Handheld` | tense or "on the ground" documentary beats (never settles by itself: content must fit with the drift) |

The moves mark themselves `data-moving` while moving, so the audit judges only the
settled frame; a settled zoom still has to keep everything in frame (it will tell
you if it doesn't).

**Infographic patterns** (from **gbro-collage-info**, rebuilt in this system at
1920×1080 — don't switch to its HyperFrames pipeline). Pick one per data beat:

| gbro pattern | When the script says… | Build it with |
|---|---|---|
| number impact | one striking figure | big `Headline` number or `Tag`, `SnapZoom` on the word, a `stamp`/`coin` foley |
| process | a sequence of steps | 3–4 `Card`s left to right with drawn arrows, entering on each step's word |
| list convergence | many items narrowing to one | a grid of `Tag`s/`Card`s, all but one exit, the survivor scales up |
| comparison flip | "you'd expect A… instead B" | two bars or tags; a dashed ghost "EXPECTED" that the real one overturns |
| result highlight | the takeaway | the result on a `NewsClipping` or `Card` with the amber highlighter and a red marker ring (`data-mark`) |

Use `Halftone` over photo-like or newsprint panels only; flat paper cards stay
flat.

**Archive photos** (from **cinematic-film**). For history and true-story beats
("shop owners in the 1800s"), a real public-domain photograph beats a drawn icon:

```bash
F=../.claude/skills/cinematic-film/scripts     # path to the installed skill from the project
python3 $F/fetch_commons.py search "general store interior 1900" --limit 12   # pick files
# list the picks in photos.json: [{"id": "P01", "kind": "photo", "commons": "File:…"}]
python3 $F/fetch_commons.py get --project .     # downloads; refuses non-free licences
python3 $F/fetch_commons.py credits --project . # writes credits.md
```

Move the files into `public/archive/` and place them with `ArchivePhoto`, its
`credit` taken from `credits.md`. Paste `credits.md` into the video description.
Never use a photo whose licence `get` refused, and never show a real person in a
way their photo was not taken for.

Scene patterns that worked: two tags side by side with a bracket; a balance
scale; a row of three cards (icon + two-line label); a grid of tags; a big shared
price card across consecutive scenes (fade between them); comparison rows with
gauges; a number line with "real" vs "felt" pins; bar charts that grow on the
word; a step chart with a highlighted cliff; a timeline with markers; storefront
rows; two-column "winner" layouts with drawn ticks; a typed comment card.

Layout rules:

- Side margins ≥ 110 px; nothing important below y ≈ 960.
- Sizes: headline 56–100, card title 58–84, labels 22–34 (tracked caps),
  serif body 36–60. Tags 230–660 px wide.
- Every number on screen comes from the script. A chart that shows the shape of
  a finding rather than its data says **ILLUSTRATIVE** in a small footnote.
- No real people's faces: names go on study cards in Playfair.
- Entrances stagger by 5–14 frames and land on their word. Tags drop only 90 px
  (a longer drop passes through other content); tags with `string={false}` pop
  in place.
- Things that leave the stage use `exit` on `Rise`/`Card`/`Tag` before the next
  phase arrives; never let two phases share the space.

### 5. Transitions

Every scene arrives over `T` = 14 frames, and every scene but the last is
lengthened by `T`, so each still starts on its word. Choose the arrival by what
kind of step it is (`ARRIVAL` in `Film.tsx`):

| Kind | Meaning |
|---|---|
| `torn` | into a chapter card or the end screen: a sheet torn across, red marker on the tear |
| `tear` | a twist or reveal: the sheet torn upward |
| `rise` | first scene of a chapter, a new study or section |
| `right` | the next step within a section |
| `left` | going back to something already shown |
| `fade` | the same image continues and builds (identical layout either side) |

Avoid 3D flips: they show black behind the cards (the film already lays paper
under everything) and read as a template, not paper.

### 6. Soundtrack

```bash
python3 ~/.claude/skills/vox-skill/scripts/score.py music/bed.wav --seconds <film_s + 1.5> --key C --bpm 84 --motif 0.8 --pulse 0.6 --bright 0.5 --build 0.1
python3 vo/build_audio.py -14
```

- Keep `--build` low (0.1); the bed's built-in swell otherwise crowds the voice in
  the last third. If `score.py` crashes with a broadcast error, nudge `--seconds`
  by a second.
- `build_audio.py`: voice high-passed and loudnorm'd to -16 LUFS (a real
  recording: no TTS EQ), bed eased ~5 dB across the film and sidechain-ducked,
  swelled ~8 dB once the voice ends (end screen), faded over the last 2.5 s. No
  transition whooshes.
- **Foley from papercut-explainer's library** (79 synthesised sounds, nothing to
  license; names and descriptions in
  `.claude/vendor/papercut-explainer/library/audio/CATALOG.md`). Map cues to sounds
  in `timeline.json`; every `*.stamp*` cue gets `stamp` unless mapped:

  ```json
  "sfx": {"hook.b": "pop", "dresstest.jump": "coin", "register.receipt": "printer", "costume.cost": "rip"}
  ```

  `vo/render_foley.mjs` renders them with papercut's engine in headless Chromium
  (needs `puppeteer-core`, already a devDependency, and a Chromium: `CHROME_PATH`
  or the Playwright one). Good fits: `pop` (a card or tag lands), `stamp`, `coin`
  (money), `printer` (receipts, data), `scribble` (a marker circle), `rip` (a
  strike-out or a torn reveal), `slide` (paper slides), `ding` (a correct answer),
  `chime` (resolution). **Keep it sparse**: 1–3 per scene on the landings that
  matter, never on every entrance or transition — the client rejected repeated
  whooshes. Without the library or a browser it falls back to stamp thuds.
- **Lighter music** for consumer or curiosity topics: set `"bed": "<preset>"` in
  `timeline.json` to a papercut bed (marimba, kalimba, piano; list in
  `library/audio/beds/`) instead of the `score.py` drone. Rendering a bed in the
  browser is slow for long films (about 6–7 min for a 5-minute film, measured), so
  `build_audio.py` caches it and re-renders only when the preset or the film length
  changes; the `score.py` drone stays the
  default for serious or investigative topics.
- Measure music under the voice above 250 Hz across the whole film (speech
  windows vs pauses, using the voice track to tell them apart). Target 17–22 dB in
  each third; adjust `music_db`.

### 7. Audit, look, release

```bash
npm run audit        # qc/fitcheck.mjs
```

The audit renders a settled frame after every cue plus each scene's end
(skipping transition frames) and fails on **CONTAIN** (text past its box's padding
or the frame; text spilling out of its own element), **COVERED** (anything painted
over text, hit-tested along every line) and **OVERLAP** (text on text, box on box).
Tagging:

- containers: `data-fit="name"`; text over a separate card: `data-inside="id"` with
  the card `data-box="id"`;
- intentional overlays that may sit on boxes (stamps, pinned cards): `data-layer="over"`;
- deliberate marks on text (strikes, circles): `data-mark`;
- anything mid-animation is `data-moving` (`Rise`, `Tag`, `Stamp` set it) and skipped;
  mark custom moving elements yourself;
- text clipped on purpose (odometer wheels) is judged only where it shows.

Then **look**. The rules can't see wrong numbers, awkward spacing, things that
merely touch, or motion:

- a contact sheet of every scene's final frame (two sheets of 18 for a 36-scene film);
- one mid-transition still per transition kind;
- one mid-entrance still where things move past each other;
- one still mid-move for every camera move (a zoom's blur, a pan between stops).

Run **papercut-qa's checklist** over the sheets too (the parts that apply to a
16:9 film): does every scene still read as paper (grain, shadows, offset stroke)?
is there one clear focal point per frame? does each number land on its word? is
any element doing nothing? is foley sparse and on landings only?

```bash
npm run release      # run in the background: ~13 min for 5 min of film
```

Audit → render (`--crf=20`, keeps 5 min of 1080p under GitHub's 100 MB hard limit;
it still warns above 50 MB) → poster frame → every audited frame is decoded from
the MP4 and compared with its audited still → only then is the deliverable
replaced.

## Pitfalls already paid for

| Symptom | Cause / fix |
|---|---|
| Render dies partway, only on long films | Node `spawnSync` 1 MB output buffer; `release.mjs` sets `maxBuffer: 1 << 30` |
| Version-mismatch banner, odd failures | a `^` range on a Remotion package; pin every `@remotion/*` to one version |
| Fonts fail / render hangs on `delayRender("Loading font…")` | install fonts as system fonts (step 1); don't load them at render time |
| faster-whisper `metadata_errors` TypeError | PyAV mismatch; `transcribe.py` decodes with ffmpeg instead |
| Odometer shows 89,900 for 79,900 | a wheel may turn only while every wheel to its right rolls 9→0 (fixed in `Odometer`) |
| Text overlapping inside a big number | negative letter-spacing plus a scaled glyph; give the scaled glyph margin |
| Audit sees a box "outside the frame" by 10⁶ px | measuring before layout; the checker waits for the paper image and holds the render |
| Audit flags a strike-through as covering text | tag deliberate marks `data-mark` |
| A label starts off-screen during a slide | fade labels in after the move, at their resting place |
| 3D flip shows black | don't use flips; paper sits under the whole film anyway |
| Chapter card flashes past | under 3 s: merge it with the next line's scene |
| Audit flags letters of one rotated word as overlapping | rotated per-character spans have overlapping bounding boxes; the checker skips sibling spans of one string and hit-tests single characters at their centre |
