"""Drawing toolkit for the Dramay Baaz video: easing, audio-reactive helpers, text, brand marks, characters, props.
Everything is vector (Cairo), drawn fresh each frame at 1920x1080."""
import cairo, math, json, bisect, random
import numpy as np

W, H, FPS = 1920, 1080, 30
TAU = math.tau

# FloStocks palette (from flostocks.com) plus PSX market colours
C = dict(
    green=(0.235, 0.80, 0.0), green2=(0.18, 0.62, 0.0), forest=(0.024, 0.149, 0.0), night=(0.043, 0.059, 0.078),
    ink=(0.06, 0.07, 0.08), white=(1, 1, 1), cream=(0.98, 0.99, 0.985), red=(0.894, 0.0, 0.169), red2=(0.69, 0.0, 0.098),
    gold=(0.902, 0.659, 0.09), gold2=(1.0, 0.906, 0.604), sky=(0.07, 0.19, 0.22), skin=(0.85, 0.63, 0.47),
    skin2=(0.74, 0.52, 0.38), hair=(0.09, 0.07, 0.06), grey=(0.55, 0.58, 0.6), blue=(0.16, 0.42, 0.85),
)

TXT = (0.06, 0.07, 0.08)  # text colour on paper cards (independent of the style's line colour)
STYLE = dict(name='crayon', fill_a=0.82, hatch_a=0.55, hatch_sp=12, hatch_w=4, line=1.0, wob=1.0,
             wash_mix=0.22, wash_a=0.85, pastel=0.0, sat=1.0)


def style_color(c):
    st = STYLE
    if st['sat'] != 1.0:
        g = (c[0] + c[1] + c[2]) / 3
        c = tuple(clamp(g + (x - g) * st['sat']) for x in c)
    if st['pastel']:
        c = tuple(x + (1 - x) * st['pastel'] for x in c)
    return c


# ---------- audio data ----------
A = json.load(open('audio/analysis.json'))
BEATS = A['beats']


def env(name, t):
    a = A[name]; x = t * 30
    i = int(x)
    if i < 0: return a[0]
    if i >= len(a) - 1: return a[-1]
    f = x - i
    return a[i] * (1 - f) + a[i + 1] * f


def beat_pulse(t, decay=7.0):
    """1 right on a beat, decaying to 0 before the next."""
    i = bisect.bisect_right(BEATS, t) - 1
    if i < 0: return 0.0
    return math.exp(-(t - BEATS[i]) * decay)


def beat_index(t):
    return bisect.bisect_right(BEATS, t) - 1


def beat_phase(t):
    i = beat_index(t)
    if i < 0 or i + 1 >= len(BEATS): return 0.0
    return (t - BEATS[i]) / (BEATS[i + 1] - BEATS[i])


# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def prog(t, t0, d): return clamp((t - t0) / d) if d > 0 else float(t >= t0)
def ease_out(x): return 1 - (1 - x) ** 3
def ease_in(x): return x ** 3
def ease_io(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def back_out(x, s=1.9):
    x -= 1; return x * x * ((s + 1) * x + s) + 1


def elastic(x):
    if x <= 0: return 0
    if x >= 1: return 1
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * TAU / 3) + 1


def mix(c1, c2, t): return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


# ---------- primitives ----------
def rgb(cr, c, a=1.0):
    c = style_color(c)
    cr.set_source_rgba(c[0], c[1], c[2], a)


def rrect(cr, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -TAU / 4, 0); cr.arc(x + w - r, y + h - r, r, 0, TAU / 4)
    cr.arc(x + r, y + h - r, r, TAU / 4, TAU / 2); cr.arc(x + r, y + r, r, TAU / 2, 3 * TAU / 4)
    cr.close_path()


def para(cr, x, y, w, h, slant=0.35, r=10):
    """Slanted parallelogram (the FloStocks logo shape), x,y = top-left of the bounding box."""
    s = h * slant
    pts = [(x + s, y), (x + w, y), (x + w - s, y + h), (x, y + h)]
    cr.new_sub_path()
    for i in range(4):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % 4]
        d1 = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); d2 = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        a = (p1[0] + (p0[0] - p1[0]) * r / d1, p1[1] + (p0[1] - p1[1]) * r / d1)
        b = (p1[0] + (p2[0] - p1[0]) * r / d2, p1[1] + (p2[1] - p1[1]) * r / d2)
        cr.line_to(*a) if i else cr.move_to(*a)
        cr.curve_to(p1[0], p1[1], p1[0], p1[1], *b)
    cr.close_path()


def circle(cr, x, y, r):
    cr.new_sub_path(); cr.arc(x, y, r, 0, TAU)


# ---------- crayon look: wobbly paths, sketchy strokes, hatched fills ----------
BOIL = [0]  # changes ~8x/sec so lines "boil" like hand-drawn frames


def _jit(x, y, sd, amp):
    return (x + amp * (math.sin(x * 0.043 + y * 0.017 + sd) + 0.6 * math.sin(y * 0.097 - sd * 2.3 + x * 0.01)),
            y + amp * (math.sin(y * 0.047 - x * 0.019 + sd * 1.7) + 0.6 * math.sin(x * 0.089 + sd * 0.7)))


def wobble(cr, amp=2.6, k=0):
    """Replace the current path with a hand-wobbled, subdivided copy."""
    sd = BOIL[0] * 1.37 + k * 5.1
    path = cr.copy_path_flat(); cr.new_path()
    last = None; start = None
    for kind, pts in path:
        if kind == cairo.PATH_MOVE_TO:
            last = start = pts; cr.move_to(*_jit(pts[0], pts[1], sd, amp))
        elif kind == cairo.PATH_LINE_TO:
            if last:
                d = math.hypot(pts[0] - last[0], pts[1] - last[1]); n = int(d / 18)
                for i in range(1, n):
                    cr.line_to(*_jit(lerp(last[0], pts[0], i / n), lerp(last[1], pts[1], i / n), sd, amp))
            cr.line_to(*_jit(pts[0], pts[1], sd, amp)); last = pts
        elif kind == cairo.PATH_CLOSE_PATH:
            if last and start:
                d = math.hypot(start[0] - last[0], start[1] - last[1]); n = int(d / 18)
                for i in range(1, n):
                    cr.line_to(*_jit(lerp(last[0], start[0], i / n), lerp(last[1], start[1], i / n), sd, amp))
            cr.close_path(); last = start


