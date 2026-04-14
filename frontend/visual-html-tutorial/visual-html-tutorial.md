# 面向客户的可视化 HTML 教程生成器

根据用户提供的素材（截图、文本、链接等），生成一个高度可视化、小白友好、生产级的单文件 HTML 教程页面。

**使用方式**: `/project:visual-html-tutorial [主题描述]`

---

## 阶段一：素材理解与内容安全验证

### 1.1 素材读取
- 使用 `Read` 工具逐一阅读项目目录中的所有图片/文档素材
- 对每张图片/文档提取：操作步骤、关键信息、技术术语、注意事项
- 按逻辑顺序重组内容，识别步骤间的依赖关系

### 1.2 内容安全与时效性验证（联网）
- 使用 `WebSearch` 验证教程涉及的软件版本是否最新（避免已知漏洞）
- 验证命令和配置的正确性与安全性
- 检查是否有更安全的替代方案
- 如发现过时内容，在教程中**自动更新到最新版本**，并添加安全加固建议章节

---

## 阶段二：技术栈与设计决策

### 2.1 输出格式
- **单文件 HTML**（所有 CSS + JS 内联，零构建依赖）
- 仅允许 2 个外部 CDN：Google Fonts + Lucide Icons
- 目标：双击即可在任何浏览器打开，可直接发给客户

### 2.2 外部依赖（仅限 CDN）
```html
<!-- 字体：一个展示字体 + 一个正文字体，禁止使用 Inter/Roboto/Arial 等泛用字体 -->
<link href="https://fonts.googleapis.com/css2?family=[展示字体]:wght@400;500;700;900&family=[正文字体]:wght@400;500;700&display=swap" rel="stylesheet">
<!-- 图标库 -->
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
```

### 2.3 字体选择原则
- **展示字体**：用于标题、Logo、步骤编号 —— 选择有辨识度和个性的字体（如 Orbitron、Space Grotesk、Outfit、Syne 等，根据主题风格决定）
- **正文字体**：用于正文、代码块 —— 选择清晰易读的等宽或无衬线字体（如 JetBrains Mono、Fira Code、Source Code Pro 等）
- **关键规则**：每次生成必须根据教程主题选择最匹配的字体组合，**不要固定使用同一组合**

### 2.4 配色方案
- 必须同时提供 Dark 和 Light 两套主题
- 使用 CSS 变量系统管理所有颜色，通过 `[data-theme="dark"]` / `[data-theme="light"]` 切换
- 主色调根据教程主题选择（科技类→赛博绿/蓝、设计类→温暖色、金融类→深蓝金等）
- 禁止使用"紫色渐变配白底"等 AI 生成风格

---

## 阶段三：设计系统（CSS 架构）

### 3.1 CSS 变量系统（必须实现）

```css
:root {
  --font-display: '[展示字体]', sans-serif;
  --font-body: '[正文字体]', monospace;
  --transition-speed: 0.4s;
  --border-radius: 12px;
  --border-radius-sm: 8px;
  --glow-spread: 0 0 40px;
}

[data-theme="dark"] {
  --bg-primary: ...;        /* 页面主背景 */
  --bg-secondary: ...;      /* 次级背景 */
  --bg-card: ...;           /* 卡片背景 */
  --bg-code: ...;           /* 代码块背景 */
  --bg-hover: ...;          /* 悬停背景 */
  --bg-input: ...;          /* 输入框/表单背景 */
  --text-primary: ...;      /* 主要文本 */
  --text-secondary: ...;    /* 次要文本 */
  --text-muted: ...;        /* 辅助文本 */
  --accent-primary: ...;    /* 主色调 */
  --accent-secondary: ...;  /* 辅助色调 */
  --accent-warning: ...;    /* 警告色 */
  --accent-danger: ...;     /* 危险色 */
  --accent-info: ...;       /* 信息色 */
  --border-color: ...;      /* 边框 */
  --border-active: ...;     /* 激活边框 */
  --shadow-glow: ...;       /* 发光阴影 */
  --shadow-card: ...;       /* 卡片阴影 */
  --code-bg: ...;           /* 代码背景 */
  --code-border: ...;       /* 代码边框 */
  --tab-bg: ...;            /* Tab 背景 */
  --tab-active-bg: ...;     /* 激活 Tab */
  --copy-success: ...;      /* 复制成功色 */
  --overlay-gradient: ...;  /* 叠加渐变 */
  --hero-gradient: ...;     /* Hero 背景渐变 */
}

[data-theme="light"] {
  /* 完整的浅色主题变量，每个变量都要覆盖 */
}
```

