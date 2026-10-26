"""Dramay Baaz, kinetic typography edition.
The lyrics are the whole video; objects (sun, phone, chat bubbles, charts) live inside the type.
The viewer is the character. FloStocks brand colours, frosted-glass panels, beat-synced motion.

Drawing happens on four layers that render_kt.py composites:
  L.bg   - backdrop (light orbs, echo words); glass panels blur this layer
  L.mask - where glass panels are (alpha); filled by glass()
  L.fg   - type, glass tints/borders, objects
  L.ui   - official logo artwork only (no effects)
"""
import cairo, math, random, json
from lib import (W, H, BEATS, beat_pulse, beat_index, beat_phase, env, clamp, lerp, ease_out, ease_in, ease_io, back_out,
                 mix, TAU, brand_img, STYLE)
from scenes import LYRICS, LYR_END, CHANTS, DB, NO, section, idx_value, idx_ref

WT = {float(k): v for k, v in json.load(open('audio/word_times.json')).items()}
DUR = 159.42


def hexc(h): return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


# FloStocks site tokens
G = hexc('#38D100'); GD = hexc('#1F7A00'); FOREST = hexc('#062600'); INK = hexc('#0A0E0A'); INK2 = hexc('#0B0F14')
RED = hexc('#E5484D')
LIGHT = True
FGC = INK_ = hexc('#0A0E0A') if LIGHT else (1, 1, 1)
GT = hexc('#2E9D00') if LIGHT else hexc('#38D100'); MUTED = (0.32, 0.36, 0.33) if LIGHT else (0.82, 0.86, 0.84); GOLD = hexc('#E6A817'); GOLDL = hexc('#FFE79A'); WASH = hexc('#EAF9E4'); WHITE = (1, 1, 1)

FONTS = {'xb': 'Manrope XB', 'b': 'Manrope B', 'm': 'Manrope M', 'inter': 'Inter', 'mono': 'IBM Plex Mono'}

SUBS = {16.2: 'You open the KSE-100 first thing in the morning', 18.1: "Before your chai, you've already hit BUY",
        20.4: 'You\'re shouting: "Upper lock today!"', 23.0: "Your tip? From your cousin's friend",
        25.5: 'Plus a little something from the newspaper', 27.3: 'So you bet your entire savings on it',
        31.1: "You thought you'd become a king", 32.9: "Car, bungalow, you'd have it all", 34.8: 'Then lower lock hit you hard',
        36.6: 'And you even forgot your stop loss', 45.5: 'You saw green, you danced', 49.3: 'You saw red, you ran',
        52.0: 'You took it out on the screen', 57.7: 'You bought without thinking', 59.8: 'Then sold in fear',
        61.5: 'Then sat down and cried', 69.5: 'Market dips: you panic sell', 71.6: 'Market rallies: you buy again',
        73.9: 'Always doing it backwards', 76.5: 'Your portfolio turned red', 79.0: 'Abba held his head',
        80.8: '"The market is rigged, Abba!" you keep saying', 85.7: 'You saw green, you danced', 89.7: 'You saw red, you ran',
        92.4: 'You took it out on the screen', 99.2: 'Enough now, yaar', 100.9: 'Stop running on guesswork',
        102.5: 'Research first, then invest', 104.6: 'Change tomorrow, starting today', 106.1: "It's not magic. It's not luck.",
        109.8: 'Strategy finds the way', 120.7: 'You trade with careful thought', 122.6: 'You make a plan, and you hold',
        124.4: 'Patience gets you there', 130.2: 'No tension, only direction'}


class Layers:
    def __init__(self, bg, fg, mask, ui):
        self.bg, self.fg, self.mask, self.ui = bg, fg, mask, ui

    def all(self): return (self.bg, self.fg, self.mask, self.ui)


# ------------------------------------------------------------------ primitives
def col(cr, c, a=1.0): cr.set_source_rgba(c[0], c[1], c[2], a)


def rr(cr, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2)); cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -TAU / 4, 0); cr.arc(x + w - r, y + h - r, r, 0, TAU / 4)
    cr.arc(x + r, y + h - r, r, TAU / 4, TAU / 2); cr.arc(x + r, y + r, r, TAU / 2, 3 * TAU / 4); cr.close_path()


