---
name: youtube-bilingual-hardburn
description: "Turn an English (or any foreign-language) video into a Chinese–English bilingual video with subtitles HARD-BURNED into the picture, so they show on every player and platform. Use when the user wants to 做双语视频, 加中文字幕, 把视频做成中英双语, 烧字幕, 双语硬烧, 中英对照, 翻译这个视频并加字幕, bilingual subtitles, burn-in subtitles, hardsub, or share an English talk/interview/tutorial to 小红书/微信/B站 with Chinese subs. Handles the hard case of YouTube auto-captions that have NO punctuation. Pipeline: download → extract captions → re-segment into readable lines → translate line-by-line with 1:1 alignment → build a styled bilingual .ass → ffmpeg hardburn. Cross-platform: runs on Claude Code and OpenAI Codex (pure Python + ffmpeg/yt-dlp). NOT for: downloading a video only (that is a plain yt-dlp job), or adding a toggleable soft-subtitle track only."
---

# YouTube Bilingual Hardburn

Turns a foreign-language video into a Chinese–English hardsub video. The deterministic steps are scripts; the translation step is done by the agent (LLM) and is where all the risk lives.

**IRON LAW: ONE Chinese line per English line. NEVER split one English line into two Chinese lines (or merge two into one). After every translation batch, run `verify_align.py`. A single off-by-one shifts every later subtitle out of sync — and you will not notice until the burn is done.**

## When the source has punctuation vs. when it doesn't

- YouTube **auto-captions** (and most ASR) have **almost no punctuation** → the "split on `.!?`" approach fails (collapses everything into one cue). This skill solves that by merging phrases up to a character cap. **This is the default path.**
- If the source already has clean punctuated subtitles, the same pipeline still works.

## Prerequisites

- `yt-dlp` (download), `ffmpeg` (hardburn), `python3` (scripts). No Python packages needed.
- A CJK-capable font installed. macOS: `PingFang SC` (default). Linux: pass `--font "Noto Sans CJK SC"`. Windows: `--font "Microsoft YaHei"`.
- `SCRIPTS=` the absolute path to this skill's `scripts/` directory. Set it once and reuse.

## Workflow

```
Bilingual Hardburn Progress:

- [ ] Step 1: Get the video + captions ⚠️ REQUIRED
- [ ] Step 2: Extract + re-segment captions into readable lines
- [ ] Step 3: Translate every line (1:1) — the careful part ⚠️ REQUIRED
- [ ] Step 4: verify_align.py == OK ⛔ BLOCKING (cannot proceed until it passes)
- [ ] Step 5: Build bilingual .ass + confirm style on ONE test frame ⚠️ REQUIRED
- [ ] Step 6: Hardburn full video (long encode) + spot-check frames
```

## Step 1: Get the video + captions ⚠️ REQUIRED

```bash
yt-dlp -o "%(upload_date)s_%(title)s.%(ext)s" \
  -f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best" \
  --merge-output-format mp4 --write-subs --write-auto-subs --sub-langs "en" \
  --no-mtime "<URL>"
```

- If `--write-auto-subs` produces **no** caption file (some videos have none), you must transcribe the audio first (e.g. whisper) into a `.vtt`/`.srt`, then continue.
- Note the two output files: `VIDEO.mp4` and `VIDEO.en.vtt`.

## Step 2: Extract + re-segment ⚠️

```bash
python3 "$SCRIPTS/extract_phrases.py" "VIDEO.en.vtt" > phrases.json
python3 "$SCRIPTS/merge_lines.py" phrases.json lines.json   # --max-chars 95 --gap 12
```

This produces `lines.json` (`[{start,end,en}]`) and `lines_en.txt` (a numbered `idx<TAB>English` file). **Translate `lines_en.txt`.** Tune later if needed:
- subtitles feel too long on screen → lower `--max-chars` (e.g. 70)
- you want breaks at natural pauses → lower `--gap` (e.g. 2.5) — yields more, shorter lines

## Step 3: Translate every line (1:1) ⚠️ REQUIRED — this is the careful part

Read `lines_en.txt` (it is numbered `0..N-1`). Produce a plain-text ZH file: **exactly one Chinese line for each English row, same order.** Write newline-separated text (NOT JSON — Chinese quotes break JSON escaping).

