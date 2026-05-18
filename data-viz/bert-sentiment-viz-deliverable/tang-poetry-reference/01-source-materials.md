# 阶段 0 实例 · 唐诗作业的源材料读法

> 配合 SKILL.md 阶段 0 看。展示真实作业的源材料处理。

## 源材料清单（SJTU 第 21 讲 作业 4）

| 文件 | 内容 | 关键约束 |
|---|---|---|
| `情感分析代码.zip` | 教师原生 sentiment.py + 模型加载脚本 | 用 `ethanyt/guwen-sent`，输出 5 类概率 + argmax；自带 pie 图 + csv 输出 |
| `PPT_第21讲_4页保留.pdf` | 任务书 PPT | 作业 4 占 20 分；要求"漂亮的可视化"；保留教师图表风格 |
| `PPT_第22讲_6页保留.pdf` | 课件 PPT | 第 5 页 lockdown trajectory 图、第 6/7 页地图样式必须借鉴 |
| `参考文献-情感分析.zip` | 3 篇 PDF | LIWC+Emb (Paper1) / Nature COVID BERT+RDD+SCM (Paper2) / Evol 古典文学 (Paper3) |

## 处理步骤

```bash
# 1. 解压所有 zip
mkdir _zip_inspect_code _zip_inspect_refs
unzip "情感分析代码.zip" -d _zip_inspect_code/
unzip "参考文献-情感分析.zip" -d _zip_inspect_refs/

# 2. 列文件
ls _zip_inspect_code/        # → sentiment.py, *.csv, 原生 pie.png
ls _zip_inspect_refs/        # → 3 篇 PDF
```

## 教师 sentiment.py 提取要点

读 sentiment.py 后必须记录：
- 模型 ID：`ethanyt/guwen-sent`
- 5 类概率列名：`["Neg Plus_概率", "Neg_概率", "Neu_概率", "Pos_概率", "Pos Plus_概率"]`
- 分类列：`情感分类_数字` (0-4)
- 教师原生输出：`唐诗300_with_sentiment.csv` + 饼图 + 统计 csv

→ 这些列名直接写入 `core/palette.py` 的 `PROB_COLS`。

## 教师 PPT 第 22 讲 提取要点

逐页 Read PDF：
- 第 5 页 `lockdown trajectory` 风格 → **05 号时间曲线直接对标**
- 第 6/7 页地图样式 → **06 号地图直接对标**

设计说明 IV 章必须 cite 这两页。

## 3 篇参考论文方法摘要

各篇至少读 abstract + 方法节，写成 `_source_notes.md`：

```markdown
# Paper 1 · LIWC + Embedding Emotionality
- 方法：LIWC 字典法 + 词嵌入"情感性轴"投影
- 关键图：actor profile（多维实体画像）
- 借鉴：sent_score 加权 ↔ emotionality 投影；雷达图 ↔ actor profile

# Paper 2 · Nature COVID BERT + RDD + SCM
- 方法：BERT 打情感分 + Regression Discontinuity / Synthetic Control
- 关键图：lockdown trajectory（时间 + 政策事件标注 + 置信带）
- 借鉴：05 号时间曲线对标其 trajectory；模型选 BERT 同路线

# Paper 3 · Evol 古典文学历时性词汇演变（最直接）
- 方法：dynasty-level timestamp + Diachronic n-gram + Word co-occurrence + Lexical semantic shift
- 借鉴最深：05 号朝代背景 / 07 号 Diachronic / 08 号 cooccurrence
```

## 红线（唐诗实例）

- 不能跳过任何一篇论文——3 篇全读完才能进阶段 1
- 教师原生 pie 图和 csv **必须**保留到最终交付（用「原生_」前缀）
- 教师 sentiment.py 的列名约定不要改——`core/palette.py` 严格沿用
