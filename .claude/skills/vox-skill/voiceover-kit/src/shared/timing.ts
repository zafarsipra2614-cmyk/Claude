// PLACEHOLDER so the kit compiles before a voiceover exists.
// Replaced by vo/build_timing.py from vo/words.json + timeline.json.

export const FPS = 30;
export const T = 14;

export const D = {
  hook: 150,
  ch1: 110,
  doc: 210,
  endcard: 360,
} as const;

export const SCENE_ORDER = ["hook", "ch1", "doc", "endcard"] as const;
export const SEQUENCE_DURATION = 830;

export const CUE = {
  "ch1.num": 8,
  "ch1.title": 34,
  "doc.clip": 70,
  "doc.photo": 4,
  "doc.zoom": 150,
  "endcard.left": 30,
  "endcard.right": 70,
  "endcard.sub": 50,
  "endcard.thanks": 6,
  "hook.a": 4,
  "hook.b": 30,
  "hook.stamp": 90,
} as const;
