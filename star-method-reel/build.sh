#!/bin/sh
# Rebuild "STAR in Four Stamps" (1080x1920 Reel) from scratch: sh build.sh
set -e
LIB=${LIB:-/root/lemo-opuscar}
export LIB
HERE=$(cd "$(dirname "$0")" && pwd)
[ -f "$LIB/core/render/video.mjs" ] || { echo "set LIB to the Lemo-Opuscar library folder"; exit 1; }
PY="$LIB/.venv/bin/python"; SZ=1080x1920
cd "$LIB"
$PY core/tts/tts.py "$HERE/lines.json" "$HERE/voices"                          # 1. narration (Kokoro af_heart)
$PY core/tts/asr_check.py "$HERE/lines.json" "$HERE/voices"                    # 2. every line must transcribe back
$PY "$HERE/music/score.py"                                                     # 3. original cool-jazz score
node core/render/events.mjs "$HERE" --size $SZ                                 # 4. picture events -> events.json
$PY "$HERE/mix.py"                                                             # 5. foley + voice + ducking + silences
node core/render/readcheck.mjs "$HERE" --size $SZ                              # 6. reading time of every on-screen text
node "$HERE/tools_cues.mjs" > "$HERE/out/cues.json" && $PY core/render/srt.py "$HERE/out/cues.json" "$HERE/star-method-reel.srt"
node core/render/video.mjs "$HERE" --size $SZ --fps 24 --workers 4 --out "$HERE/out/video.mp4"
sh core/render/mux.sh "$HERE/out/video.mp4" "$HERE/out/mix.wav" "$HERE/star-method-reel.mp4" 24 3
node core/render/still.mjs "$HERE" 45.5 --size $SZ --q nosubs=1 --prefix poster_ --out "$HERE/out" && cp "$HERE/out/poster_45.5.jpg" "$HERE/poster.jpg"