def font(cr, fam, size):
    cr.select_font_face(FONTS[fam], cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_BOLD if fam in ('mono', 'inter') else cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(max(1, size))


def tw(cr, s, fam, size):
    font(cr, fam, size); return cr.text_extents(s).x_advance


def tx(cr, s, x, y, size, fam='xb', c=WHITE, a=1.0, align='c'):
    """Text with its vertical centre (cap height) at y."""
    if a <= 0.003: return 0
    font(cr, fam, size); adv = cr.text_extents(s).x_advance
    xx = x - adv / 2 if align == 'c' else x if align == 'l' else x - adv
    cr.move_to(xx, y + size * 0.36); col(cr, c, a)
    m = cr.get_matrix(); dev = size * math.sqrt(abs(m.xx * m.yy - m.xy * m.yx))
    if dev > 300 or FORCE_PATH[0]:   # FreeType refuses very large glyph bitmaps; big type is drawn as vector paths
        cr.text_path(s); cr.fill()
    else:
        cr.show_text(s)
    return adv


def line(cr, pts, w, c, a=1.0):
    cr.set_line_width(w); cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    cr.move_to(*pts[0])
    for p in pts[1:]: cr.line_to(*p)
    col(cr, c, a); cr.stroke()


def pop(t, t0, d=0.3): return back_out(clamp((t - t0) / d)) if t >= t0 else 0.0


def fade(t, t0, t1, fi=0.2, fo=0.25): return clamp((t - t0) / fi) * clamp((t1 - t) / fo)


def glass(L, x, y, w, h, r=30, a=1.0, tint=WHITE, ta=0.075, border=0.32, shadow=True):
    if LIGHT:
        ta = ta * 4.0 if tint == WHITE else ta * 1.6
    k = 1 + 0.008 * beat_pulse(BEAT_T[0], 9); cx_, cy_ = x + w / 2, y + h / 2
    x, y, w, h = cx_ - w * k / 2, cy_ - h * k / 2, w * k, h * k
    """Frosted glass panel: the compositor blurs the backdrop under the mask; here we add tint, sheen and edge."""
    if a <= 0.01: return
    m = L.mask; m.save(); m.set_matrix(L.fg.get_matrix()); rr(m, x, y, w, h, r); m.set_source_rgba(1, 1, 1, a); m.fill(); m.restore()
    c = L.fg
    if shadow:
        c.save(); c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        c.rectangle(x - 200, y - 200, w + 400, h + 400); rr(c, x, y, w, h, r); c.clip()
        for k in range(4):
            rr(c, x - k * 6, y - k * 6 + 16, w + k * 12, h + k * 12, r + k * 6); c.set_source_rgba(0.05, 0.12, 0.05, (0.035 if LIGHT else 0.06) * a); c.fill()
        c.restore()
    g = cairo.LinearGradient(x, y, x + w * 0.4, y + h)
    g.add_color_stop_rgba(0, *tint, ta * 1.9 * a); g.add_color_stop_rgba(1, *tint, ta * 0.6 * a)
    rr(c, x, y, w, h, r); c.set_source(g); c.fill()
    g2 = cairo.LinearGradient(x, y, x, y + h)
    g2.add_color_stop_rgba(0, 1, 1, 1, border * a); g2.add_color_stop_rgba(0.5, 1, 1, 1, border * 0.25 * a); g2.add_color_stop_rgba(1, 1, 1, 1, border * 0.55 * a)
    rr(c, x + 0.75, y + 0.75, w - 1.5, h - 1.5, r); c.set_line_width(1.8); c.set_source(g2); c.stroke()
    if LIGHT:
        rr(c, x, y, w, h, r); c.set_line_width(1.2); c.set_source_rgba(0.04, 0.1, 0.04, 0.10 * a); c.stroke()


def glass_pill(L, cx, cy, text_, size=30, fam='b', c=WHITE, a=1.0, pad=34, tint=WHITE, ta=0.08):
    w = tw(L.fg, text_, fam, size) + pad * 2; h = size * 2.0
    glass(L, cx - w / 2, cy - h / 2, w, h, h / 2, a, tint=tint, ta=ta)
    tx(L.fg, text_, cx, cy, size, fam, c, a)
    return w


# ------------------------------------------------------------------ backdrop
PALS = {
    'brand': ((0.015, 0.03, 0.02), [GT, GD, FOREST, (0.1, 0.35, 0.12)]),
    'morning': ((0.05, 0.035, 0.03), [GOLD, (0.95, 0.42, 0.12), GD, (0.55, 0.22, 0.35)]),
    'gold': ((0.045, 0.035, 0.01), [GOLD, GOLD, (0.65, 0.38, 0.0), GD]),
    'red': ((0.055, 0.01, 0.015), [RED, (0.6, 0.05, 0.1), (0.35, 0.0, 0.06), (0.9, 0.35, 0.2)]),
    'green': ((0.01, 0.05, 0.012), [GT, GD, (0.6, 1.0, 0.3), FOREST]),
    'blue': ((0.02, 0.03, 0.06), [(0.2, 0.36, 0.75), (0.1, 0.2, 0.45), (0.35, 0.55, 0.85), INK2]),
    'calm': ((0.015, 0.045, 0.04), [(0.1, 0.55, 0.45), (0.15, 0.42, 0.2), GD, (0.3, 0.6, 0.5)]),
}
LINE_PAL = {16.2: 'morning', 18.1: 'morning', 20.4: 'green', 23.0: 'morning', 25.5: 'morning', 27.3: 'gold',
            31.1: 'gold', 32.9: 'gold', 34.8: 'red', 36.6: 'red', 45.5: 'green', 49.3: 'red', 52.0: 'red', 57.7: 'green',
            59.8: 'red', 61.5: 'blue', 69.5: 'red', 71.6: 'green', 73.9: 'brand', 76.5: 'red', 79.0: 'red', 80.8: 'red',
            85.7: 'green', 89.7: 'red', 92.4: 'red'}


def pal_name(t):
    sec = section(t)[1]
    if sec == 'bridge': return 'calm'
    if sec in ('final', 'outro'): return 'brand' if t < 143.1 else 'green' if t < 149 else 'brand'
    cur = None
    for l in LYRICS:
        if l[0] - 0.1 <= t: cur = l[0]
    if cur is not None and cur in LINE_PAL and t < LYR_END[cur] + 0.6: return LINE_PAL[cur]
    if sec in ('verse1',): return 'morning'
    if sec in ('dream',): return 'gold'
    if sec in ('crash',): return 'red'
    return 'brand'


def palette(t):
    ws = {}
    for k in range(7):
        n = pal_name(t - k * 0.08); ws[n] = ws.get(n, 0) + 1
    tot = sum(ws.values())
    base = (0, 0, 0); orbs = [(0, 0, 0)] * 4
    for n, w in ws.items():
        b, o = PALS[n]; f = w / tot
        base = tuple(x + y * f for x, y in zip(base, b))
        orbs = [tuple(x + y * f for x, y in zip(oo, cc)) for oo, cc in zip(orbs, o)]
    return base, orbs


CHANT_GREEN = [False]
FORCE_PATH = [False]
BEAT_T = [0.0]


def chant_green(t):
    sec = section(t)[1]
    if sec == 'outro': return snap(146.4) <= t < 149.0
    for t0, t1, ph in CHANTS:
        if snap(t0) - 0.02 <= t < t1:
            if ph == DB: return True
            return t < t0 + (1.6 if t0 in (114.0, 126.4) else 0.0) or t0 >= 134.9
    return False


def chant_age(t):
    best = 9.0
    for t0, t1, ph in CHANTS:
        a_ = t - snap(t0)
        if 0 <= a_ < best and t < t1: best = a_
    if section(t)[1] == 'outro': best = min(best, t - snap(146.4)) if t >= snap(146.4) else best
    return best


def backdrop_green(L, t):
    c = L.bg; bp = beat_pulse(t, 8)
    age = chant_age(t)
    if age < 0.3:   # green iris opens from the centre on the beat
        c.rectangle(-300, -300, W + 600, H + 600); col(c, (0.985, 0.99, 0.985)); c.fill()
        c.arc(W / 2, H / 2, 40 + ease_out(age / 0.3) * 1300, 0, TAU); col(c, hexc('#38D100')); c.fill()
    else:
        c.rectangle(-300, -300, W + 600, H + 600); col(c, hexc('#38D100')); c.fill()
    # beat ripples
    bi = beat_index(t)
    if bi >= 0:
        ra = t - BEATS[bi]
        for k in range(2):
            r = (ra + k * 0.24) * 1500
            c.arc(W / 2, H / 2, r, 0, TAU); c.set_line_width(4); c.set_source_rgba(1, 1, 1, max(0, 0.22 - (ra + k * 0.24) * 0.4)); c.stroke()
    for i, (fx, fy, r, cc, al) in enumerate(((0.2, 0.25, 700, GD, 0.35), (0.85, 0.8, 760, GD, 0.3), (0.7, 0.2, 520, (0.75, 1, 0.45), 0.45),
                                            (0.25, 0.85, 560, (0.7, 1, 0.4), 0.35))):
        x = W * (fx + 0.05 * math.sin(t * 0.4 + i)); y = H * (fy + 0.05 * math.cos(t * 0.33 + i))
        rad = r * (1 + 0.1 * bp)
        g = cairo.RadialGradient(x, y, 0, x, y, rad); g.add_color_stop_rgba(0, *cc, al); g.add_color_stop_rgba(1, *cc, 0)
        c.set_source(g); c.arc(x, y, rad, 0, TAU); c.fill()


def backdrop(L, t):
    if CHANT_GREEN[0]: return backdrop_green(L, t)
    c = L.bg
    base, orbs = palette(t)
    if LIGHT: base = mix(base, (1, 1, 1), 0.97); base = mix(base, orbs[0], 0.02)
    c.rectangle(-300, -300, W + 600, H + 600); col(c, base); c.fill()
    bass = env('bass', t); bp = beat_pulse(t)
    spots = [(0.22, 0.30, 0.13, 0.31, 620), (0.78, 0.25, 0.11, 0.23, 560), (0.65, 0.82, 0.09, 0.17, 700), (0.18, 0.85, 0.15, 0.27, 520)]
    for i, (fx, fy, sx, sy, r) in enumerate(spots):
        x = W * (fx + 0.07 * math.sin(t * sx + i)); y = H * (fy + 0.07 * math.cos(t * sy + i * 2))
        rad = r * (1 + 0.12 * bp * bass)
        g = cairo.RadialGradient(x, y, 0, x, y, rad)
        oa = 0.13 if LIGHT else 0.62
        g.add_color_stop_rgba(0, *orbs[i], oa); g.add_color_stop_rgba(0.55, *orbs[i], oa * 0.35); g.add_color_stop_rgba(1, *orbs[i], 0)
        c.set_source(g); c.arc(x, y, rad, 0, TAU); c.fill()
    if LIGHT:
        bi = beat_index(t)
        if bi >= 0:
            ra = t - BEATS[bi]
            c.arc(W / 2, H / 2, 200 + ra * 1700, 0, TAU); c.set_line_width(3)
            c.set_source_rgba(*GT, max(0, 0.14 - ra * 0.3) * clamp(bass * 1.5)); c.stroke()
    # faint grid
    c.set_line_width(1)
    for x in range(0, W + 1, 120): c.move_to(x, 0); c.line_to(x, H)
    for y in range(0, H + 1, 120): c.move_to(0, y); c.line_to(W, y)
    gk = (0, 0, 0) if LIGHT else (1, 1, 1)
    c.set_source_rgba(*gk, 0.035 + 0.02 * bp * bass); c.stroke()
    # drifting dust
    rnd = random.Random(5)
    for k in range(40):
        x = (rnd.random() * W + t * (8 + rnd.random() * 20)) % W; y = (rnd.random() * H - t * (6 + rnd.random() * 14)) % H
        c.arc(x, y, 1 + rnd.random() * 2.2, 0, TAU); c.set_source_rgba(*gk, 0.05 + 0.07 * rnd.random()); c.fill()


def echo_words(L, t, s, size=260, a=0.07, speed=120, rows=4):
    """Huge outlined words sliding behind everything (they read through the frosted glass)."""
    c = L.bg; font(c, 'xb', size)
    adv = c.text_extents(s + '  ').x_advance
    for r in range(rows):
        y = H / 2 + (r - (rows - 1) / 2) * size * 1.05
        off = (t * speed * (1 if r % 2 else -1)) % adv
        x = -off - adv
        while x < W + adv:
            c.move_to(x, y + size * 0.36); c.text_path(s); x += adv
        if CHANT_GREEN[0]: c.set_line_width(3); c.set_source_rgba(*FOREST, 0.16); c.stroke(); return
    c.set_line_width(2.5); c.set_source_rgba(*((0.04, 0.06, 0.04) if LIGHT else (1, 1, 1)), a * (0.8 if LIGHT else 1)); c.stroke()


# ------------------------------------------------------------------ kinetic type
GRID = sorted(BEATS + [(a + b) / 2 for a, b in zip(BEATS, BEATS[1:])])


def snap(x, tol=0.13):
    """Move a time onto the nearest beat / half-beat so animation hits land on the rhythm."""
    import bisect
    i = bisect.bisect_left(GRID, x)
    best = min((GRID[j] for j in (i - 1, i) if 0 <= j < len(GRID)), key=lambda g: abs(g - x), default=x)
    return best if abs(best - x) <= tol else x


_WTC = {}


def word_times(t0, n):
    if (t0, n) in _WTC: return _WTC[(t0, n)]
    v = WT.get(t0)
    if not (v and len(v) == n):
        span = max(0.6, (LYR_END[t0] - t0) * 0.6)
        v = [t0 + span * i / max(1, n) for i in range(n)]
    out = []
    for x in v:
        y = snap(x)
        if out and y <= out[-1]: y = out[-1] + 0.06
        out.append(y)
    _WTC[(t0, n)] = out
    return out


GOOD = ('BUY', 'GREEN', 'UPPER', 'NAACH', 'RALLY', 'RAJA', 'RESEARCH', 'STRATEGY', 'SOCH', 'PLAN', 'HOLD', 'SABAR', 'DIRECTION', 'KAL')
BAD = ('RED', 'LOWER', 'SELL', 'PANIC', 'GUSSA', 'BHAAG', 'RO', 'RIGGED', 'DAR', 'ULTA', 'TENSION', 'JAADU', 'KISMAT', 'TUKOON')


def word_col(u):
    u = u.upper().strip(',.!"')
    if u in ('RO',) or any(u.startswith(b) for b in BAD if b != 'RO'): return RED
    if any(u.startswith(g) for g in GOOD): return GT
    return FGC


def layout(cr, words, region, maxch=12, max_size=230, lh=1.02, fam='xb'):
    x0, y0, w, h = region
    rows, cur = [], []
    for i, wd in enumerate(words):
        if cur and len(' '.join(words[j] for j in cur + [i])) > maxch: rows.append(cur); cur = []
        cur.append(i)
    rows.append(cur)
    sizes = []
    for r in rows:
        s = ' '.join(words[i] for i in r).upper()
        sizes.append(min(max_size, 100 * w / max(1, tw(cr, s, fam, 100))))
    total = sum(sz * lh for sz in sizes)
    if total > h: sizes = [sz * h / total for sz in sizes]; total = h
    boxes = [None] * len(words)
    y = y0 + (h - total) / 2
    for ri, (r, sz) in enumerate(zip(rows, sizes)):
        cy = y + sz * lh / 2
        font(cr, fam, sz); sp = cr.text_extents(' ').x_advance * 1.1
        ws = [cr.text_extents(words[i].upper()).x_advance for i in r]
        x = x0 + (w - (sum(ws) + sp * (len(r) - 1))) / 2
        for i, wv in zip(r, ws):
            boxes[i] = (x + wv / 2, cy, sz, wv, ri); x += wv + sp
        y += sz * lh
    return boxes


def draw_word(cr, s, box, t, wt, style, c, a=1.0):
    x, y, sz, wd, ri = box
    p = clamp((t - wt) / 0.16)
    if p <= 0 or a <= 0: return
    u = s.upper()
    bp = beat_pulse(t, 9)
    pump = 1 + 0.045 * bp
    cr.save(); cr.translate(x, y); cr.scale(pump, pump); cr.translate(-x, -y)
    _draw_word(cr, u, box, t, wt, style, c, a, p, bp)
    cr.restore()


def _draw_word(cr, u, box, t, wt, style, c, a, p, bp):
    x, y, sz, wd, ri = box
    if style in ('slam', 'shake', 'shout'):
        sc = lerp(1.7, 1.0, ease_out(p))
        jx = jy = 0
        if style in ('shake', 'shout'):
            k = 7 if style == 'shake' else 4
            jx = math.sin(t * 71 + x) * k; jy = math.cos(t * 63 + y) * k
        cr.save(); cr.translate(x + jx, y + jy); cr.scale(sc, sc); tx(cr, u, 0, 0, sz, 'xb', c, a * clamp(p * 2)); cr.restore()
        return
    if style == 'rise':
        q = ease_out(clamp((t - wt) / 0.35))
        cr.save(); cr.rectangle(x - wd, y - sz * 0.62, wd * 2, sz * 1.24); cr.clip()
        tx(cr, u, x, y + (1 - q) * sz * 0.9, sz, 'xb', c, a); cr.restore()
        return
    if style == 'blurzoom':   # flies in from huge + ghosted, settles sharp
        q = ease_out(clamp((t - wt) / 0.3))
        sc = lerp(2.6, 1.0, q)
        for g_ in range(4, 0, -1):
            gs = sc * (1 + (1 - q) * 0.08 * g_)
            cr.save(); cr.translate(x, y); cr.scale(gs, gs); tx(cr, u, 0, 0, sz, 'xb', c, a * q * 0.12); cr.restore()
        cr.save(); cr.translate(x, y); cr.scale(sc, sc); tx(cr, u, 0, 0, sz, 'xb', c, a * q); cr.restore()
        return
    if style == 'slice':      # word cut into strips that slide in from alternating sides
        n = 5; top = y - sz * 0.42; hh = sz * 0.84 / n
        for k in range(n):
            q = ease_out(clamp((t - wt - k * 0.03) / 0.3))
            cr.save(); cr.rectangle(x - wd, top + k * hh, wd * 2, hh + 1); cr.clip()
            tx(cr, u, x + (1 - q) * (1 if k % 2 else -1) * (wd + 200), y, sz, 'xb', c, a * clamp(q * 3)); cr.restore()
        return
    if style == 'outline':    # outline first, colour floods in on the next beat
        font(cr, 'xb', sz); adv = cr.text_extents(u).x_advance
        q = ease_out(clamp((t - wt) / 0.25))
        cr.move_to(x - adv / 2, y + sz * 0.36); cr.text_path(u); cr.set_line_width(max(2, sz * 0.022)); col(cr, c, a * q); cr.stroke()
        fb = snap(wt + 0.47, 0.3); f = clamp((t - fb) / 0.18)
        if f > 0:
            cr.save(); cr.rectangle(x - adv / 2 - 4, y + sz * 0.5 - sz * f, adv + 8, sz * f); cr.clip()
            tx(cr, u, x, y, sz, 'xb', c, a); cr.restore()
        return
    if style == 'scramble':   # ticker-style decode: random glyphs lock in left to right
        rnd = random.Random(int(t * 30) + int(x))
        pool = 'ABCDEFGHKLMNPRSTUVXYZ0123456789#%$+'
        font(cr, 'xb', sz)
        advs = [cr.text_extents(ch).x_advance for ch in u]; lx = x - sum(advs) / 2
        for k, ch in enumerate(u):
            lock = wt + 0.08 + k * 0.045
            g_ = ch if t >= lock or not ch.isalnum() else rnd.choice(pool)
            cc = c if t >= lock else GT
            tx(cr, g_, lx + sum(advs[:k]) + advs[k] / 2, y, sz, 'xb', cc, a * (1 if t >= lock else 0.7))
        return
    if style == 'slot':       # rolls in vertically like a counter
        q = ease_out(clamp((t - wt) / 0.4))
        cr.save(); cr.rectangle(x - wd, y - sz * 0.6, wd * 2, sz * 1.2); cr.clip()
        roll = (1 - q) * 3
        for k in range(4):
            yy = y + (k - roll) * sz * 1.1
            tx(cr, u if k == 0 else ''.join(random.Random(k + int(x)).choice('ABDEGKMNRSTUY') for _ in u), x, yy, sz, 'xb', c, a * (1 if k == 0 else 0.35))
        cr.restore()
        return
    if style == 'rgb':        # RGB split ghosting
        q = clamp(p * 2); off = 6 + 14 * beat_pulse(t, 10)
        tx(cr, u, x - off, y, sz, 'xb', (0.95, 0.2, 0.3), a * q * 0.55)
        tx(cr, u, x + off, y, sz, 'xb', (0.2, 0.55, 1.0), a * q * 0.55)
        jx = math.sin(t * 71 + x) * 5
        tx(cr, u, x + jx, y, sz, 'xb', c, a * q)
        return
    # letter-level styles
    font(cr, 'xb', sz)
    advs = [cr.text_extents(ch).x_advance for ch in u]
    lx = x - sum(advs) / 2
    for k, ch in enumerate(u):
        cx = lx + sum(advs[:k]) + advs[k] / 2
        dx = dy = rot = 0; aa = a * clamp(p * 2); scl = 1
        if style == 'type':
            aa = a * clamp((t - wt - k * 0.035) / 0.05)
            if k == len(u) - 1 and t < wt + 0.6 + len(u) * 0.035 and int(t * 4) % 2 == 0:
                cr.rectangle(cx + advs[k] / 2 + 6, y - sz * 0.42, sz * 0.07, sz * 0.84); col(cr, GT, a); cr.fill()
        elif style == 'bounce':
            ph = beat_phase(t); side = 1 if (beat_index(t) + k) % 2 else -1
            dy = -abs(math.sin(ph * math.pi)) * sz * 0.16 * (1 if k % 2 else 0.5); rot = side * 0.08
        elif style == 'run':
            go = clamp((t - wt - 0.55 - k * 0.025) / 0.5)
            dx = ease_in(go) * (W * 1.2); aa *= 1 - go * 0.3
            if go > 0:
                for tr in range(1, 4):
                    tx(cr, ch, cx + dx - tr * 40 * go * 3, y, sz, 'xb', c, aa * 0.18 / tr)
        elif style == 'drip':
            sag = clamp((t - wt - 0.3) / 1.6)
            dy = ease_in(sag) * sz * (0.25 + 0.5 * ((k * 37) % 5) / 5); rot = sag * (0.2 if k % 2 else -0.15)
        elif style == 'fall':
            fall = clamp((t - wt - 0.25) / 1.2)
            dy = ease_in(fall) * (H * 0.9) * (0.6 + 0.4 * ((k * 53) % 7) / 7); rot = fall * (1.2 if k % 2 else -1.0)
        elif style == 'cascade':
            q = clamp((t - wt - k * 0.04) / 0.38)
            dy = -(1 - back_out(q, 2.6)) * sz * 1.4; aa = a * clamp(q * 3); rot = (1 - q) * (0.5 if k % 2 else -0.5)
        elif style == 'wave':
            dy = math.sin(beat_phase(t) * TAU + k * 0.7) * sz * 0.09; aa = a * clamp((t - wt - k * 0.03) / 0.12)
        elif style == 'stretch':
            scl_y = 1 + 0.35 * beat_pulse(t, 8) * (1 if k % 2 == beat_index(t) % 2 else 0.4)
            cr.save(); cr.translate(cx, y + sz * 0.36); cr.scale(1 / math.sqrt(scl_y), scl_y); cr.translate(-cx, -(y + sz * 0.36))
            tx(cr, ch, cx, y, sz, 'xb', c, aa); cr.restore(); continue
        elif style == 'tremble':
            dx = math.sin(t * 90 + k) * 3; dy = math.cos(t * 80 + k * 2) * 3
        elif style == 'flip':
            hits = sum(1 for b in BEATS if wt <= b <= t)
            ang = math.pi * hits + math.pi * ease_out(clamp(beat_phase(t) / 0.25)) * (hits > 0) - math.pi * (hits > 0)
            cr.save(); cr.translate(x, y); cr.rotate(ang); cr.translate(-x, -y)
            tx(cr, ch, cx + dx, y + dy, sz, 'xb', c, aa); cr.restore(); continue
        cr.save(); cr.translate(cx + dx, y + dy); cr.rotate(rot); cr.scale(scl, scl)
        tx(cr, ch, 0, 0, sz, 'xb', c, aa); cr.restore()


def highlight(cr, box, t, start, c=G, a=1.0):
    x, y, sz, wd, ri = box
    q = ease_io(clamp((t - start) / 0.28))
    if q <= 0: return
    rr(cr, x - wd / 2 - sz * 0.12, y - sz * 0.5, (wd + sz * 0.24) * q, sz * 1.0, sz * 0.16); col(cr, c, 0.32 * a); cr.fill()


def underline(cr, box, t, start, c=G, a=1.0):
    x, y, sz, wd, ri = box
    q = ease_out(clamp((t - start) / 0.3))
    if q <= 0: return
    line(cr, [(x - wd / 2, y + sz * 0.56), (x - wd / 2 + wd * q, y + sz * 0.56)], max(5, sz * 0.06), c, a)


def burst_lines(cr, cx, cy, t, start, c=G, r0=160, a=1.0, n=14):
    age = t - start
    if age < 0 or age > 0.6: return
    q = ease_out(age / 0.6)
    for k in range(n):
        ang = k * TAU / n + 0.2
        r1 = r0 + q * 220; r2 = r1 + 90 * (1 - q)
        line(cr, [(cx + math.cos(ang) * r1, cy + math.sin(ang) * r1), (cx + math.cos(ang) * r2, cy + math.sin(ang) * r2)], 8 * (1 - q) + 1, c, a * (1 - q))


# per-line motion design: (main style, {word: style}, [(fx, word index)])
LINE_FX = {
    16.2: ('rise', {}, [('hl', 2)]), 18.1: ('type', {3: 'slam'}, [('burst', 3)]), 20.4: ('cascade', {2: 'stretch', 3: 'stretch'}, []),
    23.0: ('scramble', {}, [('ul', 2)]), 25.5: ('slice', {}, [('hl', 2)]), 27.3: ('outline', {1: 'slam'}, [('ul', 1)]),
    31.1: ('wave', {}, []), 34.8: ('fall', {0: 'rgb', 1: 'rgb'}, []), 36.6: ('type', {5: 'drip'}, [('ul', 0)]),
    45.5: ('bounce', {0: 'blurzoom'}, [('hl', 3)]), 85.7: ('stretch', {0: 'blurzoom'}, [('hl', 3)]),
    49.3: ('run', {0: 'slam', 1: 'slam', 2: 'slam'}, []), 89.7: ('run', {0: 'slice', 1: 'slice', 2: 'slice'}, []),
    52.0: ('rgb', {}, []), 92.4: ('shake', {2: 'rgb'}, []), 57.7: ('blurzoom', {2: 'slam'}, [('burst', 2)]),
    59.8: ('tremble', {3: 'rgb'}, []), 61.5: ('drip', {}, []), 69.5: ('slam', {3: 'rgb', 4: 'rgb'}, []),
    71.6: ('cascade', {0: 'blurzoom'}, [('ul', 5)]), 73.9: ('flip', {}, []), 76.5: ('slice', {3: 'shake'}, [('hl', 3)]),
    79.0: ('cascade', {}, []), 99.2: ('blurzoom', {}, []), 100.9: ('rise', {}, []), 102.5: ('slot', {1: 'outline'}, [('hl', 1)]),
    104.6: ('rise', {3: 'slot'}, [('ul', 3)]), 109.8: ('outline', {0: 'slam'}, [('hl', 0)]), 120.7: ('scramble', {}, [('ul', 3)]),
    122.6: ('slot', {3: 'stretch'}, [('hl', 3)]), 124.4: ('wave', {0: 'outline'}, [('ul', 0)]), 130.2: ('cascade', {4: 'blurzoom'}, [('hl', 4)]),
}


def kinetic(L, t, t0, region, style='slam', maxch=12, max_size=220, styles=None, colors=None, a=1.0, words=None):
    ro = [l for l in LYRICS if l[0] == t0][0][1]
    words = words or ro.replace('"', '').split(' ')
    wts = word_times(t0, len(words))
    boxes = layout(L.fg, words, region, maxch, max_size)
    end_a = a * clamp((LYR_END[t0] + 0.35 - t) / 0.3)
    fx = []
    if t0 in LINE_FX:
        st_, ss_, fx = LINE_FX[t0]
        style = st_; styles = dict(styles or {}); styles.update(ss_)
    for kind, i in fx:
        if i < len(words) and kind == 'hl': highlight(L.fg, boxes[i], t, wts[i] + 0.12, G if word_col(words[i]) != RED else RED, end_a)
    for i, w_ in enumerate(words):
        st = (styles or {}).get(i, style)
        c_ = (colors or {}).get(i, word_col(w_))
        draw_word(L.fg, w_, boxes[i], t, wts[i], st, c_, end_a)
    for kind, i in fx:
        if i >= len(words): continue
        if kind == 'ul': underline(L.fg, boxes[i], t, wts[i] + 0.15, GT, end_a)
        if kind == 'burst': burst_lines(L.fg, boxes[i][0], boxes[i][1], t, wts[i], GT, boxes[i][3] * 0.5 + 40, end_a)
    return boxes, wts


# ------------------------------------------------------------------ objects
def sun(L, x, y, r, a=1.0):
    c = L.bg
    for rad, al in ((r * 3.2, 0.12), (r * 2.0, 0.22), (r * 1.35, 0.35)):
        g = cairo.RadialGradient(x, y, 0, x, y, rad); g.add_color_stop_rgba(0, *GOLD, al * a); g.add_color_stop_rgba(1, *GOLD, 0)
        c.set_source(g); c.arc(x, y, rad, 0, TAU); c.fill()
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, 0, x, y, r); g.add_color_stop_rgba(0, 1, 0.97, 0.8, a); g.add_color_stop_rgba(1, *GOLD, a)
    c.set_source(g); c.arc(x, y, r, 0, TAU); c.fill()