def stroke_line(cr, pts, w, c, a=1.0, cap=cairo.LINE_CAP_ROUND):
    cr.new_path(); cr.move_to(*pts[0])
    for p in pts[1:]: cr.line_to(*p)
    _sketch_stroke(cr, w, c, a)


def _sketch_stroke(cr, w, c, a, keep=False):
    p = cr.copy_path()
    cr.set_line_cap(cairo.LINE_CAP_ROUND); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    for k in range(STYLE.get('passes', 2)):
        cr.new_path(); cr.append_path(p); wobble(cr, (2.2 + k * 1.2) * STYLE['wob'], k)
        cr.set_line_width(w * STYLE['line'] * (0.85 if k == 0 else 0.6)); rgb(cr, c, a * (0.95 if k == 0 else 0.6)); cr.stroke()
    cr.new_path()
    if keep: cr.append_path(p)


def halftone(cr, path, c, a):
    x0, y0, x1, y1 = cr.path_extents()
    if (x1 - x0) * (y1 - y0) < 900: return
    cr.save(); cr.new_path(); cr.append_path(path); cr.clip()
    sp = STYLE.get('dot_sp', 16); r = sp * 0.26
    cr.new_path()
    row = 0; y = y0 - sp
    while y < y1 + sp:
        x = x0 - sp + (sp / 2 if row % 2 else 0)
        while x < x1 + sp:
            cr.new_sub_path(); cr.arc(x, y, r, 0, TAU); x += sp
        y += sp * 0.87; row += 1
    rgb(cr, c, a); cr.fill()
    cr.restore()


def hatch(cr, path, c, a, spacing=None, ang=0.8, w=None):
    if STYLE.get('hatch_mode') == 'dots': return halftone(cr, path, c, a)
    if STYLE.get('hatch_mode') == 'none': return
    spacing = spacing or STYLE['hatch_sp']; w = w or STYLE['hatch_w']
    x0, y0, x1, y1 = cr.path_extents()
    if (x1 - x0) * (y1 - y0) < 900: return
    cr.save(); cr.new_path(); cr.append_path(path); wobble(cr); cr.clip()
    ca, sa = math.cos(ang), math.sin(ang)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; R = math.hypot(x1 - x0, y1 - y0) / 2 + 10
    k = -R; i = 0; rnd = random.Random(BOIL[0] * 7 + int(cx))
    cr.new_path()
    while k < R:
        px, py = cx - sa * k, cy + ca * k
        cr.move_to(px - ca * R, py - sa * R); cr.line_to(px + ca * R, py + sa * R)
        k += spacing * (0.7 + 0.6 * rnd.random()); i += 1
    wobble(cr, 3.0, 2)
    cr.set_line_width(w); rgb(cr, c, a); cr.stroke()
    cr.restore()


def fill(cr, c, a=1.0, keep=False):
    p = cr.copy_path()
    big = False
    try:
        x0, y0, x1, y1 = cr.path_extents(); big = (x1 - x0) * (y1 - y0) > W * H * 0.45
    except Exception: pass
    STYLE['_last'] = c
    if STYLE.get('shadow') and a > 0.6 and not big:
        cr.new_path(); cr.append_path(p); wobble(cr, 2.4 * STYLE['wob'])
        cr.save(); cr.translate(7, 9); rgb(cr, (0, 0, 0), 0.3 * a); cr.fill(); cr.restore()
    cr.new_path(); cr.append_path(p); wobble(cr, 2.4 * STYLE['wob'])
    rgb(cr, c, a * (STYLE['fill_a'] if not big and a > 0.6 else 1)); cr.fill()
    if a > 0.6 and not big:
        cr.new_path(); cr.append_path(p)
        sh = STYLE.get('shade')
        if sh == 'flowers' and c in (C['skin'], C['skin2'], C['white'], C['ink'], (0.95, 0.95, 0.93)): pass
        elif sh: _shade(cr, p, c, a, sh)
        else: hatch(cr, p, mix(c, (0.05, 0.05, 0.05), 0.22), a * STYLE['hatch_a'])
    cr.new_path()
    if keep: cr.append_path(p)


def _shade(cr, p, c, a, mode):
    x0, y0, x1, y1 = cr.path_extents()
    w, h = x1 - x0, y1 - y0
    if w * h < 300: return
    cr.save(); cr.new_path(); cr.append_path(p); cr.clip()
    if mode == 'cel':      # hard anime shadow crescent on the lower right
        rgb(cr, mix(c, (0.1, 0.05, 0.2), 0.32), a); cr.paint()
        cr.translate(-min(14, w * 0.12), -min(16, h * 0.12)); cr.new_path(); cr.append_path(p); rgb(cr, c, a); cr.fill()
        cr.identity_matrix()
    elif mode == 'clay':   # soft 3D clay: lit from the top-left, rim-darkened, small specular
        cr.new_path()
        g = cairo.RadialGradient(x0 + w * 0.32, y0 + h * 0.28, 0, x0 + w * 0.45, y0 + h * 0.45, max(w, h) * 0.75)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.38 * a); g.add_color_stop_rgba(0.45, 1, 1, 1, 0.0)
        g.add_color_stop_rgba(0.8, 0, 0, 0, 0.12 * a); g.add_color_stop_rgba(1, 0, 0, 0, 0.38 * a)
        cr.set_source(g); cr.paint()
        if w > 30 and h > 30:
            cr.save(); cr.translate(x0 + w * 0.3, y0 + h * 0.24); cr.scale(w * 0.09, h * 0.05); circle(cr, 0, 0, 1); cr.restore()
            cr.set_source_rgba(1, 1, 1, 0.55 * a); cr.fill()
    elif mode == 'flowers':   # truck-art: painted dots and little 5-petal flowers
        sp = 46; row = 0; y = y0 - sp
        fc = (1, 1, 1) if sum(c) < 1.8 else (0.85, 0.05, 0.25)
        while y < y1 + sp:
            x = x0 - sp + (sp / 2 if row % 2 else 0)
            while x < x1 + sp:
                if (row + int(x / sp)) % 2:
                    for k in range(5):
                        circle(cr, x + math.cos(k * TAU / 5) * 7, y + math.sin(k * TAU / 5) * 7, 4.5)
                    rgb(cr, fc, 0.85 * a); cr.fill(); circle(cr, x, y, 3.5); rgb(cr, (1, 0.85, 0.1), a); cr.fill()
                else:
                    circle(cr, x, y, 3); rgb(cr, fc, 0.7 * a); cr.fill()
                x += sp
            y += sp * 0.8; row += 1
    cr.restore()


