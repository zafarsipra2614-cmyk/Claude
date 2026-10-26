"""Non-illustrated concepts for Dramay Baaz: the story told with type, screens, broadcast graphics, 3D and audio
visualisation instead of drawn characters. Each concept is draw(cr, t) over the full song timeline."""
from lib import *
import numpy as np
from scenes import LYRICS, LYR_END, CHANTS, DB, NO, section, mood_sign, market_mood, idx_value, idx_ref, chant_at

SPEC = np.load('audio/spec64.npy').astype(np.float32)

CRISP = dict(no_wipes=True, fill_a=1.0, hatch_mode='none', passes=1, wob=0.0, line=1.0, wash_mix=0.0, wash_a=1.0, pastel=0.0, sat=1.0,
             fonts=dict(bungee='Bungee', anton='Anton', inter='Inter', interb='Inter', mono='JetBrains Mono'))

KEY = {16.2: 'INDEX', 18.1: 'BUY!', 20.4: 'UPPER LOCK', 23.0: 'TIP', 25.5: 'AKHBAAR', 27.3: 'ALL IN', 31.1: 'RAJA',
       32.9: 'GAADI BANGLA', 34.8: 'LOWER LOCK', 36.6: 'STOP LOSS?', 45.5: 'NAACH!', 49.3: 'BHAAGO!', 52.0: 'GUSSA!',
       57.7: 'BUY', 59.8: 'SELL', 61.5: 'RONA', 69.5: 'PANIC', 71.6: 'BUY AGAIN', 73.9: 'ULTA', 76.5: '-59.8%',
       79.0: 'UFF', 80.8: 'RIGGED?', 85.7: 'NAACH!', 89.7: 'BHAAGO!', 92.4: 'GUSSA!', 99.2: 'BAS KAR', 100.9: 'NO TUKKA',
       102.5: 'RESEARCH', 104.6: 'AAJ SE', 106.1: 'NO JAADU', 109.8: 'STRATEGY', 120.7: 'SOCH', 122.6: 'HOLD',
       124.4: 'SABAR', 130.2: 'DIRECTION'}
HEADLINE = {16.2: 'LOCAL MAN OPENS KSE-100 BEFORE BRUSHING TEETH', 18.1: 'MAN SHOUTS "BUY!" BEFORE MORNING CHAI',
            20.4: 'NEIGHBOURS CONFIRM: HE IS SCREAMING "UPPER LOCK"', 23.0: "EXCLUSIVE: COUSIN'S FRIEND HAS A TIP",
            25.5: 'NEWSPAPER SAYS MARKET MEIN TEZI', 27.3: 'ENTIRE SAVINGS GO ALL-IN', 31.1: 'MAN ANNOUNCES PLAN TO BECOME KING',
            32.9: 'CAR, BUNGALOW ALREADY BOOKED IN HIS HEAD', 34.8: 'LOWER LOCK HITS. DREAMS SUSPENDED',
            36.6: 'STOP LOSS REPORTED MISSING', 45.5: 'GREEN CANDLE SPOTTED, DANCING REPORTED', 49.3: 'RED CANDLE: MAN FLEES SCENE',
            52.0: 'SCREEN ATTACKED IN FIT OF ANGER', 57.7: 'BUY ORDER PLACED WITHOUT THINKING', 59.8: 'SELL ORDER PLACED IN FEAR',
            61.5: 'MAN SITS DOWN, CRIES', 69.5: 'DIP TRIGGERS PANIC SELLING', 71.6: 'RALLY TRIGGERS PANIC BUYING',
            73.9: 'EXPERTS: HE IS DOING IT BACKWARDS', 76.5: 'PORTFOLIO TURNS COMPLETELY RED', 79.0: 'ABBA HOLDS HEAD',
            80.8: 'SON BLAMES "RIGGED MARKET"', 85.7: 'GREEN AGAIN, DANCING RESUMES', 89.7: 'RED AGAIN, RUNNING RESUMES',
            92.4: 'SECOND SCREEN ATTACKED', 99.2: 'ABBA: "BAS KAR YAAR"', 100.9: 'TIPS AND GUESSWORK BANNED',
            102.5: 'NEW RULE: RESEARCH FIRST, INVEST LATER', 104.6: 'CHANGE STARTS TODAY', 106.1: 'NO MAGIC, NO LUCK, SOURCES SAY',
            109.8: 'STRATEGY FOUND', 120.7: 'TRADE MADE AFTER ACTUAL THINKING', 122.6: 'PLAN MADE, POSITION HELD',
            124.4: 'PATIENCE PAYS OFF', 130.2: 'NO TENSION, ONLY DIRECTION'}