def chai_icon(cr, x, y, s, t, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    for k in range(3):
        ph = (t * 0.6 + k / 3) % 1
        cr.move_to(-30 + k * 30, -70 - ph * 110)
        cr.curve_to(-48 + k * 30, -95 - ph * 110, -12 + k * 30, -125 - ph * 110, -30 + k * 30, -150 - ph * 110)
        cr.set_line_width(6); cr.set_source_rgba(*((0.4, 0.42, 0.4) if LIGHT else (1, 1, 1)), a * (1 - ph) * 0.55); cr.stroke()
    cr.move_to(-70, -60); cr.line_to(70, -60); cr.line_to(56, 60); cr.line_to(-56, 60); cr.close_path()
    col(cr, (0.98, 0.97, 0.94), a); cr.fill_preserve(); cr.set_line_width(5); col(cr, GOLD, a); cr.stroke()
    cr.rectangle(-66, -54, 132, 26); col(cr, (0.76, 0.52, 0.3), a); cr.fill()
    cr.arc(80, 0, 28, -TAU / 4, TAU / 4); cr.set_line_width(10); col(cr, (0.98, 0.97, 0.94), a); cr.stroke()
    cr.restore()


def candles(cr, x, y, w, h, t, up=True, n=9, a=1.0, seed=3):
    rnd = random.Random(seed); bw = w / n
    for k in range(n):
        v = 0.25 + 0.7 * ((k / (n - 1)) if up else (1 - k / (n - 1))) + 0.12 * math.sin(k * 2.1 + t * 2)
        hh = h * clamp(v) * (0.85 + 0.15 * beat_pulse(t))
        cc = GT if (up and rnd.random() > 0.2) or (not up and rnd.random() < 0.2) else RED
        bx = x + k * bw + bw * 0.2
        line(cr, [(bx + bw * 0.3, y - hh - 18), (bx + bw * 0.3, y + 12)], 3, cc, a * 0.9)
        rr(cr, bx, y - hh, bw * 0.6, hh * 0.75, 4); col(cr, cc, a * 0.9); cr.fill()


def arrow_up(cr, x, y, s, c=GT, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(0, -60); cr.line_to(46, -8); cr.line_to(16, -8); cr.line_to(16, 60); cr.line_to(-16, 60); cr.line_to(-16, -8); cr.line_to(-46, -8)
    cr.close_path(); col(cr, c, a); cr.fill(); cr.restore()


def check(cr, x, y, s, c=GT, a=1.0, p=1.0):
    pts = [(x - s * .45, y), (x - s * .12, y + s * .32), (x + s * .5, y - s * .38)]
    if p < 1:
        q = p * 2
        pts = [pts[0], (lerp(pts[0][0], pts[1][0], min(1, q)), lerp(pts[0][1], pts[1][1], min(1, q)))] + \
              ([(lerp(pts[1][0], pts[2][0], q - 1), lerp(pts[1][1], pts[2][1], q - 1))] if q > 1 else [])
    line(cr, pts, s * 0.16, c, a)


def strike(cr, x0, y0, x1, y1, p, c=RED, w=14, a=1.0):
    if p <= 0: return
    line(cr, [(x0, y0), (lerp(x0, x1, p), lerp(y0, y1, p))], w, c, a)


def icon(cr, kind, x, y, s, c=WHITE, a=1.0):
    """Simple line icons."""
    cr.save(); cr.translate(x, y); cr.scale(s, s); cr.set_line_width(7 / max(0.3, s) * s if False else 7)
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND); col(cr, c, a)
    if kind == 'car':
        cr.move_to(-70, 20); cr.line_to(-62, -10); cr.line_to(-30, -14); cr.line_to(-14, -38); cr.line_to(30, -38)
        cr.line_to(48, -12); cr.line_to(70, -8); cr.line_to(72, 20); cr.close_path(); cr.stroke()
        for wx in (-38, 42): cr.arc(wx, 22, 14, 0, TAU); cr.stroke()
    elif kind == 'house':
        cr.move_to(-60, -10); cr.line_to(0, -60); cr.line_to(60, -10); cr.stroke()
        cr.rectangle(-46, -14, 92, 66); cr.stroke(); cr.rectangle(-12, 18, 24, 34); cr.stroke()
    elif kind == 'crown':
        cr.move_to(-62, 30); cr.line_to(-70, -30); cr.line_to(-34, 0); cr.line_to(0, -48); cr.line_to(34, 0); cr.line_to(70, -30)
        cr.line_to(62, 30); cr.close_path(); cr.stroke()
    elif kind == 'bag':
        cr.move_to(-46, -20); cr.line_to(46, -20); cr.line_to(56, 56); cr.line_to(-56, 56); cr.close_path(); cr.stroke()
        cr.arc(0, -20, 26, math.pi, 0); cr.stroke(); cr.move_to(-8, 30); tx(cr, 'Rs', 0, 18, 34, 'xb', c, a)
    elif kind == 'news':
        cr.rectangle(-60, -46, 120, 92); cr.stroke()
        for k in range(3): cr.move_to(-44, -20 + k * 22); cr.line_to(44, -20 + k * 22); cr.stroke()
    elif kind == 'calendar':
        cr.rectangle(-56, -46, 112, 100); cr.stroke(); cr.move_to(-56, -16); cr.line_to(56, -16); cr.stroke()
    cr.restore()


# ------------------------------------------------------------------ phone mockup
PW, PH = 400, 850


def phone(L, cx, cy, s, t, screen, rot=0.0, a=1.0, glow=G):
    if a <= 0.01 or s <= 0.01: return
    b = L.bg
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, 520 * s)
    g.add_color_stop_rgba(0, *glow, 0.35 * a); g.add_color_stop_rgba(1, *glow, 0); b.set_source(g); b.arc(cx, cy, 520 * s, 0, TAU); b.fill()
    c = L.fg; c.save(); c.translate(cx, cy); c.rotate(rot); c.scale(s, s)
    for k in range(5):
        rr(c, -222 - k * 5, -440 - k * 5 + 24, 444 + k * 10, 880 + k * 10, 74 + k * 5); c.set_source_rgba(0, 0, 0, 0.08 * a); c.fill()
    rr(c, -222, -440, 444, 880, 74); col(c, (0.09, 0.1, 0.11), a); c.fill()
    g = cairo.LinearGradient(-222, -440, 222, 440); g.add_color_stop_rgba(0, 0.75, 0.78, 0.8, a); g.add_color_stop_rgba(0.5, 0.25, 0.27, 0.3, a)
    g.add_color_stop_rgba(1, 0.65, 0.68, 0.7, a)
    rr(c, -222, -440, 444, 880, 74); c.set_line_width(4); c.set_source(g); c.stroke()
    rr(c, -PW / 2, -PH / 2, PW, PH, 60); col(c, (0.035, 0.045, 0.05), a); c.fill()
    c.save(); rr(c, -PW / 2, -PH / 2, PW, PH, 60); c.clip(); c.translate(-PW / 2, -PH / 2)
    if a < 1: c.push_group()
    screen(L, c, t)
    if a < 1: c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()
    rr(c, -62, -PH / 2 + 16, 124, 36, 18); col(c, (0, 0, 0), a); c.fill()
    c.restore()


