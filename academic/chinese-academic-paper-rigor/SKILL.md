---
name: chinese-academic-paper-rigor
description: 中文 LaTeX 学术论文（xelatex + ctex + biblatex-gb7714-2015）的写作 + 优化全流程严格性管道：数字真值审计、措辞稳健化、LLM 痕迹清扫、标点字符级核查、致谢段反虚构、subagent 联网取证、xelatex 编译、PDF 反推自检。
---

# 中文学术论文严格性管道（LaTeX + xelatex + ctex）

## 核心原则

**严格、准确、可反推。** 不靠“我改了”汇报，靠脚本反推 PDF 文本流。任何一项 selfcheck 不通过 → 修源 + 重编 + 重跑，不修报告。

**联网取证，不靠记忆。** 数字、年份、作者、机构、URL、量表、阈值、文献先例都必须当场取证。subagent 报告“找不到先例”是有效结论。

**派生加工不覆盖源。** 改 paper.tex 是源代码 in-place 编辑允许；但 .xlsx / .docx / .csv 数据文件**新出文件**不覆盖。

## 何时触发

- 用户说“写论文” / “改论文” / “编译论文” / “去 AI 痕迹” / “投稿前核查” / “验收” 且涉及 .tex / 中文学术稿
- 用户拿来一份草稿要审：检查事实数字、措辞、引文、标点、致谢
- 已有 paper.tex 项目要做反复优化迭代

**不触发**：纯 docx 报告（走 [[chinese-docx-humanize]]）；纯英文论文（本 skill 中文规则不适用）；ppt/poster（不同管道）。

## 输入分流

| 输入 | 处理路径 |
|------|---------|
| `.tex`（已编译 paper） | 主路径：本 skill 全流程 |
| `.md` 论文初稿 | 先转 `.tex`（手工或参考下方模板）；docx 走 [[chinese-docx-humanize]] 然后再投 LaTeX |
| `.docx` 投稿版 | 主稿做完 → docx 转换走 [[chinese-docx-humanize]] |
| 数据 `.xlsx`/`.csv` 报告 → 论文素材 | 数据先走分析管道（不本 skill），事实抽到 `.knowledge/` 然后写进 tex |

## 文件结构约定

```
paper/
├── src/
│   ├── paper.tex          # 主稿（in-place 编辑允许）
│   ├── preamble.tex       # ctex + biblatex-gb7714-2015 + fontset=windows
│   └── references.bib     # GB/T 7714-2015 格式
├── tools/
│   ├── compile.ps1        # xelatex×4 + biber 驱动（见 compile.ps1.template）
│   ├── number_audit.py    # 数字真值审计（见 number_audit.py.template）
│   ├── humanize_check.py  # 7 项 LaTeX 源 selfcheck（见 humanize_check.py.template）
│   ├── punct_audit.py     # 标点字符级核查（L-048，见 punct_audit.py.template）
│   └── pdf_reverse_verify.py  # PDF 文本流反推（见 pdf_reverse_verify.py.template）
├── out/
│   ├── paper.pdf          # 终交付
│   ├── paper.aux/.bbl/... # 编译中间产物
│   └── paper.txt          # pdftotext 反推用纯文本
├── specs/                 # 设计文档（IMRaD 大纲 + 数据真值表）
├── plans/                 # 写作 / 修订执行计划
└── checklists/
    └── paper-fact-verification-checklist.md  # 项目级核查清单（本 skill 提供模板）
```

## 写作 + 优化管道（顺序不可错）

