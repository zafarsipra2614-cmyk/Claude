"""Final lyric alignment on the isolated vocals:
1) Whisper (run on vocals.wav) gives word starts inside each lyric line's window,
2) lyric words map onto those starts in order (proportionally when the counts differ),
3) each word snaps to the nearest strong vocal syllable onset within 100 ms."""
import json, bisect
from scenes import LYRICS, LYR_END, CHANTS

old = {float(k): v for k, v in json.load(open('audio/word_times_vocal.json')).items()}
wh = [w for s in json.load(open('audio/whisper_vocals.json')) for w in s['words'] if w['e'] - w['s'] < 2.5]
WS = sorted(set(round(w['s'], 3) for w in wh))
ON = [o for o in json.load(open('audio/vocal_onsets.json'))['onsets'] if o[1] > 0.25]
OT = [o[0] for o in ON]
chant_starts = sorted(c[0] for c in CHANTS)

out, report = {}, []
for t0, ro, en in LYRICS:
    n = len(ro.replace('"', '').split(' '))
    o = old[t0]
    lo = o[0] - 0.45
    nxt = [c for c in chant_starts if c > o[0] + 0.3] + [x[0] for x in LYRICS if x[0] > t0]
    hi = min([o[-1] + 0.8] + [x - 0.05 for x in nxt[:1]] + [min(nxt) - 0.05] if nxt else [o[-1] + 0.8])
    cand = [x for x in WS if lo <= x <= hi]
    if len(cand) >= max(2, int(n * 0.6)):
        if len(cand) >= n:
            times = [cand[round(i * (len(cand) - 1) / max(1, n - 1))] for i in range(n)]
        else:
            times = []
            for i in range(n):
                x = i * (len(cand) - 1) / max(1, n - 1); k = int(x); f = x - k
                times.append(cand[k] if k + 1 >= len(cand) else cand[k] + (cand[k + 1] - cand[k]) * f)
        src = 'whisper-vocals'
    else:
        times = list(o); src = 'previous'
    snapped = []
    for i, x in enumerate(times):
        j = bisect.bisect_left(OT, x)
        near = [OT[k] for k in (j - 1, j) if 0 <= k < len(OT) and abs(OT[k] - x) <= 0.1]
        y = min(near, key=lambda z: abs(z - x)) if near else x
        if snapped and y <= snapped[-1] + 0.06: y = max(x, snapped[-1] + 0.08)
        snapped.append(round(y, 3))
    out[str(t0)] = snapped
    report.append((t0, src, max(abs(a - b) for a, b in zip(snapped, o)), ro))
json.dump(out, open('audio/word_times_final.json', 'w'))
for t0, src, d, ro in report:
    print(f"{t0:6.1f}  {src:15s} max shift {d:5.2f}s  {ro}")