def status_bar(c, light=True):
    k = (1, 1, 1) if light else INK
    tx(c, '9:41', 52, 34, 22, 'b', k, 1, 'l')
    for i in range(4): rr(c, 300 + i * 9, 40 - i * 4, 6, 6 + i * 4, 1.5); col(c, k); c.fill()
    rr(c, 345, 26, 34, 17, 5); c.set_line_width(2); col(c, k); c.stroke(); rr(c, 348, 29, 24, 11, 3); c.fill()


def scr_index(L, c, t):
    status_bar(c)
    v = idx_value(t); ref = idx_ref(t); ch = (v - ref) / ref * 100; cc = G if ch >= 0 else RED
    tx(c, 'Good morning', 32, 110, 26, 'm', (0.75, 0.78, 0.8), 1, 'l')
    tx(c, 'KSE-100', 32, 170, 24, 'mono', (0.6, 0.65, 0.68), 1, 'l')
    tx(c, f"{v:,.0f}", 32, 228, 58, 'xb', WHITE, 1, 'l')
    tx(c, f"{'+' if ch >= 0 else ''}{ch:.2f}%  today", 32, 282, 24, 'mono', cc, 1, 'l')
    vs = [idx_value(max(0, t - (39 - k) * 0.25)) + 70 * math.sin(k * 1.7) for k in range(40)]
    lo, hi = min(vs) - 40, max(vs) + 40
    pts = [(20 + k * 9.2, 520 - (x - lo) / (hi - lo) * 180) for k, x in enumerate(vs)]
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.line_to(pts[-1][0], 560); c.line_to(20, 560); c.close_path()
    g = cairo.LinearGradient(0, 330, 0, 560); g.add_color_stop_rgba(0, *cc, 0.35); g.add_color_stop_rgba(1, *cc, 0); c.set_source(g); c.fill()
    line(c, pts, 4, cc)
    rr(c, 20, 610, 360, 96, 22); c.set_source_rgba(1, 1, 1, 0.07); c.fill()
    tx(c, 'TIPWALA LTD', 44, 645, 24, 'b', WHITE, 1, 'l'); tx(c, 'Watchlist', 44, 678, 18, 'm', (0.6, 0.62, 0.65), 1, 'l')
    tx(c, '+9.80%', 356, 660, 26, 'mono', G, 1, 'r')


def scr_buy(tap_t, done_t=None):
    def f(L, c, t):
        status_bar(c)
        tx(c, 'TIPWALA LTD', 32, 120, 30, 'xb', WHITE, 1, 'l')
        tx(c, 'Rs 48.20', 32, 168, 26, 'mono', G, 1, 'l')
        for i, (k, v) in enumerate((('Quantity', '5,000'), ('Order type', 'Market'), ('Total', 'Rs 241,000'))):
            rr(c, 20, 220 + i * 92, 360, 76, 18); c.set_source_rgba(1, 1, 1, 0.06); c.fill()
            tx(c, k, 44, 258 + i * 92, 22, 'm', (0.62, 0.65, 0.68), 1, 'l'); tx(c, v, 356, 258 + i * 92, 24, 'b', WHITE, 1, 'r')
        press = clamp(1 - abs(t - tap_t) / 0.12) if t >= tap_t - 0.12 else 0
        sc = 1 - 0.06 * press
        c.save(); c.translate(200, 640); c.scale(sc, sc)
        rr(c, -170, -48, 340, 96, 48); col(c, G); c.fill()
        tx(c, 'BUY', 0, 0, 40, 'xb', INK)
        c.restore()
        if t >= tap_t:
            r = (t - tap_t) * 900
            c.arc(200, 640, r, 0, TAU); c.set_source_rgba(*G, max(0, 0.45 - (t - tap_t) * 0.9)); c.set_line_width(6); c.stroke()
        dt = done_t if done_t is not None else tap_t + 0.25
        if t >= dt:
            p = ease_out(clamp((t - dt) / 0.3))
            c.save(); c.translate(0, (1 - p) * -120)
            rr(c, 20, 66, 360, 92, 24); c.set_source_rgba(0.96, 0.98, 0.96, 0.97 * p); c.fill()
            c.arc(62, 112, 20, 0, TAU); col(c, G, p); c.fill(); check(c, 62, 112, 22, INK, p)
            tx(c, 'Order placed', 96, 98, 22, 'b', INK, p, 'l'); tx(c, 'Bought 5,000 shares', 96, 128, 20, 'm', (0.3, 0.3, 0.3), p, 'l')
            c.restore()
    return f


def scr_chat(msgs):
    def f(L, c, t):
        c.rectangle(0, 0, PW, PH); col(c, (0.06, 0.09, 0.08)); c.fill()
        status_bar(c)
        c.rectangle(0, 60, PW, 90); c.set_source_rgba(1, 1, 1, 0.06); c.fill()
        c.arc(56, 105, 26, 0, TAU); col(c, GOLD); c.fill(); tx(c, 'C', 56, 105, 26, 'xb', INK)
        tx(c, 'Cousin ka dost', 96, 96, 24, 'b', WHITE, 1, 'l'); tx(c, 'online', 96, 124, 18, 'm', G, 1, 'l')
        y = 190
        for m, mt in msgs:
            p = clamp((t - mt) / 0.18)
            if p <= 0: continue
            w = tw(c, m, 'm', 24) + 44
            c.save(); c.translate(24, y); c.scale(lerp(0.6, 1, ease_out(p)), lerp(0.6, 1, ease_out(p)))
            rr(c, 0, 0, w, 64, 18); c.set_source_rgba(0.16, 0.22, 0.2, p); c.fill()
            tx(c, m, 22, 32, 24, 'm', WHITE, p, 'l'); c.restore()
            y += 84
    return f


