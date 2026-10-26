"""Short motion previews of each concept with the song: python3 preview.py start dur key1 key2 ..."""
import sys, subprocess
from multiprocessing import Pool
import render, concepts

def clip(args):
    key, t0, dur = args
    fps = 24; out = f'build/preview_{key}.mp4'
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(fps), '-i', '-',
                           '-ss', str(t0), '-t', str(dur), '-i', 'audio/song.mp3', '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '22',
                           '-preset', 'medium', '-pix_fmt', 'yuv420p', '-vf', 'scale=1280:720', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                           '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(dur * fps)):
        ff.stdin.write(render.draw_concept(key, t0 + f / fps).tobytes())
    ff.stdin.close(); ff.wait(); return out

if __name__ == '__main__':
    t0, dur = float(sys.argv[1]), float(sys.argv[2])
    keys = sys.argv[3:] or list(concepts.CONCEPTS)
    with Pool(4) as p:
        for o in p.imap(clip, [(k, t0, dur) for k in keys]): print(o, flush=True)