| 步 | 动作 | 关键约束 |
|---|------|---------|
| 1 | **预备**：拉规范（GB/T 7714-2015 / IMRaD / 期刊投稿规范），调研已有 `.knowledge/research/` 是否已沉淀 | 用 [[cache-research]] skill 先 grep，避免重做 |
| 2 | **数据真值确认**：subagent 联网核对每个具体数字的官方一手源 | verbatim 引用 + URL + 访问日期。所有数字落 `number_audit.py` TRUTH 字典 |
| 3 | **写作**：从 `.knowledge/` 已核证的事实 + `specs/` 设计文档 → tex 源 | 写时即查事实，不留“先写完再 review”。**禁用** `本文/本研究/至关重要/旨在/推动/综上所述/通常要求` 等模板词 |
| 4 | **数字真值审计**：`python tools/number_audit.py` | 必 100% PASS（28/28 之类）；MISS 项必须修源到通过 |
| 5 | **措辞稳健化扫描**：`python tools/humanize_check.py` | 7 项规则全 OK（0 处命中） |
| 6 | **标点字符级核查**：`python tools/punct_audit.py` | ASCII `"` 全 0；中文段 `[一-鿿]` ± 1 字符窗口无半角 `,;:.`；千分位 `\d,\d{3}` 白名单豁免 |
| 7 | **硬约束+让步双向文档化**：grep 全文找硬约束声明位置，每处必须同时提到例外或 `\ref{}` 指向例外详述段 | [[L-047]] |
| 8 | **致谢段反虚构**：grep `\section\*?\{致谢\}` 段，逐句问“实际有谁做过这件事” | [[feedback-acknowledgments-no-fabrication]] |
| 9 | **编译**：`pwsh tools/compile.ps1` → xelatex ×4 + biber | MiKTeX 可能 exit 1 但 .aux/.pdf 已写就算成功（compile.ps1 已处理）；允许 'h→ht' 浮动警告 |
| 10 | **PDF 反推验证**：`pdftotext -layout out/paper.pdf out/paper.txt` + `python tools/pdf_reverse_verify.py` | ASCII `"`/`「`/`」` 残留 0；`"`/`"` 等量；数字真值 100% 命中文本流 |
| 11 | **docx 路径反推**（投稿前可选）：把 paper.txt 喂 `chinese-docx-humanize/selfcheck.py` | 0 emoji / 0 框线 / 0 AI 高频词 / 0 中文段半角逗号 |

## 不可破规则（八条踩坑沉淀）

### 1. 不留 LLM 痕迹（学术诚信硬要求）

- **正文禁用元词**：`agent` / `LLM` / `AI` / `大模型` / `生成式` / `chatgpt` / `claude` / `gemini` / `gpt-`
- **AI 高频中文词禁用**：`本文` / `本研究`（论文里直接用主语或被动语态）/ `至关重要` / `旨在` / `推动` / `综上所述` / `总而言之` / `不仅...而且` / `核心要义` / `赋能` / `破局`
- **AI 高频英文词禁用**：`delve` / `pivotal` / `unlock` / `facilitate` / `leveraging` / `robust`（不含“鲁棒性”语境）
- **装饰符号禁用**：emoji / `===+` / `---+` / `→ ⇒ ← ⇐`
- **半角括号含中文禁用**：`(说话)`、`(N=100 受试者)` → `（说话）`、`（N=100 受试者）`；纯英文/纯数字 `(N=100)` `(PsychoPy)` 保留半角
- **章节标号正文混用禁用**：`1.1 章节名` 单独成行（[[humanize_check]] R7）

→ 由 `humanize_check.py` 7 项 regex 自动抓。

### 2. 致谢段不虚构（[[feedback-acknowledgments-no-fabrication]]）

不写以下任何一项，除非**确认真实发生**：

- “感谢匿名审稿人对初稿的建设性意见” — 未投稿不存在审稿人
- “感谢上海交通大学 XX 项目提供数据资源与计算环境支持” — 没有这种项目就别写
- “其对 XX 的方法论提示” — 空泛溢美
- “本研究受 XX 基金资助（项目号 …）” — 没有就别写

**默认 fallback**：只感谢真实的指导老师 + 真实的协作者，一句话致谢比一段套话致谢更可信。

类似虚构高危区：§项目背景的“提供数据资源” / 参考文献的占位 `TODO_ref*` 编进 PDF / 署名后的“通讯作者”角色凭空标。

### 3. 数字真值不能凭记忆（[[L-045]]）

任何具体数字（规模/年份/作者数/词条数/被试数/p 值/覆盖率/极差）**写之前**必须：

- subagent 联网取证官方一手源 → verbatim 引用 + URL
- 或本地脚本可独立复现（`wc -l data/raw/...txt`、`balance_report.txt` 直接读出）
- **WebFetch 转述不算证据**（[[L-033]]：JSON 数组类查询会 AI 幻觉补全，必须 curl + jq/Python 本地解析）

