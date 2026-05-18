# 唐诗作业 reference 章节索引

> 这是 `bert-sentiment-viz-deliverable` skill 的**双层结构下层**。
>
> 上层（SKILL.md + 5 个通法支撑文档）是**通法骨架**——适用于任何 BERT 情感分析可视化交付包。
>
> 本目录是**唐诗实例**——展示通法在 SJTU 第 21 讲 · 作业 4「唐诗三百首情感分析」上具体怎么填参数、踩过哪些坑。

## 阅读路径

| 看完通法的哪节 → | 看本目录的哪份 |
|---|---|
| SKILL.md § 阶段 0 源材料阅读 | `01-source-materials.md` |
| SKILL.md § 阶段 1 核心架构 + `code-architecture.md` | `02-core-modules.md` |
| SKILL.md § 阶段 2 设计 + `design-doc-template.md` + `paper-alignment-template.md` | `03-design-doc.md` |
| SKILL.md § 阶段 3 Dashboard | `04-dashboard-spec.md` |
| SKILL.md § 阶段 4 精修图 | `05-figures-01-to-08.md` |
| SKILL.md § 阶段 5 测试 + `checklist.md` | （无单独 reference，按 checklist 走） |
| SKILL.md § 阶段 6 打包 + `packaging.md` | （无单独 reference，rebuild_zip.py 是原型） |

## 唐诗实例的关键参数（速查）

| 维度 | 唐诗实参 |
|---|---|
| 模型 | `ethanyt/guwen-sent` (BERT 古文 5 分类) |
| 语料 | 唐诗三百首 N=300 |
| 实体 | 77 位诗人 |
| 离散映射 | 4 朝代（初/盛/中/晚）+ 未细分 |
| 朝代覆盖率 | 77/77 = 100% |
| 地理映射 | 74/77 = 96.1%（未覆盖 不详/无名氏/西鄙人） |
| 时间范围 | 618-907（唐） |
| 重大事件 | 安史之乱 755-763 |
| Top 3 多产 | 杜甫 39 / 李白 33 / 王维 29 |
| 关键意象 | 12 字 = 自然 4 + 情绪 4 + 主题 4 |
| 共现 Top N | 30 字，min_edge=5 |
| 参考文献 | 3 篇（LIWC+Emb / BERT+RDD+SCM Nature / Evol 古典文学） |
| 最直接对应 | Paper 3 Evol（07/08 直接复刻） |

## 唐诗实例踩过的坑

1. **京兆 9 位诗人坐标重叠** → 用 `jitter_same_point` 圆周均布，radius = 0.30 + 0.05*n
2. **cartopy 依赖太重** → 改手绘 17 点唐土轮廓 + 黄河 11 点 + 长江 9 点
3. **Windows 中文文件名 zip 乱码** → 验证 `flag_bits & 0x800` UTF-8 标志位
4. **教师原生 pie 图差点被删** → 必须保留为「原生_*.png」证明保留教师范式
5. **设计说明 IV 章曾经只列标题** → 重写为三段式（方法 / 借鉴点 / 对应图）
6. **07/08 一开始没做** → Paper 3 借鉴变空头支票，补做后才闭环
7. **共现网络位置每次变** → `nx.spring_layout(seed=42)` 必须固定
8. **05 号 y 轴 autoscale 把情感范围压扁** → 固定 [-2, +2]
