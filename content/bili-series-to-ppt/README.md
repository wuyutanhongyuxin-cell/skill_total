# Bilibili Series → Teaching PPT

把 Bilibili 多 P 教学系列（一整个系列的合集视频）端到端转成一摞结构化、可直接讲课的 `.pptx` 课件。

## 功能

输入一个 BV 号 + 章节标题列表，输出：

```
ppt_<series>/p01.pptx ... pNN.pptx     # 每讲一份 22-26 张幻灯片的 PPT
```

每讲 PPT 严格按「封面 → 学习目标 → 提纲 → 多个知识点小节（要点/例文/Tips）→ 课堂练习 → 小结」结构渲染，16:9 宽屏，配色统一（NAVY / ACCENT / GRAY / LIGHT）。

### 流水线（8 个 stage）

```
stage 1  抓 audio_urls.json           （yt-dlp / DevTools / b64 任选）
stage 2  curl 下载 + ffprobe ±5s 校验
stage 3  bili2text + Whisper-small 转写
stage 4  收集到 transcripts_final/pNN.txt
stage 5  4× 并发 subagent 抽 outline JSON
stage 6  fix_outline_quotes.py 自愈内层 ASCII 双引号
stage 7  build_ppts.py 渲染 .pptx
stage 8  随机抽样校验
```

### 已封装的关键经验

- **8 个踩过的坑**已记录在 `references/pitfalls.md`：bili2text NoneType bug、Windows GBK 崩溃、bilibili 签名 URL 2-6 小时过期、1MB 错误页伪装成功、python-pptx 装在 `bili2text/.venv` 等
- **subagent 并发分组表**（≤5/6-10/11-20/21+ 讲）已固化在 `references/outline_subagent_prompt.md`
- **`fix_outline_quotes.py`** 修复 subagent 出 JSON 时把内层 `"…"` 嵌进中文字符串的常见问题（比让模型重写便宜 10 倍）
- **`library_patch.diff`** 修 bili2text 在本地音频转写收尾的 `'NoneType' object has no attribute 'get'`

## 使用方式

### 安装为全局 skill（推荐）

```bash
# 整个 skill 目录复制到 ~/.claude/skills/
cp -r content/bili-series-to-ppt ~/.claude/skills/
```

之后在任意项目中说：

```
帮我把 BV1xxxxxxxxx 这个系列每章生成一份教学 PPT
```

Claude Code 会自动加载该 skill 并按 `SKILL.md` 的 8 个 stage 执行。

### 触发短语

skill 在以下意图下会被自动加载：

- 「把这个 BV 系列做成讲义 PPT」
- 「BV1xxx 全部章节生成教学课件」
- 「对每一章生成严格的指导教学 PPT」

## 目录结构

```
bili-series-to-ppt/
├── SKILL.md                              # 主流程定义（8 stage + 10 条硬规则）
├── templates/
│   ├── download_all.py                   # stage 2: curl + ffprobe 下载器
│   ├── transcribe_all.py                 # stage 3: bili2text 顺序转写
│   ├── fix_outline_quotes.py             # stage 6: JSON 引号自愈
│   ├── build_ppts.py                     # stage 7: python-pptx 渲染
│   ├── outline_schema.json               # 1-shot 范例（P07 助動詞「き／けり」）
│   └── library_patch.diff                # stage 3 前打到 bili2text 的补丁
└── references/
    ├── bilibili_url_acquisition.md       # 三种 URL 抓取方式
    ├── outline_schema.md                 # outline JSON 字段说明
    ├── outline_subagent_prompt.md        # subagent prompt 模板 + 并发分组表
    └── pitfalls.md                       # 8 个已踩过的坑及修复
```

## 依赖

- Python 3.12（建议 uv 管理）
- bili2text（editable install，自带 Whisper-small）
- python-pptx（装在 `bili2text/.venv` 里，**不要**给主项目再开 venv）
- ffmpeg / ffprobe / curl
- 可选：`cookies.txt`（大会员视频 / 4K / 限制级才需要）

## 实战记录

首次封装时已用本 skill 跑通 BV1sZ4y1A7Mq「日语学习・古典文法」20 讲：

- 20 份转写：全部 1500 字+，bili2text 索引正常
- 20 份 outline JSON：4 路并发 subagent ~6 min 完成，4 份触发引号自愈
- 20 份 PPT：每份 22-26 slide / 47-66 KB，渲染 < 5 s
