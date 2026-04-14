# Visual HTML Tutorial Generator

面向客户的可视化 HTML 教程生成器。

## 功能

根据用户提供的素材（截图、文本、链接等），生成一个高度可视化、小白友好、生产级的**单文件 HTML** 教程页面。

### 核心特性

- **Dark/Light 双主题**：CSS 变量系统 + localStorage 持久化
- **交互式模拟演示**：纯 CSS 实现的终端、浏览器、面板、表单等模拟界面，带编号箭头标注
- **多系统 Tab**：Windows / macOS / Linux 等多平台命令切换
- **一键复制**：代码块复制按钮，含 Clipboard API 回退方案
- **滚动动画**：IntersectionObserver 驱动的滚动揭示效果
- **进度追踪**：顶部进度条 + 侧边圆点导航
- **内容安全验证**：联网确认软件版本和配置安全性
- **零构建依赖**：单文件 HTML，双击即可打开

### 技术栈

- 单文件 HTML（CSS + JS 内联）
- Google Fonts CDN（展示字体 + 正文字体）
- Lucide Icons CDN
- 无框架依赖

## 使用方式

```bash
# 复制到项目
cp visual-html-tutorial.md <你的项目>/.claude/commands/

# 在 Claude Code 中调用
/project:visual-html-tutorial [主题描述]
```

## 工作流程

素材读取 → 内容安全验证 → 确定主题/字体/配色 → 搭建 HTML → 实现设计系统 → 填充内容 → 创建模拟演示 → 实现 JS → 安全章节 → 验证
