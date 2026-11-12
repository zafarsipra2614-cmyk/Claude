"""Soundtrack: the client's voiceover (edited), a ducked music bed, and foley on cues.

    python3 vo/build_audio.py [music_db]

- voice:  vo/voiceover_edit.wav, high-passed at 70 Hz and normalised to -16 LUFS.
          It is a real recording, so no TTS-style EQ or heavy compression.
- music:  timeline.json "bed":
            absent            music/bed.wav from scripts/score.py (documentary drone)
            "<preset>"        a papercut-explainer bed, e.g. "marimba-F-108" (lighter,
                              for consumer/curiosity topics); presets in
                              $PAPERCUT_LIB/audio/beds/, catalogued in audio/CATALOG.md
          set `music_db` under the voice, eased down ~5 dB across the film to offset a
          bed's own build, swelled ~8 dB once the voice ends (end screen), faded over the
          last 2.5 s, and sidechain-ducked a further ~6 dB while the voice speaks.
- foley:  papercut-explainer's synthesised SFX library (79 named sounds, no files to
          license), placed on word cues. timeline.json "sfx" maps cue -> sound:
            "sfx": {"hook.b": "pop", "dresstest.jump": "coin", "origin.year": "stamp"}
          Every `*.stamp*` cue gets "stamp" unless mapped otherwise. Keep foley sparse:
          a sound on the landings that matter, never on every transition.
          Rendered by vo/render_foley.mjs (papercut's engine in headless Chromium; needs
          puppeteer-core and CHROME_PATH or a Playwright Chromium). Without the papercut
          library or a browser it falls back to a synthesised thud on stamp cues only.
Writes public/audio/mix.wav.
"""
import json
import os
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
start_of = dict(zip(names, np.cumsum([0] + durs[:-1])))
timeline = json.loads((ROOT / "timeline.json").read_text()) if (ROOT / "timeline.json").exists() else {}

# --- foley plan: cue -> sound
plan = {k: "stamp" for k in cues if ".stamp" in k}
plan.update(timeline.get("sfx", {}))
unknown = [k for k in plan if k not in cues]
if unknown:
    raise SystemExit(f"timeline.json sfx names unknown cues: {unknown}")
at_s = lambda key: (start_of[key.split(".")[0]] + cues[key]) / fps


def papercut_lib() -> Path | None:
    """$PAPERCUT_LIB, the line in ~/.config/papercut-explainer/config.env, or the vendored copy above the project."""
    cand = [os.environ.get("PAPERCUT_LIB")]
    cfg = Path.home() / ".config/papercut-explainer/config.env"
    if cfg.exists():
        cand += [l.split("=", 1)[1].strip() for l in cfg.read_text().splitlines() if l.startswith("PAPERCUT_LIB=")]
    for d in [ROOT, *ROOT.parents]:
        cand.append(str(d / ".claude/vendor/papercut-explainer/library"))
    for c in cand:
        if c and (Path(c) / "audio/engine.js").exists():
            return Path(c)
    return None


