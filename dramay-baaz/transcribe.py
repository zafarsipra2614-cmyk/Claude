from faster_whisper import WhisperModel
import json, sys
m = WhisperModel(sys.argv[1], device='cpu', compute_type='int8', cpu_threads=4)
import librosa; a,_=librosa.load('audio/song.mp3',sr=16000)
segs, info = m.transcribe(a, language=sys.argv[2], word_timestamps=True, vad_filter=False, beam_size=5, condition_on_previous_text=False)
out=[]
for s in segs:
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}", flush=True)
    out.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'w':w.word,'s':w.start,'e':w.end} for w in s.words]})
json.dump(out, open(f'audio/whisper_{sys.argv[1]}_{sys.argv[2]}.json','w'), ensure_ascii=False)
