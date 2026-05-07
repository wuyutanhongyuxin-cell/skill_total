---
name: single-file-courseware
description: Use when building a single-file HTML teaching handout / cheat sheet / 复习密钥 for non-technical students who must double-click a .html file and have it just work — no server, no install, no internet. Triggers on requests like "做一份给不会配置环境学生看的 HTML 课件", "把 markdown 笔记做成可视化教学网页", "单文件双击就能看", "带 dark/light + tabs + 模拟测试的复习材料", "把这套移植成 PDF/打印版". Covers content sourcing from MD, aesthetic commitment, embedded-markdown architecture, dark/light theming, tabs, multilingual examples, quiz module with localStorage scoring, PDF/print export, and 12-dimension cross-validation.
---

# Single-File Courseware HTML 生产工作流

This skill packages the workflow that shipped `古典文法考试复习密钥.html` (116 KB, 2440 lines, 11 tabs, 42-question mock test, dark/light theme, print-to-PDF) on 2026-05-07. The original source was a long markdown cheat sheet; the deliverable is one self-contained `.html` that students double-click to open.

```
stage 1 — content audit       (read MD, bucket into tabs)
stage 2 — aesthetic commit    (reject AI defaults, pick a vibe)
stage 3 — single-file build   (CDN deps, embedded MD, no fetch)
stage 4 — interactive layers  (tabs, theme, examples, quiz)
stage 5 — print/PDF layer     (@media print, pre-render hook)
stage 6 — cross-validation    (12-dimension self-check)
```

---

## When to fire

- User wants a long markdown study guide / handout / cheat sheet turned into a polished pedagogical webpage.
- Audience explicitly cannot run `npm install`, `python -m http.server`, or anything more involved than double-clicking a file.
- User asks for "可视化教学", "给学生看的复习材料", "可以打印成 PDF 的教辅", "带模拟测试的网页版笔记".
- Output should look like a finished editorial product, not a raw README dump or a Bootstrap demo.
- Need offline persistence: theme, last-tab, quiz best-score across browser reloads.

Do NOT fire for:
- Marketing landing pages (use frontend-design skill directly with no MD source constraint)
- Multi-page docs sites (use Docusaurus / VitePress instead)
- Apps that need a backend or auth

---

## Non-negotiable architectural rules