def cur_line(t):
    cur = None
    for l in LYRICS:
        if l[0] - 0.1 <= t < LYR_END[l[0]]: cur = l
    return cur


def last_line(t):
    cur = LYRICS[0]
    for l in LYRICS:
        if t >= l[0] - 0.1: cur = l
    return cur


def word_times(t0, words):
    span = max(0.6, (LYR_END[t0] - t0) * 0.6)
    return [t0 + span * i / max(1, len(words)) for i in range(len(words))]


def mood_col(t):
    m = mood_sign(t) if section(t)[1] == 'chorus' else market_mood(t)
    return C['green'] if m >= 0 else C['red'], m


def word_col(w_, default):
    u = w_.upper()
    if any(k in u for k in ('BUY', 'GREEN', 'UPPER', 'RAJA', 'SABAR', 'HOLD', 'RESEARCH', 'STRATEGY', 'DIRECTION')): return C['green']
    if any(k in u for k in ('RED', 'LOWER', 'SELL', 'RIGGED', 'PANIC', 'GUSSA', 'RO')): return (1, 0.25, 0.3)
    return default


def mini_caption(cr, t, y=H - 120, col=C['white'], sub=(0.7, 0.75, 0.75), size=54):
    l = cur_line(t)
    if not l: return
    t0, ro, en = l; t1 = LYR_END[t0]
    a = clamp((t - t0 + 0.1) / 0.15) * clamp((t1 - t) / 0.25)
    text(cr, ro, W / 2, y, 'anton', size, col, a, stroke=0)
    text(cr, en, W / 2, y + size * 0.75, 'inter', 26, sub, a * 0.9)


def chant_text(t):
    c = chant_at(t)
    return (c, t - c[0]) if c else (None, 0)


# =================================================================== A: kinetic typography
def kinetic(cr, t):
    col, m = mood_col(t)
    bp = beat_pulse(t)
    base = (0.035, 0.04, 0.05)
    tint = mix(base, col, 0.18 + 0.12 * bp * env('bass', t))
    cr.rectangle(0, 0, W, H); rgb(cr, tint); cr.fill()
    # slow brand-shaped stripes
    for k in range(-3, 9):
        x = (k * 300 + t * 60) % (W + 900) - 450
        para(cr, x, -60, 120, H + 120, slant=0.32, r=0); rgb(cr, col, 0.05); cr.fill()
    c, lt = chant_text(t)
    if c:
        phrase = 'DRAMAY BAAZ!' if c[2] == DB else 'AB NO DRAMAY BAAZI!'
        for r in range(-3, 4):   # marquee rows sliding opposite ways
            off = (lt * 900 * (1 if r % 2 else -1)) % 1600
            y = H / 2 + r * 175
            for k in range(-2, 4):
                text(cr, phrase, k * 1600 - off + 600, y, 'bungee', 130, C['white'] if r != 0 else C['gold'], 0.12 if r else 1.0,
                     stroke=0 if r else 10, sc=C['ink'])
        s = 1 + 0.07 * beat_pulse(t, 9)
        cr.save(); cr.translate(W / 2, H / 2); cr.scale(s, s)
        text(cr, phrase, 0, 0, 'bungee', 150 if c[2] == DB else 110, C['gold'], 1, stroke=14)
        cr.restore()
        return
    l = cur_line(t)
    if not l:
        v = idx_value(t)
        text(cr, 'KSE-100', W / 2, H / 2 - 150, 'mono', 44, (0.6, 0.65, 0.65))
        text(cr, f"{v:,.0f}", W / 2, H / 2 + 20, 'anton', 260, col, 1)
        return
    t0, ro, en = l
    key = KEY.get(t0, '')
    # giant outlined keyword behind
    if key:
        font(cr, 'bungee', 420); cr.save()
        ext = cr.text_extents(key); sc = min(1.0, (W * 1.3) / max(1, ext.x_advance))
        cr.translate(W / 2 - ext.x_advance * sc / 2 - (t - t0) * 40, H / 2 + 150); cr.scale(sc, sc)
        cr.move_to(0, 0); cr.text_path(key); cr.set_line_width(4); rgb(cr, col, 0.25); cr.stroke(); cr.restore()
    words = ro.replace('"', '').split(' ')
    wts = word_times(t0, words)
    # greedy lines of <= 12 chars
    lines, curl = [], []
    for i, w_ in enumerate(words):
        if curl and len(' '.join(words[j] for j in curl + [i])) > 12:
            lines.append(curl); curl = []
        curl.append(i)
    lines.append(curl)
    sizes = []
    for ln in lines:
        s_ = ' '.join(words[i] for i in ln).upper()
        w100 = text_w(cr, s_, 'anton', 100)
        sizes.append(min(300, 100 * 1500 / max(1, w100)))
    total_h = sum(sz * 0.95 for sz in sizes)
    y = H / 2 - total_h / 2 + sizes[0] * 0.45 - 30
    for li, ln in enumerate(lines):
        sz = sizes[li]
        font(cr, 'anton', sz)
        ws = [cr.text_extents(words[i].upper()).x_advance for i in ln]
        gap = sz * 0.22
        x = W / 2 - (sum(ws) + gap * (len(ln) - 1)) / 2
        for k, i in enumerate(ln):
            p = clamp((t - wts[i]) / 0.16)
            if p > 0:
                sc = lerp(1.7, 1.0, ease_out(p)) * (1 + 0.04 * bp)
                rot = (1 - ease_out(p)) * (0.25 if i % 2 else -0.25)
                cr.save(); cr.translate(x + ws[k] / 2, y); cr.rotate(rot); cr.scale(sc, sc)
                wc = word_col(words[i], C['white'])
                text(cr, words[i].upper(), 0, 0, 'anton', sz, wc, p, stroke=0)
                cr.restore()
            x += ws[k] + gap
        y += sz * 0.95
    text(cr, en, W / 2, H - 110, 'inter', 34, (0.75, 0.78, 0.78), clamp((t - t0 - 0.3) / 0.3))


