"""STAR in Four Stamps: original West-Coast cool-jazz cue for a 49 s Reel.
Vibraphone (step chords, comping, glissandi), jazz pizzicato bass (walking), muted trumpet (the flat answer and its droop),
flute (the payoff line), brushes + hi-hat pedal, quinto-conga "bongo" fills, finger snaps.
120 BPM, swing 60 %, D major, up a step to E for the star. Every hit time comes from the film's timeline.
Run: $LIB/.venv/bin/python music/score.py   (LIB on the path; writes music/score.wav + hits.json)
"""
import sys, os, json
LIB = os.environ.get('LIB', os.path.expanduser('~/lemo-opuscar'))
sys.path.insert(0, LIB)
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
from core.audio import sampler as S
from core.audio.sfx import SR, add

OUT = os.path.dirname(os.path.abspath(__file__))
S.seed(7); rng = np.random.default_rng(7)
B = 0.5; BAR = 4 * B; DUR = 49.0; N = int(round(DUR * SR)); SW = 0.6
def T(bar, beat=0.0):
    w = np.floor(beat + 1e-9); f = beat - w
    if abs(f - .5) < 1e-6: f = SW
    return (bar - 1) * BAR + (w + f) * B
def jit(ms=5): return float(rng.uniform(-ms, ms)) / 1000
M = lambda p: S.midi(p) if isinstance(p, str) else p
stems = {k: np.zeros((N, 2), np.float32) for k in ('drums', 'bass', 'vib', 'lead')}
hits = []
def hit(t, label): hits.append(dict(t=round(float(t), 4), label=label))
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)

def motor(x, rate=5.0, depth=.3, t0=0.0):
    t = np.arange(len(x)) / SR + t0
    return x * (1 - depth * (.5 + .5 * np.sin(2 * np.pi * rate * t))).astype(np.float32)
def vib(t, pitches, dur, vel=.45, pan=-.2, hard=False, trem=0.0, gain=1.0):
    for i, p in enumerate(pitches if isinstance(pitches, (list, tuple)) else [pitches]):
        x = S.note('vibraphone_hard' if hard else 'vibraphone', M(p), dur, vel=vel)
        if trem: x = motor(x, depth=trem, t0=i * .013)
        add(stems['vib'], x, t + i * .006, gain, pan + (i - 1.5) * .07)
def vib_run(t0, pitches, step, v0=.3, v1=.6, ring=1.0, gain=1.0):
    for i, p in enumerate(pitches):
        add(stems['vib'], S.note('vibraphone_hard', M(p), ring, vel=v0 + (v1 - v0) * i / max(1, len(pitches) - 1)), t0 + i * step, gain, -.25 + .5 * i / len(pitches))
def flute(t, p, beats, vel=.5, pan=.2, gain=1.0):
    add(stems['lead'], S.note('flute', M(p), max(.12, beats * B * .9), vel=vel, release=.09), t - .02, gain, pan)
def tpt(t, p, beats, vel=.5, pan=.25, gain=1.0):
    add(stems['lead'], S.note('trumpet_mute', M(p), max(.12, beats * B * .9), vel=vel, release=.12), t - .02, gain, pan)
def bass(t, p, beats=.9, vel=.6, gain=1.0):
    add(stems['bass'], S.note('jazz_bass', M(p), max(.1, beats * B), vel=vel, release=.08), t - .012, gain, 0)
def brush_tap(t, v=.5, pan=-.1):
    d = .16; tt = np.arange(int(d * SR)) / SR; n = rng.standard_normal(len(tt))
    x = bp(n, 1500, 9000) * np.exp(-tt / .045) + .5 * bp(n, 300, 1200) * np.exp(-tt / .02) + .25 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / .03)
    add(stems['drums'], (x / 3.2 * v).astype(np.float32), t, 1, pan)
def brush_sweep(t, d, v=.3, pan=-.15):
    tt = np.arange(int(d * SR)) / SR; n = rng.standard_normal(len(tt))
    x = bp(n, 1800, 7500) + .35 * bp(n, 500, 1800)
    add(stems['drums'], (x * np.sin(np.pi * tt / d) ** 1.5 / 4 * v).astype(np.float32), t, 1, pan)
def brushes(t0, t1, v=.3):
    t = t0
    while t < t1 - 1e-6:
        brush_sweep(t + jit(4), 2 * B * 1.05, v * .8)
        for bt in (1, 3):
            tb = t + bt * B
            if tb < t1: brush_tap(tb + jit(4), v * 1.25); add(stems['drums'], S.hit('hihat', 'pedal', min(1, .35 * v / .3), .3), tb + .004, .4, .45)
        brush_sweep(t + 2 * B + jit(4), 2 * B * 1.05, v * .8)
        t += BAR
def snap(t, v=.6, pan=.3):
    d = .09; tt = np.arange(int(d * SR)) / SR; n = rng.standard_normal(len(tt))
    x = bp(n, 1800, 6000) * np.exp(-tt / .012) + .4 * np.sin(2 * np.pi * 2300 * tt) * np.exp(-tt / .008)
    add(stems['drums'], (x / 2.5 * v).astype(np.float32), t, 1, pan)
