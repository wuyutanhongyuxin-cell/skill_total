# 阶段 2 实例 · 唐诗作业的设计说明填法

> 配合 `design-doc-template.md` 看，展示实例化后的样子。完整版见 `visualization/设计说明.md`（本项目实交付的那一份）。

## 文件清单表实例

```markdown
| 文件 | 类型 | 尺寸 / 大小 |
|---|---|---|
| `00_唐诗情感图谱_dashboard.png` | A3 横版主 Dashboard（10 面板） | 4961×3508 @300dpi |
| `01_情感分布环形图.png` | 独立精修 · 环形饼图 | 2400×2400 |
| `02_诗人情感热力图.png` | 独立精修 · 诗人 × 情感热力图 | 3600×2400 |
| `03_唐诗情感词云_总.png` | 独立精修 · 主词云（扇形遮罩） | 2400×1600 |
| `03b_唐诗情感词云_5分类拼图.png` | 独立精修 · 5 子词云拼图 | 3600×2400 |
| `04_朝代情感sankey.png` | 独立精修 · 朝代 × 情感 Sankey | 3600×2400 |
| `05_朝代情感时间曲线.png` | 独立精修 · 唐 618-907 时间轴 + 安史之乱标注 | 3600×2400 |
| `06_诗人籍贯地图.png` | 独立精修 · 唐 77 诗人地理分布 + 双河骨架 | 3600×2400 |
| `07_关键意象朝代演变.png` | 独立精修 · 12 意象 × 4 朝代 Diachronic 曲线 | 4500×2100 |
| `08_高频字共现网络.png` | 独立精修 · Top 30 字共现网络 + 力导向布局 | 3600×2400 |
| `原生_唐诗情感分布饼图.png` | sentiment.py 原生输出（教材范式） | 800×600 |
| `原生_唐诗情感统计.csv` | sentiment.py 原生输出 | — |
```

## 「对照参考文献」唐诗实参

```markdown
## 四、对照参考文献

本作业的可视化方法选择对标了教师提供的 3 篇参考文献：

### Paper 1 · LIWC + Embedding Emotionality 政治语言研究

**方法**：LIWC 字典法 + 词嵌入的"情感性轴"投影（emotionality dimension）。
**本作业借鉴**：
- "加权情感分" `sent_score = p·W` 与 emotionality 投影同构 —— 都是把多类离散
  标签投到连续标量轴上做后续可视化。
- Top 诗人雷达图（Dashboard 主视觉右）对照其 Figure 2 风格的多维 actor profile。

### Paper 2 · Nature COVID 政府公告情感影响（BERT + RDD + SCM）

**方法**：用 BERT 类模型对文本打情感分，再做 Regression Discontinuity / Synthetic Control 因果推断。
**本作业借鉴**（教师 PPT 第 22 讲展示的图正源自此文）：
- **05 号朝代时间曲线** 直接对标其 **lockdown trajectory** 风格 —— 时间轴 +
  重大事件（安史之乱 ↔ lockdown 实施日）的垂直阴影标注 + ±1σ 置信带。
- 模型选择：`ethanyt/guwen-sent` 即 BERT 在古文情感语料上微调的版本，
  与 Paper 2 的 BERT 路线一致。

### Paper 3 · Evol 古典文学历时性词汇演变项目（最直接对应）

**方法**：用 **dynasty-level timestamp**（朝代时间戳）而非公元年份做古代文献时间维度的归一化，主推三大可视化：
1. Diachronic n-gram frequency tracking
2. Word co-occurrence network
3. Lexical semantic shift

**本作业借鉴**（最深、最直接）：
- **05 号** 用朝代分段背景而非连续公元年份 —— Paper 3 论证朝代是更符合古代
  文献分布的时间单元。
- **07 号关键意象朝代演变曲线** 直接复刻 Paper 3 的 Diachronic n-gram 方法，
  公式与归一化策略与原文一致（每千字频次）。
- **08 号高频字共现网络** 直接复刻 Paper 3 的 Word co-occurrence network，
  节点-边 schema 一致，边阈值参数 `MIN_EDGE_COUNT=5` 取自 Paper 3 推荐区间。
- **06 号诗人籍贯地图** 对应 Paper 3 的地理维度补充 —— 时间 + 地理两条正交轴。
```

## 双向锚点验证（唐诗实例）

| 设计说明 IV 章说"借鉴" | 图副标实际写了 | 锚点状态 |
|---|---|---|
| 05 号 ↔ Paper 2 lockdown trajectory | "method ref: Lockdown trajectory style" | ✅ |
| 07 号 ↔ Paper 3 Diachronic n-gram | "method ref: Evol — Diachronic n-gram frequency" | ✅ |
| 08 号 ↔ Paper 3 Word co-occurrence | "method ref: Evol — Word co-occurrence network" | ✅ |

## 红线（唐诗实例）

- Paper 3 是「最直接对应」必须放最后并标注
- 必须 cite 教师 PPT 第 22 讲，因为 05 号图是直接对标其展示页
- "受启发"「类似」等含糊用词在最终设计说明里 0 出现
