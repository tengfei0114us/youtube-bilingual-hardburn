# youtube-bilingual-hardburn

把英文（或任意外语）视频做成**中英双语硬字幕**视频——字幕烧进画面像素，
任何播放器、任何平台都显示，关不掉。适合把英文演讲/访谈/教程发到
小红书、微信、B站。

## 它解决什么

YouTube 自动字幕几乎没有标点，传统"按句号断句"会把整片塌成一句字幕。
本 skill 改为按字符数 + 时间重组字幕行，再逐行翻译，**严格 1:1 对齐校验**，
最后生成中文在上、英文在下的双语 ASS，用 ffmpeg 硬烧。

## 流程

```
下载 → 解析字幕 → 重组可读行 → 逐行翻译(LLM) → verify_align 校验 → 双语 ASS → ffmpeg 硬烧 → 抽帧验证
```

## 安装

- **Claude Code**：克隆到 `~/.claude/skills/`，对它说"把这个视频做成中英双语"即可。
  ```bash
  git clone <this-repo> ~/.claude/skills/youtube-bilingual-hardburn
  ```
- **OpenAI Codex / 其他 agent**：脚本是纯 Python + ffmpeg/yt-dlp，无 Claude 专属依赖。
  把文件夹放进项目，在 `AGENTS.md` 指向 `SKILL.md`，或直接让 agent"按 SKILL.md 做"。
  详见 [`references/codex-usage.md`](references/codex-usage.md)。

## 依赖

`yt-dlp`、`ffmpeg`、`python3`，以及一个 CJK 字体
（macOS: PingFang SC / Linux: Noto Sans CJK SC / Windows: Microsoft YaHei）。

## 脚本

| 脚本 | 作用 |
|---|---|
| `scripts/extract_phrases.py` | 从无标点的 `.vtt` 解析出短语级时间轴 |
| `scripts/merge_lines.py` | 按字符数 + 起始时间重组成可读字幕行 |
| `scripts/verify_align.py` | **核心质量闸门**：校验中英 1:1 对齐，定位错位 |
| `scripts/build_bilingual_ass.py` | 生成中文在上/英文在下的双语 ASS |

## 一个诚实的说明

翻译那一步需要 LLM 在环逐行翻（2 小时视频 ≈ 1600+ 行，省不掉）。本 skill 帮你
**不踩坑**（无标点、字幕错位、JSON 引号、字体乱码、跳过测试帧），而不是把
2 小时视频变成一键完成。最关键的质量闸门是 `verify_align.py`——任何模型翻译后
都要跑它确认 1:1 对齐，再开始烧。

## License

MIT
