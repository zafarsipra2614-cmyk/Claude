"""Neubrutalism edition of the 0:34-1:09 section.
Flat brand colours, thick ink outlines, hard offset shadows (no blur), chunky uppercase sticker type,
tags, keys and buttons that physically press into their shadows on every dhol hit. Snappy motion."""
import math, random
import cairo
import kt
from kin import *
from kt import FORCE_PATH, DUR, Layers

LIGHT = True
SH = 14          # shadow offset
OL = 6           # outline width
kt.FONTS.update(xb='Manrope XB', b='Manrope B', m='Manrope M')


# ------------------------------------------------------------------ primitives
def bgfill(cr, c, dots=True):
    cr.rectangle(-400, -400, W + 800, H + 800); col(cr, c); cr.fill()
    if dots:
        dc = WHITE if c == INK else INK
        for y in range(30, H, 60):
            for x in range(30, W, 60): cr.new_sub_path(); cr.arc(x, y, 2.2, 0, TAU)
        col(cr, dc, 0.13); cr.fill()
    CUR[0] = c


CUR = [WHITE]


def press(t): return clamp(dhol(t) * 1.2)


def box(cr, x, y, w, h, fill, r=22, p=0.0, a=1.0, sh=SH):
    if a <= 0: return
    rr(cr, x + sh, y + sh, w, h, r); col(cr, INK, a); cr.fill()
    d = sh * p * 0.7
    rr(cr, x + d, y + d, w, h, r); col(cr, fill, a); cr.fill_preserve(); cr.set_line_width(OL); col(cr, INK, a); cr.stroke()
    return d


def btext(cr, s_, x, y, size, fill, align='l', a=1.0, outline=True, shadow=True, d=0.0):
    font(cr, 'xb', size); adv = cr.text_extents(s_).x_advance
    xx = x - adv / 2 if align == 'c' else x if align == 'l' else x - adv
    yy = y + size * 0.36
    off = max(6, size * 0.05)
    if shadow:
        cr.move_to(xx + off, yy + off); cr.text_path(s_); col(cr, INK, a); cr.fill()
    cr.move_to(xx + d, yy + d); cr.text_path(s_); col(cr, fill, a); cr.fill_preserve()
    if outline: cr.set_line_width(max(3, size * 0.03)); cr.set_line_join(cairo.LINE_JOIN_ROUND); col(cr, INK, a); cr.stroke()
    else: cr.new_path()
    return adv


def tag(cr, s_, x, y, size, fill, tcol, a=1.0, align='l', p=0.0, rot=0.0):
    font(cr, 'xb', size); adv = cr.text_extents(s_).x_advance
    w = adv + size * 1.1; h = size * 1.7
    xx = x - w / 2 if align == 'c' else x if align == 'l' else x - w
    cr.save(); cr.translate(xx + w / 2, y); cr.rotate(rot); cr.translate(-(xx + w / 2), -y)
    d = box(cr, xx, y - h / 2, w, h, fill, h / 2, p, a, 10)
    tx(cr, s_, xx + w / 2 + (d or 0), y + (d or 0), size, 'xb', tcol, a)
    cr.restore()
    return w


def pop(t, t0, d=0.26): return back(clamp((t - t0) / d), 1.7) if t >= t0 else 0.0


def slam(t, t0, d=0.2): return clamp((t - t0) / d)


def star(cr, x, y, r, fill, rot=0.0, n=12, a=1.0):
    def path(ox, oy):
        cr.new_path()
        for k in range(n * 2):
            ang = rot + k * math.pi / n; rad = r if k % 2 == 0 else r * 0.72
            (cr.line_to if k else cr.move_to)(ox + x + math.cos(ang) * rad, oy + y + math.sin(ang) * rad)
        cr.close_path()
    path(SH, SH); col(cr, INK, a); cr.fill()
    path(0, 0); col(cr, fill, a); cr.fill_preserve(); cr.set_line_width(OL); col(cr, INK, a); cr.stroke()