1. **One `.html` file, period.** No sibling `.css`, `.js`, `.json`. The student will not unzip a folder. The student will not run a server. Honor the double-click contract.
2. **Third-party deps via CDN with pinned versions.** Acceptable: `marked@12.0.2` for markdown rendering, Google Fonts for typography. Reject: anything that needs a build step (Tailwind JIT CDN is OK for prototypes but bloats and looks generic — don't use it here).
3. **Markdown content embedded via `<script type="text/markdown" id="src-XXX">…</script>` blocks**, then rendered into `<div id="md-XXX">` via `marked.parse(...)` on first tab activation. The `script` tag with non-JS type acts as inert text storage that survives HTML parsing.
4. **NEVER `fetch('content.md')`**. The `file://` protocol blocks `fetch` of local files in all major browsers. This will silently fail when the student double-clicks. Verify by grepping the final file for `fetch(`, `XMLHttpRequest`, `import(`, `<iframe src=`. Only CDN URLs allowed.
5. **`<meta charset="utf-8">` MUST be the first child of `<head>`.** Mandatory for CJK / diacritic content. Save the file as UTF-8 without BOM.
6. **State persistence via localStorage with one namespaced prefix** (e.g. `kotenbunpou-theme`, `kotenbunpou-tab`, `kotenbunpou-quiz-best`). Do NOT collide with other apps' keys.
7. **Theme is read in `<head>` before the stylesheet** to avoid flash-of-wrong-theme on reload (see Step 6).

---

## Step-by-step workflow

### Step 1 — Inventory the source MD

Read the source markdown end-to-end. Bucket it into 7-12 distinct tabs that map to natural pedagogical sections. Watch for:

- Sections too thin alone → merge with a neighbor
- Sections that exceed ~600 rendered lines → split
- Cross-references that need anchor links → catalog them so internal `<a href="#…">` works after rendering
- Content that should NOT be markdown (uniform tabular data like example sentences, vocabulary, quiz questions) → extract to JS arrays for consistent rendering

**Self-check**: Each tab has a clear pedagogical purpose. No tab is "Misc" or "Other". Every section is reachable.

### Step 2 — Commit to an aesthetic direction (use frontend-design skill)

Reject the AI-default Tailwind/Inter/Bootstrap look. Invoke the `frontend-design:frontend-design` skill if not already invoked. Pick an extreme tied to the subject:

- Heian-court editorial (sumi ink + vermillion seal + kinari paper) — Japanese classics
- Brutalist typewriter — programming / systems texts
- Scientific journal LaTeX — math / physics
- Memphis postmodern — design / arts
- Bauhaus geometric — architecture / form
- Wabi-sabi monochrome — meditation / philosophy

Define the palette as CSS variables on `:root`, with `[data-theme="dark"]` overrides that are deliberately re-pigmented (NOT a luminance flip):

```css
:root {
  --bg: #f4ecd8;        /* page surface */
  --ink: #1c130a;       /* primary text */
  --accent: #b73027;    /* one bold accent — used sparingly */
  --rule: #8a7a5c;      /* dividers */
  --muted: #6e5d3f;     /* secondary text */
  --paper: #fbf6e7;     /* card surface */
  --shadow: 0 1px 0 rgba(28,19,10,.08), 0 6px 24px -10px rgba(28,19,10,.18);
}
[data-theme="dark"] {
  --bg: #0e0a07;
  --ink: #ece1c8;
  --accent: #e05a48;
  --rule: #4a3f2c;
  --muted: #a89878;
  --paper: #18120b;
  --shadow: 0 1px 0 rgba(0,0,0,.6), 0 8px 28px -10px rgba(0,0,0,.7);
}
```

**Self-check**: A student glancing at the page for 2 seconds should be able to name the vibe ("looks like an old scroll", "feels like a journal article"). If they'd just say "looks like a website", redo.

### Step 3 — Typography pairing

Pair a distinctive display face with a refined body face. Avoid Inter, Roboto, Arial, system stacks. For CJK, mind Han glyph coverage — many "Japanese" Google Fonts only cover Joyo and break on classical kanji.

Vetted CJK pairings (subject → fonts):

| Subject | Display | Body |
|---|---|---|
| Japanese classics / 古文 | Shippori Mincho B1 | Klee One |
| Modern Japanese essay | Noto Serif JP | Zen Kaku Gothic Antique |
| Chinese classics / 文言文 | Noto Serif SC | LXGW WenKai |
| Code-heavy text | JetBrains Mono | IBM Plex Sans |
| Math / formal | EB Garamond | Crimson Pro |

Always include a Latin-italic display face for emphasized loanwords (Cormorant Garamond italic works almost everywhere).

### Step 4 — Tab system

7-12 tabs. Custom tab labels matching the aesthetic (kanji numerals 壹貳參肆伍陸柒捌玖拾 for Heian; roman numerals for journal; emoji for playful). One hidden `<section class="panel">` per tab. ARIA roles: `tablist` / `tab` / `tabpanel`. Persist active tab to `<prefix>-tab`. Render embedded markdown lazily on first tab activation:

```js
const tabs = document.querySelectorAll('[role="tab"]');
const panels = document.querySelectorAll('[role="tabpanel"]');
const renderMarkdownInto = (panel) => {
  panel.querySelectorAll('[data-md-source]').forEach(slot => {
    if (slot.dataset.rendered) return;
    const src = document.getElementById(slot.dataset.mdSource).textContent;
    slot.innerHTML = marked.parse(src);
    slot.dataset.rendered = '1';
  });
};
tabs.forEach((t, i) => t.addEventListener('click', () => {
  tabs.forEach(x => x.setAttribute('aria-selected', 'false'));
  panels.forEach(p => p.hidden = true);
  t.setAttribute('aria-selected', 'true');
  panels[i].hidden = false;
  renderMarkdownInto(panels[i]);
  localStorage.setItem('<prefix>-tab', i);
}));
```

### Step 5 — Multilingual examples (when source is foreign-language)

If subject is foreign-language with a translation gloss (古文 → 現代日語 → 中文; 文言文 → 白话 → English; etc.), render each example as a 3-column row, NOT free-form markdown. Hardcode as a JS tuple array `[id, source, original, modern, target]` so structure is uniform across all entries. Add a source filter (filter buttons by lesson/chapter). For 50+ examples this is worth the structure.

User's repeated guidance from the original session: **example sentences MUST be paired with target-language translations**. Do not ship examples without the translation column even if the source MD lacks them — fill in the translations yourself or stop and ask.

### Step 6 — Dark/light toggle without flash

Single button in toolbar. Toggle `<html data-theme="dark">`. Persist to `<prefix>-theme`.

**Critical**: read localStorage BEFORE the stylesheet loads, to prevent flash-of-wrong-theme:

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>…</title>
  <script>
    // Read theme synchronously before any paint.
    // This script must come BEFORE the <link rel="stylesheet">.
    const saved = localStorage.getItem('<prefix>-theme');
    if (saved) document.documentElement.dataset.theme = saved;
  </script>
  <link rel="stylesheet" href="…">
</head>
```

### Step 7 — Quiz module with localStorage scoring

Array of `{type, stem, options, answer, explain}`. Each rendered as a card with click-to-grade option buttons. Per-question state stored in-memory. Total score = `Σ(correct === true)`.

Best-score persisted to `<prefix>-quiz-best`, ONLY updated when the new score exceeds the stored value:

```js
function recordScoreIfBest() {
  const cur = score();
  const best = +localStorage.getItem('<prefix>-quiz-best') || 0;
  if (cur > best) localStorage.setItem('<prefix>-quiz-best', cur);
  updateScore();
}
function updateScore() {
  document.getElementById('scoreNum').textContent = score();
  document.getElementById('totalNum').textContent = QUIZ.length;
  const best = +localStorage.getItem('<prefix>-quiz-best') || 0;
  document.getElementById('bestScore').textContent = best === 0 ? '—' : best + ' / ' + QUIZ.length;
}
```

"Reset" button clears in-memory state but preserves the best-score (intentional — grinding for a high score is part of the UX).

For exam-prep contexts: distribute questions across all known exam question types proportional to their weight. The 古典文法 deliverable used 6/11/8/6/11 across 5 question types — match the actual exam composition, don't randomize.

### Step 8 — Print / PDF export via @media print

Add a print button in the toolbar and an `@media print` block:

```css
@media print {
  @page { size: A4; margin: 1.4cm 1.6cm; }
  body { background: var(--bg); }
  .toolbar, .tabs, .ex-filters, .reset-btn,
  button[aria-controls], .print-hide { display: none !important; }
  .panel { display: block !important; }
  .panel:first-of-type { page-break-before: auto; }
  .panel { page-break-before: always; }
  .explain { display: block !important; }       /* expand all quiz answers */
  .quiz-card { page-break-inside: avoid; }
  table { border-collapse: collapse; }
  tr { page-break-inside: avoid; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
```

**Critical pre-render**: tabs that haven't been activated yet have unrendered markdown placeholders. Calling `window.print()` directly prints empty divs. Force-render every panel BEFORE printing:

```js
document.getElementById('printBtn').addEventListener('click', () => {
  panels.forEach(p => renderMarkdownInto(p));   // pre-render all lazy markdown
  setTimeout(() => window.print(), 80);          // let layout settle
});
```

The 80ms `setTimeout` is intentional — gives the browser one paint cycle to apply the new layout before the print snapshot is taken.

---

## Cross-validation checklist (12 dimensions)

Run ALL of these before declaring done. Marking any of them N/A requires explicit reasoning written into your final report, not silence. This is the "多维度严格准确地交叉自检" the user demanded.

| # | Dim | Check | How |
|---|---|---|---|
| 1 | File transport | Double-click `.html` opens correctly | Test in actual OS file explorer (`explorer.exe path`), not via dev server |
| 2 | Encoding | CJK + diacritics render | Save UTF-8 no BOM. Inspect via `Get-Content -Encoding utf8` first 2 lines should start with `<!doctype html>`, NOT `﻿` |
| 3 | Offline (no fetch) | No `fetch()` to local files | `Grep -n "fetch\(\|XMLHttpRequest\|import\(\|<iframe src=\"\.\|<iframe src=\"file" file.html` — only CDN URLs allowed |
| 4 | First paint | No theme flash on reload | Reload 5x in dark mode — never see light flash. The `<script>` reading localStorage MUST appear before `<link rel=stylesheet>` |
| 5 | Tabs | All tabs activate and render | Click each tab; markdown panels fill with content; no empty `<div>` |
| 6 | Persistence | Theme + tab + quiz-best survive reload | Set state, F5, verify state restored. Check localStorage in DevTools Application tab |
| 7 | Quiz logic | Score increments on correct only; explain shows | Walk all questions; verify scoring math; verify wrong answers also show explain |
| 8 | Print | All sections + all answers visible in print preview | Ctrl+P; preview shows every section, every quiz answer expanded, no toolbar visible |
| 9 | Mobile | Layout doesn't break <600px | Resize browser to 375px; no horizontal scroll; tabs scroll horizontally instead of overflowing |
| 10 | Accessibility | Keyboard nav works | Tab through; focus rings visible; Space/Enter activates buttons; aria-selected updates |
| 11 | Console | Zero errors, zero warnings on load | DevTools console after F5. Network tab shows only CDN requests succeed (200) |
| 12 | Size sanity | File size matches content density | ~2KB per KB of source markdown is typical (markup + CSS + JS overhead). >5MB = font/SVG bloat to investigate |

If any row fails: **fix it**. Do NOT write a "known issue" note in lieu of fixing. Stop and re-plan if a fix is non-trivial — don't push through.

### Verifying with PowerShell after build

```powershell
# 1+2 file size + first bytes
$f = "path\to\output.html"
Get-Item $f | Select-Object Length
Get-Content $f -TotalCount 2

# 3 no local fetches
Select-String -Path $f -Pattern 'fetch\(|XMLHttpRequest|<iframe src="\.|<iframe src="file'

# Open in default browser
Start-Process $f
```

The `Get-Content -TotalCount 2` first line should be `<!doctype html>` (or `<!DOCTYPE html>`). If it's `<U+FEFF>...` you have a BOM problem — re-save the file as UTF-8 without BOM.

---

## Anti-patterns (do not do these)

| Anti-pattern | Why it fails |
|---|---|
| External `style.css` / `app.js` files | Student said double-click; honor it. Two files = broken contract |
| `fetch('content.md')` | CORS-blocked under `file://`. Silent failure. |
| `<iframe src="content.html">` | Cross-origin under `file://` |
| Tailwind via CDN with default classes | Looks like every AI-built site. Pick a real aesthetic. |
| Generic UI library components (shadcn, MUI, Chakra) | Same homogenization problem |
| "Mobile first responsive" = everything stacks vertically | Lazy. Design the desktop layout you want, then thoughtfully degrade |
| Hand-waving the print CSS | Will print as garbage. Test it with the actual Print Preview |
| Skipping the Chinese/target-language column on examples | Re-read the original session: user explicitly demanded this |
| Hardcoding "/10" in quiz UI | When you expand to 42 questions later, the UI lies. Always use `QUIZ.length` |
| Putting the theme `<script>` after `<link rel=stylesheet>` | Causes flash-of-wrong-theme on every reload |

---

## Adapting to a new subject

The architecture is portable. The aesthetic is NOT — every subject must get its own distinct visual identity.

To reuse for a different subject:

1. Replace markdown source blocks (`<script type="text/markdown" id="src-XXX">`)
2. Update tab count and labels (kanji → roman → whatever fits the new vibe)
3. **Pick a new aesthetic direction** — do not copy the Heian palette to a chemistry handout
4. Replace example/vocab/quiz JS arrays with the new subject's data
5. Re-key localStorage with a new prefix (`<prefix>-theme`, `<prefix>-tab`, `<prefix>-quiz-best`)
6. Update font pairing per the table in Step 3
7. Re-walk the 12-dimension cross-validation checklist

---

## What this skill does NOT cover

- Server-rendered or multi-page docs sites — use Docusaurus / VitePress
- PWA conversion (manifest + service worker) — separate concern, requires hosting
- Authoring the source markdown itself — assumes input MD already exists
- Generating quiz questions from scratch — you must understand the subject; this skill assumes you've drafted the questions before invoking it
- Translating examples — the skill enforces the trilingual format, but you (the model) must do the translation work upstream

---

## Reference deliverable

`E:\claude_ask\bilibili_learn\古典文法考试复习密钥.html` — the canonical implementation. 116 KB, 2440 lines, 11 tabs, 42-question quiz, full dark/light, full print/PDF, file://-safe. Inspect it as the reference when building the next instance.
