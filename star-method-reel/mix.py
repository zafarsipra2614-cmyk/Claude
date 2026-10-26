"""Mix: score + narration + foley by material + room tone -> out/mix.wav
Run: $LIB/.venv/bin/python mix.py   (needs events.json, voices/, music/score.wav)
Silences: 10.0–10.75 everything but room tone is gone (before the turn); 42.5–43.0 a breath with room tone only."""
import sys, os, json
LIB = os.environ.get('LIB', os.path.expanduser('~/lemo-opuscar'))
sys.path.insert(0, LIB)
import numpy as np, soundfile as sf, soxr
from core.audio.sfx import SR, t_, env_exp, bp, lp, hp, norm, brown, clack, whoosh, thump, ding, pop, add, compress
D = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(D, 'events.json')))
DUR = E['dur']; N = int(round(DUR * SR)); EV = E['ev']; BEAT = 0.5
rng = np.random.default_rng(11)
def nz(d): return rng.standard_normal(len(t_(d)))
def sine(f, d): return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, len(t_(d))).astype(float)) / SR)
def M(*xs): n = max(len(x) for x in xs); return sum(np.pad(x, (0, n - len(x))) for x in xs)

# ---------------- foley
def stamp():            # rubber stamp on card: damped thud + paper smack
    d = .3; tt = t_(d); return norm(sine(140 * (1 - .4 * tt), d) * env_exp(d, .035) + lp(nz(d), 1800) * env_exp(d, .012) * .9)
def paper_swish(d=.3): return norm(bp(nz(d), 1800, 8000)) * np.sin(np.pi * t_(d) / d) ** 2
def pen(d=.5): x = bp(nz(d), 2000, 7000) * (0.5 + .5 * np.abs(np.sin(2 * np.pi * 11 * t_(d)))); return norm(x) * np.sin(np.pi * t_(d) / d)
def pip(n): d = .2; f = [1046.5, 1318.5, 1568, 2093][n]; return norm(sine(f, d) * env_exp(d, .06) * np.minimum(1, t_(d) / .004) + sine(f * 2.01, d) * env_exp(d, .03) * .2)
def balloon(): d = .25; return norm(M(paper_swish(.18) * .6, sine(520 * (1 + 1.2 * t_(d)), d) * env_exp(d, .05) * .5))
def cloth(): d = .3; return norm(lp(nz(d), 2500)) * np.sin(np.pi * t_(d) / d) ** 1.5
def gulp(): d = .22; tt = t_(d); return norm(sine(300 - 500 * tt, d) * env_exp(d, .06) + lp(nz(d), 600) * env_exp(d, .02) * .3)
def slide_whistle(d=.45): f = np.linspace(600, 1500, len(t_(d))); return norm(sine(f * (1 + .012 * np.sin(2 * np.pi * 6 * t_(d))), d)) * np.sin(np.pi * t_(d) / d) ** .6
def tap(): d = .08; return norm(M(lp(nz(d), 2000) * env_exp(d, .006), sine(900, d) * env_exp(d, .01) * .4))
def iris(d): tt = t_(d); return norm(bp(nz(d), 1000, 6000) * np.linspace(1, .2, len(tt))) * np.sin(np.pi * tt / d)
def ting(): d = 1.2; tt = t_(d); return norm(sum(sine(f, d) * env_exp(d, .5 / k) * a for k, (f, a) in enumerate([(2637, 1), (3951, .5), (5274, .3)], 1)))
def book_thump(): return norm(M(thump(.8, 90)[:int(.3 * SR)], paper_swish(.15) * .4))
def wood_tick(): return norm(clack(1.1, 1)[:int(.1 * SR)])

