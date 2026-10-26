"""Dramay Baaz, Apple-inspired lyric video.
Design language: white canvas with slow pastel mesh light, Inter Display type, Apple Music "Sing"-style
time-synced lyrics (words fill as they are sung), hero type for choruses, full-bleed brand green for every
"DRAMAY BAAZ!" cut on the beat, one floating iPhone per verse whose screens change inside it, critically
damped easing everywhere (no bounce, no shake, no glitch).
Exposes render(L, t), Layers, LIGHT, DUR, FORCE_PATH for render_kt.py (VIDEO=ap)."""
import json, math, random, bisect
import cairo
import kt
from kt import (Layers, rr, col, tx, tw, font, line, check, icon, strike, glass, status_bar, PW, PH,
                scr_index, scr_buy, scr_chat, scr_portfolio, scr_call, scr_web, scr_button,
                G, GD, GT, FOREST, INK, RED, GOLD, WHITE, FGC, MUTED, LIGHT, DUR, FORCE_PATH, hexc)
from lib import W, H, BEATS, beat_pulse, beat_index, beat_phase, env, clamp, lerp, mix, TAU, brand_img
from scenes import LYRICS, LYR_END, CHANTS, DB, NO, section, idx_value, idx_ref

kt.FONTS.update(axb='Inter Display ExtraBold', abk='Inter Display Black', asb='Inter Display SemiBold',
                am='Inter Display Medium', al='Inter Display Light')
VT = {float(k): v for k, v in json.load(open('audio/word_times_vocal.json')).items()}
BRIGHT_G = hexc('#38D100')
GREY = (0.72, 0.74, 0.73)
SUBS = kt.SUBS


# ------------------------------------------------------------------ easing
def ex(x):            # expo out: fast start, long soft landing
    x = clamp(x); return 1 - 2 ** (-10 * x) if x < 1 else 1.0


def sm(x):            # smootherstep
    x = clamp(x); return x * x * x * (x * (6 * x - 15) + 10)


def env_in(t, t0, d=0.6): return ex((t - t0) / d)


def words_of(t0): return [l for l in LYRICS if l[0] == t0][0][1].replace('"', '').split(' ')


def wtimes(t0):
    n = len(words_of(t0)); v = VT.get(t0)
    if v and len(v) == n: return v
    return kt.word_times(t0, n)


def word_tint(w_):
    c = kt.word_col(w_)
    return GT if c == GT else RED if c == RED else FGC


# ------------------------------------------------------------------ backdrop: soft mesh light
MOODS = {
    'neutral': [(0.80, 0.95, 0.80), (0.90, 0.96, 0.93), (0.85, 0.92, 0.98), (0.95, 0.97, 0.90)],
    'morning': [(1.0, 0.86, 0.68), (1.0, 0.93, 0.78), (0.85, 0.95, 0.82), (1.0, 0.80, 0.75)],
    'gold': [(1.0, 0.88, 0.55), (1.0, 0.95, 0.75), (0.98, 0.84, 0.62), (0.92, 0.95, 0.80)],
    'red': [(1.0, 0.78, 0.78), (1.0, 0.88, 0.86), (0.98, 0.74, 0.80), (0.95, 0.90, 0.92)],
    'green': [(0.72, 0.95, 0.66), (0.84, 0.98, 0.78), (0.75, 0.92, 0.85), (0.92, 0.99, 0.84)],
    'blue': [(0.80, 0.86, 0.98), (0.88, 0.92, 1.0), (0.78, 0.84, 0.95), (0.92, 0.94, 0.98)],
    'mint': [(0.76, 0.95, 0.90), (0.86, 0.97, 0.94), (0.80, 0.92, 0.95), (0.90, 0.98, 0.90)],
}
LINE_MOOD = {16.2: 'morning', 18.1: 'morning', 20.4: 'green', 23.0: 'morning', 25.5: 'morning', 27.3: 'gold', 31.1: 'gold',
             32.9: 'gold', 34.8: 'red', 36.6: 'red', 45.5: 'green', 49.3: 'red', 52.0: 'red', 57.7: 'green', 59.8: 'red',
             61.5: 'blue', 69.5: 'red', 71.6: 'green', 73.9: 'neutral', 76.5: 'red', 79.0: 'red', 80.8: 'red', 85.7: 'green',
             89.7: 'red', 92.4: 'red'}


def mood_at(t):
    sec = section(t)[1]
    if sec == 'bridge': return 'mint'
    if sec in ('final', 'outro'): return 'green' if 114 <= t < 143 else 'neutral'
    cur = None
    for l in LYRICS:
        if l[0] - 0.3 <= t: cur = l[0]
    if cur in LINE_MOOD and t < LYR_END[cur] + 0.8: return LINE_MOOD[cur]
    return {'verse1': 'morning', 'dream': 'gold', 'crash': 'red'}.get(sec, 'neutral')


def mood_mix(t):
    acc = {}
    for k in range(10):
        m = mood_at(t - k * 0.09); acc[m] = acc.get(m, 0) + 1
    cols = [(0, 0, 0)] * 4
    for m, n in acc.items():
        cols = [tuple(a + b * n / 10 for a, b in zip(c1, c2)) for c1, c2 in zip(cols, MOODS[m])]
    return cols


def backdrop(L, t):
    c = L.bg
    c.rectangle(-300, -300, W + 600, H + 600); col(c, (0.992, 0.994, 0.992)); c.fill()
    cols = mood_mix(t); b = env('bass', t) * beat_pulse(t, 6)
    spots = ((0.18, 0.22, 0.05, 0.07, 900), (0.82, 0.28, 0.06, 0.05, 820), (0.70, 0.86, 0.04, 0.06, 980), (0.20, 0.82, 0.05, 0.04, 760))
    for i, (fx, fy, sx, sy, r) in enumerate(spots):
        x = W * (fx + 0.06 * math.sin(t * sx * 6 + i * 1.7)); y = H * (fy + 0.06 * math.cos(t * sy * 6 + i))
        rad = r * (1 + 0.03 * b)
        g = cairo.RadialGradient(x, y, 0, x, y, rad)
        g.add_color_stop_rgba(0, *cols[i], 0.5); g.add_color_stop_rgba(0.6, *cols[i], 0.16); g.add_color_stop_rgba(1, *cols[i], 0)
        c.set_source(g); c.arc(x, y, rad, 0, TAU); c.fill()


