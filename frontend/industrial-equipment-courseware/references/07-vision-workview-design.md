# Reference 07 — Vision Workview HMI Design (Conditional Layer 9)

When the subject device has a **camera-based vision system** as the operator's primary feedback surface — wire bonder, die bonder, wafer prober, dicing saw alignment camera, optical metrology, microscope inspection — the simulator MUST include a vision workview. This is a **conditional 9th layer** on top of the 8 mandatory layers in `02-industrial-grade-criteria.md`.

This file codifies the design template that shipped in:
- KS iConn ProCu Plus(wire bonder · vision-camera workview · L06 prototype)
- 探针台(wafer prober · 双 anchor 工业 CCD HMI · v1.1 final form)

If the device does NOT have a camera vision system (pure mechanical / pure chemical / hidden process), this layer is omitted. Document the omission in the delivery report (so reviewers know it was a conscious decision, not forgotten).

---

## When this layer is mandatory

A device gets a vision workview if ANY of the following is true:

1. The OEM HMI shows a live camera feed as the operator's primary alignment / control surface(wire bonder pad align、die bonder pickup view、prober pad contact、stepper alignment).
2. Operator decisions during RUNNING phase depend on what they see through the camera(not just what sensors read).
3. The OEM PDF / brochure shows the camera image / vision UI in 3+ figures.

Otherwise the layer is optional. Examples that DON'T need it:
- DAD3350 划片机 cutting phase(operator sets up alignment then watches sensor / cut count, not camera)
- 封装模塑机(closed chamber, no operator visual input during cure)
- CMP(operator works against recipe + endpoint detector, not camera)

---

## Architectural rules(non-negotiable for this layer)

1. **Camera dark surface stays dark across themes.** Workview background is hard-coded `#080c14` / `#0d1320` 黑底, NOT `var(--bg)`. Real CCD cameras are physically dark. Theme switch never touches workview background. Text colors inside workview are also hard-coded(white / cyan / amber)— do not reference theme CSS variables.

2. **Build-once SVG + memoized attribute writes.** All shapes built at init via `createElementNS`. Per-frame updates use `setAttribute` ONLY when the value changed:
   ```js
   const newTf = `translate(${x} ${y})`;
   if (g._tf !== newTf) { g.setAttribute('transform', newTf); g._tf = newTf; }
   ```
   `._tf` / `._op` / `._d` caches on the DOM element itself satisfy L8 anti-flicker MutationObserver 0-childList rule even at 60 Hz.

3. **Every-frame animation function MUST be called every frame, NOT dirty-gated.**(J06)Functions that drive frame-to-frame interpolation — exponential smoothing(Z 平滑)、scrub wiggle、spark fade、mini-marker tracking — MUST be invoked unconditionally inside `render()`, NOT inside `if (dirty.has('phase'))` or similar predicates. Dirty-gating is correct for discrete view state(label / class / style),wrong for frame-iterating animation. See `03-anti-flicker-patterns.md` § "Dirty-gated vs every-frame".

4. **Physical anchors + dynamic overlays separated.** Static physical elements(die outline、lead frame、scribe street、wafer outline)built once and never re-positioned. Only the moving elements(bond head capillary、probe needles、stage cross-hair、spark glow)receive per-frame updates.

---

## The 8-element template

A vision workview built to industrial standard ships with all 8 elements below. Skipping any of them lowers the deliverable from "vision HMI replica" to "schematic illustration".

### Element 1 — Permanent dark canvas

```css
.workview {
  background: #080c14;
  /* Plus subtle gradient on top to suggest CCD vignette */
  background: radial-gradient(ellipse at center, #0e1420 0%, #050810 100%);
  color: #c9d6e2;
}
```

SVG sized to a natural CCD aspect like 4:3 or 16:10. Use `viewBox` with mm-realistic coordinates(e.g., `-180 -120 360 240` for a 360 mm field at 1×;adjust by intended magnification).

### Element 2 — HUD four corners

Top-left:CAM ID + REC dot(blinking via opacity memo);例 `CAM · TOP · 100×`
Top-right:Process state(WIRE / HEATER / etc.)or 当前 die R/C(prober)
Bottom-left:Frame counter / FOV size / S/N
Bottom-right:Bonded count / CAP LIFE % / yield

