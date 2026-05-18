# 阶段 4 实例 · 唐诗 8 张精修图填法

> 配合 SKILL.md § 阶段 4 看，每张图给关键实参 + 视觉要点。

## 01 · 情感分布环形图（2400×2400）

```python
# 环形参数
start_angle = 90      # 12 点方向起笔
gap_deg = 2           # 扇区间隔
inner_radius = 0.55   # 中空
outer_radius = 0.95

# 5 扇区 + 引线 + 代表诗
for i in range(5):
    pct_i = counts.iloc[i] / total
    sweep = pct_i * 360 - gap_deg
    wedge = Wedge(center=(0,0), r=outer_radius,
                  theta1=start_angle-sweep, theta2=start_angle,
                  width=outer_radius-inner_radius,
                  facecolor=PALETTE_5_LIST[i],
                  edgecolor=BACKGROUND, linewidth=2)
```

**找代表诗**：取每类 `sent_confidence` 最大的那首 + 前 14 字片段。

## 02 · 诗人 × 情感热力图（3600×2400）

聚合：`poet_cross = pd.crosstab(df["作者"], df["情感分类_数字"])`

矩阵着色：每个格用 `PALETTE_5_LIST[c]` 着色，alpha = count / row_max。

行序按总诗数降序，列序按 0-4 情感序。

## 03 · 词云 · 扇形遮罩（2400×1600）

```python
def make_fan_mask(w=1600, h=1200):
    img = Image.new("L", (w, h), 255)
    ImageDraw.Draw(img).ellipse(
        [int(w*0.05), int(h*0.05), int(w*0.95), int(h*0.95)], fill=0)
    return np.array(img)

# color_func 按字号分段选色（大字用暖色，小字用冷色）
def make_multi_color_func():
    palette = [PALETTE_5["Pos Plus"], PALETTE_5["Pos"],
               PALETTE_5["Neg Plus"], PALETTE_5["Neg"]]
    def _fn(word, font_size, position, orientation, random_state=None, **kw):
        if font_size > 80:   return palette[_pick(random_state, 2)]
        elif font_size > 40: return palette[_pick(random_state, 4)]
        else:                return palette[2 + _pick(random_state, 2)]
    return _fn

wc = WordCloud(font_path=P.FONT_BODY, width=w, height=h,
               background_color=P.BACKGROUND, mask=mask,
               max_words=300, min_font_size=10, max_font_size=180,
               prefer_horizontal=0.88, relative_scaling=0.5,
               collocations=False, color_func=color_func,
               random_state=42, margin=4)
wc.generate_from_frequencies(features["full_freq"])
```

**红线**：`collocations=False` 必须有——否则 wordcloud 会自动合并双字，与我们手工 bigram 重复。

## 03b · 5 子情感词云拼图（3600×2400）

分 5 子图，每张用 `make_color_func(PALETTE_5_LIST[i])` 单色调，按情感类切片：

```python
for c in range(5):
    sub_df = df[df["情感分类_数字"] == c]
    sub_features = DL.text_features(sub_df)
    # render to ax[r,c]
```

## 04 · 朝代 × 情感 Sankey（3600×2400）

5 列朝代 × 5 列情感，bezier band 流量 = `dynasty_sent_cross[d, s]`。

按 DYNASTY_ORDER 列朝代，按 0-4 列情感。颜色取情感色（流的颜色由终点决定）。

## 05 · 朝代情感时间曲线（3600×2400）

```python
DYNASTY_YEARS = {
    "初唐": (618, 712), "盛唐": (713, 766),
    "中唐": (766, 836), "晚唐": (836, 907),
}
DYNASTY_BG_COLORS = {
    "初唐": "#F2ECDE", "盛唐": "#EBE3CC",
    "中唐": "#E4DABA", "晚唐": "#DBCFA5",   # 渐深
}

# 4 朝代分段背景
for d in valid:
    start, end = DYNASTY_YEARS[d]
    ax.axvspan(start, end, facecolor=DYNASTY_BG_COLORS[d], alpha=0.6, zorder=0)
    ax.text((start+end)/2, 1.85, d, ...)
    ax.text((start+end)/2, 1.65, f"{start}–{end}", ...)

# 安史之乱阴影
ax.axvspan(755, 763, facecolor=SEAL_RED, alpha=0.18, zorder=1)
ax.text(759, -1.85, "安史之乱\n755–763", color=SEAL_RED, ...)

# 4 个点 + 置信带
ax.fill_between(xs, means-stds, means+stds, color=PALETTE_5["Neg"], alpha=0.20)
ax.plot(xs, means, color=SEAL_RED, linewidth=3, marker="o", markersize=14,
        markerfacecolor=PALETTE_5["Pos Plus"], markeredgecolor=TEXT_TITLE,
        markeredgewidth=1.5)

# 数据点标注（N + mean + σ）
for x, m, s, n, d in zip(xs, means, stds, ns, valid):
    ax.annotate(f"{d}\nN={n}\nmean={m:+.2f}\nσ={s:.2f}",
                xy=(x, m), xytext=(x, m+0.55), ...)
```

