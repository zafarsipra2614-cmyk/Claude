// PLACEHOLDER so the kit compiles before a voiceover exists.
// Replaced by vo/build_timing.py from vo/words.json + timeline.json.

export const FPS = 30;
export const T = 14;

export const D = {
  hook: 150,
  ch1: 110,
  endcard: 360,
} as const;

export const SCENE_ORDER = ["hook", "ch1", "endcard"] as const;
export const SEQUENCE_DURATION = 620;

export const CUE = {
  "ch1.num": 8,
  "ch1.title": 34,
  "endcard.left": 30,
  "endcard.right": 70,
  "endcard.sub": 50,
  "endcard.thanks": 6,
  "hook.a": 4,
  "hook.b": 30,
  "hook.stamp": 90,
} as const;
