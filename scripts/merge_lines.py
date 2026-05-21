#!/usr/bin/env python3
"""Merge phrase-level cues into readable subtitle lines.

WHY THIS EXISTS: YouTube auto-captions have almost no punctuation, so the
classic "split on sentence boundaries (.!?)" approach collapses the whole
transcript into one giant cue. Instead we merge consecutive phrases up to a
character cap, sequencing strictly by START time (rolling-caption END times
overlap and cannot be trusted). Each line's END is the next line's START.

Output: JSON list [{start, end, en}] to a file. Each `en` is <= --max-chars,
which keeps the English on at most ~2 screen lines.

Usage:
  python3 merge_lines.py phrases.json lines.json [--max-chars 95] [--gap 12]

--max-chars : hard upper bound on characters per merged line (default 95)
--gap       : if the START gap between two phrases exceeds this many seconds,
              force a line break (a real pause). Default 12 = effectively
              "only the char cap controls breaks" (good for dense talks).
              Lower it (e.g. 2.5) to break on natural pauses → more, shorter lines.
"""
import argparse
import json


def to_sec(ts):
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phrases_json")
    ap.add_argument("out_json")
    ap.add_argument("--max-chars", type=int, default=95)
    ap.add_argument("--gap", type=float, default=12.0)
    a = ap.parse_args()

    cues = json.load(open(a.phrases_json))["items"]
    items = sorted(
        ({"start": to_sec(c["start"]), "text": c["text"].strip()} for c in cues),
        key=lambda x: x["start"],
    )

    merged, cur = [], None
    for it in items:
        s, t = it["start"], it["text"]
        if not t:
            continue
        if cur is None:
            cur = {"start": s, "text": t}
            continue
        if (s - cur["start"]) > a.gap or (len(cur["text"]) + 1 + len(t)) > a.max_chars:
            merged.append(cur)
            cur = {"start": s, "text": t}
        else:
            cur["text"] += " " + t
    if cur:
        merged.append(cur)

    out = []
    for i, m in enumerate(merged):
        nxt = merged[i + 1]["start"] if i + 1 < len(merged) else m["start"] + 4.0
        end = nxt - 0.05
        if end <= m["start"]:
            end = m["start"] + 1.0
        out.append({"start": m["start"], "end": end, "en": m["text"]})

    json.dump(out, open(a.out_json, "w"), ensure_ascii=False, indent=1)
    durs = [o["end"] - o["start"] for o in out]
    chars = [len(o["en"]) for o in out]
    print(f"wrote {len(out)} lines to {a.out_json}")
    print(f"  dur  min={min(durs):.1f}s max={max(durs):.1f}s avg={sum(durs)/len(durs):.1f}s")
    print(f"  char min={min(chars)} max={max(chars)} avg={sum(chars)//len(chars)}")
    # also emit a plain numbered EN file for the translation step
    en_txt = a.out_json.rsplit(".", 1)[0] + "_en.txt"
    with open(en_txt, "w") as f:
        for i, o in enumerate(out):
            f.write(f"{i}\t{o['en']}\n")
    print(f"  numbered EN -> {en_txt}  (translate this, one ZH line per row)")


if __name__ == "__main__":
    main()
