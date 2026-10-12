import json, math, numpy as np, soundfile as sf, os
D = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(D + '/timeline.json')); script = json.load(open(D + '/script.json'))
SR = 24000; N = int(math.ceil(tl['total'] * SR)) + SR
voice = np.zeros(N)
for l in tl['lines']:
    a, _ = sf.read(f"{D}/audio/line{l['i']:02d}.wav"); s = int(round(l['v0'] * SR)); voice[s:s + len(a)] += a
voice *= 0.89 / np.max(np.abs(voice))

# quiet music bed: soft pad chords plus a gentle plucked arpeggio
t = np.arange(N) / SR; music = np.zeros(N)
f = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]]  # C Am F G
bar = 4.0
for b in range(int(tl['total'] / bar) + 2):
    ch = chords[b % 4]; s0 = int(b * bar * SR); n = int((bar + 1.5) * SR); s1 = min(N, s0 + n)
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR
    env = np.minimum(1, tt / 1.2) * np.exp(-np.maximum(0, tt - bar) / 0.5)
    for m in ch:
        music[s0:s1] += env * (np.sin(2 * np.pi * f(m) * tt) + 0.25 * np.sin(4 * np.pi * f(m) * tt)) * 0.05
    for k in range(8):  # arpeggio, one note per half second
        m = ch[[0, 1, 2, 3, 2, 1, 2, 3][k]] + 12; p0 = s0 + int(k * 0.5 * SR); p1 = min(N, p0 + int(1.2 * SR))
        if p0 >= N: break
        tp = np.arange(p1 - p0) / SR
        music[p0:p1] += np.exp(-tp / 0.35) * np.sin(2 * np.pi * f(m) * tp) * 0.035 * np.minimum(1, tp / 0.005)
# smooth lowpass to keep it soft
k = np.exp(-np.arange(60) / 12.0); k /= k.sum(); music = np.convolve(music, k, mode='same')
# duck under the voice
act = np.convolve((np.abs(voice) > 0.02).astype(float), np.ones(int(0.4 * SR)) / int(0.4 * SR), mode='same')
duck = 1 - 0.45 * np.clip(act * 4, 0, 1)
music = music / np.max(np.abs(music)) * 0.11 * duck
fade = np.minimum(1, t / 2.0) * np.clip((tl['total'] + 0.5 - t) / 3.0, 0, 1)
mix = voice + music * fade
mix = mix[:int(tl['total'] * SR)]
sf.write(D + '/audio/mix.wav', mix / max(1, np.max(np.abs(mix)) / 0.95), SR)

# subtitles: each line split into chunks of at most seven words, timed inside that line's real audio
def chunks(text):
    w = text.split(); n = math.ceil(len(w) / 7); target = len(w) / n; out = []; cur = []
    for i, x in enumerate(w):
        cur.append(x); left = len(w) - i - 1
        if len(cur) == 7 or (len(cur) >= target - 1.5 and x[-1] in ',.:?!' and left >= 2) or (len(cur) >= math.ceil(target) and left > 0 and len(out) < n - 1):
            out.append(cur); cur = []
    if cur:
        if out and len(cur) <= 2 and len(out[-1]) + len(cur) <= 7: out[-1] += cur
        else: out.append(cur)
    return [' '.join(c) for c in out]
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
srt = []; k = 1; worst = 9; L = tl['lines']
for j, l in enumerate(L):
    cs = script[l['i']]['chunks']; tot = sum(len(c) for c in cs)
    win_end = min(L[j + 1]['v0'] - 0.12, l['v1'] + 1.0) if j + 1 < len(L) else tl['total'] - 0.2
    # proportional starts on the real audio, then make every chunk hold >= 0.3 s per word
    starts = [l['v0']]
    for c in cs[:-1]: starts.append(starts[-1] + l['dur'] * len(c) / tot)
    ends = []
    for m, c in enumerate(cs):
        st = max(starts[m], ends[-1] if ends else 0); starts[m] = st
        nat = starts[m + 1] if m + 1 < len(cs) else l['v1'] + 0.25
        ends.append(max(nat, st + 0.3 * len(c.split()) + 0.03))
    over = ends[-1] - win_end
    if over > 0: print('window overflow line', j, round(over, 2))
    for m, c in enumerate(cs):
        worst = min(worst, (ends[m] - starts[m]) / len(c.split()))
        srt.append(f"{k}\n{ts(starts[m])} --> {ts(ends[m])}\n{c}\n"); k += 1
open(D + '/subtitles.srt', 'w').write('\n'.join(srt))
print('chunks', k - 1, 'min seconds per word', round(worst, 3))