def backdrop_green(L, t, age):
    c = L.bg
    c.rectangle(-300, -300, W + 600, H + 600); col(c, BRIGHT_G); c.fill()
    for i, (fx, fy, r, cc, al) in enumerate(((0.15, 0.2, 900, (0.55, 0.95, 0.35), 0.5), (0.9, 0.85, 950, (0.14, 0.62, 0.0), 0.35),
                                            (0.75, 0.15, 700, (0.7, 1.0, 0.5), 0.35))):
        x = W * (fx + 0.04 * math.sin(t * 0.3 + i)); y = H * (fy + 0.04 * math.cos(t * 0.25 + i))
        g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *cc, al); g.add_color_stop_rgba(1, *cc, 0)
        c.set_source(g); c.arc(x, y, r, 0, TAU); c.fill()


# ------------------------------------------------------------------ chants: full-bleed green, cut on the beat
def snap(x, tol=0.13):
    i = bisect.bisect_left(BEATS, x)
    best = min((BEATS[j] for j in (i - 1, i) if 0 <= j < len(BEATS)), key=lambda g: abs(g - x), default=x)
    return best if abs(best - x) <= tol else x


def chant_now(t):
    for c in CHANTS:
        if snap(c[0]) - 0.02 <= t < c[1]: return c
    return None


def chant_beats(t0, t1):
    s = snap(t0)
    return [s] + [b for b in BEATS if s + 0.1 < b < t1]


def hero_word(cr, s_, x, y, size, c, t, t_on, fam='abk', a=1.0):
    q = ex((t - t_on) / 0.35)
    if q <= 0: return
    sc = lerp(1.07, 1.0, q)
    cr.save(); cr.translate(x, y + (1 - q) * 18); cr.scale(sc, sc)
    tx(cr, s_, 0, 0, size, fam, c, a * clamp(q * 1.6)); cr.restore()