### 3.2 动画系统（必须实现）
```css
@keyframes fadeInUp     { /* 从下往上淡入，用于滚动揭示 */ }
@keyframes fadeIn       { /* 纯淡入 */ }
@keyframes slideInLeft  { /* 从左滑入 */ }
@keyframes pulse        { /* 脉冲闪烁 */ }
@keyframes terminalBlink { /* 终端光标闪烁 */ }
@keyframes gradientShift { /* 渐变色流动，用于标题 */ }
@keyframes float        { /* 上下浮动，用于标注箭头 */ }

/* 滚动揭示组件 */
.reveal { opacity: 0; transform: translateY(30px); transition: opacity 0.7s, transform 0.7s; }
.reveal.visible { opacity: 1; transform: translateY(0); }
```

### 3.3 响应式断点
- 桌面端（>1080px）：显示侧边进度导航
- 平板端（640px-1080px）：隐藏侧边栏
- 移动端（<640px）：紧凑布局，表单标签改为上下排列，隐藏终端标注

---

## 阶段四：组件库（必须全部实现）

### 4.1 页面级组件

#### 顶栏 `.topbar`
- 固定定位，毛玻璃背景 (`backdrop-filter: blur(20px)`)
- Logo 使用展示字体 + Lucide 图标
- 主题切换按钮（滑块式，带太阳/月亮图标，支持 localStorage 持久化）
- 底部 2px 阅读进度条（渐变色）

#### Hero 区 `.hero`
- 标题使用 `clamp()` 响应式字号
- 关键词使用 `.gradient-text` 渐变填充文字 (`-webkit-background-clip: text`)
- 技术徽章 `.hero-badge`
- 元信息行 `.hero-meta`（系统、版本、预计时间等）
- 入场动画使用 `animation-delay` 错位出现

#### 目录 `.toc`
- 网格布局 `grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))`
- 由 JS 从步骤节点自动生成，不需要手写
- 每项带编号圆标 + 步骤名

#### 侧边进度导航 `.progress-rail`
- 固定在页面左侧，垂直圆点 + 连接线
- 当前步骤圆点高亮 + 发光
- 已完成步骤变色
- 悬停显示步骤标签
- 1080px 以下自动隐藏

#### 底部阅读进度条 `.reading-progress`
- 固定在顶栏下方，跟随滚动进度变宽

### 4.2 内容级组件

#### 步骤卡片 `.step-section` > `.step-card`
```html
<section class="step-section reveal" id="stepN" data-step-label="步骤名称">
  <div class="step-card">
    <div class="step-header">
      <div class="step-number">N</div>
      <div class="step-title-group">
        <div class="step-title">标题</div>
        <div class="step-desc">描述</div>
      </div>
    </div>
    <div class="step-body">
      <!-- 内容 -->
    </div>
  </div>
</section>
```
- 悬停效果：边框变色 + 发光阴影

#### 代码块 `.code-block`
```html
<div class="code-block">
  <div class="code-header">
    <div class="code-lang"><i data-lucide="terminal"></i> 说明</div>
    <button class="copy-btn" data-copy="要复制的纯文本命令"><i data-lucide="copy"></i> 复制</button>
  </div>
  <div class="code-content">
    <span class="cmd-prompt">$ </span>命令内容
    <span class="cmd-comment"># 注释</span>
    <span class="cmd-output">输出内容</span>
  </div>
</div>
```
- `cmd-prompt` 带 `user-select: none` 防止复制提示符
- 复制按钮使用 `data-copy` 属性存储纯文本命令

#### 多系统 Tab `.sys-tabs`
```html
<div class="sys-tabs">
  <div class="sys-tabs-header">
    <button class="sys-tab-btn active" data-tab="win"><i data-lucide="monitor"></i> Windows</button>
    <button class="sys-tab-btn" data-tab="mac"><i data-lucide="apple"></i> macOS</button>
    <button class="sys-tab-btn" data-tab="linux"><i data-lucide="terminal"></i> Linux</button>
  </div>
  <div class="sys-tab-panel active" data-tab="win">内容</div>
  <div class="sys-tab-panel" data-tab="mac">内容</div>
  <div class="sys-tab-panel" data-tab="linux">内容</div>
</div>
```
- Tab 之间不仅限于系统区分，可用于任何需要分 Tab 的场景（客户端、方案对比等）

