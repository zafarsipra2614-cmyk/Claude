"""Storyboard + scene drawing for Dramay Baaz. render(cr, t) draws one full frame at song time t."""
from lib import *

DUR = A['dur']

# ---------------- timeline (seconds, from Whisper word timings) ----------------
# (start, roman urdu, english)
LYRICS = [
    (16.2, "Subah subah index khola", "Opened the index first thing in the morning"),
    (18.1, "Chai se pehle \"BUY!\" bola", "Shouted BUY before his morning chai"),
    (20.4, "\"Aaj toh upper lock!\" chillata hai", "Screams: \"Upper lock today!\""),
    (23.0, "Tip mili cousin ke yaar se", "Got a tip from his cousin's friend"),
    (25.5, "Thodi suni akhbaar se", "Heard a bit more from the newspaper"),
    (27.3, "Saari savings daao pe lagata hai", "Bets his entire savings on it"),
    (31.1, "Socha tha main raja banunga", "Thought I'd become a king"),
    (32.9, "Gaadi, bangla, sab lunga", "Car, bungalow, I'll have it all"),
    (34.8, "Lower lock ne aisa maara", "Then lower lock hit him hard"),
    (36.6, "Stop loss bhi bhool gaya bechara", "Poor guy even forgot his stop loss"),
    (45.5, "Green dekha toh naach liya", "Saw green, started dancing"),
    (49.3, "Red dekha toh bhaag liya", "Saw red, ran away"),
    (52.0, "Screen pe gussa jhaad liya", "Took it out on the screen"),
    (57.7, "Bina soche buy kiya", "Bought without thinking"),
    (59.8, "Dar ke phir sell kiya", "Then sold in fear"),
    (61.5, "Baith ke phir ro liya", "Then sat down and cried"),
    (69.5, "Dip aaya toh panic sell", "Market dips: panic sell"),
    (71.6, "Rally aayi toh phir se buy", "Market rallies: buy again"),
    (73.9, "Ulta seedha chalta rehta hai", "Always doing it backwards"),
    (76.5, "Portfolio ho gaya red", "The portfolio turned red"),
    (79.0, "Abba ne pakda apna head", "Abba held his head"),
    (80.8, "\"Market rigged hai Abba!\" kehta rehta hai", "\"The market's rigged, Abba!\" he keeps saying"),
    (85.7, "Green dekha toh naach liya", "Saw green, started dancing"),
    (89.7, "Red dekha toh bhaag liya", "Saw red, ran away"),
    (92.4, "Screen pe gussa jhaad liya", "Took it out on the screen"),
    (99.2, "Arre bas kar yaar", "Enough now, yaar"),
    (100.9, "Tukoon pe na chal", "Don't run on guesswork"),
    (102.5, "Pehle research, phir investment", "Research first, then invest"),
    (104.6, "Aaj se badal kal", "Start changing tomorrow, today"),
    (106.1, "Na jaadu hai, na kismat hai", "It's not magic, it's not luck"),
    (109.8, "Strategy se nikle hal", "Strategy finds the way"),
    (120.7, "Soch samajh ke trade kiya", "Traded with careful thought"),
    (122.6, "Plan bana ke hold kiya", "Made a plan and held"),
    (124.4, "Sabar se sab paa liya", "Patience got him everything"),
    (130.2, "Ab na tension, sirf direction", "No tension now, only direction"),
]
LYR_END = {16.2: 18.1}
for i, l in enumerate(LYRICS):
    nxt = LYRICS[i + 1][0] if i + 1 < len(LYRICS) else DUR
    LYR_END[l[0]] = min(nxt, l[0] + 3.6)
LYR_END[80.8] = 83.7; LYR_END[109.8] = 113.8; LYR_END[61.5] = 65.5; LYR_END[36.6] = 41.5

# chant windows: (start, end, phrase)
DB, NO = "DRAMAY BAAZ!", "AB NO DRAMAY BAAZI!"
CHANTS = [(0.0, 1.9, DB), (4.04, 5.9, DB), (7.84, 9.7, DB), (11.54, 13.6, DB),
          (43.4, 45.4, DB), (47.2, 48.9, DB), (51.0, 52.0, DB), (54.6, 57.5, DB), (65.7, 69.3, DB),
          (83.8, 85.6, DB), (87.6, 89.5, DB), (91.3, 92.3, DB), (95.0, 99.1, DB),
          (114.0, 120.5, NO), (126.4, 130.1, NO), (132.0, 133.8, NO),
          (134.9, 137.3, NO), (139.0, 141.6, NO), (143.1, 144.2, DB), (146.4, 148.0, DB), (156.2, 159.0, DB)]

SECTIONS = [(0, 'intro'), (16.2, 'verse1'), (31.1, 'dream'), (34.8, 'crash'), (43.4, 'chorus'), (69.5, 'verse2'),
            (83.8, 'chorus'), (99.2, 'bridge'), (114.0, 'final'), (143.1, 'outro')]
WIPES = [16.2, 43.4, 69.5, 83.8, 99.2, 114.0, 143.1]


def section(t):
    s = SECTIONS[0]
    for x in SECTIONS:
        if t >= x[0]: s = x
    return s


def chant_at(t):
    for c in CHANTS:
        if c[0] - 0.05 <= t < c[1]: return c
    return None


# ---------------- story-driven KSE-100 value ----------------
IDX_K = [(0, 158200), (16, 158400), (20.4, 160100), (31, 163600), (34.8, 164000), (37.5, 147600), (43, 147100),
         (69.5, 149800), (70.6, 145600), (72.8, 151200), (74.5, 146800), (76.5, 143900), (84, 144600), (99, 145200),
         (114, 147400), (143, 171500), (160, 172600)]


IDX_REF = {'intro': 158200, 'verse1': 158200, 'dream': 158200, 'crash': 164000, 'verse2': 150000, 'bridge': 145200,
           'final': 147400, 'outro': 147400}


def idx_ref(t):
    name = section(t)[1]
    if name == 'chorus': return idx_value(t, False)
    return IDX_REF[name]


def idx_value(t, wobble=True):
    v = IDX_K[-1][1]
    for (t0, v0), (t1, v1) in zip(IDX_K, IDX_K[1:]):
        if t0 <= t < t1:
            v = lerp(v0, v1, ease_io((t - t0) / (t1 - t0))); break
    if not wobble: return v
    name = section(t)[1]
    wob = {'chorus': 1600, 'verse2': 400, 'final': 120, 'bridge': 60}.get(name, 150)
    if name == 'chorus':  # green lines go up, red lines go down
        v += wob * mood_sign(t)
    return v + wob * 0.25 * math.sin(t * 2.3) + wob * 0.15 * math.sin(t * 7.1)


def mood_sign(t):
    """+1 green, -1 red, 0 neutral — what the chorus visuals are doing."""
    for s, e, sign in [(45.5, 49.2, 1), (49.3, 57.6, -1), (57.7, 59.7, 1), (59.8, 65.6, -1), (85.7, 89.6, 1), (89.7, 99.2, -1)]:
        if s <= t < e: return sign * ease_out(prog(t, s, 0.5))
    return 0


def market_mood(t):
    name = section(t)[1]
    if name in ('crash', 'verse2'): return -1
    if name == 'chorus': return mood_sign(t) or -0.3
    if name in ('verse1', 'dream', 'final', 'outro'): return 1
    return 0.2


