# Outline 抽取 subagent prompt 模板

## 为什么要用 subagent

主上下文塞 20 份 ~360KB 的转写既污染又超限。subagent 拿到自己那一组转写，吐出 N 份 outline JSON 文件路径回主线即可。

## 并发分组

| 总讲数 N | agent 数 | 每个 agent 的范围 |
|----------|----------|-------------------|
| ≤ 5      | 1        | 全部              |
| 6–10     | 2        | 1..⌈N/2⌉ / 余下   |
| 11–20    | 4        | 1-5 / 6-10 / 11-15 / 16-20 |
| 21+      | ⌈N/5⌉    | 每 agent 5 讲     |

**在主线一次性发起所有 agent**：在同一条 message 里塞 K 个 `Agent` tool 调用块，类型全部 `general-purpose`，让 harness 并发执行。**不要**串行 await。

## Prompt 模板

下面是给单个 subagent 的 prompt 骨架。`{{...}}` 是模板变量，发起前由主线填好。

```
你是一名严谨的 PPT 大纲抽取助手。我会给你 {{N_CHAPTERS}} 份课程转写文本，
你的任务是为每一份生成一份严格符合 schema 的 JSON 大纲，写入指定文件。

==== 范围 ====
本次你处理 P{{P_START}}-P{{P_END}} 共 {{N_CHAPTERS}} 讲。

==== 章节标题 (来自 audio_urls.json，是先验信息，可信) ====
{{TITLE_LIST}}
   例如：
   - P06: 06 古典文法・正格活用
   - P07: 07 助動詞入門 + 過去助動詞「き」「けり」
   - P08: 08 完了助動詞「つ」「ぬ」
   - P09: 09 完了助動詞「たり」「り」
   - P10: 10 古典文法・综合练习一

==== 输入文件路径 ====
{{TRANSCRIPT_PATHS}}
   例如：
   - E:\\<workdir>\\transcripts_final\\p06.txt
   - ...

==== 输出文件路径 ====
{{OUTLINE_PATHS}}
   - E:\\<workdir>\\outlines\\p06.json
   - ...

==== Schema (严格执行，缺字段一律会被下游 fail) ====

每份 JSON 文件必须严格符合以下 schema：

{
  "p": <int, 章节号>,
  "title": "<str, 章节标题，去掉序号前缀，例如 '古典文法 — 正格活用'>",
  "subtitle": "<str, 一句话副标题描述>",
  "objectives": ["<str>", "..."],     # 4-6 条学习目标
  "outline": ["一、...", "二、...", "..."],  # 5-9 条本讲提纲
  "sections": [
    {
      "heading": "<str, 章节小标题>",
      "eyebrow": "知识点",            # 固定
      "bullets": ["<str>", "..."],    # 4-8 条要点
      "examples": [                   # 0-4 条例文，可空数组
        {"jp": "<日文原文>", "read": "<读音>", "note": "<解说>"}
      ],
      "tips": ["<str>", "..."]        # 0-4 条注意点，可空数组
    }
  ],                                  # 5-8 个 section
  "exercises": [                      # 2-4 道练习，可空数组
    {"q": "<问题>", "a": "<答案>"}
  ],
  "summary": ["<str>", "..."]         # 4-6 条本讲小结
}

完整范例见: C:\\Users\\<user>\\.claude\\skills\\bili-series-to-ppt\\templates\\outline_schema.json
读它一遍再开始。

==== 写作硬要求 ====
1. **绝对不要在中文 string value 里嵌套 ASCII 双引号 "…"**。要引述就用全角「…」或『…』。
   反例（会让 JSON 解析失败）: "做题时务必按"X→Y"顺序判别"
   正例: "做题时务必按「X→Y」顺序判别"
2. 内容必须严格基于转写实际讲到的，不要胡编。转写文本来自 Whisper-small，可能有
   OCR 级别的同音错字（例如「形容詞」→「型容词」），你需要根据上下文还原正确写法
   再写入大纲。
3. 例文必须是转写里出现过的，不要自创。如果一节实在没有清晰例文，就把 examples 留空数组。
4. 不要写无意义的 "总而言之"/"总结一下" 类废话——bullets 要直接是知识点，
   每条 12-40 字之间，便于在 PPT 一行内显示。

==== 输出 ====
为 P{{P_START}}-P{{P_END}} 各写一份 JSON 文件到上面的输出路径。
**不要把 JSON 内容塞回 chat**，只在结尾写一行确认：

   wrote: pNN.json (sections=K, examples=M, exercises=Q)
   wrote: pNN+1.json (...)
   ...
   ALL DONE

如果某一讲转写明显偏题或太短（< 1500 字），仍然要按 schema 写一份缩水版，
并在 chat 里额外打印一行 `WARN: pNN truncated (<reason>)`。
```

## 主线发起代码骨架

```python
# 假设 N=20, 4 路并发
agents = [
    ("P01-P05", 1, 5),
    ("P06-P10", 6, 10),
    ("P11-P15", 11, 15),
    ("P16-P20", 16, 20),
]

# 在同一个 message 里发 4 个 Agent tool 调用
# subagent_type="general-purpose"
# prompt 用上面的模板把 {{...}} 填好
```

## 校验

四个 agent 全返回后，主线必跑：

```python
import json, pathlib
missing, broken = [], []
for p in range(1, N+1):
    f = pathlib.Path(f'outlines/p{p:02d}.json')
    if not f.exists():
        missing.append(p); continue
    try:
        json.loads(f.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        broken.append((p, str(e)))
print('missing:', missing)
print('broken:', broken)
```

`broken` 的 → stage 6 跑 `fix_outline_quotes.py`。
`missing` 的 → 单独发一个 agent 补抽。