def chant_db(L, t, c_):
    t0, t1, _ = c_
    bs = chant_beats(t0, t1)
    k = max(0, bisect.bisect_right(bs, t) - 1)
    ci = [c[0] for c in CHANTS].index(t0)
    mode = ci % 3
    fg = L.fg
    out_a = clamp((t1 + 0.15 - t) / 0.15)
    if mode == 0:     # one giant word per beat
        w_ = ('DRAMAY', 'BAAZ!')[k % 2]
        size = 330 if w_ == 'DRAMAY' else 400
        hero_word(fg, w_, W / 2, H / 2, size, WHITE if k % 2 == 0 else FOREST, t, bs[k], 'abk', out_a)
    elif mode == 1:   # stacked, second word lands on the next beat
        cyc = (k // 2) * 2
        b0 = bs[min(cyc, len(bs) - 1)]; b1 = bs[min(cyc + 1, len(bs) - 1)] if cyc + 1 < len(bs) else t1 + 9
        hero_word(fg, 'DRAMAY', W / 2, H / 2 - 120, 260, WHITE, t, b0, 'abk', out_a)
        hero_word(fg, 'BAAZ!', W / 2, H / 2 + 150, 300, FOREST, t, b1, 'abk', out_a)
    else:             # one line, words light up on their beats
        wd = tw(fg, 'DRAMAY BAAZ!', 'abk', 210); x0 = W / 2 - wd / 2; w1 = tw(fg, 'DRAMAY ', 'abk', 210)
        on0 = t >= bs[0]; on1 = k % 2 == 1 or (len(bs) > 1 and t >= bs[1] and k >= 1)
        tx(fg, 'DRAMAY', x0, H / 2, 210, 'abk', WHITE if k % 2 == 0 else (1, 1, 1), out_a * (1 if k % 2 == 0 else 0.45), 'l')
        tx(fg, 'BAAZ!', x0 + w1, H / 2, 210, 'abk', FOREST, out_a * (1 if k % 2 == 1 else 0.3), 'l')


def chant_no(L, t, t0, t1, cx=W / 2, cy=H / 2, s=1.0, a=1.0, on_green=True):
    fg = L.fg
    bs = chant_beats(t0, t1) + [t1 + 9, t1 + 9]
    fg.save(); fg.translate(cx, cy); fg.scale(s, s)
    hero_word(fg, 'Ab no', 0, -190, 120, WHITE if on_green else GT, t, bs[0], 'axb', a)
    hero_word(fg, 'DRAMAY BAAZI!', 0, 40, 190, FOREST if on_green else FGC, t, bs[1], 'abk', a)
    q = sm((t - bs[2]) / 0.45)
    if q > 0:
        w = tw(fg, 'DRAMAY BAAZI!', 'abk', 190)
        strike(fg, -w / 2 - 20, 50, -w / 2 - 20 + (w + 40) * q, 50, 1, WHITE if on_green else GT, 18, a)
    fg.restore()


# ------------------------------------------------------------------ Apple Music "Sing" lyric panel
GROUPS = [[16.2, 18.1, 20.4, 23.0, 25.5, 27.3], [31.1, 32.9, 34.8, 36.6], [69.5, 71.6, 73.9, 76.5, 79.0, 80.8],
          [99.2, 100.9, 102.5, 104.6, 106.1, 109.8], [120.7, 122.6, 124.4], [130.2]]
HERO = (45.5, 49.3, 52.0, 57.7, 59.8, 61.5, 85.7, 89.7, 92.4)


def wrap(cr, words, size, width, fam='axb'):
    rows, cur = [], []
    for i, w_ in enumerate(words):
        trial = ' '.join(words[j] for j in cur + [i])
        if cur and tw(cr, trial, fam, size) > width: rows.append(cur); cur = []
        cur.append(i)
    rows.append(cur)
    return rows


def sing_panel(L, t, group, x0, width, cy, size=96):
    fg = L.fg
    starts = [wtimes(l)[0] - 0.12 for l in group]
    act = max(0, bisect.bisect_right(starts, t) - 1)
    # continuous focus position, eased between lines
    f = act + (0 if act + 1 >= len(group) else 0)
    if act > 0:
        f = act - 1 + ex((t - starts[act]) / 0.6)
    gap = size * 0.55
    blocks = []
    for l in group:
        ws = words_of(l); rows = wrap(fg, ws, size, width)
        blocks.append((l, ws, rows, len(rows) * size * 1.08))
    pos = [0.0]
    for b in blocks[:-1]: pos.append(pos[-1] + b[3] + gap)
    fi = int(math.floor(f)); fr = f - fi
    focus = lerp(pos[fi] + blocks[fi][3] / 2, pos[min(fi + 1, len(pos) - 1)] + blocks[min(fi + 1, len(blocks) - 1)][3] / 2, fr)
    g_in = ex((t - starts[0]) / 0.7)
    g_out = clamp((LYR_END[group[-1]] + 0.6 - t) / 0.5)
    ga = g_in * g_out
    if ga <= 0: return
    for j, (l, ws, rows, bh) in enumerate(blocks):
        y_top = cy + pos[j] - focus
        dist = abs(j - f)
        if dist > 2.2: continue
        if y_top + bh < -100 or y_top > H + 100: continue
        line_a = ga * (1.0 if dist < 0.5 else lerp(1.0, 0.28, clamp(dist)))
        if j > act: line_a = ga * 0.32 * clamp(2.2 - dist)
        line_a *= sm((y_top - 120) / 160) * sm((H - 60 - (y_top + bh)) / 160)   # fade at the frame edges
        wts = wtimes(l)
        sc = 1 - 0.04 * clamp(dist)
        fg.save(); fg.translate(x0, y_top); fg.scale(sc, sc)
        for ri, r in enumerate(rows):
            yy = ri * size * 1.08 + size * 0.54
            xx = 0
            font(fg, 'axb', size); sp = fg.text_extents(' ').x_advance
            for i in r:
                w_ = ws[i]; adv = tw(fg, w_, 'axb', size)
                t_on = wts[i]; t_next = wts[i + 1] if i + 1 < len(wts) else t_on + 0.5
                fill = clamp((t - t_on) / max(0.12, min(0.45, t_next - t_on)))
                base = (0.70, 0.72, 0.71)
                tc = word_tint(w_)
                if j == act and dist < 0.6:
                    tx(fg, w_, xx, yy, size, 'axb', base, line_a * 0.55, 'l')
                    if fill > 0:   # soft-edged fill gliding through the word, like Apple Music lyrics
                        edge = size * 0.6; xe = xx - edge + (adv + 2 * edge) * fill
                        fg.push_group(); tx(fg, w_, xx, yy, size, 'axb', tc, line_a, 'l'); fg.pop_group_to_source()
                        mg = cairo.LinearGradient(xe - edge, 0, xe, 0); mg.add_color_stop_rgba(0, 0, 0, 0, 1); mg.add_color_stop_rgba(1, 0, 0, 0, 0)
                        fg.mask(mg)
                else:
                    tx(fg, w_, xx, yy, size, 'axb', tc if j < act else base, line_a * (0.55 if j < act else 1), 'l')
                xx += adv + sp
        fg.restore()
        if j == act and l in SUBS:
            sa = ga * ex((t - wts[0] - 0.2) / 0.5) * clamp((LYR_END[l] + 0.3 - t) / 0.3)
            tx(fg, SUBS[l], x0, y_top + bh + 34, 30, 'am', (0.42, 0.45, 0.43), sa, 'l')


# ------------------------------------------------------------------ hero lines (choruses)
def hero_line(L, t, l):
    fg = L.fg
    ws = words_of(l); wts = wtimes(l)
    size = 200
    rows = wrap(fg, [w.upper() for w in ws], size, 1600, 'abk')
    if len(rows) > 2: size = 160; rows = wrap(fg, [w.upper() for w in ws], size, 1600, 'abk')
    total = len(rows) * size * 1.05
    out_q = sm((t - LYR_END[l] - 0.05) / 0.4)
    a_out = 1 - out_q
    y0 = H / 2 - total / 2 + size * 0.52 - 90 - out_q * 40
    for ri, r in enumerate(rows):
        font(fg, 'abk', size); sp = fg.text_extents(' ').x_advance
        advs = [tw(fg, ws[i].upper(), 'abk', size) for i in r]
        x = W / 2 - (sum(advs) + sp * (len(r) - 1)) / 2
        for k, i in enumerate(r):
            u = ws[i].upper(); q = ex((t - wts[i] + 0.04) / 0.5)
            if q > 0:
                c = word_tint(ws[i])
                style = l in (49.3, 89.7) and i >= 3          # "bhaag liya": the words leave to the right
                dx = sm((t - wts[i] - 0.5) / 0.7) * 1400 if style else 0
                sink = sm((t - wts[i] - 0.4) / 1.4) * 60 if l == 61.5 else 0
                fg.save(); fg.translate(x + advs[k] / 2 + dx, y0 + ri * size * 1.05 + (1 - q) * 40 + sink)
                s_ = lerp(1.06, 1.0, q) * (1 + 0.012 * beat_pulse(t, 9)); fg.scale(s_, s_)
                tx(fg, u, 0, 0, size, 'abk', c, a_out * clamp(q * 1.4) * (1 - 0.6 * clamp(dx / 1400)))
                fg.restore()
            x += advs[k] + sp
    if l in SUBS:
        sa = ex((t - wts[0] - 0.3) / 0.5) * a_out
        tx(fg, SUBS[l], W / 2, 975, 32, 'am', (0.4, 0.43, 0.41), sa)
    # quiet accents under the type
    if l in (45.5, 85.7, 49.3, 89.7):
        up = l in (45.5, 85.7); q = sm((t - l) / 1.6)
        pts = []
        for k in range(61):
            x_ = 260 + k * 23.3
            y_ = 880 - (k / 60) * 110 * (1 if up else -1) + 10 * math.sin(k * 0.7) - (0 if up else 110)
            pts.append((x_, y_))
        n = max(2, int(len(pts) * q))
        line(fg, pts[:n], 5, GT if up else RED, 0.9 * a_out)
    if l in (57.7, 59.8):
        lab, cc = ('BUY', BRIGHT_G) if l == 57.7 else ('SELL', RED)
        tap = beat_phase(t) < 0.18 and t > wts[0]
        cr = fg; cr.save(); cr.translate(W / 2, 830); s_ = 0.95 if tap else 1; cr.scale(s_, s_)
        rr(cr, -170, -52, 340, 104, 52); col(cr, cc, a_out * ex((t - l) / 0.5)); cr.fill()
        tx(cr, lab, 0, 0, 46, 'abk', INK if lab == 'BUY' else WHITE, a_out * ex((t - l) / 0.5)); cr.restore()


# ------------------------------------------------------------------ the floating iPhone
def iphone(L, cx, cy, s, t, screen, a=1.0, rot=0.0):
    if a <= 0.01 or s <= 0.01: return
    b = L.bg
    g = cairo.RadialGradient(cx, cy + 420 * s, 0, cx, cy + 420 * s, 360 * s)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.16 * a); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    b.save(); b.translate(cx, cy + 420 * s); b.scale(1, 0.18); b.translate(-cx, -(cy + 420 * s))
    b.set_source(g); b.arc(cx, cy + 420 * s, 360 * s, 0, TAU); b.fill(); b.restore()
    c = L.fg; c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(s, s)
    if a < 1: c.push_group()
    for k in range(6):
        rr(c, -222 - k * 6, -440 - k * 6 + 30, 444 + k * 12, 880 + k * 12, 74 + k * 6); c.set_source_rgba(0.1, 0.12, 0.1, 0.035); c.fill()
    rr(c, -222, -440, 444, 880, 74); col(c, (0.16, 0.17, 0.18)); c.fill()
    gg = cairo.LinearGradient(-222, -440, 222, 440)
    for st, v in ((0, 0.86), (0.35, 0.55), (0.5, 0.78), (0.7, 0.5), (1, 0.82)): gg.add_color_stop_rgb(st, v, v * 1.01, v * 1.02)
    rr(c, -222, -440, 444, 880, 74); c.set_line_width(5); c.set_source(gg); c.stroke()
    rr(c, -PW / 2, -PH / 2, PW, PH, 60); col(c, (0.035, 0.045, 0.05)); c.fill()
    c.save(); rr(c, -PW / 2, -PH / 2, PW, PH, 60); c.clip(); c.translate(-PW / 2, -PH / 2)
    screen(L, c, t)
    # screen glare
    gl = cairo.LinearGradient(0, 0, PW, PH); gl.add_color_stop_rgba(0, 1, 1, 1, 0.08); gl.add_color_stop_rgba(0.4, 1, 1, 1, 0.0)
    c.rectangle(0, 0, PW, PH); c.set_source(gl); c.fill()
    c.restore()
    rr(c, -62, -PH / 2 + 16, 124, 36, 18); col(c, (0, 0, 0)); c.fill()
    if a < 1: c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()


