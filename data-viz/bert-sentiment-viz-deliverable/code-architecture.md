# 核心架构 · `core/` 5 模块详细模板

> 阶段 1 的落地参考。每个模块给出完整骨架 + 红线 + 自检命令。

## 整体目录

```
visualization/
├── core/
│   ├── __init__.py            ← 空文件，但必须有
│   ├── palette.py
│   ├── theme.py
│   ├── data_loader.py
│   ├── <category_map>.py      （如 dynasty.py）
│   └── <entity_geo>.py        （如 poet_birthplace.py）
├── extras/
│   ├── __init__.py
│   └── 01_*.py ... 0N_*.py
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── data/
│   └── <corpus>_with_sentiment.csv
├── outputs/                   （PNG / CSV 产物）
├── dashboard.py
└── 设计说明.md
```

`core/` vs `extras/` 的分界：
- `core/` 提供**数据 + 颜色 + 字体 + 主题 + 离散映射**，是"无副作用纯计算 + 常量"
- `extras/` 提供**渲染脚本**，每个文件一个 `render(df, out_path)` + `if __name__`

---

## 1. `core/palette.py`

```python
"""<项目名> · 5 情感色谱 + 辅助色 + 字体常量

色值来源：<填来源，如 zhongguose.com 实证 HEX>
字体路径：Windows 11 本机探测，带 5 级降级
"""
from pathlib import Path
import matplotlib.font_manager as fm

# ----- 5 情感色 (按 0-4 序号对应模型输出) -----
PALETTE_5 = {
    "Neg Plus": "#003472",   # 极悲
    "Neg":      "#425066",   # 哀
    "Neu":      "#75878A",   # 中
    "Pos":      "#D9B611",   # 喜
    "Pos Plus": "#FF461F",   # 极喜
}
PALETTE_5_LIST = list(PALETTE_5.values())
SENTIMENT_LABELS_CN = ["极悲", "哀", "中", "喜", "极喜"]
SENTIMENT_LABELS_EN = list(PALETTE_5.keys())

# ----- 辅助色 -----
BACKGROUND   = "#F2ECDE"   # 缟色（底）
CARD_BG      = "#EAE3CC"   # 米色（卡片）
GRID_MAIN    = "#D6CBB0"
GRID_MINOR   = "#BFB49A"
TEXT_TITLE   = "#1C1A17"
TEXT_BODY    = "#3B3A35"
TEXT_NOTE    = "#7A7468"
SEAL_RED     = "#9E2A21"   # 钤印红
BORDER       = "#8C7A4F"

# ----- 字体候选 (5 级降级) -----
FONT_CANDIDATES_TITLE = [
    r"C:\Windows\Fonts\STLITI.TTF",
    r"C:\Windows\Fonts\STXINWEI.TTF",
    r"C:\Windows\Fonts\STKAITI.TTF",
    r"C:\Windows\Fonts\simkai.ttf",
    r"C:\Windows\Fonts\simhei.ttf",
]
FONT_CANDIDATES_BODY = [
    r"C:\Windows\Fonts\STKAITI.TTF",
    r"C:\Windows\Fonts\simkai.ttf",
    r"C:\Windows\Fonts\STSONG.TTF",
    r"C:\Windows\Fonts\simsun.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
]
FONT_CANDIDATES_DATA = [
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
]

def pick_font(candidates):
    for p in candidates:
        if Path(p).exists():
            return p
    return None

FONT_TITLE = pick_font(FONT_CANDIDATES_TITLE)
FONT_BODY  = pick_font(FONT_CANDIDATES_BODY)
FONT_DATA  = pick_font(FONT_CANDIDATES_DATA)

def get_font_prop(role="body", size=14, weight="normal"):
    path = {"title": FONT_TITLE, "body": FONT_BODY, "data": FONT_DATA}.get(role, FONT_BODY)
    if path is None:
        return fm.FontProperties(size=size, weight=weight)
    return fm.FontProperties(fname=path, size=size, weight=weight)

# ----- 模型输出列名约定 -----
PROB_COLS = ["Neg Plus_概率", "Neg_概率", "Neu_概率", "Pos_概率", "Pos Plus_概率"]
WEIGHTS = [-2, -1, 0, 1, 2]

if __name__ == "__main__":
    print(f"FONT_TITLE: {FONT_TITLE}")
    print(f"FONT_BODY:  {FONT_BODY}")
    print(f"FONT_DATA:  {FONT_DATA}")
```

