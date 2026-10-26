"""Forced alignment of the Roman Urdu lyrics on the isolated vocals with Meta's MMS aligner (torchaudio).
Each line is aligned inside a window around its rough position; '*' tokens at both ends absorb any
neighbouring chant or ad-lib, so only the line's own words are placed."""
import json, re, torch, torchaudio, librosa, numpy as np
import torchaudio.functional as F
from torchaudio.pipelines import MMS_FA as bundle
from scenes import LYRICS, LYR_END, CHANTS

model = bundle.get_model(with_star=True); model.eval()
DICT = bundle.get_dict(star='*')
y, _ = librosa.load('sep/htdemucs/song/vocals.wav', sr=16000, mono=True)
wav = torch.from_numpy(y).float()
old = {float(k): v for k, v in json.load(open('audio/word_times_vocal.json')).items()}
starts = sorted([l[0] for l in LYRICS] + [c[0] for c in CHANTS])


def norm(w): return re.sub(r"[^a-z']", '', w.lower())


out, rep = {}, []
for t0, ro, en in LYRICS:
    words = ro.replace('"', '').split(' ')
    toks = [norm(w) for w in words]
    o = old[t0]
    a = max(0.0, o[0] - 1.2)
    nxt = [s for s in starts if s > t0 + 0.3]
    b = min(o[-1] + 1.6, (nxt[0] + 1.0) if nxt else o[-1] + 1.6)
    seg = wav[int(a * 16000):int(b * 16000)]
    with torch.inference_mode():
        em, _ = model(seg[None])
    targets = [DICT['*']] + [DICT[c] for w in toks for c in w] + [DICT['*']]
    ali, scores = F.forced_align(em, torch.tensor([targets], dtype=torch.int32), blank=0)
    spans = F.merge_tokens(ali[0], scores[0].exp())
    fr = (b - a) / em.shape[1]
    # spans line up 1:1 with targets (star, chars..., star)
    k = 1; times, conf = [], []
    for w in toks:
        sp = spans[k:k + len(w)]
        times.append(round(a + sp[0].start * fr, 3)); conf.append(float(np.mean([s.score for s in sp])))
        k += len(w)
    out[str(t0)] = times
    rep.append((t0, ro, times, o, float(np.mean(conf))))
json.dump(out, open('audio/word_times_final.json', 'w'))
for t0, ro, ts, o, cf in rep:
    d = [round(x - y, 2) for x, y in zip(ts, o)]
    print(f"{t0:6.1f} conf={cf:.2f}  {ro[:34]:34s} first={ts[0]:7.2f} (was {o[0]:7.2f})  shifts={d}")
