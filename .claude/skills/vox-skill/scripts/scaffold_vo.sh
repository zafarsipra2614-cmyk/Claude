#!/usr/bin/env bash
# Start a voiceover-mode film: copy voiceover-kit/ into a new project.
#   scaffold_vo.sh <project-dir> <voiceover.mp3> [script.txt] [deliverable.mp4]
# Then follow references/voiceover-mode.md from step 2.
set -euo pipefail
DIR="${1:?usage: scaffold_vo.sh <project-dir> <voiceover.mp3> [script.txt] [deliverable.mp4]}"
VO="${2:?usage: scaffold_vo.sh <project-dir> <voiceover.mp3> [script.txt] [deliverable.mp4]}"
SCRIPT="${3:-}"
OUT="${4:-film.mp4}"
KIT="$(cd "$(dirname "$0")/../voiceover-kit" && pwd)"

[ -e "$DIR/package.json" ] && { echo "refusing: $DIR already has a project"; exit 1; }
mkdir -p "$DIR"
cp -R "$KIT/." "$DIR/"
cp "$VO" "$DIR/vo/voiceover.mp3"
[ -n "$SCRIPT" ] && cp "$SCRIPT" "$DIR/script.txt"
cd "$DIR"
python3 - "$(basename "$DIR")" "$OUT" <<'PY'
import json, sys
j = json.load(open("package.json"))
j["name"], j["video"]["deliverable"] = sys.argv[1], sys.argv[2]
json.dump(j, open("package.json", "w"), indent=2)
open("package.json", "a").write("\n")
PY
# silent placeholder soundtrack so the demo scenes render before the real mix exists
ffmpeg -y -v error -f lavfi -i anullsrc=r=48000:cl=stereo -t 21 public/audio/mix.wav
echo "scaffolded $DIR (deliverable: $OUT)"
echo "next: npm install; bash vo/edit_vo.sh; python3 vo/transcribe.py vo/voiceover_edit.wav"