每个 chip 12×8 px 圆角矩形 + 单色文字。Memo guards on every text update。HUD 是恒定结构,只有数字 / 状态变,布局永不变。

### Element 3 — Phase chip(centered bottom)

A big horizontal pill showing the current phase in **OEM 原文 + 序号**:

- Wire bonder: `P1 · LOOK` / `P2 · APPROACH` / `P3 · 1ST BOND` / ...
- Prober: `P1 · IDLE` / `P3 · OVERTRAVEL` / `P4 · MEAS` / ...

Color states:
- `var(--accent)` 默认
- 红色背景闪烁 if `mode === 'EMSTOP' || mode === 'FAULT'`(同步 alarm)
- 静默灰 if `mode === 'IDLE' || mode === 'PAUSED'`

Memo guard:cache(phase, mode)tuple,变才写。注意 EMSTOP→IDLE 这种 mode 变 phase 不变的情况要捕获(L27)。

### Element 4 — Physical anchor layer(static)

Built once, never re-positioned. Subject-specific:

| Device | Static anchors |
|---|---|
| Wire bonder | Die outline + lead frame fingers + Au/Cu pads(4-8 个)+ scribe line |
| Die bonder | Die source carrier + target substrate cavity + pickup tool footprint |
| Prober | Current die + adjacent [W][E] dies(部分可见)+ scribe street + pad array |
| Dicing align | Wafer outline + reference street + previous cut traces |
| Stepper | Reticle field outline + exposure shot box grid |

Use a stable color scheme:
- `var(--pad)` 或 `#c9a960` 的金黄 for metal pads
- `#5b8def` 或 `var(--wafer)` for silicon
- `#3a4658` 灰 for scribe / 切割道
- `#1a1f2e` 深灰 for substrate / 衬底

### Element 5 — Dynamic moving elements(per-frame)

Subject-specific:

| Device | Moving elements |
|---|---|
| Wire bonder | Capillary tip(XY tracking)+ EFO spark glow + wire trail(累积 multi-cycle) |
| Die bonder | Pickup tool(Z 平滑) + die-in-flight indicator + thrust meter |
| Prober | Probe needles(Z 平滑,P3 OVERTRAVEL 时 lateral scrub)+ spark glow on touchdown |
| Dicing | Blade Z position + cut trace line(累积) |

每个 moving element 走 `_tf` / `_op` memo guard。Spark glow 用 `<radialGradient>` + opacity ramp。Wire trail 用累积 `<path d="M ... L ...">` 节点,**每 cycle 末尾 append 一段而不是清空重建**(L06 element 7)。

### Element 6 — Scale ruler