#### 提示框 `.callout`
```html
<div class="callout callout-warning">
  <div class="callout-icon"><i data-lucide="alert-triangle"></i></div>
  <div class="callout-content"><strong>标题</strong>说明文本</div>
</div>
```
- 四种变体：`callout-warning`(黄)、`callout-danger`(红)、`callout-info`(蓝)、`callout-success`(绿)

#### 子步骤列表 `.sub-steps`
- CSS 计数器自动编号
- 圆形编号 + 文字横排

#### 折叠块 `.collapse-block`
```html
<div class="collapse-block">
  <div class="collapse-header" onclick="toggleCollapse(this)">
    <i data-lucide="chevron-right"></i>
    <span>标题</span>
  </div>
  <div class="collapse-body">
    <div class="collapse-body-inner">内容</div>
  </div>
</div>
```
- 展开/收起带动画（max-height 过渡）
- 箭头图标旋转 90 度指示状态

#### 特性网格 `.feature-grid`
- `auto-fit` 响应式网格
- 每项带图标圆标 + 标题 + 描述

### 4.3 交互式模拟演示组件（核心差异化！）

**这是最关键的部分**。对于每一个复杂操作步骤，必须创建纯 CSS 模拟演示图，让客户即使不看真实截图也能理解操作。

#### 模拟终端 `.mock-terminal`
```html
<div class="mock-terminal">
  <div class="mock-terminal-bar">
    <div class="mock-terminal-dots"><span></span><span></span><span></span></div>
    <div class="mock-terminal-bar-title">终端标题</div>
  </div>
  <div class="mock-terminal-body">
    <div class="t-line">
      <div class="t-line-content"><span class="t-prompt">$ </span>命令</div>
      <span class="t-note t-note-green">标注说明</span>
    </div>
    <div class="t-line">
      <div class="t-line-content"><span class="t-dim">输出行</span></div>
      <span class="t-note t-note-yellow">⬅ 这里是关键</span>
    </div>
  </div>
</div>
<div class="mock-caption">▲ 图示说明文字</div>
```
- 红黄绿三点标题栏
- 终端行 `.t-line` 支持右侧标注 `.t-note`（四色变体：green/yellow/cyan/red）
- 闪烁光标 `.t-cursor`
- 颜色类：`.t-green`、`.t-yellow`、`.t-cyan`、`.t-red`、`.t-dim`、`.t-bold`、`.t-prompt`

#### 模拟浏览器 `.mock-browser`
```html
<div class="mock-browser">
  <div class="mock-browser-bar">
    <div class="mock-browser-dots"><span></span><span></span><span></span></div>
    <div class="mock-browser-url">https://example.com/<span class="url-highlight">path</span></div>
  </div>
  <div class="mock-browser-body">
    <!-- 嵌入 panel / login / form 等子组件 -->
  </div>
</div>
```
- URL 栏支持 `.url-highlight` 高亮关键路径

#### 模拟登录页 `.mock-login`
```html
<div class="mock-login">
  <div class="mock-login-box">
    <div class="mock-login-title">面板名称</div>
    <div class="mock-login-row">
      <label>用户名</label>
      <div class="mock-login-input filled">admin</div>
    </div>
    <div class="mock-login-row">
      <label>密码</label>
      <div class="mock-login-input filled">••••••</div>
    </div>
    <div class="mock-login-btn">登 录</div>
  </div>
</div>
```

#### 模拟面板布局 `.mock-panel-layout`
```html
<div class="mock-panel-layout">
  <div class="mock-panel-sidebar">
    <div class="mock-sidebar-row active"><i data-lucide="home"></i> 首页</div>
    <div class="mock-sidebar-row"><i data-lucide="settings"></i> 设置</div>
  </div>
  <div class="mock-panel-main">
    <div class="mock-panel">
      <div class="mock-panel-title">
        标题 <span class="badge">REQUIRED</span>
      </div>
      <!-- 表单或内容 -->
    </div>
  </div>
</div>
```
- 响应式：移动端侧栏改为水平滚动

#### 模拟表单 `.mock-form-grid`
```html
<div class="mock-form-grid">
  <div class="mock-form-row">
    <div class="mock-form-label">字段名</div>
    <div class="mock-form-input highlight">填写值</div>
    <div class="mock-anno">
      <span class="mock-anno-arrow">◀</span>
      <span class="mock-anno-text">① 操作说明</span>
    </div>
  </div>
</div>
```
- `.highlight` 绿色边框高亮重要字段
- `.highlight-warn` 黄色边框高亮需注意字段
- 右侧 `.mock-anno` 带浮动箭头 + 编号标注

