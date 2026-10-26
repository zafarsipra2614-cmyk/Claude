"""Kinetic, all-out edition of the 0:34-1:09 section.
Always-moving camera, depth-flying words with echo trails, stacking lines, outline ripples on the beat,
parallax word walls, diagonal ticker bands, burst lines, market graphics in motion, and beat-locked
zoom-through / whip / flash transitions. Brand palette: ink, white, FloStocks green; red losses; gold accents."""
import math, random
import cairo
import kt
from kin import *
from kt import FORCE_PATH, DUR, Layers

LIGHT = True
kt.FONTS.update(xb='Manrope XB', b='Manrope B', m='Manrope M')
CUR = [INK]


# ------------------------------------------------------------------ backgrounds & layers
def bgfill(cr, c):
    cr.rectangle(-2000, -2000, W + 4000, H + 4000); col(cr, c); cr.fill(); CUR[0] = c


def fg_on(c): return WHITE if c == INK else INK


def word_wall(cr, t, s_, size, c, a, speed=180, rows=5, rot=-0.08):
    """Huge outlined words scrolling in alternating directions behind everything (parallax depth)."""
    cr.save(); cr.translate(W / 2, H / 2); cr.rotate(rot); cr.translate(-W / 2, -H / 2)
    font(cr, 'xb', size); adv = cr.text_extents(s_ + '   ').x_advance
    for r in range(-1, rows + 1):
        y = H / 2 + (r - rows / 2 + 0.5) * size * 1.02
        off = (t * speed * (1 if r % 2 else -1)) % adv
        x = -off - adv - 400
        while x < W + 400:
            cr.move_to(x, y + size * 0.36); cr.text_path(s_); x += adv
    cr.set_line_width(max(2, size * 0.012)); col(cr, c, a); cr.stroke(); cr.restore()


def band(cr, t, y, h, rot, c_bg, c_tx, items, speed=420, a=1.0):
    cr.save(); cr.translate(W / 2, y); cr.rotate(rot); cr.translate(-W / 2, -y)
    cr.rectangle(-600, y - h / 2, W + 1200, h); col(cr, c_bg, a); cr.fill()
    s_ = '   ◆   '.join(items) + '   ◆   '
    font(cr, 'xb', h * 0.5); adv = cr.text_extents(s_).x_advance
    x = -((t * speed) % adv) - 600
    while x < W + 600: tx(cr, s_, x, y, h * 0.5, 'xb', c_tx, a, 'l'); x += adv
    cr.restore()


def bursts(cr, t, times, cx, cy, c, r0=380, n=20, life=0.35, w=10):
    for h in times:
        age = t - h
        if 0 <= age < life:
            q = ex(age / life)
            for k in range(n):
                ang = k * TAU / n + h * 3
                r1 = r0 + q * 380; r2 = r1 + 160 * (1 - q)
                line(cr, [(cx + math.cos(ang) * r1, cy + math.sin(ang) * r1), (cx + math.cos(ang) * r2, cy + math.sin(ang) * r2)], w * (1 - q) + 1, c, 1 - q)


def sparks(cr, t, times, c, n=10, life=0.3):
    for h in times:
        age = t - h
        if 0 <= age < life:
            rnd = random.Random(int(h * 1000))
            for k in range(n):
                ang = rnd.random() * TAU; sp = 300 + rnd.random() * 700
                x = W / 2 + rnd.uniform(-700, 700) + math.cos(ang) * sp * age; y = H / 2 + rnd.uniform(-350, 350) + math.sin(ang) * sp * age
                cr.arc(x, y, 6 * (1 - age / life), 0, TAU); col(cr, c, 1 - age / life); cr.fill()


def candle(cr, x, base, w, h, c, a=1.0):
    line(cr, [(x + w / 2, base - h - 30), (x + w / 2, base + 20)], max(3, w * 0.12), c, a)
    cr.rectangle(x, base - h, w, h * 0.82); col(cr, c, a); cr.fill()


