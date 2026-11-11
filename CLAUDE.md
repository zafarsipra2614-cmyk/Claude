# Project notes for Claude

## Video work (vox-skill / Remotion)

- **Check that every piece of content fits its container before pushing a video.**
  Text and elements must sit inside their card, stamp, phone screen or backing
  paper (inside its padding, not touching the border) and inside the frame.
  For `gamestop-vox`, run `node qc/fitcheck.mjs` (exits non-zero on any
  overflow), then look at `out/qc/sheet.png`; the checker cannot see
  occlusion (one element covering another), so eyeball the sheet for that.
- **No dark footer band** (the skill's `DeskEdge`) across the bottom of scenes.
  Use the space for explanatory visuals instead.
