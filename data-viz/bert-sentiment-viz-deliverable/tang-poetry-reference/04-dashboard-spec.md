# 阶段 3 实例 · 唐诗 Dashboard 10 面板布局

> 配合 SKILL.md § 阶段 3 看。

## 10 面板 GridSpec 实参

```python
fig = plt.figure(figsize=(16.5, 11.7), dpi=300)   # A3 横版 4961×3508
gs = GridSpec(
    nrows=6, ncols=12, figure=fig,
    hspace=0.55, wspace=0.45,
    height_ratios=[0.6, 0.8, 2.0, 1.8, 1.8, 1.4],
)
```

| 行 | 列范围 | 面板 | 函数 |
|---|---|---|---|
| 0 | 全幅 | A · 印章式标题 | `render_row_a_title(fig, gs, df)` |
| 1 | 全幅 → 5 卡片 | B · KPI 条 (300首/77人/5情感/均值/最高产) | `render_row_b_kpi(fig, gs, df)` |
| 2 | 0:4 | C-1 · 5 情感环形饼 | `render_panel_ring(fig, gs[2, 0:4], df)` |
| 2 | 4:8 | C-2 · 300 首情感分排序色带 | `render_panel_strip(fig, gs[2, 4:8], df)` |
| 2 | 8:12 | C-3 · Top 4 诗人雷达 | `render_panel_radar(fig, gs[2, 8:12], df)` |
| 3 | 0:7 | D-1 · 诗人 Top 20 堆叠条 | `render_panel_poet_bar(fig, gs[3, 0:7], df)` |
| 3 | 7:12 | D-2 · 5 子词云缩略 | `render_panel_wc_thumb(fig, gs[3, 7:12], df)` |
| 4 | 0:7 | E-1 · 朝代 × 情感 Sankey | `render_panel_sankey(fig, gs[4, 0:7], df)` |
| 4 | 7:12 | E-2 · 朝代×情感矩阵 | `render_panel_matrix(fig, gs[4, 7:12], df)` |
| 5 | 0:6 | F-1 · 最哀 Top 5 卡 | `render_panel_extreme_neg(fig, gs[5, 0:6], df)` |
| 5 | 6:12 | F-2 · 最喜 Top 5 卡 | `render_panel_extreme_pos(fig, gs[5, 6:12], df)` |

## 印章式标题唐诗实参

```python
seal = FancyBboxPatch((0.01, 0.15), 0.07, 0.7,
    boxstyle="round,pad=0.005,rounding_size=0.015",
    facecolor=P.PALETTE_5["Pos Plus"],   # 朱砂
    edgecolor=P.TEXT_TITLE, linewidth=1.5,
    transform=ax.transAxes)
ax.add_patch(seal)
ax.text(0.045, 0.5, "唐诗\n三百首",     # 印章字
    fontproperties=P.get_font_prop("title", 18, weight="bold"),
    color="white", ha="center", va="center",
    transform=ax.transAxes, linespacing=0.9)
ax.text(0.10, 0.65, "情感图谱",          # 主标
    fontproperties=P.get_font_prop("title", 42, weight="bold"),
    color=P.TEXT_TITLE, ha="left", va="center", transform=ax.transAxes)
ax.text(0.10, 0.25, "An Emotional Atlas of 300 Tang Poems",   # 英文副标
    fontproperties=P.get_font_prop("body", 16), style="italic",
    color=P.TEXT_NOTE, ha="left", va="center", transform=ax.transAxes)
ax.text(0.99, 0.5, "guwen\nsent\n模型",  # 右上模型角标
    fontproperties=P.get_font_prop("body", 9, weight="bold"),
    color=P.SEAL_RED, ha="right", va="center", transform=ax.transAxes,
    linespacing=1.2,
    bbox=dict(boxstyle="round,pad=0.4", facecolor=P.BACKGROUND,
              edgecolor=P.SEAL_RED, linewidth=1.2))
```

## KPI 实参（5 卡片内容）

```python
kpis = [
    (f"{len(df)}",                       "首诗",       "唐诗三百首总量"),
    (f"{len(stats['poet_count'])}",      "位诗人",     "覆盖唐代代表诗人"),
    ("5",                                "情感等级",   "Neg+/Neg/Neu/Pos/Pos+"),
    (f"{df['sent_score'].mean():+.2f}",  "加权情感分", "全集均值 ∈ [-2, +2]"),
    (f"{top2[0]} · {top2[1]}",           "最高产诗人", f"{n1} / {n2} 首"),
]
```

## Sankey 实现要点

Sankey 用自定义 bezier band：

```python
def _bezier_band(x0, y0t, y0b, x1, y1t, y1b, color, alpha=0.55):
    cx = (x0 + x1) / 2
    verts = [(x0, y0t), (cx, y0t), (cx, y1t), (x1, y1t),
             (x1, y1b), (cx, y1b), (cx, y0b), (x0, y0b), (x0, y0t)]
    codes = [MplPath.MOVETO,
             MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
             MplPath.LINETO,
             MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
             MplPath.CLOSEPOLY]
    return PathPatch(MplPath(verts, codes),
                     facecolor=color, edgecolor="none", alpha=alpha)
```

不依赖 plotly——纯 matplotlib 实现，输出 PNG 即可。

## 红线（唐诗实例）

- KPI 第 5 卡的"最高产诗人"用「李白·杜甫」拼接而非只显 Top 1——避免只展示极值
- Sankey 朝代顺序按 DYNASTY_ORDER 而非按字典序，否则视觉混乱
- 极端诗双栏（最哀/最喜 Top 5）每首附作者+前 14 字——让评分老师能文学层面验证模型
