#!/usr/bin/env bash
# Render each scene at its fullest frame, collect FIT overflow errors from the
# in-page checker (src/scenes/kit.tsx FitCheck) and build a contact sheet.
# Exit status 1 if anything spills out of its box. Run before every push.
set -uo pipefail
cd "$(dirname "$0")/.."
FRAMES="${FRAMES:-165 345 479 665 975 1185 1360 1645 1840}"
mkdir -p out/qc
: > out/qc/fit.log
for f in $FRAMES; do
  npx remotion still src/index.ts GameStopSequence "out/qc/f$f.png" --frame="$f" --log=info 2>&1 \
    | grep -o 'FIT frame=.*' | sort -u >> out/qc/fit.log
done
inputs=(); filt=""; i=0
for f in $FRAMES; do inputs+=(-i "out/qc/f$f.png"); filt+="[$i:v]scale=640:-1[v$i];"; i=$((i+1)); done
rows=""; for r in 0 1 2; do filt+="[v$((r*3))][v$((r*3+1))][v$((r*3+2))]hstack=inputs=3[r$r];"; rows+="[r$r]"; done
ffmpeg -y -v error "${inputs[@]}" -filter_complex "${filt}${rows}vstack=inputs=3" out/qc/sheet.png
if [ -s out/qc/fit.log ]; then echo "FIT PROBLEMS:"; cat out/qc/fit.log; exit 1; fi
echo "fit check: clean ($(echo $FRAMES | wc -w) frames)"
