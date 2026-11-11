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
node qc/fitcheck.mjs                                         # layout QC: must print "clean"
npx remotion render src/index.ts GameStopSequence out/final.mp4
```

## Layout QC

`qc/fitcheck.mjs` renders each scene's fullest frame and runs an in-page checker
(`FitCheck` in `src/scenes/kit.tsx`). Containers are tagged `data-fit` (text must
stay inside the padding and the box inside the frame) or `data-box` / `data-inside`
(text positioned over a separate backing card). Any overflow is reported with its
side and size in px and the script exits 1. It also writes `out/qc/sheet.png`.

## Facts on screen

- Short interest ≈140% of float, mid-January 2021 (widely reported estimate).
- GME closes (pre-2022 4-for-1 split): $17.25 Jan 4 → $347.51 Jan 27 → $53.50 Feb 4.
- Melvin Capital: −53% in January 2021.
- Jan 28, 2021: Robinhood and other brokers restrict buying (position closing only).
- House Financial Services Committee hearing: Feb 18, 2021.
- GameStop fiscal 2019 net loss ≈ $471M.
- Jan 25, 2021: Citadel and Point72 put $2.75B into Melvin Capital.
- Jan 28, 2021: GME intraday high ≈ $483, close $193.60; Robinhood faced a ~$3B clearinghouse deposit call.
