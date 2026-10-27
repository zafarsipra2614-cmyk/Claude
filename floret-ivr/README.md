# Floret Capitals – IVR greeting

| File | Use |
|---|---|
| `floret_ivr_<female|male>_8k_mono.wav` | Upload to the phone system (8 kHz, mono, 16-bit PCM, band-limited to 250–3500 Hz) |
| `floret_ivr_<female|male>_review.mp3` | Full-quality copy for listening/approval |

Length: about 20–22 s of speech, 32–33 s in total (1 s music intro, the script's pauses, and a 4 s music tail with fade-out).

Voices (8% slower than normal):
- Female: `en-IN-NeerjaNeural` + `ur-PK-UzmaNeural`
- Male: `en-IN-PrabhatNeural` + `ur-PK-AsadNeural`

Each section is read as one natural sentence (no spliced fragments). "Flor-et" / "فلورِٹ" steers FLOR-et;
PMEX/PSX are written as spaced letters (P M E X) so they are spelled out.

Music: original soft piano and pad bed generated in code (no licensing needed), ducked under the voice.

## Rebuild
```bash
pip install edge-tts numpy
python3 make_voice.py male clips/         # set TTS_CA_BUNDLE=<ca.crt> if behind a TLS proxy
python3 build_mix.py clips/ . male
```
Edit the text in `make_voice.py` and the pauses in `build_mix.py` (`TIMELINE`).