def outline(cr, w=6, c=None, a=1.0):
    if STYLE.get('no_outline') and c is None:
        cr.new_path(); return
    if STYLE.get('neon') and c is None:
        c = mix(STYLE.get('_last', C['green']), (1, 1, 1), 0.3)
    _sketch_stroke(cr, w * 1.05, c or C['ink'], a)


# ---------- text ----------
FONTS = {'bungee': 'Cabin Sketch', 'anton': 'Caveat Brush', 'inter': 'Patrick Hand', 'interb': 'Gochi Hand', 'mono': 'Patrick Hand',
         'brand': 'Bungee'}


def font(cr, name, size):
    face_ = STYLE.get('fonts', {}).get(name, FONTS[name])
    weight = cairo.FONT_WEIGHT_BOLD if face_ in ('Cabin Sketch', 'Inter') else cairo.FONT_WEIGHT_NORMAL
    cr.select_font_face(face_, cairo.FONT_SLANT_NORMAL, weight)
    cr.set_font_size(size)


def text_w(cr, s, name, size):
    font(cr, name, size); return cr.text_extents(s).x_advance


def text(cr, s, x, y, name='bungee', size=60, c=C['white'], a=1.0, align='c', stroke=0, sc=None, shadow=0):
    """Draw text with its baseline-centre (align c) / left (l) / right (r) at x,y. y is the vertical centre of caps."""
    if not stroke and size >= 40 and c == C['white']: stroke = max(4, size * 0.07)
    font(cr, name, size)
    ext = cr.text_extents(s)
    fe = cr.font_extents()
    cap = fe[0] * 0.72
    tx = x - ext.x_advance / 2 if align == 'c' else x if align == 'l' else x - ext.x_advance
    ty = y + cap / 2
    if shadow:
        cr.move_to(tx + shadow, ty + shadow); cr.text_path(s); rgb(cr, C['ink'], a * 0.85); cr.fill()
    cr.move_to(tx, ty); cr.text_path(s)
    if stroke:
        cr.set_line_width(stroke); cr.set_line_join(cairo.LINE_JOIN_ROUND); rgb(cr, sc or C['ink'], a); cr.stroke_preserve()
    rgb(cr, c, a); cr.fill()
    return ext.x_advance


# ---------- brand (official FloStocks artwork only, never redrawn) ----------
_IMG = {}


def brand_img(cr, kind, cx, cy, width, a=1.0, dark=None, rot=0.0):
    """Paint an official logo PNG centred at cx,cy. kind: 'logo' (with tagline), 'wordmark' or 'icon'.
    dark=True picks the version made for dark backgrounds (white FLO / white bar)."""
    dark = STYLE.get('dark', False) if dark is None else dark
    key = f"assets/{kind}_{'dark' if dark else 'light'}.png"
    if key not in _IMG: _IMG[key] = cairo.ImageSurface.create_from_png(key)
    im = _IMG[key]; sc = max(1e-3, width / im.get_width())
    cr.save(); cr.translate(cx, cy); cr.rotate(rot); cr.scale(sc, sc)
    cr.translate(-im.get_width() / 2, -im.get_height() / 2)
    cr.set_source_surface(im, 0, 0); cr.get_source().set_filter(cairo.FILTER_BEST); cr.paint_with_alpha(a)
    cr.restore()


# ---------- characters ----------
def limb(cr, x, y, a1, l1, a2, l2, w, c, end=None, endc=None, endr=0):
    """Crayon stick limb from (x,y). Angles in degrees, 0 = straight down, positive = towards +x."""
    r1, r2 = math.radians(a1), math.radians(a1 + a2)
    x1, y1 = x + math.sin(r1) * l1, y + math.cos(r1) * l1
    x2, y2 = x1 + math.sin(r2) * l2, y1 + math.cos(r2) * l2
    stroke_line(cr, [(x, y), (x1, y1), (x2, y2)], w + 7, C['ink'], 0.9)
    stroke_line(cr, [(x, y), (x1, y1), (x2, y2)], w, c)
    if end:
        circle(cr, x2, y2, endr); fill(cr, endc, keep=True); outline(cr, 5)
    return x2, y2


DEFAULT_POSE = dict(lA=(-14, 8), rA=(14, -8), lL=(-4, 0), rL=(4, 0), lean=0, eyes='open', mouth='smile',
                    brows='up', look=(0, 0), bob=0, sweat=0, tears=0, blush=0, head_tilt=0, palm=False)
PANTS = (0.55, 0.7, 0.92)   # "white" shalwar, drawn the way a kid would: light blue crayon
CHEEK = (0.97, 0.45, 0.5)


def _legs(cr, p, hip, shoe):
    for side, (a1, a2) in ((-1, p['lL']), (1, p['rL'])):
        fx, fy = limb(cr, side * hip, -190, a1, 100, a2, 95, 24, PANTS)
        cr.save(); cr.translate(fx + side * 10, fy); cr.scale(34, 16); circle(cr, 0, 0, 1); cr.restore()
        fill(cr, shoe, keep=True); outline(cr, 5)


def _hands_front(cr, hands, palm=False):
    for hx, hy in hands:
        if hy < -430 and (palm or math.hypot(hx, hy + 505) > 112): circle(cr, hx, hy, 19); fill(cr, C['skin'], keep=True); outline(cr, 5)