def marquee(cr, y, h, t, fill, tcol, items, speed=320, rot=0.0, a=1.0):
    cr.save(); cr.translate(W / 2, y); cr.rotate(rot); cr.translate(-W / 2, -y)
    cr.rectangle(-300, y - h / 2, W + 600, h); col(cr, fill, a); cr.fill_preserve(); cr.set_line_width(OL); col(cr, INK, a); cr.stroke()
    s_ = '  ✦  '.join(items) + '  ✦  '
    font(cr, 'xb', h * 0.46); adv = cr.text_extents(s_).x_advance
    x = -((t * speed) % adv) - 300
    while x < W + 300: tx(cr, s_, x, y, h * 0.46, 'xb', tcol, a, 'l'); x += adv
    cr.restore()


def candle_sticker(cr, x, y, w, h, fill, a=1.0):
    line(cr, [(x + w / 2 + 6, y - 40), (x + w / 2 + 6, y + h + 40)], 8, INK, a)
    box(cr, x, y, w, h, fill, 10, 0, a, 10)


# ------------------------------------------------------------------ shots
def s_lowerlock(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE); p = press(t)
    q = pop(t, w[0])
    if q > 0:
        cr.save(); cr.translate(110 + 560, 380); cr.scale(q, q); cr.translate(-(110 + 560), -380)
        d = box(cr, 110, 140, 1120, 500, RED, 30, p)
        btext(cr, 'LOWER', 170 + d, 270 + d, 210, WHITE)
        if t >= w[1]: btext(cr, 'LOCK', 170 + d, 500 + d, 210, WHITE)
        cr.restore()
    if t >= w[1]: tag(cr, '▼ −7.50%', 1000, 140, 50, WHITE, RED, 1, 'l', p, -0.06 * pop(t, w[1]))
    if t >= w[2]: tag(cr, 'ne aisa', 130, 760, 56, INK, WHITE, 1, 'l', p)
    q2 = slam(t, w[4])
    if q2 > 0:
        cr.save(); cr.translate(760, 760 - (1 - q2) * 260); cr.rotate(-0.05)
        d = box(cr, -20, -90, 560, 180, GREEN, 24, p); btext(cr, 'MAARA!', 250 + d, d, 120, INK, 'c', shadow=False)
        cr.restore()
    fall = ein((t - w[3]) / 0.35)
    if fall > 0: candle_sticker(cr, 1450, -700 + fall * 880, 150, 520, RED)
    if t >= w[1]: marquee(cr, 975, 90, t, INK, WHITE, ['KSE-100 ▼ 7.50%', 'LOWER LOCK', 'TIPWALA LTD ▼ 7.50%', 'CIRCUIT BREAKER'], 360)


def toggle(cr, x, y, off, p=0.0):
    d = box(cr, x - 150, y - 80, 300, 160, mix(GREEN, (0.85, 0.85, 0.85), off), 80, p)
    cx = lerp(x + 70, x - 70, off) + d
    cr.arc(cx, y + d, 58, 0, TAU); col(cr, WHITE); cr.fill_preserve(); cr.set_line_width(OL); col(cr, INK); cr.stroke()


def s_stoploss(cr, t, t0):
    w = wt(t0); bgfill(cr, INK); p = press(t)
    q = pop(t, w[0])
    if q > 0:
        cr.save(); cr.translate(950, 330); cr.scale(q, q); cr.translate(-950, -330)
        d = box(cr, 110, 190, 1300, 280, WHITE, 26, p)
        btext(cr, 'STOP LOSS', 170 + d, 330 + d, 190, INK, shadow=False)
        cr.restore()
    s = slam(t, w[3], 0.16)
    if s > 0:
        cr.save(); cr.translate(760, 330); cr.rotate(-0.05)
        box(cr, -680, -14, 1360 * s, 28, RED, 8, 0, 1, 6)
        cr.restore()
    if t >= w[2]: tag(cr, 'bhi bhool gaya', 130, 600, 60, GREEN, INK, 1, 'l', p, -0.03)
    off = sm((t - w[3]) / 0.3)
    toggle(cr, 1640, 330, off, p)
    tx(cr, 'OFF' if off > 0.5 else 'ON', 1640, 470, 56, 'xb', RED if off > 0.5 else GREEN)
    if t >= w[5]:
        sink = sm((t - w[5] - 0.25) / 1.6)
        cr.save(); cr.translate(150, 820 + sink * 60); cr.rotate(0.06 * sink)
        btext(cr, 'BECHARA', 0, 0, 200, RED, 'l', pop(t, w[5]) and 1); cr.restore()


