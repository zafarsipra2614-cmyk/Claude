# Brief: The Hawthorne Effect

- Takeaway: watching people can change what you see.
- Audience: general, no psychology background. Plain, friendly tone.
- Length/format: ~60 s, 16:9 (1920x1080). Captions only, no voice (silent clips in audio/, len/16 + 0.8 s per line, min 2.5 s; voice.json uses the "files" engine).

## Facts and sources (checked 2026-11-11)
- Illumination tests at Western Electric's Hawthorne Works, Cicero, Illinois (near Chicago), from Nov 1924 to 1927; further studies into the early 1930s.
  https://www.simplypsychology.org/hawthorne-effect.html · https://www.ebsco.com/research-starters/social-sciences-and-humanities/hawthorne-effect
- Term usually credited to Henry A. Landsberger (1958); some sources credit John R. P. French (1953).
  https://www.scientificamerican.com/blog/absolutely-maybe/the-hawthorne-effect-an-old-scientists-tale-lingering-in-the-gunsmoke-of-academic-snipers/
- Levitt & List (2011, AEJ: Applied Economics 3(1):224-238) recovered the illumination data: the described patterns were "entirely fictional", with subtler signs of a possible effect.
  https://www.nber.org/papers/w15016 · https://pmc.ncbi.nlm.nih.gov/articles/PMC9679018

## Rebuild
  python3 ../.claude/skills/whiteboard-video/scripts/make_audio.py .
  CHROME_PATH=<chrome with --no-sandbox when running as root> node ../.claude/skills/whiteboard-video/scripts/render.js . full