def scr_portfolio(t0):
    def f(L, c, t):
        status_bar(c)
        tx(c, 'Portfolio', 32, 110, 30, 'xb', WHITE, 1, 'l')
        p = ease_out(clamp((t - t0) / 1.8))
        val = 1000000 * (1 - 0.598 * p)
        tx(c, f"Rs {val:,.0f}", 32, 190, 48, 'xb', WHITE, 1, 'l')
        tx(c, f"{-59.8 * p:.1f}%", 32, 246, 30, 'mono', RED, 1, 'l')
        pts = [(20 + k * 9.2, 330 + (k / 39) ** 1.6 * 280 * p + 14 * math.sin(k * 1.9)) for k in range(40)]
        line(c, pts, 4, RED)
        for i, (n, ch) in enumerate((('TIPWALA LTD', '-72.4%'), ('HOT TIP CO', '-55.1%'), ('BHAI KA SHARE', '-48.9%'))):
            rr(c, 20, 660 + i * 58 - 20, 360, 50, 14); c.set_source_rgba(1, 1, 1, 0.05); c.fill()
            tx(c, n, 40, 665 + i * 58, 20, 'b', WHITE, 1, 'l'); tx(c, ch, 360, 665 + i * 58, 20, 'mono', RED, 1, 'r')
    return f


def scr_call(L, c, t):
    g = cairo.LinearGradient(0, 0, 0, PH); g.add_color_stop_rgb(0, 0.16, 0.2, 0.22); g.add_color_stop_rgb(1, 0.04, 0.05, 0.06)
    c.rectangle(0, 0, PW, PH); c.set_source(g); c.fill()
    status_bar(c)
    ring = (t * 1.4) % 1
    for k in range(3):
        q = (ring + k / 3) % 1; c.arc(200, 300, 100 + q * 130, 0, TAU); c.set_source_rgba(1, 1, 1, 0.35 * (1 - q)); c.set_line_width(3); c.stroke()
    c.arc(200, 300, 96, 0, TAU); c.set_source_rgba(0.55, 0.6, 0.65, 1); c.fill(); tx(c, 'A', 200, 300, 90, 'xb', WHITE)
    tx(c, 'Abba', 200, 460, 52, 'xb', WHITE); tx(c, 'calling...', 200, 515, 26, 'm', (0.8, 0.82, 0.85))
    sh = math.sin(t * 50) * 5 * (int(t * 2) % 2)
    for xx, cc, lab in ((80, RED, 'Decline'), (320, G, 'Accept')):
        c.arc(xx + sh, 700, 46, 0, TAU); col(c, cc); c.fill(); tx(c, lab, xx, 778, 20, 'm', WHITE)


def scr_crack(t0):
    def f(L, c, t):
        status_bar(c)
        v = idx_value(t)
        tx(c, 'KSE-100', 32, 120, 24, 'mono', (0.6, 0.65, 0.68), 1, 'l'); tx(c, f"{v:,.0f}", 32, 176, 50, 'xb', WHITE, 1, 'l')
        tx(c, f"{(v - idx_ref(t)) / idx_ref(t) * 100:.2f}%", 32, 226, 24, 'mono', RED, 1, 'l')
        pts = [(20 + k * 9.2, 300 + (k / 39) * 330 + 30 * math.sin(k * 1.3 + t)) for k in range(40)]
        line(c, pts, 4, RED)
        hits = sum(1 for b in BEATS if t0 + 0.2 < b <= t)
        rnd = random.Random(4)
        for k in range(min(hits * 2, 14)):
            ang = rnd.random() * TAU; L_ = 120 + rnd.random() * 260
            cx, cy = 210, 430
            pts = [(cx, cy)] + [(cx + math.cos(ang + rnd.uniform(-.3, .3)) * L_ * j / 3, cy + math.sin(ang + rnd.uniform(-.3, .3)) * L_ * j / 3) for j in range(1, 4)]
            line(c, pts, 2.5, WHITE, 0.85)
    return f


def scr_button(label, cc):
    def f(L, c, t):
        status_bar(c)
        tx(c, 'TIPWALA LTD', 32, 120, 30, 'xb', WHITE, 1, 'l')
        tap = beat_phase(t) < 0.22
        c.save(); c.translate(200, 520); s_ = 0.93 if tap else 1; c.scale(s_, s_)
        rr(c, -170, -70, 340, 140, 70); col(c, cc); c.fill(); tx(c, label, 0, 0, 56, 'xb', INK if cc == G else WHITE)
        c.restore()
        if tap:
            q = beat_phase(t) / 0.22; c.arc(200, 520, 150 + q * 120, 0, TAU); c.set_source_rgba(*cc, 0.5 * (1 - q)); c.set_line_width(6); c.stroke()
    return f


def scr_web(stage_times):
    """flostocks.com in the phone browser -> Open Account -> guided form -> submitted."""
    t_tap, t_f1, t_f2, t_f3, t_submit, t_done = stage_times

    def f(L, c, t):
        c.rectangle(0, 0, PW, PH); col(c, (0.03, 0.05, 0.035)); c.fill()
        status_bar(c)
        rr(c, 20, 58, 360, 46, 23); c.set_source_rgba(1, 1, 1, 0.1); c.fill()
        tx(c, 'flostocks.com', 200, 81, 20, 'm', (0.8, 0.85, 0.82))
        if t < t_tap + 0.35:
            # official logo, painted on the untouched UI layer with the phone's transform
            u = L.ui; u.save(); u.set_matrix(c.get_matrix()); brand_img(u, 'wordmark', 200, 190, 300, 1.0, dark=True); u.restore()
            tx(c, "Pakistan's Modern", 200, 300, 30, 'xb', WHITE); tx(c, 'Gateway to the', 200, 342, 30, 'xb', WHITE)
            tx(c, 'Stock Market', 200, 384, 30, 'xb', G)
            for i, s_ in enumerate(('01  Learn the Market', '02  Open PSX Account', '03  Start Investing')):
                tx(c, s_, 70, 470 + i * 44, 22, 'b', (0.8, 0.85, 0.82), 1, 'l')
            press = clamp(1 - abs(t - t_tap) / 0.12) if t >= t_tap - 0.12 else 0
            c.save(); c.translate(200, 680); s_ = 1 - 0.07 * press; c.scale(s_, s_)
            rr(c, -150, -42, 300, 84, 42); col(c, G); c.fill(); tx(c, 'Open Account', 0, 0, 30, 'xb', FOREST); c.restore()
            if t >= t_tap:
                q = (t - t_tap) / 0.35; c.arc(200, 680, 60 + q * 200, 0, TAU); c.set_source_rgba(*G, 0.5 * (1 - q)); c.set_line_width(6); c.stroke()
            return
        if t < t_done:
            tx(c, 'Open your', 32, 160, 34, 'xb', WHITE, 1, 'l'); tx(c, 'PSX account', 32, 204, 34, 'xb', G, 1, 'l')
            tx(c, 'Fully guided, all online', 32, 248, 20, 'm', (0.8, 0.85, 0.82), 1, 'l')
            fields = (('Full name', 'Ali Raza', t_f1), ('CNIC', '35202-•••••••-•', t_f2), ('Mobile', '+92 3•• •••••••', t_f3))
            for i, (lab, val, ft) in enumerate(fields):
                y = 300 + i * 112
                tx(c, lab, 32, y, 18, 'm', (0.8, 0.85, 0.82), 1, 'l')
                rr(c, 24, y + 18, 352, 62, 16); c.set_source_rgba(1, 1, 1, 0.07); c.fill()
                act = ft - 0.3 <= t
                if act:
                    rr(c, 24, y + 18, 352, 62, 16); c.set_line_width(2); col(c, G, 0.9 if t < ft + 0.6 else 0.35); c.stroke()
                n = int(len(val) * clamp((t - ft) / 0.45))
                tx(c, val[:n], 44, y + 49, 24, 'b', WHITE, 1, 'l')
                if n >= len(val): check(c, 350, y + 49, 22, G)
            press = clamp(1 - abs(t - t_submit) / 0.12) if t >= t_submit - 0.12 else 0
            c.save(); c.translate(200, 700); s_ = 1 - 0.07 * press; c.scale(s_, s_)
            rr(c, -176, -40, 352, 80, 40); col(c, G if t >= t_f3 + 0.4 else (0.2, 0.3, 0.22)); c.fill()
            tx(c, 'Submit', 0, 0, 30, 'xb', FOREST); c.restore()
            return
        p = ease_out(clamp((t - t_done) / 0.4))
        c.arc(200, 330, 90 * p, 0, TAU); col(c, G); c.fill(); check(c, 200, 330, 90 * p, FOREST, 1, clamp((t - t_done - 0.1) / 0.35))
        tx(c, 'Details received', 200, 490, 32, 'xb', WHITE, p)
        tx(c, 'Our team will contact', 200, 548, 24, 'm', (0.8, 0.85, 0.82), p); tx(c, 'you shortly', 200, 582, 24, 'm', (0.8, 0.85, 0.82), p)
    return f


# ------------------------------------------------------------------ chants
def chant_db(L, t, c_):
    t0, t1, _ = c_
    echo_words(L, t, 'DRAMAY BAAZ!', 240, 0.08, 160)
    for b_ in BEATS:
        if t0 <= b_ <= t and t - b_ < 0.5: burst_lines(L.fg, W / 2, H / 2, t, b_, WHITE, 520, 0.8, 18)
    bi0 = beat_index(t0 - 0.06) + 1
    nb = max(0, beat_index(t) - bi0); cyc = nb // 4
    b0 = BEATS[min(len(BEATS) - 1, bi0 + cyc * 4)] if cyc else snap(t0)
    b1 = BEATS[min(len(BEATS) - 1, bi0 + cyc * 4 + 1)]
    ci = [c[0] for c in CHANTS].index(t0)
    lay = (cyc + ci) % 5
    a = clamp((t1 + 0.25 - t) / 0.25)
    kick = 1 + 0.035 * beat_pulse(t, 10)
    fg = L.fg
    if lay == 0:
        glass(L, 260, 250, 1400, 560, 48, a)
        for s_, y, wt, cc in (('DRAMAY', 430, b0, FOREST), ('BAAZ!', 640, b1, WHITE)):
            p = clamp((t - wt) / 0.14)
            if p > 0:
                fg.save(); fg.translate(W / 2, y); sc = lerp(1.9, 1, ease_out(p)) * kick; fg.scale(sc, sc)
                tx(fg, s_, 0, 0, 220, 'xb', cc, a * clamp(p * 2)); fg.restore()
    elif lay == 1:
        glass(L, 120, 380, 1680, 300, 150, a)
        p0 = clamp((t - b0) / 0.14); p1 = clamp((t - b1) / 0.14)
        fg.save(); fg.translate(W / 2, 530); fg.scale(kick, kick)
        wd = tw(fg, 'DRAMAY ', 'xb', 200)
        full = tw(fg, 'DRAMAY BAAZ!', 'xb', 200)
        tx(fg, 'DRAMAY', -full / 2 + tw(fg, 'DRAMAY', 'xb', 200) / 2 - (1 - ease_out(p0)) * 300, 0, 200, 'xb', FOREST, a * p0)
        tx(fg, 'BAAZ!', -full / 2 + wd + tw(fg, 'BAAZ!', 'xb', 200) / 2 + (1 - ease_out(p1)) * 300, 0, 200, 'xb', WHITE, a * p1)
        fg.restore()
    elif lay == 3:   # diagonal marquee strips
        fg.save(); fg.translate(W / 2, H / 2); fg.rotate(-0.2)
        for r in range(-3, 4):
            y = r * 175; dirn = 1 if r % 2 else -1
            off = ((t - b0) * 700 * dirn) % 1500
            rr(fg, -1600, y - 70, 3200, 140, 0); col(fg, FOREST if (r % 2 or r == 0) else WHITE, 0.92 * a if r == 0 else 0.18 * a); fg.fill()
            if r == 0: continue
            for k in range(-2, 3):
                tx(fg, 'DRAMAY BAAZ!', k * 1500 - off, y, 110, 'xb', WHITE if r % 2 else FOREST, 0.35 * a)
        p0 = clamp((t - b0) / 0.14); p1 = clamp((t - b1) / 0.14)
        tx(fg, 'DRAMAY', -260 - (1 - ease_out(p0)) * 900, 0, 120, 'xb', WHITE, a * p0)
        tx(fg, 'BAAZ!', 330 + (1 - ease_out(p1)) * 900, 0, 120, 'xb', hexc('#38D100'), a * p1)
        fg.restore()
    elif lay == 4:   # giant crop: BAAZ! bleeds off the frame
        p0 = clamp((t - b0) / 0.14); p1 = clamp((t - b1) / 0.16)
        fg.save(); fg.translate(W / 2, H / 2 + 60); s_ = lerp(1.5, 1, ease_out(p1)) * kick; fg.scale(s_, s_)
        tx(fg, 'BAAZ!', 0, 0, 640, 'xb', WHITE, a * p1); fg.restore()
        glass(L, W / 2 - 420, 120, 840, 180, 90, a * p0)
        tx(fg, 'DRAMAY', W / 2, 210, 130, 'xb', FOREST, a * p0)
    else:
        for i, (s_, wt, cc) in enumerate((('DRAMAY', b0, FOREST), ('BAAZ!', b1, WHITE))):
            p = clamp((t - wt) / 0.16)
            x = 140 + i * 860
            glass(L, x, 300 + i * 80, 780, 400, 44, a * ease_out(p))
            fg.save(); fg.translate(x + 390, 500 + i * 80); fg.rotate((-0.06, 0.05)[i]); sc = lerp(1.6, 1, ease_out(p)) * kick; fg.scale(sc, sc)
            tx(fg, s_, 0, 0, 170, 'xb', cc, a * clamp(p * 2)); fg.restore()