KEYS = 'DRAMAYBAAZ'


def s_buildup(cr, t, t0):
    t0, t_drop = 39.4, snap(43.4)
    if t < 41.45:   # keyboard: one key presses per half-beat
        bgfill(cr, WHITE)
        hb = half_beats(39.3, 41.5)
        n = len([h for h in hb if h <= t])
        ks = 150; gap = 22; total = 6 * ks + 5 * gap
        for row, word in enumerate(('DRAMAY', 'BAAZ')):
            x0 = W / 2 - (len(word) * ks + (len(word) - 1) * gap) / 2; y0 = 260 + row * 240
            for k, ch in enumerate(word):
                idx = k if row == 0 else 6 + k
                on = idx < n
                pr = 1.0 if on and (t - hb[idx]) < 0.12 else (0.55 if on else 0.0)
                d = box(cr, x0 + k * (ks + gap), y0, ks, ks, GREEN if on else WHITE, 22, pr)
                tx(cr, ch, x0 + k * (ks + gap) + ks / 2 + d, y0 + ks / 2 + d, 96, 'xb', INK)
        tag(cr, 'LOADING DRAMA', W / 2, 860, 44, INK, WHITE, 1, 'c')
        bar = clamp(n / 10)
        box(cr, W / 2 - 400, 920, 800, 34, WHITE, 17, 0, 1, 8); rr(cr, W / 2 - 400, 920, 800 * bar, 34, 17); col(cr, GREEN); cr.fill_preserve(); cr.set_line_width(OL); col(cr, INK); cr.stroke()
        return
    marks = []
    for b in beats_between(41.4, t_drop):
        bi = BEATS.index(b); nb = BEATS[bi + 1] if bi + 1 < len(BEATS) else b + 0.47
        sub = 1 if b < 42.3 else 2 if b < 42.9 else 4
        marks += [b + (nb - b) * k / sub for k in range(sub)]
    marks = [m for m in marks if m < t_drop - 0.1] or [41.45]
    i = max(0, bisect.bisect_right(marks, t) - 1)
    push = 1 + 0.25 * ein((t - 41.45) / (t_drop - 41.45))
    bgfill(cr, INK if i % 2 else WHITE)
    cr.save(); cr.translate(W / 2, H / 2); cr.scale(push, push); cr.translate(-W / 2, -H / 2)
    for k, (lab, c) in enumerate((('BUY', GREEN), ('SELL', RED))):
        x = W / 2 - 620 + k * 660
        pressed = (i % 2 == k) and (t - marks[i]) < 0.14
        d = box(cr, x, 380, 560, 300, c, 40, 1.0 if pressed else 0.0)
        btext(cr, lab, x + 280 + d, 530 + d, 170, WHITE, 'c')
    cr.restore()
    fl = sm((t - (t_drop - 0.1)) / 0.1)
    if fl > 0: cr.rectangle(0, 0, W, H); col(cr, WHITE, fl); cr.fill()