def _stick(cr, x, y, s, p, t, father):
    """Whiteboard marker stick figure sharing the same pose rig."""
    if 880 <= y <= 980: y -= 70; s *= 0.94
    ink = C['ink']; acc = C['green2'] if not father else (0.5, 0.3, 0.15)
    cr.save(); cr.translate(x, y); cr.scale(s, s); cr.translate(0, -p['bob']); cr.rotate(math.radians(p['lean']))
    for side, (a1, a2) in ((-1, p['lL']), (1, p['rL'])):
        r1, r2 = math.radians(a1), math.radians(a1 + a2)
        x1, y1 = side * 6 + math.sin(r1) * 100, -190 + math.cos(r1) * 100
        stroke_line(cr, [(side * 6, -190), (x1, y1), (x1 + math.sin(r2) * 95, y1 + math.cos(r2) * 95)], 10, ink)
    stroke_line(cr, [(0, -190), (0, -392)], 11, ink)
    # one colour accent: green scarf for Baaz, brown waistcoat for Abba
    if father:
        cr.new_path(); cr.move_to(-40, -380); cr.line_to(40, -380); cr.line_to(30, -250); cr.line_to(-30, -250); cr.close_path()
        fill(cr, acc, 0.9, keep=True); outline(cr, 6)
    else:
        stroke_line(cr, [(-34, -378), (0, -360), (34, -378)], 16, acc); stroke_line(cr, [(10, -362), (26, -300)], 14, acc)
    hands = []
    for side, (a1, a2) in ((-1, p['lA']), (1, p['rA'])):
        r1, r2 = math.radians(a1), math.radians(a1 + a2)
        x1, y1 = side * 4 + math.sin(r1) * 92, -372 + math.cos(r1) * 92
        x2, y2 = x1 + math.sin(r2) * 82, y1 + math.cos(r2) * 82
        stroke_line(cr, [(side * 4, -372), (x1, y1), (x2, y2)], 10, ink)
        circle(cr, x2, y2, 12); fill(cr, (1, 1, 1), keep=True); outline(cr, 6); hands.append((x2, y2))
    cr.save(); cr.translate(0, -505); cr.rotate(math.radians(p['head_tilt']))
    circle(cr, 0, 0, 112); fill(cr, (1, 1, 1), keep=True); outline(cr, 8)
    if father:
        cr.new_path(); cr.move_to(-80, -84); cr.line_to(80, -84); cr.line_to(72, -140); cr.line_to(-72, -140); cr.close_path()
        fill(cr, (0.45, 0.43, 0.4), 0.9, keep=True); outline(cr, 6)
        cr.new_path(); cr.move_to(-100, 14); cr.curve_to(-90, 130, -40, 168, 0, 170); cr.curve_to(40, 168, 90, 130, 100, 14)
        cr.curve_to(60, 70, -60, 70, -100, 14); cr.close_path(); outline(cr, 6)
        for k in range(5): stroke_line(cr, [(-50 + k * 25, 90), (-44 + k * 25, 140)], 4, ink, 0.6)
    else:
        for k in range(7):
            ang = math.pi * (1.15 + 0.7 * k / 6)
            stroke_line(cr, [(math.cos(ang) * 108, math.sin(ang) * 108), (math.cos(ang) * 150, math.sin(ang) * 150 - 6)], 8, ink)
    cr.save(); cr.scale(1.15, 1.15); face(cr, p, t, abba=father); cr.restore()
    if not father:
        stroke_line(cr, [(-60, 46), (-28, 32), (0, 42), (28, 32), (60, 46)], 12, ink)
    cr.restore()
    cr.restore()
    return [(x + hx * s, y + (hy - p['bob']) * s) for hx, hy in hands]


def baaz(cr, x, y, s, pose=None, t=0, shirt=None):
    """Crayon doodle hero: big round head, spiky scribbled hair, curly mustache, green kurta. Origin at feet centre."""
    p = dict(DEFAULT_POSE); p.update(pose or {})
    if STYLE.get('stick'): return _stick(cr, x, y, s, p, t, False)
    shirt = shirt or C['green2']
    if 880 <= y <= 980: y -= 70; s *= 0.94
    cr.save(); cr.translate(x, y); cr.scale(s, s); cr.translate(0, -p['bob'])
    cr.rotate(math.radians(p['lean']))
    _legs(cr, p, 30, (0.35, 0.2, 0.1))
    cr.new_path(); cr.move_to(-66, -392); cr.line_to(66, -392); cr.line_to(104, -175); cr.line_to(-104, -175); cr.close_path()
    fill(cr, shirt, keep=True); outline(cr, 7)
    for by in (-360, -320, -280): circle(cr, 0, by, 7); fill(cr, C['gold'])
    hands = [limb(cr, -60, -372, p['lA'][0], 92, p['lA'][1], 82, 22, shirt, True, C['skin'], 19),
             limb(cr, 60, -372, p['rA'][0], 92, p['rA'][1], 82, 22, shirt, True, C['skin'], 19)]
    hs = STYLE.get('head', 1.0)
    cr.save(); cr.translate(0, -505 - 116 * (hs - 1)); cr.scale(hs, hs); cr.rotate(math.radians(p['head_tilt']))
    for side in (-1, 1): circle(cr, side * 112, 8, 22); fill(cr, C['skin2'], keep=True); outline(cr, 5)
    circle(cr, 0, 0, 116); fill(cr, C['skin'], keep=True); outline(cr, 7)
    # scribbled spiky hair
    pts = []
    for k in range(17):
        ang = math.pi * (1.06 + 0.88 * k / 16)
        r = 112 if k % 2 == 0 else 150 + 10 * math.sin(k * 2.3)
        pts.append((math.cos(ang) * r, math.sin(ang) * r - 6))
    cr.new_path(); cr.move_to(*pts[0])
    for q in pts[1:]: cr.line_to(*q)
    cr.arc_negative(0, -6, 108, math.pi * 1.94, math.pi * 1.06); cr.close_path()
    fill(cr, C['hair'], keep=True); outline(cr, 5)
    for side in (-1, 1):
        cr.save(); cr.translate(side * 70, 34); cr.scale(24, 15); circle(cr, 0, 0, 1); cr.restore(); fill(cr, CHEEK, 0.75)
    cr.save(); cr.scale(1.2, 1.2)
    face(cr, p, t)
    cr.restore()
    stroke_line(cr, [(-74, 50), (-58, 36), (-30, 30), (0, 40), (30, 30), (58, 36), (74, 50)], 15, C['hair'])
    cr.restore()
    _hands_front(cr, hands, p.get('palm'))
    cr.restore()
    return [(x + hx * s, y + (hy - p['bob']) * s) for hx, hy in hands]


