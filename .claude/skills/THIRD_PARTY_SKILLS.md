# Third-party skills installed in this repo

All MIT-licensed except where noted; each keeps its own LICENSE. Installed by
copying from GitHub after a code review (network calls, destructive commands,
paid services). Upstream docs and demo media were left out.

| Skill(s) | Source | Licence | Engine | Needs |
|---|---|---|---|---|
| `papercut-explainer`, `papercut-setup`, `-strategy`, `-hook`, `-script`, `-storyboard`, `-voice`, `-build`, `-qa` | [0xS4N4TG/papercut-explainer](https://github.com/0xS4N4TG/papercut-explainer) | MIT | Remotion | library at `.claude/vendor/papercut-explainer/library`; set `PAPERCUT_LIB` to it (or the `PAPERCUT_LIB=` line in `~/.config/papercut-explainer/config.env`). Node 20+, ffmpeg, numpy/Pillow/soundfile, Chromium. Its optional local TTS (Qwen3, several GB) is not needed: we use the client's voiceover |
| `remotion-best-practices` (router) and 12 more `remotion-*` | [remotion-dev/skills](https://github.com/remotion-dev/skills) (official, v4.0.543) | Remotion's terms | Remotion | nothing; guidance only. Required by `papercut-build` |
| `cinematic-film` | [Moh4696/cinematic-skill](https://github.com/Moh4696/cinematic-skill) | MIT | Python + Skia | `pip install -r .claude/skills/cinematic-film/requirements.txt` (skia-python, numpy, pillow). Contacts only Wikimedia Commons (public-domain photos, licences recorded), jsDelivr (map outlines) and Google Fonts |
| `gbro-collage-info` | [pyang5166/gbro-collage-info](https://github.com/pyang5166/gbro-collage-info) | MIT | HyperFrames (HTML/CSS/GSAP) | Node 22+, `hyperframes@0.7.56` (npm, on first use), Chromium, ffmpeg. Docs in Chinese; output defaults to 1080×1920, set 1920×1080 for our films |

Not installed: `Vincentwei1021/video-talkcraft` (PolyForm Noncommercial — not for a
monetised channel); Vox skills that need paid generation services (Atlas Cloud,
MaxFusion, image-generation APIs).
