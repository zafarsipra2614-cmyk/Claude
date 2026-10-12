import json, sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
M=sys.argv[1]; out=sys.argv[2]
k=Kokoro(M+"/kokoro-v1.0.onnx",M+"/voices-v1.0.bin")
lines=json.load(open(out+"/script.json"))
durs=[]
for i,l in enumerate(lines):
    s,sr=k.create(l["say"],voice="af_heart",speed=0.9,lang="en-us")
    # trim near-silence at ends
    a=np.abs(s); idx=np.where(a>0.01)[0]; s=s[max(0,idx[0]-240):idx[-1]+2400]
    sf.write(f"{out}/audio/line{i:02d}.wav",s,sr); durs.append(len(s)/sr); print(i,round(len(s)/sr,2))
json.dump(durs,open(out+"/audio/durs.json","w"))
print("total",sum(durs))
