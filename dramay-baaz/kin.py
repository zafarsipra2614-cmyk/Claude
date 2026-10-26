"""Shared engine for the kinetic lyric video styles (nb = neubrutalism, sw = swiss motion).
Timing: per-word times (prefers the vocal-isolated alignment if present), beat grid, dhol/clap hits.
Timeline: shots keyed by lyric line / chant; each style module supplies the shot drawings + transitions."""
import json, math, bisect, os
import cairo
import kt
from kt import tx, tw, font, rr, col, line, hexc
from lib import W, H, BEATS, beat_pulse, beat_index, beat_phase, env, clamp, lerp, mix, TAU, brand_img
from scenes import LYRICS, LYR_END, CHANTS, DB, NO

_tf = 'audio/word_times_final.json' if os.path.exists('audio/word_times_final.json') else 'audio/word_times_vocal.json'
VT = {float(k): v for k, v in json.load(open(_tf)).items()}
RH = json.load(open('audio/rhythm.json'))
DHOL = [h for h in RH['dhol'] if h[1] >= 0.7]; DHOL_T = [h[0] for h in DHOL]; DHOL_S = [h[1] for h in DHOL]
CLAP_T = [h[0] for h in RH['clap'] if h[1] >= 0.8]

INK = hexc('#0A0E0A'); WHITE = (1, 1, 1); GREEN = hexc('#38D100'); GDEEP = hexc('#1F7A00'); RED = hexc('#E5484D')
GOLD = hexc('#E6A817'); FOREST = hexc('#062600')


def ex(x):
    x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0


def sm(x):
    x = clamp(x); return x * x * x * (x * (6 * x - 15) + 10)


def eio(x):
    x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def ein(x): x = clamp(x); return x * x * x


def back(x, s=1.6):
    x = clamp(x) - 1; return x * x * ((s + 1) * x + s) + 1


def hit_env(t, times, strengths=None, decay=11.0, window=0.4):
    i = bisect.bisect_right(times, t) - 1; v = 0.0
    while i >= 0 and t - times[i] < window:
        v = max(v, (strengths[i] if strengths else 1.0) * math.exp(-(t - times[i]) * decay)); i -= 1
    return v


def dhol(t): return hit_env(t, DHOL_T, DHOL_S)


def clap(t): return hit_env(t, CLAP_T, None, 16.0, 0.25)


def snap(x, tol=0.12):
    i = bisect.bisect_left(BEATS, x)
    best = min((BEATS[j] for j in (i - 1, i) if 0 <= j < len(BEATS)), key=lambda g: abs(g - x), default=x)
    return best if abs(best - x) <= tol else x


def beats_between(a, b): return [x for x in BEATS if a <= x < b]


def half_beats(a, b):
    out = []
    for x in beats_between(a - 0.6, b):
        i = BEATS.index(x); nx = BEATS[i + 1] if i + 1 < len(BEATS) else x + 0.47
        out += [x, (x + nx) / 2]
    return [g for g in out if a <= g < b]


def wt(t0): return VT[t0]


def beat_no(t):
    """1..4 position inside the bar (for counters)."""
    return beat_index(t) % 4 + 1


def C(t0): return [c for c in CHANTS if c[0] == t0][0]


# sample section: 0:34 - 1:09 (lower lock, build-up, drop, chorus 1)
def line_start(t0): return snap(wt(t0)[0] - 0.12, 0.1)


SECTION = [
    (line_start(34.8), 'lowerlock', 34.8), (line_start(36.6), 'stoploss', 36.6), (39.4, 'buildup', None),
    (snap(43.4), 'chant', 43.4), (line_start(45.5), 'green', 45.5), (snap(47.2), 'chant', 47.2), (line_start(49.3), 'red', 49.3),
    (snap(51.0), 'chant', 51.0), (line_start(52.0), 'gussa', 52.0), (snap(54.6), 'chant', 54.6), (line_start(57.7), 'buy', 57.7),
    (line_start(59.8), 'sell', 59.8), (line_start(61.5), 'cry', 61.5), (snap(65.7), 'chant', 65.7), (69.45, 'end', None),
]


class Runner:
    """Plays a list of shots; around each cut both neighbours are rendered and blended by the style's transition."""

    def __init__(self, shots, transitions, td=0.3, start=34.4):
        self.shots, self.trans, self.td = shots, transitions, td
        self.tl = [s for s in SECTION if s[0] >= start - 0.5]
        self.starts = [s[0] for s in self.tl]

    def draw(self, cr, i, t):
        _, key, ref = self.tl[i]
        self.shots[key](cr, t, ref)

    def frame(self, cr, t):
        i = max(0, bisect.bisect_right(self.starts, t) - 1)
        j = None
        if i + 1 < len(self.tl) and self.starts[i + 1] - t < self.td / 2: j = i + 1
        elif t - self.starts[i] < self.td / 2 and i > 0: j = i
        if j is None:
            self.draw(cr, i, t); return
        q = clamp((t - (self.starts[j] - self.td / 2)) / self.td)
        cr.push_group(); self.draw(cr, j - 1, t); A = cr.pop_group()
        cr.push_group(); self.draw(cr, j, t); B = cr.pop_group()
        kind = self.trans.get(self.tl[j][1], self.trans.get('default'))
        kind(cr, q, A, B, self.tl[j - 1][1], self.tl[j][1])


def paint(cr, p, a=1.0, fn=None):
    cr.save()
    if fn: fn(cr)
    cr.set_source(p); cr.paint_with_alpha(a); cr.restore()