每条数字落 `number_audit.py` TRUTH 字典，绑定到论文正文里的一个或多个变体（`"1,818,649" / "1818649" / "1{,}818{,}649"`），改任一处自动同步审计。

### 4. 措辞稳健化（[[L-046]]）

正文出现下列措辞必须**当场判定**有无 published 文献先例：

| 措辞 | 判定 | 改法 |
|---|---|---|
| “通常要求 X” / “一般取 X” / “常用阈值 X” | 有先例？引文；无 → “本研究为 Y，将 X 定为 …” |
| “工程实践中 X” | 同上 |
| “普遍接受 X” / “学界共识” | 同上 |
| “标准做法是 X” | 同上 |

**写“本研究为 …”的归因**比借不存在的“先例”做背书安全 — 审稿人查文献就露馅。

### 5. 硬约束 + 让步双向文档化（[[L-047]]）

硬约束在工程实施时常需“有限让步”。**约束的每个声明位置必须同步提到例外的存在 + 指向例外的详述位置**：

- 摘要：把“严格筛 X”→“以 X 为主体的清洗”（措辞软化）
- 方法（§2.X）候选池清洗段：把“仅保留 X”→“保留 X 作为候选池主体” + 段末指向 §让步详述段
- 结果/讨论（§5.X 之类）：补入正式声明 N 个例外 + 每个例外的不可替代理由 + 占比百分数
- §1.2 举例段：在举出例外后**立即**声明“3 个例外见 §让步详述”
- 摘要英文同步软化

**selfcheck**：grep 硬约束关键词所有命中位置，每处 200 字符内必须出现：“例外” 或 `\ref{<例外详述label>}` 或占比数字 / 例外数量。

### 6. 标点字符级核查（[[L-048]]）

**问题本质**：xelatex+ctex+`fontset=windows` 把宋体里的 U+0022 (`"`) 字形渲染成右关引号样式，所以 PDF 里每对 `"..."` 看起来都是关-关 `""...""`（开关字形差 ~1 px，肉眼盲）。

**禁用字符黑名单**（中文段 `[一-鿿]` 前后 1 字符窗口内不应出现）：

| 字符 | 编码 | 正确替代 | 例外 |
|---|---|---|---|
| `"` | U+0022 | `"` (U+201C) 开 / `"` (U+201D) 关 按出现顺序奇偶交替 | LaTeX 命令参数 / 代码块内 |
| `'` | U+0027 | `'` (U+2018) 开 / `'` (U+2019) 关 | 英文缩写 `Levene's` `team's` `Li's` |
| `「` | U+300C | `"` (U+201C) | 无（日文括弧不规范） |
| `」` | U+300D | `"` (U+201D) | 无 |
| `,` | U+002C | `，` (U+FF0C) | 千分位数字 `1,818,649` |
| `;` | U+003B | `；` (U+FF1B) | 无 |
| `:` | U+003A | `：` (U+FF1A) | URL / 时间戳 / LaTeX 字段名 `\label{xxx:yyy}` |
| `.` | U+002E | `。` (U+3002) 句末 | 小数 `0.7287` / 缩写 `Xu \& Li (2020)` |

**引号配对替换算法**（一次性全文修订，如 paper.tex 212 个 ASCII `"` → 116 对）：

```python
from pathlib import Path
p = Path('src/paper.tex')
text = p.read_text(encoding='utf-8')
# 备份
Path('src/paper.tex.before-quote-fix').write_text(text, encoding='utf-8')
# 「」 → ""
text = text.replace('「', '“').replace('」', '”')
# 配对替换 ASCII " 按奇偶
out, toggle = [], 0
for c in text:
    if c == '"':
        out.append('“' if toggle == 0 else '”')
        toggle ^= 1
    else:
        out.append(c)
assert toggle == 0, 'ASCII " 数为奇数，配对失败'
new_text = ''.join(out)
assert new_text.count('"') == 0
assert new_text.count('「') == 0 and new_text.count('」') == 0
assert new_text.count('“') == new_text.count('”')
p.write_text(new_text, encoding='utf-8')
```

### 7. 不要相信“PDF 看起来对”

