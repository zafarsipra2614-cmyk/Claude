# TikTok-style captions

Burns captions into a video: 4 words at a time (max 5), white bold uppercase
text with a black outline, and a red box behind the word being spoken.

```
pip install faster-whisper pillow fonttools
python captions/make_captions.py input.mp4 output.mp4
```

Needs `ffmpeg`. The first run downloads a Whisper speech model from Hugging Face.
Use `--model medium` for better accuracy, or `--words words.json`
(`[[start, end, "word"], ...]`) to supply your own timings.

Tweak `WORDS_PER_CAPTION`, `RED`, and `centre_y` at the top of the script.
Font: Montserrat ExtraBold (SIL Open Font License, see `fonts/OFL.txt`).