def blend_screens(sa, sb, q):
    """Cross-dissolve + slide between two phone screens."""
    def f(L, c, t):
        if q < 1:
            c.save(); c.translate(-q * 60, 0); c.push_group(); sa(L, c, t); c.pop_group_to_source(); c.paint_with_alpha(1 - q); c.restore()
        if q > 0:
            c.save(); c.translate((1 - q) * 60, 0); c.push_group(); sb(L, c, t); c.pop_group_to_source(); c.paint_with_alpha(q); c.restore()
    return f


def scr_upper(L, c, t):
    scr_index(L, c, t)
    p = ex((t - 20.9) / 0.5)
    rr(c, 20, 66 - (1 - p) * 120, 360, 92, 24); c.set_source_rgba(0.94, 0.99, 0.92, 0.97 * p); c.fill()
    c.arc(62, 112 - (1 - p) * 120, 20, 0, TAU); col(c, BRIGHT_G, p); c.fill()
    tx(c, '▲', 62, 112 - (1 - p) * 120, 18, 'axb', INK, p)
    tx(c, 'Upper lock', 96, 98 - (1 - p) * 120, 22, 'axb', INK, p, 'l'); tx(c, 'TIPWALA LTD  +7.50%', 96, 128 - (1 - p) * 120, 20, 'am', (0.3, 0.3, 0.3), p, 'l')


def scr_news(L, c, t):
    c.rectangle(0, 0, PW, PH); col(c, (0.98, 0.98, 0.97)); c.fill()
    status_bar(c, light=False)
    tx(c, 'News', 32, 112, 40, 'axb', INK, 1, 'l')
    tx(c, 'MARKETS', 32, 170, 18, 'mono', RED, 1, 'l')
    tx(c, 'Market mein', 32, 222, 40, 'axb', INK, 1, 'l'); tx(c, 'tezi!', 32, 270, 40, 'axb', GT, 1, 'l')
    tx(c, 'Daily Khabar · 6 min read', 32, 316, 18, 'am', (0.45, 0.45, 0.45), 1, 'l')
    rr(c, 24, 350, 352, 240, 18); col(c, (0.93, 0.96, 0.92)); c.fill()
    pts = [(44 + k * 10.5, 560 - k * 4.5 - 25 * math.sin(k * 0.6)) for k in range(31)]
    line(c, pts, 4, GT)
    for k in range(4): rr(c, 32, 620 + k * 40, 336 - k * 60, 14, 7); col(c, (0.85, 0.86, 0.85)); c.fill()


def scr_allin(L, c, t):
    status_bar(c)
    tx(c, 'Transfer', 32, 112, 34, 'axb', WHITE, 1, 'l')
    q = sm((t - 28.3) / 1.4)
    tx(c, 'Savings account', 32, 190, 22, 'am', (0.65, 0.68, 0.66), 1, 'l')
    tx(c, f"Rs {1000000 * (1 - q):,.0f}", 32, 240, 50, 'axb', WHITE, 1, 'l')
    rr(c, 32, 290, 336, 12, 6); c.set_source_rgba(1, 1, 1, 0.12); c.fill(); rr(c, 32, 290, 336 * (1 - q), 12, 6); col(c, GOLD); c.fill()
    tx(c, '↓', 200, 370, 40, 'axb', (0.6, 0.62, 0.6))
    tx(c, 'TIPWALA LTD', 32, 450, 22, 'am', (0.65, 0.68, 0.66), 1, 'l')
    tx(c, f"Rs {1000000 * q:,.0f}", 32, 500, 50, 'axb', BRIGHT_G, 1, 'l')
    p = ex((t - 29.5) / 0.4)
    rr(c, 32, 600, 336, 96, 48); col(c, BRIGHT_G, p); c.fill(); tx(c, 'ALL IN', 200, 648, 36, 'abk', INK, p)


