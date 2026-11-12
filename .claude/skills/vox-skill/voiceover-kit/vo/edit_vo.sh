#!/usr/bin/env bash
# Client edits to the supplied voiceover, applied losslessly; writes vo/voiceover_edit.wav.
# Find cut points with an energy profile (see references/voiceover-mode.md) and cut
# inside silence, with 10 ms fades. With no edits, this just converts to WAV.
#
# Example (remove 182.20–182.86 s):
#   ffmpeg -y -v error -i voiceover.mp3 -filter_complex "
#     [0:a]atrim=0:182.20,asetpts=PTS-STARTPTS,afade=t=out:st=182.19:d=0.01[a];
#     [0:a]atrim=start=182.86,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.01[b];
#     [a][b]concat=n=2:v=0:a=1" -ar 44100 -ac 1 voiceover_edit.wav
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -y -v error -i voiceover.mp3 -ar 44100 -ac 1 voiceover_edit.wav
echo "wrote vo/voiceover_edit.wav ($(ffprobe -v error -show_entries format=duration -of csv=p=0 voiceover_edit.wav)s)"