def face(cr, p, t, abba=False):
    lx, ly = p['look']
    ey = -12
    e = p['eyes']
    blink = (t * 1.0) % 3.7 < 0.12 and e == 'open'
    for side in (-1, 1):
        ex = side * 34
        if e in ('happy',) or blink:
            cr.move_to(ex - 16, ey + 4); cr.curve_to(ex - 8, ey - 12, ex + 8, ey - 12, ex + 16, ey + 4)
            outline(cr, 6)
        elif e == 'closed' or e == 'cry':
            cr.move_to(ex - 16, ey); cr.curve_to(ex - 8, ey + 10, ex + 8, ey + 10, ex + 16, ey); outline(cr, 6)
        elif e == 'dizzy':
            cr.save(); cr.translate(ex, ey); cr.rotate(t * 8 * side)
            for k in range(30):
                a = k * 0.5; r = 1 + k * 0.6
                (cr.line_to if k else cr.move_to)(math.cos(a) * r, math.sin(a) * r)
            outline(cr, 4); cr.restore()
        elif e == 'dollar':
            cr.save(); cr.scale(1, 1.15); circle(cr, ex, ey / 1.15, 20); cr.restore(); fill(cr, C['white'], keep=True); outline(cr, 5)
            text(cr, '$', ex, ey, 'anton', 34, C['green2'])
        elif STYLE.get('anime') and e in ('open', 'shock'):
            big = e == 'shock'
            cr.save(); cr.translate(ex, ey + 4); cr.scale(21, 29); circle(cr, 0, 0, 1); cr.restore()
            fill(cr, C['white'], keep=True); outline(cr, 4)
            ix, iy = ex + lx * 4, ey + 8 + ly * 4
            cr.save(); cr.translate(ix, iy); cr.scale(13 if not big else 8, 22 if not big else 12); circle(cr, 0, 0, 1); cr.restore()
            fill(cr, (0.25, 0.14, 0.08))
            cr.save(); cr.translate(ix, iy + 6); cr.scale(9 if not big else 5, 11 if not big else 6); circle(cr, 0, 0, 1); cr.restore()
            fill(cr, (0.55, 0.32, 0.12))
            circle(cr, ix - 5, iy - 9, 6 if not big else 4); rgb(cr, (1, 1, 1)); cr.fill()
            circle(cr, ix + 5, iy + 7, 3); rgb(cr, (1, 1, 1)); cr.fill()
            stroke_line(cr, [(ex - 22, ey - 22), (ex, ey - 28), (ex + 22, ey - 22)], 6, C['ink'])
            if abba:
                circle(cr, ex, ey + 4, 30); outline(cr, 4, (0.25, 0.2, 0.15))
        else:
            big = e == 'shock'
            rw, rh = (22, 26) if big else (16, 20)
            cr.save(); cr.translate(ex, ey); cr.scale(rw, rh); circle(cr, 0, 0, 1); cr.restore()
            fill(cr, C['white'], keep=True); outline(cr, 5)
            pr = 6 if big else 9
            circle(cr, ex + lx * 6, ey + ly * 6 + 2, pr); fill(cr, C['ink'])
            if abba:
                circle(cr, ex, ey, 26); outline(cr, 5, (0.25, 0.2, 0.15))
    if abba:
        stroke_line(cr, [(-8, ey), (8, ey)], 5, (0.25, 0.2, 0.15))
    # brows
    b = p['brows']
    for side in (-1, 1):
        ex = side * 34
        if b == 'angry':
            pts = [(ex - side * 22, ey - 40), (ex + side * 18, ey - 26)][::side]
        elif b == 'sad':
            pts = [(ex - side * 20, ey - 26), (ex + side * 18, ey - 40)][::side]
        elif b == 'raised':
            pts = [(ex - 20, ey - 46), (ex + 20, ey - 50)]
        else:
            pts = [(ex - 20, ey - 36), (ex + 20, ey - 38)]
        stroke_line(cr, pts, 9, (0.85, 0.85, 0.85) if abba else C['hair'])
    # mouth
    m = p['mouth']; my = 62
    if m == 'smile':
        cr.move_to(-28, my - 6); cr.curve_to(-14, my + 14, 14, my + 14, 28, my - 6); outline(cr, 6)
    elif m == 'grin':
        cr.move_to(-38, my - 10); cr.curve_to(-20, my + 32, 20, my + 32, 38, my - 10); cr.close_path()
        fill(cr, (0.45, 0.08, 0.1), keep=True); outline(cr, 6)
        cr.rectangle(-26, my - 9, 52, 9); fill(cr, C['white'])
    elif m == 'shout' or m == 'o':
        rr = 26 + (6 * math.sin(t * 30) if m == 'shout' else 0)
        cr.save(); cr.translate(0, my + 8); cr.scale(0.8 if m == 'shout' else 0.5, 1 if m == 'shout' else 0.6); circle(cr, 0, 0, rr); cr.restore()
        fill(cr, (0.45, 0.08, 0.1), keep=True); outline(cr, 6)
    elif m == 'frown':
        cr.move_to(-26, my + 10); cr.curve_to(-12, my - 8, 12, my - 8, 26, my + 10); outline(cr, 6)
    elif m == 'wavy':
        cr.move_to(-30, my + 4)
        for k in range(1, 7): cr.line_to(-30 + k * 10, my + 4 + (6 if k % 2 else -6))
        outline(cr, 5)
    elif m == 'flat':
        stroke_line(cr, [(-22, my + 2), (22, my + 2)], 6, C['ink'])
    if p['blush']:
        for side in (-1, 1):
            cr.save(); cr.translate(side * 58, 25); cr.scale(18, 10); circle(cr, 0, 0, 1); cr.restore(); fill(cr, (0.95, 0.4, 0.4), p['blush'] * .6)
    if p['tears']:
        for side in (-1, 1):
            for k in range(3):
                ph = (t * 1.8 + k / 3) % 1
                tx = side * (34 + 10 + ph * 50); ty = ey + 10 + ph * 140 + ph * ph * 60
                cr.save(); cr.translate(tx, ty); cr.scale(1, 1.4); circle(cr, 0, 0, 9 * p['tears']); cr.restore(); fill(cr, (0.45, 0.75, 1.0), 0.9)
            # stream
            cr.move_to(side * 40, ey + 14); cr.curve_to(side * 46, ey + 60, side * 48, ey + 90, side * 52, ey + 120)
            outline(cr, 10 * p['tears'], (0.45, 0.75, 1.0), 0.8)
    if p['sweat']:
        ph = (t * 1.3) % 1
        cr.save(); cr.translate(78, -50 + ph * 60); cr.scale(1, 1.5); circle(cr, 0, 0, 10); cr.restore()
        fill(cr, (0.55, 0.85, 1.0), (1 - ph) * p['sweat'], keep=True); outline(cr, 3, C['ink'], 1 - ph)