# =================================================================== B: screen-life phone POV
def _bokeh(cr, t, col):
    rnd = random.Random(3)
    for k in range(26):
        x = rnd.random() * W + math.sin(t * 0.3 + k) * 40; y = rnd.random() * H; r = 40 + rnd.random() * 120
        g = cairo.RadialGradient(x, y, 0, x, y, r)
        cc = [col, C['gold'], (0.4, 0.5, 1.0)][k % 3]
        g.add_color_stop_rgba(0, *cc, 0.16); g.add_color_stop_rgba(1, *cc, 0)
        cr.set_source(g); cr.arc(x, y, r, 0, TAU); cr.fill()


def _app_chart(cr, t, x, y, w, h, col):
    vs = [idx_value(max(0.0, t - (59 - k) * 0.12)) + 90 * math.sin(k * 1.9 + t) for k in range(60)]
    lo, hi = min(vs) - 50, max(vs) + 50
    pts = [(x + k * w / 59, y + h - 20 - (v - lo) / (hi - lo) * (h - 40)) for k, v in enumerate(vs)]
    g = cairo.LinearGradient(0, y, 0, y + h); g.add_color_stop_rgba(0, *col, 0.35); g.add_color_stop_rgba(1, *col, 0)
    cr.move_to(*pts[0])
    for p in pts[1:]: cr.line_to(*p)
    cr.line_to(x + w, y + h); cr.line_to(x, y + h); cr.close_path(); cr.set_source(g); cr.fill()
    cr.move_to(*pts[0])
    for p in pts[1:]: cr.line_to(*p)
    cr.set_line_width(5); rgb(cr, col); cr.stroke()
    circle(cr, *pts[-1], 9 + 5 * beat_pulse(t)); rgb(cr, col); cr.fill()


def _notif(cr, x, y, w, app, msg, p, icon_col):
    if p <= 0: return
    cr.save(); cr.translate(0, (1 - ease_out(p)) * -140)
    rrect(cr, x, y, w, 120, 26); rgb(cr, (0.97, 0.97, 0.98), 0.96 * clamp(p * 2)); cr.fill()
    rrect(cr, x + 20, y + 22, 50, 50, 12); rgb(cr, icon_col, clamp(p * 2)); cr.fill()
    text(cr, app, x + 88, y + 38, 'interb', 24, (0.45, 0.45, 0.5), clamp(p * 2), 'l')
    text(cr, msg, x + 88, y + 78, 'inter', 30, (0.08, 0.08, 0.1), clamp(p * 2), 'l')
    cr.restore()


