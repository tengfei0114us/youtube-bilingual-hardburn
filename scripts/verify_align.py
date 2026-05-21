#!/usr/bin/env python3
"""Verify a ZH translation file aligns 1:1 with the merged EN lines.

This is the most important quality gate in the workflow. Translating a long
talk in batches, it is extremely easy to split ONE English line into TWO
Chinese lines (or merge two into one). A single such error shifts every
later subtitle out of sync. This tool catches it instantly.

If counts match: prints OK.
If they differ: prints a side-by-side table so you can eyeball exactly where
EN and ZH stop corresponding (the row where the meanings diverge is the split).

Usage:
  python3 verify_align.py lines.json zh.txt
  python3 verify_align.py lines_en.txt zh.txt   # also accepts the numbered EN txt
"""
import json
import sys


def load_en(path):
    if path.endswith(".json"):
        return [c["en"] for c in json.load(open(path))]
    # numbered "idx<TAB>text" file
    out = []
    for l in open(path, encoding="utf-8").read().splitlines():
        if not l:
            continue
        out.append(l.split("\t", 1)[1] if "\t" in l else l)
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: verify_align.py <lines.json|lines_en.txt> <zh.txt>")
    en = load_en(sys.argv[1])
    zh = [l for l in open(sys.argv[2], encoding="utf-8").read().splitlines() if l != ""]
    print(f"EN: {len(en)}  ZH: {len(zh)}", "OK" if len(en) == len(zh) else "MISMATCH")
    if len(en) == len(zh):
        return
    n = max(len(en), len(zh))
    for i in range(n):
        e = en[i][:34] if i < len(en) else "———"
        z = zh[i][:18] if i < len(zh) else "———"
        mark = "" if (i < len(en) and i < len(zh)) else "  <<< extra"
        print(f"{i:4} | {e:36} | {z}{mark}")
    sys.exit(1)


if __name__ == "__main__":
    main()
