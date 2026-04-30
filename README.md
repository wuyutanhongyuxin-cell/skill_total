# Skill Total

Claude Code 自定义 Skill 集合，按用途分类管理。

## 目录结构

```
skill_total/
├── frontend/                  # 前端 / UI 相关 Skill
│   └── visual-html-tutorial/  # 面向客户的可视化 HTML 教程生成器
├── content/                   # 内容生产 / 媒体转换 Skill
│   └── bili-series-to-ppt/    # Bilibili 多 P 系列 → 教学 PPT 课件流水线
├── backend/                   # 后端相关 Skill（待添加）
├── devops/                    # DevOps 相关 Skill（待添加）
└── README.md
```

## 使用方式

本仓库下的 Skill 分两种形态，安装方式不同：

### 1. 单文件 slash command（如 `frontend/visual-html-tutorial`）

```bash
cp frontend/visual-html-tutorial/visual-html-tutorial.md <你的项目>/.claude/commands/
```

然后在 Claude Code 中输入 `/project:visual-html-tutorial` 调用。

### 2. 全局 Skill 目录（如 `content/bili-series-to-ppt`）

含 `SKILL.md` + `templates/` + `references/`，整体复制到全局 skills 目录：

```bash
cp -r content/bili-series-to-ppt ~/.claude/skills/
```

之后用自然语言说出触发短语（见各 skill README 的「触发短语」章节）即可由 Claude Code 自动加载执行。

## Skill 列表

| Skill | 分类 | 形态 | 说明 |
|-------|------|------|------|
| [visual-html-tutorial](frontend/visual-html-tutorial/) | frontend | slash command | 根据素材生成面向客户的高度可视化单文件 HTML 教程，含 Dark/Light 主题、交互式模拟演示、多系统 Tab 等 |
| [bili-series-to-ppt](content/bili-series-to-ppt/) | content | 全局 skill | Bilibili 多 P 系列端到端流水线：抓 URL → 下载 → Whisper 转写 → 4 路并发 subagent 抽大纲 → 渲染 22-26 张/讲的教学 PPT |

## 分类说明

- **frontend**：前端可视化、HTML/CSS/JS 生成、客户端 UI 类
- **content**：内容生产与媒体转换流水线（视频→文本→课件、音频处理、文档批量生成等）
- **backend**：服务端、API、数据库、后台任务（待添加）
- **devops**：CI/CD、部署、监控、基础设施（待添加）

新增 Skill 时优先归到现有分类，确实不匹配再开新分类，并同步更新本 README 的目录结构表与 Skill 列表表。
