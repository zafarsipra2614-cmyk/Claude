"""Refine per-word lyric timings onto vocal attacks.
Harmonic/percussive separation pushes the dhol and claps out of the way, then onsets in the vocal band
(300-3500 Hz) are detected; each Whisper-derived word time moves to the strongest nearby vocal onset."""
import json, numpy as np, librosa
from scenes import LYRICS

y, sr = librosa.load('audio/song.mp3', sr=22050, mono=True)
yh, yp = librosa.effects.hpss(y, margin=3.0)
hop = 256
S = np.abs(librosa.stft(yh, n_fft=2048, hop_length=hop))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
band = S[(f > 300) & (f < 3500)]
env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(band, ref=np.max), sr=sr, hop_length=hop)
env = env / (np.percentile(env, 99) + 1e-9)
times = librosa.times_like(env, sr=sr, hop_length=hop)
peaks = librosa.util.peak_pick(env, pre_max=3, post_max=3, pre_avg=8, post_avg=8, delta=0.08, wait=4)
P = [(times[i], env[i]) for i in peaks]

base = json.load(open('audio/word_times.json'))
out, moved = {}, []
for t0, ro, en in LYRICS:
    ws = base[str(t0)]
    new = []
    for i, w in enumerate(ws):
        lo = new[-1] + 0.08 if new else w - 0.18
        cands = [(pt, st) for pt, st in P if max(lo, w - 0.15) <= pt <= w + 0.15]
        if cands:
            pt, st = max(cands, key=lambda c: c[1] * (1 - abs(c[0] - w) / 0.3))
            new.append(round(float(pt), 3)); moved.append(abs(pt - w))
        else:
            new.append(max(w, lo))
    out[str(t0)] = new
json.dump(out, open('audio/word_times_vocal.json', 'w'))
print('words refined:', len(moved), 'median shift %.3fs' % float(np.median(moved)))
for t0 in (16.2, 18.1, 45.5, 120.7):
    print(t0, out[str(t0)])