def screenlife(cr, t):
    col, m = mood_col(t)
    cr.rectangle(0, 0, W, H); rgb(cr, (0.05, 0.05, 0.07)); cr.fill()
    _bokeh(cr, t, col)
    # lyric on the left, big
    l = cur_line(t)
    if l:
        t0, ro, en = l
        a = clamp((t - t0 + 0.1) / 0.2) * clamp((LYR_END[t0] - t) / 0.25)
        words = ro.split(' '); y = 360; line = ''; lines = []
        for w_ in words:
            if len(line + ' ' + w_) > 14 and line: lines.append(line); line = w_
            else: line = (line + ' ' + w_).strip()
        lines.append(line)
        for i, ln in enumerate(lines):
            text(cr, ln, 140, y + i * 120, 'anton', 110, word_col(ln, C['white']), a * clamp((t - t0 - i * 0.3) / 0.2), 'l', stroke=0)
        text(cr, en, 140, y + len(lines) * 120 + 10, 'inter', 32, (0.7, 0.72, 0.75), a, 'l')
    # the phone
    px, py, pw, ph = 1270, 540, 520, 1000
    bob = math.sin(t * 1.3) * 8 + beat_pulse(t) * 6 * env('bass', t)
    cr.save(); cr.translate(px, py + bob); cr.rotate(-0.05 + math.sin(t * 0.5) * 0.01)
    rrect(cr, -pw / 2 - 16, -ph / 2 - 16, pw + 32, ph + 32, 70); rgb(cr, (0.12, 0.12, 0.14)); cr.fill()
    rrect(cr, -pw / 2, -ph / 2, pw, ph, 56); rgb(cr, (0.98, 0.98, 0.99)); cr.fill()
    cr.save(); rrect(cr, -pw / 2, -ph / 2, pw, ph, 56); cr.clip(); cr.translate(-pw / 2, -ph / 2)
    _phone_screen(cr, t, pw, ph, col)
    cr.restore()
    rrect(cr, -70, -ph / 2 + 18, 140, 34, 17); rgb(cr, (0.05, 0.05, 0.06)); cr.fill()
    cr.restore()
    c, lt = chant_text(t)
    if c:
        s = back_out(clamp(lt / 0.25)) * (1 + 0.06 * beat_pulse(t, 9))
        cr.save(); cr.translate(W / 2 - 200, H / 2); cr.rotate(-0.08); cr.scale(s, s)
        text(cr, 'DRAMAY BAAZ!' if c[2] == DB else 'AB NO DRAMAY BAAZI!', 0, 0, 'bungee', 120 if c[2] == DB else 86, C['gold'], 1, stroke=14)
        cr.restore()


