# Project notes for Claude

## Video work (vox-skill / Remotion)

- **Client gives a script + voiceover:** use the vox-skill's voiceover mode
  (`.claude/skills/vox-skill/references/voiceover-mode.md`, start with
  `scripts/scaffold_vo.sh`). It encodes every rule below.
- **Raise the quality with the installed style skills** (sources and setup in
  `.claude/skills/THIRD_PARTY_SKILLS.md`); borrow from them into the voiceover-mode
  film rather than switching pipelines:
  - `remotion-best-practices` (official): Remotion markup, animation, captions,
    maps (`remotion-maps` for route/map scenes) — consult before writing scenes.
  - `papercut-*`: its library's camera moves (crane, dolly zoom, rack focus,
    snap zoom, pull back…), paper-fold transitions, synthesised SFX and QA
    contact-sheet checklist (`papercut-qa`) — reels are 9:16, our films stay 16:9.
  - `cinematic-film`: documentary grammar — one continuous camera over archival
    photos, documents and maps, and public-domain Wikimedia images with licences
    recorded (credits) — for history/true-story beats.
  - `gbro-collage-info`: halftone paper-collage infographic patterns (number
    impact, process, list convergence, comparison flip, result highlight) —
    rebuild the chosen pattern in our Remotion system at 1920×1080.

- **No footer of any kind.** No dark desk band (the skill's `DeskEdge`) and no
  pale paper strip (`PaperBand`) across the bottom. Compose every scene on the
  full 16:9 frame (1920×1080) and put labels next to what they label.
- **Never push a video that hasn't passed the audit.** For each video project
  (`gamestop-vox`, `brandonomics-99`), ship only through `npm run release`, which:
  1. runs the layout audit (`npm run audit`, `qc/fitcheck.mjs`) on a settled
     frame after every cue plus each scene's end, failing on
     - CONTAIN: text past its container's padding, or anything outside the frame
     - COVERED: anything painted on top of text
     - OVERLAP: text on text, or two boxes colliding (only `data-layer="over"`
       elements such as stamps may sit on other boxes, and still never on text);
  2. renders, then pulls every audited frame back out of the MP4 and compares
     it with the audited still; the deliverable is replaced only if all match.
  Still look at a contact sheet of every scene for anything the rules can't
  judge (wrong numbers, awkward spacing, things that merely touch).
- New containers get `data-fit="name"`; text laid over a separate card gets
  `data-inside="id"` with the card tagged `data-box="id"`; deliberate marks on
  text (strike-throughs, circles) get `data-mark`.
- When working from a client's voiceover, time everything from word-level
  timestamps of the actual recording, and apply any requested audio edits to
  the recording itself (scripted, losslessly) before re-transcribing.