A small horizontal scale bar in a corner — e.g., `100 µm` between two tick marks. Gives the user a sense of scale. Built once with `<line>` + `<text>`,never updates(scale doesn't change unless magnification is dynamic; in that case memo-guard the width).

### Element 7 — Scanline / grain overlay(CRT 摄像头质感)

Two thin horizontal lines that scroll downward at ~0.5 Hz, opacity ~2%:

```css
.scanline {
  background: repeating-linear-gradient(
    transparent 0px, transparent 3px,
    rgba(255,255,255,0.02) 4px, rgba(255,255,255,0.02) 4px
  );
  animation: scanline 6s linear infinite;
}
@keyframes scanline {
  from { transform: translateY(-100%); }
  to { transform: translateY(100%); }
}
```

Optional dust / noise pattern via `<pattern>` SVG — adds CCD authenticity but must stay below 3% alpha or the workview becomes muddy.

### Element 8 — Cycle trail accumulation

After each successful operation cycle, the workview accumulates a visible trace:
- Wire bonder: every successful wire stays drawn(faint Au curve)— after 100 cycles the package looks "filled in"
- Prober: every touchdown leaves scrub marks on the pad(small ellipses)— after 100 TD pad shows accumulated damage
- Dicing: every cut stroke leaves a kerf line — operator sees the cut grid build up

This is the difference between "operator hits keys" and "operator sees the work they did". Important for muscle memory training.

Cap the accumulation to avoid SVG bloat:
```js
const MAX_TRAIL = padCount * 26;  // prober example
if (scrubGroup.children.length > MAX_TRAIL) {
  scrubGroup.removeChild(scrubGroup.firstChild);
}
```

---

## Dual-anchor pattern(wafer-class devices)

For devices that work on a wafer(prober、dicing、stepper alignment、wafer-level test),add a **second small workview** anchored bottom-right of the main workview:

- **Main view**:high-magnification probe / blade / pickup tool view(100× — 500× equivalent)— operator's primary focus
- **Mini wafer map**:low-magnification full-wafer status overlay(0.5× — 1× equivalent)— operator's situational awareness

```html
<div class="workview-container">
  <svg class="workview-main" viewBox="...">...</svg>
  <div class="mini-wafer">
    <svg viewBox="-110 -110 220 220">
      <defs>...wafer-disc gradient...</defs>
      <circle r="100" fill="url(#wafer-disc)" />
      <path d="M -8 100 L 0 92 L 8 100 Z" fill="#0d1117" />  <!-- notch -->
      <g id="wafer-cells"></g>
      <circle id="curr-die-dot" r="2.5" fill="cyan" />
      <text class="ax">+X</text>
    </svg>
    <div class="wafer-lbl">
      <span id="wafer-tot">621</span> / 
      <span id="wafer-pass">0</span> pass / 
      <span id="wafer-fail">0</span> fail
    </div>
  </div>
</div>
```

CSS:
```css
.mini-wafer {
  position: absolute;
  right: 10px; top: 50%;
  transform: translateY(-50%);
  width: 96px; height: 124px;
  background: rgba(4,7,13,0.85);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 4px;
}
```

### Mini wafer geometry — J07 rule

Building the die grid inside a circular wafer outline:

```js
function initWafer(D, P) {
  // D = wafer diameter (mm), e.g. 200
  // P = die pitch (mm), e.g. 7
  const R_max = D/2 - 1.5;   // physical containment cutoff
  const R_use = D/2 - 6;     // edge-exclusion start (5 mm edge ring per SEMI M1)
  // INVARIANT: R_max > R_use + P/2  -- else no die lands in the edge ring
  // 200mm / 7mm pitch → R_max=98.5, R_use=94 → 52 edge dies + 569 valid + 0 outside = 621 total
  const dies = [];
  for (let row = -Math.floor(D/(2*P)); row <= Math.floor(D/(2*P)); row++) {
    for (let col = -Math.floor(D/(2*P)); col <= Math.floor(D/(2*P)); col++) {
      const cx = col * P, cy = row * P;
      const r = Math.hypot(cx, cy);
      if (r > R_max) continue;
      const status = (r > R_use) ? 'edge' : 'untested';
      dies.push({ row, col, cx, cy, status });
    }
  }
  return dies;
}
```

5-state die color map:
- `untested` 暗蓝 `#1f2a44`
- `current` 青光 `#06b6d4` + 1.5px stroke
- `pass` 绿 `#22c55e`
- `fail` 红 `#e23b3b`
- `edge` 黑 `#0a0d14`(SEMI M1 edge-exclusion ring)

Self-check after initWafer:
```js
APP.wafer.dies.filter(d => d.status === 'edge').length >= 30
// For 200mm + 7mm pitch this is 52. Below 30 = formula bug.
```

---

## Card-type / recipe-type dynamic build pattern

If the visible array changes with card / recipe(prober probe count、wire bonder wire diameter、stepper reticle field size),the build function MUST be **idempotent + multi-hook**:

```js
function buildPadsAndNeedles() {
  // Clear existing
  while (padsG.firstChild) padsG.removeChild(padsG.firstChild);
  while (shaftsG.firstChild) shaftsG.removeChild(shaftsG.firstChild);
  while (sparkG.firstChild) sparkG.removeChild(sparkG.firstChild);
  // Build per card type
  const layout = CARD_LAYOUTS[APP.cardType];   // 'canti' / 'vert' / 'mems'
  layout.pads.forEach(p => padsG.appendChild(rect(p)));
  layout.needles.forEach(n => shaftsG.appendChild(line(n)));
  // ...
}

// Hook from ALL entry points that can change the array:
runCmd handler 'POWER':         buildPadsAndNeedles();
runCmd handler 'CARD_CANTI':    buildPadsAndNeedles();
runCmd handler 'CARD_VERT':     buildPadsAndNeedles();
runCmd handler 'CARD_MEMS':     buildPadsAndNeedles();
runCmd handler 'PROBE_CLEAN':   buildPadsAndNeedles();
runCmd handler 'CARD_CHANGE':   buildPadsAndNeedles();
DOMContentLoaded:               buildPadsAndNeedles();
```

Forgetting one hook = phantom needles when user does that operation. List all 5+ entry points before declaring done.

---

## 18-dim self-check additions for this layer

When this layer is included, append to the simulator 18-dim self-check:

| # | Dim | Check | Verification |
|---|---|---|---|
| V1 | Vision workview present | `document.querySelector('.workview svg')` exists | DOM |
| V2 | Dark canvas hard-coded | `getComputedStyle(workview).backgroundColor` not affected by theme toggle | MCP toggle test |
| V3 | HUD 4 corners + phase chip + scale ruler all present | Element-count check | MCP |
| V4 | Frame-iterating animation runs every frame | After triggering a Z target change, sample SVG `transform` at 1s intervals; must converge within 5 ramp time constants | MCP |
| V5 | Mini wafer geometry valid(if wafer device)| `APP.wafer.dies.filter(d=>d.status==='edge').length >= 30` for 200mm + 7mm pitch | MCP |
| V6 | Card-type dynamic build hooked from all 5+ entry points | `grep buildPadsAndNeedles\(\) simulator.html` ≥ 5 occurrences | static |
| V7 | Trail accumulation works | Run 5 cycles, expect 5 trail children added(within cap) | MCP MutationObserver(child + allowed here, NOT a flicker — it's accumulation) |
| V8 | Theme toggle does NOT recolor workview | Take screenshot both themes, workview pixels in dark zone identical | MCP screenshot diff |

---

## Reference deliverable comparisons

| Project | Workview style | Mini map | Phase chip | Trail accumulation |
|---|---|---|---|---|
| DAD3350 | omitted(cut phase has no camera-primary HMI)| — | — | — |
| AD8312PLUS | basic die-pickup illustration | — | yes | — |
| KS iConn | full vision HMI(L06 prototype)| — | yes | wire trail |
| 模塑机 | omitted(closed chamber)| — | — | — |
| 探针台 v1.0 | rectangular die-grid schematic | — | partial | — |
| 探针台 v1.1 | full vision HMI + dual anchor | **yes**(621 dies, 5 status)| yes | scrub marks(cap 208) |

探针台 v1.1 is the canonical reference for wafer-class devices.
KS iConn is the canonical reference for non-wafer-class(packaged-device-on-frame).

---

## Anti-patterns

| Anti-pattern | Why fails |
|---|---|
| Workview uses `var(--bg)` for background | Light theme makes camera surface white → not CCD-realistic; breaks every-time visual contract |
| `updateWorkview()` placed inside `if (dirty.has('phase'))` | J06 — frame-iterating animation stalls when phase doesn't change; Z 平滑 dies at frame 1 |
| `buildPadsAndNeedles()` only hooked from one entry point | Phantom needles after card change / clean operations |
| Mini wafer `R_max <= R_use + pitch/2` | J07 — no die ever lands in edge ring; mini map looks unrealistic with no SEMI M1 edge band |
| Trail accumulation without cap | After hours of operation SVG grows unbounded → eventual page hang |
| HUD writes text every frame without memo | MutationObserver characterData counts will be high(though not childList — still wastes CPU)|
| EMSTOP shows phase chip but doesn't change color | Operator can't tell at a glance the machine is in emergency |
| Scale ruler in arbitrary units / no real-world relation | Defeats the purpose of "giving sense of scale" |

---

## When to update this file

After every project that adds a vision workview:
- New subject device → add a row to the reference deliverable comparison table
- New camera-class element discovered → add to the 8-element template(currently 8;may grow)
- New geometry-class issue → document the rule(J07-style)
