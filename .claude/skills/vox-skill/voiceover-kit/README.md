# voiceover-kit

Project template for **voiceover mode**: a client script + recorded voiceover →
long-form paper-cut explainer. Start a film with

```bash
bash ../scripts/scaffold_vo.sh <project-dir> <voiceover.mp3> [script.txt] [deliverable.mp4]
```

and follow `../references/voiceover-mode.md`. The example scenes in
`src/scenes/example.tsx` and the placeholder `src/shared/timing.ts` exist only so
a fresh project compiles and renders; both are replaced for each film.

| Path | What |
|---|---|
| `vo/edit_vo.sh` | client audio edits, lossless, → `vo/voiceover_edit.wav` |
| `vo/transcribe.py` | word timestamps (faster-whisper) → `vo/words.json` |
| `timeline.example.json` → `timeline.json` | scene start phrases and word cues |
| `vo/build_timing.py` | → `src/shared/timing.ts`, `vo/scenes.txt` |
| `vo/build_audio.py` | voice + ducked bed + stamp thuds → `public/audio/mix.wav` |
| `src/scenes/lib.tsx` | paper system: Frame, Tag, Card, Icon/Glyph, ChapterCard, Headline, Odometer, Tick |
| `src/scenes/transitions.tsx` | torn-paper wipe (across and upward) |
| `src/scenes/endcard.tsx` | YouTube end screen |
| `src/scenes/kit.tsx` | Rise/Label/Kicker and the in-page layout audit (FitCheck) |
| `qc/fitcheck.mjs` | `npm run audit` |
| `src/scenes/Thumbnail.tsx`, `qc/thumbnail.mjs` | newspaper-collage YouTube thumbnail; `npm run thumbnail` → audited 1280×720 JPEG |
| `qc/release.mjs` | `npm run release`: audit → render → poster → verify MP4 → deliverable |

`package.json` → `video.composition` / `video.deliverable` name the composition
and the output file.