def arrow(cr, x, y, s, c, a=1.0, down=False):
    cr.save(); cr.translate(x, y); cr.scale(s, -s if down else s)
    cr.move_to(0, -60); cr.line_to(52, -4); cr.line_to(18, -4); cr.line_to(18, 60); cr.line_to(-18, 60); cr.line_to(-18, -4); cr.line_to(-52, -4)
    cr.close_path(); col(cr, c, a); cr.fill(); cr.restore()


# ------------------------------------------------------------------ word animations (all land on the sung syllable)
def _draw(cr, s_, x, y, size, c, a, align='c'):
    tx(cr, s_, x, y, size, 'xb', c, a, align)


def a_depth(cr, s_, x, y, size, c, t, t0, align='c'):
    """Flies in from depth: big + transparent -> sharp, with an echo trail behind."""
    q = ex((t - t0) / 0.32)
    if q <= 0: return
    for e in range(5, 0, -1):
        qe = ex((t - t0 - e * 0.025) / 0.32)
        sc = lerp(3.2, 1, qe)
        cr.save(); cr.translate(x, y); cr.scale(sc, sc); _draw(cr, s_, 0, 0, size, c, 0.10 * (1 - qe * 0.6), align); cr.restore()
    sc = lerp(3.2, 1, q)
    cr.save(); cr.translate(x, y); cr.scale(sc, sc); _draw(cr, s_, 0, 0, size, c, clamp(q * 1.5), align); cr.restore()


def a_ripple(cr, s_, x, y, size, c, t, t0, align='c', fg=None):
    """After landing, outline copies ripple outward on every beat (keeps the key word alive)."""
    if t < t0: return
    font(cr, 'xb', size); adv = cr.text_extents(s_).x_advance
    xx = x - adv / 2 if align == 'c' else x if align == 'l' else x - adv
    for b in beats_between(t0 + 0.2, t + 0.001)[-2:]:
        age = t - b
        if age > 0.5: continue
        sc = 1 + age * 0.5
        cr.save(); cr.translate(xx + adv / 2, y); cr.scale(sc, sc); cr.translate(-(xx + adv / 2), -y)
        cr.move_to(xx, y + size * 0.36); cr.text_path(s_); cr.set_line_width(3); col(cr, c, 0.6 * (1 - age / 0.5)); cr.stroke(); cr.restore()


def a_flip(cr, s_, x, y, size, c, t, t0, align='c'):
    """Letters flip in one by one (3D card flip)."""
    font(cr, 'xb', size); advs = [cr.text_extents(ch).x_advance for ch in s_]; total = sum(advs)
    xx = x - total / 2 if align == 'c' else x if align == 'l' else x - total
    for k, ch in enumerate(s_):
        q = ex((t - t0 - k * 0.035) / 0.28)
        if q <= 0: break
        cx_ = xx + sum(advs[:k]) + advs[k] / 2
        cr.save(); cr.translate(cx_, y); cr.scale(1, max(0.02, abs(math.cos((1 - q) * math.pi / 2)))); _draw(cr, ch, 0, 0, size, c, clamp(q * 2)); cr.restore()


def a_slide(cr, s_, x, y, size, c, t, t0, align='c', d=1):
    q = ex((t - t0) / 0.3)
    if q <= 0: return
    for e in range(4, 0, -1):
        qe = ex((t - t0 - e * 0.02) / 0.3)
        _draw(cr, s_, x - d * (1 - qe) * 700, y, size, c, 0.12, align)
    _draw(cr, s_, x - d * (1 - q) * 700, y, size, c, clamp(q * 2), align)


def a_split(cr, s_, x, y, size, c, t, t0, align='c'):
    """Top and bottom halves slam together from opposite sides."""
    q = ex((t - t0) / 0.28)
    if q <= 0: return
    font(cr, 'xb', size); adv = cr.text_extents(s_).x_advance
    xx = x - adv / 2 if align == 'c' else x if align == 'l' else x - adv
    for half, d in ((0, -1), (1, 1)):
        cr.save(); cr.rectangle(xx - 50, y - size * 0.6 + half * size * 0.6, adv + 100, size * 0.6); cr.clip()
        _draw(cr, s_, x + d * (1 - q) * 900, y, size, c, 1, align); cr.restore()


