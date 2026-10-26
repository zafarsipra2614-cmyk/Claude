from faster_whisper import WhisperModel
import json, librosa
a, _ = librosa.load('sep/htdemucs/song/vocals.wav', sr=16000)
m = WhisperModel('medium', device='cpu', compute_type='int8', cpu_threads=4)
segs, info = m.transcribe(a, language='hi', word_timestamps=True, vad_filter=False, beam_size=5, condition_on_previous_text=False)
out = []
for s in segs:
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}", flush=True)
    out.append({'start': s.start, 'end': s.end, 'text': s.text, 'words': [{'w': w.word, 's': w.start, 'e': w.end} for w in s.words]})
json.dump(out, open('audio/whisper_vocals.json', 'w'), ensure_ascii=False)
print('WHISPER_DONE')
