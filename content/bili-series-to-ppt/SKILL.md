---
name: bili-series-to-ppt
description: Use when the user wants to turn a Bilibili 多 P 教学系列（合集/番剧/课程视频）into a stack of structured teaching .pptx files. Triggers on requests like "把这个 BV 系列做成讲义 PPT", "BV1xxx 全部章节生成教学课件", "下载并转写一整套 bilibili 教学视频再出 PPT", "对每一章生成严格的指导教学 PPT", or when the user references this project (`E:\claude_ask\bilibili_learn`), `audio_urls.json`, `bili2text`, or `scripts/build_ppts.py`.
---

# Bilibili 系列 → 转写 → 大纲 → 教学 PPT 全链路

把一套多 P 的 Bilibili 教学合集（默认 20 讲规模）端到端转成一份"每讲一份 .pptx"的教学课件。

参考实现已经跑通过一遍：`E:\claude_ask\bilibili_learn\` 下的「日语学习・古典文法」(BV1sZ4y1A7Mq, 20 讲) 跑出了 `ppt_古典文法/p01.pptx..p20.pptx`，分数线为「内容正确 + 字号统一 + 16:9 留白合理」。

```
stage 1 — 抓 audio URL    (yt-dlp / 浏览器抓包)   → audio_urls.json
stage 2 — 批量下载        (curl + ffprobe 校验)   → audio/p*.m4a
stage 3 — 批量转写        (bili2text + Whisper)  → bili2text/.b2t/transcripts/original/*.txt
stage 4 — 收集转写        (拷贝最新一份)          → transcripts_final/p*.txt
stage 5 — 大纲抽取        (并发 subagent × 4)     → outlines/p*.json
stage 6 — JSON 自愈       (fix_outline_quotes)    → outlines/p*.json (有效 JSON)
stage 7 — 渲染 PPT        (python-pptx)           → ppt/p*.pptx
stage 8 — 抽样校验        (Read 切片 / 解 zip)    → 视觉/字段抽检
```

---

## When to fire

- 用户给出 Bilibili 多 P 视频的 BV id 或合集 URL，希望把每一 P 转成讲义 PPT。
- 用户明确说「下载并转写后做成教学课件」或类似的多阶段交付。
- 用户引用本仓库下任何文件（`audio_urls.json`、`scripts/{download,transcribe,build_ppts,fix_outline_quotes}.py`、`bili2text/`）。
- 用户上一轮交付了 `transcripts_final/p*.txt` 后，要求"基于转写做 PPT"——直接从 stage 5 入。

不要在以下场景套用本 skill：
- 单条视频 / 非系列性内容 → 用更轻的 `bili2text tx <url>` 单跑即可。
- 用户想出学术汇报用 PPT（百廿红、Q1-Q5 风格）→ 切到 `sjtu-ppt-build` skill。

---

## Non-negotiable rules

1. **`bili2text` 必须用它自己的 uv venv 跑**：`uv run --project <ROOT>/bili2text bili2text tx <audio>`。直接用全局 `python` 一定 ModuleNotFoundError。
2. **Windows 控制台必须 `PYTHONIOENCODING=utf-8`**，否则 bili2text 输出中文时 GBK 编码崩溃，进程退出码非 0 但其实转写已完成。务必 `env=os.environ.copy(); env["PYTHONIOENCODING"] = "utf-8"`。
3. **必须打过 `library.py:34` 的补丁**：原代码 `result.metadata.get("download", {}).get("title")` 在 source 是本地 audio 时会 `'NoneType' object has no attribute 'get'`，因为 pipeline 把 `metadata["download"] = None`（键存在但值为 None，所以 `.get` 的默认 `{}` 不生效）。改成 `(result.metadata.get("download") or {}).get("title")`。详见 `references/pitfalls.md`。
4. **下载用 curl 而不是 yt-dlp / requests**：bilibili 音频 mirror 强校验 `Referer: https://www.bilibili.com/` + UA + 部分 cookies。`scripts/download_all.py` 的命令行已经调好；不要重写。
5. **每个 m4a 必须用 `ffprobe` 校验时长** 与 `audio_urls.json` 里的 `d` 字段差 ≤ 5 秒，否则视为下载失败重试。size > 1MB 不够，因为部分错误响应也是 1MB+。
6. **大纲抽取用并发 subagent**：20 讲时分 4 个 general-purpose agent，每人 5 讲。串行做主上下文会爆。给每个 agent 严格喂 schema 范例（见 `references/outline_subagent_prompt.md`），输出 path 提前算好。
7. **subagent 出的 JSON 必跑一遍 `fix_outline_quotes.py`**：模型在中文里写嵌套 ASCII `"…"` 是已知问题。脚本会保留语义，把内层 `"…"` 转成 `「…」`。
8. **PPT 渲染前必须 `json.loads` 过 20 个文件**，跑不过的不要进 stage 7，停下来人工诊断。
9. **PPT 用 16:9（13.33×7.5 in）和 navy/accent/gray 配色**，字号统一 18-28pt（详见 `templates/build_ppts.py`）。**不要再加新模板色**——视觉一致性比花哨重要。
10. **每一阶段都要落盘**（audio/, transcripts_final/, outlines/, ppt/）。下次任务来时可以从任一阶段断点续跑。

---

## Standard flow

### Stage 0. 项目脚手架

让用户提供：
- 系列的 BV id 或完整 URL（**必填**）
- 系列总讲数（必填，用于 sanity check）
- 是否需要 cookies（涉及大会员 / 限制级视频）
- 输出目录前缀（默认 `<workdir>/ppt_<系列简称>`）

在工作目录下铺出：

```
<workdir>/
├── audio_urls.json             # stage 1 产物
├── cookies.txt                 # 用户提供（如需）
├── audio/                      # stage 2 产物
├── bili2text/                  # 提前 git clone + uv sync
├── logs/
├── transcripts_final/
├── outlines/
├── ppt/                        # 或 ppt_<系列名>/
└── scripts/
    ├── download_all.py
    ├── transcribe_all.py
    ├── fix_outline_quotes.py
    └── build_ppts.py
```

四个 `scripts/` 直接从本 skill 的 `templates/` 拷过去，绝大多数不需要改。

### Stage 1. 抓 audio URL

输入: BV id / 合集 URL。
产物: `audio_urls.json`，schema 严格固定为：

```json
[
  {"p": 1, "t": "01 第一讲・XXX", "d": 994, "u": "https://...mirror.../...m4a", "b": "https://...backup.../...m4a"}
]
```

字段说明:
- `p`: 1-based part 号
- `t`: 章节标题（保留前缀 "01 ", "02 " 之类，build_ppts 会去掉）
- `d`: 时长（秒，整数）
- `u`: primary mirror URL
- `b`: backup mirror URL（可空，但强烈建议有）

抓取方法（**优先级从高到低**）：
1. `yt-dlp -j https://www.bilibili.com/video/BV.../?p=N` → 解 `formats[]` 里 `acodec=mp4a` 的 entry 拿 audio URL。
2. 浏览器 DevTools Network → 过滤 `bilivideo.com` → 复制 .m4a 请求 URL。
3. 从已有 `audio_urls.b64` / `audio_urls_v2.b64` 解 base64 拿到（仅旧项目复用时）。

**重要**: bilibili audio URL 一般 **2-6 小时过期**，过期会 403。如果 stage 2 里大面积 403，就必须重抓。

### Stage 2. 批量下载

```bash
PYTHONIOENCODING=utf-8 python scripts/download_all.py
```

`download_all.py` 行为（见 `templates/download_all.py`）:
- 串行下载 20 个文件（不要并发，bilibili 会限流）
- curl 命令: `--retry 5 --retry-delay 2 --retry-all-errors --connect-timeout 20 --max-time 600 -A <Chrome UA> -H "Referer: https://www.bilibili.com/"`
- 每个 mirror 失败后切 backup
- ffprobe 校验时长 ±5s
- 跳过已存在且校验通过的文件（断点续跑友好）

**校验**: `ls -la audio/ | wc -l` 应该 = N+1（含 ".") 或者 N+2。所有文件 size 都 > 1MB。

### Stage 3. 批量转写

**前置补丁**（首次跑 bili2text 必做）：

```python
# bili2text/src/b2t/library.py:34 附近
# 原: title=result.metadata.get("download", {}).get("title") or result.source.display_name,
# 改:
title=(result.metadata.get("download") or {}).get("title") or result.source.display_name,
```

bili2text 是 editable install，改源即生效，**不要 re-install**。

然后跑：

```bash
python scripts/transcribe_all.py 2>&1 | tee logs/transcribe.log
```

`transcribe_all.py` 行为（见 `templates/transcribe_all.py`）:
- `env["PYTHONIOENCODING"] = "utf-8"`
- 串行调 `uv run --project bili2text bili2text tx <audio.resolve()>`
- 每条转写一份 log: `logs/tx_p01.log` ... `logs/tx_p20.log`
- 每条结束打印 `ok in <X>s` / `FAIL exit=<C>`
- 等不到 audio 时会循环 sleep 10s（允许 stage 2 与 stage 3 流水线并跑）

转写参数: 默认 Whisper-small CPU。一条 10-15 分钟视频在常规机器上 5-10 分钟。20 讲全部跑完 1.5-3 小时。**不要切 GPU**，因为 bili2text 的 CUDA 路径在 Windows 上版本耦合很脆弱。

### Stage 4. 收集转写

bili2text 把每次转写写到 `bili2text/.b2t/transcripts/original/p01-<timestamp>.txt`，可能多份。我们要把"每个 p 最新一份" 拷到 `transcripts_final/p01.txt`：

```python
import pathlib, shutil, re
src = pathlib.Path('bili2text/.b2t/transcripts/original')
dst = pathlib.Path('transcripts_final'); dst.mkdir(exist_ok=True)
for p in range(1, 21):
    files = sorted(src.glob(f'p{p:02d}-*.txt'), key=lambda f: f.stat().st_mtime)
    if files: shutil.copy(files[-1], dst / f'p{p:02d}.txt')
```

校验: `wc -l transcripts_final/p*.txt`，单文件 100-1000 行不等，**不应该有 0 行的**。

### Stage 5. 大纲抽取（**核心 — 并发 subagent**）

**为什么用 subagent**: 20 份转写 × 平均 ~18KB = ~360KB，全塞主上下文会污染并占爆。subagent 只把最终 JSON 摘要返回主线即可。

**分组**: 默认 4 个 general-purpose agent，每人 5 讲。如果总讲数 ≠ 20，按 `ceil(N / 5)` 个 agent 分组，每组覆盖连续讲数。

**给每个 agent 的 prompt 模板**: 见 `references/outline_subagent_prompt.md`。关键点：
- **明确范围**: 「请处理 P06-P10 共 5 讲」
- **附带章节标题**: 从 audio_urls.json 提取每讲 `t` 给 agent 当先验
- **附带 schema 完整范例**: 用 `templates/outline_schema.json` 做 1-shot 示范
- **明确输出**: "为每讲写一份 outlines/p<NN>.json，写完返回 5 个文件路径"
- **禁止**: 不要让 agent 直接自己 json.dumps，要它**写文件**（避免 200KB 在 agent 间传递）

**并发**: 在一个 message 里发 4 个 Agent tool 调用，类型 `general-purpose`。

**校验**: 4 个 agent 全返回后

```python
import json, pathlib
for p in range(1, 21):
    f = pathlib.Path(f'outlines/p{p:02d}.json')
    assert f.exists(), f
    json.loads(f.read_text(encoding='utf-8'))   # may raise
```

**预期失败率**: ~20% 的 JSON 因为「中文里嵌套未转义 ASCII 双引号」无法解析。这正是 stage 6 要解决的——不要在 stage 5 让 agent 重写，**stage 6 比重新跑 agent 便宜 10 倍**。

### Stage 6. JSON 自愈

```bash
python scripts/fix_outline_quotes.py
```

逻辑（见 `templates/fix_outline_quotes.py`）:
- 只处理 `json.loads` 当前**失败**的文件（已经合法的不动）
- 行级匹配 `^(\s*)"(.*)"(\s*[,\]]?\s*)$`
- 跳过含 `":\s*"` 的 object key:value 行（避免破坏结构）
- 把"字符串值"内的成对 ASCII `"…"` 交替替换为 `「…」`

跑完再 `json.loads` 校验全部 20 份。如果还有失败的，**人工打开看那一行**，多半是嵌套 3 重引号或者 stray `\` 转义——这种少见 case 直接手改更快。

### Stage 7. 渲染 PPT

```bash
uv run --project bili2text python scripts/build_ppts.py
```

为什么走 `bili2text` 的 venv: `python-pptx` 已经在那个 venv 里 ready。**不要给主项目再装一份 venv**，多一个 lock 文件多一个坑。

`build_ppts.py` 行为（见 `templates/build_ppts.py`）:
- 16:9: `prs.slide_width = Inches(13.33); prs.slide_height = Inches(7.5)`
- 配色: navy `#142A5C` / accent `#B83A3A` / gray `#555555` / light `#F2EEE3`
- 每讲 PPT 结构（**严格固定**）:
  1. 封面（第N讲 + title + subtitle）
  2. 学习目标 (`objectives`)
  3. 本讲提纲 (`outline`)
  4. 每个 section 一组三页:
     - 知识点 (`bullets`)
     - 例文 (`examples`，可选)
     - 注意点 (`tips`，可选)
  5. 课堂练习 (`exercises`)
  6. 本讲小结 (`summary`)
- 字号: 标题 28pt / 正文 18pt / 例文 jp 20pt / 例文 read 16pt / 例文 note 15pt / 练习 17pt
- 输出: `ppt/p<NN>.pptx`

### Stage 8. 抽样校验

不要靠"20 个 .pptx 都生成了"就认为完成。**至少抽 1 份解 zip 看 slide XML**：

```python
import zipfile, pathlib
with zipfile.ZipFile('ppt/p07.pptx') as z:
    print(sorted(n for n in z.namelist() if n.startswith('ppt/slides/slide')))
    # 应该有 22-26 个 slide XML
```

或者用 python-pptx 把 P07 每页 text 打印一遍：

```python
from pptx import Presentation
prs = Presentation('ppt/p07.pptx')
for i, s in enumerate(prs.slides):
    print(f'=== slide {i+1} ===')
    for shape in s.shapes:
        if shape.has_text_frame:
            print(shape.text_frame.text[:200])
```

人工确认: 标题对、章节内容对、没有空 placeholder、字号统一。

最后报告给用户:
- 输出目录绝对路径
- 每讲页数范围（如 "22-26 slides 不等"）
- 每讲文件大小范围（如 "47-66 KB"）
- 抽检章节 + 抽检结果

---

## File map

```
<workdir>/                        ← 用户工作目录，e.g. E:\claude_ask\bilibili_learn
├── audio_urls.json
├── cookies.txt                  ← 用户提供（可选）
├── playlist.json                ← yt-dlp 抓的原始 metadata（可选）
├── audio/                       ← p01.m4a..pNN.m4a
├── bili2text/                   ← git clone + uv sync 后的 editable install
│   ├── .venv/
│   ├── .b2t/transcripts/original/  ← Whisper raw 输出
│   └── src/b2t/library.py       ← 必须打的 NoneType 补丁
├── logs/
│   ├── tx_p01.log..tx_pNN.log   ← 转写日志
│   └── transcribe.log           ← 总日志
├── transcripts_final/p*.txt     ← 收集后的最终转写
├── outlines/p*.json             ← subagent 大纲产物
├── ppt/p*.pptx                  ← 最终交付
└── scripts/                     ← 从本 skill 复制
    ├── download_all.py
    ├── transcribe_all.py
    ├── fix_outline_quotes.py
    └── build_ppts.py
```

---

## References (read before each phase)

- `references/outline_subagent_prompt.md` — 完整的 subagent prompt 模板 + 4 路并发的发起方式
- `references/outline_schema.md` — outline JSON schema 字段说明 + 1-shot 范例
- `references/pitfalls.md` — 已踩过的 8 个坑及 root cause + fix
- `references/bilibili_url_acquisition.md` — yt-dlp / 浏览器抓包 / b64 解码三种 URL 获取方式

## Templates

- `templates/download_all.py` — curl + ffprobe 校验下载脚本
- `templates/transcribe_all.py` — bili2text 串行转写脚本
- `templates/fix_outline_quotes.py` — JSON 引号自愈
- `templates/build_ppts.py` — python-pptx 渲染脚本
- `templates/outline_schema.json` — 大纲 1-shot 范例（喂 subagent）
- `templates/library_patch.diff` — bili2text NoneType bug 补丁

---

## Canonical assumptions

| 项 | 默认 |
|----|------|
| Python (主项目) | 系统 python，不强求版本 |
| Python (bili2text) | uv 管理的 .venv（Python 3.12） |
| 工作目录 | 用户提供，绝对路径，Windows 路径用反斜杠 |
| 字符编码 | UTF-8（环境变量 `PYTHONIOENCODING=utf-8` 必须设置） |
| 系列规模假设 | 默认 20 讲；脚本对任意 N 都能跑（download/transcribe 读 audio_urls.json，build_ppts 读 outlines/*.json） |
| Whisper 模型 | small CPU（不要切 GPU） |
| Subagent 并发 | 4 路（每路 5 讲，N=20 时） |
| PPT 比例 | 16:9 |

如果用户偏离任一项，**在 Stage 0 当面确认**而不是硬跑。