中文引号配对错误肉眼几乎检不出。**必须**：

1. `pdftotext -layout out/paper.pdf out/paper.txt` 反推 PDF 文本流
2. `python -c "from pathlib import Path; t=Path('out/paper.txt').read_text('utf-8'); print('ASCII\"残留:', t.count(chr(0x22)))"` 字符级核
3. `number_audit.py` 对 paper.txt（而非 paper.tex）再跑一次反推 — 期望 100% 命中
4. 抽 3-5 对引号样本（例：`"擀面" "扫地" "概念"`）肉眼复核字形

→ 由 `pdf_reverse_verify.py` 一键完成。

### 8. 引文核证（GB/T 7714-2015 + biblatex）

每条 `references.bib` 核 5 项：(a) 作者拼写顺序 (b) 年份 (c) 刊名/会议名 (d) 卷号/页码 (e) DOI 可访问

- 占位文献（`TODO_ref*` 之类）**不能直接编入 PDF**，编译前 grep 一遍剔除
- 每次 `\cite{}` 新文献，先 `grep -n "<key>" src/references.bib` 验在；再 WebSearch / WebFetch DOI 验存在
- 投稿前用 `biber --validate-datamodel` 跑一次形式校验

## 自检协议（终稿编译前必跑）

按顺序运行，任何一项不通过禁止交付：

```powershell
# 1. 数字真值
python tools/number_audit.py                      # 期望 N/N PASS

# 2. LaTeX 源 7 项 humanize
python tools/humanize_check.py                    # 期望 [PASS] 全部 7 项 OK

# 3. 标点字符级
python tools/punct_audit.py                       # 期望 ASCII " 0 / 「」 0 / 中文段半角标点 0

# 4. 编译
pwsh tools/compile.ps1                            # 仅允许 'h→ht' 浮动警告

# 5. PDF 反推
python tools/pdf_reverse_verify.py                # 期望 字符级 + 数字 100% 命中

# 6. （投稿前可选）docx 路径反推
pdftotext -layout out/paper.pdf out/paper.txt
python C:\Users\16191\.claude\skills\chinese-docx-humanize\selfcheck.py out/paper.txt
```

任何一项 FAIL → 反查 `paper.tex` 漏哪条规则 / 漏哪个新数字 / 漏哪个标点；**不要在 PDF 里手改**，必须可重跑复现。

## 反推回去协议（reverse-verify，硬要求）

selfcheck 通过 ≠ 交付完成。**必须再做内容反推**：

1. `pdftotext -layout out/paper.pdf out/paper.txt`
2. Python 字符级核：
   ```python
   from pathlib import Path
   t = Path('out/paper.txt').read_text('utf-8')
   assert t.count('"') == 0, f'ASCII " 残留 {t.count(chr(0x22))} 处'
   assert t.count('「') == 0, '「 残留'
   assert t.count('」') == 0, '」 残留'
   assert t.count('“') == t.count('”'), f'""不平衡: 开{t.count("“")} 关{t.count("”")}'
   ```
3. 数字真值审计对 paper.txt 反推（修改 number_audit.py 让它读 paper.txt 而非 paper.tex），期望 N/N 命中
4. 用 `chinese-docx-humanize/selfcheck.py` 7 项 regex 反推 paper.txt（0 emoji / 0 框线 / 0 AI 词 / 0 半角括号含中文 / 0 箭头 / 0 中文段半角逗号 / 字体跳过）

**任何一项失败 → 不修报告，修 paper.tex → 重编 → 重推。**

## 派 subagent 联网取证 SOP（[[L-033]]）

任何“论文里某句话需要外部事实支撑”必须派 `general-purpose` subagent 取证：

1. 要求 **verbatim 引用 + 真实可访问 URL**（不要 AI 转述）
2. **每条断言至少 2 个独立源** 交叉
3. **subagent 报告“找不到先例”是有效结论** — 此时归因到本研究自定（[[L-046]]）
4. **subagent 给出的人名/机构/邮箱/数字** 必须 WebFetch 单独验证（一手主页 / 官方 doi.org / arxiv abs）才能写进论文
5. **JSON 数组类查询走本地** `curl + jq/Python json.load`，不走 WebFetch（[[L-033]] AI 幻觉补全）