**自检**：`python -m core.palette` 必须看到 3 个 FONT 路径全非 None。

**红线**：
- WEIGHTS 顺序必须与 PROB_COLS 一一对应
- 5 色 HEX 不要随手编——色值带文化语义时（如中国传统色）必须有来源

---

## 2. `core/theme.py`

```python
"""一键应用 matplotlib rcParams"""
import matplotlib as mpl
from . import palette as P

def apply_ancient_theme():
    mpl.rcParams.update({
        "figure.facecolor": P.BACKGROUND,
        "axes.facecolor":   P.BACKGROUND,
        "axes.edgecolor":   P.BORDER,
        "axes.linewidth":   0.8,
        "axes.labelcolor":  P.TEXT_BODY,
        "axes.titlecolor":  P.TEXT_TITLE,
        "axes.titlesize":   18,
        "axes.titleweight": "bold",
        "axes.titlepad":    14,
        "axes.labelsize":   12,
        "xtick.color":      P.TEXT_BODY,
        "ytick.color":      P.TEXT_BODY,
        "xtick.labelsize":  10,
        "ytick.labelsize":  10,
        "grid.color":       P.GRID_MAIN,
        "grid.linestyle":   ":",
        "grid.linewidth":   0.6,
        "grid.alpha":       0.7,
        "axes.grid":        True,
        "axes.axisbelow":   True,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.spines.left":  True,
        "axes.spines.bottom": True,
        "axes.unicode_minus": False,
        "savefig.facecolor": P.BACKGROUND,
        "savefig.edgecolor": "none",
        "savefig.dpi":       300,
        "savefig.bbox":      "tight",
        "savefig.pad_inches": 0.25,
        "font.family":       "sans-serif",
        "font.sans-serif":   ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
    })
```

**红线**：`"axes.unicode_minus": False` 必须有，否则负数轴标变方框。

---

## 3. `core/data_loader.py`

```python
"""<语料名> 情感数据加载器 + 衍生统计量"""
from collections import Counter
from pathlib import Path
import re
import numpy as np
import pandas as pd
from . import palette as P

STOPWORDS = set("""
之 乎 者 也 矣 焉 哉 兮 耶 邪 耳 歟 夫 蓋 凡
其 而 以 於 于 與 与 及 若 且 則 然 所 為 为 被 何
是 非 莫 勿 弗 毋 無 无 有 此 彼 蓋 盖
吾 余 予 我 汝 爾 尔 子 君 卿 公 朕 寡
不 又 已 將 将 即 便 乃 始 終 终 常 每 復 复
個 个 些 多 少 大 小 來 来 去 同 共 並 并 還 还 都
一 二 三 四 五 六 七 八 九 十 百 千 萬 万
""".split())
_PUNCT = set("，。、；：？！“”‘’（）《》〈〉【】「」『』·…—\n\r\t 　")
STOPWORDS |= _PUNCT

def _strip_to_chinese(s):
    if not isinstance(s, str): return ""
    return re.sub(r"[^一-鿿]", "", s)

def load_poems(csv_path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    needed = ["标题", "作者", "内容", "情感分类_数字"] + P.PROB_COLS
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"CSV 缺少必需列：{missing}")
    df = df.dropna(subset=["情感分类_数字"] + P.PROB_COLS).reset_index(drop=True)
    df["情感分类_数字"] = df["情感分类_数字"].astype(int)

    probs = df[P.PROB_COLS].to_numpy(dtype=float)
    df["sent_score"] = probs @ np.array(P.WEIGHTS, dtype=float)
    df["sent_confidence"] = probs.max(axis=1)
    df["char_count"] = df["内容"].apply(lambda s: len(_strip_to_chinese(s)))
    return df

def poet_stats(df):
    poet_count    = df.groupby("作者").size().sort_values(ascending=False)
    poet_avg_sent = df.groupby("作者")["sent_score"].mean()
    poet_cross    = pd.crosstab(df["作者"], df["情感分类_数字"])
    for c in range(5):
        if c not in poet_cross.columns: poet_cross[c] = 0
    poet_cross = poet_cross[[0, 1, 2, 3, 4]]
    return {"poet_count": poet_count, "poet_avg_sent": poet_avg_sent, "poet_cross": poet_cross}

def text_features(df, top_chars=200, top_bigrams=30, bigram_min_count=2):
    char_counter, bigram_counter = Counter(), Counter()
    for text in df["内容"].dropna():
        s = _strip_to_chinese(text)
        char_counter.update(c for c in s if c not in STOPWORDS)
        for i in range(len(s) - 1):
            bi = s[i:i + 2]
            if bi[0] in STOPWORDS or bi[1] in STOPWORDS: continue
            bigram_counter[bi] += 1
    char_freq = dict(char_counter.most_common(top_chars))
    bigram_freq = {w: c * 2     # ←权重 ×2，让 bigram 在词云更显眼
                   for w, c in bigram_counter.most_common(top_bigrams)
                   if c >= bigram_min_count}
    return {"char_freq": char_freq, "bigram_freq": bigram_freq,
            "full_freq": {**char_freq, **bigram_freq}}

def extreme_poems(df, n=5):
    cols = ["标题", "作者", "sent_score", "内容"]
    bottom = df.nsmallest(n, "sent_score")[cols].reset_index(drop=True)
    top    = df.nlargest(n, "sent_score")[cols].reset_index(drop=True)
    return bottom, top
```