def chrome() -> str | None:
    for c in [os.environ.get("CHROME_PATH"), *sorted(map(str, Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome")), reverse=True),
              "/usr/bin/chromium", "/usr/bin/google-chrome"]:
        if c and Path(c).exists():
            return c
    return None


def render_papercut(lib: Path, bed: str | None) -> tuple[Path | None, Path] | None:
    """Render foley (and the papercut bed) offline with papercut's Web Audio engine."""
    browser = chrome()
    if not browser:
        print("  papercut audio: no Chromium found (set CHROME_PATH); falling back")
        return None
    cue_file = ROOT / "out/sfx_cues.json"
    cue_file.parent.mkdir(exist_ok=True)
    cue_file.write_text(json.dumps({"dur": round(total, 3), "cues": [{"t": round(at_s(k), 3), "type": v} for k, v in sorted(plan.items(), key=lambda kv: at_s(kv[0]))]}))
    out_dir = ROOT / "music/papercut"
    # a papercut bed takes minutes to render for a long film: reuse it while the preset and length are unchanged
    key_file, key = out_dir / "bed.key", f"{bed}|{total:.3f}"
    bed_cached = bool(bed) and (out_dir / "music.wav").exists() and key_file.exists() and key_file.read_text() == key
    render_bed = bool(bed) and not bed_cached
    r = subprocess.run(["node", str(ROOT / "vo/render_foley.mjs"), str(lib), str(cue_file), str(out_dir), *([bed] if render_bed else [])],
                       cwd=ROOT, env={**os.environ, "CHROME_PATH": browser}, capture_output=True, text=True)
    if r.returncode != 0:
        err = [l for l in (r.stderr or r.stdout).strip().splitlines() if l.strip() and not l.strip().startswith("at ")]
        print("  papercut audio failed; falling back:\n    " + "\n    ".join(err[:6]))
        return None
    print("  papercut audio:", r.stdout.strip().splitlines()[-1] + (f" (bed {bed} reused from cache)" if bed_cached else ""))
    if render_bed:
        key_file.write_text(key)
    # place each sound's clip at its cue times
    out = np.zeros((int(total * SR) + 4 * SR, 2))
    clips = {}
    for key, name in plan.items():
        if name not in clips:
            with wave.open(str(out_dir / f"sfx_{name}.wav")) as w:
                ch, sr = w.getnchannels(), w.getframerate()
                a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
                a = a.reshape(-1, ch) if ch > 1 else np.repeat(a[:, None], 2, axis=1)
                if sr != SR:  # resample by linear interpolation (clips are short)
                    x = np.arange(0, len(a), sr / SR)
                    a = np.stack([np.interp(x, np.arange(len(a)), a[:, c]) for c in range(2)], axis=1)
                clips[name] = a[:, :2]
        a = clips[name]
        i = int(at_s(key) * SR)
        seg = out[i:i + len(a)]
        seg += a[: len(seg)]
    fx = out_dir / "fx.wav"
    with wave.open(str(fx), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    return (out_dir / "music.wav" if bed else None), fx


def synth_thuds() -> Path:
    """Fallback: a synthesised thud on every stamp cue."""
    rng = np.random.default_rng(3)
    out = np.zeros((int(total * SR) + SR, 2))
    n = int(0.32 * SR)
    t = np.arange(n) / SR
    th = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 14) + rng.normal(0, 1, n) * np.exp(-t * 90) * 0.5
    th /= np.abs(th).max()
    for k in [k for k in cues if ".stamp" in k]:
        i = int((at_s(k) + 0.05) * SR)
        seg = out[i:i + n]
        seg += th[: len(seg), None] * 0.42
    path = ROOT / "music/sfx.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    return path


bed_preset = timeline.get("bed")
lib = papercut_lib()
rendered = render_papercut(lib, bed_preset) if lib else None
if not lib:
    print("  papercut library not found; foley falls back to stamp thuds")
fx = rendered[1] if rendered else synth_thuds()
if bed_preset and not (rendered and rendered[0]):
    print(f"  papercut bed {bed_preset} unavailable; using music/bed.wav")
    bed_preset = None
bed = rendered[0] if (rendered and rendered[0]) else ROOT / "music/bed.wav"
if not bed.exists():
    raise SystemExit(f"no music bed at {bed.relative_to(ROOT)}: run scripts/score.py, or set timeline.json \"bed\" to a papercut preset")

vo_end = json.loads((ROOT / "vo/words.json").read_text())["words"][-1]["e"] + 0.3  # music swells for the end screen
mix = ROOT / "public/audio/mix.wav"
graph = f"""
[0:a]highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11,aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,asplit=2[voice][keyraw];
[keyraw]apad[key];
[1:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,apad,atrim=0:{total:.3f},volume={music_db}dB,volume='1-0.44*t/{total:.1f}':eval=frame,volume='if(lt(t,{vo_end:.2f}),1,min(2.5,1+1.5*(t-{vo_end:.2f})/1.5))':eval=frame,afade=t=out:st={total-2.5:.2f}:d=2.5[bed];
[bed][key]sidechaincompress=threshold=0.03:ratio=8:attack=18:release=420:makeup=1[ducked];
[2:a]aformat=sample_fmts=fltp:sample_rates={SR}:channel_layouts=stereo,volume=-4dB[fx];
[voice][ducked][fx]amix=inputs=3:duration=longest:dropout_transition=0:normalize=0,alimiter=limit=0.94,atrim=0:{total:.3f}
"""
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(ROOT / "vo/voiceover_edit.wav"), "-i", str(bed), "-i", str(fx),
                "-filter_complex", graph, "-ar", str(SR), "-ac", "2", str(mix)], check=True)
print(f"wrote {mix.relative_to(ROOT)} ({total:.1f}s, music {music_db} dB, bed {bed_preset or 'score.py'}, {len(plan)} foley cues"
      f"{' via papercut' if rendered else ' (synth fallback)'})")