模板 prompt：

> 核对论文 §X line YY 的说法 “Z”。
>
> 要求：
> 1. 找 ≥ 2 个独立的 published 来源（论文 / 官方网站 / 政府文件）
> 2. 每个来源给 verbatim 引用 + URL + 访问日期
> 3. 如果找不到先例，明说“找不到先例”+ 列出搜过的 keyword
> 4. 不要 AI 转述，引用必须可复现
> 5. 不要 GitHub Contents API 这类 JSON 数组的“完整列表”查询，改 `curl` 取原始 JSON 后本地解析
>
> 报告 < 300 字。

## xelatex 编译细节

### preamble.tex 模板（中文论文标准）

```latex
\usepackage[UTF8, heading=false, fontset=windows]{ctex}
\usepackage{amsmath, amssymb, graphicx, booktabs, array, caption}
\usepackage[colorlinks=false, hidelinks]{hyperref}
\usepackage[
  backend=biber,
  style=gb7714-2015,
  gbnamefmt=lowercase,
  gbpub=false,
  sorting=none
]{biblatex}
\addbibresource{references.bib}
\usepackage[a4paper, margin=2.5cm]{geometry}
\setlength{\parindent}{2em}
\title{...}
\author{...}
\date{...}
```

`fontset=windows` 用 Windows 自带宋体/黑体/Times；这是 ASCII `"` 渲染成关引号的根因（[[L-048]]），换不了字体，必须从源消除 ASCII 直引号。

### compile.ps1 关键陷阱

- **MiKTeX 25.x exit code 1 是“更新检查”警告**，不是失败：判断成功要看 `out/paper.aux` 和 `out/paper.pdf` 是否写出
- **xelatex ×4** 是因为：1 次取 .aux → biber 取 .bbl → 3 次再吃 .bbl 收敛交叉引用
- **`h→ht` 浮动说明符警告** 是 ctex + booktabs 已知无害提示，忽略
- 真错误特征：`Emergency stop` / `Fatal error` / `LaTeX Error:` / 缺 .pdf 输出

### 编译命令

```powershell
powershell -ExecutionPolicy Bypass -File E:\<your-path>\paper\tools\compile.ps1
# 或在 PowerShell 里直接：
pwsh tools\compile.ps1
```

## 实证案例库

| 教训 | 来源项目 | 关键细节 |
|---|---|---|
| [[L-045]] | M9 paper 验收 | BCC 论文里“18 亿”凭记忆错，subagent 取证 corpus.bfsu.edu.cn 正确是 150 亿（六大子库总和） |
| [[L-046]] | M9 paper 验收 | “工程实践中通常要求 p > 0.10” 被 subagent 文献核查打回，改“本研究为降低 II 类错误风险，将平衡性阈值定为 p > 0.10” |
| [[L-047]] | M9 paper Round 1 | “以双字词为主”硬约束 vs 3 文化锚词例外（馕/哈密瓜/清真寺），5 处对偶补丁同步 |
| [[L-048]] | M9 paper Round 3 | paper.tex 212 个 ASCII `"` 全部渲染成关引号，肉眼检不出；脚本配对替换 116 对 + pdftotext 反推 0 残留 |
| [[L-033]] | M4 维语方向调研 | WebFetch 对 GitHub Contents API JSON 数组的“完整列表”幻觉补全（编出不存在的 megahr.ug）|
| [[L-029]] | M2 续 docx | 千分位数字 `1,818,649` 被 PUNCT_FIX 误转 `1，818，649`，selfcheck 抓不到 |
| [[feedback-acknowledgments-no-fabrication]] | 全项目 | 致谢段不写不存在的项目/审稿人/方法论提示 |
| [[feedback-no-overwrite-source]] | 全项目 | 派生加工不覆盖源 xlsx/docx/csv，tex 源代码 in-place 允许 |

## 红旗（STOP 自查）

