# Running this skill outside Claude Code (OpenAI Codex, OpenCode, etc.)

This skill has no Claude-specific dependency. The pipeline is:
**pure-Python scripts** (deterministic) + **one LLM translation step** (the agent) + **ffmpeg/yt-dlp** (CLI). Any shell-capable coding agent can run it.

## What's different per platform

| Step | Claude Code | OpenAI Codex / other |
|---|---|---|
| Loading the guide | `Skill` tool auto-loads `SKILL.md` | Tell the agent: "Follow the steps in `SKILL.md`" — it's plain Markdown, the agent reads it directly |
| Running scripts/ffmpeg | `Bash` tool | Codex's shell / `!` command — identical commands |
| The translation step | Claude translates `lines_en.txt` | GPT (Codex) translates `lines_en.txt` — same 1:1 rule |
| Reading/writing files | `Read`/`Write` tools | shell (`cat`, editor, redirection) |

The SKILL.md body is already written as **shell commands + an explicit "translate this file" instruction**, so it transfers as-is. There is nothing to rewrite.

## Install under Codex

Codex has no dedicated "skills" directory. Two simple options:

1. **Per-project (recommended).** Copy this folder into the repo (e.g. `tools/youtube-bilingual-hardburn/`) and add a line to the project's `AGENTS.md`:
   ```
   ## Bilingual hardburn
   To turn a foreign-language video into a Chinese–English hardsub video,
   follow tools/youtube-bilingual-hardburn/SKILL.md. Set
   SCRIPTS=tools/youtube-bilingual-hardburn/scripts before running.
   ```
   Codex reads `AGENTS.md` on startup, so it will know the capability exists.

2. **Ad-hoc.** Put the folder anywhere and just tell Codex:
   "Follow `<path>/SKILL.md` to make a bilingual hardsub of `<URL>`.
   `SCRIPTS=<path>/scripts`."

## The one thing that matters on any platform

The translation step is where every agent (Claude or GPT) tends to break the
**1:1 line rule**. Whatever the platform, after each translation batch run:

```bash
python3 "$SCRIPTS/verify_align.py" lines.json zh.txt
```

and do not build the `.ass` until it prints `OK`. This single gate is what makes
the workflow reliable regardless of which model does the translating.

## Environment notes

- Fonts are the most common cross-machine failure: a missing CJK font renders
  Chinese as tofu boxes (□□□). Pass `--font` to `build_bilingual_ass.py`:
  macOS `PingFang SC` · Linux `Noto Sans CJK SC` · Windows `Microsoft YaHei`.
- `yt-dlp` must be recent (YouTube anti-bot changes frequently). On a stale
  version, downloads 403 — upgrade it (`brew upgrade yt-dlp` / `pip install -U yt-dlp`).
- Behind the GFW, YouTube needs a proxy: add `--proxy "http://127.0.0.1:7897"`
  (or your local proxy port) to the `yt-dlp` command.
