"""Dramay Baaz, Bollywood-energy kinetic lyric video (text + graphics, no characters).
Brand palette only: ink black, white, FloStocks green; red for losses; a touch of gold.
Every lyric line is a designed composition (key word huge, support words small); every line change
is a beat-locked transition; dhol hits punch, claps flash, and instrumentals get their own choreography.
Exposes render(L, t), Layers, LIGHT, DUR, FORCE_PATH for render_kt.py (VIDEO=bw)."""
import json, math, random, bisect
import cairo
import kt
from kt import Layers, rr, col, tx, tw, font, line, check, strike, hexc, FORCE_PATH, DUR
from lib import W, H, BEATS, beat_pulse, beat_index, beat_phase, env, clamp, lerp, mix, TAU, brand_img
from scenes import LYRICS, LYR_END, CHANTS, DB, NO

LIGHT = True
INK = hexc('#0A0E0A'); WHITE = (1, 1, 1); PAPER = hexc('#FBFDFC'); GREEN = hexc('#38D100'); GDEEP = hexc('#1F7A00')
RED = hexc('#E5484D'); GOLD = hexc('#E6A817'); FOREST = hexc('#062600')
VT = {float(k): v for k, v in json.load(open('audio/word_times_vocal.json')).items()}
RH = json.load(open('audio/rhythm.json'))
DHOL = [h for h in RH['dhol'] if h[1] >= 0.7]
DHOL_T = [h[0] for h in DHOL]
CLAP = [h for h in RH['clap'] if h[1] >= 0.8]
CLAP_T = [h[0] for h in CLAP]


# ------------------------------------------------------------------ easing & rhythm
def ex(x):
    x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0


def sm(x):
    x = clamp(x); return x * x * x * (x * (6 * x - 15) + 10)


def ein(x):
    x = clamp(x); return x * x * x


def hit_env(t, times, strengths=None, decay=11.0, window=0.4):
    i = bisect.bisect_right(times, t) - 1; v = 0.0
    while i >= 0 and t - times[i] < window:
        s = strengths[i] if strengths else 1.0
        v = max(v, s * math.exp(-(t - times[i]) * decay)); i -= 1
    return v


def dhol(t): return hit_env(t, DHOL_T, [h[1] for h in DHOL])


def clap(t): return hit_env(t, CLAP_T, None, 16.0, 0.25)


def snap(x, tol=0.12):
    i = bisect.bisect_left(BEATS, x)
    best = min((BEATS[j] for j in (i - 1, i) if 0 <= j < len(BEATS)), key=lambda g: abs(g - x), default=x)
    return best if abs(best - x) <= tol else x


def beats_between(a, b): return [x for x in BEATS if a <= x < b]


def wt(t0): return VT[t0]


# ------------------------------------------------------------------ type helpers
F = {'xb': 'Manrope XB', 'b': 'Manrope B', 'm': 'Manrope M'}
kt.FONTS.update(F)


CUR_BG = [None]


def bg(cr, c): cr.rectangle(-400, -400, W + 800, H + 800); col(cr, c); cr.fill(); CUR_BG[0] = c


def glint(cr, s_, x, y, size, t, t0, align='l', c=WHITE, a=0.85, fam='xb'):
    """A light sweep travelling across a word once (premium sheen)."""
    q = (t - t0) / 0.45
    if q <= 0 or q >= 1: return
    font(cr, fam, size); adv = cr.text_extents(s_).x_advance
    xx = x - adv / 2 if align == 'c' else x if align == 'l' else x - adv
    cr.save(); cr.move_to(xx, y + size * 0.36); cr.text_path(s_); cr.clip()
    gx = xx - size + (adv + 2 * size) * sm(q)
    g = cairo.LinearGradient(gx - size * 0.5, 0, gx + size * 0.5, 0)
    g.add_color_stop_rgba(0, *c, 0); g.add_color_stop_rgba(0.5, *c, a); g.add_color_stop_rgba(1, *c, 0)
    cr.rectangle(xx - 10, y - size, adv + 20, size * 2); cr.set_source(g); cr.fill(); cr.restore()