| 念头 | 实际意味 |
|------|---------|
| “PDF 看起来对，不跑反推” | STOP，必跑 pdftotext + 字符级 + 数字真值反推 |
| “这个数字我记得是 X” | STOP，subagent 取证官方一手源，或本地脚本读出 |
| “加一句'通常这么做'更稳” | STOP，查文献否则改“本研究为 …” |
| “致谢段加'感谢匿名审稿人'更正式” | STOP，没投稿不存在 |
| “这段标点我手改一下” | STOP，跑 humanize_check + punct_audit |
| “subagent 报告里说有这个文件” | STOP，curl HEAD 单独验证，特别是 JSON 数组类查询 |
| “selfcheck 漏过一项” | STOP，修 selfcheck regex 集合再跑，不放过 |
| “这是简单的 typo 改一下就好” | STOP，过 selfcheck 协议（自己写的中文段也可能引入半角括号 [[L-031]]）|
| “PDF 编译完了就交付” | STOP，反推回去协议必跑（pdftotext + 字符级 + 数字真值 + chinese-docx-humanize 反推）|
| “WebFetch 报告说存在 X 文件” | STOP，curl 单独验证存在 |

所有这些念头都意味着：**别走捷径，跑全 selfcheck + reverse-verify**。

## 工具脚本（本目录提供模板）

| 文件 | 用途 | 默认路径假设 |
|------|------|------------|
| `number_audit.py.template` | 数字真值审计：TRUTH 字典逐项 grep `paper.tex` 正文 | `paper/src/paper.tex` ↔ `paper/tools/` |
| `humanize_check.py.template` | 7 项 LaTeX 源 selfcheck（LLM 痕迹 / AI 高频词 / emoji / 半角括号 / 千分位 / 章节标号） | 同上 |
| `punct_audit.py.template` | 标点字符级核查（ASCII `"` / `「」` / 中文段半角 `,;:.` / 千分位白名单） | 同上 |
| `pdf_reverse_verify.py.template` | PDF 文本流反推（pdftotext + 字符级 + 数字真值对 paper.txt） | `paper/out/paper.pdf` |
| `compile.ps1.template` | xelatex ×4 + biber 驱动（MiKTeX exit-code 1 容错） | 用户 MiKTeX 路径需替换 |
| `bootstrap.py.template` | **项目初始化辅助**（L1 确定性）：探测 xelatex/biber 改写 compile.ps1；扫 paper.tex 数字 token 生成 truth_skeleton.md 待人工核证 | `paper/tools/` |
| `paper-fact-verification-checklist.md.template` | 项目级核查清单（9 节：数字 / 引用 / 措辞 / 硬约束让步 / 致谢 / 编译 / 取证 SOP / 历史踩坑 / 标点字符级） | 复制到 `paper/checklists/` |

**初始化新论文项目**：

```powershell
# 假设新论文项目在 E:\your-paper-project\
$skill = 'C:\Users\16191\.claude\skills\chinese-academic-paper-rigor'
$dst   = 'E:\your-paper-project'

New-Item -ItemType Directory -Path "$dst\paper\src","$dst\paper\tools","$dst\paper\out","$dst\paper\checklists" -Force | Out-Null

Copy-Item "$skill\number_audit.py.template"          "$dst\paper\tools\number_audit.py"
Copy-Item "$skill\humanize_check.py.template"        "$dst\paper\tools\humanize_check.py"
Copy-Item "$skill\punct_audit.py.template"           "$dst\paper\tools\punct_audit.py"
Copy-Item "$skill\pdf_reverse_verify.py.template"    "$dst\paper\tools\pdf_reverse_verify.py"
Copy-Item "$skill\compile.ps1.template"              "$dst\paper\tools\compile.ps1"
Copy-Item "$skill\bootstrap.py.template"             "$dst\paper\tools\bootstrap.py"
Copy-Item "$skill\paper-fact-verification-checklist.md.template" "$dst\paper\checklists\paper-fact-verification-checklist.md"
```

**初始化辅助一键跑**：

```powershell
python "$dst\paper\tools\bootstrap.py" --all
```

`bootstrap.py` 自动完成两件**确定性**的事（不调 LLM）：

1. **Stage A**：探测本机 `xelatex.exe` / `biber.exe`（先 PATH 后 MiKTeX/TeX Live 常见路径），改写 `compile.ps1` 的 `$XeLaTeX` / `$Biber` 变量（备份原文件到 `compile.ps1.bak`）
2. **Stage B**：扫 `paper.tex` 抽数字 token（千分位整数 / 大整数 / 小数 / 百分比 / 比率 / p 值表达式，自动排除 1900-2199 年份），生成 `tools/truth_skeleton.md` 待人工核证清单