#### 模拟开关 `.mock-toggle`
```html
<div class="mock-toggle on"></div>  <!-- 开 -->
<div class="mock-toggle off"></div> <!-- 关 -->
```

#### 模拟按钮 `.mock-btn`
- `.mock-btn-primary`（主色填充）和 `.mock-btn-outline`（边框样式）

#### 模拟数据表 `.mock-table`
```html
<table class="mock-table">
  <thead><tr><th>列1</th><th>列2</th></tr></thead>
  <tbody><tr><td class="mono">值</td><td class="link-text">链接</td></tr></tbody>
</table>
```

#### 模拟服务器信息 `.mock-server-info`
```html
<div class="mock-server-info">
  <div class="mock-server-row">
    <span class="label">IP 地址</span>
    <span class="value">123.45.67.89</span>
    <div class="mock-anno"><span class="mock-anno-arrow">◀</span><span class="mock-anno-text">说明</span></div>
  </div>
</div>
```

#### 模拟演示底部说明 `.mock-caption`
- 每个模拟演示下方必须加 `▲` 开头的说明文字

---

## 阶段五：JavaScript 功能（必须全部实现）

### 5.1 主题切换
```javascript
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;
const savedTheme = localStorage.getItem('[项目名]-theme') || 'dark';
html.setAttribute('data-theme', savedTheme);

themeToggle.addEventListener('click', () => {
  const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('[项目名]-theme', next);
  updateThemeIcon(next);
});
```

### 5.2 系统/客户端 Tab 切换
```javascript
document.querySelectorAll('.sys-tabs').forEach(tabGroup => {
  tabGroup.querySelectorAll('.sys-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      tabGroup.querySelectorAll('.sys-tab-btn').forEach(b => b.classList.remove('active'));
      tabGroup.querySelectorAll('.sys-tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      tabGroup.querySelector(`.sys-tab-panel[data-tab="${tab}"]`).classList.add('active');
    });
  });
});
```

### 5.3 复制到剪贴板（重要：已修复的可靠实现）
```javascript
document.querySelectorAll('.copy-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    const text = btn.dataset.copy;
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
    } catch (e) {
      // 回退方案
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.cssText = 'position:fixed;opacity:0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    }
    // 视觉反馈 —— 直接替换 innerHTML，不要试图操作 Lucide 的 data-lucide 属性
    const origHTML = btn.innerHTML;
    btn.classList.add('copied');
    btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg> 已复制';
    setTimeout(() => {
      btn.classList.remove('copied');
      btn.innerHTML = origHTML;
      lucide.createIcons(); // 全局重新渲染 Lucide 图标
    }, 2000);
  });
});
```
> **已知坑**：Lucide 渲染后 `<i data-lucide="copy">` 会变成 `<svg>`，不能通过修改 `data-lucide` 属性并调用 `lucide.createIcons({ nodes: [el] })` 来切换图标——这种方式不可靠。正确做法是保存原始 HTML、替换为内联 SVG、然后恢复并全局调用 `lucide.createIcons()`。

### 5.4 折叠展开
```javascript
function toggleCollapse(header) {
  const body = header.nextElementSibling;
  header.classList.toggle('open');
  body.style.maxHeight = header.classList.contains('open') ? body.scrollHeight + 'px' : '0';
}
```

### 5.5 滚动揭示（IntersectionObserver）
```javascript
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
    }
  });
}, { threshold: 0.08 });
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
```

### 5.6 自动生成目录（从 DOM 节点）
```javascript
const tocGrid = document.getElementById('tocGrid');
document.querySelectorAll('.step-section').forEach((step, i) => {
  const link = document.createElement('a');
  link.className = 'toc-item';
  link.href = `#${step.id}`;
  link.innerHTML = `<span class="toc-number">${i}</span><span>${step.dataset.stepLabel}</span>`;
  tocGrid.appendChild(link);
});
```

### 5.7 进度导航（侧边栏圆点 + 阅读进度条）
```javascript
// 动态生成进度圆点
const progressRail = document.getElementById('progressRail');
steps.forEach((step, i) => {
  const dot = document.createElement('div');
  dot.className = 'progress-dot';
  dot.innerHTML = `<span class="progress-dot-label">${step.dataset.stepLabel}</span>`;
  dot.addEventListener('click', () => step.scrollIntoView({ behavior: 'smooth' }));
  progressRail.appendChild(dot);
  if (i < steps.length - 1) {
    const line = document.createElement('div');
    line.className = 'progress-line';
    progressRail.appendChild(line);
  }
});

