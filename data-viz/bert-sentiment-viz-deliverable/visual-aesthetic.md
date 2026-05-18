# 视觉风格规范

> 整套作业要"一眼可识别"，所有图必须共享同一套视觉语法。

## 1. 五情感色映射（强约束）

```python
PALETTE_5 = {
    "Neg Plus": "#003472",   # 极悲
    "Neg":      "#425066",   # 哀
    "Neu":      "#75878A",   # 中
    "Pos":      "#D9B611",   # 喜
    "Pos Plus": "#FF461F",   # 极喜
}
```

- **冷→暖即悲→喜**：极悲是最深的冷色，极喜是最艳的暖色
- **中性是低饱和灰色**：让中性样本"退到背景"，让两端样本"跳出"
- **5 色按情感梯度排列**，不可对换顺序

### 中国传统色版本（推荐）

| 序 | HEX | 中文名 | 拼音 |
|---|---|---|---|
| 0 | `#003472` | 花青 | huā qīng |
| 1 | `#425066` | 黛蓝 | dài lán |
| 2 | `#75878A` | 苍色 | cāng sè |
| 3 | `#D9B611` | 秋香色 | qiū xiāng |
| 4 | `#FF461F` | 朱砂 | zhū shā |

色值来源：zhongguose.com / color5.com 实证 HEX。**红线**：不要随手编色值，必须有可追溯来源。

## 2. 辅助色

```python
BACKGROUND   = "#F2ECDE"   # 缟（底）
CARD_BG      = "#EAE3CC"   # 米（卡片）
GRID_MAIN    = "#D6CBB0"
GRID_MINOR   = "#BFB49A"
TEXT_TITLE   = "#1C1A17"   # 几近黑（标题）
TEXT_BODY    = "#3B3A35"   # 深褐（正文）
TEXT_NOTE    = "#7A7468"   # 灰褐（注脚）
SEAL_RED     = "#9E2A21"   # 钤印红
BORDER       = "#8C7A4F"   # 古铜
```

**红线**：背景必须**温暖低饱和**而非纯白——纯白让中国风视觉无所依托。

## 3. 字体三级体系

| 角色 | 用途 | 首选 |
|---|---|---|
| `title` | 大标题 / 印章字 | 华文隶书 STLITI |
| `body` | 副标 / 正文 / 注脚 | 华文楷体 STKAITI |
| `data` | KPI 数字 / 标签 | 微软雅黑粗体 msyhbd |

**5 级降级机制**：见 `code-architecture.md` § 1。

**红线**：
- 标题与正文必须**不同字体**才有层次感
- 数字必须**粗体黑体类**才有"数据感"——用楷体写数字会显得软

## 4. 连续 colormap（情感分专用）

```python
import matplotlib.colors as mcolors
cmap = mcolors.LinearSegmentedColormap.from_list(
    "sent", P.PALETTE_5_LIST, N=256,
)
norm = mcolors.Normalize(vmin=-2.0, vmax=2.0)
# 取色：cmap(norm(sent_score_value))
```

**为什么 N=256**：让插值平滑，避免离散块感。

**红线**：
- vmin/vmax **必须**固定为 -2.0 / +2.0
- 不可用 df["sent_score"].min() / max()——会让不同图之间颜色不可比
- colormap 名称固定叫 `"sent"`（语义清楚），不要用 `"my_cmap"`

## 5. dpi 与画布

| 用途 | figsize | dpi | 出图像素 |
|---|---|---|---|
| Dashboard A3 横版 | (16.5, 11.7) | 300 | 4961 × 3508 |
| 精修单图（横版） | (12, 8) | 300 | 3600 × 2400 |
| 精修单图（方版） | (8, 8) | 300 | 2400 × 2400 |
| 精修单图（横长） | (15, 7) | 300 | 4500 × 2100 |
| 教师原生兼容 | (8, 6) | 100 | 800 × 600 |

**红线**：savefig 必须 `dpi=300, bbox_inches="tight", facecolor=P.BACKGROUND, pad_inches=0.3`。

## 6. 标题排版规则

```python
# 主标题：fig.text 而非 ax.set_title（独立控制位置）
fig.text(0.5, 0.97, "中文主标题",
    fontproperties=P.get_font_prop("title", 22, weight="bold"),
    color=P.TEXT_TITLE, ha="center", va="top")

# 英文副标 + 方法溯源
fig.text(0.5, 0.93, "English Subtitle (method ref: <Paper>)",
    fontproperties=P.get_font_prop("body", 11), style="italic",
    color=P.TEXT_NOTE, ha="center", va="top")
```

**红线**：
- 英文副标必须斜体（`style="italic"`）
- 「method ref: <Paper>」括号注释**必须**出现在借鉴某论文方法的图上——这是与设计说明「对照参考文献」章节的双向锚点

## 7. Footer 规则（数字结论）

```python
fig.text(0.5, 0.02, "<数据来源> · <Top N 结论> · <方法注>",
    fontproperties=P.get_font_prop("body", 8),
    color=P.TEXT_NOTE, ha="center", va="bottom")
```

**红线**：footer 必须含**至少一个数字**——空泛的"数据：xxx.csv"不算 insight。
范例：「Top 3 最强共现：「人-山」62首 · 「山-月」55首 · 「人-月」51首」

## 8. spine / 网格

```python
# rcParams 已设
"axes.spines.top":   False,
"axes.spines.right": False,
"axes.spines.left":  True,
"axes.spines.bottom": True,
"grid.linestyle":   ":",   # 点线，最低视觉重量
"grid.alpha":       0.7,
```

某些图（共现网络 / Sankey）需要去掉所有 spine：

```python
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([]); ax.set_yticks([])
```

## 9. 中文负号修复

```python
"axes.unicode_minus": False    # 必有！否则负数轴标变方框
```

## 10. 印章 / 装饰

钤印红方块（用于标题旁的"模型/工具"角标）：

```python
from matplotlib.patches import FancyBboxPatch
seal = FancyBboxPatch((x, y), w, h,
    boxstyle="round,pad=0.005,rounding_size=0.015",
    facecolor=P.SEAL_RED, edgecolor=P.TEXT_TITLE, linewidth=1.5,
    transform=ax.transAxes)
ax.add_patch(seal)
```

KPI 卡片：

```python
card = FancyBboxPatch((0.05, 0.05), 0.9, 0.9,
    boxstyle="round,pad=0.01,rounding_size=0.04",
    facecolor=P.CARD_BG, edgecolor=P.BORDER, linewidth=0.8)
```

## 11. 同套色多图的协调红线

- 所有图共享 `theme.apply_ancient_theme()` 一次
- 所有"情感色"用法**必须**走 `PALETTE_5_LIST` 或 cmap，不可直接 `"red"` / `"blue"`
- 中性灰（`#75878A`）只用来标"中性情感"，**不**当作通用灰色背景使
- 朱砂（`#FF461F` / `#9E2A21`）只用于"喜情感"和"钤印/警告标记"两种场景，避免视觉混淆

## 12. 视觉自检（每张图渲染后必做）

用 Read 工具打开 PNG 看：

- [ ] 标题中文不是方框
- [ ] 副标英文斜体显示正常
- [ ] colormap 方向正确（左/下=冷=悲，右/上=暖=喜）
- [ ] 负数轴标不是方框
- [ ] 网格点线低调，不喧宾夺主
- [ ] Footer 含数字结论
- [ ] 背景米色而非纯白
- [ ] 边距未把标题挤出画面