def a_slam(cr, s_, x, y, size, c, t, t0, align='c'):
    q = clamp((t - t0) / 0.12)
    if q <= 0: return
    sc = lerp(1.6, 1, ein(q)) if q < 1 else 1 + 0.06 * math.exp(-(t - t0 - 0.12) * 14)
    cr.save(); cr.translate(x, y); cr.scale(sc, sc); _draw(cr, s_, 0, 0, size, c, clamp(q * 3), align); cr.restore()


def a_bounce(cr, s_, x, y, size, c, t, t0, align='c'):
    font(cr, 'xb', size); advs = [cr.text_extents(ch).x_advance for ch in s_]; total = sum(advs)
    xx = x - total / 2 if align == 'c' else x if align == 'l' else x - total
    for k, ch in enumerate(s_):
        q = ex((t - t0 - k * 0.03) / 0.25)
        if q <= 0: break
        ph = beat_phase(t); up = (1 if (k + beat_index(t)) % 2 else 0.35)
        dy = -abs(math.sin(ph * math.pi)) * size * 0.22 * up + (1 - q) * size
        rot = (0.12 if (k + beat_index(t)) % 2 else -0.12) * (1 - ph)
        cx_ = xx + sum(advs[:k]) + advs[k] / 2
        cr.save(); cr.translate(cx_, y + dy); cr.rotate(rot); _draw(cr, ch, 0, 0, size, c, clamp(q * 2)); cr.restore()


def a_run(cr, s_, x, y, size, c, t, t0, align='c'):
    font(cr, 'xb', size); advs = [cr.text_extents(ch).x_advance for ch in s_]; total = sum(advs)
    xx = x - total / 2 if align == 'c' else x if align == 'l' else x - total
    for k, ch in enumerate(s_):
        q = ex((t - t0 - k * 0.03) / 0.2)
        if q <= 0: break
        go = ein((t - t0 - 0.45 - k * 0.04) / 0.45) * 2200
        cx_ = xx + sum(advs[:k]) + advs[k] / 2
        for e in range(1, 6):
            if go > 5: _draw(cr, ch, cx_ + go - e * go * 0.08, y, size, c, 0.18 / e)
        _draw(cr, ch, cx_ + go, y, size, c, clamp(q * 2))


def a_drip(cr, s_, x, y, size, c, t, t0, align='c'):
    font(cr, 'xb', size); advs = [cr.text_extents(ch).x_advance for ch in s_]; total = sum(advs)
    xx = x - total / 2 if align == 'c' else x if align == 'l' else x - total
    for k, ch in enumerate(s_):
        q = ex((t - t0 - k * 0.05) / 0.4)
        if q <= 0: break
        sag = sm((t - t0 - 0.4 - k * 0.07) / 1.8)
        dy = sag * size * (0.3 + 0.4 * ((k * 37) % 5) / 5) - (1 - q) * size * 0.8
        cx_ = xx + sum(advs[:k]) + advs[k] / 2
        cr.save(); cr.translate(cx_, y + dy); cr.rotate(sag * (0.15 if k % 2 else -0.1)); _draw(cr, ch, 0, 0, size, c, clamp(q * 2)); cr.restore()


ANIM = dict(depth=a_depth, flip=a_flip, slide=a_slide, slider=lambda *a, **k: a_slide(*a, d=-1, **k), split=a_split, slam=a_slam,
            bounce=a_bounce, run=a_run, drip=a_drip)