def chant_no(L, t, t0, t1, cx=W / 2, cy=H / 2 - 20, s=1.0, a=1.0, with_glass=True):
    """AB NO  ~~DRAMAY BAAZI~~ !  (the drama gets struck out in brand green)"""
    fg = L.fg
    bi0 = beat_index(t0 - 0.06) + 1
    b = [BEATS[min(len(BEATS) - 1, bi0 + k)] for k in range(3)]
    b[0] = snap(t0)
    kick = 1 + 0.03 * beat_pulse(t, 10)
    if with_glass:
        glass(L, cx - 760 * s, cy - 300 * s, 1520 * s, 600 * s, 50 * s, a)
    fg.save(); fg.translate(cx, cy); fg.scale(s * kick, s * kick)
    p0 = clamp((t - b[0]) / 0.14); p1 = clamp((t - b[1]) / 0.14); p2 = clamp((t - b[2]) / 0.3)
    gr = CHANT_GREEN[0]
    tx(fg, 'AB NO', 0, -160, 150, 'xb', WHITE if gr else GT, a * p0)
    w = tw(fg, 'DRAMAY BAAZI!', 'xb', 170)
    fg.save(); sc = lerp(1.6, 1, ease_out(p1)); fg.scale(sc, sc)
    tx(fg, 'DRAMAY BAAZI!', 0, 70, 170, 'xb', FOREST if gr else FGC, a * clamp(p1 * 2) * (1 - 0.45 * ease_out(p2)))
    fg.restore()
    strike(fg, -w / 2 - 20, 92, w / 2 + 20, 48, ease_out(p2), WHITE if gr else GT, 22, a)
    fg.restore()


# ------------------------------------------------------------------ lyric shots
def cur_line(t):
    cur = None
    for l in LYRICS:
        if l[0] - 0.12 <= t < LYR_END[l[0]] + 0.35: cur = l[0]
    return cur


LEFT = (90, 190, 1050, 640)       # type region when an object sits on the right
FULL = (110, 200, 1700, 600)


def shot(L, t, t0):
    fg = L.fg; T = lambda d=0.0: t - t0 - d
    if t0 == 16.2:
        sun(L, 1470, lerp(980, 380, ease_out(clamp(T() / 2.5))), 150)
        kinetic(L, t, t0, LEFT, 'rise', maxch=11)
        phone(L, 1400, 560, 0.82 * pop(t, t0 + 0.4, 0.5), t, scr_index, rot=0.06)
    elif t0 == 18.1:
        sun(L, 1470, 380, 150, 0.7)
        bt = word_times(t0, 5)[3]
        kinetic(L, t, t0, LEFT, 'rise', maxch=11, styles={3: 'slam'})
        chai_icon(fg, 300, 900, 0.8 * pop(t, t0), t)
        phone(L, 1400, 560, 0.82, t, scr_buy(bt), rot=0.06)
    elif t0 == 20.4:
        echo_words(L, t, 'UPPER LOCK', 260, 0.08, 220)
        kinetic(L, t, t0, (110, 260, 1180, 560), 'shout', maxch=10, styles={0: 'rise', 1: 'rise'})
        p = pop(t, word_times(t0, 6)[2])
        glass(L, 1340, 360, 470, 340, 40, clamp(p), tint=GT, ta=0.12)
        for k in range(3): arrow_up(fg, 1440 + k * 120, 470 - (T() * 300 + k * 90) % 160 + 60, 0.7 * p, GT, clamp(p))
        tx(fg, 'UPPER LOCK', 1575, 640, 56, 'xb', GT, clamp(p))
    elif t0 == 23.0:
        kinetic(L, t, t0, LEFT, 'type', maxch=11)
        wts = word_times(t0, 6)
        phone(L, 1400, 560, 0.82 * pop(t, t0, 0.4), t, scr_chat([('Bhai ek tip hai...', wts[1]), ('Ye share pakka 10x!', wts[3]),
                                                                    ('Andar ki khabar hai', wts[4]), ('Sab laga do!!!', wts[5] + 0.2)]), rot=0.05)
    elif t0 == 25.5:
        kinetic(L, t, t0, LEFT, 'rise', maxch=11)
        p = pop(t, t0 + 0.3)
        fg.save(); fg.translate(1470, 540); fg.rotate(0.05 - (1 - clamp(p)) * 0.4)
        glass(L, -330, -230, 660, 460, 30, clamp(p), tint=(1, 0.97, 0.9), ta=0.12)
        tx(fg, 'DAILY KHABAR', 0, -170, 34, 'mono', (0.85, 0.85, 0.8), clamp(p))
        line(fg, [(-290, -130), (290, -130)], 2, FGC, 0.4 * clamp(p))
        tx(fg, 'MARKET MEIN', 0, -60, 78, 'xb', FGC, clamp(p)); tx(fg, 'TEZI!', 0, 30, 96, 'xb', GT, clamp(p))
        candles(fg, -260, 190, 520, 110, t, True, 12, clamp(p))
        fg.restore()
    elif t0 == 27.3:
        echo_words(L, t, 'ALL IN', 300, 0.07, 140)
        kinetic(L, t, t0, LEFT, 'slam', maxch=10)
        p = pop(t, t0)
        glass(L, 1260, 330, 560, 420, 40, clamp(p), tint=GOLD, ta=0.1)
        drain = ease_io(clamp(T(0.8) / 1.6))
        tx(fg, 'YOUR SAVINGS', 1540, 410, 30, 'mono', GOLD, clamp(p))
        tx(fg, f"Rs {1000000 * (1 - drain):,.0f}", 1540, 490, 58, 'xb', FGC, clamp(p))
        rr(fg, 1310, 560, 460, 26, 13); fg.set_source_rgba(1, 1, 1, 0.12 * p); fg.fill()
        rr(fg, 1310, 560, 460 * (1 - drain), 26, 13); col(fg, GOLD, clamp(p)); fg.fill()
        tx(fg, 'ALL IN  →  TIPWALA LTD', 1540, 660, 28, 'b', GT, clamp(T(0.9) / 0.3))
    elif t0 == 31.1:
        echo_words(L, t, 'RAJA', 320, 0.07, 100)
        kinetic(L, t, t0, (110, 380, 1700, 520), 'rise', colors={3: GOLD, 4: GOLD})
        p = pop(t, word_times(t0, 5)[3])
        icon(fg, 'crown', W / 2, 250, 1.6 * p, GOLD, clamp(p))
    elif t0 == 32.9:
        wts = word_times(t0, 4)
        for i, (k, lab) in enumerate((('car', 'GAADI'), ('house', 'BANGLA'), ('bag', 'SAB'))):
            p = pop(t, wts[i])
            x = 250 + i * 520
            glass(L, x, 260, 440, 420, 40, clamp(p), tint=GOLD, ta=0.09)
            icon(fg, k, x + 220, 420, 1.4 * p, GOLD, clamp(p))
            tx(fg, lab, x + 220, 600, 70, 'xb', FGC, clamp(p))
        tx(fg, 'LUNGA!', W / 2, 820, 120, 'xb', GOLD, clamp((t - wts[3]) / 0.15) * fade(t, t0, LYR_END[t0] + 0.3))
    elif t0 == 34.8:
        echo_words(L, t, 'LOWER LOCK', 260, 0.09, 300)
        kinetic(L, t, t0, (110, 230, 1700, 520), 'fall', maxch=12, styles={0: 'shake', 1: 'shake'})
        p = pop(t, t0 + 0.05, 0.2)
        glass(L, W / 2 - 330, 780, 660, 130, 65, clamp(p), tint=RED, ta=0.18)
        tx(fg, '▼  LOWER LOCK  −7.5%', W / 2, 845, 44, 'xb', FGC, clamp(p))
    elif t0 == 36.6:
        kinetic(L, t, t0, (110, 200, 1100, 520), 'rise', maxch=10, styles={5: 'drip'})
        p = pop(t, t0 + 0.2)
        glass(L, 1290, 330, 520, 300, 40, clamp(p))
        tx(fg, 'Stop loss', 1360, 420, 44, 'b', FGC, clamp(p), 'l')
        off = ease_io(clamp(T(0.9) / 0.35))
        rr(fg, 1360, 490, 180, 90, 45); col(fg, mix(GT, (0.35, 0.35, 0.38), off), clamp(p)); fg.fill()
        fg.arc(lerp(1495, 1405, off), 535, 36, 0, TAU); col(fg, FGC, clamp(p)); fg.fill()
        tx(fg, 'OFF' if off > 0.5 else 'ON', 1600, 535, 40, 'xb', RED if off > 0.5 else GT, clamp(p), 'l')
        if t > 39.4:   # build into the chorus
            k = clamp((t - 39.4) / 4.0)
            for i in range(24):
                v = env('mid', t - i * 0.01) * (0.4 + 0.6 * k)
                rr(fg, 160 + i * 66, 1000 - 260 * v * k, 44, 260 * v * k, 10); col(fg, RED if i % 3 else FGC, 0.6 * k); fg.fill()
    elif t0 in (45.5, 85.7):
        echo_words(L, t, 'GREEN GREEN', 260, 0.08, 160)
        rnd = random.Random(9)
        for k in range(46):
            ph = ((t - t0) * (0.35 + rnd.random() * 0.5) + rnd.random()) % 1
            x = rnd.random() * W + math.sin(t * 2 + k) * 30; y = -40 + ph * (H + 80)
            fg.save(); fg.translate(x, y); fg.rotate(t * 3 + k); rr(fg, -9, -4, 18, 8, 2)
            col(fg, (G, GOLD, GD)[k % 3], 0.85); fg.fill(); fg.restore()
        kinetic(L, t, t0, LEFT, 'bounce', maxch=11, styles={0: 'slam'})
        glass(L, 1260, 220, 560, 640, 44, pop(t, t0) and 1, tint=GT, ta=0.1)
        candles(fg, 1310, 800, 460, 480, t, True, 9)
    elif t0 in (49.3, 89.7):
        echo_words(L, t, 'RED RED RED', 260, 0.09, 420)
        kinetic(L, t, t0, (110, 230, 1700, 560), 'run', maxch=13, styles={0: 'slam', 1: 'slam', 2: 'slam'})
        for k in range(14):
            yy = 120 + k * 64
            x = (T() * 2600 + k * 337) % (W + 600) - 300
            line(fg, [(x, yy), (x + 200 + (k * 53) % 160, yy)], 3, FGC, 0.18)
    elif t0 in (52.0, 92.4):
        kinetic(L, t, t0, LEFT, 'shake', maxch=10)
        phone(L, 1400, 560, 0.82 * pop(t, t0, 0.35), t, scr_crack(t0), rot=-0.05 + math.sin(t * 40) * 0.01, glow=RED)
    elif t0 == 57.7:
        kinetic(L, t, t0, LEFT, 'slam', maxch=10)
        phone(L, 1400, 560, 0.82 * pop(t, t0, 0.3), t, scr_button('BUY', GT), rot=0.05)
    elif t0 == 59.8:
        kinetic(L, t, t0, LEFT, 'tremble', maxch=10)
        phone(L, 1400, 560, 0.82, t, scr_button('SELL', RED), rot=0.05 + math.sin(t * 60) * 0.006, glow=RED)
    elif t0 == 61.5:
        rnd = random.Random(int(t * 30))
        for k in range(60):
            x = rnd.random() * W; y = rnd.random() * H
            line(L.bg, [(x, y), (x - 8, y + 50)], 2, (0.3, 0.45, 0.75) if LIGHT else (0.7, 0.8, 1), 0.25)
        kinetic(L, t, t0, (110, 220, 1700, 560), 'drip', maxch=13)
    elif t0 == 69.5:
        chart_scene(L, t, 'dip')
        kinetic(L, t, t0, (110, 120, 1700, 330), 'slam', maxch=30, max_size=150)
    elif t0 == 71.6:
        chart_scene(L, t, 'rally')
        kinetic(L, t, t0, (110, 120, 1700, 330), 'slam', maxch=30, max_size=150)
    elif t0 == 73.9:
        chart_scene(L, t, 'flip')
        kinetic(L, t, t0, (110, 200, 1700, 560), 'flip', maxch=13)
    elif t0 == 76.5:
        kinetic(L, t, t0, LEFT, 'slam', maxch=10, styles={3: 'shake'})
        phone(L, 1400, 560, 0.82 * pop(t, t0, 0.35), t, scr_portfolio(t0 + 0.3), rot=0.05, glow=RED)
    elif t0 == 79.0:
        kinetic(L, t, t0, LEFT, 'rise', maxch=10)
        phone(L, 1400, 560, 0.82 * pop(t, t0, 0.35), t, scr_call, rot=0.05 + math.sin(t * 50) * 0.008 * (int(t * 2) % 2))
    elif t0 == 80.8:
        words = ['MARKET', 'RIGGED', 'HAI', 'ABBA!']
        wts = word_times(t0, 7)
        for e in range(3):   # the excuse keeps echoing
            et = t0 + e * 0.95
            if t < et: continue
            boxes = layout(fg, words, (140 + e * 40, 170 + e * 200, 1640 - e * 80, 240), 30, 150)
            for i, w_ in enumerate(words):
                draw_word(fg, w_, boxes[i], t, et + (wts[i] - t0) * 0.6, 'slam', RED if w_ == 'RIGGED' else FGC,
                          (1 - e * 0.28) * fade(t, et, 83.9))
        tx(fg, 'kehta rehta hai...', W / 2, 900, 56, 'b', MUTED, clamp((t - wts[4]) / 0.3) * fade(t, t0, 83.9))
    elif t0 == 99.2:
        kinetic(L, t, t0, (110, 300, 1700, 420), 'rise', maxch=20)
    elif t0 == 100.9:
        kinetic(L, t, t0, (110, 640, 1700, 300), 'rise', maxch=25, max_size=180)
        for i, (m, ang) in enumerate((('10x pakka!', -0.06), ('Andar ki khabar', 0.04), ('Sab laga do!', -0.03))):
            p = pop(t, t0 + i * 0.15)
            x = 230 + i * 520
            fg.save(); fg.translate(x + 230, 360); fg.rotate(ang)
            glass(L, -230, -80, 460, 160, 40, clamp(p))
            tx(fg, m, 0, 0, 46, 'b', FGC, clamp(p))
            strike(fg, -200, 20, 200, -20, ease_out(clamp((t - word_times(t0, 4)[2]) / 0.3 - i * 0.3)), RED, 12)
            fg.restore()
    elif t0 == 102.5:
        kinetic(L, t, t0, LEFT, 'rise', maxch=10)
        glass(L, 1260, 220, 560, 640, 40, clamp(pop(t, t0)))
        tx(fg, 'BEFORE YOU INVEST', 1540, 290, 28, 'mono', MUTED)
        for i, lab in enumerate(('Earnings', 'Debt', 'Valuation', 'Risk')):
            it = t0 + 0.5 + i * 0.4
            a = clamp((t - it) / 0.2)
            rr(fg, 1320, 360 + i * 120, 70, 70, 18); fg.set_source_rgba(*GT, 0.18 * a); fg.fill()
            check(fg, 1355, 395 + i * 120, 46, GT, a, clamp((t - it) / 0.3))
            tx(fg, lab, 1420, 395 + i * 120, 48, 'b', FGC, a, 'l')
    elif t0 == 104.6:
        kinetic(L, t, t0, LEFT, 'rise', maxch=10)
        fl = clamp((t - word_times(t0, 4)[3] + 0.2) / 0.4)
        glass(L, 1300, 260, 480, 520, 40, clamp(pop(t, t0)))
        rr(fg, 1300, 260, 480, 110, 40); col(fg, GT, 0.85); fg.fill()
        fg.save(); fg.translate(1540, 560); fg.scale(1, max(0.02, abs(math.cos(fl * math.pi))))
        tx(fg, 'AAJ' if fl < 0.5 else 'KAL', 0, 0, 170, 'xb', FGC if fl < 0.5 else GT); fg.restore()
    elif t0 == 106.1:
        wts = word_times(t0, 6)
        tx(fg, 'NA', W / 2 - 520, 380, 120, 'xb', FGC, clamp((t - wts[0]) / 0.15))
        tx(fg, 'JAADU', W / 2 + 60, 380, 200, 'xb', FGC, clamp((t - wts[1]) / 0.15))
        strike(fg, W / 2 - 230, 400, W / 2 + 350, 360, ease_out(clamp((t - wts[2]) / 0.3)), RED, 20)
        tx(fg, 'NA', W / 2 - 600, 660, 120, 'xb', FGC, clamp((t - wts[3]) / 0.15))
        tx(fg, 'KISMAT', W / 2 + 40, 660, 200, 'xb', FGC, clamp((t - wts[4]) / 0.15))
        strike(fg, W / 2 - 300, 680, W / 2 + 380, 640, ease_out(clamp((t - wts[5]) / 0.3)), RED, 20)
    elif t0 == 109.8:
        kinetic(L, t, t0, (110, 160, 1700, 300), 'rise', maxch=30, max_size=170)
        for i, s_ in enumerate(('RESEARCH', 'PLAN', 'INVEST', 'HOLD')):
            st = t0 + 0.4 + i * 0.55
            p = pop(t, st)
            x = 150 + i * 420; y = 640 - i * 50
            if i:
                q = clamp((t - st + 0.3) / 0.3)
                line(fg, [(x - 70, y + 50), (lerp(x - 70, x, q), lerp(y + 50, y, q))], 5, GT, 0.8)
            glass(L, x, y - 70, 340, 140, 70, clamp(p), tint=GT if i == 3 else FGC, ta=0.1)
            tx(fg, s_, x + 170, y, 46, 'xb', GT if i == 3 else FGC, clamp(p))