def s_chant(cr, t, t0):
    c_ = C(t0); t1 = c_[1]
    bs = [snap(t0)] + [b for b in BEATS if snap(t0) + 0.1 < b < t1]
    k = max(0, bisect.bisect_right(bs, t) - 1)
    bgfill(cr, GREEN); p = press(t)
    star(cr, W / 2, H / 2, 460 + 30 * beat_pulse(t), WHITE, t * 0.3, 14)
    words = ('DRAMAY', 'BAAZ!')
    for j in range(min(k + 1, len(bs))):
        if j < k - 1: continue
        wd = words[j % 2]; q = slam(t, bs[j], 0.14)
        rot = (-0.06, 0.05)[j % 2]; y = H / 2 - 175 if j % 2 == 0 else H / 2 + 190
        cr.save(); cr.translate(W / 2, y - (1 - q) * 300); cr.rotate(rot)
        sc = lerp(1.2, 1, q); cr.scale(sc, sc)
        d = SH * p * 0.6
        btext(cr, wd, d, d, 230 if j % 2 == 0 else 270, WHITE if j % 2 == 0 else INK, 'c', 1)
        cr.restore()
    for cl in [c for c in CLAP_T if bs[0] <= c <= t and t - c < 0.3]:
        rnd = random.Random(int(cl * 100))
        x = rnd.choice([rnd.uniform(140, 420), rnd.uniform(1500, 1780)]); y = rnd.uniform(160, 920)
        star(cr, x, y, 60 * pop(t, cl, 0.15), (GOLD, WHITE, RED)[int(cl * 10) % 3], cl, 8)


def s_green(cr, t, t0):
    w = wt(t0); bgfill(cr, INK); p = press(t)
    rnd = random.Random(3)
    for k in range(7):
        h = 140 + k * 60
        g = ein(clamp((t - t0 - k * 0.08) / 0.4))
        candle_sticker(cr, 1380 + k * 72, 960 - h * g, 46, h * g + 4, GREEN if rnd.random() > 0.2 else RED)
    q = pop(t, w[0])
    if q > 0:
        cr.save(); cr.translate(560, 300); cr.scale(q, q); cr.translate(-560, -300)
        d = box(cr, 100, 170, 920, 260, GREEN, 26, p); btext(cr, 'GREEN', 560 + d, 300 + d, 210, INK, 'c', shadow=False)
        cr.restore()
    if t >= w[1]: tag(cr, 'dekha toh', 110, 520, 58, WHITE, INK, 1, 'l', p, 0.03)
    # NAACH LIYA as tiles that dance on the beat
    if t >= w[3]:
        ks = 118; gap = 10; s_ = 'NAACH LIYA'; x = 110
        for k, ch in enumerate(s_):
            if ch == ' ': x += 40; continue
            on = t >= w[3] + k * 0.04 if k < 5 else t >= w[4] + (k - 6) * 0.04
            if not on: x += ks + gap; continue
            ph = beat_phase(t); bob = -abs(math.sin(ph * math.pi)) * 28 * (1 if (k + beat_index(t)) % 2 else 0.3)
            d = box(cr, x, 680 + bob, ks, ks, WHITE if k % 2 else GREEN, 18, 0)
            tx(cr, ch, x + ks / 2, 680 + bob + ks / 2, 80, 'xb', INK)
            x += ks + gap


def s_red(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE); p = press(t)
    for k in range(6):
        f = ein(clamp((t - t0 - k * 0.12) / 1.0))
        candle_sticker(cr, 1300 + k * 90, -500 + f * 1300 + (k * 97) % 160, 56, 180 + (k * 53) % 120, RED)
    q = pop(t, w[0])
    if q > 0:
        cr.save(); cr.translate(400, 330); cr.scale(q, q); cr.translate(-400, -330)
        d = box(cr, 100, 180, 640, 300, RED, 26, p); btext(cr, 'RED', 420 + d, 330 + d, 230, WHITE, 'c', shadow=False)
        cr.restore()
    if t >= w[1]: tag(cr, 'dekha toh', 800, 300, 58, INK, WHITE, 1, 'l', p, -0.04)
    if t >= w[3]:
        ks = 118; gap = 10; s_ = 'BHAAG LIYA'; x = 110
        for k, ch in enumerate(s_):
            if ch == ' ': x += 40; continue
            st = w[3] + k * 0.04 if k < 5 else w[4] + (k - 6) * 0.04
            if t < st: x += ks + gap; continue
            go = ein((t - st - 0.45) / 0.5) * 1900
            box(cr, x + go, 680, ks, ks, INK, 18, 0); tx(cr, ch, x + go + ks / 2, 680 + ks / 2, 80, 'xb', WHITE)
            x += ks + gap