剩余仍需**人工**完成（项目独有，且**必须人工核证**不能信 LLM 转述，[[L-033]]）：

- `number_audit.py` 的 TRUTH dict — 逐条核证 `truth_skeleton.md` 里 KEEP 的 token 的真值来源（论文 verbatim / 官方统计 / 本地脚本 `wc -l` / `balance_report.txt` 可复现），加全部变体
- `paper-fact-verification-checklist.md` — 填本项目的数据集 / 统计 / 引用真值表
- `preamble.tex` — 标题 / 作者署名 / 期刊模板特有命令

复杂数据源场景下可派 subagent **辅助**对齐，见下方 **L2 协议**（不进默认管道）。

### L2 可选协议：subagent 辅助真值对齐（不进默认管道）

bootstrap.py 生成 `truth_skeleton.md` 后，每个 token 仍需人工核证真值来源。当数据源结构复杂（多个 csv/json/xlsx 跨表组合）时，可派 subagent **辅助**做 KEEP/DROP 建议 — 但 subagent 输出**不**直接写入 `number_audit.py` TRUTH dict，**必须**经用户审查 + `number_audit.py` 验证后才算证据。

**为什么不进默认管道**：[[L-033]] / [[feedback-acknowledgments-no-fabrication]] 这条铁律要求真值核证不能依赖 LLM 转述。subagent 可能：

- 把临近数字算作匹配（数据源 `Z2=447823` vs `paper.tex` `447,876` 是不同数字）
- 跨表 join 时拼错 key
- 把版本号 / 文档结构编号当数据规模

让 subagent 直接当 `number_audit` 的输入源会破自检闭环 — 自检的全部价值就在于它的独立性。**用 LLM 生成真值，再用 LLM 写的 regex 自检该真值，等于没自检。**

**适用场景**：

- 数据源是多个 csv/json 表，TRUTH 候选 30+ 条手对齐成本高
- `paper.tex` 已写完，bootstrap.py 抽出 ~50 个 token 待 KEEP/DROP 决定
- 用户有明确的“数据源锚点”（哪个文件的哪一列对应哪个论文数字）

**subagent prompt 模板**（用户复制粘贴跑，**不要**让本 skill 自动调用）：

```
读取 <项目>/tools/truth_skeleton.md 中的 token 列表，对照 <项目>/data/ 下的
数据源（指定路径：cells.csv、anova_result.json、selection_report.txt），逐条
对齐。

要求：
1. 每个 token 输出三段：
   (a) bucket + token 字面值（verbatim）
   (b) 数据源命中（文件:行号 + verbatim 值 + 是否相等/近似）
   (c) KEEP/DROP 建议 + 一句话理由

2. 不要修改任何文件。只输出建议。

3. 不要"近似匹配"：
   - paper.tex 写 447,823，数据源 Z2 = 447876 → 报告"数值不一致"，不报匹配
   - paper.tex 写 0.7287，数据源 anova_result.json["pos"]["p"] = 0.728733
     → 报告"低精度 vs 高精度，可能匹配，需用户确认"

4. 不要走 GitHub Contents API / JSON 数组的 WebFetch 全列表查询（L-033 幻觉补全）。
   读本地文件用 Read，结构化数据用 Python json.load / pandas。

5. 报告 < 500 字。
```

**用户接管步骤**（不可省）：

1. 看 subagent 输出（≤ 500 字 + 逐 token 三段）
2. 用户**自己**决定每个 token KEEP/DROP
3. 用户**自己**填 `number_audit.py` 的 TRUTH dict（subagent 不写文件）
4. `python tools/number_audit.py` 跑确认 N/N PASS
5. 编译 + 反推 + selfcheck 全流程

**红线**：subagent 输出不写 `paper.tex` / `number_audit.py`。审计链路里不能有 LLM 一手输出。

## 与其它 skill 的衔接