Rules that prevent the Iron-Law violation:
- **One row in → one line out.** Translate the English row as its own unit. If a row breaks mid-sentence (it often will — that's normal for ASR), let the Chinese break at the same place. Do **not** "fix" it by flowing across rows.
- **Work in batches** of ~120–150 rows. After EACH batch write its file and immediately run `verify_align.py` on the cumulative result.
- Keep proper nouns in their correct form (ChatGPT, OpenAI, Claude, Gemini, Grok, DeepSeek…). ASR mangles them ("chpd"→ChatGPT, "grock"→Grok, "ha cou"→haiku) — fix to the real name.
- Natural spoken Chinese, not stiff translation. Match the speaker's register.

Concatenate all batch files into one `zh.txt` (one ZH line per EN row, in order).

## Step 4: verify_align.py ⛔ BLOCKING

```bash
python3 "$SCRIPTS/verify_align.py" lines.json zh.txt
```

- Prints `OK` → proceed.
- Prints `MISMATCH` + a side-by-side table → find the row where EN and ZH meanings stop corresponding. That row is a split (one EN row became two ZH lines) or a merge. Fix it (merge the two ZH lines back into one, or split one into two), then re-run. **Do not proceed until OK.**

## Step 5: Build .ass + confirm on ONE test frame ⚠️ REQUIRED

```bash
python3 "$SCRIPTS/build_bilingual_ass.py" lines.json zh.txt styled.ass
# Chinese on top (white 44px) + English below (grey 30px), bottom-centre.
# Linux/Windows: add --font "Noto Sans CJK SC" / --font "Microsoft YaHei"
```

Render ONE frame at a timestamp known to have a subtitle, and LOOK at it before the long encode:

```bash
ffmpeg -ss 60 -i "VIDEO.mp4" -copyts -vf "ass=styled.ass" -frames:v 1 -y test_frame.png
```

Confirm with the user: Chinese renders (no tofu boxes □□□), two-tier layout looks right, size/position acceptable. Adjust `--zh-size/--en-size/--margin/--font` and rebuild if needed. **Do not start the full encode until the test frame looks correct.**

## Step 6: Hardburn full video + spot-check

```bash
ffmpeg -y -i "VIDEO.mp4" -vf "ass=styled.ass" \
  -c:v libx264 -preset fast -crf 22 -c:a copy -sn "VIDEO_中英双语.mp4"
```

A 2-hour 1080p video takes ~15–40 min — run it in the background. When done, grab frames at the start, middle, and near-end to confirm subtitles stay in sync the whole way:

```bash
for t in 600 3900 7200; do ffmpeg -ss $t -i "VIDEO_中英双语.mp4" -frames:v 1 -y "chk_$t.png"; done
```

If a frame looks misaligned, re-confirm the same timestamp's cue in `lines.json`+`zh.txt` are the same source row before assuming a bug (low-res frames are easy to misread).

## Anti-Patterns

- **Splitting/merging lines during translation** — the #1 cause of full-video desync. One EN row = one ZH line, always.
- **Writing translations as JSON** — Chinese curly quotes “ ” and 「」 silently break JSON parsing. Use newline-separated plain text.
- **Trusting caption END times for ordering** — rolling-caption ENDs overlap; `merge_lines.py` sequences by START only. Don't reorder by END.
- **Skipping the test frame** — burning 2 hours then discovering tofu boxes or a wrong font wastes the whole encode.
- **Re-encoding audio** — use `-c:a copy`. Only the video track changes.
- **Using the old `build_bilingual.py` from the video-download skill** on auto-captions — it splits on punctuation and collapses the whole transcript into one cue. This skill replaces it.

## Pre-Delivery Checklist

- [ ] `verify_align.py` printed `OK` (EN count == ZH count) before building the .ass
- [ ] Test frame inspected: Chinese renders, no □ boxes, layout/size correct
- [ ] Spot-checked start/middle/end frames of the final mp4 — subtitles in sync
- [ ] Output named clearly (e.g. `<title>_中英双语.mp4`); original video untouched
- [ ] Proper nouns corrected (no "chpd"/"grock"/"ha cou" left in the Chinese)

## Cross-platform (OpenAI Codex, etc.)

All scripts are pure `python3` + `ffmpeg`/`yt-dlp` — no Claude-specific dependency. To run this workflow under Codex (or any shell-capable agent), load `references/codex-usage.md`.
