# Skill Total

Claude Code 自定义 Skill 集合，按用途分类管理。

## 目录结构

```
skill_total/
├── frontend/                  # 前端相关 Skill
│   └── visual-html-tutorial/  # 面向客户的可视化 HTML 教程生成器
├── backend/                   # 后端相关 Skill（待添加）
├── devops/                    # DevOps 相关 Skill（待添加）
└── README.md
```

## 使用方式

每个 Skill 目录下包含一个 `.md` 文件，将其复制到项目的 `.claude/commands/` 目录下即可使用：

```bash
# 示例：使用 visual-html-tutorial skill
cp frontend/visual-html-tutorial/visual-html-tutorial.md <你的项目>/.claude/commands/
```

然后在 Claude Code 中输入 `/project:visual-html-tutorial` 调用。

## Skill 列表

| Skill | 分类 | 说明 |
|-------|------|------|
| [visual-html-tutorial](frontend/visual-html-tutorial/) | frontend | 根据素材生成面向客户的高度可视化单文件 HTML 教程，含 Dark/Light 主题、交互式模拟演示、多系统 Tab 等 |