**红线**：`y` 轴必须固定在 `[-2, 2]`（情感分定义域），不要用 autoscale。

## 06 · 诗人籍贯地图（3600×2400）

```python
# 手绘唐土轮廓（17 点）
TANG_OUTLINE = [
    (92.0, 39.5), (95.0, 42.0), (104.0, 41.5), (114.0, 41.0),
    (122.0, 40.5), (123.0, 35.5), (121.5, 31.0), (121.0, 28.0),
    (118.5, 24.0), (113.5, 22.0), (108.0, 21.5), (104.0, 22.5),
    (100.5, 25.5), (99.5, 30.0), (97.0, 32.0), (93.0, 35.0), (92.0, 39.5),
]
# 黄河（11 点）+ 长江（9 点）主干道：见 06_poet_birthplace_map.py
YELLOW_RIVER = [...]
YANGTZE_RIVER = [...]

# 古地理标签
GEO_LABELS = [
    (108.94, 34.27, "长安"), (112.45, 34.62, "洛阳"),
    (104.70, 31.78, "蜀"),   (120.59, 31.30, "江南"),
    (113.60, 24.82, "岭南"), (114.49, 36.79, "河北"),
    (102.64, 37.93, "陇右"),
]

# 同坐标 jitter
def jitter_same_point(records):
    bucket = {}
    for r in records:
        key = (round(r["lat"], 2), round(r["lon"], 2))
        bucket.setdefault(key, []).append(r)
    out = []
    for _, group in bucket.items():
        n = len(group)
        if n == 1: out.append(group[0]); continue
        radius = 0.30 + 0.05 * n     # 1° ≈ 110 km
        for i, r in enumerate(group):
            theta = 2 * math.pi * i / n
            r2 = dict(r)
            r2["lat"] += radius * math.sin(theta)
            r2["lon"] += radius * math.cos(theta)
            out.append(r2)
    return out

# 散点（大小 = 诗数，颜色 = 平均情感分）
sizes = [80 + 220 * math.sqrt(r["n"]) for r in records]
colors = [cmap(norm(r["avg_sent"])) for r in records]

# Top 8 引线（避免互相覆盖：8 个固定方位角）
angles = [40, 90, 140, 200, 250, 305, 20, 160]
for r, ang in zip(top_recs, angles):
    rad = math.radians(ang)
    dx, dy = 4.5 * math.cos(rad), 3.0 * math.sin(rad)
    # annotate with arrow ...

# 黄河金线 #C9A227 / 长江蓝线 #4F7DA5
ax.plot(yr_xs, yr_ys, color="#C9A227", linewidth=2.5, alpha=0.85,
        zorder=2, solid_capstyle="round")
ax.plot(yz_xs, yz_ys, color="#4F7DA5", linewidth=2.5, alpha=0.85,
        zorder=2, solid_capstyle="round")

ax.set_xlim(88, 130); ax.set_ylim(20, 44)
ax.set_aspect("equal", adjustable="box")
```

**红线**：
- **不**用 cartopy/geopandas——依赖太重，手绘多边形即可
- `set_aspect("equal")` 必须有，否则地图变形
- 黄河必须是金色（文化意象），长江必须是水蓝

## 07 · 关键意象朝代演变（4500×2100）

