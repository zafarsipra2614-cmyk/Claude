#!/bin/sh
# Join the rendered segments, add narration + music, and attach subtitles as a default soft track.
set -e
cd "$(dirname "$0")"
ffmpeg -y -loglevel error -f concat -safe 0 -i render/list.txt -c copy render/video.mp4
ffmpeg -y -loglevel error -i render/video.mp4 -i audio/mix.wav -i subtitles.srt \
  -map 0:v -map 1:a -map 2:s -c:v copy -c:a aac -b:a 192k -c:s mov_text \
  -metadata:s:s:0 language=eng -disposition:s:0 default -movflags +faststart sukuk_psx_explainer.mp4
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate -of compact sukuk_psx_explainer.mp4