def chart_scene(L, t, mode):
    fg = L.fg
    glass(L, 110, 400, 1700, 520, 44, 1)
    def yv(x): return 690 + 160 * math.sin((x - 110) / 260 - 0.6) + 30 * math.sin(x / 70)
    reveal = clamp((t - 69.5) / 6.0)
    xs = list(range(150, 1780, 16)); n = max(2, int(len(xs) * reveal))
    pts = [(x, yv(x)) for x in xs[:n]]
    if mode == 'flip':
        fg.save(); fg.translate(W / 2, 660)
        hits = sum(1 for b in BEATS if 73.9 <= b <= t)
        fg.rotate(math.pi * (hits % 2) if beat_phase(t) > 0.25 else math.pi * ((hits - 1) % 2) + math.pi * ease_out(beat_phase(t) / 0.25) if hits else 0)
        fg.translate(-W / 2, -660)
    line(fg, pts, 6, FGC, 0.95)
    for (mx, lab, cc, sub, mt) in ((560, 'SELL', RED, 'sold low', 70.3), (1050, 'BUY', GT, 'bought high', 72.6), (1450, 'SELL', RED, 'sold low again', 73.4)):
        if t < mt or mx > pts[-1][0] + 5: continue
        p = pop(t, mt); my = yv(mx)
        fg.arc(mx, my, 16 * p, 0, TAU); col(fg, cc); fg.fill()
        dy = 80 if lab == 'SELL' else -80
        glass_pill(L, mx, my + dy, lab, 30, 'xb', cc, clamp(p))
        tx(fg, sub, mx, my + dy * 1.75, 26, 'm', MUTED, clamp(p))
    if mode == 'flip': fg.restore()


# ------------------------------------------------------------------ final + outro
def final_section(L, t):
    fg = L.fg
    # chant moments
    for c_ in CHANTS:
        t0, t1, ph = c_
        if t0 <= t < t1 and ph == NO:
            big = t < t0 + (1.6 if t0 in (114.0, 126.4) else 0.0) or t0 >= 134.9
            if big:
                echo_words(L, t, 'AB NO DRAMAY BAAZI', 200, 0.07, 160)
                chant_no(L, t, t0, t1)
            elif cur_line(t) is None:
                chant_no(L, t, t0, t1, W / 2, 150, 0.42, 1, with_glass=False)
            if big: return
    # steps from flostocks.com "How it works"
    if 115.5 <= t < 120.6:
        a = fade(t, 115.5, 120.6)
        steps = (('01', 'Learn the Market', 'Free Bootcamp & Analyzer'), ('02', 'Open PSX Account', 'Through Floret Capitals'),
                 ('03', 'Start Investing', 'With real confidence'))
        for i, (n, h, s_) in enumerate(steps):
            bt = BEATS[beat_index(115.7) + 1 + i * 2]
            p = ease_out(clamp((t - bt) / 0.35))
            x = 130 + i * 570; y = 380 + (1 - p) * 80
            glass(L, x, y, 520, 360, 40, a * p, tint=GT if i == 1 else FGC, ta=0.1)
            tx(fg, n, x + 50, y + 80, 64, 'xb', GT, a * p, 'l')
            tx(fg, h, x + 50, y + 200, 50, 'xb', FGC, a * p, 'l')
            tx(fg, s_, x + 50, y + 270, 30, 'm', MUTED, a * p, 'l')
        return
    l = cur_line(t)
    if l in (120.7, 122.6, 124.4):
        kinetic(L, t, l, LEFT, 'rise', maxch=10)
        p = clamp(pop(t, l))
        glass(L, 1260, 260, 560, 560, 40, p)
        if l == 120.7:
            tx(fg, 'PSX ANALYZER', 1540, 330, 28, 'mono', GT, p)
            tx(fg, 'Score any listed', 1540, 420, 40, 'b', FGC, p); tx(fg, 'company in plain', 1540, 470, 40, 'b', FGC, p)
            tx(fg, 'English', 1540, 520, 40, 'b', FGC, p)
            for i in range(5):
                rr(fg, 1340 + i * 82, 600, 64, 120, 12); col(fg, GT, p * (0.25 + 0.75 * (i < 1 + int(clamp((t - l - 0.4) / 1.2) * 4)))); fg.fill()
        elif l == 122.6:
            tx(fg, 'SIP CALCULATOR', 1540, 330, 28, 'mono', GT, p)
            tx(fg, 'Steady, every month', 1540, 400, 36, 'b', FGC, p)
            for i in range(8):
                hh = 40 + i * 30 * clamp((t - l - 0.2) / 1.2)
                rr(fg, 1320 + i * 56, 760 - hh, 40, hh, 8); col(fg, GT, p * 0.9); fg.fill()
            tx(fg, 'HOLD', 1540, 520, 90, 'xb', GT, p)
        else:
            tx(fg, 'PATIENCE', 1540, 330, 28, 'mono', GT, p)
            pts = [(1310 + k * 11, 740 - k * 7 * clamp((t - l) / 1.4) - 14 * math.sin(k * 0.9)) for k in range(42)]
            line(fg, pts, 6, GT, p)
        return
    # phone: flostocks.com -> Open Account -> form -> submitted
    if 127.6 <= t < 134.9:
        stages = (128.6, 130.45, 130.95, 131.45, 132.55, 133.05)
        ph = scr_web(stages)
        if l == 130.2:
            kinetic(L, t, l, LEFT, 'rise', maxch=10)
            phone(L, 1400, 590, 0.8, t, ph, rot=0.04)
        else:
            a = fade(t, 127.6, 134.9, 0.3, 0.3)
            phone(L, 1400 if t >= 132.0 else W / 2 + 330, 590, 0.8 * ease_out(clamp((t - 127.6) / 0.4)), t, ph, rot=0.04, a=a)
            if t < 130.2:
                tx(fg, 'Open your PSX', 640, 470, 96, 'xb', FGC, clamp((t - 127.8) / 0.3) * a)
                tx(fg, 'account online', 640, 590, 96, 'xb', GT, clamp((t - 128.1) / 0.3) * a)
            if t >= 133.6:
                badges = ('PSX Licensed Brokerage', 'SECP Compliant', 'Personal Relationship Managers')
                for i, b_ in enumerate(badges):
                    p = ease_out(clamp((t - 133.6 - i * 0.22) / 0.3))
                    pw = glass_pill(L, 640, 380 + i * 150, '      ' + b_, 38, 'b', FGC, a * p, tint=GT, ta=0.1)
                    check(fg, 640 - pw / 2 + 52, 380 + i * 150, 30, GT, a * p)
        return
    if 137.3 <= t < 139.0:
        a = fade(t, 137.3, 139.0)
        tx(fg, 'Learn. Open your account.', W / 2, 430, 90, 'xb', FGC, a * clamp((t - 137.3) / 0.2))
        tx(fg, 'Start investing.', W / 2, 560, 110, 'xb', GT, a * clamp((t - 137.8) / 0.2))
        glass_pill(L, W / 2, 720, 'flostocks.com', 44, 'b', FGC, a * clamp((t - 138.2) / 0.2))
        return
    if t >= 141.6:
        chant_no(L, t, 139.0, 143.1, a=clamp((143.1 - t) / 0.4))