def word_in(cr, s_, x, y, size, c, t, t_on, style='rise', align='l', a=1.0, fam='xb'):
    """Reveal styles: rise (masked slide up), punch (scale-in impact + sheen), drop, wipe, type."""
    if t < t_on - 0.02 or a <= 0: return
    font(cr, fam, size); adv = cr.text_extents(s_).x_advance
    xx = x - adv / 2 if align == 'c' else x if align == 'l' else x - adv
    if style == 'rise':
        q = ex((t - t_on) / 0.32)
        cr.save(); cr.rectangle(xx - 20, y - size * 0.62, adv + 40, size * 1.25); cr.clip()
        tx(cr, s_, xx, y + (1 - q) * size * 1.1, size, fam, c, a, 'l'); cr.restore()
    elif style == 'punch':
        q = ex((t - t_on) / 0.22); sc = lerp(1.45, 1.0, q)
        cx = xx + adv / 2
        cr.save(); cr.translate(cx, y); cr.scale(sc, sc); tx(cr, s_, 0, 0, size, fam, c, a * clamp(q * 2.5)); cr.restore()
        glint(cr, s_, xx, y, size, t, t_on + 0.12, 'l', WHITE if c != WHITE else GREEN, 0.7, fam)
    elif style == 'drop':
        q = ex((t - t_on) / 0.3)
        tx(cr, s_, xx, y - (1 - q) * 220, size, fam, c, a * clamp(q * 2), 'l')
    elif style == 'wipe':
        q = sm((t - t_on) / 0.3)
        cr.save(); cr.rectangle(xx - 10, y - size, (adv + 20) * q, size * 2); cr.clip(); tx(cr, s_, xx, y, size, fam, c, a, 'l'); cr.restore()
    return adv


def letters(cr, s_, x, y, size, c, t, t_on, mode, align='l', a=1.0):
    """Per-letter motion: bounce (dances on the beat), run (exits right), sink (droops), shake (on dhol)."""
    font(cr, 'xb', size)
    advs = [cr.text_extents(ch).x_advance for ch in s_]; total = sum(advs)
    xx = x - total / 2 if align == 'c' else x if align == 'l' else x - total
    q0 = ex((t - t_on) / 0.3)
    for k, ch in enumerate(s_):
        cx = xx + sum(advs[:k]); dx = dy = rot = 0; aa = a * clamp((t - t_on - k * 0.025) / 0.12)
        if mode == 'bounce':
            ph = beat_phase(t); up = abs(math.sin(ph * math.pi))
            dy = -(1 - up) * size * 0.12 * (1 if (k + beat_index(t)) % 2 else 0.4)
            dy += (1 - q0) * size * 0.8
        elif mode == 'run':
            go = ein((t - t_on - 0.55 - k * 0.03) / 0.55)
            dx = go * 1700; aa *= 1 - go * 0.6
            for tr in range(1, 4):
                if go > 0.02: tx(cr, ch, cx + dx - tr * 50 * go * 2, y, size, 'xb', c, aa * 0.15 / tr, 'l')
        elif mode == 'sink':
            s2 = sm((t - t_on - 0.3 - k * 0.05) / 1.6)
            dy = s2 * size * (0.25 + 0.35 * ((k * 37) % 5) / 5); rot = s2 * (0.12 if k % 2 else -0.08)
            dy += (1 - q0) * -size * 0.6
        cr.save(); cr.translate(cx + advs[k] / 2 + dx, y + dy); cr.rotate(rot); tx(cr, ch, 0, 0, size, 'xb', c, aa); cr.restore()


# ------------------------------------------------------------------ market graphics
def candles(cr, x0, base, w, hmax, t, n=14, up=True, c=GREEN, a=1.0, grow_on=None, seed=2, hits=True):
    rnd = random.Random(seed); bw = w / n
    for k in range(n):
        trend = (k / (n - 1)) if up else (1 - k / (n - 1))
        h = hmax * (0.18 + 0.75 * trend + 0.12 * rnd.random())
        if grow_on is not None: h *= sm((t - grow_on - k * 0.05) / 0.5)
        if hits: h *= 1 + 0.12 * dhol(t - k * 0.01)
        bx = x0 + k * bw + bw * 0.2; cc = c if rnd.random() > 0.18 else (RED if c == GREEN else GREEN)
        line(cr, [(bx + bw * 0.3, base - h - 20), (bx + bw * 0.3, base + 14)], 3, cc, a)
        rr(cr, bx, base - h, bw * 0.6, h * 0.8, 4); col(cr, cc, a); cr.fill()


