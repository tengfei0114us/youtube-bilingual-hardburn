# youtube-bilingual-hardburn

> 仓库 · Repo: https://github.com/tengfei0114us/youtube-bilingual-hardburn

把英文视频配上中英双语字幕、直接烧进画面的工具。下下来就是一个带字幕的视频文件，手机、电脑、断网、发给别人，走到哪看到哪。

我做这个就是为了自己学 AI。YouTube 上好东西太多了，但基本都是英文；YouTube 自带的翻译又不好用，看着费劲。我英文不算差，可一边听一边啃终归慢，我更想能踏踏实实坐下来，把一个两小时的硬核视频真正看明白。所以干脆自己动手：把视频下下来、配上中英字幕，一来看着省力，二来存在本地，想什么时候看就什么时候看。说白了，外面那么多好内容，不该因为是英文、因为要翻墙，就跟大多数人没关系。

真正逼我自己写一套的，是 YouTube 的自动字幕几乎没有标点。市面上那些"按句号断句"的工具一上来就把两小时的字幕揉成一句话，根本没法用。我把整条流程从头串了一遍，顺手做成了这个 skill。

它干的就是一条链：下视频 → 扒字幕 → 把碎成一截一截的字幕重新拼成能读的句子 → 一行一行翻译 → 中文在上英文在下 → ffmpeg 烧进画面。

## 注意事项

1. **这不是纯脚本工具，翻译那步要 AI 在环。** 得在 Claude Code 或 OpenAI Codex 里跑，让 AI 一行行翻——两小时视频一千六百多行，省不掉。这工具帮你的是少踩坑，不是把长视频变成点一下就完事。clone 下来直接跑脚本是跑不出结果的。
2. **`yt-dlp` 要保持最新。** YouTube 反爬经常变，版本旧了下载会报 403。先升级：`brew upgrade yt-dlp`（或 `pip install -U yt-dlp`）。
3. **得装中文字体，否则中文显示成方块。** macOS（`PingFang SC`）和 Windows（`Microsoft YaHei`）系统自带，不用管；Linux 装一下 Noto 再用：`sudo apt install fonts-noto-cjk`，然后给脚本传 `--font "Noto Sans CJK SC"`。
4. **翻完一定先对齐再烧。** 跑一下 `verify_align.py` 确认中英行数严格 1:1，对齐了再烧进视频。错一行，后面全乱——这步千万别省。

（默认你能正常访问 YouTube，代理这种前提就不在这儿展开了。）

## 怎么用

用 Claude Code 的话，clone 到 skills 目录：

```bash
git clone https://github.com/tengfei0114us/youtube-bilingual-hardburn ~/.claude/skills/youtube-bilingual-hardburn
```

然后丢给它一个视频链接、说一句"把这个做成中英双语"就行，剩下的它按 `SKILL.md` 一步步走。

用 OpenAI Codex 或别的 agent 也能跑，脚本是纯 Python，没有 Claude 专属的东西。把文件夹放进项目，按 [`references/codex-usage.md`](references/codex-usage.md) 走。

## 得先装这些

`yt-dlp`、`ffmpeg`、`python3`，再加一个中文字体（见注意事项第 3 条）。

## 脚本都干嘛的

| 脚本 | 干啥 |
|---|---|
| `scripts/extract_phrases.py` | 从没标点的 `.vtt` 里把短语和时间轴扒出来 |
| `scripts/merge_lines.py` | 把碎短语按字数和时间拼成能读的字幕行 |
| `scripts/verify_align.py` | 对齐校验，中英对不上时直接指出错在哪行（最重要的一步） |
| `scripts/build_bilingual_ass.py` | 生成中文在上、英文在下的双语字幕 |

## 致谢

这个小工具是站在别人肩膀上的，真正干重活的是下面这些开源项目：

- **下载靠 [yt-dlp](https://github.com/yt-dlp/yt-dlp)。** 它没有单一作者——是 youtube-dl 的社区分支（youtube-dl 最早 2006 年由 Ricardo García 写、后由 Philipp Hagemeister 接手）。2020 年 youtube-dl 被 RIAA 封杀那几天，`pukkandan` 重新分叉出了 yt-dlp，如今由 coletdjnz、dirkf、Grub4K、bashonly、seproDev 等一群志愿者共同维护。它更新很勤（YouTube 一改反爬它就跟着修），所以记得常 `brew upgrade yt-dlp`。谢谢这群人，没有它这事根本起不了步。
- **烧字幕、转码靠 [FFmpeg](https://ffmpeg.org/)。**
- **中文字体如果用 [Noto Sans CJK](https://github.com/notofonts/noto-cjk)，感谢 Google 把它开源。**

## License

MIT
