"""Render the crayon-style video. Each frame: draw the scene and UI as vector layers with Cairo, then composite
them onto a paper texture through animated crayon-grain masks (numpy), and pipe RGB frames into ffmpeg.
usage: python3 render.py [fps] [workers]   |   python3 render.py stills t1 t2 ..."""
import sys, os, subprocess, time
from multiprocessing import Process
import numpy as np, cairo
from PIL import Image, ImageFilter
import lib
from lib import W, H
import scenes

OUT = 'build'


class Ctx(cairo.Context):
    """Cairo context whose scale never collapses to zero (pop-in animations start at scale 0)."""
    def scale(self, sx, sy):
        sx = sx if abs(sx) > 1e-3 else 1e-3; sy = sy if abs(sy) > 1e-3 else 1e-3
        super().scale(sx, sy)


def _smooth_noise(rng, cells, size):
    n = rng.random((size[1] // cells + 2, size[0] // cells + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((size[0], size[1]), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255


STYLES = {
    'A_crayon': dict(title='A · Crayon', sub="Kid's crayon drawing on paper, hand-drawn line boil", paper=(0.96, 0.94, 0.88), grain=1.0, kind='plain', style={}),
    'B_paper_cutout': dict(title='B · Paper Cut-Out', sub='Construction-paper collage, stop-motion jitter, drop shadows', paper=(0.93, 0.9, 0.82), grain=0.35,
                           kind='kraft', style=dict(fill_a=1.0, hatch_mode='none', shadow=True, no_outline=True, wob=1.3, wash_mix=0.1, wash_a=1.0, sat=1.1, bg='bands',
                                      fonts=dict(bungee='Luckiest Guy', anton='Luckiest Guy', interb='Luckiest Guy'))),
    'C_neon': dict(title='C · Neon Trading Floor', sub='Glowing neon lines on a dark synthwave market', paper=(0.03, 0.02, 0.07), grain=0.08, kind='plain',
                   ink=(0.02, 0.02, 0.05), post='glow',
                   style=dict(fill_a=0.18, hatch_mode='none', neon=True, passes=1, wob=0.15, line=0.8, wash_mix=0.0, wash_a=1.0, sat=1.4, bg='neon',
                              caption='neon', fonts=dict(bungee='Audiowide', anton='Audiowide', interb='Audiowide', inter='Inter', mono='JetBrains Mono'))),
    'D_pop_art': dict(title='D · Pop-Art Comic', sub='Bold black ink, Ben-Day halftone dots, punchy colours', paper=(0.99, 0.95, 0.83), grain=0.2, kind='plain',
                      ink=(0.02, 0.02, 0.02), style=dict(fill_a=1.0, hatch_mode='dots', hatch_a=0.45, dot_sp=15, passes=1, wob=0.25, line=1.6,
                                                         sat=1.35, wash_mix=0.05, wash_a=1.0, bg='halftone', panel=True,
                                                         caption='comic', fonts=dict(bungee='Bangers', anton='Bangers', interb='Bangers', inter='Inter'))),
    'E_risograph': dict(title='E · Risograph Print', sub='Retro zine print: four fluorescent inks, grainy dither', paper=(0.97, 0.95, 0.9), grain=0.5, kind='plain',
                        post='riso', style=dict(fill_a=1.0, hatch_mode='none', passes=1, wob=0.6, wash_mix=0.3, wash_a=1.0, caption='riso',
                                   fonts=dict(bungee='Rubik Mono One', anton='Anton', interb='Anton', inter='Inter'))),
}
STYLES['MAIN'] = dict(STYLES['D_pop_art'], title='Pop-Art Comic + Kinetic Type', sub='Story in comic panels, chants and choruses as kinetic type')
STYLES['MAIN']['style'] = dict(STYLES['D_pop_art']['style'], kinetic=True, no_wipes=True,
                               fonts=dict(bungee='Bangers', anton='Bangers', interb='Bangers', inter='Inter', mono='Bangers'))
RISO = np.array([[0.97, 0.95, 0.9], [1.0, 0.85, 0.12], [1.0, 0.33, 0.58], [0.0, 0.64, 0.66], [0.16, 0.2, 0.52],
                 [1.0, 0.33, 0.58 * 0.12 + 0.0], [0.0, 0.62, 0.15], [0.16, 0.2, 0.52 * 0.66], [0.12, 0.1, 0.16], [0.55, 0.12, 0.35]], np.float32)
PICO = np.array([[0, 0, 0], [29, 43, 83], [126, 37, 83], [0, 135, 81], [171, 82, 54], [95, 87, 79], [194, 195, 199], [255, 241, 232],
                 [255, 0, 77], [255, 163, 0], [255, 236, 39], [0, 228, 54], [41, 173, 255], [214, 156, 112], [255, 119, 168], [255, 204, 170]],
                np.float32) / 255
POST = [None]
CHAR_STYLES = {
    'A_truck_art': dict(title='A · Pakistani Truck Art', sub='Folk-art paint, flower patterns, chamak-patti border', paper=(0.98, 0.95, 0.85), grain=0.25,
                        kind='plain', style=dict(fill_a=1.0, shade='flowers', passes=1, wob=0.3, line=1.3, sat=1.45, wash_mix=0.0, wash_a=1.0,
                                                 bg='rays', truck_border=True, caption='truck', fonts=dict(bungee='Luckiest Guy', anton='Luckiest Guy', interb='Luckiest Guy'))),
    'B_pixel_game': dict(title='B · 8-bit Pixel Game', sub='Retro video-game sprites, RPG dialogue boxes', paper=(0.1, 0.1, 0.15), grain=0.0, kind='plain', post='pixel',
                         style=dict(fill_a=1.0, hatch_mode='none', passes=1, wob=0.0, line=1.5, wash_mix=0.0, wash_a=1.0, bg='plain', caption='dialog',
                                    fonts=dict(bungee='Press Start 2P', anton='Press Start 2P', interb='Press Start 2P', inter='Press Start 2P', mono='Press Start 2P'))),
    'C_claymation': dict(title='C · Claymation', sub='Soft 3D clay figures, studio lighting, stop-motion feel', paper=(0.9, 0.88, 0.84), grain=0.15, kind='plain',
                         style=dict(fill_a=1.0, shade='clay', shadow=True, no_outline=True, wob=0.9, wash_mix=0.15, wash_a=1.0, bg='plain', sat=1.1,
                                    fonts=dict(bungee='Luckiest Guy', anton='Luckiest Guy', interb='Luckiest Guy'))),
    'D_whiteboard': dict(title='D · Whiteboard Stick Figures', sub='Marker explainer style, one colour accent', paper=(0.985, 0.985, 0.98), grain=0.2, kind='plain',
                         style=dict(stick=True, fill_a=0.25, hatch_mode='none', passes=1, wob=0.5, line=1.1, wash_mix=0.9, wash_a=1.0, bg='plain', caption='plain',
                                    fonts=dict(bungee='Gochi Hand', anton='Gochi Hand', interb='Gochi Hand'))),
    'E_anime_chibi': dict(title='E · Anime Chibi', sub='Big heads, sparkly eyes, cel shading, speed lines', paper=(0.97, 0.97, 1.0), grain=0.0, kind='plain',
                          style=dict(anime=True, head=1.3, fill_a=1.0, shade='cel', passes=1, wob=0.0, line=0.75, sat=1.15, wash_mix=0.35, wash_a=1.0, bg='rays',
                                     caption='plain', fonts=dict(bungee='Bangers', anton='Bangers', interb='Bangers', inter='Inter'))),
}
BASE_STYLE = dict(lib.STYLE); BASE_INK = lib.C['ink']


def make_paper(base=(0.96, 0.94, 0.88), kind='plain'):
    rng = np.random.default_rng(7)
    low = _smooth_noise(rng, 90, (W, H)) * 0.6 + _smooth_noise(rng, 23, (W, H)) * 0.4
    fine = rng.random((H, W)).astype(np.float32)
    # faint horizontal fibres
    fib = np.repeat(rng.random((H, 1)).astype(np.float32), W, 1) * _smooth_noise(rng, 40, (W, H))
    shade = 0.93 + 0.07 * low - 0.025 * fine - 0.02 * (fib > 0.6)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.12 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    if kind == 'board':
        shade = 0.85 + 0.3 * low + 0.04 * fine
    if kind == 'kraft':
        shade = shade * (0.95 + 0.08 * (fib > 0.4))
    out = (np.array(base, np.float32)[None, None, :] * (shade * vig)[..., None]).astype(np.float32)
    if kind == 'ruled':
        for y in range(150, H, 56):
            out[y:y + 2] = out[y:y + 2] * 0.55 + np.array([0.35, 0.55, 0.85], np.float32) * 0.45
        out[:, 150:153] = out[:, 150:153] * 0.4 + np.array([0.9, 0.3, 0.35], np.float32) * 0.6
    return out


def use_style(key):
    global PAPER, GRAINS, GRAINS_UI
    st = {**STYLES, **CHAR_STYLES}[key]
    lib.STYLE.clear(); lib.STYLE.update(BASE_STYLE); lib.STYLE.update(st['style']); lib.STYLE['paper_rgb'] = st['paper']
    lib.C['ink'] = st.get('ink', BASE_INK)
    POST[0] = st.get('post')
    PAPER = make_paper(st['paper'], st['kind'])
    GRAINS = [make_grain(s, st['grain']) for s in range(3)]
    GRAINS_UI = [make_grain(10 + s, 0.35) for s in range(3)]


def make_grain(seed, strength):
    """Waxy crayon tooth: long diagonal streaks plus a little speckle; 1 = full pigment, low = paper shows through."""
    rng = np.random.default_rng(seed)
    h3, w3 = H // 3 + 20, W // 3 + 40
    n = rng.random((h3, w3)).astype(np.float32)
    acc = n.copy()
    for i in range(1, 14):
        acc += np.roll(np.roll(n, i, 0), 2 * i, 1)
    acc = acc[10:H // 3 + 10, 20:W // 3 + 20]
    acc = (acc - acc.mean()) / acc.std()
    g = np.asarray(Image.fromarray(((np.clip(acc, -3, 3) + 3) / 6 * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255 * 6 - 3
    fine = rng.random((H, W)).astype(np.float32)
    speck = (fine > 0.93).astype(np.float32)
    v = 0.93 + 0.13 * g - 0.35 * speck
    return np.clip(1 - strength + strength * v, 0.12, 1.0).astype(np.float32)


ONES = np.ones((H, W), np.float32)
PAPER = make_paper()
GRAINS = [make_grain(s, 1.0) for s in range(3)]
GRAINS_UI = [make_grain(10 + s, 0.35) for s in range(3)]


def layer(fn, t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    fn(Ctx(surf), t); surf.flush()
    return np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)


def comp(dst, arr, grain):
    a = arr[..., 3].astype(np.float32) * (grain / 255)
    col = arr[..., 2::-1].astype(np.float32) * (grain / 255)[..., None]   # BGRA premultiplied -> RGB
    return dst * (1 - a[..., None]) + col


def draw(t):
    lib.BOIL[0] = int(t * 8); lib.BOIL[1] = t
    g = lib.BOIL[0] % 3
    sl = layer(scenes.render_scene, t)
    out = comp(PAPER, sl, GRAINS[g])
    if POST[0] == 'glow':
        im = Image.fromarray(sl[..., 2::-1].copy()).resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
        out = out + np.asarray(im.resize((W, H), Image.BILINEAR), np.float32) / 255 * 0.9
    if POST[0] != 'pixel':
        out = comp(out, layer(scenes.render_ui, t), GRAINS_UI[g])
    if POST[0] == 'pixel':
        im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).resize((W // 6, H // 6), Image.BOX)
        q = np.asarray(im, np.float32) / 255
        d = ((q[:, :, None, :] - PICO[None, None]) ** 2).sum(-1)
        small = (PICO[d.argmin(-1)] * 255).astype(np.uint8)
        out = np.asarray(Image.fromarray(small).resize((W, H), Image.NEAREST), np.float32) / 255
        out = comp(out, layer(scenes.render_ui, t), ONES)
    if POST[0] == 'riso':
        rng = np.random.default_rng(lib.BOIL[0])
        q = np.clip(out, 0, 1) + (rng.random((H, W, 1), np.float32) - 0.5) * 0.18
        d = ((q[:, :, None, :] - RISO[None, None]) ** 2).sum(-1)
        out = RISO[d.argmin(-1)]
    out = comp(out, layer(scenes.render_brand, t), ONES)   # official logos: no texture, no colour effects
    out *= scenes.fade(t)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


BLACK = np.zeros((H, W, 3), np.float32)


def glow(out, arr, k):
    im = Image.fromarray(arr[..., 2::-1].copy()).resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
    return out + np.asarray(im.resize((W, H), Image.BILINEAR), np.float32) / 255 * k


def glitch(out, amt, t):
    if amt < 0.02: return out
    rng = np.random.default_rng(int(t * 30))
    sh = int(6 + amt * 40)
    o = out.copy()
    o[..., 0] = np.roll(out[..., 0], sh, 1); o[..., 2] = np.roll(out[..., 2], -sh, 1)
    for _ in range(int(amt * 8)):   # horizontal tear bands
        y = rng.integers(0, H - 60); hh = rng.integers(8, 60)
        o[y:y + hh] = np.roll(o[y:y + hh], rng.integers(-120, 120), 1)
    o += (rng.random((H, W, 1), np.float32) - 0.5) * 0.12 * amt
    return o


SCAN = (1 - 0.08 * ((np.arange(H) % 4) < 2)).astype(np.float32)[:, None, None]


def draw_concept(key, t):
    import concepts
    cfg = concepts.CONCEPTS[key]
    lib.BOIL[0] = int(t * 8)
    lib.STYLE.clear(); lib.STYLE.update(BASE_STYLE); lib.STYLE.update(concepts.CRISP); lib.STYLE['dark'] = True
    lib.C['ink'] = BASE_INK
    if key.startswith('C_'): lib.STYLE['bug_x'] = W - 366
    sl = layer(cfg['fn'], t)
    out = comp(BLACK, sl, ONES)
    post = cfg.get('post')
    if post == 'glow': out = glow(out, sl, 0.9)
    if post == 'glow_soft': out = glow(out, sl, 0.35)
    if post == 'glitch': out = glitch(out, concepts.glitch_amount(t), t) * SCAN
    out = comp(out, layer(scenes.render_brand, t), ONES)
    out *= scenes.fade(t)
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def worker(w, f0, f1, fps):
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-tune', 'grain',
                           '-pix_fmt', 'yuv420p', f'{OUT}/seg{w:02d}.mp4'], stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        ff.stdin.write(draw(f / fps).tobytes())
        if w == 0 and (f - f0) % 120 == 0:
            print(f'w0 {f - f0}/{f1 - f0} {time.time() - t0:.0f}s', flush=True)
    ff.stdin.close(); ff.wait()


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1:2] == ['conceptboard']:
        from PIL import ImageDraw, ImageFont
        import concepts
        times = [19.0, 46.5, 80.2]
        fb = ImageFont.truetype(os.path.expanduser('~/.fonts/CabinSketch-Bold.ttf'), 64)
        fs = ImageFont.truetype(os.path.expanduser('~/.fonts/PatrickHand-Regular.ttf'), 40)
        rows = []
        for key, st in concepts.CONCEPTS.items():
            frames = [Image.fromarray(draw_concept(key, t)) for t in times]
            strip = Image.new('RGB', (2880, 640), (250, 248, 240))
            for i, f in enumerate(frames): strip.paste(f.resize((960, 540), Image.LANCZOS), (i * 960, 100))
            d = ImageDraw.Draw(strip)
            d.text((30, 14), st['title'], font=fb, fill=(20, 20, 20)); d.text((1150, 34), st['sub'], font=fs, fill=(90, 90, 90))
            strip.save(f'{OUT}/concept_{key}_strip.jpg', quality=88); rows.append(strip); print('concept', key, flush=True)
        board = Image.new('RGB', (2880, 640 * len(rows)))
        for i, r in enumerate(rows): board.paste(r, (0, i * 640))
        board.resize((1920, 640 * len(rows) * 2 // 3), Image.LANCZOS).save(f'{OUT}/concept_board.jpg', quality=85)
        sys.exit()
    if sys.argv[1:2] in (['styleboard'], ['charboard']):
        SET = STYLES if sys.argv[1] == 'styleboard' else CHAR_STYLES
        prefix = 'style' if sys.argv[1] == 'styleboard' else 'char'
        from PIL import ImageDraw, ImageFont
        times = [19.0, 46.5, 80.2]
        fb = ImageFont.truetype(os.path.expanduser('~/.fonts/CabinSketch-Bold.ttf'), 64)
        fs = ImageFont.truetype(os.path.expanduser('~/.fonts/PatrickHand-Regular.ttf'), 40)
        rows = []
        for key, st in SET.items():
            use_style(key)
            frames = [Image.fromarray(draw(t)) for t in times]
            frames[0].save(f'{OUT}/{prefix}_{key}_hero.png')
            strip = Image.new('RGB', (2880, 640), (250, 248, 240))
            for i, f in enumerate(frames): strip.paste(f.resize((960, 540), Image.LANCZOS), (i * 960, 100))
            d = ImageDraw.Draw(strip)
            d.text((30, 14), st['title'], font=fb, fill=(20, 20, 20)); d.text((1100, 34), st['sub'], font=fs, fill=(90, 90, 90))
            strip.save(f'{OUT}/{prefix}_{key}_strip.jpg', quality=88)
            rows.append(strip); print('style', key, flush=True)
        board = Image.new('RGB', (2880, 640 * len(rows)))
        for i, r in enumerate(rows): board.paste(r, (0, i * 640))
        board.resize((1920, 640 * len(rows) * 2 // 3), Image.LANCZOS).save(f'{OUT}/{prefix}_board.jpg', quality=85)
        sys.exit()
    if sys.argv[1:2] == ['stills']:
        use_style('MAIN')
        for a in sys.argv[2:]:
            Image.fromarray(draw(float(a))).save(f'{OUT}/still_{float(a):07.2f}.png')
        sys.exit()
    use_style('MAIN')
    fps = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    total = int(scenes.DUR * fps)
    per = -(-total // nw)
    ps = [Process(target=worker, args=(w, w * per, min(total, (w + 1) * per), fps)) for w in range(nw)]
    [p.start() for p in ps]; [p.join() for p in ps]
    with open(f'{OUT}/list.txt', 'w') as fh:
        fh.write('\n'.join(f"file 'seg{w:02d}.mp4'" for w in range(nw)))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-i', 'audio/song.mp3',
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart',
                    'DramayBaaz_MusicVideo.mp4'], check=True)
    print('done', total, 'frames')
