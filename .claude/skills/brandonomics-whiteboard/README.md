# brandonomics-whiteboard

The Brandonomics whiteboard explainer video skill for Claude Code. Pictures sketch, ink and colour themselves; bold black outlines; hatched pencil shadows; Brandonomics blue in every scene; Permanent Marker titles and Indie Flower labels; James as the locked recurring lead; captions; 1920x1080 MP4. Rendered locally with headless Chrome and ffmpeg.

Read `SKILL.md` for the house style, the quality gate and the workflow. Quick start:

```bash
cd scripts && npm install && pip install scikit-image
cp -r ../examples/hawthorne-effect /tmp/hawthorne && cd ..
python3 scripts/silent_audio.py /tmp/hawthorne && python3 scripts/make_audio.py /tmp/hawthorne
node scripts/prep.js /tmp/hawthorne && node scripts/render.js /tmp/hawthorne check && node scripts/render.js /tmp/hawthorne full
```

Based on [whiteboard-video-skill](https://github.com/Matteoikarieth96/whiteboard-video-skill) by Matteoikarieth96 (MIT). Characters: Open Peeps by Pablo Stanley (CC0). Fonts: OFL-1.1 / Apache-2.0, licences in `assets/fonts/`.