def abba(cr, x, y, s, pose=None, t=0):
    """Crayon doodle father: karakul cap, round glasses, scribbled white beard, brown waistcoat."""
    p = dict(DEFAULT_POSE); p.update(pose or {})
    if STYLE.get('stick'): return _stick(cr, x, y, s, p, t, True)
    if 880 <= y <= 980: y -= 70; s *= 0.94
    cr.save(); cr.translate(x, y); cr.scale(s, s); cr.translate(0, -p['bob']); cr.rotate(math.radians(p['lean']))
    _legs(cr, p, 34, (0.3, 0.18, 0.1))
    kameez = (0.93, 0.93, 0.86)
    cr.new_path(); cr.move_to(-72, -392); cr.line_to(72, -392); cr.curve_to(150, -320, 140, -220, 118, -172)
    cr.line_to(-118, -172); cr.curve_to(-140, -220, -150, -320, -72, -392); cr.close_path()
    fill(cr, kameez, keep=True); outline(cr, 7)
    for side in (-1, 1):
        cr.new_path(); cr.move_to(side * 16, -392); cr.line_to(side * 72, -392); cr.curve_to(side * 128, -330, side * 124, -270, side * 110, -232)
        cr.line_to(side * 16, -246); cr.close_path(); fill(cr, (0.5, 0.3, 0.15), keep=True); outline(cr, 6)
    hands = [limb(cr, -66, -372, p['lA'][0], 92, p['lA'][1], 82, 24, kameez, True, C['skin'], 19),
             limb(cr, 66, -372, p['rA'][0], 92, p['rA'][1], 82, 24, kameez, True, C['skin'], 19)]
    hs = STYLE.get('head', 1.0)
    cr.save(); cr.translate(0, -505 - 116 * (hs - 1)); cr.scale(hs, hs); cr.rotate(math.radians(p['head_tilt']))
    for side in (-1, 1): circle(cr, side * 112, 8, 22); fill(cr, C['skin2'], keep=True); outline(cr, 5)
    circle(cr, 0, 0, 114); fill(cr, C['skin'], keep=True); outline(cr, 7)
    for side in (-1, 1):  # grey side tufts
        stroke_line(cr, [(side * 100, -40), (side * 118, -20), (side * 104, 0), (side * 120, 20), (side * 106, 40)], 12, (0.7, 0.7, 0.72))
    # karakul cap
    cr.new_path(); cr.move_to(-84, -86); cr.line_to(84, -86); cr.line_to(76, -150); cr.line_to(-76, -150); cr.close_path()
    fill(cr, (0.42, 0.4, 0.38), keep=True); outline(cr, 6)
    for k in range(7): stroke_line(cr, [(-66 + k * 22, -138), (-58 + k * 22, -100)], 5, (0.25, 0.24, 0.23), 0.8)
    # beard
    cr.new_path(); cr.move_to(-104, 10); cr.curve_to(-96, 130, -40, 170, 0, 172); cr.curve_to(40, 170, 96, 130, 104, 10)
    cr.curve_to(70, 70, 40, 84, 0, 84); cr.curve_to(-40, 84, -70, 70, -104, 10); cr.close_path()
    fill(cr, (0.95, 0.95, 0.93), keep=True); outline(cr, 5)
    for side in (-1, 1):
        cr.save(); cr.translate(side * 70, 34); cr.scale(22, 13); circle(cr, 0, 0, 1); cr.restore(); fill(cr, CHEEK, 0.6)
    cr.save(); cr.scale(1.2, 1.2)
    face(cr, p, t, abba=True)
    cr.restore()
    stroke_line(cr, [(-60, 50), (-30, 38), (0, 46), (30, 38), (60, 50)], 13, (0.85, 0.85, 0.85))
    cr.restore()
    _hands_front(cr, hands, p.get('palm'))
    cr.restore()


# ---------- props ----------
def candle(cr, x, yo, yc, yh, yl, w, up=None, a=1.0):
    up = (yc < yo) if up is None else up
    c = C['green'] if up else C['red']
    stroke_line(cr, [(x, yh), (x, yl)], max(2, w * 0.12), c, a, cairo.LINE_CAP_BUTT)
    top, bot = min(yo, yc), max(yo, yc)
    cr.rectangle(x - w / 2, top, w, max(2, bot - top)); fill(cr, c, a)