**红线**：
- 必检 `needed` 列存在，缺列立刻 ValueError，**不**回填空值
- bigram 权重 ×2 是经验值；古文场景必须如此，否则单字压死双字
- 不要用 jieba 默认分词处理古文——会切错（"白日依山尽" → "白日/依山/尽"）

**自检**：`python -m core.data_loader` 看到 sent_score 范围与 Top 5 多产实体。

---

## 4. `core/<category_map>.py`（离散映射，如 `dynasty.py`）

```python
"""<实体>→<类别>硬编 dict"""

CATEGORY_ORDER = ["A", "B", "C", "D", "未细分"]

CATEGORY_MAP = {
    "entity1": "A",
    # ... 列全
}

def get_category(name):
    return CATEGORY_MAP.get(name, "未细分")

def coverage_report(names):
    names = list(names)
    covered = [n for n in names if n in CATEGORY_MAP]
    missing = sorted(set(names) - set(CATEGORY_MAP.keys()))
    return {"total": len(set(names)),
            "covered": len(set(covered)),
            "coverage_rate": len(set(covered)) / len(set(names)) if names else 0.0,
            "missing": missing}

if __name__ == "__main__":
    from collections import Counter
    print(f"MAP 共 {len(CATEGORY_MAP)} 条")
    for d in CATEGORY_ORDER:
        print(f"  {d}: {Counter(CATEGORY_MAP.values())[d]}")
    # 实测：跑覆盖率
    import pandas as pd
    from pathlib import Path
    csv = Path(__file__).parent.parent / "data" / "<corpus>_with_sentiment.csv"
    if csv.exists():
        df = pd.read_csv(csv)
        r = coverage_report(df["作者"].unique())
        print(f"\n实测：{r['total']} 实体，覆盖 {r['covered']} ({r['coverage_rate']*100:.1f}%)")
        if r["missing"]: print(f"未覆盖: {r['missing']}")
```

**红线**：
- 硬编而不是"按规则推断"——古代实体的分类规则不可能 100% 覆盖，硬编可控
- `if __name__` 段必须真跑覆盖率，给设计说明引用

---

## 5. `core/<entity_geo>.py`（实体→坐标，如 `poet_birthplace.py`）

```python
"""<实体>→(lat, lon, 现代地名) 硬编 dict"""

# (lat, lon, place_name_modern)
BIRTHPLACE_MAP = {
    "entity1": (34.27, 108.94, "西安"),
    # ...
}

def get_birthplace(name):
    return BIRTHPLACE_MAP.get(name)   # 缺失返回 None，由调用方处理

def coverage_report(names):
    names = list(set(names))
    covered = [n for n in names if n in BIRTHPLACE_MAP]
    missing = sorted(set(names) - set(BIRTHPLACE_MAP.keys()))
    return {"total": len(names), "covered": len(covered),
            "coverage_rate": len(covered) / len(names) if names else 0.0,
            "missing": missing}
```

**红线**：
- 坐标取**现代行政中心**（如长安 → 西安 lat 34.27 lon 108.94），不是古代经纬度（误差大且不可查）
- 缺失返回 None 而不是 (0,0)——避免地图上出现假点

---

## 模块依赖关系

```
palette ────┬────> theme ────┐
            ├────> data_loader ─┐
            └─────────────────┐ │
                              ↓ ↓
            category_map ──> extras/0N_*.py
            entity_geo  ──┘
```

**红线**：core/ 内部禁止反向依赖（data_loader 不能 import dynasty）。
