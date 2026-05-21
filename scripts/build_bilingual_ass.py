#!/usr/bin/env python3
"""Build a styled two-tier bilingual .ass from lines.json + a ZH text file.

Layout: Chinese on top (white, larger), English below (light grey, smaller),
bottom-centre with a black outline. Works on any player because it is meant to
be HARD-BURNED into the pixels (subtitles you cannot toggle off).

IRON RULE: the ZH file MUST have exactly one line per lines.json entry. The
script aborts on mismatch — never silently truncates or pads, because a single
off-by-one shifts every subsequent subtitle out of sync. Run verify_align.py
first if unsure.

Usage:
  python3 build_bilingual_ass.py lines.json zh.txt out.ass
      [--zh-size 44] [--en-size 30] [--font "PingFang SC"] [--margin 46]

Then hard-burn:
  ffmpeg -y -i in.mp4 -vf "ass=out.ass" -c:v libx264 -preset fast -crf 22 \
      -c:a copy -sn out_bilingual.mp4
"""
import argparse
import json


def ass_ts(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec - h * 3600 - m * 60
    cs = int(round((s - int(s)) * 100))
    si = int(s)
    if cs == 100:
        cs, si = 0, si + 1
    return f"{h:d}:{m:02d}:{si:02d}.{cs:02d}"


def esc(t):
    # ASS treats { } as override-tag delimiters; neutralise any literal braces.
    return t.replace("\\", "\\\\").replace("{", "(").replace("}", ")").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lines_json")
    ap.add_argument("zh_txt")
    ap.add_argument("out_ass")
    ap.add_argument("--zh-size", type=int, default=44)
    ap.add_argument("--en-size", type=int, default=30)
    ap.add_argument("--font", default="PingFang SC")
    ap.add_argument("--margin", type=int, default=46)
    a = ap.parse_args()

    lines = json.load(open(a.lines_json))
    zh = [l for l in open(a.zh_txt, encoding="utf-8").read().splitlines() if l != ""]
    if len(lines) != len(zh):
        raise SystemExit(
            f"ABORT: lines.json has {len(lines)} entries but {a.zh_txt} has "
            f"{len(zh)} non-empty lines. They must match exactly. "
            f"Run verify_align.py to locate the divergence."
        )

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{a.font},{a.zh_size},&H00FFFFFF,&H000000FF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,{a.margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    en_tag = r"{\fs%d\c&HCCCCCC&}" % a.en_size  # English: smaller + light grey

    with open(a.out_ass, "w", encoding="utf-8") as f:
        f.write(header)
        for c, z in zip(lines, zh):
            text = esc(z) + r"\N" + en_tag + esc(c["en"])
            f.write(
                f"Dialogue: 0,{ass_ts(c['start'])},{ass_ts(c['end'])},"
                f"Default,,0,0,0,,{text}\n"
            )
    print(f"wrote {len(lines)} bilingual cues to {a.out_ass}")


if __name__ == "__main__":
    main()
