#!/usr/bin/env python3
"""Extract phrase-level cues from a YouTube auto-caption .vtt.

CRITICAL: YouTube rolling-caption VTT has decorative " " (single-space) lines
inside cues as placeholders for the second text slot. A naive parser that uses
line.strip() as the cue-text terminator will skip the first growing cue
entirely, shifting all phrase start times by 2-3 seconds. The loop condition
here uses `lines[i] != ""` — matching only truly empty lines.

Each phrase's start = earliest cue start where its text first appears.
Each phrase's end   = latest cue end where its text still appears.

Output: JSON {count, items: [{start, end, text}]} to stdout.

Usage: python3 extract_phrases.py path/to/captions.vtt > phrases.json
"""
import html
import re
import sys
import json

TAG_RE = re.compile(r"<[^>]+>")
TS_RE = re.compile(r"^(\d\d:\d\d:\d\d\.\d\d\d)\s+-->\s+(\d\d:\d\d:\d\d\.\d\d\d)")
WS_RE = re.compile(r"\s+")


def strip_tags(line: str) -> str:
    out = html.unescape(TAG_RE.sub("", line))
    return WS_RE.sub(" ", out).strip()


def parse(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    cues = []
    i = 0
    while i < len(lines):
        m = TS_RE.match(lines[i])
        if not m:
            i += 1
            continue
        start, end = m.group(1), m.group(2)
        i += 1
        texts = []
        while i < len(lines) and lines[i] != "" and not TS_RE.match(lines[i]):
            t = strip_tags(lines[i])
            if t:
                texts.append(t)
            i += 1
        if texts:
            cues.append((start, end, texts))
    return cues


def extract(cues):
    phrases, order = {}, []
    for start, end, texts in cues:
        for t in texts:
            if t not in phrases:
                phrases[t] = {"start": start, "end": end}
                order.append(t)
            else:
                phrases[t]["end"] = end
    return [{"start": phrases[t]["start"], "end": phrases[t]["end"], "text": t}
            for t in order]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: extract_phrases.py captions.vtt > phrases.json")
    phrases = extract(parse(sys.argv[1]))
    print(json.dumps({"count": len(phrases), "items": phrases}, ensure_ascii=False))
