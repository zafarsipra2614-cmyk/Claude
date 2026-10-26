"""Swiss motion edition of the 0:34-1:09 section.
International Typographic Style: 12-column grid, flush-left grotesk type, hairline rules that draw on,
small tracked captions, big numerals, geometric bars and circles. Precise ease-in-out moves that land
on the beat; green is the single accent, red marks losses. No bounce, no shadows."""
import math, random
import cairo
import kt
from kin import *
from kt import FORCE_PATH, DUR, Layers

LIGHT = True
kt.FONTS.update(blk='Inter Display Black', med='Inter Display Medium', xb='Inter Display ExtraBold')
M = 96; CW = 122; GU = 24


def cx(i): return M + i * (CW + GU)          # left edge of column i (0..11)


CUR = [WHITE]


def bgfill(cr, c):
    cr.rectangle(-400, -400, W + 800, H + 800); col(cr, c); cr.fill(); CUR[0] = c


def fgc(): return INK if CUR[0] in (WHITE, GREEN) else WHITE


def rule(cr, x0, y, x1, p, w=3, c=None, a=1.0):
    if p <= 0: return
    cr.rectangle(x0, y - w / 2, (x1 - x0) * clamp(p), w); col(cr, c or fgc(), a); cr.fill()


def vrule(cr, x, y0, y1, p, w=3, c=None, a=1.0):
    if p <= 0: return
    cr.rectangle(x - w / 2, y0, w, (y1 - y0) * clamp(p)); col(cr, c or fgc(), a); cr.fill()


def tracked(cr, s_, x, y, size, c, a=1.0, track=0.12, fam='med', align='l'):
    font(cr, fam, size)
    advs = [cr.text_extents(ch).x_advance + size * track for ch in s_]
    total = sum(advs) - size * track
    xx = x if align == 'l' else x - total if align == 'r' else x - total / 2
    for ch, ad in zip(s_, advs):
        tx(cr, ch, xx, y, size, fam, c, a, 'l'); xx += ad
    return total


def cap(cr, s_, x, y, t, t_on, c=None, a=1.0, align='l', size=22):
    q = eio((t - t_on) / 0.3)
    if q <= 0: return
    tracked(cr, s_.upper(), x, y, size, c or fgc(), a * q, 0.14, 'med', align)


def big(cr, s_, x, y, size, c, t, t_on, align='l', fam='blk', a=1.0, dur=0.34):
    """Baseline mask reveal: the word rises out of its own baseline, precise ease-in-out."""
    if t < t_on - 0.01: return 0
    font(cr, fam, size); adv = cr.text_extents(s_).x_advance
    xx = x if align == 'l' else x - adv if align == 'r' else x - adv / 2
    q = eio((t - t_on) / dur)
    cr.save(); cr.rectangle(xx - 20, y - size * 0.85, adv + 40, size * 1.35); cr.clip()
    tx(cr, s_, xx, y + (1 - q) * size * 1.05, size, fam, c, a, 'l'); cr.restore()
    return adv


def counter(cr, t, x, y, c=None):
    """Bar position 1-4 as a large numeral + four squares (Swiss metronome)."""
    n = beat_no(t)
    for k in range(4):
        cr.rectangle(x + k * 30, y, 22, 22); col(cr, c or fgc(), 1 if k < n else 0.18); cr.fill()


def frame_meta(cr, t, label, t0):
    """Top hairline + running captions on every frame: section label, time code, KSE."""
    q = eio((t - t0) / 0.4)
    rule(cr, M, 132, W - M, q, 2)
    cap(cr, label, M, 100, t, t0)
    cap(cr, f"{t:05.2f}", W - M, 100, t, t0, align='r')


# ------------------------------------------------------------------ shots
def s_lowerlock(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE)
    frame_meta(cr, t, 'KSE-100  /  Circuit breaker', t0 - 0.1)
    big(cr, 'Lower', cx(0) - 8, 470, 300, RED, t, w[0])
    big(cr, 'lock', cx(0) - 8, 760, 300, RED, t, w[1])
    cap(cr, 'ne aisa', cx(8), 470, t, w[2], size=34)
    big(cr, 'maara.', cx(8), 600, 110, INK, t, w[4], fam='xb')
    # a single red bar collapsing on the beat (the index, as a Swiss bar chart)
    for k, b in enumerate(beats_between(w[0], t + 0.001)[:6]):
        pass
    hgt = lerp(560, 90, eio((t - w[4]) / 0.5))
    cr.rectangle(cx(10), 960 - hgt, CW * 2 + GU, hgt); col(cr, RED); cr.fill()
    cap(cr, '−7.50%', cx(10), 960 - hgt - 30, t, w[1], RED, size=26)
    rule(cr, M, 962, W - M, eio((t - t0) / 0.5), 2)


