# Single-File Courseware HTML

把一份长 markdown 笔记/复习密钥/cheat sheet **变成一个学生双击就能看的单文件 HTML 教学课件**。零配置,零依赖,可离线,支持 Dark/Light、Tabs、模拟测试、一键打印为 PDF。

## 适用场景

- 受众**不会**配置开发环境(学生、客户、家人),只能双击 .html 打开
- 已有一份较长的 markdown 笔记/复习材料/手册,想做成可视化教学产物
- 需要带:Dark/Light 主题切换 · 多 Tab 分模块 · 多语对照例句 · 模拟测试题(localStorage 记录最佳成绩) · 打印/导出 PDF
- 输出要"像一份正式的编辑物",不是 README 直渲、不是 Bootstrap demo

不适用于:

- 营销落地页(直接用 frontend-design)
- 多页文档站(用 Docusaurus / VitePress)
- 需要后端 / 鉴权的应用

## 核心特性

- **单 .html 文件**:无 sibling .css/.js/.json,严格遵守"双击即看"契约
- **CDN 依赖钉版本**:marked@12.0.2 (markdown 渲染) + Google Fonts
- **Markdown 内嵌**:`<script type="text/markdown">` 块作为惰性文本存储,首次激活 tab 时通过 `marked.parse(...)` 渲染——绕过 `file://` 协议下 `fetch()` 被 CORS 屏蔽的问题
- **首屏不闪屏**:`<head>` 内同步脚本读 localStorage,样式表加载前就把 `data-theme` 设好
- **持久化**:主题、当前 tab、最佳成绩、答题状态全部 localStorage,统一前缀防碰撞
- **打印/PDF 完整**:`@media print` + 点击 `印` 前预渲染所有 tab 的 markdown,A4 / 1.4cm 边距 / 答案展开 / 朱印颜色保留
- **12 维交叉自检表**:文件传输 / 编码 / 离线 / 首屏 / Tabs / 持久化 / Quiz 逻辑 / 打印 / 移动 / 可达性 / Console / 体积——任何维度不达标必须修,不允许"已知问题"备注

## 与本仓库其他 skill 的差异

| | `frontend/visual-html-tutorial` | `frontend/single-file-courseware` (本) |
|---|---|---|
| 形态 | slash command (单 .md) | 全局 skill 目录 (SKILL.md) |
| 输入 | 用户描述/截图素材 | 已有 markdown 笔记 |
| 输出特化 | 软件操作教程,带模拟终端/浏览器/系统切换 | 学习/复习材料,带多语例句 + Quiz + 打印 |
| 受众 | 软件用户/客户 | 学生/学习者 |
| 触发 | `/project:visual-html-tutorial` | 自然语言("做单文件复习课件") |

## 安装

含 `SKILL.md`,属于全局 skill 目录形态,整体复制到全局 skills:

```bash
# Linux / macOS
cp -r frontend/single-file-courseware ~/.claude/skills/

# Windows PowerShell
Copy-Item -Recurse frontend\single-file-courseware $HOME\.claude\skills\
```

之后用自然语言触发即可,Claude Code 会按 description 字段自动召回。

## 触发短语

任意一句自然语言含下列意图均可触发:

- "做一份给不会配置环境学生看的 HTML 课件"
- "把 markdown 笔记做成可视化教学网页"
- "单文件双击就能看"
- "带 dark/light + tabs + 模拟测试的复习材料"
- "把这套移植成 PDF/打印版"

也可直接在文件中点名:"按 single-file-courseware 工作流做"。

## 工作流(SKILL.md 详细版)

```
stage 1 — 内容审计     (读 MD,分桶到 7-12 个 tab)
stage 2 — 美学定调     (拒 AI 默认风,选一种鲜明视觉方向)
stage 3 — 单文件搭建   (CDN 依赖,内嵌 markdown,绝不 fetch 本地)
stage 4 — 交互层       (tabs / theme / 多语例句 / quiz)
stage 5 — 打印层       (@media print + 预渲染钩子)
stage 6 — 12 维交叉自检 (任何维度不过必须修)
```

## 不可妥协的架构铁律

1. 必须单文件 .html,无 sibling 资源
2. CDN 依赖必须钉版本号
3. Markdown 通过 `<script type="text/markdown">` 内嵌,严禁 `fetch('content.md')`(file:// CORS 会静默失败)
4. `<meta charset="utf-8">` 必须是 `<head>` 第一个元素;UTF-8 无 BOM
5. localStorage 键统一前缀,防止与其他应用碰撞
6. 主题读取脚本必须在 `<head>` 样式表之前,防首屏闪屏

## 参考实现

`E:\claude_ask\bilibili_learn\古典文法考试复习密钥.html`(2026-05-07)——日语古典文法考试复习课件,116 KB / 2440 行,11 个 tab,42 题模拟卷,完整 dark/light + 完整打印/PDF + file:// 安全,通过 12 维交叉自检。

## 反模式(禁止)

- 外置 .css / .js 文件 → 违反"双击"契约
- `fetch('content.md')` → CORS 屏蔽,静默失败
- `<iframe src="...">` → file:// 跨源限制
- Tailwind CDN 默认类组合 → 看起来跟其他 AI 网站一样
- 通用 UI 库组件(shadcn/MUI/Chakra) → 同质化问题
- 主题脚本放 `<body>` 末尾 → 必有首屏闪屏
- Quiz UI 硬编码 "/10" → 题量改了 UI 撒谎,必须用 `QUIZ.length`
- 跳过外语例句的目标语言对照列 → 这是该 skill 强制要求的字段

## 适配新学科

架构可移植,**美学不可移植**——每门学科必须有独立的视觉身份:

1. 替换 `<script type="text/markdown">` 内的源文本
2. 调整 tab 数量和标签
3. **重选美学方向**(古文用平安朝,化学用别的)
4. 替换例句/词汇/quiz JS 数组
5. localStorage 前缀换新名
6. 字体配对(SKILL.md 内有 CJK 字体推荐表)
7. 重跑 12 维交叉自检
