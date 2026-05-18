# 终局自检清单（6 阶段）

> 在 SendUserFile 前**逐项**打钩。任何一项未过 → 回相应阶段修，绝不带缺口交付。

## 阶段 0 · 源材料阅读

- [ ] 教师 zip / 原生脚本目录已全部解压并列文件
- [ ] 每个 .py 至少 Read 一次，提取它输出什么、用什么模型
- [ ] 教师 PDF 每页都看过，分值分布与要求清单记到 `_source_notes.md`
- [ ] 参考论文 zip 全部解压，每篇 PDF 至少读 abstract + 方法节
- [ ] 原始 CSV / JSON 的列名、行数、缺失情况确认
- [ ] `_source_notes.md` 含「每份材料 → 一句关键约束」

## 阶段 1 · 核心架构

- [ ] `core/__init__.py` 存在（让 import 工作）
- [ ] `core/palette.py` 含 `PALETTE_5_LIST`、`WEIGHTS`、`PROB_COLS`、`get_font_prop`
- [ ] `core/theme.py` 含 `apply_ancient_theme()` 一键应用
- [ ] `core/data_loader.py` 的 `load_poems` 算出 `sent_score`、`sent_confidence`、`char_count`
- [ ] sent_score 范围实测 ∈ [-2, +2]（跑 `python -m core.data_loader`）
- [ ] 离散映射模块（如 `dynasty.py`）的 `coverage_report` 给出覆盖率
- [ ] 字体降级实测：在终端跑 `python -m core.palette` 看到 FONT_TITLE / BODY / DATA 路径全非 None
- [ ] STOPWORDS 含：文言虚词 + 标点 + 数字 + 常见代词

## 阶段 2 · 设计与对照参考文献

- [ ] 已用 `superpowers:brainstorming` 提出 2-3 候选方案
- [ ] 用户已批准设计方向
- [ ] 设计说明.md 含 4 章节：作品说明 / 算法说明 / 阅读指南 / **对照参考文献**
- [ ] 文件清单表所有图都列在内（含原生产物）
- [ ] 「对照参考文献」每篇论文写了**方法** + **借鉴点（明示对应到 0X 号图）**
- [ ] 已用 `superpowers:writing-plans` 出 plan 文件

## 阶段 3 · Dashboard

- [ ] dashboard.py 入口 `from core import palette / theme / data_loader / 离散映射`
- [ ] A3 横版 figsize=(16.5, 11.7) dpi=300，验证产物 ≈ 4961 × 3508
- [ ] 至少 6 类面板：标题 / KPI / 主视觉 / 二级 / 时间或地理 / 极端样本
- [ ] 印章式标题用了 FancyBboxPatch + 朱砂底
- [ ] dashboard 渲染后 Read 一次，确认全部中文无方框

## 阶段 4 · 精修图

- [ ] N 张精修图全部 ≥ 3600 × 2400 @300dpi
- [ ] 每张图 `from core import` 而非自定义颜色 / 字体
- [ ] colormap 用 `LinearSegmentedColormap.from_list("sent", PALETTE_5_LIST, N=256)`
- [ ] `Normalize(vmin=-2.0, vmax=2.0)` 固定，不用 df 实测
- [ ] 每张图标题 + 英文副标 + footer 含数字结论
- [ ] 时间曲线图含重大事件 axvspan + 标注
- [ ] 地图图用手绘 polygon + jitter_same_point
- [ ] 共现网络图固定 `seed=42`
- [ ] 历时 n-gram 图用每千字归一化（freq / total_chars × 1000）
- [ ] **每张图 Read 一次确认视觉**（不只看 stdout）

## 阶段 5 · 测试

- [ ] `tests/test_palette.py` 测字体路径 + 5 色长度
- [ ] `tests/test_data_loader.py` 测 sent_score 范围 + 列存在
- [ ] `tests/test_dynasty.py` 测离散映射覆盖率
- [ ] 跑 `pytest visualization/tests/ -v` 全部通过
- [ ] 实测覆盖率与设计说明里写的数字一致（如 96.1%）

## 阶段 6 · 打包

- [ ] zip 结构：设计说明.md 在顶层 + 代码/ + 图片/
- [ ] 代码/ 含 dashboard.py + core/ + extras/ + tests/
- [ ] 图片/ 含所有 0N_*.png + 原生_*.png + 原生_*.csv
- [ ] 教师原生产物（pie 图 / csv）**没被删掉**
- [ ] `zipfile.ZIP_DEFLATED, compresslevel=6`
- [ ] **bit 0x800 验证**：`all((zi.flag_bits & 0x800) for zi in z.infolist())` = True
- [ ] zip 大小记录到交付 caption 里

## 终局

- [ ] 上述全部打钩
- [ ] SendUserFile 用 `status="proactive"`
- [ ] caption 写明：大小 / 文件数 / 包含什么
- [ ] 不在终端响应里附加"接下来要做 X"——任务结束就是结束

## 失败响应

任一项打不上钩：
1. **不**绕过、**不**写 TODO、**不**称"基本完成"
2. 回到对应阶段重做
3. 重做完重跑这份清单
4. 反复直到全打钩
