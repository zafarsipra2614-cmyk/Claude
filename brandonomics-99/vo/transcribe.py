"""Word-level timestamps for the supplied voiceover (faster-whisper)."""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "small.en", device="cpu", compute_type="int8")
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-f", "s16le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
segs, info = m.transcribe(audio, word_timestamps=True, beam_size=5, vad_filter=False,
                          initial_prompt="Manoj Thomas, Vicki Morwitz, Eric Anderson, Duncan Simester, Nicola Lacetera, Devin Pope, Justin Sydnor, Monica Wadhwa, Kuangjie Zhang.")
words = []
for s in segs:
    for w in s.words:
        words.append({"w": w.word.strip(), "t": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)})
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}", flush=True)
json.dump({"duration": info.duration, "words": words}, open("vo/words.json", "w"), indent=0)
