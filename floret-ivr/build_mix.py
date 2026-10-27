"""Assemble the Floret Capitals IVR greeting: voice clips + pauses + soft piano bed.

Usage: python3 build_mix.py <clips_dir> <out_dir>
"""
import subprocess, sys, wave
import numpy as np

SR = 24000
clips_dir, out_dir = sys.argv[1], sys.argv[2]


def load(name):
    """Decode a clip to mono float32 and trim leading/trailing silence."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", f"{clips_dir}/{name}.mp3",
         "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    loud = np.where(np.abs(x) > 0.01)[0]
    pad = int(0.03 * SR)
    return x[max(loud[0] - pad, 0): loud[-1] + pad]


def gap(sec):
    return ("gap", sec)


# (item, ...) timeline. Pauses follow the script.
TIMELINE = [
    gap(1.0),                       # music intro
    "01_en_greeting", gap(1.0),
    "02_ur_greeting", gap(1.5),
    "03_en_menu1", gap(0.45), "04_en_menu2", gap(1.0),
    "05_ur_menu1", gap(0.45), "06_ur_menu2", gap(2.0),
    "07_en_hold", gap(1.0),
    "08_ur_hold",
]
TAIL = 4.0  # music continues after last line

voice_parts, speech_sec = [], 0.0
for item in TIMELINE:
    if isinstance(item, tuple):
        voice_parts.append(np.zeros(int(item[1] * SR), np.float32))
    else:
        clip = load(item)
        speech_sec += len(clip) / SR
        voice_parts.append(clip)
voice_parts.append(np.zeros(int(TAIL * SR), np.float32))
voice = np.concatenate(voice_parts)
voice /= np.max(np.abs(voice)) / 0.89          # normalise voice to about -1 dBFS
N = len(voice)
t = np.arange(N) / SR

# ---- soft piano bed -------------------------------------------------------
def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def piano_note(freq, dur, vel):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    tone = sum(a * np.sin(2 * np.pi * freq * k * tt) * np.exp(-tt * (1.2 + 1.6 * k))
               for k, a in [(1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)])
    attack = np.minimum(tt / 0.012, 1.0)
    return (tone * attack * vel).astype(np.float32)

# Fmaj9 - Dm9 - Bbmaj7 - Csus (warm, calm, unresolved loop), 4 s per chord
CHORDS = [
    (41, [60, 64, 67, 69]),
    (38, [60, 62, 65, 69]),
    (46, [58, 62, 65, 69]),
    (36, [58, 60, 65, 67]),
]
BAR = 4.0
music = np.zeros(N + SR * 6, np.float32)
bar, start = 0, 0.0
while start < N / SR:
    bass, notes = CHORDS[bar % len(CHORDS)]
    s = int(start * SR)
    b = piano_note(midi_hz(bass), 4.5, 0.5)
    music[s:s + len(b)] += b
    # gentle broken-chord arpeggio: one note every half beat
    for i, m in enumerate(notes + notes[1:3][::-1]):
        ns = s + int(i * 0.5 * SR)
        p = piano_note(midi_hz(m), 3.5, 0.28)
        music[ns:ns + len(p)] += p
    # soft sustained pad underneath
    pad_n = int(BAR * SR)
    pt = np.arange(pad_n) / SR
    pad_env = np.sin(np.pi * pt / BAR) ** 2
    pad = sum(np.sin(2 * np.pi * midi_hz(m) * pt) for m in notes[:3]) * 0.05 * pad_env
    music[s:s + pad_n] += pad.astype(np.float32)
    start += BAR
    bar += 1
music = music[:N]

# simple low-pass smoothing for a mellow tone
kernel = np.ones(6, np.float32) / 6
music = np.convolve(music, kernel, mode="same")
music /= np.max(np.abs(music))

# Ducking: music sits low (about -24 dB) under speech, a little higher (about -17 dB) in gaps.
env = np.abs(voice)
win = int(0.25 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
speaking = np.clip(env / 0.02, 0, 1)
smooth = np.convolve(speaking, np.ones(int(0.3 * SR)) / int(0.3 * SR), mode="same")
music_gain = 10 ** ((-17 - 7 * smooth) / 20)

# Fade in over the 1 s intro, fade out over the tail.
fade = np.ones(N)
fi = int(0.6 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fo = int(3.0 * SR)
fade[-fo:] = np.linspace(1, 0, fo) ** 1.5

mix = voice + music * music_gain * fade
mix /= max(1.0, np.max(np.abs(mix)) / 0.95)

master = f"{out_dir}/floret_ivr_master_24k.wav"
with wave.open(master, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

# Telephone version: band-limit to 300-3400 Hz, 8 kHz mono 16-bit PCM.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", master,
                "-af", "highpass=f=250,lowpass=f=3500,loudnorm=I=-18:TP=-2:LRA=11",
                "-ar", "8000", "-ac", "1", "-c:a", "pcm_s16le",
                f"{out_dir}/floret_ivr_8k_mono.wav"], check=True)
# Review copy: full-band MP3.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", master,
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100",
                "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k",
                f"{out_dir}/floret_ivr_review.mp3"], check=True)

print(f"speech: {speech_sec:.1f}s  total: {N / SR:.1f}s")
