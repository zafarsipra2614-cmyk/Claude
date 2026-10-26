"""Rhythm map for the Bollywood edition: dhol hits (low percussive onsets), claps (high percussive onsets),
riser energy, and vocal-free gaps (from the per-word vocal timings) so instrumentals get their own choreography."""
import json, numpy as np, librosa
from scenes import LYRICS, LYR_END, CHANTS

y, sr = librosa.load('audio/song.mp3', sr=22050, mono=True)
yh, yp = librosa.effects.hpss(y, margin=2.0)
hop = 256
S = np.abs(librosa.stft(yp, n_fft=2048, hop_length=hop)); f = librosa.fft_frequencies(sr=sr, n_fft=2048)
def onsets(lo, hi, delta):
    band = S[(f >= lo) & (f < hi)]
    env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(band, ref=np.max), sr=sr, hop_length=hop)
    env = env / (np.percentile(env, 99) + 1e-9)
    pk = librosa.util.peak_pick(env, pre_max=4, post_max=4, pre_avg=10, post_avg=10, delta=delta, wait=6)
    tm = librosa.times_like(env, sr=sr, hop_length=hop)
    return [(round(float(tm[i]), 3), round(float(min(1.5, env[i])), 3)) for i in pk]
dhol = onsets(40, 250, 0.12)
clap = onsets(2500, 9000, 0.14)
rms = librosa.feature.rms(y=y, hop_length=735)[0]; rms = rms / np.percentile(rms, 98)

VT = json.load(open('audio/word_times_vocal.json'))
sung = []
for t0, ro, en in LYRICS:
    ws = VT[str(t0)]; sung.append((ws[0], max(LYR_END[t0], ws[-1] + 0.5)))
for c in CHANTS: sung.append((c[0], c[1]))
sung.sort()
gaps, cur = [], 0.0
for a, b in sung:
    if a - cur > 0.9: gaps.append((round(cur, 2), round(a, 2)))
    cur = max(cur, b)
if 159.4 - cur > 0.9: gaps.append((round(cur, 2), 159.4))
json.dump(dict(dhol=dhol, clap=clap, gaps=gaps), open('audio/rhythm.json', 'w'))
print('dhol hits', len(dhol), ' claps', len(clap))
print('vocal-free gaps (instrumental moments):')
for a, b in gaps: print(f'  {a:6.2f} - {b:6.2f}  ({b - a:4.1f}s)  rms={rms[int(a*30):int(b*30)].mean():.2f}')
