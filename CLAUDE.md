# Project notes for Claude

## Video work (vox-skill / Remotion)

- **No footer of any kind.** No dark desk band (the skill's `DeskEdge`) and no
  pale paper strip (`PaperBand`) across the bottom. Compose every scene on the
  full 16:9 frame (1920×1080) and put labels next to what they label.
- **Never push a video that hasn't passed the audit.** For `gamestop-vox`, ship
  only through `npm run release`, which:
  1. runs the layout audit (`npm run audit`, `qc/fitcheck.mjs`) on a settled
     frame after every cue plus each scene's end, failing on
     - CONTAIN: text past its container's padding, or anything outside the frame
     - COVERED: anything painted on top of text
     - OVERLAP: text on text, or two boxes colliding (only `data-layer="over"`
       elements such as stamps may sit on other boxes, and still never on text);
  2. renders, then pulls every audited frame back out of the MP4 and compares
     it with the audited still; the deliverable is replaced only if all match.
  Still look at `out/qc/sheet.png` for anything the rules can't judge.
- New containers get `data-fit="name"`; text laid over a separate card gets
  `data-inside="id"` with the card tagged `data-box="id"`.