# ---------------- backgrounds ----------------
def bg_grad(cr, top, bot, a=0.85):
    """Crayon wash: soft gradient plus big diagonal scribble strokes, so paper tooth shows through."""
    paper = STYLE.get('paper_rgb', (0.96, 0.94, 0.88))
    top, bot = mix(top, paper, STYLE['wash_mix']), mix(bot, paper, STYLE['wash_mix']); a = STYLE['wash_a']
    mode = STYLE.get('bg', 'scribble')
    if mode == 'neon':
        top, bot = mix(top, (0.04, 0.0, 0.1), 0.75), mix(bot, (0.01, 0.0, 0.03), 0.85)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgba(0, *top, a); g.add_color_stop_rgba(1, *bot, a)
    cr.rectangle(-200, -200, W + 400, H + 400); cr.set_source(g); cr.fill()
    if mode == 'neon':
        hz = H * 0.6; T = BOIL[0] / 8
        cr.set_line_width(2.5)
        for k in range(14):
            yy = hz + (H - hz) * ((k + (T * 0.8) % 1) / 14) ** 2
            cr.move_to(-100, yy); cr.line_to(W + 100, yy)
        for k in range(-16, 17):
            cr.move_to(W / 2 + k * 40, hz); cr.line_to(W / 2 + k * 260, H + 60)
        rgb(cr, (1.0, 0.2, 0.75), 0.35); cr.stroke()
        g2 = cairo.LinearGradient(0, hz - 140, 0, hz + 20); g2.add_color_stop_rgba(0, 1, 0.2, 0.7, 0); g2.add_color_stop_rgba(1, 1, 0.3, 0.6, 0.35)
        cr.rectangle(0, hz - 140, W, 160); cr.set_source(g2); cr.fill()
        return
    if mode == 'plain':
        return
    if mode == 'rays':   # truck art sunburst / anime speed burst
        cx, cy = W / 2, H * 0.55; n = 28
        for k in range(n):
            a0 = k * TAU / n + BOIL[0] * 0.004
            cr.new_path(); cr.move_to(cx, cy); cr.arc(cx, cy, 2400, a0, a0 + TAU / n / 2); cr.close_path()
            rgb(cr, (1, 1, 1) if STYLE.get('anime') else mix(top, (1, 0.85, 0.2), 0.35), 0.10 if STYLE.get('anime') else 0.3); cr.fill()
        return
    if mode == 'bands':
        rnd = random.Random(5)
        for k in range(5):
            y0 = H * (0.12 + k * 0.2)
            c = mix(top, bot, k / 4)
            c = mix(c, (1, 1, 1), 0.12 if k % 2 else 0.0)
            cr.new_path(); cr.move_to(-100, H + 100); cr.line_to(-100, y0)
            for j in range(1, 11):
                cr.line_to(-100 + j * 220, y0 + rnd.uniform(-35, 35))
            cr.line_to(W + 100, H + 100); cr.close_path()
            fill(cr, c)
        return
    if mode == 'halftone':
        dk = mix(bot, (0, 0, 0), 0.35)
        sp = 30
        for row in range(0, H // sp + 2):
            r = 2 + 9 * (row * sp / H) ** 1.3
            for col in range(0, W // sp + 2):
                circle(cr, col * sp + (sp / 2 if row % 2 else 0), row * sp, r)
            rgb(cr, dk, 0.35); cr.fill()
        return
    rnd = random.Random(42)
    for k in range(34):
        y0 = rnd.uniform(-300, H + 100); c = mix(top, bot, clamp(y0 / H))
        cr.new_path(); cr.move_to(-100, y0)
        for j in range(1, 9):
            cr.line_to(-100 + j * 280, y0 + j * rnd.uniform(25, 45) + (40 if j % 2 else -40))
        wobble(cr, 6, k)
        cr.set_line_width(rnd.uniform(40, 90)); cr.set_line_cap(cairo.LINE_CAP_ROUND)
        rgb(cr, mix(c, (0, 0, 0), 0.18), 0.16); cr.stroke()


def grid(cr, t, col, a=0.12, speed=30, step=96):
    p = beat_pulse(t) * env('bass', t)
    cr.set_line_width(2)
    off = (t * speed) % step
    for x in range(-step, W + step, step):
        cr.move_to(x - off, 0); cr.line_to(x - off, H)
    for y in range(0, H + step, step):
        cr.move_to(0, y); cr.line_to(W, y)
    rgb(cr, col, a + 0.12 * p); cr.stroke()


SKY_RND = random.Random(3)
SKYLINE = []
x = -40
while x < W + 80:
    w = SKY_RND.randint(50, 130); h = SKY_RND.randint(90, 330)
    SKYLINE.append((x, w, h, SKY_RND.random())); x += w + SKY_RND.randint(-10, 12)


def skyline(cr, t, base, col, a=1.0, lights=0.0):
    for (x, w, h, r) in SKYLINE:
        cr.rectangle(x, base - h, w, h + 400); fill(cr, col, a)
        if r > 0.8:  # minaret
            cr.rectangle(x + w / 2 - 8, base - h - 90, 16, 90); fill(cr, col, a)
            circle(cr, x + w / 2, base - h - 96, 16); fill(cr, col, a)
        if lights > 0:
            rnd = random.Random(int(x))
            for wy in range(int(base - h + 20), int(base) - 10, 34):
                for wx in range(int(x + 10), int(x + w - 14), 26):
                    if rnd.random() < 0.35:
                        on = 0.5 + 0.5 * math.sin(t * 2 + wx * 0.1 + wy)
                        cr.rectangle(wx, wy, 12, 16); fill(cr, C['gold2'], a * lights * (0.4 + 0.6 * on))


def particles(cr, t, n, col, a=0.5, seed=1, up=True, size=6):
    rnd = random.Random(seed)
    for k in range(n):
        x0, y0, sp, ph = rnd.random() * W, rnd.random() * H, 20 + rnd.random() * 60, rnd.random() * TAU
        y = (y0 - t * sp) % (H + 40) - 20 if up else (y0 + t * sp) % (H + 40) - 20
        x = x0 + math.sin(t * 0.7 + ph) * 30
        circle(cr, x, y, size * (0.5 + rnd.random())); fill(cr, col, a * (0.4 + 0.6 * rnd.random()))


def candle_rain(cr, t, sign, n=26, seed=5, a=1.0):
    """Candles streaming upward (sign>0) or falling (sign<0), beat-reactive length."""
    rnd = random.Random(seed)
    b = beat_pulse(t)
    for k in range(n):
        x = rnd.random() * W; sp = 200 + rnd.random() * 300; ph = rnd.random() * (H + 400)
        y = (ph - t * sp) % (H + 400) - 200 if sign > 0 else (ph + t * sp) % (H + 400) - 200
        h = 60 + rnd.random() * 120 + 50 * b
        w = 18 + rnd.random() * 18
        candle(cr, x, y + h, y, y - 30, y + h + 30, w, up=sign > 0, a=a * (0.25 + 0.5 * rnd.random()))


def eq_bars(cr, t, y, h, a=0.9):
    """Candle equalizer driven by bass/mid/high envelopes."""
    n = 48; bw = W / n
    for i in range(n):
        band = 'bass' if i % 3 == 0 else 'mid' if i % 3 == 1 else 'high'
        v = env(band, t - i * 0.004) * (0.6 + 0.4 * math.sin(i * 1.7 + t * 3)) ** 2
        v = clamp(v * (0.7 + 0.6 * beat_pulse(t)))
        hh = 10 + h * v
        up = math.sin(i * 2.1 + int(t * 2.13)) > -0.2 if market_mood(t) >= 0 else math.sin(i * 2.1 + int(t * 2.13)) > 0.5
        candle(cr, i * bw + bw / 2, y, y - hh, y - hh - 12, y + 8, bw * 0.55, up=up, a=a)


def vignette(cr, a=0.55):
    return
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, a)
    cr.rectangle(0, 0, W, H); cr.set_source(g); cr.fill()


# ---------------- HUD ----------------
TICKERS = ['OGDC', 'PPL', 'HUBC', 'LUCK', 'ENGRO', 'MEBL', 'UBL', 'MCB', 'PSO', 'TRG', 'SYS', 'FFC', 'EFERT', 'MARI',
           'BAHL', 'HBL', 'POL', 'DGKC', 'MLCF', 'NBP', 'KEL', 'PAEL', 'SEARL', 'ATRL']
TRND = random.Random(11)
TBASE = [(s, TRND.uniform(20, 900), TRND.uniform(0.2, 1.0)) for s in TICKERS]


def ticker_tape(cr, t):
    y0 = H - 44
    cr.rectangle(0, y0, W, 44); fill(cr, (0.02, 0.03, 0.03), 0.92)
    stroke_line(cr, [(0, y0), (W, y0)], 3, C['green'], 0.8, cairo.LINE_CAP_BUTT)
    m = market_mood(t)
    font(cr, 'mono', 22)
    x = -((t * 140) % 2600)
    while x < W:
        for i, (s, p, k) in enumerate(TBASE):
            ch = (m * 4.5 + math.sin(i * 3.3 + t * 0.2) * 2.2) * k
            ch = clamp(ch, -10, 10)
            col = C['green'] if ch >= 0 else C['red']
            seg = f"{s} {p * (1 + ch / 100):.2f} "
            text(cr, s, x, y0 + 22, 'mono', 22, C['white'], 0.9, 'l')
            x += text_w(cr, s + ' ', 'mono', 22)
            arrow = ('+' if ch >= 0 else '') + f"{ch:.2f}%"
            text(cr, f"{p * (1 + ch / 100):.2f} {arrow}", x, y0 + 22, 'mono', 22, col, 1, 'l')
            x += text_w(cr, f"{p * (1 + ch / 100):.2f} {arrow}", 'mono', 22) + 46
            if x > W: break
        if x > W: break


def index_widget(cr, t, a=1.0):
    v = idx_value(t); v0 = idx_ref(t)
    ch = (v - v0) / v0 * 100
    col = C['green'] if ch >= 0 else C['red']
    x, y = W - 430, 34
    col = C['green2'] if ch >= 0 else C['red']
    cr.save(); cr.translate(x + 200, y + 46); cr.rotate(0.015); cr.translate(-x - 200, -y - 46)
    rrect(cr, x, y, 400, 96, 14); fill(cr, (0.99, 0.98, 0.94), a, keep=True); outline(cr, 5, col, a)
    text(cr, 'KSE-100', x + 24, y + 26, 'mono', 26, (0.35, 0.35, 0.35), a, 'l')
    text(cr, f"{v:,.0f}", x + 22, y + 64, 'anton', 50, TXT, a, 'l')
    arrow = '▲' if ch >= 0 else '▼'
    text(cr, f"{'+' if ch >= 0 else ''}{ch:.2f}%", x + 380, y + 66, 'interb', 34, col, a, 'r')
    # mini spark line
    cr.save()
    pts = [(x + 230 + k * 7, y + 30 - (idx_value(t - (19 - k) * 0.25) - v) / 900) for k in range(20)]
    stroke_line(cr, pts, 4, col, a * 0.9)
    cr.restore(); cr.restore()


def brand_bug(cr, t, a=0.9):
    dark = STYLE.get('dark', False)
    x0 = STYLE.get('bug_x', 36)
    rrect(cr, x0, 36, 330, 84, 14); rgb(cr, (0.06, 0.06, 0.08) if dark else (1, 1, 1), 0.9 * a); cr.fill()
    brand_img(cr, 'wordmark', x0 + 165, 36 + 42, 290, a)


# ---------------- captions ----------------
def caption(cr, t):
    cur = None
    for l in LYRICS:
        if l[0] - 0.1 <= t < LYR_END[l[0]]: cur = l
    if not cur: return
    t0, ro, en = cur; t1 = LYR_END[t0]
    a = clamp((t - t0 + 0.1) / 0.15) * clamp((t1 - t) / 0.25)
    words = ro.split(' ')
    font(cr, 'anton', 58)
    gap = max(22, cr.text_extents('n').x_advance * 0.9)
    widths = [cr.text_extents(w_).x_advance + gap for w_ in words]
    total = sum(widths) - gap
    font(cr, 'inter', 26); ew = cr.text_extents(en).x_advance
    bw = max(total, ew) + 120
    y = H - 160
    slide = ease_out(clamp((t - t0 + 0.1) / 0.3))
    cr.save(); cr.translate((1 - slide) * -80, 0)
    cap = STYLE.get('caption', 'paper')
    cr.save(); cr.translate(W / 2, y); cr.rotate(-0.012 if cap == 'paper' else 0); cr.translate(-W / 2, -y)
    if cap == 'comic':
        cr.rectangle(W / 2 - bw / 2, y - 54, bw, 122); rgb(cr, (1, 0.9, 0.25), a); cr.fill_preserve(); cr.set_line_width(6); rgb(cr, (0, 0, 0), a); cr.stroke()
    elif cap == 'neon':
        rrect(cr, W / 2 - bw / 2, y - 54, bw, 122, 22); rgb(cr, (0.06, 0.02, 0.12), 0.82 * a); cr.fill_preserve()
        cr.set_line_width(4); rgb(cr, (0.3, 1, 0.5), a); cr.stroke()
    elif cap == 'dialog':   # retro RPG dialogue box
        cr.rectangle(W / 2 - bw / 2, y - 54, bw, 122); rgb(cr, (0.05, 0.07, 0.25), 0.95 * a); cr.fill_preserve()
        cr.set_line_width(8); rgb(cr, (1, 1, 1), a); cr.stroke()
        cr.rectangle(W / 2 - bw / 2 + 10, y - 44, bw - 20, 102); cr.set_line_width(3); rgb(cr, (0.6, 0.7, 1), a); cr.stroke()
    elif cap == 'truck':
        rrect(cr, W / 2 - bw / 2, y - 54, bw, 122, 40); rgb(cr, (1, 0.85, 0.15), a); cr.fill_preserve()
        cr.set_line_width(7); rgb(cr, (0.85, 0.05, 0.2), a); cr.stroke()
        for k in range(int(bw / 40)):
            circle(cr, W / 2 - bw / 2 + 30 + k * 40, y - 54, 6); rgb(cr, (0.1, 0.6, 0.9), a); cr.fill()
    elif cap == 'plain':
        cr.rectangle(W / 2 - bw / 2, y - 54, bw, 122); rgb(cr, (1, 1, 1), 0.95 * a); cr.fill_preserve(); cr.set_line_width(5); rgb(cr, TXT, a); cr.stroke()
    elif cap == 'riso':
        cr.rectangle(W / 2 - bw / 2, y - 54, bw, 122); rgb(cr, (1.0, 0.85, 0.12), a); cr.fill()
    else:
        rrect(cr, W / 2 - bw / 2, y - 54, bw, 122, 10); fill(cr, (0.995, 0.985, 0.95), a, keep=True); outline(cr, 5, C['ink'], a * 0.85)
    for tx in ((W / 2 - bw / 2 + 10, W / 2 + bw / 2 - 70) if cap == 'paper' else ()):   # masking tape corners
        cr.save(); cr.translate(tx + 30, y - 54); cr.rotate(-0.3 if tx < W / 2 else 0.3)
        cr.rectangle(-45, -16, 90, 32); fill(cr, (0.95, 0.85, 0.55), 0.7 * a); cr.restore()
    cr.restore()
    # word-by-word reveal across ~65% of the line
    span = max(0.6, (t1 - t0) * 0.6)
    x = W / 2 - total / 2
    for i, w_ in enumerate(words):
        wt = t0 + span * i / max(1, len(words))
        p = clamp((t - wt) / 0.18)
        if p <= 0: x += widths[i]; continue
        sc = back_out(p) if p < 1 else 1
        hot = clamp(1 - (t - wt) / 0.4)
        base_c = (0.95, 0.95, 1.0) if STYLE.get('caption') in ('neon', 'dialog') else TXT
        col = mix(base_c, (0.9, 0.45, 0.0), hot)
        if any(k in w_.upper() for k in ('BUY', 'GREEN', 'UPPER')): col = C['green2']
        if any(k in w_.upper() for k in ('RED', 'LOWER', 'SELL', 'RIGGED', 'PANIC')): col = C['red']
        cr.save(); cr.translate(x + widths[i] / 2, y - 6); cr.scale(sc, sc)
        text(cr, w_, -widths[i] / 2, 0, 'anton', 62, col, a, 'l', stroke=0)
        cr.restore()
        x += widths[i]
    text(cr, en, W / 2, y + 44, 'inter', 28, (0.75, 0.75, 0.85) if STYLE.get('caption') in ('neon', 'dialog') else (0.3, 0.3, 0.3), a * clamp((t - t0 - 0.25) / 0.3))
    cr.restore()


# ---------------- chant slam ----------------
def chant_overlay(cr, t):
    c = chant_at(t)
    if not c: return
    t0, t1, phrase = c
    lt = t - t0
    a = clamp(lt / 0.06) * clamp((t1 - t) / 0.2)
    bp = beat_pulse(t, 9)
    i = CHANTS.index(c)
    rot = (-0.06 if i % 2 else 0.05)
    m = ease_io(clamp((lt - 1.5) / 0.35)) if t1 - t0 > 2.2 else 0.0
    cr.save(); cr.translate(W / 2, lerp(H / 2 - 40, 200, m)); cr.scale(lerp(1, 0.36, m), lerp(1, 0.36, m))
    # darken scene
    cr.save(); cr.identity_matrix(); cr.rectangle(0, 0, W, H); fill(cr, (0, 0, 0), 0.45 * a * (1 - m)); cr.restore()
    # radiating slanted bars
    cr.save(); cr.rotate(rot)
    for k in range(-6, 7):
        para(cr, k * 170 - 60 - (lt * 300) % 170, -700, 70, 1400, slant=0.3, r=4)
        fill(cr, C['green'] if k % 2 else C['white'], 0.07 * a * (1 - m))
    cr.restore()
    s = (back_out(clamp(lt / 0.28)) if lt < 0.28 else 1) * (1 + 0.08 * bp)
    cr.rotate(rot); cr.scale(s, s)
    if phrase == DB:
        size = 190
        burst(cr, 0, 0, 640, 520, 18, C['red'] if mood_sign(t) < 0 else C['green2'], rot=t * 0.4, a=a * 0.9 * (1 - m))
        jitter = 5 * bp
        text(cr, 'DRAMAY', -8 + jitter, -95, 'bungee', size, C['white'], a, stroke=22, shadow=14)
        text(cr, 'BAAZ!', 8 - jitter, 105, 'bungee', size * 1.12, C['gold'], a, stroke=22, shadow=14)
    else:
        burst(cr, 0, 0, 700, 560, 22, C['green2'], rot=t * 0.3, a=a * 0.9 * (1 - m))
        text(cr, 'AB NO', 0, -150, 'bungee', 120, C['white'], a, stroke=18, shadow=10)
        w = text(cr, 'DRAMAY', 0, 0, 'bungee', 150, C['gold'], a, stroke=20, shadow=10)
        text(cr, 'BAAZI!', 0, 150, 'bungee', 150, C['gold'], a, stroke=20, shadow=10)
        p = ease_out(clamp((lt - 0.25) / 0.3))
        if p > 0:
            stroke_line(cr, [(-w / 2 - 30, 60), (-w / 2 - 30 + (w + 60) * p, -40 + 100 * (1 - p) * 0)], 34, C['ink'], a)
            stroke_line(cr, [(-w / 2 - 30, 60), (-w / 2 - 30 + (w + 60) * p, -40)], 22, C['green'], a)
    cr.restore()


# ---------------- transitions ----------------
def wipes(cr, t):
    for tb in WIPES:
        d = t - tb
        if -0.45 < d < 0.45:
            p = (d + 0.45) / 0.9  # 0..1, fully covered at 0.5
            for k, col in enumerate((C['green'], C['white'], C['green2'])):
                pk = clamp(p * 1.25 - k * 0.12)
                x = lerp(-W * 1.6, W * 1.3, ease_io(pk))
                para(cr, x + k * 120, -50, W * 1.15, H + 100, slant=0.35, r=0); fill(cr, col)


def flash(cr, t, at, d=0.25, col=C['white']):
    if at <= t < at + d:
        cr.rectangle(0, 0, W, H); fill(cr, col, (1 - (t - at) / d) * 0.85)


# ---------------- character motion helpers ----------------
def dance(t, wild=1.0):
    i = beat_index(t); ph = beat_phase(t); side = 1 if i % 2 else -1
    up = math.sin(ph * math.pi)
    return dict(lA=(-118 + 28 * side * wild, -20), rA=(118 + 28 * side * wild, 20), lL=(-12 - 10 * up, 15 * up), rL=(12 + 10 * up, -15 * up),
                lean=8 * side * wild, bob=30 * (1 - ph) * wild, eyes='happy', mouth='grin', head_tilt=-6 * side)


def run(t, speed=9):
    ph = t * speed
    s = math.sin(ph)
    return dict(lA=(50 * s, -70), rA=(-50 * s, 70), lL=(-40 * s, 40 + 30 * max(0, s)), rL=(40 * s, 40 + 30 * max(0, -s)),
                lean=10, bob=12 * abs(math.cos(ph)), eyes='shock', mouth='shout', sweat=1, brows='sad')


def pop(t, t0, d=0.35):
    return max(0.001, back_out(clamp((t - t0) / d))) if t >= t0 else 0.001


def shake(t, at, d=0.6, amp=26):
    if at <= t < at + d:
        k = 1 - (t - at) / d
        return (math.sin(t * 91) * amp * k, math.cos(t * 77) * amp * k)
    return (0, 0)


# ============================================================
#                         SCENES
# ============================================================

def scene_intro(cr, t):
    bg_grad(cr, (0.1, 0.3, 0.18), (0.04, 0.16, 0.08))
    grid(cr, t, C['green'], 0.06)
    # trading-floor board of flickering numbers
    rnd = random.Random(int(t * 8))
    for r in range(7):
        for c in range(9):
            x = 120 + c * 200; y = 210 + r * 92
            up = rnd.random() > 0.45
            v = 100 + ((r * 13 + c * 7) * 37) % 800 + rnd.random()
            cr.rectangle(x - 80, y - 32, 170, 64); fill(cr, (0.02, 0.05, 0.03), 0.9)
            text(cr, f"{v:7.2f}", x + 5, y, 'interb', 40, (0.4, 1, 0.3) if up else (1, 0.35, 0.4), 0.55 + 0.45 * env('high', t))
    eq_bars(cr, t, H - 70, 260, 0.9)
    # title assembles after the chants
    p = clamp((t - 13.6) / 0.5)
    if p > 0:
        a = p * clamp((16.2 - t) / 0.3 + 1)
        cr.save(); cr.translate(W / 2, H / 2 - 40); s = back_out(p); cr.scale(s, s)
        para(cr, -620, -150, 1240, 300, slant=0.25, r=20); fill(cr, (0.01, 0.02, 0.02), 0.92 * a, keep=True); outline(cr, 8, C['green'], a)
        text(cr, 'DRAMAY BAAZ', 0, -20, 'bungee', 130, C['white'], a, stroke=14)
        text(cr, 'a PSX tragedy-comedy', 0, 90, 'inter', 34, C['green'], a)
        cr.restore()


def morning_bg(cr, t, lt):
    sun = ease_out(clamp(lt / 3))
    bg_grad(cr, mix((0.05, 0.08, 0.2), (0.98, 0.62, 0.3), sun), mix((0.15, 0.1, 0.2), (1.0, 0.85, 0.55), sun))
    cr.save()
    sy = lerp(900, 360, sun)
    for r, a in ((260, 0.12), (190, 0.2), (130, 1)):
        circle(cr, 1450, sy, r * (1 + 0.04 * beat_pulse(t))); fill(cr, (1, 0.9, 0.5), a)
    cr.restore()
    skyline(cr, t, 860, mix((0.08, 0.06, 0.15), (0.45, 0.25, 0.3), sun), 1, lights=1 - sun)
    cr.rectangle(0, 860, W, 300); fill(cr, mix((0.1, 0.08, 0.12), (0.55, 0.36, 0.3), sun))


def phone_index(t, up=True):
    def content(c):
        v = idx_value(t)
        text(c, 'KSE-100', 0, -140, 'mono', 22, C['grey'])
        text(c, f"{v:,.0f}", 0, -100, 'anton', 44, C['white'])
        pts = [(-90 + k * 9, 60 - (idx_value(t - (20 - k) * 0.4) - 156000) / 90) for k in range(21)]
        stroke_line(c, pts, 5, C['green'] if up else C['red'])
        c.rectangle(-80, 120, 160, 46); fill(c, C['green']); text(c, 'BUY', 0, 143, 'bungee', 26, C['white'])
    return content


def scene_verse1(cr, t):
    lt = t - 16.2
    morning_bg(cr, t, lt)
    bx = 640
    # 16.2 subah: phone pops
    if t < 18.1:
        pose = dict(rA=(-160, 40), lA=(-20, 10), eyes='open', look=(1, -1), mouth='smile')
        hands = baaz(cr, bx, 900, 1.0, pose, t)
        ps = pop(t, 16.5)
        phone(cr, 1180, 470, 1.25 * ps, t, phone_index(t))
    # 18.1 chai + BUY
    elif t < 20.4:
        press = 1.0 if (t - 18.9) % 0.47 < 0.12 and t > 18.9 else 0.0
        pose = dict(rA=(-120 + 30 * press, 0), lA=(-40, -20), eyes='dollar', mouth='shout', look=(1, 0))
        baaz(cr, bx, 900, 1.0, pose, t)
        chai(cr, 300, 760, 1.1 * pop(t, 18.1), t)
        button(cr, 1250, 560, 480, 200, 'BUY!', C['green2'], press, pop(t, 18.4) > 0 and 1 or 0)
        if pop(t, 18.4) > 0:
            for k in range(8):
                ang = k * TAU / 8 + t
                r = 280 + 30 * beat_pulse(t)
                stroke_line(cr, [(1250 + math.cos(ang) * r, 560 + math.sin(ang) * r * .6), (1250 + math.cos(ang) * (r + 50), 560 + math.sin(ang) * (r + 50) * .6)], 10, C['white'], 0.7)
    # 20.4 upper lock
    elif t < 23.0:
        pose = dict(lA=(-165, -10), rA=(165, 10), eyes='happy', mouth='shout', bob=20 * beat_pulse(t), blush=1)
        baaz(cr, 560, 900, 1.0, pose, t)
        for k in range(6):
            yy = (900 - ((t - 20.4) * 500 + k * 180) % 900)
            cr.save(); cr.translate(1000 + k * 140, yy)
            cr.move_to(0, -60); cr.line_to(45, 0); cr.line_to(16, 0); cr.line_to(16, 60); cr.line_to(-16, 60); cr.line_to(-16, 0); cr.line_to(-45, 0); cr.close_path()
            fill(cr, C['green'], 0.8, keep=True); outline(cr, 5); cr.restore()
        s = pop(t, 20.7, 0.3) * (1 + 0.06 * beat_pulse(t))
        stamp(cr, 1380, 500, 'UPPER LOCK', 92, C['green'], -0.1, 1, s)
        bubble(cr, 900, 250, 520, 120, (-1, 1))
        text(cr, 'AAJ TOH UPPER LOCK!', 900, 250, 'anton', 52, C['ink'], pop(t, 20.5))
    # 23.0 tip from cousin's friend
    elif t < 25.5:
        pose = dict(rA=(-150, 30), lA=(-20, 0), eyes='open', look=(1, 0), mouth='o', brows='raised')
        baaz(cr, 520, 900, 1.0, pose, t)
        x0 = 860
        para(cr, x0, 150, 860, 640, slant=0.04, r=24); fill(cr, (0.07, 0.17, 0.12), 0.95, keep=True); outline(cr, 6)
        cr.rectangle(x0 + 10, 150, 840, 90); fill(cr, (0.03, 0.33, 0.25))
        circle(cr, x0 + 70, 195, 30); fill(cr, C['gold'])
        text(cr, "Cousin ka Dost", x0 + 120, 185, 'interb', 34, C['white'], 1, 'l')
        text(cr, "online", x0 + 120, 218, 'inter', 22, (0.7, 0.9, 0.8), 1, 'l')
        msgs = [("Bhai ek tip hai...", 23.2), ("Ye share pakka 10x jayega!", 23.8), ("Andar ki khabar hai, kisi ko mat batana", 24.4), ("Sab laga do!!!", 25.0)]
        for i, (m, mt) in enumerate(msgs):
            p = pop(t, mt, 0.3)
            if p <= 0: continue
            cr.save(); cr.translate(x0 + 50, 280 + i * 120); cr.scale(p, p)
            wdt = text_w(cr, m, 'inter', 34) + 50
            rrect(cr, 0, 0, wdt, 80, 18); fill(cr, (0.13, 0.23, 0.2), keep=True); outline(cr, 3, (0.2, 0.4, 0.3))
            text(cr, m, 25, 40, 'inter', 34, C['white'], 1, 'l')
            cr.restore()
    # 25.5 newspaper
    elif t < 27.3:
        pose = dict(lA=(-120, -40), rA=(120, 40), eyes='dollar', mouth='grin')
        baaz(cr, 480, 900, 1.0, pose, t)
        p = ease_out(clamp((t - 25.5) / 0.5))
        newspaper(cr, 1220, 470, 1.3 * p, (1 - p) * 8 + 0.05, 'MARKET MEIN TEZI!')
    # 27.3 savings all in
    else:
        lt2 = t - 27.3
        pose = dict(lA=(-160, 20), rA=(160, -20), eyes='dollar', mouth='grin', bob=15 * beat_pulse(t))
        baaz(cr, 440, 900, 1.0, pose, t)
        crack = clamp(lt2 / 1.2)
        if crack < 1:
            piggy(cr, 980, 640, 1.4, crack)
        else:
            stamp(cr, 980, 640, 'ALL IN', 110, C['gold'], -0.15, 1, pop(t, 28.5))
        # coins fly into a chart
        for k in range(16):
            ph = ((t - 27.6) * 0.9 + k / 16) % 1 if t > 27.6 else 0
            if ph <= 0: continue
            x = lerp(980, 1600, ph); y = 640 - math.sin(ph * math.pi) * 380 + ph * -60
            (coin if k % 3 else lambda c, x, y, r, rot: note(c, x, y, 0.8, rot))(cr, x, y, 34, t * 6 + k)
        monitor(cr, 1640, 380, 360, 240, content=lambda c: [candle(c, 1520 + i * 45, 470 - i * 18, 450 - i * 24, 430 - i * 24, 480 - i * 18, 26, True) for i in range(6)])


def scene_dream(cr, t):
    """31.1 - 34.8: raja banunga / gaadi bangla."""
    bg_grad(cr, (0.25, 0.1, 0.35), (0.9, 0.6, 0.2))
    particles(cr, t, 50, C['gold2'], 0.6, seed=4, size=5)
    for k in range(10):
        ang = k * TAU / 10 + t * 0.3
        cr.move_to(W / 2, 1200); cr.line_to(W / 2 + math.cos(ang) * 2400, 1200 + math.sin(ang) * 2400)
        cr.line_to(W / 2 + math.cos(ang + 0.15) * 2400, 1200 + math.sin(ang + 0.15) * 2400); cr.close_path(); fill(cr, (1, 0.9, 0.5), 0.07)
    # dream cloud
    cr.save(); cr.translate(W / 2 + 80, 400); s = pop(t, 31.15, 0.5); cr.scale(s, s)
    for (cx, cy, r) in [(-420, 30, 150), (-220, -80, 190), (40, -110, 210), (300, -60, 180), (450, 60, 140), (200, 120, 170), (-150, 120, 180)]:
        circle(cr, cx, cy, r); fill(cr, C['white'], 0.95)
    cr.restore()
    for (cx, cy, r, d) in [(620, 720, 26, 31.2), (700, 640, 40, 31.3)]:
        circle(cr, cx, cy, r * pop(t, d)); fill(cr, C['white'], 0.95)
    # dream items on beats
    crown(cr, 1000, 320, 1.4 * pop(t, 31.6), 1)
    if t > 32.9:
        car(cr, 760, 470, 1.1 * pop(t, 32.95), t)
        house(cr, 1320, 470, 1.15 * pop(t, 33.45))
        text(cr, 'SAB LUNGA!', 1040, 230, 'bungee', 70, C['gold'], pop(t, 33.9), stroke=10)
    pose = dict(lA=(-150, -30), rA=(150, 30), eyes='happy', mouth='grin', blush=1, bob=12 * beat_pulse(t))
    baaz(cr, 420, 940, 0.95, pose, t)
    crown(cr, 420, 940 - 0.95 * 640, 0.6 * pop(t, 31.6), 1)


def scene_crash(cr, t):
    """34.8 - 43.4: lower lock + forgot stop loss."""
    lt = t - 34.8
    bg_grad(cr, (0.25, 0.0, 0.03), (0.06, 0.0, 0.01))
    grid(cr, t, C['red'], 0.1, speed=-120)
    candle_rain(cr, t, -1, n=30, a=0.8)
    # plunging chart line
    pts = []
    for k in range(40):
        x = 100 + k * 45
        p = clamp(lt * 1.6 - k / 40)
        y = 250 + (k / 40) ** 2 * 600 * min(1, lt * 0.8) + math.sin(k * 1.3) * 30
        pts.append((x, y))
    n = int(clamp(lt * 1.5) * 39) + 1
    if n > 1:
        stroke_line(cr, pts[:n], 22, C['ink'], 0.8); stroke_line(cr, pts[:n], 12, C['red'])
    # giant red candle smashes down at 34.8
    d = ease_in(clamp(lt / 0.35))
    cy = lerp(-700, 160, d)
    candle(cr, 1500, cy, cy + 620, cy - 80, cy + 760, 220, up=False)
    if t < 36.6:
        pose = dict(lA=(-150, -40), rA=(150, 40), eyes='shock', mouth='shout', brows='sad', sweat=1, lean=-8)
        baaz(cr, 700, 920, 1.0, pose, t)
        # crown falls off
        cp = clamp(lt / 0.9)
        crown(cr, 700 + cp * 260, 920 - 640 + cp * cp * 640, 0.6, 1 - cp * 0.5)
        stamp(cr, 1150, 420, 'LOWER LOCK', 110, (1, 0.25, 0.3), 0.12, 1, pop(t, 35.0, 0.25) * (1 + 0.05 * beat_pulse(t)))
    else:
        # dizzy + stop-loss note flying away
        sw = math.sin(t * 3) * 6
        pose = dict(lA=(-30, 20), rA=(30, -20), eyes='dizzy', mouth='wavy', brows='sad', lean=sw, head_tilt=sw)
        baaz(cr, 700, 920, 1.0, pose, t)
        for k in range(5):
            ang = t * 4 + k * TAU / 5
            burst(cr, 700 + math.cos(ang) * 120, 330 + math.sin(ang) * 30, 22, 10, 5, C['gold'])
        fp = clamp((t - 36.8) / 2.5)
        nx = lerp(820, 1750, fp); ny = 500 - math.sin(fp * 6) * 60 - fp * 300
        cr.save(); cr.translate(nx, ny); cr.rotate(math.sin(t * 6) * 0.4 + fp * 2)
        cr.rectangle(-110, -80, 220, 160); fill(cr, (1, 0.93, 0.35), keep=True); outline(cr, 5)
        text(cr, 'STOP', 0, -30, 'bungee', 44, C['red2']); text(cr, 'LOSS', 0, 30, 'bungee', 44, C['red2'])
        cr.restore()
        text(cr, 'BECHARA...', 1250, 700, 'bungee', 80, C['white'], pop(t, 38.3), stroke=10)
        # build-up to chorus: equalizer swell
        if t > 39.5:
            eq_bars(cr, t, H - 60, 120 + 200 * clamp((t - 39.5) / 3.9), 0.85)


def chorus_bg(cr, t):
    s = mood_sign(t)
    top = mix((0.08, 0.06, 0.1), C['forest'], max(0, s)); top = mix(top, (0.3, 0.0, 0.05), max(0, -s))
    bot = mix((0.02, 0.02, 0.03), (0.0, 0.08, 0.0), max(0, s)); bot = mix(bot, (0.08, 0.0, 0.01), max(0, -s))
    bg_grad(cr, top, bot)
    grid(cr, t, C['green'] if s >= 0 else C['red'], 0.08, speed=60 * (1 if s >= 0 else -1))
    if abs(s) > 0.05:
        candle_rain(cr, t, s, n=22, a=abs(s) * 0.7)
    eq_bars(cr, t, H - 60, 140, 0.55)


def line_at(t, times):
    cur = None
    for x in times:
        if t >= x: cur = x
    return cur


def scene_chorus(cr, t):
    chorus_bg(cr, t)
    second = t > 80
    L = line_at(t, [43.4, 45.5, 49.3, 52.0, 57.7, 59.8, 61.5, 65.6] if not second else [83.8, 85.7, 89.7, 92.4, 99])
    green, red, screen = (45.5, 49.3, 52.0) if not second else (85.7, 89.7, 92.4)
    if L in (43.4, 83.8):
        baaz(cr, W / 2, 900, 1.0, dance(t, 0.6), t)
    elif L == green:
        baaz(cr, W / 2, 900, 1.05, dance(t), t)
        for k in range(30):
            rnd = random.Random(k)
            ph = ((t - green) * (0.4 + rnd.random() * .5) + rnd.random()) % 1
            cx = rnd.random() * W; cy = -40 + ph * (H + 80)
            cr.save(); cr.translate(cx, cy); cr.rotate(t * 3 + k); cr.rectangle(-10, -5, 20, 10)
            fill(cr, [C['green'], C['gold'], C['white']][k % 3]); cr.restore()
        stamp(cr, 400, 300, 'GREEN!', 90, C['green'], -0.15, 1, pop(t, green + 0.1) * (1 + .08 * beat_pulse(t)))
        stamp(cr, 1520, 300, 'NAACH!', 90, C['gold'], 0.12, 1, pop(t, green + 0.9) * (1 + .08 * beat_pulse(t)))
    elif L == red:
        lt = t - red
        x = lerp(-200, W + 250, clamp(lt / 2.6))
        # a red chart line chases him
        pts = [(x - 900 + k * 40, 560 + math.sin(k * 0.9 + t * 6) * 40 + k * 8) for k in range(20)]
        stroke_line(cr, pts, 26, C['ink']); stroke_line(cr, pts, 16, C['red'])
        cr.save(); cr.translate(x - 120, pts[-1][1]); cr.move_to(0, -40); cr.line_to(60, 0); cr.line_to(0, 40); fill(cr, C['red'], keep=True); outline(cr, 5); cr.restore()
        baaz(cr, x, 900, 1.0, run(t), t)
        for k in range(4):
            circle(cr, x - 160 - k * 70, 880 - k * 6, 30 - k * 5); fill(cr, (0.8, 0.75, 0.7), 0.5)
        stamp(cr, W / 2 + 380, 230, 'BHAAGO!', 110, (1, 0.3, 0.35), 0.08, 1, pop(t, red + 0.6))
    elif L == screen or (second and t >= screen):
        lt = t - screen
        hits = sum(1 for b in BEATS if screen + 0.2 < b <= t)
        crack = clamp(hits / 6)
        def content(c):
            for i in range(10):
                yy = 330 + i * 26 + (i * i) * 3
                candle(c, 760 + i * 44, yy, yy + 50, yy - 15, yy + 65, 26, False)
        monitor(cr, 1000, 450, 640, 400, 1, content, crack)
        ph = beat_phase(t)
        fist = 1 - ph
        pose = dict(lA=(-150 + 120 * fist, -20), rA=(150 - 120 * fist, 20), eyes='open', brows='angry', mouth='shout', look=(1, -1), lean=6 * fist)
        baaz(cr, 560, 920, 1.0, pose, t)
        for side in (-1, 1):  # steam from ears
            for k in range(3):
                pp = ((t * 1.5) + k / 3) % 1
                circle(cr, 560 + side * (110 + pp * 60), 920 - 505 - pp * 120, 18 + pp * 22); fill(cr, C['white'], 0.6 * (1 - pp))
        if crack > 0.2:
            stamp(cr, 1400, 160, 'GUSSA!', 80, (1, 0.3, 0.35), 0.1, 1, pop(t, screen + 1.0))
    elif L == 57.7:
        press = 1.0 if beat_phase(t) < 0.25 else 0
        pose = dict(rA=(-110 + 30 * press, 0), lA=(-20, 0), eyes='closed', mouth='grin', lean=-5)
        baaz(cr, 620, 900, 1.0, pose, t)
        button(cr, 1250, 540, 460, 190, 'BUY', C['green2'], press)
        text(cr, 'Soch? Kya soch?', 1250, 800, 'anton', 56, C['white'], pop(t, 58.3))
    elif L == 59.8:
        tremble = math.sin(t * 60) * 4
        pose = dict(rA=(-110, 0), lA=(-40, -60), eyes='shock', mouth='wavy', brows='sad', sweat=1, lean=tremble)
        baaz(cr, 620 + tremble, 900, 1.0, pose, t)
        press = 1.0 if beat_phase(t) < 0.25 else 0
        button(cr, 1250, 540, 460, 190, 'SELL', C['red'], press)
        for k in range(3):
            text(cr, '!', 520 + k * 60, 260 - k * 20, 'bungee', 90, C['gold'], pop(t, 60 + k * 0.2), stroke=8)
    elif L == 61.5:
        # sitting on a box, crying, rain cloud
        cr.rectangle(W / 2 - 150, 810, 300, 150); fill(cr, (0.45, 0.3, 0.15), keep=True); outline(cr, 6)
        text(cr, 'PORTFOLIO', W / 2, 885, 'bungee', 34, C['ink'])
        pose = dict(lA=(-30, 60), rA=(30, -60), lL=(-80, 80), rL=(80, -80), eyes='cry', mouth='shout', brows='sad', tears=1)
        baaz(cr, W / 2, 900, 1.0, pose, t)
        cr.save(); cr.translate(W / 2, 180)
        for (cx, cy, r) in [(-140, 0, 80), (-40, -40, 100), (80, -20, 90), (160, 20, 70), (0, 30, 90)]:
            circle(cr, cx, cy, r); fill(cr, (0.35, 0.38, 0.45))
        cr.restore()
        for k in range(40):
            rnd = random.Random(k)
            ph = (t * 1.6 + rnd.random()) % 1
            x = W / 2 - 200 + rnd.random() * 400; y = 230 + ph * 600
            stroke_line(cr, [(x, y), (x - 6, y + 30)], 5, (0.55, 0.75, 1), 0.7)
    else:
        baaz(cr, W / 2, 900, 1.0, dance(t, 0.6), t)


def scene_verse2(cr, t):
    lt = t - 69.5
    bg_grad(cr, (0.06, 0.07, 0.1), (0.02, 0.02, 0.03))
    grid(cr, t, C['grey'], 0.06)
    flip = 0
    if 73.9 <= t < 76.5:
        hits = sum(1 for b in BEATS if 73.9 <= b <= t)
        flip = math.pi * hits + math.pi * (ease_out(beat_phase(t)) if hits else 0)
        flip = math.pi * (hits % 2) if beat_phase(t) > 0.3 else math.pi * ((hits - 1) % 2) + math.pi * ease_out(beat_phase(t) / 0.3)
    cr.save(); cr.translate(W / 2, H / 2); cr.rotate(flip); cr.translate(-W / 2, -H / 2)
    if t < 76.5:
        # zig-zag chart: panic sell at the bottom, buy at the top
        def yv(x): return 430 + 200 * math.sin(x / 260 - 0.6) + 40 * math.sin(x / 70)
        reveal = clamp(lt / 6.5)
        xs = list(range(120, 1820, 20))
        nmax = max(2, int(len(xs) * reveal))
        pts = [(x, yv(x)) for x in xs[:nmax]]
        stroke_line(cr, pts, 20, C['ink']); stroke_line(cr, pts, 11, C['white'])
        marks = [(560, 'SELL', C['red'], 'sasta becha', 69.7), (1050, 'BUY', C['green2'], 'mehnga khareeda', 71.8), (1450, 'SELL', C['red'], 'phir sasta', 73.0)]
        for (mx, lab, col, sub, mt) in marks:
            p = pop(t, mt)
            if p <= 0: continue
            my = yv(mx)
            circle(cr, mx, my, 22 * p); fill(cr, col, keep=True); outline(cr, 5)
            cr.save(); cr.translate(mx, my + (110 if lab == 'SELL' else -120)); cr.scale(p, p)
            rrect(cr, -95, -40, 190, 80, 16); fill(cr, col, keep=True); outline(cr, 5)
            text(cr, lab, 0, 0, 'bungee', 42, C['white'])
            text(cr, sub, 0, 70 if lab == 'SELL' else -70, 'anton', 34, C['gold2'])
            cr.restore()
        # little baaz rides the line
        hx = pts[-1][0]; hy = pts[-1][1]
        pose = run(t, 12) if t < 73.9 else dict(eyes='dizzy', mouth='wavy', lA=(-150, 0), rA=(150, 0))
        baaz(cr, hx, hy, 0.38, pose, t)
    elif t < 79.0:
        # portfolio card turning red
        p = pop(t, 76.5, 0.4)
        cr.save(); cr.translate(W / 2 + 200, 450); cr.scale(p, p)
        rrect(cr, -420, -260, 840, 520, 36); fill(cr, (0.08, 0.09, 0.11), keep=True); outline(cr, 8, C['red'])
        text(cr, 'MERA PORTFOLIO', -360, -190, 'bungee', 40, C['grey'], 1, 'l')
        pct = -68.4 * ease_out(clamp((t - 76.7) / 1.6))
        text(cr, f"{pct:.1f}%", 0, -40, 'anton', 190, C['red'], 1)
        val = 1000000 * (1 + pct / 100)
        text(cr, f"Rs {val:,.0f}", 0, 120, 'mono', 54, C['white'], 1)
        for i in range(6):
            yy = 180 + i * 10
            candle(cr, -300 + i * 120, 170 + i * 6, 200 + i * 8, 160 + i * 6, 210 + i * 8, 40, False)
        cr.restore()
        pose = dict(eyes='shock', mouth='o', brows='sad', lA=(-30, -90), rA=(30, 90), sweat=1)
        baaz(cr, 380, 920, 0.9, pose, t)
    else:
        # Abba facepalm + "market rigged hai Abba!"
        pose_a = dict(rA=(-170, -10), lA=(-20, 0), palm=True, eyes='closed', mouth='frown', brows='angry', head_tilt=-8, lL=(-6, 0), rL=(6, 0))
        enter = ease_out(clamp((t - 79.0) / 0.5))
        abba(cr, lerp(2200, 1350, enter), 940, 1.0, pose_a, t)
        if t > 79.4:
            text(cr, 'UFF!', 1600, 250, 'bungee', 90, C['gold'], pop(t, 79.4), stroke=10)
        pose_b = dict(lA=(-140, -20), rA=(-30, 40), eyes='open', brows='raised', mouth='shout', look=(1, 0))
        baaz(cr, 560, 940, 1.0, pose_b, t)
        if t > 80.8:
            reps = 1 + sum(1 for x in (81.9, 82.8) if t > x)
            for r in range(reps):
                cr.save(); cr.translate(560 + r * 40, 230 + r * 150)
                sc = pop(t, 80.8 + [0, 1.1, 2.0][r]) * (1 - r * 0.15)
                cr.scale(sc, sc); cr.rotate(-0.05 + r * 0.06)
                bubble(cr, 0, 0, 640, 130, (1, 1))
                text(cr, 'MARKET RIGGED HAI ABBA!', 0, 0, 'anton', 56, C['red2'], 1)
                cr.restore()
    cr.restore()


def scene_bridge(cr, t):
    lt = t - 99.2
    bg_grad(cr, (0.02, 0.12, 0.1), (0.01, 0.05, 0.04))
    particles(cr, t, 40, C['green'], 0.25, seed=9, size=4)
    # soft rings breathe with the beat
    for k in range(4):
        r = 200 + k * 160 + (lt * 40) % 160
        circle(cr, W / 2, H / 2, r); outline(cr, 2, C['green'], 0.08)
    L = line_at(t, [99.2, 100.9, 102.5, 104.6, 106.1, 109.8])
    if L == 99.2:
        # Abba calms him down
        pose_b = dict(eyes='cry', mouth='frown', brows='sad', tears=0.4, lA=(-10, 10), rA=(10, -10))
        baaz(cr, 820, 920, 1.0, pose_b, t)
        pose_a = dict(lA=(-80, -60), rA=(20, -10), eyes='open', mouth='smile', look=(-1, 0), brows='up')
        abba(cr, 1180, 920, 1.0, pose_a, t)
        text(cr, 'BAS KAR YAAR', W / 2, 220, 'bungee', 90, C['white'], pop(t, 99.4), stroke=10)
    elif L == 100.9:
        # tips crossed out
        for i, (m, ang) in enumerate([("10x pakka!", -0.1), ("Andar ki khabar", 0.08), ("Sab laga do!", -0.05)]):
            cr.save(); cr.translate(500 + i * 460, 420 + (i % 2) * 120); cr.rotate(ang); cr.scale(pop(t, 101.0 + i * 0.15), pop(t, 101.0 + i * 0.15))
            bubble(cr, 0, 0, 400, 110, (-1, 1), (0.85, 0.95, 0.88))
            text(cr, m, 0, 0, 'anton', 50, C['ink'])
            cr.restore()
        p = ease_out(clamp((t - 101.6) / 0.4))
        if p > 0:
            stamp(cr, W / 2, 470, 'NO TUKKA', 130, C['red'], -0.1, 1, back_out(p))
    elif L == 102.5:
        # research: magnifier over a company report + checklist
        rrect(cr, 260, 200, 700, 620, 24); fill(cr, (0.95, 0.97, 0.95), keep=True); outline(cr, 6)
        text(cr, 'COMPANY REPORT', 610, 260, 'bungee', 40, C['forest'])
        for i in range(6):
            stroke_line(cr, [(320, 330 + i * 36), (320 + 300 + (i * 70) % 260, 330 + i * 36)], 12, (0.75, 0.8, 0.78))
        for i in range(6):
            hh = 60 + i * 28
            cr.rectangle(330 + i * 90, 780 - hh, 60, hh); fill(cr, C['green2'])
        ang = t * 1.5
        magnifier(cr, 610 + math.cos(ang) * 160, 480 + math.sin(ang) * 120, 1.0)
        items = [('Earnings', 102.8), ('Debt', 103.3), ('Valuation', 103.8), ('Risk', 104.2)]
        for i, (lab, it) in enumerate(items):
            a = clamp((t - it) / 0.2)
            rrect(cr, 1110, 250 + i * 140, 90, 90, 14); fill(cr, (0.04, 0.2, 0.12), a, keep=True); outline(cr, 5, C['green'], a)
            tick(cr, 1155, 295 + i * 140, 70, C['green'], a, clamp((t - it) / 0.35))
            text(cr, lab, 1240, 295 + i * 140, 'anton', 64, C['white'], a, 'l')
    elif L == 104.6:
        # calendar flip AAJ -> KAL, sunrise
        sun = ease_out(clamp((t - 104.6) / 1.4))
        circle(cr, W / 2, 900 - sun * 300, 220); fill(cr, C['gold'], 0.35 * sun)
        flipp = clamp((t - 105.2) / 0.4)
        cr.save(); cr.translate(W / 2, 460)
        rrect(cr, -260, -260, 520, 520, 30); fill(cr, C['white'], keep=True); outline(cr, 8)
        cr.rectangle(-260, -260, 520, 120); fill(cr, C['red'])
        for x_ in (-150, 150): rrect(cr, x_ - 15, -300, 30, 80, 12); fill(cr, (0.3, 0.3, 0.3))
        sy = math.cos(flipp * math.pi)
        cr.save(); cr.scale(1, max(0.02, abs(sy)))
        text(cr, 'AAJ' if flipp < 0.5 else 'KAL', 0, 60, 'bungee', 170, C['ink'] if flipp < 0.5 else C['green2'])
        cr.restore()
        cr.restore()
    elif L == 106.1:
        # no magic, no luck
        p1, p2 = pop(t, 106.2), pop(t, 107.6)
        cr.save(); cr.translate(650, 470); cr.scale(p1, p1); cr.rotate(-0.4)
        stroke_line(cr, [(0, 200), (0, -150)], 30, C['ink']); stroke_line(cr, [(0, 200), (0, -150)], 20, (0.2, 0.2, 0.25))
        stroke_line(cr, [(0, -150), (0, -200)], 20, C['white'])
        cr.restore()
        burst(cr, 560, 270, 60, 26, 5, C['gold'], t, p1)
        text(cr, 'JAADU', 650, 760, 'bungee', 70, C['white'], p1)
        if p1 > 0.9: cross(cr, 650, 470, 340 * pop(t, 106.9), 1)
        cr.save(); cr.translate(1270, 470); cr.scale(p2, p2); cr.rotate(t * 2)
        rrect(cr, -110, -110, 220, 220, 30); fill(cr, C['white'], keep=True); outline(cr, 8)
        for (dx, dy) in [(-55, -55), (55, 55), (0, 0), (55, -55), (-55, 55)]: circle(cr, dx, dy, 20); fill(cr, C['ink'])
        cr.restore()
        text(cr, 'KISMAT', 1270, 760, 'bungee', 70, C['white'], p2)
        if p2 > 0.9: cross(cr, 1270, 470, 340 * pop(t, 108.3), 1)
    elif L == 109.8:
        # strategy roadmap
        steps = ['RESEARCH', 'PLAN', 'INVEST', 'HOLD']
        for i, s in enumerate(steps):
            st = 110.0 + i * 0.75
            p = pop(t, st)
            x = 330 + i * 420; y = 640 - i * 110
            if i:
                q = clamp((t - st + 0.4) / 0.4)
                px, py = 330 + (i - 1) * 420, 640 - (i - 1) * 110
                stroke_line(cr, [(px + 150, py), (lerp(px + 150, x - 150, q), lerp(py, y, q))], 10, C['green'], 0.9)
            cr.save(); cr.translate(x, y); cr.scale(p, p)
            para(cr, -160, -60, 320, 120, slant=0.3, r=14); fill(cr, C['green2'] if i < 3 else C['gold'], keep=True); outline(cr, 6)
            text(cr, s, 0, 0, 'bungee', 44, C['white'], 1, stroke=6)
            text(cr, str(i + 1), -120, -90, 'anton', 50, C['green'])
            cr.restore()
        text(cr, 'STRATEGY SE NIKLE HAL', W / 2, 200, 'bungee', 72, C['white'], pop(t, 112.5), stroke=8)


def uptrend_y(x, t):
    return 820 - (x - 100) * 0.33 + 25 * math.sin(x / 90)


def scene_final(cr, t):
    lt = t - 114.0
    bg_grad(cr, (0.02, 0.2, 0.05), (0.0, 0.06, 0.02))
    for k in range(12):
        ang = k * TAU / 12 + t * 0.15
        cr.move_to(W / 2, H + 100); cr.line_to(W / 2 + math.cos(ang) * 2600, H + 100 + math.sin(ang) * 2600)
        cr.line_to(W / 2 + math.cos(ang + 0.13) * 2600, H + 100 + math.sin(ang + 0.13) * 2600); cr.close_path(); fill(cr, C['green'], 0.06)
    grid(cr, t, C['green'], 0.07, speed=40)
    particles(cr, t, 30, C['gold2'], 0.5, seed=12, size=5)
    eq_bars(cr, t, H - 60, 150, 0.6)
    L = line_at(t, [114.0, 120.7, 122.6, 124.4, 126.4, 130.2, 132.0])
    # steady uptrend line drawn across the screen; Baaz walks calmly up it
    reveal = clamp(lt / 6)
    xs = list(range(100, 1820, 20))
    n = max(2, int(len(xs) * reveal))
    pts = [(x, uptrend_y(x, t)) for x in xs[:n]]
    stroke_line(cr, pts, 22, C['ink'], 0.8); stroke_line(cr, pts, 12, C['green'])
    if L in (114.0, 126.4, 132.0) or L is None:
        walk = clamp(lt / 6)
        bx = lerp(200, 1600, walk) if L == 114.0 else 1200 + 200 * math.sin(t)
        by = uptrend_y(bx, t)
        ph = t * 5
        pose = dict(lL=(-20 * math.sin(ph), 10), rL=(20 * math.sin(ph), 10), lA=(15 * math.sin(ph), -10), rA=(-15 * math.sin(ph), 10),
                    eyes='happy', mouth='smile', bob=6 * abs(math.cos(ph)))
        if L in (126.4, 132.0): pose = dance(t, 0.8)
        baaz(cr, bx, by, 0.55, pose, t)
    elif L == 120.7:
        # think, then calm buy
        pose = dict(rA=(-160, -30), lA=(-20, 0), eyes='open', look=(0.5, -1), mouth='flat', brows='raised')
        baaz(cr, 640, 920, 1.0, pose, t)
        p = pop(t, 120.9)
        cr.save(); cr.translate(820, 230); cr.scale(p, p)
        circle(cr, 0, 0, 70); fill(cr, C['gold2'], keep=True); outline(cr, 6)
        cr.rectangle(-30, 60, 60, 40); fill(cr, C['grey'], keep=True); outline(cr, 5)
        for k in range(8):
            ang = k * TAU / 8 + t
            stroke_line(cr, [(math.cos(ang) * 95, math.sin(ang) * 95), (math.cos(ang) * 130, math.sin(ang) * 130)], 8, C['gold2'], 0.8 + 0.2 * beat_pulse(t))
        cr.restore()
        press = 1 if 121.9 < t < 122.1 else 0
        button(cr, 1350, 520, 420, 170, 'BUY', C['green2'], press, pop(t, 121.4))
        tick(cr, 1600, 380, 140, C['gold'], 1, clamp((t - 121.9) / 0.4))
    elif L == 122.6:
        # plan + hold: clipboard and months flying by
        rrect(cr, 300, 210, 520, 640, 24); fill(cr, (0.96, 0.95, 0.9), keep=True); outline(cr, 6)
        rrect(cr, 470, 180, 180, 60, 14); fill(cr, (0.5, 0.5, 0.5), keep=True); outline(cr, 5)
        text(cr, 'MERA PLAN', 560, 300, 'bungee', 48, C['forest'])
        for i, it in enumerate(['Goal: 5 saal', 'SIP har mahina', 'Diversify', 'Stop loss: ON']):
            a = clamp((t - 122.8 - i * 0.25) / 0.2)
            tick(cr, 370, 400 + i * 100, 50, C['green2'], a, clamp((t - 122.8 - i * 0.25) / 0.3))
            text(cr, it, 420, 400 + i * 100, 'anton', 50, C['ink'], a, 'l')
        months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
        mi = int((t - 122.6) * 5) % 12
        text(cr, 'HOLD', 1350, 330, 'bungee', 150, C['gold'], 1, stroke=12)
        text(cr, months[mi] + f"  {2026 + int((t - 122.6) * 5) // 12}", 1350, 520, 'mono', 70, C['white'])
        pose = dict(lA=(-30, 20), rA=(30, -20), eyes='happy', mouth='smile')
        baaz(cr, 1350, 940, 0.55, pose, t)
    elif L == 124.4:
        # Abba proud, portfolio green
        p = pop(t, 124.5, 0.4)
        cr.save(); cr.translate(W / 2, 330); cr.scale(p, p)
        rrect(cr, -380, -150, 760, 300, 30); fill(cr, (0.04, 0.12, 0.06), keep=True); outline(cr, 8, C['green'])
        pct = 42.7 * ease_out(clamp((t - 124.6) / 1.6))
        text(cr, f"+{pct:.1f}%", 0, -20, 'anton', 150, C['green'])
        text(cr, 'SABAR KA PHAL', 0, 100, 'bungee', 40, C['gold'])
        cr.restore()
        baaz(cr, 700, 960, 0.85, dict(lA=(-150, -20), rA=(60, -40), eyes='happy', mouth='grin', blush=0.8), t)
        abba(cr, 1220, 960, 0.85, dict(lA=(-60, -60), rA=(150, -30), eyes='happy', mouth='grin', blush=0.6), t)
        for k in range(14):
            ph = ((t - 124.4) * 0.7 + k / 14) % 1
            coin(cr, 200 + (k * 137) % 1500, -60 + ph * 1100, 30, t * 5 + k)
    elif L == 130.2:
        # compass: no tension, only direction
        cr.save(); cr.translate(W / 2, 470)
        circle(cr, 0, 0, 300); fill(cr, (0.95, 0.95, 0.9), keep=True); outline(cr, 12)
        circle(cr, 0, 0, 260); outline(cr, 4, C['grey'])
        for k, lab in enumerate(['N', 'E', 'S', 'W']):
            ang = k * TAU / 4 - TAU / 4
            text(cr, lab, math.cos(ang) * 210, math.sin(ang) * 210, 'bungee', 50, C['ink'])
        settle = ease_out(clamp((t - 130.2) / 1.2))
        needle = (1 - settle) * math.sin(t * 14) * 1.6 + 0.6 * (1 - settle) - TAU / 8 * settle
        cr.rotate(needle)
        cr.move_to(0, -230); cr.line_to(34, 0); cr.line_to(-34, 0); cr.close_path(); fill(cr, C['green'], keep=True); outline(cr, 5)
        cr.move_to(0, 230); cr.line_to(34, 0); cr.line_to(-34, 0); cr.close_path(); fill(cr, C['grey'], keep=True); outline(cr, 5)
        circle(cr, 0, 0, 22); fill(cr, C['ink'])
        cr.restore()
        text(cr, 'NO TENSION', 360, 470, 'bungee', 66, C['white'], pop(t, 130.4), stroke=8)
        text(cr, 'SIRF DIRECTION', 1560, 470, 'bungee', 66, C['green'], pop(t, 131.0), stroke=8)
    # baaz & abba dance together in the last stretch
    if t >= 136:
        d = dance(t, 1.0)
        baaz(cr, 700, 940, 0.85, d, t)
        d2 = dance(t + 0.24, 0.7); d2['brows'] = 'up'
        abba(cr, 1220, 940, 0.85, d2, t)


def scene_outro(cr, t):
    lt = t - 143.1
    bg_grad(cr, (0.97, 0.96, 0.9), (0.85, 0.93, 0.8), 0.5)
    grid(cr, t, C['green'], 0.05)
    a2 = clamp((t - 148.5) / 0.5)
    if a2 > 0:
        text(cr, 'Invest smart. No dramay baazi.', W / 2, 860, 'interb', 64, C['white'] if STYLE.get('dark') else TXT, a2)
        bp = 1 + 0.05 * beat_pulse(t) * env('bass', t)
        cr.save(); cr.translate(W / 2, 960); cr.scale(bp, bp)
        para(cr, -330, -40, 660, 80, slant=0.3, r=12); fill(cr, C['green2'], a2)
        text(cr, 'www.flostocks.com', 0, 0, 'brand', 40, C['white'], a2)
        cr.restore()
    eq_bars(cr, t, H, 90 * clamp((t - 150) / 2), 0.5)
    # cameo: baaz waves from the corner
    if t > 149:
        p = ease_out(clamp((t - 149) / 0.6))
        wave = math.sin(t * 8) * 25
        baaz(cr, lerp(-200, 220, p), 1100, 0.6, dict(rA=(-160 + wave, -20), lA=(-14, 8), eyes='happy', mouth='grin'), t)
        abba(cr, lerp(W + 200, W - 220, p), 1100, 0.6, dict(lA=(160 + wave, 20), rA=(14, -8), eyes='happy', mouth='smile'), t)


SCENE_FN = {'intro': scene_intro, 'verse1': scene_verse1, 'dream': scene_dream, 'crash': scene_crash, 'chorus': scene_chorus,
            'verse2': scene_verse2, 'bridge': scene_bridge, 'final': scene_final, 'outro': scene_outro}


def render_scene(cr, t):
    name = section(t)[1]
    zoom = 1 + 0.018 * beat_pulse(t) * clamp(env('bass', t) * 1.5)
    sx, sy = shake(t, 34.8, 0.8, 34)
    for c in CHANTS:
        if name != 'bridge':
            dx, dy = shake(t, c[0], 0.25, 12); sx += dx; sy += dy
    cr.save()
    cr.translate(W / 2 + sx, H / 2 + sy); cr.scale(zoom, zoom); cr.translate(-W / 2, -H / 2)
    SCENE_FN[name](cr, t)
    cr.restore()
    flash(cr, t, 34.8, 0.3, (1, 0.2, 0.25))
    for c in CHANTS:
        if c[2] == NO: flash(cr, t, c[0], 0.15, C['white'])
    chant_overlay(cr, t)
    wipes(cr, t)
    if STYLE.get('truck_border'):
        _truck_border(cr, t)
    if STYLE.get('panel'):
        m = 22
        cr.new_path(); cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        cr.rectangle(0, 0, W, H); cr.rectangle(m, m, W - 2 * m, H - 2 * m)
        rgb(cr, (0.99, 0.97, 0.9)); cr.fill(); cr.set_fill_rule(cairo.FILL_RULE_WINDING)
        cr.rectangle(m, m, W - 2 * m, H - 2 * m); cr.set_line_width(10); rgb(cr, (0, 0, 0)); cr.stroke()


def _truck_border(cr, t):
    """Pakistani truck-art frame: red band, chamak-patti triangles, mirror dots, corner flowers."""
    m = 30
    cr.new_path(); cr.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    cr.rectangle(0, 0, W, H); cr.rectangle(m, m, W - 2 * m, H - 2 * m)
    rgb(cr, (0.8, 0.04, 0.2)); cr.fill(); cr.set_fill_rule(cairo.FILL_RULE_WINDING)
    cols = [(1, 0.85, 0.1), (0.1, 0.65, 0.95), (0.2, 0.75, 0.25), (1, 1, 1)]
    k = 0
    for x in range(m, W - m, 36):   # bunting triangles hanging from top and up from bottom
        for yb, d in ((m, 1), (H - m, -1)):
            cr.move_to(x, yb); cr.line_to(x + 36, yb); cr.line_to(x + 18, yb + d * 30); cr.close_path()
            rgb(cr, cols[k % 4]); cr.fill()
        k += 1
    for y in range(m, H - m, 36):
        for xb, d in ((m, 1), (W - m, -1)):
            cr.move_to(xb, y); cr.line_to(xb, y + 36); cr.line_to(xb + d * 30, y + 18); cr.close_path()
            rgb(cr, cols[k % 4]); cr.fill()
        k += 1
    for x in range(20, W, 60):
        for yy in (15, H - 15):
            circle(cr, x, yy, 7); rgb(cr, (0.85, 0.9, 1.0)); cr.fill()
    for (cx, cy) in ((m + 10, m + 10), (W - m - 10, m + 10), (m + 10, H - m - 10), (W - m - 10, H - m - 10)):
        for j in range(8):
            ang = j * TAU / 8 + t
            cr.save(); cr.translate(cx + math.cos(ang) * 26, cy + math.sin(ang) * 26); cr.scale(16, 10); cr.rotate(0); circle(cr, 0, 0, 1); cr.restore()
            rgb(cr, (1, 0.5, 0.75)); cr.fill()
        circle(cr, cx, cy, 16); rgb(cr, (1, 0.85, 0.1)); cr.fill()


def render_brand(cr, t):
    """Official logo artwork, composited last with no texture so it stays exactly on-brand."""
    for tb in WIPES:
        d = t - tb
        if abs(d) < 0.2 and tb < 143:
            brand_img(cr, 'icon', W / 2, H / 2, 300 * (1 + 0.5 * (0.2 - abs(d))), 1.0, dark=False)
    if section(t)[1] == 'outro':
        p = ease_out(clamp((t - 143.4) / 0.7))
        if p > 0.001:
            brand_img(cr, 'logo', W / 2, 470, 1150 * (0.9 + 0.1 * p), p)
    elif not any(abs(t - w) < 0.3 for w in WIPES):
        brand_bug(cr, t, 0.95 * clamp((t - 2) / 1))


def render_ui(cr, t):
    if section(t)[1] == 'outro' or any(abs(t - w) < 0.3 for w in WIPES): return
    index_widget(cr, t, clamp((t - 2) / 1))
    ticker_tape(cr, t)
    caption(cr, t)


def fade(t):
    return clamp(t / 0.4) * clamp((DUR - t) / 1.2)