- **[[cache-research]]**：写论文前先 grep `.knowledge/research/` 已有的调研沉淀，避免重做。subagent 取证完后写回 `.knowledge/`（含 verbatim 引用 + URL + 访问日期）。
- **[[chinese-docx-humanize]]**：投稿 docx 版本时走它的管道。本 skill 的 `pdf_reverse_verify.py` 也会调用它的 `selfcheck.py` 作交叉验证。
- **[[superpowers:writing-plans]] + [[superpowers:subagent-driven-development]]**：写大改、多章节修订时用 plan + subagent 协同；小改本 skill 直接 in-place 即可。

## 用户硬约束记忆（项目级 — 来自 [[feedback]] memory）

- **不要在源文件上改 新出一个文件**（限 xlsx/docx/csv；`paper.tex` 是源代码 in-place 允许）
- **不要体现一点 LLM 做的工作**（论文正文 + 致谢 + 注释 + commit message 都不能出现 LLM 元词）
- **一定要严格准确 符合论文规范**
- **作者署名仅“上海交通大学失语症词表课题组”**（不个人姓名）
- **王老师 hard constraint**: ANOVA 三个 p > 0.10
- **BCC 是唯一授权的中文词频基线**（SUBTLEX-CH / HSK / AoA 是辅助信号，不替代）

这些跨会话生效（在 `C:\Users\16191\.claude\projects\E--claude-ask-Notion-weiwuer\memory\` 里），本 skill 调用时遵从。

## 故障排查（FAQ）

**Q1: humanize_check.py 报 R5_半角括号 命中，但我看正文是英文/数字括号 `(N=100)`，不应该命中。**

A: regex `(?<!\})\([^()]*[一-鿿]+[^()]*\)` 要求括号内**至少含一个中文字符**才命中。若误报，可能是括号内有“鿿”以下的非中文字符被误判（如全角空格 U+3000 落在 `[一-鿿]` 范围内），grep 实际匹配位置确认。

**Q2: number_audit.py 报某数字 MISS，但我肉眼看正文有。**

A: 检查变体形式：`"1,818,649"` 可能被 LaTeX 渲染为 `1{,}818{,}649`（biblatex 包用 `{,}` 防意外断行），TRUTH 字典里同时列两个变体 `["1,818,649", "1{,}818{,}649"]` 任一命中算通过。

**Q3: punct_audit.py 报中文段半角逗号，但我看是日期 `2026,05,23`。**

A: 应是日期分隔符的话改全角 `、` 或 `·`，或加 lookbehind/lookahead 数字保护（参考 [[L-029]] 千分位保护模式）。

**Q4: compile.ps1 跑完 exit code 是 1，是失败吗？**

A: 看 `out/paper.aux` 和 `out/paper.pdf` 是否存在。MiKTeX 25.x 的 “major issue: not checked for updates” 会让 exit 1 但实际编译成功。compile.ps1 已内置这个判断。

**Q5: pdf_reverse_verify.py 报数字命中率 95%，5% 是什么？**

A: PDF 渲染会把多字符紧凑（如 `9{,}877` LaTeX 源 → PDF 显示 `9,877`），number_audit 在 TRUTH 里同时列 `["9{,}877", "9877", "9,877"]` 三变体之一命中。若 5% 仍 MISS，多半是 pdftotext -layout 把表格列拆行了（数字跨了 \n），用 `pdftotext -raw` 或调 PyMuPDF 重提。

**Q6: subagent 取证回来说“找不到这个数字的官方源”，但我记得论文里见过。**

A: [[L-046]] — “记得见过”不是证据。subagent 找不到 → 改写“本研究为 …”归因到本研究自定，或换一个有据可查的近似数字 + 引文，**不要硬写**。

## 红线（绝对禁止）

- 把 LLM 转述当事实写进论文（[[L-033]]）
- 编 `TODO_ref*` 占位文献的真实条目（用占位等真补）
- 致谢段虚构资助方/审稿人/项目（[[feedback-acknowledgments-no-fabrication]]）
- 派生加工覆盖源 xlsx/docx/csv（[[feedback-no-overwrite-source]]）
- 跳过反推回去协议直接交付 PDF
- 把 selfcheck FAIL 注释掉硬过

违反任一条 → 立即停手，告知用户原因，等指示。