def arrow(cr, x, y, s, c, a=1.0, down=False):
    cr.save(); cr.translate(x, y); cr.scale(s, -s if down else s)
    cr.move_to(0, -60); cr.line_to(50, -6); cr.line_to(18, -6); cr.line_to(18, 60); cr.line_to(-18, 60); cr.line_to(-18, -6); cr.line_to(-50, -6)
    cr.close_path(); col(cr, c, a); cr.fill(); cr.restore()


def ticker_band(cr, y, h, t, c_bg, c_tx, items, speed=260, a=1.0, rot=0.0):
    cr.save(); cr.translate(W / 2, y); cr.rotate(rot); cr.translate(-W / 2, -y)
    cr.rectangle(-300, y - h / 2, W + 600, h); col(cr, c_bg, a); cr.fill()
    s_ = '   ·   '.join(items) + '   ·   '
    font(cr, 'xb', h * 0.48); adv = cr.text_extents(s_).x_advance
    x = -((t * speed) % adv) - 300
    while x < W + 300:
        tx(cr, s_, x, y, h * 0.48, 'xb', c_tx, a, 'l'); x += adv
    cr.restore()


def crack(cr, cx, cy, t, t0, c=WHITE, a=0.6):
    """Glass-crack lines that grow one burst per dhol hit."""
    n_hits = len([h for h in DHOL_T if t0 <= h <= t])
    rnd = random.Random(11)
    for k in range(min(18, n_hits * 3)):
        ang = rnd.random() * TAU; L_ = 220 + rnd.random() * 520
        pts = [(cx, cy)]
        for j in range(1, 5):
            pts.append((cx + math.cos(ang + rnd.uniform(-.25, .25)) * L_ * j / 4, cy + math.sin(ang + rnd.uniform(-.25, .25)) * L_ * j / 4))
        line(cr, pts, 3, c, a)


