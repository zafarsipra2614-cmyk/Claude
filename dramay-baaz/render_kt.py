"""Renderer for the kinetic-typography edition.
Per frame: draw backdrop / glass-mask / foreground / logo layers with Cairo (kt.py), then composite:
backdrop -> frosted blur under glass -> foreground -> bloom -> grain + vignette -> official logo layer.
usage: python3 render_kt.py [fps] [workers]  |  python3 render_kt.py stills t1 t2 ...  |  python3 render_kt.py clip t0 dur"""
import sys, os, subprocess, time
from multiprocessing import Process
import numpy as np, cairo
from PIL import Image, ImageFilter
from lib import W, H
import kt

OUT = 'build'
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.05 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2).clip(0.55, 1)[..., None].astype(np.float32)
del yy, xx
GRAIN = [(np.random.default_rng(s).random((H, W, 1), np.float32) - 0.5) * 0.028 for s in range(4)]


class Ctx(cairo.Context):
    def scale(self, sx, sy):
        super().scale(sx if abs(sx) > 1e-3 else 1e-3, sy if abs(sy) > 1e-3 else 1e-3)


def surf():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return s, Ctx(s)


def arr(s):
    s.flush()
    return np.frombuffer(s.get_data(), np.uint8).reshape(H, W, 4)


def blur(rgb, k=4, radius=7):
    im = Image.fromarray(rgb).resize((W // k, H // k), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im.resize((W, H), Image.BILINEAR), np.float32) / 255


def over(dst, a8):
    a = a8[..., 3:4].astype(np.float32) / 255
    return dst * (1 - a) + a8[..., 2::-1].astype(np.float32) / 255


def draw(t):
    (sb, bg), (sf, fg), (sm, mk), (su, ui) = surf(), surf(), surf(), surf()
    kt.render(kt.Layers(bg, fg, mk, ui), t)
    b = arr(sb)
    brgb = b[..., 2::-1].copy()
    out = brgb.astype(np.float32) / 255
    m = arr(sm)[..., 3:4].astype(np.float32) / 255
    if m.max() > 0:
        frost = blur(brgb, 4, 9) * 0.86 + 0.13 if kt.LIGHT else blur(brgb, 4, 9) * 0.92 + 0.03
        out = out * (1 - m) + frost * m
    f = arr(sf)
    out = over(out, f)
    # bloom from bright foreground (glowing type and UI)
    fa = f[..., 3:4].astype(np.float32) / 255
    bright = (f[..., 2::-1].astype(np.float32) / 255) * fa
    bright = np.clip(bright - 0.35, 0, 1) * 1.5
    if bright.max() > 0 and not kt.LIGHT:
        out = out + blur((bright * 255).astype(np.uint8), 4, 8) * 0.55
    out = out * VIG + GRAIN[int(t * 24) % 4]
    out = over(np.clip(out, 0, 1), arr(su))
    fd = min(1.0, t / 0.5, (kt.DUR - t) / 1.2) if t < 0.5 or t > kt.DUR - 1.2 else 1.0
    return (np.clip(out * max(0.0, fd), 0, 1) * 255).astype(np.uint8)


def encode(path, frames_iter, fps, audio=None, crf=18):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-']
    if audio: cmd += ['-ss', str(audio[0]), '-t', str(audio[1]), '-i', 'audio/song.mp3', '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in frames_iter: ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()


def worker(w, f0, f1, fps):
    t0 = time.time()

    def gen():
        for f in range(f0, f1):
            if w == 0 and (f - f0) % 240 == 0: print(f'w0 {f - f0}/{f1 - f0} {time.time() - t0:.0f}s', flush=True)
            yield draw(f / fps)
    encode(f'{OUT}/kt_seg{w:02d}.mp4', gen(), fps)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1:2] == ['stills']:
        for a in sys.argv[2:]:
            Image.fromarray(draw(float(a))).save(f'{OUT}/kt_{float(a):07.2f}.png')
        sys.exit()
    if sys.argv[1:2] == ['clip']:
        t0, dur, fps = float(sys.argv[2]), float(sys.argv[3]), 24
        encode(f'{OUT}/kt_clip_{t0:g}.mp4', (draw(t0 + i / fps) for i in range(int(dur * fps))), fps, (t0, dur), 22)
        sys.exit()
    fps = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    nw = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count()
    total = int(kt.DUR * fps); per = -(-total // nw)
    ps = [Process(target=worker, args=(w, w * per, min(total, (w + 1) * per), fps)) for w in range(nw)]
    [p.start() for p in ps]; [p.join() for p in ps]
    with open(f'{OUT}/kt_list.txt', 'w') as fh:
        fh.write('\n'.join(f"file 'kt_seg{w:02d}.mp4'" for w in range(nw)))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/kt_list.txt', '-i', 'audio/song.mp3',
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart',
                    'DramayBaaz_KineticType.mp4'], check=True)
    print('done', total, 'frames')