def s_stoploss(cr, t, t0):
    w = wt(t0); bgfill(cr, INK)
    frame_meta(cr, t, 'Order settings', t0)
    big(cr, 'Stop', cx(0) - 8, 420, 260, WHITE, t, w[0])
    big(cr, 'loss', cx(0) - 8, 670, 260, WHITE, t, w[1])
    font(cr, 'blk', 260); sw_ = cr.text_extents('loss').x_advance
    rule(cr, cx(0) - 20, 672, cx(0) + sw_ + 20, eio((t - w[3]) / 0.25), 20, GREEN)
    cap(cr, 'bhi bhool gaya', cx(6), 420, t, w[2], WHITE, size=34)
    big(cr, 'Bechara.', W - M, 880, 150, RED, t, w[5], 'r', 'xb')
    # geometric switch: circle slides one column left = off
    off = eio((t - w[3]) / 0.35)
    cr.rectangle(cx(9), 540, CW * 2 + GU, 4); col(cr, WHITE, 0.4); cr.fill()
    cr.arc(lerp(cx(10) + CW + GU, cx(9) + 40, off), 542, 40, 0, TAU); col(cr, mix(GREEN, (0.5, 0.5, 0.5), off)); cr.fill()
    cap(cr, 'off' if off > 0.5 else 'on', cx(9), 620, t, t0, RED if off > 0.5 else GREEN, size=26)


def s_buildup(cr, t, t0):
    t0, t_drop = 39.4, snap(43.4)
    if t < 41.45:   # modular grid fills one cell per half-beat; numerals count the build
        bgfill(cr, WHITE)
        frame_meta(cr, t, 'Build', 39.4)
        hb = half_beats(39.3, 41.5); n = len([h for h in hb if h <= t])
        for k in range(12):
            r, c_ = divmod(k, 6)
            x = cx(c_ * 2); y = 300 + r * (CW * 2 + GU)
            on = k < n
            q = eio((t - hb[k]) / 0.15) if on and k < len(hb) else 0
            cr.rectangle(x, y, CW * 2 + GU, CW * 2); col(cr, INK if k % 3 else GREEN, q); cr.fill()
            cr.rectangle(x, y, CW * 2 + GU, CW * 2); cr.set_line_width(2); col(cr, INK, 0.25); cr.stroke()
        tracked(cr, f"{n:02d}", W - M, 860, 200, INK, 1, -0.02, 'blk', 'r')
        cap(cr, 'Dramay baaz in', W - M, 960, t, 39.4, align='r', size=24)
        return
    marks = []
    for b in beats_between(41.4, t_drop):
        bi = BEATS.index(b); nb = BEATS[bi + 1] if bi + 1 < len(BEATS) else b + 0.47
        sub = 1 if b < 42.3 else 2 if b < 42.9 else 4
        marks += [b + (nb - b) * k / sub for k in range(sub)]
    marks = [m for m in marks if m < t_drop - 0.1] or [41.45]
    i = max(0, bisect.bisect_right(marks, t) - 1)
    inv = i % 2
    bgfill(cr, INK if inv else WHITE)
    word = ('Buy', 'Sell')[inv]; c = (GREEN, RED)[inv]
    q = eio((t - marks[i]) / 0.06)
    tracked(cr, word, cx(0) - 8, 600, 420, c, q, -0.03, 'blk')
    rule(cr, M, 760, W - M, clamp((t - 41.45) / (t_drop - 41.45)), 8, c)
    cap(cr, f"{len(marks[:i + 1]):02d} / {len(marks):02d}", W - M, 820, t, 41.45, align='r', size=30)
    fl = clamp((t - (t_drop - 0.1)) / 0.1)
    if fl > 0: cr.rectangle(0, 0, W, H); col(cr, WHITE, fl); cr.fill()