def s_gussa(cr, t, t0):
    w = wt(t0); bgfill(cr, INK); p = press(t)
    if t >= w[0]: tag(cr, 'screen pe', W / 2, 230, 60, WHITE, INK, 1, 'c', p, -0.03)
    q = pop(t, w[2])
    if q > 0:
        sh = math.sin(t * 70) * 10 * dhol(t)
        cr.save(); cr.translate(W / 2 + sh, 520); cr.scale(q, q); cr.rotate(-0.03); cr.translate(-W / 2, -520)
        d = box(cr, 330, 360, 1260, 320, RED, 30, p); btext(cr, 'GUSSA', W / 2 + d, 520 + d, 250, WHITE, 'c')
        rnd = random.Random(5)
        nh = len([h for h in DHOL_T if w[2] <= h <= t])
        for k in range(min(14, nh * 2)):   # cracks spreading across the card
            ang = rnd.random() * TAU; L_ = 120 + rnd.random() * 300
            line(cr, [(W / 2 + 200, 520), (W / 2 + 200 + math.cos(ang) * L_, 520 + math.sin(ang) * L_ * 0.5)], 5, INK, 0.9)
        cr.restore()
    if t >= w[3]: tag(cr, 'jhaad liya', W / 2, 820, 60, GREEN, INK, 1, 'c', p, 0.03)


def big_button(cr, t, lab, c, x, y, tap_from, p):
    tap = t >= tap_from and beat_phase(t) < 0.2
    d = box(cr, x, y, 900, 340, c, 60, 1.0 if tap else p * 0.5)
    btext(cr, lab, x + 450 + d, y + 170 + d, 230, WHITE if c == RED else INK, 'c', shadow=False)
    # pointer
    cx, cy = x + 760 + d, y + 250 + d + (0 if tap else 18)
    cr.move_to(cx, cy); cr.line_to(cx, cy + 110); cr.line_to(cx + 30, cy + 82); cr.line_to(cx + 52, cy + 130); cr.line_to(cx + 72, cy + 120)
    cr.line_to(cx + 50, cy + 74); cr.line_to(cx + 90, cy + 72); cr.close_path(); col(cr, WHITE); cr.fill_preserve(); cr.set_line_width(5); col(cr, INK); cr.stroke()


def s_buy(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE); p = press(t)
    if t >= w[0]: tag(cr, 'bina soche', 160, 230, 64, INK, WHITE, 1, 'l', p, -0.04)
    q = pop(t, w[2])
    if q > 0:
        cr.save(); cr.translate(610, 560); cr.scale(q, q); cr.translate(-610, -560)
        big_button(cr, t, 'BUY', GREEN, 160, 390, w[2], p); cr.restore()
    if t >= w[3]: tag(cr, 'kiya', 1200, 860, 70, GREEN, INK, 1, 'l', p, 0.05)


def s_sell(cr, t, t0):
    w = wt(t0); bgfill(cr, INK); p = press(t)
    if t >= w[0]: tag(cr, 'dar ke phir', W - 160, 230, 64, WHITE, INK, 1, 'r', p, 0.04)
    q = pop(t, w[3])
    if q > 0:
        cr.save(); cr.translate(W - 610, 560); cr.scale(q, q); cr.translate(-(W - 610), -560)
        big_button(cr, t, 'SELL', RED, W - 1060, 390, w[3], p); cr.restore()
    if t >= w[4]: tag(cr, 'kiya', 700, 860, 70, RED, WHITE, 1, 'r', p, -0.05)


