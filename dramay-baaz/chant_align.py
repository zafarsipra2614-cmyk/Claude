"""Find every group chant in the gaps between lyric lines with the MMS forced aligner and pin each
chant word (DRAMAY / BAAZ, or AB / NO / DRAMAY / BAAZI) to the syllable actually sung."""
import json, re, torch, librosa, numpy as np
import torchaudio.functional as F
from torchaudio.pipelines import MMS_FA as bundle
from scenes import LYRICS

model = bundle.get_model(with_star=True); model.eval(); DICT = bundle.get_dict(star='*')
y, _ = librosa.load('sep/htdemucs/song/vocals.wav', sr=16000, mono=True); wav = torch.from_numpy(y).float()
DUR = len(y) / 16000
FT = {float(k): v for k, v in json.load(open('audio/word_times_final.json')).items()}
spans = sorted((FT[l[0]][0] - 0.12, FT[l[0]][-1] + 0.35) for l in LYRICS)
gaps = []; cur = 0.0
for a, b in spans:
    if a - cur > 0.6: gaps.append((cur, a))
    cur = max(cur, b)
gaps.append((cur, DUR))
PHR = {'DB': ['dramay', 'baaz'], 'NO': ['ab', 'no', 'dramay', 'baazi']}


def try_align(a, b, kind, k):
    seg = wav[int(a * 16000):int(b * 16000)]
    with torch.inference_mode(): em, _ = model(seg[None])
    words = PHR[kind] * k
    tg = [DICT['*']]
    for i, w in enumerate(words):
        tg += [DICT[c] for c in w]
        if (i + 1) % len(PHR[kind]) == 0: tg.append(DICT['*'])
    ali, sc = F.forced_align(em, torch.tensor([tg], dtype=torch.int32), blank=0)
    sp = F.merge_tokens(ali[0], sc[0].exp())
    fr = (b - a) / em.shape[1]
    res = []; idx = 1
    for c in range(k):
        rep = []
        for w in PHR[kind]:
            s = sp[idx:idx + len(w)]; idx += len(w)
            rep.append((w, round(a + s[0].start * fr, 3), round(a + s[-1].end * fr, 3), float(np.mean([x.score for x in s]))))
        idx += 1   # star between repetitions
        res.append(rep)
    return res


events = []
for a, b in gaps:
    L = b - a
    kinds = ['NO', 'DB'] if 113 < a < 143 else ['DB']
    best = None
    for kind in kinds:
        per = 1.6 if kind == 'NO' else 0.85
        kmax = max(1, int(L / per))
        res = try_align(a, b, kind, kmax)
        good = [r for r in res if np.mean([w[3] for w in r]) > 0.3 and r[-1][2] - r[0][1] < 2.4]
        score = sum(np.mean([w[3] for w in r]) for r in good)
        if best is None or score > best[0]: best = (score, kind, good)
    for r in best[2]:
        events.append(dict(kind=best[1], start=r[0][1], end=r[-1][2], words=[(w[0].upper(), w[1]) for w in r],
                           score=round(float(np.mean([w[3] for w in r])), 2)))
events.sort(key=lambda e: e['start'])
json.dump(events, open('audio/chants_aligned.json', 'w'))
for e in events:
    print(f"{e['start']:7.2f}-{e['end']:7.2f} {e['kind']} score={e['score']:.2f}  " + '  '.join(f"{w}@{t:.2f}" for w, t in e['words']))
print(len(events), 'chant phrases')