# ------------------------------------------------------------------ composed lyric lines
# rows: (text, word indices that start it, size, colour key, animation, y)
LINES = {
    34.8: dict(bg=INK, rows=[('LOWER LOCK', [0, 1], 270, 'red', 'depth', 400), ('NE AISA', [2], 90, 'fg', 'slide', 640), ('MAARA!', [4], 200, 'fg', 'slam', 800)],
               wall='LOWER LOCK', key=0),
    36.6: dict(bg=WHITE, rows=[('STOP LOSS', [0, 1], 250, 'fg', 'flip', 360), ('BHI BHOOL GAYA', [2], 100, 'fg', 'slider', 580), ('BECHARA', [5], 230, 'red', 'drip', 790)],
               wall='STOP LOSS', key=0),
    45.5: dict(bg=INK, rows=[('GREEN', [0], 330, 'green', 'depth', 380), ('DEKHA TOH', [1], 90, 'fg', 'slide', 590), ('NAACH LIYA', [3], 200, 'fg', 'bounce', 790)],
               wall='GREEN GREEN', key=0),
    49.3: dict(bg=WHITE, rows=[('RED', [0], 400, 'red', 'split', 380), ('DEKHA TOH', [1], 90, 'fg', 'slider', 620), ('BHAAG LIYA', [3], 200, 'fg', 'run', 810)],
               wall='RED RED', key=0),
    52.0: dict(bg=INK, rows=[('SCREEN PE', [0], 100, 'fg', 'slide', 260), ('GUSSA', [2], 400, 'red', 'slam', 540), ('JHAAD LIYA', [3], 100, 'fg', 'slider', 820)],
               wall='GUSSA', key=1),
    57.7: dict(bg=WHITE, rows=[('BINA SOCHE', [0], 110, 'fg', 'slide', 260), ('BUY', [2], 470, 'green', 'depth', 560), ('KIYA', [3], 120, 'fg', 'slam', 840)],
               wall='BUY BUY', key=1),
    59.8: dict(bg=INK, rows=[('DAR KE PHIR', [0], 110, 'fg', 'slider', 260), ('SELL', [3], 470, 'red', 'depth', 560), ('KIYA', [4], 120, 'fg', 'slam', 840)],
               wall='SELL SELL', key=1),
    61.5: dict(bg=WHITE, rows=[('BAITH KE PHIR', [0], 110, 'fg', 'slide', 320), ('RO LIYA', [3], 330, 'fg', 'drip', 620)], wall='RO LIYA', key=1),
}


def colour(k, bg): return dict(red=RED, green=GREEN, gold=GOLD, fg=fg_on(bg))[k]


def s_line(cr, t, t0):
    cfg = LINES[t0]; w = wt(t0); bg = cfg['bg']
    bgfill(cr, bg)
    word_wall(cr, t, cfg['wall'], 300, fg_on(bg), 0.07, 120)
    graphics(cr, t, t0, w, bg)
    for i, (s_, idx, size, ck, an, y) in enumerate(cfg['rows']):
        c = colour(ck, bg); t_on = w[idx[0]]
        if i == cfg['key']:
            a_ripple(cr, s_, W / 2, y, size, c, t, t_on + 0.3)
        # words of a multi-word row land on their own syllables
        if len(idx) > 1 and an in ('depth', 'flip'):
            parts = s_.split(' '); font(cr, 'xb', size)
            sp = cr.text_extents(' ').x_advance; advs = [cr.text_extents(p).x_advance for p in parts]
            x = W / 2 - (sum(advs) + sp * (len(parts) - 1)) / 2
            for p, a_, j in zip(parts, advs, idx):
                ANIM[an](cr, p, x + a_ / 2, y, size, c, t, w[j]); x += a_ + sp
        else:
            ANIM[an](cr, s_, W / 2, y, size, c, t, t_on)
    bursts(cr, t, [w[cfg['rows'][cfg['key']][1][0]]], W / 2, cfg['rows'][cfg['key']][5], colour(cfg['rows'][cfg['key']][3], bg))