```python
KEYWORDS_THEMED = {
    "自然": {"color": "#D9B611", "words": ["月", "风", "花", "春"]},
    "情绪": {"color": "#003472", "words": ["愁", "泪", "孤", "思"]},
    "主题": {"color": "#9E2A21", "words": ["酒", "边", "乡", "客"]},
}
DYNASTIES = ["初唐", "盛唐", "中唐", "晚唐"]

# 每千字归一化
freq_norm = count(word in dynasty_text) / total_chars(dynasty_text) * 1000

# 3 子图横排，每图一主题（4 字 × 4 朝代）
fig, axes = plt.subplots(1, 3, figsize=(15, 7), dpi=300, sharey=False)

# 同主题内 4 字用线型 × 标记循环 + 同色梯度
styles = ["-", "--", "-.", ":"]
markers = ["o", "s", "D", "^"]
shade_factor = 0.55 + 0.15 * i      # 同主题色越来越浅

# 安史之乱垂直阴影（盛唐 ↔ 中唐 分界 x=1.5）
ax.axvspan(1.45, 1.55, color=SEAL_RED, alpha=0.22, zorder=1)
```

**Footer insight**（必须含数字）：

```python
insights_sorted = sorted(insights, key=lambda x: -abs(x["delta"]))[:3]
insight_str = " · ".join(
    f"「{x['word']}」{x['init']:.1f}→{x['final']:.1f}‰ (峰{x['peak']})"
    for x in insights_sorted
)
# 例: 「孤」1.8→3.5‰ (峰晚唐) · 「春」3.0→7.6‰ (峰晚唐) · 「边」5.5→1.5‰ (峰盛唐)
```

## 08 · 高频字共现网络（3600×2400）

```python
TOP_N_CHARS = 30
MIN_EDGE_COUNT = 5

# 共现统计：对每首诗取 char_set，combinations 计数
for _, row in df.iterrows():
    chars = _poem_char_set(row["内容"]) & top_set
    for a, b in combinations(sorted(chars), 2):
        edge_counter[(a, b)] += 1

# 节点元数据：freq + 平均情感分
G.add_node(c, freq=char_counter[c], sent=char_sent_sum[c]/char_doc_count[c])

# 力导向布局（seed 固定）
pos = nx.spring_layout(G, k=1.2, iterations=200, seed=42, weight="weight")

# 节点：大小 ∝ 字频，颜色 ∝ 情感分均值
size = 700 + 2200 * (freq / max_freq)
color = cmap(norm(sent))

# Top 5 度数节点：金色描边 + 名次
edgecolors = "#C9A227" if is_top else TEXT_TITLE
linewidths = 2.4 if is_top else 0.7
# 标 "#1" ~ "#5" 名次

# 边：粗 ∝ 共现强度
lw = 0.5 + 3.5 * ratio
alpha = 0.18 + 0.55 * ratio
```

**Footer insight**：
```python
# Top 3 最强边
top_edges = sorted(edge_counter.items(), key=lambda x: -x[1])[:3]
top_edge_str = " · ".join(f"「{a}-{b}」{c}首" for (a, b), c in top_edges)
# 例: 「人-山」62首 · 「山-月」55首 · 「人-月」51首

# Top 5 度数
top_degree_str = " · ".join(f"#{i+1} 「{n}」({int(d)})" ...)
```

## 8 张图共享的标题模式

```python
fig.text(0.5, 0.97, "<中文主标题>",
    fontproperties=P.get_font_prop("title", 22, weight="bold"),
    color=P.TEXT_TITLE, ha="center", va="top")
fig.text(0.5, 0.93, "<English subtitle> (method ref: <Paper>)",
    fontproperties=P.get_font_prop("body", 11), style="italic",
    color=P.TEXT_NOTE, ha="center", va="top")
```

英文副标对 05/06/07/08 都含 `method ref:`，匹配设计说明 IV 章。

## 唐诗实测产物

```
00_唐诗情感图谱_dashboard.png        2.8 MB
01_情感分布环形图.png                 320 KB
02_诗人情感热力图.png                 590 KB
03_唐诗情感词云_总.png                450 KB
03b_唐诗情感词云_5分类拼图.png        980 KB
04_朝代情感sankey.png                 410 KB
05_朝代情感时间曲线.png               680 KB
06_诗人籍贯地图.png                   631 KB
07_关键意象朝代演变.png               584 KB
08_高频字共现网络.png                 2450 KB
原生_唐诗情感分布饼图.png             45 KB
原生_唐诗情感统计.csv                 1 KB
```

总 9.65 MB。

## 红线（唐诗实例）

- 06 号黄河必须 #C9A227（金）/长江 #4F7DA5（蓝），不要随手换
- 07 号安史之乱阴影 x 必须落在 1.45-1.55（盛唐↔中唐分界）
- 08 号 `seed=42` 必须固定——否则每次重画位置都不一样
- 05/06/07/08 副标必须含 `method ref:` 与设计说明 IV 双向锚点