// 滚动时更新当前进度
function updateProgress() {
  const progress = Math.min((window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100, 100);
  document.getElementById('readingProgress').style.width = progress + '%';
  document.getElementById('topbarProgress').style.width = progress + '%';
  // 更新圆点状态...
}
window.addEventListener('scroll', updateProgress, { passive: true });
```

### 5.8 Lucide 图标初始化
```javascript
lucide.createIcons(); // 放在 script 最后
```

---

## 阶段六：模拟演示创建策略

这是区别"普通教程"和"客户级教程"的**核心环节**。

### 6.1 判断哪些步骤需要模拟演示
- **必须加演示的**：涉及 GUI 操作的步骤（面板登录、表单填写、设置切换、用户管理等）
- **必须加演示的**：终端操作中有多个关键输出需要识别的步骤（安装结果、连接过程等）
- **可选演示的**：简单的单行命令步骤（用代码块 + 注释即可）
- 原则：**宁多勿少**，客户看不懂的成本远高于多画一个图的成本

### 6.2 每个演示的结构
1. 选择合适的容器（`.mock-terminal` / `.mock-browser` + 子组件）
2. 模拟真实界面的布局和关键元素
3. 用 `.mock-anno`（编号箭头标注）指示操作顺序
4. 用 `.highlight` / `.highlight-warn` 高亮关键字段
5. 底部加 `.mock-caption` 说明这个演示展示了什么

### 6.3 标注编号规则
- 同一个演示内使用 ①②③④⑤⑥⑦⑧⑨⑩ 编号
- 标注箭头使用 `◀` 指向左侧的操作位置
- 标注文字格式：`① 操作说明`
- 关键标注用黄色，成功/确认标注用绿色 `.green`

---

## 阶段七：内容安全加固章节

无论教程主题是什么，如果涉及服务器/网络配置，必须添加安全加固章节：
- SSH 端口修改（防暴力扫描）
- fail2ban 安装（防暴力登录）
- 自动安全更新
- 防火墙配置
- 密码/密钥修改提醒
- 使用 `.collapse-block` 折叠包裹，降低新手的视觉压力

---

## 阶段八：质量验证清单

完成 HTML 后，逐项检查：

- [ ] 双击 HTML 文件能在浏览器正常打开
- [ ] Dark/Light 主题切换正常，所有元素颜色都跟随变化
- [ ] 主题选择持久化到 localStorage
- [ ] 所有代码块的复制按钮工作正常
- [ ] 所有 Tab 切换正常
- [ ] 所有折叠块展开/收起正常
- [ ] 滚动时进度条和侧边导航正确更新
- [ ] 每个复杂步骤都有对应的模拟演示图
- [ ] 所有模拟演示的标注箭头有浮动动画
- [ ] 移动端响应式布局正常（侧栏、表单、标注适配）
- [ ] HTML 标签正确闭合（使用 Python 脚本验证）
- [ ] 页脚包含安全审核声明和版本信息
- [ ] 教程内容已通过联网验证为最新、安全
- [ ] 使用 `frontend-design` skill 的设计原则（杜绝 AI 生成感的泛用设计）

### 验证 HTML 结构的脚本
```bash
python3 -c "
import re, sys
html = open('[文件路径]', encoding='utf-8').read()
tags = re.findall(r'<(/?)(\w+)[^>]*>', html)
stack = []
void_tags = {'meta','link','br','hr','img','input','source','col','area','base','embed','track','wbr'}
for is_close, tag in tags:
    tag = tag.lower()
    if tag in void_tags: continue
    if is_close:
        if stack and stack[-1] == tag: stack.pop()
    else: stack.append(tag)
print('OK' if not stack else f'Unclosed: {stack}')
"
```

---

## 执行流程总结

```
素材读取 → 内容安全验证(联网) → 确定主题/字体/配色 → 
使用 frontend-design skill → 搭建 HTML 骨架 → 实现设计系统 → 
填充内容组件 → 为复杂步骤创建模拟演示 → 实现 JS 功能 → 
添加安全章节 → 结构验证 → 浏览器打开验证
```

**记住**：这不是给开发者看的文档，是给**完全不懂技术的客户**看的操作指南。每一个可能让人困惑的步骤都需要可视化演示。
