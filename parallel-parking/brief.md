# Brief: Parallel Parking in 3 Moves

- Topic: how to parallel park. Takeaway: "right, straight, left".
- Audience: new / learner drivers, no prior experience. Friendly, plain tone.
- Length/format: ~60 s, 16:9 (1920x1080).
- Traffic side: right-hand traffic (park on the right curb).
- Voice: none. Captions only. Caption timing comes from silent clips in audio/ (len/18 + 0.8 s per line, min 2.5 s), voice.json uses the "files" engine.
- Facts: standard reference-point method (align rear bumpers, reverse full right to ~45°, straighten until the front clears, full left until parallel, pull forward). Space size (~1.5 car lengths), side gap (2–3 ft) and curb distance (~1 ft) are rules of thumb; legal curb distance varies by jurisdiction (e.g. 12 or 18 inches in different US states).

## Rebuild
Regenerate silent clips (see timing rule above) into audio/<scene>_<line>.wav, then:
  python3 ../.claude/skills/whiteboard-video/scripts/make_audio.py .
  CHROME_PATH=<chrome launched with --no-sandbox when running as root> node ../.claude/skills/whiteboard-video/scripts/render.js . full