def _phone_screen(cr, t, w, h, col):
    dark = (0.06, 0.07, 0.09)
    sec = section(t)[1]
    text(cr, '9:31', 50, 50, 'interb', 26, (0.1, 0.1, 0.1), 1, 'l')
    if 79.0 <= t < 84:      # incoming call from Abba
        g = cairo.LinearGradient(0, 0, 0, h); g.add_color_stop_rgb(0, 0.2, 0.25, 0.3); g.add_color_stop_rgb(1, 0.05, 0.06, 0.08)
        cr.rectangle(0, 0, w, h); cr.set_source(g); cr.fill()
        ring = (t * 1.6) % 1
        for k in range(3):
            r = 110 + ((ring + k / 3) % 1) * 140
            circle(cr, w / 2, 330, r); cr.set_line_width(3); rgb(cr, (1, 1, 1), 0.4 * (1 - (ring + k / 3) % 1)); cr.stroke()
        circle(cr, w / 2, 330, 105); rgb(cr, (0.55, 0.6, 0.65)); cr.fill()
        text(cr, 'A', w / 2, 330, 'interb', 110, (1, 1, 1))
        text(cr, 'Abba', w / 2, 500, 'interb', 56, (1, 1, 1))
        text(cr, 'calling...', w / 2, 560, 'inter', 30, (0.8, 0.8, 0.85))
        shake = math.sin(t * 50) * 6 * (int(t * 2) % 2)
        circle(cr, w / 2 - 130 + shake, h - 170, 52); rgb(cr, (0.95, 0.25, 0.3)); cr.fill()
        circle(cr, w / 2 + 130 - shake, h - 170, 52); rgb(cr, (0.2, 0.8, 0.35)); cr.fill()
        text(cr, 'Decline', w / 2 - 130, h - 90, 'inter', 24, (1, 1, 1)); text(cr, 'Accept', w / 2 + 130, h - 90, 'inter', 24, (1, 1, 1))
        _notif(cr, 20, 70, w - 40, 'PORTFOLIO', 'Down -59.8% today', clamp((t - 79.3) / 0.4), C['red'])
        return
    if 23.0 <= t < 25.5:    # WhatsApp tip
        cr.rectangle(0, 0, w, h); rgb(cr, (0.93, 0.9, 0.85)); cr.fill()
        cr.rectangle(0, 0, w, 150); rgb(cr, (0.05, 0.37, 0.33)); cr.fill()
        text(cr, "Cousin ka Dost", 110, 100, 'interb', 32, (1, 1, 1), 1, 'l'); circle(cr, 60, 100, 30); rgb(cr, C['gold']); cr.fill()
        for i, (msg, mt) in enumerate([("Bhai ek tip hai...", 23.2), ("Ye share pakka 10x!", 23.8), ("Andar ki khabar hai", 24.4), ("Sab laga do!!!", 25.0)]):
            p = clamp((t - mt) / 0.2)
            if p <= 0: continue
            bw = text_w(cr, msg, 'inter', 32) + 50
            rrect(cr, 30, 190 + i * 110, bw, 80, 18); rgb(cr, (1, 1, 1), p); cr.fill()
            text(cr, msg, 55, 230 + i * 110, 'inter', 32, (0.1, 0.1, 0.1), p, 'l')
        return
    # trading app
    cr.rectangle(0, 0, w, h); rgb(cr, dark); cr.fill()
    v = idx_value(t); ref = idx_ref(t); ch = (v - ref) / ref * 100
    text(cr, 'KSE-100', 40, 230, 'interb', 30, (0.6, 0.62, 0.66), 1, 'l')
    text(cr, f"{v:,.0f}", 40, 300, 'interb', 72, (1, 1, 1), 1, 'l')
    text(cr, f"{'+' if ch >= 0 else ''}{ch:.2f}%", 40, 360, 'interb', 34, C['green'] if ch >= 0 else C['red'], 1, 'l')
    _app_chart(cr, t, 0, 400, w, 300, C['green'] if ch >= 0 else C['red'])
    press = 1.0 if (18.6 < t < 20.4 and beat_phase(t) < 0.25) else 0
    for i, (lab, cc) in enumerate((('BUY', C['green2']), ('SELL', C['red']))):
        bx = 30 + i * (w / 2 - 15)
        sc = 0.92 if (press and i == 0) or (59.8 <= t < 61.5 and i == 1 and beat_phase(t) < 0.25) else 1
        cr.save(); cr.translate(bx + (w / 2 - 45) / 2, 820); cr.scale(sc, sc)
        rrect(cr, -(w / 2 - 45) / 2, -50, w / 2 - 45, 100, 24); rgb(cr, cc); cr.fill()
        text(cr, lab, 0, 0, 'interb', 44, (1, 1, 1)); cr.restore()
    if 18.9 <= t < 23:
        _notif(cr, 20, 70, w - 40, 'ORDER FILLED', 'Bought 5,000 shares', clamp((t - 18.9) / 0.3), C['green2'])
    if sec == 'chorus' and mood_sign(t) > 0.3:
        _notif(cr, 20, 70, w - 40, 'PRICE ALERT', 'Green! Portfolio +4.2%', clamp((t - 45.6) / 0.3) if t < 80 else clamp((t - 85.8) / 0.3), C['green2'])
    if sec == 'chorus' and mood_sign(t) < -0.3:
        _notif(cr, 20, 70, w - 40, 'PRICE ALERT', 'Red! Portfolio -6.8%', 1, C['red'])