def scr_crash(L, c, t):
    status_bar(c)
    v = idx_value(t)
    tx(c, 'KSE-100', 32, 150, 24, 'mono', (0.6, 0.65, 0.68), 1, 'l'); tx(c, f"{v:,.0f}", 32, 210, 58, 'axb', WHITE, 1, 'l')
    tx(c, f"{(v - idx_ref(t)) / idx_ref(t) * 100:.2f}%  today", 32, 266, 24, 'mono', RED, 1, 'l')
    q = sm((t - 34.8) / 1.0)
    pts = [(20 + k * 9.2, 330 + (k / 39) ** 2 * 300 * q + 16 * math.sin(k * 1.2)) for k in range(40)]
    line(c, pts, 4, RED)
    p = ex((t - 35.3) / 0.5)
    rr(c, 20, 66 - (1 - p) * 120, 360, 92, 24); c.set_source_rgba(1.0, 0.94, 0.94, 0.97 * p); c.fill()
    c.arc(62, 112 - (1 - p) * 120, 20, 0, TAU); col(c, RED, p); c.fill(); tx(c, '▼', 62, 112 - (1 - p) * 120, 18, 'axb', WHITE, p)
    tx(c, 'Lower lock', 96, 98 - (1 - p) * 120, 22, 'axb', INK, p, 'l'); tx(c, 'TIPWALA LTD  −7.50%', 96, 128 - (1 - p) * 120, 20, 'am', (0.3, 0.3, 0.3), p, 'l')


def scr_stoploss(L, c, t):
    c.rectangle(0, 0, PW, PH); col(c, (0.95, 0.95, 0.96)); c.fill()
    status_bar(c, light=False)
    tx(c, 'Order settings', 32, 112, 34, 'axb', INK, 1, 'l')
    for i, (lab, on) in enumerate((('Price alerts', True), ('Stop loss', None), ('Auto-invest', False))):
        y = 190 + i * 96
        rr(c, 20, y, 360, 80, 18); col(c, (1, 1, 1)); c.fill()
        tx(c, lab, 44, y + 40, 26, 'asb', INK, 1, 'l')
        off = sm((t - 37.3) / 0.4) if on is None else (0 if on else 1)
        rr(c, 296, y + 22, 64, 36, 18); col(c, mix(BRIGHT_G, (0.82, 0.82, 0.84), off)); c.fill()
        c.arc(lerp(342, 314, off), y + 40, 15, 0, TAU); col(c, (1, 1, 1)); c.fill()
    p = ex((t - 38.2) / 0.5)
    tx(c, 'Stop loss turned off', 200, 540, 22, 'am', RED, p)


def scr_chart(mode):
    def f(L, c, t):
        status_bar(c)
        tx(c, 'TIPWALA LTD', 32, 120, 30, 'axb', WHITE, 1, 'l')
        def yv(k): return 470 + 150 * math.sin(k / 9 - 0.5) + 14 * math.sin(k * 0.9)
        n = 40; rev = 0.3 + 0.7 * sm((t - 69.3) / 4.5)
        pts = [(20 + k * 9.2, yv(k)) for k in range(max(2, int(n * rev)))]
        line(c, pts, 4, WHITE, 0.95)
        for k_, lab, cc, mt in ((14, 'SELL', RED, 70.3), (27, 'BUY', BRIGHT_G, 72.6), (36, 'SELL', RED, 73.4)):
            if t < mt or k_ >= len(pts): continue
            p = ex((t - mt) / 0.4); x, y = 20 + k_ * 9.2, yv(k_)
            c.arc(x, y, 9 * p, 0, TAU); col(c, cc); c.fill()
            dy = 46 if lab == 'SELL' else -46
            rr(c, x - 38, y + dy - 18, 76, 36, 18); col(c, cc, p); c.fill(); tx(c, lab, x, y + dy, 16, 'abk', INK if cc == BRIGHT_G else WHITE, p)
        tx(c, 'Sold low, bought high', 200, 760, 20, 'am', (0.65, 0.68, 0.66), clamp((t - 73.6) / 0.4))
    return f


# per-line phone screens; None = no phone for that line
_SCR = {}


def screen_for(l):
    if l in _SCR: return _SCR[l]
    wt = wtimes(l)
    if l == 16.2: f = scr_index
    elif l == 18.1: f = scr_buy(wt[3])
    elif l == 20.4: f = scr_upper
    elif l == 23.0: f = scr_chat([('Bhai ek tip hai...', wt[1]), ('Ye share pakka 10x!', wt[3]), ('Andar ki khabar hai', wt[4]),
                                  ('Sab laga do!!!', wt[5] + 0.2)])
    elif l == 25.5: f = scr_news
    elif l == 27.3: f = scr_allin
    elif l == 34.8: f = scr_crash
    elif l == 36.6: f = scr_stoploss
    elif l in (69.5, 71.6, 73.9): f = scr_chart('x')
    elif l == 76.5: f = scr_portfolio(76.8)
    elif l in (79.0, 80.8): f = scr_call
    else: f = None
    _SCR[l] = f
    return f