def graphics(cr, t, t0, w, bg):
    fg = fg_on(bg)
    if t0 == 34.8:   # red crash candle smashes down, ticker band
        q = ein((t - w[4] + 0.12) / 0.2)
        if q > 0:
            candle(cr, 1560, lerp(-400, 980, q), 160, 700, RED, 0.85)
            candle(cr, 230, lerp(-500, 1000, ein((t - w[4]) / 0.22)), 120, 520, RED, 0.6)
        band(cr, t, 960, 86, -0.05, RED, WHITE, ['KSE-100 ▼ 7.50%', 'LOWER LOCK', 'CIRCUIT BREAKER', 'TIPWALA LTD ▼ 7.50%'], 520, ex((t - w[1]) / 0.3))
    elif t0 == 36.6:   # strike through STOP LOSS on "bhool"
        q = ex((t - w[3]) / 0.22)
        if q > 0: line(cr, [(W / 2 - 700, 380), (W / 2 - 700 + 1400 * q, 340)], 26, RED)
    elif t0 in (45.5, 85.7):   # green equalizer candles pump on the beat
        n = 22
        for k in range(n):
            h = (120 + 260 * (k / n)) * (0.6 + 0.6 * beat_pulse(t - k * 0.01, 6)) * ex((t - w[0] - k * 0.02) / 0.4)
            candle(cr, 60 + k * 85, 1060, 44, h, GREEN if k % 5 else RED, 0.35)
    elif t0 in (49.3, 89.7):   # red candles raining down
        for k in range(14):
            rnd = random.Random(k); f = ((t - w[0]) * (0.9 + rnd.random()) + rnd.random()) % 1.2
            candle(cr, rnd.random() * W, -200 + f * 1400, 44, 160 + rnd.random() * 140, RED, 0.3)
    elif t0 in (52.0, 92.4):   # cracks spread on each dhol hit
        n = len([h for h in DHOL_T if w[2] <= h <= t]); rnd = random.Random(9)
        for k in range(min(30, n * 4)):
            ang = rnd.random() * TAU; L_ = 200 + rnd.random() * 700; pts = [(W / 2, H / 2)]
            for j in range(1, 5): pts.append((W / 2 + math.cos(ang + rnd.uniform(-.3, .3)) * L_ * j / 4, H / 2 + math.sin(ang + rnd.uniform(-.3, .3)) * L_ * j / 4))
            line(cr, pts, 3, fg, 0.45)
    elif t0 == 57.7:   # arrows burst upward
        for k in range(10):
            rnd = random.Random(k); ph = ((t - w[2]) * (0.8 + rnd.random()) + rnd.random()) % 1
            if t > w[2]: arrow(cr, 100 + rnd.random() * (W - 200), H + 100 - ph * (H + 300), 0.9, GREEN, 0.4)
    elif t0 == 59.8:   # arrows rain down
        for k in range(10):
            rnd = random.Random(k); ph = ((t - w[3]) * (0.8 + rnd.random()) + rnd.random()) % 1
            if t > w[3]: arrow(cr, 100 + rnd.random() * (W - 200), -100 + ph * (H + 300), 0.9, RED, 0.4, down=True)
    elif t0 == 61.5:   # rain + a falling chart line
        rnd = random.Random(int(t * 30))
        for k in range(70):
            x = rnd.random() * W; y = rnd.random() * H; line(cr, [(x, y), (x - 8, y + 60)], 2, (0.4, 0.45, 0.5), 0.3)
        pts = [(k * 32, 200 + (k / 60) ** 1.6 * 700 * sm((t - w[0]) / 3) + 20 * math.sin(k)) for k in range(61)]
        line(cr, pts, 6, RED, 0.45)