def bongo(t, v=.5, pan=.35, var='quinto'): add(stems['drums'], S.hit('conga', var, v), t, .55, pan)
def ride(t0, t1, v=.25):
    t = t0
    while t < t1 - 1e-6:
        for b in (0, 1, 1.6, 2, 3, 3.6):
            if t + b * B < t1: add(stems['drums'], S.hit('sus_cymbal', 'stick', v * (1 if b in (1, 3) else .7), 1.0), t + b * B + jit(3), .35, .35)
        t += BAR

V = {   # vibraphone voicings (rootless, mid register)
    'Dmaj9': ['F#3', 'A3', 'C#4', 'E4'], 'Bm9': ['A3', 'D4', 'F#4', 'C#5'], 'Em9': ['G3', 'B3', 'D4', 'F#4'],
    'A13': ['G3', 'C#4', 'F#4', 'B4'], 'Gmaj7': ['F#3', 'B3', 'D4', 'G4'], 'F#m7': ['E3', 'A3', 'C#4', 'E4'],
    'Emaj9': ['G#3', 'B3', 'D#4', 'F#4'], 'C#m9': ['B3', 'E4', 'G#4', 'D#5'], 'F#m9': ['A3', 'C#4', 'E4', 'G#4'], 'B13': ['A3', 'D#4', 'G#4', 'C#5'],
}
ROOT = {'Dmaj9': 'D2', 'Bm9': 'B1', 'Em9': 'E2', 'A13': 'A1', 'Gmaj7': 'G1', 'F#m7': 'F#1', 'Emaj9': 'E2', 'C#m9': 'C#2', 'F#m9': 'F#1', 'B13': 'B1'}
SCALE = {'D': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'], 'E': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#']}
def walk(t0, chords, vel=.58):
    """walking bass, one chord per bar: root, 3rd/5th, approach tone into the next root"""
    for k, ch in enumerate(chords):
        r = M(ROOT[ch]); nx = M(ROOT[chords[k + 1]]) if k + 1 < len(chords) else r
        line = [r, r + (3 if 'm' in ch else 4), r + 7, nx + (1 if nx < r + 7 else -1)]
        for b, p in enumerate(line): bass(t0 + k * BAR + b * B + jit(4), p, .92, vel * (1.08 if b == 0 else .95))
def comp(t, ch, vel=.3):
    vib(t + jit(3), V[ch], 1.4 * B, vel)
    vib(t + 1.6 * B + jit(3), V[ch], .6 * B, vel * .8)

# ================= HOOK 0–4: stab on the card pop, snaps, bass enters on bar 2
hit(0.25, 'question card pop: Dmaj9 stab')
vib(0.25, V['Dmaj9'] + ['A4'], 2.4 * B, .6, hard=True, trem=.25); bass(0.25, 'D2', 2, .75)
for b in (1, 3, 5, 7): snap(b * B + jit(3), .55)
walk(2.0, ['Bm9'], .5); vib(2.0, V['Bm9'], 1.4 * B, .26)
bongo(3.5, .4); bongo(3.75, .35, var='muted')

# ================= WRONG 4–10: the groove, the muted trumpet "answers", the droop on the X
walk(4.0, ['Em9', 'A13', 'Dmaj9'], .6); brushes(4.0, 10.0, .28)
comp(4.0, 'Em9', .24); comp(6.0, 'A13', .24); vib(8.0, V['Dmaj9'], 1.2 * B, .24)
for t, p, ln in [(4.0 + 3.6 * B, 'B4', .5), (4.0 + 4 * B, 'A4', .5), (4.0 + 4.6 * B, 'F#4', 1.0)]: tpt(t, p, ln, .34)   # under "most people say"
hit(8.5, 'X stamp: trumpet droop')
for t, p, ln, v in [(8.5, 'A4', .5, .55), (8.5 + .6 * B, 'G#4', .5, .5), (9.0, 'G4', .6, .48), (9.0 + .6 * B, 'F#4', 2.0, .42)]: tpt(t, p, ln, v)
add(stems['drums'], S.hit('sus_cymbal', 'hit', .3, 1.2), 8.5, .35, .3)
# 10–13: SILENCE (music out entirely)

# ================= STEPS 13–37: a chord per stamp, then the groove
PROG = [['Dmaj9', 'Bm9', 'Em9'], ['Bm9', 'Em9', 'A13'], ['Em9', 'A13', 'Dmaj9'], ['A13', 'Dmaj9', 'Gmaj7']]
LICK = [[('F#5', .5), ('E5', .5), ('C#5', .5), ('A4', 1.5)], [('D5', .5), ('C#5', .5), ('B4', .5), ('F#4', 1.5)],
        [('G5', .5), ('F#5', .5), ('D5', .5), ('B4', 1.5)], [('E5', .5), ('C#5', .5), ('B4', .5), ('G4', 1.5)]]
