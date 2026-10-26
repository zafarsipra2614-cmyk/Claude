"""Renderer for the kinetic-typography edition.
Per frame: draw backdrop / glass-mask / foreground / logo layers with Cairo (kt.py), then composite:
backdrop -> frosted blur under glass -> foreground -> bloom -> grain + vignette -> official logo layer.
usage: python3 render_kt.py [fps] [workers]  |  python3 render_kt.py stills t1 t2 ...  |  python3 render_kt.py clip t0 dur"""
import sys, os, subprocess, time
from multiprocessing import Process
import numpy as np, cairo
from PIL import Image, ImageFilter
from lib import W, H
import importlib
kt = importlib.import_module(os.environ.get('VIDEO', 'kt'))

OUT = 'build'
PFX = os.environ.get('VIDEO', 'kt')
SHUTTER = 1 / 120    # motion blur: each output frame blends two moments this far apart


def _bgra_surface(arr4):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    np.frombuffer(s.get_data(), np.uint8).reshape(H, W, 4)[:] = arr4
    s.mark_dirty(); return s


def _make_static():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = (0.05 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2).clip(0, 0.45)
    vig = np.zeros((H, W, 4), np.uint8); vig[..., 3] = (v * 255).astype(np.uint8)          # black, premultiplied
    grains = []
    for s in range(4):
        rng = np.random.default_rng(s)
        al = (rng.random((H, W)) * 9).astype(np.uint8); white = rng.random((H, W)) > 0.5
        g = np.zeros((H, W, 4), np.uint8); g[..., 3] = al
        for ch in range(3): g[..., ch] = np.where(white, al, 0)
        grains.append(_bgra_surface(g))
    return _bgra_surface(vig), grains


VIG_S, GRAIN_S = _make_static()


class Ctx(cairo.Context):
    def scale(self, sx, sy):
        super().scale(sx if abs(sx) > 1e-3 else 1e-3, sy if abs(sy) > 1e-3 else 1e-3)


def surf():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return s, Ctx(s)


def layers(t):
    try:
        (sb, bg), (sf, fg), (sm, mk), (su, ui) = surf(), surf(), surf(), surf()
        kt.render(kt.Layers(bg, fg, mk, ui), t)
    except cairo.Error:   # font rasteriser hiccup: redraw this frame with all type as vector paths
        kt.FORCE_PATH[0] = True
        try:
            (sb, bg), (sf, fg), (sm, mk), (su, ui) = surf(), surf(), surf(), surf()
            kt.render(kt.Layers(bg, fg, mk, ui), t)
        finally:
            kt.FORCE_PATH[0] = False
    return sb, sf, sm, su


def frost_pattern(sb):
    """Quarter-size Gaussian blur of the backdrop, scaled back up: the frosted glass."""
    sw, sh = W // 4, H // 4
    small = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
    c = cairo.Context(small); c.scale(0.25, 0.25); c.set_source_surface(sb); c.get_source().set_filter(cairo.FILTER_GOOD); c.paint()
    small.flush()
    buf = np.frombuffer(small.get_data(), np.uint8).reshape(sh, small.get_stride() // 4, 4)[:, :sw]
    blurred = np.asarray(Image.fromarray(np.ascontiguousarray(buf), 'RGBA').filter(ImageFilter.GaussianBlur(9)))
    np.frombuffer(small.get_data(), np.uint8).reshape(sh, small.get_stride() // 4, 4)[:, :sw] = blurred
    small.mark_dirty()
    pat = cairo.SurfacePattern(small); pat.set_matrix(cairo.Matrix(xx=0.25, yy=0.25)); pat.set_filter(cairo.FILTER_BILINEAR)
    return pat


def frame_surface(t):
    sb, sf, sm, su = layers(t)
    out = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(out)
    c.set_source_surface(sb); c.paint()
    c.set_source(frost_pattern(sb)); c.mask_surface(sm, 0, 0)
    if kt.LIGHT:
        c.set_source_rgba(1, 1, 1, 0.13); c.mask_surface(sm, 0, 0)
    c.set_source_surface(sf); c.paint()
    c.set_source_surface(VIG_S); c.paint()
    c.set_source_surface(GRAIN_S[int(t * 60) % 4]); c.paint()
    c.set_source_surface(su); c.paint()
    fd = min(1.0, t / 0.5, (kt.DUR - t) / 1.2)
    if fd < 1: c.set_source_rgba(0, 0, 0, 1 - max(0.0, fd)); c.paint()
    return out


def draw_surface(t, blur=True):
    if not blur: return frame_surface(t)
    a = frame_surface(t - SHUTTER / 2); b = frame_surface(t + SHUTTER / 2)
    c = cairo.Context(a); c.set_source_surface(b); c.paint_with_alpha(0.5)
    a.flush(); return a


def draw(t, blur=True):
    """RGB uint8 frame (used for stills)."""
    s = draw_surface(t, blur)
    return np.asarray(Image.frombuffer('RGBA', (W, H), bytes(s.get_data()), 'raw', 'BGRA', 0, 1).convert('RGB'))


def encode(path, frames_iter, fps, audio=None, crf=18):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-']
    if audio: cmd += ['-ss', str(audio[0]), '-t', str(audio[1]), '-i', 'audio/song.mp3', '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames_iter: ff.stdin.write(fr)
    ff.stdin.close(); ff.wait()


def worker(w, f0, f1, fps):
    t0 = time.time()

    def gen():
        for f in range(f0, f1):
            if w == 0 and (f - f0) % 240 == 0: print(f'w0 {f - f0}/{f1 - f0} {time.time() - t0:.0f}s', flush=True)
            yield bytes(draw_surface(f / fps, not os.environ.get('NOBLUR')).get_data())
    encode(f'{OUT}/{PFX}_seg{w:02d}.mp4', gen(), fps)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1:2] == ['stills']:
        for a in sys.argv[2:]:
            Image.fromarray(draw(float(a))).save(f'{OUT}/{PFX}_{float(a):07.2f}.png')
        sys.exit()
    if sys.argv[1:2] == ['clip']:
        t0, dur, fps = float(sys.argv[2]), float(sys.argv[3]), 24
        fps = int(os.environ.get('FPS', 60)); blur = not os.environ.get('NOBLUR')
        encode(f'{OUT}/{PFX}_clip_{t0:g}.mp4', (bytes(draw_surface(t0 + i / fps, blur).get_data()) for i in range(int(dur * fps))), fps, (t0, dur), 20)
        sys.exit()
    fps = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    total = int(kt.DUR * fps); per = -(-total // nw)
    ps = [Process(target=worker, args=(w, w * per, min(total, (w + 1) * per), fps)) for w in range(nw)]
    [p.start() for p in ps]; [p.join() for p in ps]
    with open(f'{OUT}/{PFX}_list.txt', 'w') as fh:
        fh.write('\n'.join(f"file '{PFX}_seg{w:02d}.mp4'" for w in range(nw)))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/{PFX}_list.txt', '-i', 'audio/song.mp3',
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart',
                    os.environ.get('OUTFILE', 'DramayBaaz_KineticType.mp4')], check=True)
    print('done', total, 'frames')