# ------------------------------------------------------------------ build-up (instrumental)
def s_buildup(cr, t, t0):
    t0, t_drop = BUILD_T, DROP
    span = t_drop - t0; k = clamp((t - t0) / span)
    hb = half_beats(t0 - 0.05, t_drop)
    lit = len([h for h in hb if h <= t])
    marks = []
    for b in beats_between(PH_B - 0.05, t_drop):
        bi = BEATS.index(b); nb = BEATS[bi + 1] if bi + 1 < len(BEATS) else b + 0.47
        sub = 2 if b < t_drop - 0.9 else 4
        marks += [b + (nb - b) * j / sub for j in range(sub)]
    strobe = len([m for m in marks if m <= t and m > t_drop - 0.95]) % 2 == 1
    bg = WHITE if strobe else INK
    bgfill(cr, bg); fg = fg_on(bg)
    spin = ein(k) * 0.9 * math.sin(t * 1.3); zoom = 1 + 0.9 * ein(k)
    collapse = sm((t - (t_drop - 0.18)) / 0.18)
    cr.save(); cr.translate(W / 2, H / 2); cr.rotate(spin); s_ = zoom * (1 - 0.97 * collapse); cr.scale(s_, s_); cr.translate(-W / 2, -H / 2)
    rows = 9; size = 150
    for r in range(rows):
        y = H / 2 + (r - rows / 2 + 0.5) * size * 1.08
        # position = integral of a speed ramping 260 -> 1160 px/s (k^3 ease), so motion stays continuous
        pos = (260 * (t - t0) + 900 * span * k ** 4 / 4 + r * 137) * (1 if r % 2 else -1)
        font(cr, 'xb', size); s2 = 'DRAMAY BAAZ  '; adv = cr.text_extents(s2).x_advance
        x = -(pos % adv) - adv - 600
        on = r < lit * rows / max(1, len(hb))
        c = GREEN if on else fg
        while x < W + 600:
            if on: tx(cr, s2, x, y, size, 'xb', c, 1, 'l')
            else:
                cr.move_to(x, y + size * 0.36); cr.text_path(s2); cr.set_line_width(2); col(cr, c, 0.35); cr.stroke()
            x += adv
    cr.restore()
    bursts(cr, t, [h for h in hb if h > t_drop - 1.0], W / 2, H / 2, GREEN, 200, 16, 0.25)
    if collapse > 0:
        cr.arc(W / 2, H / 2, 40 + 30 * collapse, 0, TAU); col(cr, WHITE); cr.fill()


# ------------------------------------------------------------------ chants
def s_chant(cr, t, ev):
    hits = ev['hits']
    k = max(0, bisect.bisect_right(hits, t) - 1)
    bgfill(cr, GREEN)
    word_wall(cr, t, 'DRAMAY BAAZ', 260, INK, 0.12, 300, rot=-0.12 if k % 2 else 0.1)
    band(cr, t, 180, 70, -0.1, INK, GREEN, ['DRAMAY BAAZ', 'FLOSTOCKS', 'PSX'], 600)
    band(cr, t, 930, 70, -0.1, INK, GREEN, ['DRAMAY BAAZ', 'FLOSTOCKS', 'PSX'], -600)
    ci = CHANT_EV.index(ev)
    w_ = ('DRAMAY', 'BAAZ!')[k % 2]
    lay = (k + ci) % 3
    c = WHITE if k % 2 == 0 else INK
    h = hits[k] if t >= hits[0] else hits[0]
    if lay == 0:
        a_depth(cr, w_, W / 2, H / 2, 340 if k % 2 == 0 else 420, c, t, h)
    elif lay == 1:
        cr.save(); cr.translate(W / 2, H / 2); cr.rotate(-math.pi / 2 * (1 - ex((t - h) / 0.25))); cr.translate(-W / 2, -H / 2)
        a_slam(cr, w_, W / 2, H / 2, 380, c, t, h); cr.restore()
    else:
        a_split(cr, w_, W / 2, H / 2, 380, c, t, h)
    a_ripple(cr, w_, W / 2, H / 2, 380, c, t, h + 0.15)
    bursts(cr, t, [x for x in hits if x <= t], W / 2, H / 2, WHITE, 480, 22, 0.35, 12)
    sparks(cr, t, [x for x in CLAP_T if hits[0] - 0.1 <= x <= t], WHITE, 12)


SHOTS = dict(lowerlock=lambda cr, t, r: s_line(cr, t, 34.8), stoploss=lambda cr, t, r: s_line(cr, t, 36.6),
             green=lambda cr, t, r: s_line(cr, t, r), red=lambda cr, t, r: s_line(cr, t, r), gussa=lambda cr, t, r: s_line(cr, t, r),
             buy=lambda cr, t, r: s_line(cr, t, 57.7), sell=lambda cr, t, r: s_line(cr, t, 59.8), cry=lambda cr, t, r: s_line(cr, t, 61.5),
             buildup=s_buildup, chant=s_chant, end=lambda cr, t, r: bgfill(cr, INK))