fx = np.zeros((N, 2)); vo = np.zeros((N, 2)); amb = np.zeros((N, 2))
for e in EV:
    t, ty, g = e['t'], e['type'], e.get('gain', 1.0)
    if ty == 'vo': continue
    if ty == 'stamp': add(fx, stamp(), t, .75 * g, -.05)
    elif ty == 'pop': add(fx, pop(1), t, .32 * g, .2)
    elif ty == 'pen': add(fx, pen(e.get('dur', .5)), t, .16, -.25)
    elif ty == 'swish': add(fx, paper_swish(.32), t, .32 * g, .3)
    elif ty == 'slide': add(fx, paper_swish(.22), t, .16, -.4)
    elif ty == 'whoosh': add(fx, whoosh(e.get('dur', .35), 1), t, .22 * g, .4)
    elif ty == 'balloon': add(fx, balloon(), t, .3, .3)
    elif ty == 'cloth': add(fx, cloth(), t, .2, -.1)
    elif ty == 'gulp': add(fx, gulp(), t, .3)
    elif ty == 'pip': add(fx, pip(e.get('n', 0)), t, .22, -.3 + .2 * e.get('n', 0))
    elif ty == 'iris': add(fx, iris(e.get('dur', .5)), t, .22)
    elif ty == 'whistle': add(fx, slide_whistle(), t, .2, .4)
    elif ty == 'tap': add(fx, tap(), t, .45, .4)
    elif ty == 'ting': add(fx, ting(), t, .2 * g, .1)
    elif ty == 'thump': add(fx, book_thump(), t, .7)

# ---------------- narration: compressed, on top
venv = np.zeros(N)
for e in EV:
    if e['type'] != 'vo': continue
    y, sr = sf.read(os.path.join(D, 'voices', e['id'] + '.wav'))
    if y.ndim > 1: y = y.mean(1)
    y = soxr.resample(y, sr, SR)
    y = compress(norm(y, .9), thr=.3, ratio=3.0)
    add(vo, y, e['t'], .9, 0)
    s = int(e['t'] * SR); venv[s:s + len(y)] = 1

# ---------------- ambience: warm room tone + a quiet mantel clock on the half-note grid
room = lp(brown(DUR), 900) * .018
amb += np.stack([room, np.roll(room, 311)], 1)
for k in range(int(DUR / (2 * BEAT))):
    t = k * 2 * BEAT
    if 10.0 <= t < 13.0 or t >= 48.0: continue
    add(amb, wood_tick(), t, .03, -.6)

# ---------------- music, ducked ~8 dB under the voice
mus, msr = sf.read(os.path.join(D, 'music', 'score.wav'))
if msr != SR: mus = soxr.resample(mus, msr, SR)
mus = mus[:N] if len(mus) >= N else np.pad(mus, ((0, N - len(mus)), (0, 0)))
k = int(.12 * SR); sm = np.convolve(venv, np.ones(k) / k, 'same')
mus = mus * (1 - sm * (1 - 10 ** (-8 / 20)))[:, None]

def gate(buf, a, b, keep=0.0, fade=.03):
    s, e = int(a * SR), int(b * SR); f = int(fade * SR); m = np.ones(N); m[s:e] = keep
    m[max(0, s - f):s] = np.linspace(1, keep, min(f, s)); m[e:e + f] = np.linspace(keep, 1, len(m[e:e + f])); buf *= m[:, None]
gate(fx, 10.0, 10.74); gate(mus, 42.5, 43.0, keep=.15, fade=.12)
gate(fx, 42.5, 43.0)

# ---------------- balance: voice ~10 dB above music by RMS where both play
def rms(x, m=None): x = x if m is None else x[m]; return np.sqrt(np.mean(x ** 2) + 1e-12)
vm = venv > 0
gv = 1.0; gm = rms(vo, vm) / (rms(mus, vm) * 10 ** (10 / 20)) if rms(mus, vm) > 0 else 1
out = vo * gv + mus * gm + fx * .9 + amb
out = out / np.abs(out).max() * .9
os.makedirs(os.path.join(D, 'out'), exist_ok=True)
# 13 s of trailing silence: mux.sh trims to the picture, and some ffmpeg builds report loudnorm progress ~3 s short
out = np.pad(out, ((0, 13 * SR), (0, 0)))
sf.write(os.path.join(D, 'out', 'mix.wav'), out.astype(np.float32), SR, subtype='PCM_24')
print('mix.wav', DUR, 's  music gain', round(float(gm), 3))