def phone_stage(L, t, group, cx=1430, cy=560, s=0.86):
    starts = [wtimes(l)[0] - 0.12 for l in group]
    act = max(0, bisect.bisect_right(starts, t) - 1)
    scr = screen_for(group[act])
    if scr is None: return False
    prev = screen_for(group[act - 1]) if act > 0 else None
    q = sm((t - starts[act]) / 0.45) if prev else 1
    fn = blend_screens(prev, scr, q) if (prev and q < 1) else scr
    a = ex((t - starts[0] + 0.2) / 0.7) * clamp((LYR_END[group[-1]] + 0.6 - t) / 0.5)
    first = [i for i, l in enumerate(group) if screen_for(l)][0]
    if act == first and screen_for(group[first]) and first > 0:
        a *= ex((t - starts[first]) / 0.6)
    rot = 0.012 * math.sin(t * 0.6)
    if group[act] == 73.9:   # "ulta seedha": the phone turns upside down and back on the beats
        hits = [b for b in BEATS if 74.0 <= b <= min(t, 76.2)]
        k = len(hits)
        if k:
            rot += math.pi * lerp((k - 1) % 2, k % 2, sm((t - hits[-1]) / 0.3))
    iphone(L, cx, cy + 10 * math.sin(t * 0.9), s * lerp(0.94, 1, a), t, fn, a, rot)
    return True


# ------------------------------------------------------------------ cards (bridge, dream, final)
def card(L, x, y, w, h, t, t_on, a=1.0, tint=WHITE, ta=0.12):
    q = ex((t - t_on) / 0.6) * a
    if q <= 0: return 0
    glass(L, x, y + (1 - q) * 40, w, h, 36, q, tint=tint, ta=ta)
    return q


