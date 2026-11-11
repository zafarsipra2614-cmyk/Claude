# The GameStop short squeeze — a 1-minute Vox-style explainer

`gamestop_short_squeeze.mp4` · 61.8s · 1920×1080 · built with the `vox-skill` (Remotion).

Every visual is drawn in code; narration is Edge neural TTS (en-US-AndrewMultilingualNeural),
the music bed is synthesised locally (`score.py`) and sidechain-ducked under the voice.

## Rebuild

```bash
npm install
# fonts: install public/fonts/*.woff2 as system fonts (converted to .ttf) so Chromium finds them offline
python3 ~/.claude/skills/vox-skill/scripts/gen_vo.py        # narration + vo/timing.json
python3 ~/.claude/skills/vox-skill/scripts/sync_timing.py   # src/shared/timing.ts from cues.json
python3 ~/.claude/skills/vox-skill/scripts/score.py music/bed.wav --seconds 61.8 --key D --bpm 76 --motif 0.85 --pulse 0.8
bash ~/.claude/skills/vox-skill/scripts/mix_audio.sh public/audio/vo.mp3 music/bed.wav music/mix.wav -12
ffmpeg -y -i music/mix.wav -c:a libmp3lame -q:a 2 public/audio/mix.mp3
npm run release                                              # audit, render, verify, copy
```

## Layout audit and release

```bash
npm run audit     # layout audit only
npm run release   # audit → render → poster → verify MP4 → copy deliverable
```

`qc/fitcheck.mjs` renders a settled frame after every cue in `src/shared/timing.ts`
plus each scene's last frame, and an in-page checker (`FitCheck` in
`src/scenes/kit.tsx`) reports:

- **CONTAIN**: text crossing its container's padding, or any text/box outside the frame
- **COVERED**: anything painted on top of a run of text (hit-tested across each line)
- **OVERLAP**: text overlapping text, or two tagged boxes colliding; elements marked
  `data-layer="over"` (stamps, the pinned rescue card) may sit on boxes, never on text

Elements still entering or exiting (`data-moving`) are skipped, so only the
settled layout is judged. Containers are tagged `data-fit`; text laid over a
separate card uses `data-inside` / `data-box`.

`qc/release.mjs` only replaces `gamestop_short_squeeze.mp4` when the audit is clean
and every audited frame decoded from the rendered MP4 matches the audited still
(results in `out/qc/release.json`).

## Facts on screen

- Short interest ≈140% of float, mid-January 2021 (widely reported estimate).
- GME closes (pre-2022 4-for-1 split): $17.25 Jan 4 → $347.51 Jan 27 → $53.50 Feb 4.
- Melvin Capital: −53% in January 2021.
- Jan 28, 2021: Robinhood and other brokers restrict buying (position closing only).
- House Financial Services Committee hearing: Feb 18, 2021.
- GameStop fiscal 2019 net loss ≈ $471M.
- Jan 25, 2021: Citadel and Point72 put $2.75B into Melvin Capital.
- Jan 28, 2021: GME intraday high ≈ $483, close $193.60; Robinhood faced a ~$3B clearinghouse deposit call.
