"""Soundtrack: the client's voiceover (edited), a ducked music bed, and stamp thuds.

    python3 vo/build_audio.py [music_db]

- voice:  vo/voiceover_edit.wav, high-passed at 70 Hz and normalised to -16 LUFS.
          It is a real recording, so no TTS-style EQ or heavy compression.
- music:  music/bed.wav (scripts/score.py), set `music_db` under the voice, eased down
          ~5 dB across the film to offset the bed's own build, swelled ~8 dB once the voice
          ends (end screen) and faded over the last 2.5 s, and sidechain-ducked a further ~6 dB while the voice speaks.
- sfx:    a soft thud on every stamp, synthesised here so nothing is downloaded.
          (Transition whooshes were removed at the client's request.)
Writes public/audio/mix.wav.
"""
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
music_db = float(sys.argv[1]) if len(sys.argv) > 1 else -14

ts = (ROOT / "src/shared/timing.ts").read_text()
block = lambda name: ts.split(f"export const {name} = {{")[1].split("} as const")[0]
durs = [int(m.group(2)) for m in re.finditer(r"^\s+(\w+): (\d+),", block("D"), re.M)]
names = [m.group(1) for m in re.finditer(r"^\s+(\w+): (\d+),", block("D"), re.M)]
cues = {m.group(1): int(m.group(2)) for m in re.finditer(r'"([^"]+)": (-?\d+),', block("CUE"))}
fps = int(re.search(r"FPS = (\d+)", ts).group(1))
total = int(re.search(r"SEQUENCE_DURATION = (\d+)", ts).group(1)) / fps
starts = np.cumsum([0] + durs[:-1])
start_of = dict(zip(names, starts))

rng = np.random.default_rng(3)
out = np.zeros((int(total * SR) + SR, 2))


def place(sig: np.ndarray, t: float, gain: float, pan: float = 0.0):
    i = int(t * SR)
    seg = out[i:i + len(sig)]
    n = len(seg)
    seg[:, 0] += sig[:n] * gain * (1 - max(0, pan))
    seg[:, 1] += sig[:n] * gain * (1 + min(0, pan))


def swish(dur=0.42):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n)
    # sweep a resonant band-pass from low to high: paper sliding past
    f = np.linspace(500, 3800, n)
    y = np.zeros(n)
    s1 = s2 = 0.0
    for k in range(n):
        w = 2 * np.pi * f[k] / SR
        q = 2.2
        a = np.sin(w) / (2 * q)
        # state-variable-ish one-pole pair, cheap and smooth
        s1 += a * (noise[k] - s1 - q * 0.1 * s2)
        s2 += a * s1
        y[k] = s1
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    y = y * env
    return y / (np.abs(y).max() + 1e-9)


def thud(dur=0.32):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
    click = rng.normal(0, 1, n) * np.exp(-t * 90) * 0.5
    y = body + click
    return y / np.abs(y).max()


# no transition whooshes (client: they repeat too often); stamps keep their thud
th = thud()
for key in [k for k in cues if ".stamp" in k]:  # every stamp cue gets a thud
    sc = key.split(".")[0]
    place(th, (start_of[sc] + cues[key]) / fps + 0.05, 0.42)

sfx = ROOT / "music/sfx.wav"
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
with wave.open(str(sfx), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

import json
vo_end = json.loads((ROOT / "vo/words.json").read_text())["words"][-1]["e"] + 0.3  # music swells for the end screen
mix = ROOT / "public/audio/mix.wav"
graph = f"""
[0:a]highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11,aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,asplit=2[voice][keyraw];
[keyraw]apad[key];
[1:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,volume={music_db}dB,volume='1-0.44*t/{total:.1f}':eval=frame,volume='if(lt(t,{vo_end:.2f}),1,min(2.5,1+1.5*(t-{vo_end:.2f})/1.5))':eval=frame,afade=t=out:st={total-2.5:.2f}:d=2.5[bed];
[bed][key]sidechaincompress=threshold=0.03:ratio=8:attack=18:release=420:makeup=1[ducked];
[2:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo[fx];
[voice][ducked][fx]amix=inputs=3:duration=longest:dropout_transition=0:normalize=0,alimiter=limit=0.94,atrim=0:{total:.3f}
"""
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(ROOT / "vo/voiceover_edit.wav"), "-i", str(ROOT / "music/bed.wav"), "-i", str(sfx),
                "-filter_complex", graph, "-ar", str(SR), "-ac", "2", str(mix)], check=True)
print(f"wrote {mix.relative_to(ROOT)} ({total:.1f}s, music {music_db} dB)")
