# Skill Total

Claude Code 自定义 Skill 集合，按用途分类管理。

## 目录结构

```
skill_total/
├── frontend/                              # 前端 / UI 相关 Skill
│   ├── visual-html-tutorial/              # 面向客户的可视化 HTML 教程生成器
│   ├── single-file-courseware/            # MD 笔记 → 双击即看的单文件教学课件（含 quiz + 打印）
│   └── industrial-equipment-courseware/   # OEM 工业设备 → 操作手册 + 工业级仿真训练器双交付 skill
├── content/                               # 内容生产 / 媒体转换 Skill
│   └── bili-series-to-ppt/                # Bilibili 多 P 系列 → 教学 PPT 课件流水线
├── data-viz/                              # 数据分析 / 学术可视化交付 Skill
│   └── bert-sentiment-viz-deliverable/    # BERT 情感分类语料 → A3 主 Dashboard + N 张精修图 + 设计说明 + 论文对标 + UTF-8 zip 交付包（含唐诗实例 reference 双层结构）
├── academic/                              # 中文学术写作 / 论文严谨化 Skill
│   └── chinese-academic-paper-rigor/      # 中文 LaTeX 论文写作 + xelatex/biber 编译 + 数字真值审计 + 标点字符级核查 + PDF 文本反推 严谨化流水线（L1 bootstrap 确定性初始化 + L2 subagent 辅助真值对齐协议）
├── backend/                               # 后端相关 Skill（待添加）
├── devops/                                # DevOps 相关 Skill（待添加）
└── README.md
```

## 使用方式

本仓库下的 Skill 分两种形态，安装方式不同：

### 1. 单文件 slash command（如 `frontend/visual-html-tutorial`）

```bash
cp frontend/visual-html-tutorial/visual-html-tutorial.md <你的项目>/.claude/commands/
```

然后在 Claude Code 中输入 `/project:visual-html-tutorial` 调用。

### 2. 全局 Skill 目录（如 `content/bili-series-to-ppt`、`data-viz/bert-sentiment-viz-deliverable`、`frontend/industrial-equipment-courseware`）

含 `SKILL.md` + 支撑文档（templates / references / 实例 reference 子目录等），整体复制到全局 skills 目录：

```bash
cp -r content/bili-series-to-ppt ~/.claude/skills/
cp -r data-viz/bert-sentiment-viz-deliverable ~/.claude/skills/
cp -r frontend/industrial-equipment-courseware ~/.claude/skills/
cp -r academic/chinese-academic-paper-rigor ~/.claude/skills/
```

之后用自然语言说出触发短语（见各 skill SKILL.md 的 description 字段或 README 的「触发短语」章节）即可由 Claude Code 自动加载执行。

## Skill 列表

| Skill | 分类 | 形态 | 说明 |
|-------|------|------|------|
| [visual-html-tutorial](frontend/visual-html-tutorial/) | frontend | slash command | 根据素材生成面向客户的高度可视化单文件 HTML 教程，含 Dark/Light 主题、交互式模拟演示、多系统 Tab 等 |
| [single-file-courseware](frontend/single-file-courseware/) | frontend | 全局 skill | 把 markdown 笔记/cheat sheet 变成学生双击即看的单文件 HTML 教学课件，带 Tabs、多语例句、模拟测试题（localStorage 记最佳成绩）、一键打印为 PDF；含 12 维交叉自检表 |
| [bili-series-to-ppt](content/bili-series-to-ppt/) | content | 全局 skill | Bilibili 多 P 系列端到端流水线：抓 URL → 下载 → Whisper 转写 → 4 路并发 subagent 抽大纲 → 渲染 22-26 张/讲的教学 PPT |
| [bert-sentiment-viz-deliverable](data-viz/bert-sentiment-viz-deliverable/) | data-viz | 全局 skill | BERT 情感分类语料端到端可视化交付包：6 阶段流程（源材料阅读 → core/ 五模块架构 → 设计说明+对照参考文献 → A3 主 Dashboard → N 张精修图 → 测试视检 → UTF-8 zip 打包）；双层结构（通法骨架 + 唐诗作业实例 reference）；含色板/字体/colormap 视觉规范、双向锚点验证、跨平台中文文件名解决方案 |
| [industrial-equipment-courseware](frontend/industrial-equipment-courseware/) | frontend | 全局 skill | OEM 工业设备(划片机 / 贴片机 / 引线键合机 / 模塑机 / 探针台 ...)→ 操作手册 HTML + 工业级仿真训练器 HTML 双交付全流程 skill：8 stages × 9 layers(8 必备 + 1 条件 vision workview)× 23-dim self-check × 6 mandatory MCP patterns；5 个项目沉淀(DAD3350 / AD8312PLUS / KS iConn / 封装模塑机 / 探针台)|
| [chinese-academic-paper-rigor](academic/chinese-academic-paper-rigor/) | academic | 全局 skill | 中文 LaTeX 学术论文严谨化流水线：bootstrap.py 一键探测 MiKTeX/TeX Live 路径 + 抽 paper.tex 数字 token 生成待人工核证骨架；compile.ps1 驱动 xelatex+biber 四遍编译；number_audit.py 数字真值审计（千分位 / p 值 / 百分比 / 比率多形态）；punct_audit.py 7 项标点字符级核查（ASCII " / 「」 / 半角逗号在中文段，千分位白名单豁免）；pdf_reverse_verify.py 反推 PDF 文本流复核；humanize_check.py AI 高频词与套话审计；含 paper-fact-verification-checklist 真值表模板 + L2 subagent 辅助真值对齐协议（输出不进审计闭环，护 L-033 铁律） |

## 分类说明

- **frontend**：前端可视化、HTML/CSS/JS 生成、客户端 UI 类
- **content**：内容生产与媒体转换流水线（视频→文本→课件、音频处理、文档批量生成等）
- **data-viz**：数据分析 / 学术可视化交付包（BERT/NLP 情感分析、统计图表、Dashboard + 多图组合、论文方法对标、设计说明等）
- **academic**：中文学术写作 / 论文严谨化流水线（LaTeX 编译驱动、数字真值审计、标点字符级核查、PDF 文本反推、AI 高频词审计、人工核证闭环协议等）
- **backend**：服务端、API、数据库、后台任务（待添加）
- **devops**：CI/CD、部署、监控、基础设施（待添加）

新增 Skill 时优先归到现有分类，确实不匹配再开新分类，并同步更新本 README 的目录结构表与 Skill 列表表。
