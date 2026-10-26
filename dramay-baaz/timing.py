"""Per-word timings for every lyric line: map the line's words onto Whisper's word timestamps inside the line's
window (the transcript is in Devanagari, so we match by position, not spelling), fall back to even spacing."""
import json
from scenes import LYRICS, LYR_END, CHANTS

WH = [w for s in json.load(open('audio/whisper_medium_hi.json')) for w in s['words']]


def line_word_times(t0, t1, n):
    ws = [w['s'] for w in WH if t0 - 0.25 <= w['s'] < t1 - 0.1]
    ws = sorted(set(round(x, 2) for x in ws))
    if len(ws) >= max(2, n * 0.6):
        if len(ws) >= n:
            return [ws[round(i * (len(ws) - 1) / max(1, n - 1))] for i in range(n)]
        # fewer detected words than lyric words: interpolate between detected anchors
        out = []
        for i in range(n):
            x = i * (len(ws) - 1) / max(1, n - 1); k = int(x); f = x - k
            out.append(ws[k] if k + 1 >= len(ws) else ws[k] + (ws[k + 1] - ws[k]) * f)
        return out
    span = max(0.6, (t1 - t0) * 0.6)
    return [t0 + span * i / max(1, n) for i in range(n)]


# hand fixes where the Devanagari transcript was garbled
MANUAL = {18.1: [18.1, 18.44, 18.7, 19.15, 19.9], 130.2: [130.16, 130.5, 130.85, 131.25, 131.55],
          124.4: [124.42, 124.85, 125.25, 125.7, 126.05]}


if __name__ == '__main__':
    out = {}
    for t0, ro, en in LYRICS:
        words = ro.replace('"', '').split(' ')
        t1 = min([LYR_END[t0]] + [c[0] for c in CHANTS if c[0] > t0 + 0.5])
        times = line_word_times(t0, t1, len(words))
        if t0 in MANUAL: times = MANUAL[t0]
        times[0] = min(times[0], t0 + 0.05) if times[0] > t0 else max(times[0], t0 - 0.2)
        out[str(t0)] = [round(x, 3) for x in times]
        print(f"{t0:6.1f} " + ' '.join(f"{w}@{x:.2f}" for w, x in zip(words, times)))
    json.dump(out, open('audio/word_times.json', 'w'))