# ------------------------------------------------------------------ transitions (beat-locked, motion-blurred at 60 fps)
def t_zoomthrough(cr, q, A, B, a, b):
    if q < 0.5:
        s_ = lerp(1, 6, ein(q * 2)); paint(cr, A, 1, lambda c: (c.translate(W / 2, H / 2), c.scale(s_, s_), c.translate(-W / 2, -H / 2)))
        cr.rectangle(0, 0, W, H); col(cr, WHITE, ein(q * 2) * 0.8); cr.fill()
    else:
        s_ = lerp(0.4, 1, ex((q - 0.5) * 2)); cr.rectangle(0, 0, W, H); col(cr, WHITE); cr.fill()
        paint(cr, B, 1, lambda c: (c.translate(W / 2, H / 2), c.scale(s_, s_), c.translate(-W / 2, -H / 2)))


def t_whip(cr, q, A, B, a, b):
    e = sm(q); d = 1 if hash(b) % 2 else -1
    paint(cr, A, 1, lambda c: (c.translate(W / 2, H / 2), c.rotate(d * e * 0.6), c.translate(-W / 2 - d * e * W * 1.2, -H / 2)))
    paint(cr, B, 1, lambda c: (c.translate(W / 2, H / 2), c.rotate(-d * (1 - e) * 0.6), c.translate(-W / 2 + d * (1 - e) * W * 1.2, -H / 2)))


def t_flash(cr, q, A, B, a, b):
    paint(cr, B if q >= 0.5 else A)
    cr.rectangle(0, 0, W, H); col(cr, WHITE, (1 - abs(q - 0.5) * 2) ** 0.7); cr.fill()


def t_slats(cr, q, A, B, a, b):
    paint(cr, A); cr.save()
    for k in range(14):
        p = sm(q * 1.7 - k / 14 * 0.7)
        cr.rectangle(k * W / 14, 0, W / 14 + 1, H * p) if k % 2 else cr.rectangle(k * W / 14, H * (1 - p), W / 14 + 1, H * p)
    cr.clip(); cr.set_source(B); cr.paint(); cr.restore()


TRANS = dict(default=t_whip, stoploss=t_slats, buildup=t_zoomthrough, chant=t_flash, green=t_zoomthrough, red=t_whip, gussa=t_slats,
             buy=t_zoomthrough, sell=t_whip, cry=t_slats, end=t_flash)
RUN = Runner(SHOTS, TRANS, 0.3)


# ------------------------------------------------------------------ camera + frame
def camera(t):
    i = max(0, bisect.bisect_right(RUN.starts, t) - 1)
    t0 = RUN.starts[i]; nxt = RUN.starts[i + 1] if i + 1 < len(RUN.starts) else t0 + 3
    p = clamp((t - t0) / max(0.5, nxt - t0))
    d = 1 if i % 2 else -1
    zoom = 1 + 0.07 * sm(p) + 0.035 * dhol(t)
    rot = d * 0.025 * (sm(p) - 0.5) + 0.006 * math.sin(t * 9) * dhol(t)
    dx = d * 40 * (sm(p) - 0.5); dy = 6 * math.sin(t * 2.1)
    key = RUN.tl[i][1]
    if key in ('gussa', 'lowerlock'):   # impact shake on big hits
        sh = 14 * dhol(t); dx += math.sin(t * 31) * sh; dy += math.cos(t * 27) * sh
    return zoom, rot, dx, dy


def render(L, t):
    kt.BEAT_T[0] = t
    c = L.fg
    z, r, dx, dy = camera(t)
    c.translate(W / 2 + dx, H / 2 + dy); c.rotate(r); c.scale(z, z); c.translate(-W / 2, -H / 2)
    L.bg.rectangle(0, 0, W, H); col(L.bg, INK); L.bg.fill()
    RUN.trans['chant'] = t_flash
    RUN.frame(c, t)
    c.identity_matrix()
    if CUR[0] != GREEN:
        brand_img(L.ui, 'wordmark', 180, 66, 230, 0.95, dark=(CUR[0] == INK))
