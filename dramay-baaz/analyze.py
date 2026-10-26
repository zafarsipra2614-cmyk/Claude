# Beat grid, onsets and per-band energy envelopes (30 fps) for driving the visuals.
import librosa, numpy as np, json
y, sr = librosa.load('audio/song.mp3', sr=22050, mono=True)
dur = len(y)/sr
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time', start_bpm=125)
hop = 735  # 30 fps at 22050
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
def band(lo, hi):
    e = S[(f>=lo)&(f<hi)].mean(0); e = e/np.percentile(e, 98); return np.clip(e,0,1.5)
bass, mid, high = band(30,150), band(300,3000), band(5000,11000)
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; rms = rms/np.percentile(rms,98)
on = librosa.onset.onset_detect(y=y, sr=sr, units='time', hop_length=256)
r = lambda a: [round(float(x),3) for x in a]
json.dump({'dur':dur,'tempo':float(np.atleast_1d(tempo)[0]),'beats':r(beats),'onsets':r(on),
  'bass':r(bass),'mid':r(mid),'high':r(high),'rms':r(rms)}, open('audio/analysis.json','w'))
print('dur',dur,'tempo',tempo,'beats',len(beats), beats[:8])
# 2-second energy summary
for i in range(0,int(dur),2):
    a=slice(i*30,(i+2)*30); print(f"{i:4d}s rms={rms[a].mean():.2f} bass={bass[a].mean():.2f} hi={high[a].mean():.2f} "+'#'*int(rms[a].mean()*30))
