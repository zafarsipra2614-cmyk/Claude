# Floret Capitals – IVR greeting

| File | Use |
|---|---|
| `floret_ivr_8k_mono.wav` | Upload to the phone system (8 kHz, mono, 16-bit PCM, band-limited to 250–3500 Hz) |
| `floret_ivr_review.mp3` | Full-quality copy for listening/approval |

Length: about 22 s of speech, 34.6 s in total (1 s music intro, the script's pauses, and a 4 s music tail with fade-out).

Voices (same gender, matching warm tone, 10% slower than normal):
- English: `en-IN-NeerjaNeural` (South Asian English accent)
- Urdu: `ur-PK-UzmaNeural` (Pakistani Urdu)

Pronunciation handling: "Flor-et" / "فلورِٹ" for FLOR-et; PMEX/PSX are written as separate letters with
punctuation so each letter gets a small gap; the numbers are set off with commas for a slight stress.

Music: original soft piano and pad bed generated in code (no licensing needed), ducked under the voice.

## Rebuild
```bash
pip install edge-tts numpy
python3 make_voice.py clips/          # set TTS_CA_BUNDLE=<ca.crt> if behind a TLS proxy
python3 build_mix.py clips/ .
```
Edit the text in `make_voice.py` and the pauses in `build_mix.py` (`TIMELINE`).