for i in range(4):
    t0 = 13.0 + 6.0 * i; ch = PROG[i][0]
    hit(t0, f'stamp {"STAR"[i]}: {ch}')
    vib(t0, V[ch], (3.2 if i == 2 else 2.2) * B, .62 if i != 2 else .7, hard=True, trem=.28)
    bass(t0, ROOT[ch], 1.6, .8)
    brush_sweep(t0, .5, .55)
    walk(t0 + BAR, PROG[i][1:], .56); comp(t0 + BAR, PROG[i][1], .24); comp(t0 + 2 * BAR, PROG[i][2], .24)
    brushes(t0, t0 + 6.0, .26 if i != 2 else .3)
    if i == 2: ride(t0 + BAR, t0 + 6.0, .2)        # Action: sticks on the cymbal for energy
    tt = t0 + 4.0 + .5 * B                            # flute answers in the third bar, after the line
    for p, ln in LICK[i]: flute(tt + jit(3), p, ln, .42); tt += ln * B
    bongo(t0 + 5.5, .35); bongo(t0 + 5.75, .3, var='muted')

# ================= PAYOFF 37–43: the four chords come back, one per medallion; up a step for the star
for i, ch in enumerate(['Dmaj9', 'Bm9', 'Em9', 'A13']):
    t = 37.5 + .5 * i; hit(t, f'medallion {"STAR"[i]} lands: {ch}')
    vib(t, V[ch], .9 * B if i < 3 else 2.6 * B, .5, hard=True, trem=.2)
    bass(t, ROOT[ch], .9, .7)
walk(39.0, ['Bm9'], .55); brushes(37.0, 41.0, .24); ride(39.0, 41.0, .2)
for t, p, ln in [(39.0, 'A5', 1.0), (39.5, 'F#5', .5), (39.8, 'E5', .5), (40.0, 'C#5', 1.0), (40.5, 'E5', 1.0)]: flute(t, p, ln, .45)
hit(41.0, 'star: up to E, gliss')
vib_run(40.6, ['B3', 'C#4', 'E4', 'F#4', 'G#4', 'B4', 'C#5', 'E5'], .05, .3, .6)
vib(41.0, V['Emaj9'] + ['B4'], 3 * B, .7, hard=True, trem=.3); bass(41.0, 'E2', 2.5, .8); flute(41.0, 'G#5', 2.6, .5)
add(stems['drums'], S.hit('sus_cymbal', 'cresc', .45), 40.2, .4, .3)
# 42.5–43: breath (nothing new)

# ================= CTA 43–49: half-time, gliss into the final chord, tails ring past the iris
hit(43.3, 'book thump: C#m9'); bass(43.3, 'C#2', 1.8, .7); vib(43.3, V['C#m9'], 2.4 * B, .4)
bass(44.0, 'F#1', 3.6, .6); vib(44.0, V['F#m9'], 3.4 * B, .3)
bass(46.0 - 2 * B, 'B1', 1.8, .6); vib(46.0 - 2 * B, V['B13'], 1.8 * B, .3)
snap(44.0 + 2 * B, .4); snap(44.0 + 6 * B, .4)
for t in np.arange(44.0, 46.0, BAR): brush_sweep(t, 4 * B, .22)
vib_run(45.55, ['E4', 'F#4', 'G#4', 'B4', 'C#5', 'D#5', 'E5', 'G#5'], .055, .25, .55)
hit(46.0, 'final Emaj9'); vib(46.0, V['Emaj9'] + ['B4', 'E5'], 6 * B, .55, hard=True, trem=.35); bass(46.0, 'E2', 4, .7)
flute(46.0, 'B5', 3.6, .38); add(stems['drums'], S.hit('sus_cymbal', 'hit', .25, 3.0), 46.0, .3, .3)

# ---------------- mix the stems
mix = stems['drums'] * .9 + stems['bass'] * 1.0 + stems['vib'] * .85 + stems['lead'] * .8
# hard silence 10.0–13.0 (stamp S is the first music after it); fade-out tail after 48.3
s0, s1 = int(10.0 * SR), int(13.0 * SR); f = int(.04 * SR)
mix[s0:s1] = 0; mix[s0 - f:s0] *= np.linspace(1, 0, f)[:, None]
e0 = int(48.2 * SR); mix[e0:] *= np.linspace(1, 0, N - e0)[:, None] ** 1.5
pk = np.abs(mix).max(); mix = mix / pk * .89
sf.write(os.path.join(OUT, 'score.wav'), mix.astype(np.float32), SR, subtype='FLOAT')
json.dump(sorted(hits, key=lambda h: h['t']), open(os.path.join(OUT, 'hits.json'), 'w'), indent=1)
with open(os.path.join(OUT, 'CREDITS_music.txt'), 'w') as fh: fh.write('\n'.join(S.credits(['vibraphone', 'vibraphone_hard', 'jazz_bass', 'flute', 'trumpet_mute', 'hihat', 'conga', 'sus_cymbal'])) + '\n')
print('score.wav', DUR, 's,', len(hits), 'hits')
