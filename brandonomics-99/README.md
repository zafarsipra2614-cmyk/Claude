# Why do prices end in .99? — paper-cut explainer

`why_prices_end_in_99.mp4` · 5:20 · 1920×1080 · built with the `vox-skill` (Remotion)
on the client's own voiceover.

## Voiceover

- `vo/voiceover.mp3` — as supplied.
- `vo/edit_vo.sh` — client edit: removes "Part two." before "Chapter three"
  (182.20–182.86 s, cut inside silence with 10 ms fades) → `vo/voiceover_edit.wav`.
- `vo/transcribe.py` — word-level timestamps (faster-whisper `small.en`) → `vo/words.json`.

## Timing

`timeline.json` names the phrase each scene starts on and the word every cue lands
on; `vo/build_timing.py` resolves them against `vo/words.json` into
`src/shared/timing.ts` (and `vo/scenes.txt`, every scene's words with local frames).
Every scene arrives over 14 frames and is lengthened by that overlap so it
still starts on its word. The transition says what kind of step it is
(`src/scenes/Film.tsx`): a torn-paper wipe into each chapter card and the end
screen, an upward tear for the twist, paper rising for the first scene of a
chapter or a new study, a push from the right for the next step, from the left
for going back, and a cross-fade where the image continues.

The film ends on a 13 s YouTube end screen (two 16:9 video placeholders and a
subscribe circle + button); add the matching elements in YouTube Studio over
the last 13 seconds.

## Rebuild

```bash
npm install
bash vo/edit_vo.sh
python3 vo/transcribe.py vo/voiceover_edit.wav small.en
python3 vo/build_timing.py
python3 ~/.claude/skills/vox-skill/scripts/score.py music/bed.wav --seconds 322 --key C --bpm 84 --motif 0.8 --pulse 0.6 --bright 0.5 --build 0.1
python3 vo/build_audio.py -14        # voice -16 LUFS, ducked bed, stamp thuds → public/audio/mix.wav
npm run release                       # audit → render → poster → verify MP4 → copy deliverable
```

Fonts: install `public/fonts/*.woff2` as system fonts (converted to .ttf) so
Chromium resolves them offline.

## Layout audit

Same checker as `gamestop-vox` (`FitCheck` in `src/scenes/kit.tsx`, run by
`qc/fitcheck.mjs`): a settled frame after every cue plus each scene's end
(169 frames), failing on CONTAIN, COVERED and OVERLAP. Text clipped on purpose
(odometer wheels) is judged only where it shows; strike-throughs and circles are
tagged `data-mark`.

## Facts on screen

All from the script. Charts marked "illustrative" show the shape of a finding,
not its data: the auction-volume spikes (Lacetera, Pope & Sydnor, 2012), the
mileage price curve between the stated −$10 / −$210 steps, and the 2019
average-price bars.
