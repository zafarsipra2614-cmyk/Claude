"""Burn TikTok-style captions into a video.

- 4 words per caption (never more than 5), split early at pauses or sentence ends
- White, bold, black-outlined uppercase text in the lower third
- The word being spoken sits on a red rounded box

Usage:
  python make_captions.py input.mp4 output.mp4            # transcribe with Whisper
  python make_captions.py input.mp4 output.mp4 --words words.json
      (words.json = [[start, end, "word"], ...] if you already have timings)
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import ImageFont

HERE = Path(__file__).parent
FONT_FILE = HERE / "fonts" / "Montserrat-ExtraBold.ttf"
FONT_NAME = "Montserrat ExtraBold"

WORDS_PER_CAPTION = 4
MAX_WORDS = 5
MAX_GAP = 0.6  # a pause this long (seconds) starts a new caption
RED = "&H2B2BE8&"  # ASS colours are BGR -> #E82B2B


def probe_size(path):
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:stream_side_data=rotation",
        "-of", "json", path,
    ]))["streams"][0]
    w, h = info["width"], info["height"]
    rot = [abs(int(sd.get("rotation", 0))) for sd in info.get("side_data_list", [])]
    if 90 in rot or 270 in rot:
        w, h = h, w
    return w, h


def transcribe(path, model_name):
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path, word_timestamps=True, vad_filter=True)
    return [(w.start, w.end, w.word.strip()) for s in segments for w in s.words if w.word.strip()]


def group(words):
    groups, cur = [], []
    for w in words:
        if cur and (len(cur) >= WORDS_PER_CAPTION or w[0] - cur[-1][1] > MAX_GAP):
            groups.append(cur)
            cur = []
        cur.append(w)
        if w[2][-1] in ".?!" and len(cur) >= 2:
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    # fold a lone trailing word into the previous caption if it fits
    out = []
    for g in groups:
        if out and len(g) == 1 and len(out[-1]) < MAX_WORDS and g[0][0] - out[-1][-1][1] <= MAX_GAP:
            out[-1].append(g[0])
        else:
            out.append(g)
    return out


def ts(t):
    t = max(t, 0)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def rounded_rect(w, h, r):
    """ASS vector drawing of a rounded rectangle with top-left at 0,0."""
    k = r * 0.45  # bezier handle
    return (
        f"m {r} 0 l {w - r} 0 b {w - k} 0 {w} {k} {w} {r} "
        f"l {w} {h - r} b {w} {h - k} {w - k} {h} {w - r} {h} "
        f"l {r} {h} b {k} {h} 0 {h - k} 0 {h - r} "
        f"l 0 {r} b 0 {k} {k} 0 {r} 0"
    )


def layout(words, font, max_width, space):
    """Split words into 1-2 centred lines; return [(line_words, widths)]."""
    widths = [font.getlength(w) for w in words]
    total = sum(widths) + space * (len(words) - 1)
    if total <= max_width or len(words) == 1:
        return [list(range(len(words)))], widths
    # best two-line split (most balanced)
    best = min(range(1, len(words)), key=lambda k: abs(
        (sum(widths[:k]) + space * (k - 1)) - (sum(widths[k:]) + space * (len(words) - k - 1))))
    return [list(range(best)), list(range(best, len(words)))], widths


def build_ass(groups, W, H):
    size = round(W * 0.08)
    # libass sizes a font so usWinAscent+usWinDescent == size; Pillow uses the em size
    tt = TTFont(str(FONT_FILE))
    upem, os2 = tt["head"].unitsPerEm, tt["OS/2"]
    px_per_unit = size / (os2.usWinAscent + os2.usWinDescent)
    font = ImageFont.truetype(str(FONT_FILE), round(upem * px_per_unit))
    outline = max(2, round(size * 0.08))
    space = font.getlength(" ") * 2.2
    line_h = size * 1.35
    pad_x, pad_y = size * 0.28, size * 0.2
    radius = size * 0.2
    centre_y = H * 0.70  # lower third, like the reference
    max_w = W * 0.86
    # libass lines start at usWinAscent; Pillow's start at hhea ascent
    cap_h = font.getbbox("H")[3] - font.getbbox("H")[1]
    cap_top = (os2.usWinAscent - os2.sCapHeight) * px_per_unit

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,{FONT_NAME},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,{outline},{round(size*0.04)},7,0,0,0,1
Style: Box,{FONT_NAME},{size},&H00{RED[2:-1]},&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for gi, g in enumerate(groups):
        texts = [w[2].upper() for w in g]
        lines, widths = layout(texts, font, max_w, space)
        block_top = centre_y - line_h * len(lines) / 2
        pos = {}  # word index -> (x, y_top_of_text)
        for li, idxs in enumerate(lines):
            lw = sum(widths[i] for i in idxs) + space * (len(idxs) - 1)
            x = (W - lw) / 2
            y = block_top + li * line_h
            for i in idxs:
                pos[i] = (x, y)
                x += widths[i] + space

        g_end = groups[gi + 1][0][0] if gi + 1 < len(groups) else g[-1][1] + 0.5
        g_end = min(g_end, g[-1][1] + 0.8)
        for i in range(len(g)):
            start = g[0][0] if i == 0 else g[i][0]
            end = g[i + 1][0] if i + 1 < len(g) else g_end
            if end <= start:
                continue
            t0, t1 = ts(start), ts(end)
            # red box behind the spoken word
            bx, by = pos[i]
            bw = widths[i] + 2 * pad_x
            bh = cap_h + 2 * pad_y + size * 0.12
            box_y = by + cap_top - pad_y - size * 0.06
            events.append(
                f"Dialogue: 0,{t0},{t1},Box,,0,0,0,,"
                f"{{\\pos({bx - pad_x:.1f},{box_y:.1f})\\p1\\bord0\\shad0\\c{RED}}}"
                f"{rounded_rect(round(bw), round(bh), round(radius))}{{\\p0}}"
            )
            for j, word in enumerate(texts):
                x, y = pos[j]
                events.append(
                    f"Dialogue: 1,{t0},{t1},Word,,0,0,0,,{{\\pos({x:.1f},{y:.1f})}}{word}"
                )
    return header + "\n".join(events) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--model", default="small")
    ap.add_argument("--words", help="JSON file of [start, end, word] timings (skips transcription)")
    args = ap.parse_args()

    W, H = probe_size(args.input)
    if args.words:
        words = [tuple(w) for w in json.loads(Path(args.words).read_text())]
    else:
        words = transcribe(args.input, args.model)
    if not words:
        sys.exit("No speech found.")
    ass_path = Path(args.output).with_suffix(".ass")
    ass_path.write_text(build_ass(group(words), W, H), encoding="utf-8")
    print(f"{len(words)} words -> {ass_path}")

    subprocess.check_call([
        "ffmpeg", "-y", "-loglevel", "error", "-i", args.input,
        "-vf", f"ass={ass_path}:fontsdir={FONT_FILE.parent}",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "copy", args.output,
    ])
    print(f"done -> {args.output}")


if __name__ == "__main__":
    main()
