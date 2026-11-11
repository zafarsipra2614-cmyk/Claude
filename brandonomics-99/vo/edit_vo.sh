#!/usr/bin/env bash
# Voiceover edits requested by the client, applied losslessly to the supplied MP3.
#   - remove "Part two." before "Chapter three" (182.20–182.86 s, both edges in silence)
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -y -v error -i voiceover.mp3 -filter_complex "
  [0:a]atrim=0:182.20,asetpts=PTS-STARTPTS,afade=t=out:st=182.19:d=0.01[a];
  [0:a]atrim=start=182.86,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.01[b];
  [a][b]concat=n=2:v=0:a=1" -ar 44100 -ac 1 voiceover_edit.wav
echo "wrote vo/voiceover_edit.wav ($(ffprobe -v error -show_entries format=duration -of csv=p=0 voiceover_edit.wav)s)"