def s_chant(cr, t, t0):
    c_ = C(t0); t1 = c_[1]
    bs = [snap(t0)] + [b for b in BEATS if snap(t0) + 0.1 < b < t1]
    k = max(0, bisect.bisect_right(bs, t) - 1)
    bgfill(cr, GREEN)
    side = (k // 2) % 2   # composition alternates left / right every bar half
    cap(cr, 'Chorus', M, 100, t, bs[0], INK)
    rule(cr, M, 132, W - M, 1, 2, INK)
    counter(cr, t, W - M - 112, 92, INK)
    a1 = 'l' if side == 0 else 'r'; x1 = cx(0) - 8 if side == 0 else W - M
    big(cr, 'Dramay', x1, 560, 330, INK, t, bs[k - (k % 2)] if k % 2 else bs[k], a1, dur=0.18)
    if k % 2 == 1:
        big(cr, 'baaz!', x1, 900, 330, WHITE, t, bs[k], a1, dur=0.18)
    # vertical running title on the free edge
    cr.save(); cr.translate(W - M - 10 if side == 0 else M + 30, 980); cr.rotate(-math.pi / 2)
    tracked(cr, 'DRAMAY BAAZ  —  FLOSTOCKS', 0, 0, 26, INK, 0.8, 0.2); cr.restore()
    r = 60 + 40 * beat_pulse(t, 8)
    cr.arc(cx(10) + CW if side == 0 else cx(1), 300, r, 0, TAU); col(cr, INK); cr.fill()


def s_green(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE)
    frame_meta(cr, t, 'Market  /  Up', t0)
    big(cr, 'Green', cx(0) - 8, 440, 360, GREEN, t, w[0])
    cap(cr, 'dekha toh', cx(0), 660, t, w[1], size=34)
    big(cr, 'naach', cx(0) - 8, 840, 220, INK, t, w[3], dur=0.25)
    big(cr, 'liya.', cx(4) + 40, 840, 220, INK, t, w[4], dur=0.25)
    for k in range(4):   # bars step up one per beat
        n = len(beats_between(w[0], t + 0.001))
        h = 120 + k * 110 if k < n else 0
        hh = h * eio((t - (beats_between(w[0], t + 1)[k] if k < len(beats_between(w[0], t + 1)) else t + 1)) / 0.2)
        cr.rectangle(cx(8) + k * (CW + GU), 960 - hh, CW, hh); col(cr, GREEN); cr.fill()
    rule(cr, cx(8), 962, W - M, eio((t - t0) / 0.4), 2)


def s_red(cr, t, t0):
    w = wt(t0); bgfill(cr, INK)
    frame_meta(cr, t, 'Market  /  Down', t0)
    big(cr, 'Red', cx(0) - 8, 460, 420, RED, t, w[0])
    cap(cr, 'dekha toh', cx(0), 720, t, w[1], WHITE, size=34)
    # "bhaag liya" steps out one column per beat
    nb = len(beats_between(w[3] + 0.3, t + 0.001))
    shift = (nb + eio((t - (beats_between(w[3] + 0.3, t + 1)[nb] if nb < len(beats_between(w[3] + 0.3, t + 1)) else t)) / 0.2) * 0) * (CW + GU) * 2
    cr.save(); cr.translate(shift, 0)
    big(cr, 'bhaag liya.', cx(0), 860, 150, WHITE, t, w[3], fam='xb')
    cr.restore()
    for k in range(4):
        h = 520 - k * 120
        cr.rectangle(cx(8) + k * (CW + GU), 960 - h * eio((t - t0 - k * 0.1) / 0.3), CW, h * eio((t - t0 - k * 0.1) / 0.3)); col(cr, RED); cr.fill()
    rule(cr, M, 962, W - M, eio((t - t0) / 0.4), 2)


def s_gussa(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE)
    frame_meta(cr, t, 'Screen', t0)
    cap(cr, 'screen pe', cx(0), 260, t, w[0], size=34)
    sc = 1 + 0.05 * dhol(t)
    cr.save(); cr.translate(cx(0), 640); cr.scale(sc, sc); cr.translate(-cx(0), -640)
    big(cr, 'Gussa', cx(0) - 8, 640, 430, RED, t, w[2]); cr.restore()
    cap(cr, 'jhaad liya', cx(0), 780, t, w[3], size=34)
    # crosshair rules jolt on each dhol hit
    nh = len([h for h in DHOL_T if w[2] <= h <= t])
    for k in range(min(nh, 8)):
        y = 300 + (k * 97) % 600
        rule(cr, cx(8), y, W - M, 1, 3, RED, 0.8)
    cr.arc(cx(10), 540, 140 + 30 * dhol(t), 0, TAU); cr.set_line_width(3); col(cr, INK); cr.stroke()


def s_buy(cr, t, t0):
    w = wt(t0); bgfill(cr, INK)
    frame_meta(cr, t, 'Order  /  Buy', t0)
    cap(cr, 'bina soche', cx(0), 300, t, w[0], WHITE, size=34)
    big(cr, 'Buy', cx(0) - 12, 760, 520, GREEN, t, w[2], dur=0.22)
    big(cr, 'kiya.', cx(6), 760, 160, WHITE, t, w[3], fam='xb')
    for k in range(3):
        vrule(cr, cx(10) + k * 60, 760 - 100 * k, 300, eio((t - w[2] - k * 0.1) / 0.4), 6, GREEN)


def s_sell(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE)
    frame_meta(cr, t, 'Order  /  Sell', t0)
    cap(cr, 'dar ke phir', W - M, 300, t, w[0], align='r', size=34)
    big(cr, 'Sell', W - M + 12, 760, 520, RED, t, w[3], 'r', dur=0.22)
    big(cr, 'kiya.', cx(4), 760, 160, INK, t, w[4], 'r', fam='xb')
    for k in range(3):
        vrule(cr, cx(1) - k * 60, 300, 400 + 140 * k, eio((t - w[3] - k * 0.1) / 0.4), 6, RED)


def s_cry(cr, t, t0):
    w = wt(t0); bgfill(cr, INK)
    frame_meta(cr, t, 'Portfolio', t0)
    cap(cr, 'baith ke phir', cx(0), 300, t, w[0], WHITE, size=34)
    steps = len(beats_between(w[3] + 0.4, t + 0.001))   # sinks one baseline step per beat
    drop = steps * 24
    big(cr, 'ro liya.', cx(0) - 8, 640 + drop, 300, WHITE, t, w[3])
    pts = [(cx(7) + k * 14, 300 + (k / 50) ** 1.6 * 560 * eio((t - t0) / 3)) for k in range(51)]
    line(cr, pts, 4, RED)


SHOTS = dict(lowerlock=s_lowerlock, stoploss=s_stoploss, buildup=s_buildup, chant=s_chant, green=s_green, red=s_red,
             gussa=s_gussa, buy=s_buy, sell=s_sell, cry=s_cry, end=lambda cr, t, r: bgfill(cr, WHITE))


# ------------------------------------------------------------------ transitions: precise, grid-based
def t_push(cr, q, A, B, a, b):
    e = eio(q)
    paint(cr, A, 1, lambda c: c.translate(-W * e, 0)); paint(cr, B, 1, lambda c: c.translate(W * (1 - e), 0))


def t_columns(cr, q, A, B, a, b):
    paint(cr, A)
    cr.save()
    for i in range(12):
        p = eio(q * 1.8 - i * 0.07)
        cr.rectangle(cx(i) - GU / 2, 0, CW + GU + 1, H * p)
    cr.clip(); cr.set_source(B); cr.paint(); cr.restore()


def t_band(cr, q, A, B, a, b):
    paint(cr, A)
    e = eio(q)
    cr.save(); cr.rectangle(0, 0, W, H * e); cr.clip(); cr.set_source(B); cr.paint(); cr.restore()
    cr.rectangle(0, H * e - 3, W, 6); col(cr, GREEN); cr.fill()


def t_flash(cr, q, A, B, a, b):
    paint(cr, B if q >= 0.5 else A)
    cr.rectangle(0, 0, W, H); col(cr, WHITE, 1 - abs(q - 0.5) * 2); cr.fill()


def t_cut(cr, q, A, B, a, b): paint(cr, B if q >= 0.5 else A)


TRANS = dict(default=t_push, stoploss=t_columns, buildup=t_band, chant=t_cut, green=t_columns, red=t_push, gussa=t_band,
             buy=t_columns, sell=t_push, cry=t_band, end=t_flash)
RUN = Runner(SHOTS, TRANS, 0.34)


def render(L, t):
    kt.BEAT_T[0] = t
    c = L.fg
    L.bg.rectangle(0, 0, W, H); col(L.bg, WHITE); L.bg.fill()
    RUN.trans['chant'] = t_flash if abs(t - snap(43.4)) < 0.3 else t_cut
    RUN.frame(c, t)
    c.identity_matrix()
    if CUR[0] != GREEN:
        brand_img(L.ui, 'wordmark', W - M - 115, 1030, 210, 0.95, dark=(CUR[0] == INK))