def outro(L, t):
    fg = L.fg
    words = [('START', 143.4, FGC), ('TRADING', 143.85, FGC), ('IN PSX', 144.3, GT), ('TODAY', 144.75, FGC)]
    if t < 149.0:
        a = clamp((149.0 - t) / 0.3)
        if t < 146.3:
            echo_words(L, t, 'START TRADING IN PSX TODAY', 160, 0.06, 140)
            for i, (s_, wt, cc) in enumerate(words):
                p = clamp((t - wt) / 0.14)
                if p <= 0: continue
                y = 260 + i * 185
                fg.save(); fg.translate(W / 2, y); sc = lerp(1.8, 1, ease_out(p)) * (1 + 0.02 * beat_pulse(t)); fg.scale(sc, sc)
                tx(fg, s_, 0, 0, 180, 'xb', cc, a * clamp(p * 2)); fg.restore()
        else:
            tx(fg, 'because', W / 2, 250, 80, 'm', FOREST, clamp((t - 146.4) / 0.2) * a)
            chant_no(L, t, 146.75, 149.0, W / 2, 600, 0.8, a)
        return
    # end card
    a = clamp((t - 149.0) / 0.5)
    tx(fg, 'START TRADING IN PSX TODAY', W / 2, 190, 86, 'xb', FGC, a)
    glass(L, 360, 290, 1200, 420, 48, a)
    u = L.ui; u.save(); u.set_matrix(fg.get_matrix()); brand_img(u, 'logo', W / 2, 500, 900 * (0.96 + 0.04 * a), a, dark=not LIGHT); u.restore()
    w1 = tw(fg, 'because ', 'm', 46); w2 = tw(fg, 'AB NO DRAMAY BAAZI!', 'xb', 64); x0 = W / 2 - (w1 + w2) / 2
    tx(fg, 'because', x0, 800, 46, 'm', MUTED, a, 'l')
    k = 1 + 0.04 * beat_pulse(t, 9) * (t > 156.2)
    fg.save(); fg.translate(x0 + w1 + w2 / 2, 800); fg.scale(k, k)
    tx(fg, 'AB NO DRAMAY BAAZI!', 0, 0, 64, 'xb', GT, a); fg.restore()
    bw = 560
    glass(L, W / 2 - bw / 2, 880, bw, 100, 50, a, tint=GT, ta=0.18)
    tx(fg, 'Open Account  ·  flostocks.com', W / 2, 930, 34, 'b', FGC, a)
    tx(fg, 'Illustrative content. Investing in securities involves risk.', W / 2, 1040, 20, 'm', MUTED, a * 0.9)


# ------------------------------------------------------------------ intro
def intro_idle(L, t):
    fg = L.fg
    if t >= 13.6:
        p = clamp((t - 13.6) / 0.3); a = clamp((16.3 - t) / 0.3)
        echo_words(L, t, 'DRAMAY BAAZ', 240, 0.06, 120)
        glass(L, 260, 280, 1400, 480, 48, a * p)
        tx(fg, 'DRAMAY BAAZ', W / 2, 470, 190, 'xb', FGC, a * p)
        tx(fg, 'a PSX story starring', W / 2 - 60, 640, 54, 'm', MUTED, a * clamp((t - 14.2) / 0.3), 'c')
        tx(fg, 'YOU', W / 2 + 330, 640, 80, 'xb', GT, a * clamp((t - 14.6) / 0.15))
        return
    v = idx_value(t)
    glass(L, W / 2 - 520, H / 2 - 190, 1040, 380, 44, 1)
    tx(fg, 'KSE-100', W / 2, H / 2 - 90, 44, 'mono', MUTED)
    tx(fg, f"{v:,.0f}", W / 2, H / 2 + 50, 170, 'xb', FGC)


# ------------------------------------------------------------------ HUD
def hud(L, t):
    if t >= 143.1: return
    a = clamp((t - 2.0) / 0.8)
    glass(L, 36, 34, 336, 86, 43, a, shadow=False)
    u = L.ui; u.save(); u.identity_matrix(); brand_img(u, 'wordmark', 204, 77, 280, a, dark=not LIGHT); u.restore()
    return
    v = idx_value(t); ref = idx_ref(t); ch = (v - ref) / ref * 100; cc = GT if ch >= 0 else RED
    glass(L, W - 400, 34, 364, 86, 43, a, shadow=False)
    fg = L.fg
    tx(fg, 'KSE-100', W - 370, 77, 22, 'mono', MUTED, a, 'l')
    tx(fg, f"{v:,.0f}", W - 250, 77, 34, 'xb', FGC, a, 'l')
    tx(fg, f"{'+' if ch >= 0 else ''}{ch:.1f}%", W - 60, 77, 22, 'mono', cc, a, 'r')


def subtitle(L, t):
    l = cur_line(t)
    if l is None or l not in SUBS: return
    a = fade(t, l + 0.15, LYR_END[l] + 0.3, 0.25, 0.3)
    if a <= 0: return
    glass_pill(L, W / 2, H - 70, SUBS[l], 30, 'm', MUTED, a, pad=36)


# ------------------------------------------------------------------ camera, transitions, light leaks
TRANS = ('push', 'zoom', 'drop', 'tilt', 'iris', 'pushl', 'spin')


def shot_camera(t, c_, sec):
    """Slow push-in + drift per shot, and an entrance transition that rotates through TRANS."""
    cam = dict(dx=0.0, dy=0.0, sc=1.0, rot=0.0, iris=None)
    if c_ or sec in ('final', 'outro'):
        return cam
    l = cur_line(t)
    if l is None: return cam
    li = [x[0] for x in LYRICS].index(l)
    t0 = snap(l); dur = max(1.0, LYR_END[l] - l)
    lt = t - t0
    cam['sc'] = 1 + 0.045 * clamp(lt / dur)
    cam['rot'] = (0.006 if li % 2 else -0.006) * clamp(lt / dur)
    cam['dx'] = (14 if li % 2 else -14) * clamp(lt / dur)
    q = ease_out(clamp(lt / 0.34)); kind = TRANS[li % len(TRANS)]
    if q < 1:
        if kind == 'push': cam['dx'] += (1 - q) * 360
        elif kind == 'pushl': cam['dx'] -= (1 - q) * 360
        elif kind == 'zoom': cam['sc'] *= lerp(1.22, 1.0, q)
        elif kind == 'drop': cam['dy'] -= (1 - q) * 240
        elif kind == 'tilt': cam['rot'] += (1 - q) * -0.08; cam['dy'] += (1 - q) * 120
        elif kind == 'spin': cam['rot'] += (1 - q) * 0.25; cam['sc'] *= lerp(0.8, 1.0, q)
        elif kind == 'iris': cam['iris'] = 60 + q * 1400
    return cam


def apply_cam(cr, cam, k):
    cr.translate(W / 2 + cam['dx'] * k, H / 2 + cam['dy'] * k)
    cr.rotate(cam['rot'] * k); s_ = 1 + (cam['sc'] - 1) * k; cr.scale(s_, s_)
    cr.translate(-W / 2, -H / 2)


def leak(L, t):
    """Soft diagonal light sweep when a chant hits."""
    for t0, t1, ph in CHANTS:
        age = t - snap(t0)
        if 0 <= age < 0.55:
            q = age / 0.55; x = lerp(-700, W + 700, ease_io(q))
            c = L.fg; c.save(); c.identity_matrix()
            g = cairo.LinearGradient(x - 400, 0, x + 400, 0)
            g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(0.5, 1, 1, 0.9, 0.35 * (1 - q)); g.add_color_stop_rgba(1, 1, 1, 1, 0)
            c.move_to(x - 300, -50); c.line_to(x + 500, -50); c.line_to(x + 300, H + 50); c.line_to(x - 500, H + 50); c.close_path()
            c.set_source(g); c.fill(); c.restore()


# ------------------------------------------------------------------ frame
def render(L, t):
    sec = section(t)[1]
    zoom = 1 + 0.012 * beat_pulse(t) * clamp(env('bass', t) * 1.6)
    sx = sy = 0
    c_ = None
    for c in CHANTS:
        if c[0] - 0.05 <= t < c[1]: c_ = c
    if c_ and sec != 'bridge':
        zoom += 0.03 * beat_pulse(t, 11)
    if 34.8 <= t < 35.7:
        k = 1 - (t - 34.8) / 0.9; sx = math.sin(t * 91) * 30 * k; sy = math.cos(t * 77) * 30 * k
    CHANT_GREEN[0] = chant_green(t); BEAT_T[0] = t
    for cr in L.all():
        cr.translate(W / 2 + sx, H / 2 + sy); cr.scale(zoom, zoom); cr.translate(-W / 2, -H / 2)
    cam = shot_camera(t, c_, sec)
    L.bg.save(); apply_cam(L.bg, cam, 0.45)
    backdrop(L, t)
    L.bg.restore()
    for cr in (L.fg, L.mask, L.ui): apply_cam(cr, cam, 1.0)
    if cam.get('iris') is not None:
        for cr in (L.fg, L.mask): cr.arc(W / 2, H / 2, cam['iris'], 0, TAU); cr.clip()
    leak(L, t)
    if sec in ('final',) and t >= 114.0:
        final_section(L, t)
    elif sec == 'outro':
        outro(L, t)
    elif c_ and c_[2] == DB:
        chant_db(L, t, c_)
    else:
        l = cur_line(t)
        if l is not None:
            shot(L, t, l)
        elif sec == 'intro':
            intro_idle(L, t)
    for cr in L.all(): cr.reset_clip(); cr.identity_matrix()
    hud(L, t)
    if not c_ or sec in ('final',):
        subtitle(L, t)