def toggle(cr, x, y, s, off, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    rr(cr, -110, -60, 220, 120, 60); col(cr, mix(GREEN, (0.75, 0.76, 0.75), off), a); cr.fill()
    cr.arc(lerp(50, -50, off), 0, 48, 0, TAU); col(cr, WHITE, a); cr.fill()
    cr.restore()


# ------------------------------------------------------------------ shots
# each shot draws a full frame (its own background) for time t; transitions blend neighbouring shots
def shot_lowerlock(cr, t):
    t0 = 34.8; w = wt(t0)
    bg(cr, INK)
    # the big red candle smashes down on "maara"
    q = ein((t - w[4] + 0.1) / 0.3)
    cy = lerp(-900, 120, q)
    rr(cr, 1560, cy, 170, 640, 10); col(cr, RED, 0.9 if q > 0 else 0); cr.fill()
    line(cr, [(1645, cy - 120), (1645, cy + 780)], 6, RED, 0.9 if q > 0 else 0)
    word_in(cr, 'LOWER', 130, 290, 250, RED, t, w[0], 'punch')
    word_in(cr, 'LOCK', 130, 530, 250, RED, t, w[1], 'punch')
    word_in(cr, 'ne aisa', 140, 740, 80, WHITE, t, w[2], 'rise')
    word_in(cr, 'MAARA', 140 + tw(cr, 'ne aisa ', 'xb', 80), 725, 140, WHITE, t, w[4], 'drop')
    if t > w[1]:
        ticker_band(cr, 945, 80, t, RED, WHITE, ['KSE-100  ▼ −7.50%', 'LOWER LOCK', 'TIPWALA LTD  ▼ −7.50%', 'CIRCUIT BREAKER'],
                    300, ex((t - w[1]) / 0.4), -0.025)


def shot_stoploss(cr, t):
    t0 = 36.6; w = wt(t0)
    bg(cr, PAPER)
    word_in(cr, 'STOP', 140, 330, 230, INK, t, w[0], 'punch')
    word_in(cr, 'LOSS', 140 + tw(cr, 'STOP ', 'xb', 230), 330, 230, INK, t, w[1], 'punch')
    sw = tw(cr, 'STOP LOSS', 'xb', 230)
    strike(cr, 120, 340, 160 + sw, 320, sm((t - w[3]) / 0.35), RED, 22)
    word_in(cr, 'bhi bhool gaya', 150, 540, 90, INK, t, w[2], 'rise')
    letters(cr, 'BECHARA', 140, 760, 190, RED, t, w[5], 'sink')
    off = sm((t - w[3]) / 0.35)
    toggle(cr, 1560, 640, 1.3 * ex((t - t0) / 0.5), off)
    tx(cr, 'OFF' if off > 0.5 else 'ON', 1560, 800, 60, 'xb', RED if off > 0.5 else GDEEP, ex((t - t0) / 0.5))


def shot_buildup(cr, t):
    """39.4 - 43.4: instrumental build. Each dhol hit lights a letter of the coming chant, then BUY/SELL
    flip faster and faster while the frame pushes in, and a white flash drops us into the chorus."""
    t0, t_drop = 39.4, snap(43.4)
    if t < 41.5:
        bg(cr, INK)
        candles(cr, 80, 1000, 1760, 300 + 200 * clamp((t - t0) / 2), t, 26, True, GREEN, 0.35, hits=True, seed=5)
        grid = []
        for b in beats_between(t0 - 0.5, 41.6):
            bi = BEATS.index(b); nb = BEATS[bi + 1]; grid += [b, (b + nb) / 2]
        hits = [g for g in grid if t0 <= g <= t]
        word = 'DRAMAY BAAZ'
        font(cr, 'xb', 230); x = W / 2 - cr.text_extents(word).x_advance / 2
        lit = 0
        for k, ch in enumerate(word):
            adv = tw(cr, ch, 'xb', 230)
            if ch != ' ':
                on = lit < len(hits)
                cr.move_to(x, H / 2 - 40 + 230 * 0.36); cr.text_path(ch)
                if on:
                    p = ex((t - hits[lit]) / 0.2); col(cr, mix(WHITE, GREEN, 0.0), p); cr.fill()
                else:
                    cr.set_line_width(3); col(cr, WHITE, 0.25); cr.stroke()
                lit += 1
            x += adv
        return
    # acceleration: beats -> half beats -> quarter beats
    marks = []
    for b in beats_between(41.4, t_drop):
        bi = BEATS.index(b); nb = BEATS[bi + 1] if bi + 1 < len(BEATS) else b + 0.47
        sub = 1 if b < 42.3 else 2 if b < 42.9 else 4
        marks += [b + (nb - b) * k / sub for k in range(sub)]
    marks = [m for m in marks if m < t_drop - 0.12]
    i = max(0, bisect.bisect_right(marks, t) - 1)
    flip = i % 2
    push = 1 + 0.35 * ein((t - 41.4) / (t_drop - 41.4))
    bg(cr, PAPER if flip else INK)
    cr.save(); cr.translate(W / 2, H / 2); cr.scale(push, push); cr.translate(-W / 2, -H / 2)
    wd = 'BUY' if flip == 0 else 'SELL'
    cc = GREEN if wd == 'BUY' else RED
    q = ex((t - marks[i]) / 0.08) if marks else 1
    cr.save(); cr.translate(W / 2, H / 2); s_ = lerp(1.15, 1.0, q); cr.scale(s_, s_)
    tx(cr, wd, 0, 0, 380, 'xb', cc, 1); cr.restore()
    arrow(cr, W / 2 + (420 if wd == 'BUY' else 470), H / 2, 1.6, cc, 1, down=wd == 'SELL')
    cr.restore()
    fl = sm((t - (t_drop - 0.12)) / 0.12)
    if fl > 0: bg(cr, WHITE) if fl >= 1 else (cr.rectangle(0, 0, W, H), col(cr, WHITE, fl), cr.fill())


def chant_comp(cr, t, c_):
    """Full-bleed green stomps: one word per beat, layouts rotate each bar, dhol punches the type."""
    t0, t1, ph = c_
    bs = [snap(t0)] + [b for b in BEATS if snap(t0) + 0.1 < b < t1]
    k = max(0, bisect.bisect_right(bs, t) - 1)
    bg(cr, GREEN)
    ci = [c[0] for c in CHANTS].index(t0)
    lay = (k // 2 + ci) % 3
    punch = 1 + 0.06 * dhol(t)
    # diagonal ink band behind, slides each beat
    band_q = ex((t - bs[k]) / 0.25)
    cr.save(); cr.translate(W / 2, H / 2); cr.rotate(-0.08 if k % 2 else 0.06)
    cr.rectangle(-1400, -150 + (1 - band_q) * (60 if k % 2 else -60), 2800, 300); col(cr, INK, 0.92); cr.fill()
    cr.restore()
    w1, w2 = 'DRAMAY', 'BAAZ!'
    first = (k % 2 == 0)
    cur = w1 if first else w2
    cr.save(); cr.translate(W / 2, H / 2); cr.scale(punch, punch); cr.translate(-W / 2, -H / 2)
    q = ex((t - bs[k]) / 0.16)
    if lay == 0:
        cr.save(); cr.translate(W / 2, H / 2); s_ = lerp(1.3, 1, q); cr.scale(s_, s_)
        tx(cr, cur, 0, 0, 330 if first else 400, 'xb', WHITE if first else GREEN, 1); cr.restore()
    elif lay == 1:   # DRAMAY on the band, BAAZ! stamped in ink on the green underneath
        tx(cr, w1, W / 2, H / 2, 250, 'xb', WHITE, 1)
        if not first:
            cr.save(); cr.translate(W / 2, H / 2 + 300); s_ = lerp(1.4, 1, q); cr.scale(s_, s_); tx(cr, w2, 0, 0, 200, 'xb', INK, 1); cr.restore()
    else:
        x0 = W / 2 - tw(cr, 'DRAMAY BAAZ!', 'xb', 180) / 2
        tx(cr, w1, x0, H / 2, 180, 'xb', WHITE, 1 if first else 0.35, 'l')
        tx(cr, w2, x0 + tw(cr, 'DRAMAY ', 'xb', 180), H / 2, 180, 'xb', GREEN, 1 if not first else 0.25, 'l')
    glint(cr, cur, W / 2, H / 2, 300, t, bs[k] + 0.05, 'c', WHITE, 0.5)
    cr.restore()
    cl = clap(t)
    if cl > 0.05:
        cr.rectangle(0, 0, W, H); col(cr, WHITE, 0.12 * cl); cr.fill()


def shot_green(cr, t):
    t0 = 45.5 if t < 80 else 85.7; w = wt(t0)
    bg(cr, INK)
    candles(cr, 120, 1010, 1680, 520, t, 22, True, GREEN, 0.22, grow_on=t0, seed=7)
    word_in(cr, 'GREEN', W / 2, 360, 330, GREEN, t, w[0], 'punch', 'c')
    word_in(cr, 'dekha toh', W / 2, 560, 80, WHITE, t, w[1], 'rise', 'c')
    letters(cr, 'NAACH LIYA', W / 2, 740, 190, WHITE, t, w[3], 'bounce', 'c')


def shot_red(cr, t):
    t0 = 49.3 if t < 80 else 89.7; w = wt(t0)
    bg(cr, PAPER)
    for k in range(9):   # red candles tumbling down on the right
        fall = ein((t - t0 - k * 0.12) / 1.2)
        rr(cr, 1250 + k * 70, -300 + fall * 1400 + (k * 97) % 200, 34, 160 + (k * 53) % 120, 6); col(cr, RED, 0.35); cr.fill()
    word_in(cr, 'RED', 130, 430, 380, RED, t, w[0], 'punch')
    word_in(cr, 'dekha toh', 140, 700, 90, INK, t, w[1], 'rise')
    letters(cr, 'BHAAG LIYA', 140, 860, 170, INK, t, w[3], 'run')


def shot_gussa(cr, t):
    t0 = 52.0 if t < 80 else 92.4; w = wt(t0)
    bg(cr, INK)
    crack(cr, W / 2, H / 2, t, t0, WHITE, 0.35)
    word_in(cr, 'screen pe', W / 2, 270, 90, WHITE, t, w[0], 'rise', 'c')
    if t >= w[2] - 0.02:
        p = 1 + 0.08 * dhol(t)
        cr.save(); cr.translate(W / 2, H / 2 + 20); cr.scale(p, p); cr.translate(-W / 2, -(H / 2 + 20))
        word_in(cr, 'GUSSA', W / 2, H / 2 + 20, 380, RED, t, w[2], 'punch', 'c'); cr.restore()
    word_in(cr, 'jhaad liya', W / 2, 820, 90, WHITE, t, w[3], 'rise', 'c')


def shot_buy(cr, t):
    t0 = 57.7; w = wt(t0)
    bg(cr, PAPER)
    word_in(cr, 'bina soche', 150, 300, 100, INK, t, w[0], 'rise')
    word_in(cr, 'BUY', 140, 600, 430, GREEN, t, w[2], 'punch')
    word_in(cr, 'kiya', 150 + tw(cr, 'BUY', 'xb', 430) + 30, 720, 130, INK, t, w[3], 'rise')
    for k in range(4):
        arrow(cr, 1500 + k * 90, 560 - ((t - w[2]) * 400 + k * 80) % 300 + 120, 0.9, GREEN, 0.85 * ex((t - w[2]) / 0.3))


def shot_sell(cr, t):
    t0 = 59.8; w = wt(t0)
    bg(cr, INK)
    word_in(cr, 'dar ke phir', W - 150, 300, 100, WHITE, t, w[0], 'rise', 'r')
    word_in(cr, 'SELL', W - 140, 600, 430, RED, t, w[3], 'punch', 'r')
    word_in(cr, 'kiya', W - 150 - tw(cr, 'SELL', 'xb', 430) - 30, 720, 130, WHITE, t, w[4], 'rise', 'r')
    for k in range(4):
        arrow(cr, 200 + k * 90, 300 + ((t - w[3]) * 400 + k * 80) % 300, 0.9, RED, 0.85 * ex((t - w[3]) / 0.3), down=True)


def shot_cry(cr, t):
    t0 = 61.5; w = wt(t0)
    bg(cr, PAPER)
    rnd = random.Random(int(t * 30))
    for k in range(40):
        x = rnd.random() * W; y = rnd.random() * H
        line(cr, [(x, y), (x - 6, y + 46)], 2, (0.55, 0.6, 0.65), 0.35)
    pts = [(120 + k * 28, 300 + (k / 59) ** 1.7 * 560 * sm((t - t0) / 2.5) + 14 * math.sin(k * 0.9)) for k in range(60)]
    line(cr, pts, 6, RED, 0.5)
    word_in(cr, 'baith ke phir', W / 2, 330, 100, INK, t, w[0], 'rise', 'c')
    letters(cr, 'RO LIYA', W / 2, 600, 300, INK, t, w[3], 'sink', 'c')


# ------------------------------------------------------------------ timeline (sample: 34.8 - 69.5)
def chant_shot(c_):
    return lambda cr, t: chant_comp(cr, t, c_)


def C(t0): return [c for c in CHANTS if c[0] == t0][0]


TIMELINE = [  # (start, shot, transition into this shot)
    (34.6, shot_lowerlock, 'cut'),
    (snap(36.45), shot_stoploss, 'slats'),
    (39.4, shot_buildup, 'zoom'),
    (snap(43.4), chant_shot(C(43.4)), 'flash'),
    (snap(45.35), shot_green, 'bars'),
    (snap(47.2), chant_shot(C(47.2)), 'punch'),
    (snap(49.1) - 0.0, shot_red, 'whip'),
    (snap(51.0), chant_shot(C(51.0)), 'punch'),
    (snap(51.9), shot_gussa, 'split'),
    (snap(54.6), chant_shot(C(54.6)), 'punch'),
    (snap(57.55), shot_buy, 'bars'),
    (snap(59.7), shot_sell, 'whip_l'),
    (snap(61.4), shot_cry, 'slats'),
    (snap(65.7), chant_shot(C(65.7)), 'flash'),
    (69.45, None, 'cut'),
]
STARTS = [x[0] for x in TIMELINE]
TD = 0.3   # transition length (seconds), centred on the cut


def draw_shot(cr, i, t):
    fn = TIMELINE[i][1]
    if fn is None: bg(cr, INK); return
    fn(cr, t)


def transition(cr, kind, q, A, B):
    """Composite outgoing pattern A and incoming pattern B for progress q (0..1)."""
    def paint(p, a=1.0, mtx=None):
        cr.save()
        if mtx: mtx(cr)
        cr.set_source(p); cr.paint_with_alpha(a); cr.restore()
    if kind == 'cut':
        paint(B if q >= 0.5 else A); return
    if kind == 'flash':
        paint(B if q >= 0.5 else A)
        f = 1 - abs(q - 0.5) * 2
        cr.rectangle(0, 0, W, H); col(cr, WHITE, f); cr.fill(); return
    if kind == 'punch':
        paint(A if q < 0.35 else B, 1.0, (lambda c: (c.translate(W / 2, H / 2), c.scale(lerp(1.25, 1, ex((q - 0.35) / 0.65)), lerp(1.25, 1, ex((q - 0.35) / 0.65))), c.translate(-W / 2, -H / 2))) if q >= 0.35 else None)
        return
    if kind == 'zoom':   # fly into the old frame, new one settles from large
        if q < 0.5:
            s_ = lerp(1, 4, ein(q * 2)); paint(A, 1 - ein(q * 2) * 0.6, lambda c: (c.translate(W / 2, H / 2), c.scale(s_, s_), c.translate(-W / 2, -H / 2)))
        else:
            s_ = lerp(1.6, 1, ex((q - 0.5) * 2)); paint(B, 1, lambda c: (c.translate(W / 2, H / 2), c.scale(s_, s_), c.translate(-W / 2, -H / 2)))
        return
    if kind in ('whip', 'whip_l'):
        d = 1 if kind == 'whip' else -1
        e = sm(q)
        for k in range(5):   # streaked motion
            off = (e - k * 0.03) * W * d
            paint(A, 0.35 if k else 1, lambda c, o=off: c.translate(-o, 0))
            paint(B, 0.35 if k else 1, lambda c, o=off: c.translate(W * d - o, 0))
        return
    paint(A)
    cr.save()
    if kind == 'slats':   # vertical slats flip open, staggered left to right
        n = 12
        for k in range(n):
            p = sm(q * 1.6 - k / n * 0.6)
            cr.rectangle(k * W / n + (W / n) * (1 - p) / 2, 0, W / n * p + 1, H)
    elif kind == 'bars':  # brand slanted bars (logo shape) sweep across
        n = 6
        for k in range(n):
            p = sm(q * 1.5 - k * 0.08)
            x = lerp(-W * 0.4, W * 1.1, p) - k * 40
            cr.move_to(x - 900 + k * 320, -50); cr.line_to(x + k * 320 - 200, -50); cr.line_to(x + k * 320 - 600, H + 50); cr.line_to(x - 1300 + k * 320, H + 50); cr.close_path()
        cr.rectangle(-W, -100, lerp(-W, W * 3, sm(q * 1.2 - 0.15)), H + 200)
    elif kind == 'split':  # horizontal split opens from the middle
        e = sm(q); cr.rectangle(0, H / 2 - H / 2 * e, W, H * e)
    cr.clip(); cr.set_source(B); cr.paint(); cr.restore()


def frame(cr, t):
    i = max(0, bisect.bisect_right(STARTS, t) - 1)
    # transition window around the cut into shot i (or into i+1 if we are just before it)
    j = None
    if i + 1 < len(TIMELINE) and STARTS[i + 1] - t < TD / 2: j = i + 1
    elif t - STARTS[i] < TD / 2 and i > 0: j = i
    if j is None or TIMELINE[j][2] == 'cut' and False:
        draw_shot(cr, i, t); return
    q = clamp((t - (STARTS[j] - TD / 2)) / TD)
    cr.push_group(); draw_shot(cr, j - 1, t); A = cr.pop_group()
    cr.push_group(); draw_shot(cr, j, t); B = cr.pop_group()
    transition(cr, TIMELINE[j][2], q, A, B)


# ------------------------------------------------------------------ frame entry
def render(L, t):
    kt.BEAT_T[0] = t
    c = L.fg
    # camera: dhol punches + slow breathing on the bass
    z = 1 + 0.018 * dhol(t) + 0.006 * beat_pulse(t) * env('bass', t)
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    L.bg.rectangle(0, 0, W, H); col(L.bg, INK); L.bg.fill()
    frame(c, t)
    c.identity_matrix()
    # small brand mark (official artwork), dark/light by background brightness
    b = CUR_BG[0]
    if b != GREEN:
        brand_img(L.ui, 'wordmark', 180, 66, 230, 0.9, dark=(b == INK))