def side_cards(L, t, l, x=1180, a=1.0):
    fg = L.fg; wt = wtimes(l)
    if l == 31.1:
        q = card(L, x, 300, 560, 460, t, wt[3] - 0.1, a, tint=GOLD, ta=0.08)
        icon(fg, 'crown', x + 280, 470, 2.0, GOLD, q); tx(fg, 'Raja', x + 280, 650, 64, 'axb', FGC, q)
    elif l == 32.9:
        for i, (k, lab) in enumerate((('car', 'Gaadi'), ('house', 'Bangla'), ('bag', 'Sab'))):
            q = card(L, x + (i % 2) * 300, 200 + (i // 2) * 330 + (i == 2) * 0, 270, 290, t, wt[i] - 0.1, a, tint=GOLD, ta=0.06)
            icon(fg, k, x + 135 + (i % 2) * 300, 300 + (i // 2) * 330, 1.2, GOLD, q)
            tx(fg, lab, x + 135 + (i % 2) * 300, 420 + (i // 2) * 330, 40, 'axb', FGC, q)
    elif l == 99.2:
        q = card(L, x - 40, 380, 640, 150, t, wt[0], a)
        fg.arc(x + 30, 455, 34, 0, TAU); col(fg, (0.6, 0.64, 0.66), q); fg.fill(); tx(fg, 'A', x + 30, 455, 32, 'axb', WHITE, q)
        tx(fg, 'Abba', x + 90, 428, 26, 'axb', FGC, q, 'l'); tx(fg, 'Arre bas kar yaar.', x + 90, 478, 30, 'am', (0.3, 0.32, 0.3), q, 'l')
    elif l == 100.9:
        for i, m in enumerate(('10x pakka!', 'Andar ki khabar', 'Sab laga do!')):
            q = card(L, x, 250 + i * 170, 560, 130, t, l + i * 0.12, a)
            tx(fg, m, x + 280, 315 + i * 170, 40, 'asb', FGC, q)
            strike(fg, x + 60, 318 + i * 170, x + 500, 312 + i * 170, sm((t - wt[2] - i * 0.1) / 0.4), RED, 7, q)
    elif l == 102.5:
        q = card(L, x, 220, 580, 620, t, l, a)
        tx(fg, 'Before you invest', x + 50, 290, 30, 'am', (0.4, 0.42, 0.4), q, 'l')
        for i, lab in enumerate(('Earnings', 'Debt', 'Valuation', 'Risk')):
            it = wt[min(i, len(wt) - 1)] + 0.15 * i
            p = ex((t - it) / 0.4) * q
            fg.arc(x + 80, 380 + i * 110, 26, 0, TAU); col(fg, BRIGHT_G, p); fg.fill(); check(fg, x + 80, 380 + i * 110, 28, WHITE, p, sm((t - it) / 0.35))
            tx(fg, lab, x + 130, 380 + i * 110, 48, 'axb', FGC, p, 'l')
    elif l == 104.6:
        q = card(L, x + 40, 240, 480, 520, t, l, a)
        rr(fg, x + 40, 240, 480, 110, 36); col(fg, RED, 0.9 * q); fg.fill()
        fl = sm((t - wt[3] + 0.15) / 0.5)
        fg.save(); fg.translate(x + 280, 560); fg.scale(1, max(0.02, abs(math.cos(fl * math.pi))))
        tx(fg, 'Aaj' if fl < 0.5 else 'Kal', 0, 0, 150, 'abk', FGC if fl < 0.5 else GT, q); fg.restore()
    elif l == 106.1:
        for i, (lab, k) in enumerate((('Jaadu', 1), ('Kismat', 4))):
            q = card(L, x, 260 + i * 290, 560, 220, t, wt[k] - 0.1, a)
            tx(fg, lab, x + 280, 370 + i * 290, 90, 'abk', FGC, q)
            w_ = tw(fg, lab, 'abk', 90)
            strike(fg, x + 280 - w_ / 2 - 20, 375 + i * 290, x + 280 + w_ / 2 + 20, 365 + i * 290, sm((t - wt[k + 1] + 0.05) / 0.35), RED, 12, q)
    elif l == 109.8:
        for i, s_ in enumerate(('Research', 'Plan', 'Invest', 'Hold')):
            q = card(L, x + 60, 200 + i * 165, 460, 130, t, l + 0.3 + i * 0.35, a, tint=BRIGHT_G if i == 3 else WHITE, ta=0.1)
            tx(fg, f"0{i + 1}", x + 120, 265 + i * 165, 30, 'mono', GT, q, 'l'); tx(fg, s_, x + 200, 265 + i * 165, 50, 'axb', FGC, q, 'l')
    elif l == 120.7:
        q = card(L, x, 260, 580, 540, t, l, a)
        tx(fg, 'PSX ANALYZER', x + 50, 330, 24, 'mono', GT, q, 'l')
        for i, s_ in enumerate(('Score any listed', 'company in plain', 'English.')):
            tx(fg, s_, x + 50, 410 + i * 56, 46, 'axb', FGC, q, 'l')
        for i in range(5):
            p = q * (0.2 + 0.8 * (i < 1 + int(sm((t - l - 0.4) / 1.2) * 4)))
            rr(fg, x + 50 + i * 100, 640, 80, 100, 16); col(fg, BRIGHT_G, p); fg.fill()
    elif l == 122.6:
        q = card(L, x, 260, 580, 540, t, l, a)
        tx(fg, 'SIP CALCULATOR', x + 50, 330, 24, 'mono', GT, q, 'l')
        tx(fg, 'Every month,', x + 50, 410, 46, 'axb', FGC, q, 'l'); tx(fg, 'steadily.', x + 50, 466, 46, 'axb', FGC, q, 'l')
        for i in range(9):
            hh = 30 + i * 22 * sm((t - l - 0.2) / 1.4)
            rr(fg, x + 50 + i * 55, 760 - hh, 38, hh, 10); col(fg, BRIGHT_G, q * 0.9); fg.fill()
    elif l == 124.4:
        q = card(L, x, 260, 580, 540, t, l, a)
        tx(fg, 'PATIENCE', x + 50, 330, 24, 'mono', GT, q, 'l')
        pts = [(x + 50 + k * 11.5, 720 - k * 7 * sm((t - l) / 1.6) - 10 * math.sin(k * 0.8)) for k in range(42)]
        line(fg, pts, 6, GT, q)


# ------------------------------------------------------------------ final section + outro
def final_section(L, t):
    fg = L.fg
    c_ = chant_now(t)
    if c_ and c_[2] == NO:
        t0, t1, _ = c_
        big = t < snap(t0) + (1.6 if t0 in (114.0, 126.4) else 99)
        if big:
            chant_no(L, t, t0, t1, a=clamp((t1 + 0.15 - t) / 0.15) if t0 >= 134.9 else 1)
            return
    if 115.5 <= t < 120.6:
        a = clamp((120.6 - t) / 0.4)
        tx(fg, 'How it works.', 140, 230, 84, 'abk', FGC, ex((t - 115.5) / 0.6) * a, 'l')
        steps = (('01', 'Learn the Market', 'Free Bootcamp & Analyzer'), ('02', 'Open PSX Account', 'Through Floret Capitals'),
                 ('03', 'Start Investing', 'With real confidence'))
        for i, (n, h, s_) in enumerate(steps):
            bt = BEATS[beat_index(115.7) + 1 + i * 2]
            q = card(L, 140 + i * 560, 380, 520, 380, t, bt, a, tint=BRIGHT_G if i == 1 else WHITE, ta=0.1)
            tx(fg, n, 200 + i * 560, 460, 52, 'mono', GT, q, 'l')
            tx(fg, h, 200 + i * 560, 600, 50, 'axb', FGC, q, 'l')
            tx(fg, s_, 200 + i * 560, 666, 30, 'am', (0.38, 0.41, 0.39), q, 'l')
        return
    for grp in ([120.7, 122.6, 124.4],):
        if wtimes(grp[0])[0] - 0.2 <= t < LYR_END[grp[-1]] + 0.6:
            sing_panel(L, t, grp, 140, 900, 470)
            starts = [wtimes(l)[0] - 0.12 for l in grp]; act = max(0, bisect.bisect_right(starts, t) - 1)
            for j, l in enumerate(grp):
                aa = clamp((t - starts[j] + 0.1) / 0.3) * (clamp((starts[j + 1] - t) / 0.3) if j + 1 < len(grp) else clamp((LYR_END[l] + 0.6 - t) / 0.5))
                if aa > 0: side_cards(L, t, l, a=aa)
            return
    if 126.4 <= t < 134.9:
        stages = (128.6, 130.45, 130.95, 131.45, 132.55, 133.05)
        ph = scr_web(stages)
        if 130.0 <= t < 132.2:
            sing_panel(L, t, [130.2], 140, 900, 470)
        elif t < 130.0:
            q = ex((t - 127.7) / 0.6)
            tx(fg, 'Open your PSX', 140, 430, 96, 'abk', FGC, q, 'l'); tx(fg, 'account online.', 140, 545, 96, 'abk', GT, ex((t - 128.0) / 0.6), 'l')
            tx(fg, 'Fully guided. Through Floret Capitals.', 140, 640, 34, 'am', (0.38, 0.41, 0.39), ex((t - 128.4) / 0.6), 'l')
        else:
            tx(fg, 'Built on trust.', 140, 300, 84, 'abk', FGC, ex((t - 132.4) / 0.6), 'l')
            for i, b_ in enumerate(('PSX Licensed Brokerage', 'SECP Compliant', 'Personal Relationship Managers')):
                q = ex((t - 132.9 - i * 0.25) / 0.5)
                fg.arc(170, 430 + i * 110, 24, 0, TAU); col(fg, BRIGHT_G, q); fg.fill(); check(fg, 170, 430 + i * 110, 26, WHITE, q)
                tx(fg, b_, 220, 430 + i * 110, 46, 'axb', FGC, q, 'l')
        iphone(L, 1430, 560 + 10 * math.sin(t * 0.9), 0.86 * lerp(0.94, 1, ex((t - 127.6) / 0.7)), t, ph, ex((t - 127.6) / 0.7) * clamp((134.9 - t) / 0.3),
               0.012 * math.sin(t * 0.6))
        return
    if 137.3 <= t < 139.0:
        a = clamp((139.0 - t) / 0.25)
        for i, (s_, c) in enumerate((('Learn.', FGC), ('Open your account.', FGC), ('Start investing.', GT))):
            tx(fg, s_, W / 2, 360 + i * 150, 120, 'abk', c, ex((t - 137.3 - i * 0.4) / 0.5) * a)
        return
    if t >= 141.6:
        chant_no(L, t, 139.0, 143.1, a=clamp((143.1 - t) / 0.3))


def outro(L, t):
    fg = L.fg
    if 146.4 <= t < 149.0:
        a = clamp((149.0 - t) / 0.3)
        tx(fg, 'because', W / 2, 300, 72, 'am', WHITE, ex((t - snap(146.4)) / 0.5) * a)
        chant_no(L, t, 146.75, 149.0, W / 2, 600, 0.85, a)
        return
    words = (('Start', 143.4), ('trading', 143.85), ('in PSX', 144.3), ('today.', 144.75))
    if t < 146.4:
        a = clamp((146.4 - t) / 0.2)
        x = 0
        full = tw(fg, 'Start trading in PSX today.', 'abk', 130)
        x0 = W / 2 - full / 2
        for s_, wt in words:
            adv = tw(fg, s_ + ' ', 'abk', 130)
            q = ex((t - snap(wt)) / 0.5)
            tx(fg, s_, x0 + x, H / 2 + (1 - q) * 30, 130, 'abk', GT if s_ == 'in PSX' else FGC, q * a, 'l')
            x += adv
        return
    a = ex((t - 149.0) / 0.8)
    tx(fg, 'Start trading in PSX today.', W / 2, 200, 84, 'abk', FGC, a)
    u = L.ui; u.save(); u.set_matrix(fg.get_matrix()); brand_img(u, 'logo', W / 2, 470, 860 * lerp(0.96, 1, a), a, dark=False); u.restore()
    w1 = tw(fg, 'because ', 'am', 44); w2 = tw(fg, 'AB NO DRAMAY BAAZI!', 'abk', 58); x0 = W / 2 - (w1 + w2) / 2
    tx(fg, 'because', x0, 760, 44, 'am', (0.4, 0.43, 0.41), ex((t - 149.6) / 0.8), 'l')
    k = 1 + 0.02 * beat_pulse(t, 9) * (t > 156.2)
    fg.save(); fg.translate(x0 + w1 + w2 / 2, 760); fg.scale(k, k); tx(fg, 'AB NO DRAMAY BAAZI!', 0, 0, 58, 'abk', GT, ex((t - 149.9) / 0.8)); fg.restore()
    q = ex((t - 150.4) / 0.8)
    rr(fg, W / 2 - 240, 850, 480, 96, 48); col(fg, BRIGHT_G, q); fg.fill()
    tx(fg, 'Open Account', W / 2, 898, 36, 'axb', FOREST, q)
    tx(fg, 'flostocks.com', W / 2, 990, 32, 'am', (0.35, 0.38, 0.36), q)
    tx(fg, 'Illustrative content. Investing in securities involves risk.', W / 2, 1050, 18, 'am', (0.55, 0.58, 0.56), q * 0.9)


def intro(L, t):
    fg = L.fg
    if t >= 13.6:
        a = clamp((snap(16.2) - 0.1 - t) / 0.35)
        tx(fg, 'Dramay Baaz.', W / 2, 470, 190, 'abk', FGC, ex((t - 13.6) / 0.7) * a)
        tx(fg, 'A PSX story. Starring you.', W / 2, 640, 50, 'am', (0.38, 0.41, 0.39), ex((t - 14.3) / 0.7) * a)
        return
    v = idx_value(t)
    q = ex((t - 1.9) / 0.6)
    tx(fg, 'KSE-100', W / 2, 400, 40, 'mono', (0.45, 0.48, 0.46), q)
    tx(fg, f"{v:,.0f}", W / 2, 540, 200, 'abk', FGC, q)


# ------------------------------------------------------------------ frame
def render(L, t):
    kt.BEAT_T[0] = t
    sec = section(t)[1]
    c_ = chant_now(t)
    green = False
    if c_:
        if c_[2] == DB and sec != 'outro': green = True
        elif c_[2] == NO:
            green = t < snap(c_[0]) + (1.6 if c_[0] in (114.0, 126.4) else 99) or c_[0] >= 134.9
    if sec == 'outro' and snap(146.4) <= t < 149.0: green = True
    if t >= 141.6 and t < 143.1: green = True
    # gentle global camera: slow drift, tiny beat breath
    zoom = 1 + 0.004 * beat_pulse(t, 8) * clamp(env('bass', t) * 1.5) + (0.012 * beat_pulse(t, 9) if green else 0)
    for cr in L.all():
        cr.translate(W / 2, H / 2); cr.scale(zoom, zoom); cr.translate(-W / 2 + 6 * math.sin(t * 0.21), -H / 2 + 5 * math.cos(t * 0.17))
    if green: backdrop_green(L, t, 0)
    else: backdrop(L, t)
    if sec == 'final' and t >= 114.0:
        final_section(L, t)
    elif sec == 'outro':
        outro(L, t)
    elif c_ and c_[2] == DB:
        chant_db(L, t, c_)
    else:
        done = False
        for grp in GROUPS[:4]:
            if wtimes(grp[0])[0] - 0.4 <= t < LYR_END[grp[-1]] + 0.7:
                has_phone = any(screen_for(l) for l in grp)
                starts = [wtimes(l)[0] - 0.12 for l in grp]; act = max(0, bisect.bisect_right(starts, t) - 1)
                showing_phone = has_phone and screen_for(grp[act]) is not None
                cards_line = grp[act] in (31.1, 32.9, 99.2, 100.9, 102.5, 104.6, 106.1, 109.8)
                if showing_phone or cards_line:
                    sing_panel(L, t, grp, 140, 900, 470)
                    if showing_phone: phone_stage(L, t, grp)
                    for j, l in enumerate(grp):
                        aa = clamp((t - starts[j] + 0.1) / 0.3) * (clamp((starts[j + 1] - t) / 0.3) if j + 1 < len(grp) else clamp((LYR_END[l] + 0.6 - t) / 0.5))
                        if aa > 0: side_cards(L, t, l, a=aa)
                else:
                    sing_panel(L, t, grp, 260, 1400, 470, 110)
                done = True
                break
        if not done:
            for l in HERO:
                if wtimes(l)[0] - 0.15 <= t < LYR_END[l] + 0.5:
                    hero_line(L, t, l); done = True; break
        if not done and sec == 'intro':
            intro(L, t)
    for cr in L.all(): cr.reset_clip(); cr.identity_matrix()
    if t < 143.1:
        a = clamp((t - 2.0) / 0.8)
        if not green: brand_img(L.ui, 'wordmark', 190, 70, 250, a, dark=False)