# =================================================================== C: glitch news broadcast
def news(cr, t):
    col, m = mood_col(t)
    g = cairo.LinearGradient(0, 0, W, H); g.add_color_stop_rgb(0, 0.03, 0.06, 0.16); g.add_color_stop_rgb(1, 0.01, 0.02, 0.06)
    cr.rectangle(0, 0, W, H); cr.set_source(g); cr.fill()
    for k in range(8):   # studio light streaks
        x = (k * 330 + t * 120) % (W + 600) - 300
        cr.move_to(x, 0); cr.line_to(x + 80, 0); cr.line_to(x - 220, H); cr.line_to(x - 300, H); cr.close_path(); rgb(cr, (0.3, 0.5, 1), 0.04); cr.fill()
    # main graphic: big chart panel
    px, py, pw, ph = 120, 150, 1680, 600
    rrect(cr, px, py, pw, ph, 18); rgb(cr, (0.02, 0.04, 0.1), 0.85); cr.fill_preserve(); cr.set_line_width(3); rgb(cr, (0.3, 0.5, 1), 0.6); cr.stroke()
    for i in range(1, 6):
        stroke_line(cr, [(px, py + i * ph / 6), (px + pw, py + i * ph / 6)], 1, (0.4, 0.5, 0.8), 0.2)
    n = 64
    vals = [idx_value(max(0.0, t - (n - 1 - k) * 0.35)) + 260 * math.sin(k * 2.7 + math.floor(t * 2.9)) * (0.4 + 0.6 * (k % 3 == 0)) for k in range(n)]
    lo, hi = min(vals) - 300, max(vals) + 300
    for k in range(1, n):
        x = px + 30 + k * (pw - 60) / n
        o, c_ = vals[k - 1], vals[k]
        yo = py + ph - 30 - (o - lo) / (hi - lo) * (ph - 60); yc = py + ph - 30 - (c_ - lo) / (hi - lo) * (ph - 60)
        candle(cr, x, yo, yc, min(yo, yc) - 10, max(yo, yc) + 10, 16, up=c_ >= o)
    v = idx_value(t); ch = (v - idx_ref(t)) / idx_ref(t) * 100
    text(cr, f"KSE-100  {v:,.0f}", px + 40, py + 50, 'interb', 40, (1, 1, 1), 1, 'l')
    text(cr, f"{'+' if ch >= 0 else ''}{ch:.2f}%", px + pw - 40, py + 50, 'interb', 40, C['green'] if ch >= 0 else C['red'], 1, 'r')
    # LIVE bug + channel name
    rrect(cr, 60, 50, 120, 54, 8); rgb(cr, (0.85, 0.05, 0.12)); cr.fill()
    circle(cr, 84, 77, 8); rgb(cr, (1, 1, 1), 0.5 + 0.5 * math.sin(t * 6)); cr.fill()
    text(cr, 'LIVE', 136, 77, 'interb', 28, (1, 1, 1))
    text(cr, 'MARKET WATCH  ·  09:31 PKT', 200, 77, 'interb', 28, (0.85, 0.9, 1), 1, 'l')
    # chant: full-screen breaking flash
    c, lt = chant_text(t)
    # lower third
    l = last_line(t); t0 = l[0]
    head = HEADLINE.get(t0, '')
    if c: head = 'DRAMAY BAAZ ALERT!' if c[2] == DB else 'NO MORE DRAMAY BAAZI!'
    slide = ease_out(clamp((t - (c[0] if c else t0)) / 0.35))
    y = 800
    rrect(cr, 60, y, 330, 70, 6); rgb(cr, (0.85, 0.05, 0.12)); cr.fill()
    text(cr, 'BREAKING NEWS', 225, y + 35, 'interb', 34, (1, 1, 1))
    cr.save(); cr.rectangle(390, y, W - 450, 160); cr.clip()
    cr.translate((1 - slide) * -1400, 0)
    cr.rectangle(390, y, W - 450, 70); rgb(cr, (0.97, 0.97, 0.98)); cr.fill()
    font(cr, 'interb', 40); sc = min(1, (W - 500) / max(1, cr.text_extents(head).x_advance))
    cr.save(); cr.translate(420, y + 35); cr.scale(sc, sc); text(cr, head, 0, 0, 'interb', 40, (0.05, 0.05, 0.1), 1, 'l'); cr.restore()
    cr.restore()
    cl = cur_line(t)
    if cl:
        cr.rectangle(60, y + 70, W - 120, 56); rgb(cr, (0.04, 0.08, 0.22), 0.95); cr.fill()
        text(cr, f"“{cl[1]}”  —  {cl[2]}", 90, y + 98, 'inter', 30, (0.85, 0.9, 1), 1, 'l')
    # ticker
    cr.rectangle(0, H - 70, W, 70); rgb(cr, (0.98, 0.8, 0.1)); cr.fill()
    rrect(cr, 0, H - 70, 190, 70, 0); rgb(cr, (0.04, 0.08, 0.22)); cr.fill()
    text(cr, 'PSX', 95, H - 35, 'interb', 34, (1, 1, 1))
    cr.save(); cr.rectangle(190, H - 70, W - 190, 70); cr.clip()
    msg = '   •   '.join(HEADLINE[k] for k in sorted(HEADLINE))
    x = 210 - (t * 160) % (text_w(cr, msg + '   •   ', 'interb', 30))
    text(cr, msg + '   •   ' + msg, x, H - 35, 'interb', 30, (0.05, 0.05, 0.1), 1, 'l')
    cr.restore()
    if c and lt < 0.6:
        cr.rectangle(0, 0, W, H); rgb(cr, (0.85, 0.05, 0.12), 0.5 * (1 - lt / 0.6)); cr.fill()


def glitch_amount(t):
    g = 0.25 * beat_pulse(t, 10) * env('bass', t)
    c = chant_at(t)
    if c: g += 0.8 * math.exp(-(t - c[0]) * 4)
    if 34.8 <= t < 36: g += 1.0 * (1 - (t - 34.8) / 1.2)
    return g