def s_cry(cr, t, t0):
    w = wt(t0); bgfill(cr, WHITE); p = press(t)
    for k in range(12):   # outlined tear drops falling
        rnd = random.Random(k); ph = ((t - t0) * (0.5 + rnd.random() * 0.4) + rnd.random()) % 1
        x = rnd.random() * W; y = -60 + ph * (H + 120)
        cr.move_to(x, y - 34); cr.curve_to(x + 26, y, x + 26, y + 30, x, y + 30); cr.curve_to(x - 26, y + 30, x - 26, y, x, y - 34)
        col(cr, (0.55, 0.75, 1.0)); cr.fill_preserve(); cr.set_line_width(4); col(cr, INK); cr.stroke()
    if t >= w[0]: tag(cr, 'baith ke phir', W / 2, 260, 64, INK, WHITE, 1, 'c', p)
    q = pop(t, w[3])
    if q > 0:
        sink = sm((t - w[3] - 0.3) / 2.2)
        cr.save(); cr.translate(W / 2, 600 + sink * 120); cr.rotate(0.05 * sink); cr.scale(q, q)
        d = box(cr, -560, -170, 1120, 340, (0.55, 0.75, 1.0), 30, p); btext(cr, 'RO LIYA', d, d, 220, INK, 'c', shadow=False)
        cr.restore()


SHOTS = dict(lowerlock=s_lowerlock, stoploss=s_stoploss, buildup=s_buildup, chant=s_chant, green=s_green, red=s_red,
             gussa=s_gussa, buy=s_buy, sell=s_sell, cry=s_cry, end=lambda cr, t, r: bgfill(cr, INK))


# ------------------------------------------------------------------ transitions: hard, snappy, physical
def t_block(cr, q, A, B, a, b):
    """An outlined colour block slams across the frame and pulls the next shot in behind it."""
    fill = GREEN if b != 'chant' else INK
    x = lerp(-W - 200, W + 200, eio(q))
    paint(cr, A if x < W / 2 - 100 else B)
    box(cr, x - W * 0.6, -60, W * 1.2, H + 120, fill, 0, 0, 1, 0)


def t_drop(cr, q, A, B, a, b):
    paint(cr, A)
    y = lerp(-H, 0, back(q, 1.2))
    cr.save(); cr.translate(SH, SH + y); cr.rectangle(0, 0, W, H); col(cr, INK); cr.fill(); cr.restore()
    paint(cr, B, 1, lambda c: c.translate(0, y))


def t_slide(cr, q, A, B, a, b):
    e = eio(q)
    paint(cr, A, 1, lambda c: c.translate(-W * e, 0))
    paint(cr, B, 1, lambda c: c.translate(W * (1 - e), 0))
    cr.rectangle(W * (1 - e) - OL, 0, OL * 2, H); col(cr, INK); cr.fill()


def t_flash(cr, q, A, B, a, b):
    paint(cr, B if q >= 0.5 else A)
    cr.rectangle(0, 0, W, H); col(cr, WHITE, 1 - abs(q - 0.5) * 2); cr.fill()


def t_stamp(cr, q, A, B, a, b):
    paint(cr, A if q < 0.3 else B, 1, (lambda c: (c.translate(W / 2, H / 2), c.scale(lerp(1.15, 1, ex((q - 0.3) / 0.7)), lerp(1.15, 1, ex((q - 0.3) / 0.7))), c.translate(-W / 2, -H / 2))) if q >= 0.3 else None)


TRANS = dict(default=t_slide, stoploss=t_block, buildup=t_drop, chant=t_stamp, green=t_block, red=t_slide, gussa=t_drop,
             buy=t_block, sell=t_slide, cry=t_drop, end=t_flash)
RUN = Runner(SHOTS, TRANS, 0.3)
RUN.trans_first_chant = True


def render(L, t):
    kt.BEAT_T[0] = t
    c = L.fg
    z = 1 + 0.012 * dhol(t)
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    L.bg.rectangle(0, 0, W, H); col(L.bg, WHITE); L.bg.fill()
    # the drop into the first chant is a white flash rather than a stamp
    RUN.trans['chant'] = t_flash if abs(t - snap(43.4)) < 0.3 else t_stamp
    RUN.frame(c, t)
    c.identity_matrix()
    if CUR[0] != GREEN:
        brand_img(L.ui, 'wordmark', 180, 66, 230, 0.95, dark=(CUR[0] == INK))
