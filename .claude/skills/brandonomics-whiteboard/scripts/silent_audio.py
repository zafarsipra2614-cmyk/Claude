#!/usr/bin/env python3
"""Captions-only videos: write a silent clip per caption line so make_audio.py can time the video.

Usage: silent_audio.py <project> [--rate 16] [--base 0.8] [--min 2.5]

Each line in script.json gets audio/<scene>_<line>.wav lasting len(text)/rate + base seconds (at least --min),
which is a comfortable reading time. A line can set its own length with "secs": 4.2 (use it to give a scene
room for its drawings). Then run make_audio.py with {"engine": "files"} in voice.json.
"""
import argparse, json, os, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("project"); ap.add_argument("--rate", type=float, default=16); ap.add_argument("--base", type=float, default=.8)
ap.add_argument("--min", type=float, default=2.5)
a = ap.parse_args()
os.makedirs(os.path.join(a.project, "audio"), exist_ok=True)
total = 0
for sc in json.load(open(os.path.join(a.project, "script.json"))):
    for i, ln in enumerate(sc["lines"]):
        d = ln.get("secs") or max(a.min, len(ln["t"]) / a.rate + a.base)
        total += d
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{d:.2f}",
                        os.path.join(a.project, "audio", f"{sc['id']}_{i}.wav")], check=True)
json.dump({"engine": "files", "trim": False}, open(os.path.join(a.project, "voice.json"), "w"))
print(f"silent caption clips written: {total:.1f}s of lines")