# =================================================================== D: 3D isometric candlestick city
def iso_city(cr, t):
    col, m = mood_col(t)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *mix((0.03, 0.05, 0.12), col, 0.12)); g.add_color_stop_rgb(1, 0.01, 0.02, 0.04)
    cr.rectangle(0, 0, W, H); cr.set_source(g); cr.fill()
    th = 0.78 + 0.18 * math.sin(t * 0.15)
    S = 62; cx, cy = W / 2, H * 0.6
    cs, sn = math.cos(th), math.sin(th)

    def P(x, y, z):
        return cx + (x * cs - y * sn) * S, cy + (x * sn + y * cs) * S * 0.5 - z * S

    N = 9
    # floor grid
    for i in range(-N // 2, N // 2 + 2):
        a, b = P(i - 0.5, -N / 2 - 0.5, 0), P(i - 0.5, N / 2 + 0.5, 0)
        cr.move_to(*a); cr.line_to(*b)
        a, b = P(-N / 2 - 0.5, i - 0.5, 0), P(N / 2 + 0.5, i - 0.5, 0)
        cr.move_to(*a); cr.line_to(*b)
    cr.set_line_width(1.5); rgb(cr, col, 0.25); cr.stroke()
    bi = beat_index(t); ph = beat_phase(t)
    towers = []
    for i in range(N):
        for j in range(N):
            x, y = i - N // 2, j - N // 2
            d = math.hypot(x, y)
            seed = math.sin(i * 12.9898 + j * 78.233) * 43758.5453; seed -= math.floor(seed)
            wave = math.exp(-((d - ph * 7) ** 2) / 2.0) * env('bass', t) * 2.2
            trend = market_mood(t) if section(t)[1] != 'chorus' else mood_sign(t)
            h = 0.6 + seed * 2.2 + wave + trend * (0.6 + seed) * 1.2 + 0.3 * math.sin(t * 1.3 + seed * 6)
            h = max(0.25, h)
            up = (seed + 0.15 * trend) > (0.5 - 0.35 * trend)
            towers.append((x * sn + y * cs, x, y, h, up))
    towers.sort()
    for _, x, y, h, up in towers:
        base = C['green'] if up else C['red']
        w = 0.32
        corners = [(x - w, y - w), (x + w, y - w), (x + w, y + w), (x - w, y + w)]
        top = [P(a, b, h) for a, b in corners]; bot = [P(a, b, 0) for a, b in corners]
        faces = []
        for k in range(4):
            k2 = (k + 1) % 4
            mx = (corners[k][0] + corners[k2][0]) / 2; my = (corners[k][1] + corners[k2][1]) / 2
            faces.append((mx * sn + my * cs, k, k2))
        faces.sort()
        for _, k, k2 in faces[2:]:
            cr.move_to(*bot[k]); cr.line_to(*bot[k2]); cr.line_to(*top[k2]); cr.line_to(*top[k]); cr.close_path()
            shade = 0.55 if (k % 2) else 0.75
            rgb(cr, mix(base, (0, 0, 0), 1 - shade)); cr.fill()
        cr.move_to(*top[0])
        for p in top[1:]: cr.line_to(*p)
        cr.close_path(); rgb(cr, mix(base, (1, 1, 1), 0.2)); cr.fill()
        a, b = P(x, y, h), P(x, y, h + 0.6)
        stroke_line(cr, [a, b], 3, base, 0.9)
    # floating 3D extruded keyword
    l = cur_line(t); c, lt = chant_text(t)
    word = ('DRAMAY BAAZ!' if c[2] == DB else 'AB NO DRAMAY BAAZI!') if c else (KEY.get(l[0], '') if l else '')
    if word:
        t0 = c[0] if c else l[0]
        p = back_out(clamp((t - t0) / 0.35))
        size = 150 if len(word) < 12 else 110
        cr.save(); cr.translate(W / 2, 250 + math.sin(t * 1.5) * 12); cr.scale(p * (1 + 0.04 * beat_pulse(t)), p * (1 + 0.04 * beat_pulse(t)))
        font(cr, 'bungee', size); wdt = cr.text_extents(word).x_advance
        for k in range(18, 0, -1):   # extrusion
            cr.move_to(-wdt / 2 + k * 1.2, size * 0.36 + k * 1.6); cr.text_path(word)
            rgb(cr, mix(col, (0, 0, 0), 0.45 + k * 0.02)); cr.fill()
        cr.move_to(-wdt / 2, size * 0.36); cr.text_path(word); rgb(cr, mix(col, (1, 1, 1), 0.25)); cr.fill()
        cr.restore()
    mini_caption(cr, t, y=H - 130)


# =================================================================== E: audio visualizer
def visualizer(cr, t):
    col, m = mood_col(t)
    cr.rectangle(0, 0, W, H); rgb(cr, (0.02, 0.025, 0.035)); cr.fill()
    fi = min(len(SPEC) - 1, max(0, int(t * 30)))
    sp = SPEC[fi]
    cx, cy = W / 2, H / 2 - 30
    bass = env('bass', t); bp = beat_pulse(t)
    R = 250 + 40 * bp * bass
    # particles burst on each beat
    bi = beat_index(t); age = t - BEATS[bi] if bi >= 0 else 9
    rnd = random.Random(bi)
    for k in range(70):
        ang = rnd.random() * TAU; spd = 300 + rnd.random() * 700
        r = R + age * spd
        if r > 1400: continue
        circle(cr, cx + math.cos(ang) * r, cy + math.sin(ang) * r, 2 + 3 * rnd.random()); rgb(cr, col, max(0, 0.8 - age * 1.2)); cr.fill()
    # radial spectrum, mirrored
    n = 64
    for side in (1, -1):
        for k in range(n):
            v = float(sp[k]) ** 1.6
            ang = -math.pi / 2 + side * (k + 0.5) / n * math.pi
            L = 20 + v * 330
            x1, y1 = cx + math.cos(ang) * R, cy + math.sin(ang) * R
            x2, y2 = cx + math.cos(ang) * (R + L), cy + math.sin(ang) * (R + L)
            stroke_line(cr, [(x1, y1), (x2, y2)], 11, mix(col, C['gold'], k / n * 0.6), 0.95)
    circle(cr, cx, cy, R - 14); cr.set_line_width(4); rgb(cr, col, 0.6); cr.stroke()
    # oscilloscope ring of recent rms
    cr.new_path()
    for k in range(181):
        ang = k / 180 * TAU
        rr = R - 40 - env('rms', t - k * 0.01) * 50
        (cr.line_to if k else cr.move_to)(cx + math.cos(ang) * rr, cy + math.sin(ang) * rr)
    cr.set_line_width(3); rgb(cr, (1, 1, 1), 0.35); cr.stroke()
    # centre: current word / chant / index
    c, lt = chant_text(t)
    l = cur_line(t)
    if c:
        s = 1 + 0.08 * beat_pulse(t, 9)
        cr.save(); cr.translate(cx, cy); cr.scale(s, s)
        if c[2] == DB:
            text(cr, 'DRAMAY', 0, -45, 'bungee', 84, C['white'], 1); text(cr, 'BAAZ!', 0, 55, 'bungee', 96, C['gold'], 1)
        else:
            text(cr, 'AB NO', 0, -60, 'bungee', 60, C['white'], 1); text(cr, 'DRAMAY', 0, 10, 'bungee', 70, C['gold'], 1); text(cr, 'BAAZI!', 0, 80, 'bungee', 70, C['gold'], 1)
        cr.restore()
    elif l:
        words = l[1].replace('"', '').split(' '); wts = word_times(l[0], words)
        i = max([k for k, wt in enumerate(wts) if t >= wt] or [0])
        p = clamp((t - wts[i]) / 0.15)
        w_ = words[i].upper()
        font(cr, 'anton', 150); sc = min(1, 380 / max(1, cr.text_extents(w_).x_advance))
        cr.save(); cr.translate(cx, cy); cr.scale(sc * lerp(1.3, 1, ease_out(p)), sc * lerp(1.3, 1, ease_out(p)))
        text(cr, w_, 0, 0, 'anton', 150, word_col(w_, C['white']), p); cr.restore()
    else:
        text(cr, f"{idx_value(t):,.0f}", cx, cy, 'anton', 110, col, 1)
    mini_caption(cr, t, y=H - 120)


CONCEPTS = {
    'A_kinetic_type': dict(title='A · Kinetic Typography', sub='The lyrics ARE the visuals: words slam in on the beat', fn=kinetic, post='glow_soft'),
    'B_screen_life': dict(title='B · Screen-Life (Phone POV)', sub="Story told on his phone: app, WhatsApp tips, Abba calling", fn=screenlife, post=None),
    'C_glitch_news': dict(title='C · Glitch News Broadcast', sub='Breaking-news parody with VHS glitch, RGB split on beats', fn=news, post='glitch'),
    'D_3d_city': dict(title='D · 3D Candlestick City', sub='Isometric 3D candle towers pumping to the bass, 3D words', fn=iso_city, post='glow_soft'),
    'E_visualizer': dict(title='E · Audio Visualizer', sub='Radial spectrum, beat particles, waveform rings', fn=visualizer, post='glow'),
}