def phone(cr, x, y, s, t, content=None, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    rrect(cr, -110, -200, 220, 400, 30); fill(cr, C['ink'], a, keep=True); outline(cr, 6, (0.3, 0.3, 0.3), a)
    rrect(cr, -98, -186, 196, 372, 20); fill(cr, C['night'], a)
    if content: cr.save(); rrect(cr, -98, -186, 196, 372, 20); cr.clip(); content(cr); cr.restore()
    rrect(cr, -30, -194, 60, 10, 5); fill(cr, (0.2, 0.2, 0.2), a)
    cr.restore()


def chai(cr, x, y, s, t, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    for k in range(3):
        ph = (t * 0.6 + k / 3) % 1
        cr.move_to(-30 + k * 30, -70 - ph * 120)
        cr.curve_to(-50 + k * 30, -100 - ph * 120, -10 + k * 30, -130 - ph * 120, -30 + k * 30, -160 - ph * 120)
        outline(cr, 8, C['white'], a * (1 - ph) * 0.6)
    cr.move_to(-70, -70); cr.line_to(70, -70); cr.line_to(55, 60); cr.line_to(-55, 60); cr.close_path()
    fill(cr, (0.95, 0.95, 0.92), a, keep=True); outline(cr, 6, C['ink'], a)
    cr.rectangle(-66, -62, 132, 30); fill(cr, (0.72, 0.5, 0.3), a)
    cr.arc(80, -10, 30, -TAU / 4, TAU / 4); outline(cr, 12, C['ink'], a); cr.arc(80, -10, 30, -TAU / 4, TAU / 4); outline(cr, 6, (0.95, 0.95, 0.92), a)
    cr.save(); cr.translate(0, 70); cr.scale(110, 18); circle(cr, 0, 0, 1); cr.restore(); fill(cr, (0.95, 0.95, 0.92), a, keep=True); outline(cr, 5, C['ink'], a)
    cr.restore()


def button(cr, x, y, w, h, label, col, press=0.0, a=1.0, size=None):
    d = 14 * (1 - press)
    rrect(cr, x - w / 2, y - h / 2 + 14, w, h, h * 0.3); fill(cr, mix(col, C['ink'], 0.5), a)
    rrect(cr, x - w / 2, y - h / 2 + 14 - d, w, h, h * 0.3); fill(cr, col, a, keep=True); outline(cr, 6, C['ink'], a)
    text(cr, label, x, y + 14 - d, 'bungee', size or h * 0.48, C['white'], a, stroke=8)


def bubble(cr, x, y, w, h, tail=(-1, 1), c=C['white'], a=1.0):
    rrect(cr, x - w / 2, y - h / 2, w, h, 28)
    tx = x + tail[0] * w * 0.3; ty = y + tail[1] * h / 2
    cr.move_to(tx - 24, ty - tail[1] * 4); cr.line_to(tx + tail[0] * 30, ty + tail[1] * 50); cr.line_to(tx + 24, ty - tail[1] * 4)
    fill(cr, c, a, keep=True); outline(cr, 6, C['ink'], a)
    rrect(cr, x - w / 2 + 3, y - h / 2 + 3, w - 6, h - 6, 26); fill(cr, c, a)


def burst(cr, x, y, r1, r2, n, c, rot=0, a=1.0):
    cr.new_path()
    for k in range(n * 2):
        ang = rot + k * math.pi / n; r = r1 if k % 2 == 0 else r2
        (cr.line_to if k else cr.move_to)(x + math.cos(ang) * r, y + math.sin(ang) * r)
    cr.close_path(); fill(cr, c, a, keep=True); outline(cr, 6, C['ink'], a)


def coin(cr, x, y, r, rot=0, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(max(0.15, abs(math.cos(rot))), 1)
    circle(cr, 0, 0, r); fill(cr, C['gold'], a, keep=True); outline(cr, 4, C['ink'], a)
    circle(cr, 0, 0, r * 0.7); outline(cr, 3, (0.7, 0.5, 0.05), a)
    text(cr, 'Rs', 0, 0, 'anton', r * 0.8, (0.6, 0.4, 0.0), a)
    cr.restore()


def note(cr, x, y, s, rot=0, a=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    rrect(cr, -60, -30, 120, 60, 6); fill(cr, (0.55, 0.78, 0.45), a, keep=True); outline(cr, 4, C['ink'], a)
    circle(cr, 0, 0, 16); outline(cr, 3, (0.2, 0.4, 0.15), a)
    text(cr, '5000', 0, 0, 'anton', 18, (0.15, 0.35, 0.1), a)
    cr.restore()


def house(cr, x, y, s, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.rectangle(-90, -100, 180, 100); fill(cr, (0.98, 0.9, 0.75), a, keep=True); outline(cr, 6, C['ink'], a)
    cr.move_to(-115, -95); cr.line_to(0, -180); cr.line_to(115, -95); cr.close_path(); fill(cr, C['red'], a, keep=True); outline(cr, 6, C['ink'], a)
    cr.rectangle(-20, -60, 40, 60); fill(cr, (0.45, 0.28, 0.15), a, keep=True); outline(cr, 5, C['ink'], a)
    for wx in (-65, 40): cr.rectangle(wx, -80, 26, 26); fill(cr, (0.6, 0.85, 1), a, keep=True); outline(cr, 4, C['ink'], a)
    cr.restore()


def car(cr, x, y, s, t=0, a=1.0, col=None):
    col = col or C['gold']
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-150, -20); cr.line_to(-140, -70); cr.line_to(-70, -80); cr.line_to(-40, -125); cr.line_to(60, -125)
    cr.line_to(100, -80); cr.line_to(150, -70); cr.line_to(155, -20); cr.close_path(); fill(cr, col, a, keep=True); outline(cr, 6, C['ink'], a)
    cr.move_to(-30, -115); cr.line_to(50, -115); cr.line_to(80, -82); cr.line_to(-55, -82); cr.close_path(); fill(cr, (0.6, 0.85, 1), a, keep=True); outline(cr, 4, C['ink'], a)
    for wx in (-90, 95):
        circle(cr, wx, -18, 30); fill(cr, C['ink'], a); circle(cr, wx, -18, 12); fill(cr, C['grey'], a)
        stroke_line(cr, [(wx + math.cos(t * 12) * 12, -18 + math.sin(t * 12) * 12), (wx, -18)], 4, C['ink'], a)
    cr.restore()


def crown(cr, x, y, s, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    cr.move_to(-80, 30); cr.line_to(-90, -40); cr.line_to(-45, 0); cr.line_to(0, -60); cr.line_to(45, 0); cr.line_to(90, -40); cr.line_to(80, 30); cr.close_path()
    fill(cr, C['gold'], a, keep=True); outline(cr, 6, C['ink'], a)
    for gx, gc in ((-40, C['red']), (0, C['green']), (40, C['blue'])): circle(cr, gx, 12, 9); fill(cr, gc, a)
    cr.restore()


def piggy(cr, x, y, s, crack=0.0, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    pink = (0.98, 0.6, 0.7)
    for lx in (-50, -15, 25, 55): rrect(cr, lx - 12, 40, 24, 45, 8); fill(cr, pink, a, keep=True); outline(cr, 5, C['ink'], a)
    cr.save(); cr.scale(1.25, 1); circle(cr, 0, 0, 80); cr.restore(); fill(cr, pink, a, keep=True); outline(cr, 6, C['ink'], a)
    cr.save(); cr.translate(100, 5); cr.scale(0.8, 1); circle(cr, 0, 0, 26); cr.restore(); fill(cr, (0.95, 0.5, 0.6), a, keep=True); outline(cr, 5, C['ink'], a)
    circle(cr, 95, 0, 4); fill(cr, C['ink'], a); circle(cr, 107, 0, 4); fill(cr, C['ink'], a)
    circle(cr, 55, -30, 8); fill(cr, C['ink'], a)
    cr.move_to(-30, -45); cr.line_to(-60, -100); cr.line_to(0, -70); fill(cr, pink, a, keep=True); outline(cr, 5, C['ink'], a)
    rrect(cr, -25, -82, 50, 10, 5); fill(cr, C['ink'], a)
    if crack > 0:
        pts = [(-20, -78), (-5, -40), (-30, -10), (0, 20), (-15, 50), (5, 80)]
        n = 1 + int(crack * (len(pts) - 1))
        stroke_line(cr, pts[:n + 1], 6, C['ink'], a)
    cr.restore()


def newspaper(cr, x, y, s, rot, headline, a=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(s, s)
    cr.rectangle(-260, -170, 520, 340); fill(cr, (0.96, 0.94, 0.88), a, keep=True); outline(cr, 6, C['ink'], a)
    text(cr, 'DAILY KHABAR', 0, -130, 'anton', 44, C['ink'], a)
    stroke_line(cr, [(-240, -100), (240, -100)], 4, C['ink'], a)
    text(cr, headline, 0, -55, 'anton', 62, C['red2'], a)
    for k in range(5):
        stroke_line(cr, [(-240, 0 + k * 28), (-20, 0 + k * 28)], 8, (0.7, 0.7, 0.68), a)
    cr.rectangle(10, -10, 230, 150); fill(cr, (0.85, 0.85, 0.8), a)
    stroke_line(cr, [(20, 120), (70, 80), (110, 100), (160, 40), (230, 0)], 8, C['green2'], a)
    cr.restore()


def monitor(cr, x, y, w, h, a=1.0, content=None, crack=0.0):
    rrect(cr, x - w / 2 - 18, y - h / 2 - 18, w + 36, h + 36, 18); fill(cr, (0.15, 0.16, 0.18), a, keep=True); outline(cr, 6, C['ink'], a)
    cr.rectangle(x - w / 2, y - h / 2, w, h); fill(cr, C['night'], a)
    if content: cr.save(); cr.rectangle(x - w / 2, y - h / 2, w, h); cr.clip(); content(cr); cr.restore()
    cr.rectangle(x - 30, y + h / 2 + 18, 60, 70); fill(cr, (0.15, 0.16, 0.18), a, keep=True); outline(cr, 5, C['ink'], a)
    rrect(cr, x - 120, y + h / 2 + 80, 240, 26, 10); fill(cr, (0.15, 0.16, 0.18), a, keep=True); outline(cr, 5, C['ink'], a)
    if crack > 0:
        rnd = random.Random(7)
        cx, cy = x + w * 0.1, y - h * 0.05
        for k in range(9):
            ang = k * TAU / 9 + rnd.random() * 0.4; L = (0.25 + rnd.random() * 0.4) * w * crack
            pts = [(cx, cy)]
            for j in range(1, 4):
                pts.append((cx + math.cos(ang + rnd.uniform(-.25, .25)) * L * j / 3, cy + math.sin(ang + rnd.uniform(-.25, .25)) * L * j / 3))
            stroke_line(cr, pts, 4, C['white'], a * 0.85)


def magnifier(cr, x, y, s, a=1.0):
    cr.save(); cr.translate(x, y); cr.scale(s, s)
    stroke_line(cr, [(60, 60), (150, 150)], 34, C['ink'], a); stroke_line(cr, [(60, 60), (150, 150)], 22, (0.45, 0.28, 0.15), a)
    circle(cr, 0, 0, 90); fill(cr, (0.75, 0.9, 1.0), a * 0.35, keep=True); outline(cr, 16, C['ink'], a)
    circle(cr, 0, 0, 90); outline(cr, 8, C['grey'], a)
    cr.arc(0, 0, 65, math.pi * 1.1, math.pi * 1.4); outline(cr, 8, C['white'], a * 0.8)
    cr.restore()


def tick(cr, x, y, s, c=C['green'], a=1.0, p=1.0):
    pts = [(x - s * .5, y), (x - s * .15, y + s * .35), (x + s * .55, y - s * .4)]
    if p < 1:
        seg = p * 2
        if seg <= 1: pts = [pts[0], (lerp(pts[0][0], pts[1][0], seg), lerp(pts[0][1], pts[1][1], seg))]
        else: pts = [pts[0], pts[1], (lerp(pts[1][0], pts[2][0], seg - 1), lerp(pts[1][1], pts[2][1], seg - 1))]
    stroke_line(cr, pts, s * 0.22, C['ink'], a); stroke_line(cr, pts, s * 0.13, c, a)


def cross(cr, x, y, s, a=1.0):
    for d in ((-1, -1, 1, 1), (-1, 1, 1, -1)):
        stroke_line(cr, [(x + d[0] * s / 2, y + d[1] * s / 2), (x + d[2] * s / 2, y + d[3] * s / 2)], s * 0.24, C['ink'], a)
        stroke_line(cr, [(x + d[0] * s / 2, y + d[1] * s / 2), (x + d[2] * s / 2, y + d[3] * s / 2)], s * 0.15, C['red'], a)


def stamp(cr, x, y, label, size, c, rot=-0.12, a=1.0, sc=1.0):
    cr.save(); cr.translate(x, y); cr.rotate(rot); cr.scale(sc, sc)
    w = text_w(cr, label, 'bungee', size) + size * 0.8
    h = size * 1.5
    rrect(cr, -w / 2, -h / 2, w, h, 14); rgb(cr, (0.99, 0.98, 0.94), a * 0.9); cr.fill_preserve(); outline(cr, size * 0.12, c, a)
    rrect(cr, -w / 2 + size * .14, -h / 2 + size * .14, w - size * .28, h - size * .28, 10); outline(cr, size * 0.04, c, a)
    text(cr, label, 0, 0, 'bungee', size, c, a)
    cr.restore()
