"""Word-level timestamps for the supplied voiceover (faster-whisper).

    python3 vo/transcribe.py vo/voiceover_edit.wav [model]      # model default small.en

Proper names in the script (people, brands, places) go one per line in
vo/names.txt; they are passed to the model as spelling hints.
Writes vo/words.json: {"duration": s, "words": [{"w","t","e","p"}, ...]}.
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
from pathlib import Path
names = Path(__file__).with_name("names.txt")
HINT = ", ".join(l.strip() for l in names.read_text().splitlines() if l.strip()) + "." if names.exists() else None
m = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "small.en", device="cpu", compute_type="int8")
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
segs, info = m.transcribe(audio, word_timestamps=True, beam_size=5, vad_filter=False,
                          initial_prompt=HINT)
words = []
for s in segs:
    for w in s.words:
        words.append({"w": w.word.strip(), "t": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)})
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}", flush=True)
json.dump({"duration": info.duration, "words": words}, open("vo/words.json", "w"), indent=0)
