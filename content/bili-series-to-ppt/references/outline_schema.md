# Outline JSON schema 字段说明

每讲一份 JSON。`build_ppts.py` 会按这些字段渲染成 22-26 张 slide。

## 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `p`         | int    | ✓ | 1-based 章节号 |
| `title`     | str    | ✓ | 章节标题，**去掉**「01 」「02 」之类前缀；可加破折号副标 |
| `subtitle`  | str    | ✓ | 一句话副标题，封面用 |
| `objectives`| list[str] | ✓ | 4-6 条学习目标，渲染为「学习目标」slide |
| `outline`   | list[str] | ✓ | 5-9 条本讲提纲，每条以「一、」「二、」开头便于阅读 |
| `sections`  | list[Section] | ✓ | 5-8 个章节小段 |
| `exercises` | list[Exercise] | ✗ | 2-4 道课堂练习；空数组则不渲染该 slide |
| `summary`   | list[str] | ✗ | 4-6 条本讲小结；空数组则不渲染该 slide |

## Section

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `heading`  | str    | ✓ | 章节小标题，e.g. "三、助動詞「き」的活用" |
| `eyebrow`  | str    | ✗ | 渲染时显示在标题上方，默认 "知识点" |
| `bullets`  | list[str \| {label, text}] | ✓ | 4-8 条要点；如果传 dict，渲染时 label 用 ACCENT 色 |
| `examples` | list[Example] | ✗ | 0-4 条例文；空则跳过 examples slide |
| `tips`     | list[str] | ✗ | 0-4 条注意点；空则跳过 tips slide |

## Example

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `jp`   | str | ✓ | 日文原文 |
| `read` | str | ✗ | 读音 / 历史假名遣 |
| `note` | str | ✗ | 解说 / 翻译 |

## Exercise

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `q` | str | ✓ | 问题 |
| `a` | str | ✗ | 答案；空字符串则不渲染答案行 |

## 渲染规则速查

每讲 slide 数 = `2 + has(objectives) + has(outline) + Σsection(1 + has(examples) + has(tips)) + has(exercises) + has(summary)`

20 讲跑下来典型数字：每讲 22-26 slide / 47-66 KB。

## 1-shot 范例

见 `templates/outline_schema.json`（P07 助動詞「き」「けり」，已实战验证）。
