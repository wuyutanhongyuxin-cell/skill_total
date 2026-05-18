---
name: industrial-equipment-courseware
description: Use when building a paired single-file HTML deliverable set for industrial / semiconductor / process equipment — an operation manual courseware PLUS an industrial-grade web simulator — from an OEM PDF + online cross-validated research. Triggers on requests like "给 XX 设备做一份操作学习手册 + 仿真训练器", "联网查最权威方案做工业级仿真", "把 DAD3350 / SECS/GEM / dicing / wire bonder / steppers 这类设备教学化", "单文件双击就能学 + 能模拟操作". Covers authority-source research with cross-validation, OEM PDF deep extraction, dual-artifact architecture (manual + simulator with coherent aesthetics + localStorage namespace), industrial-grade simulator requirements (state machine + interlock chain + sensor physics + fault injection + Web Audio + training scenarios + anti-flicker), automated MCP verification (physics/interlock/MutationObserver patterns), safety + copyright protocol.
---

# Industrial Equipment Courseware — Manual + Simulator 全流程 Skill

This skill packages the workflow that shipped the DAD3350 paired artifacts (操作完整手册 225 KB + 仿真训练器 126 KB) — researched against authoritative sources, anchored to a 388-page OEM manual, built as two single-file HTML deliverables with coherent aesthetics, verified via chrome-devtools MCP. Use this as the rigorous foundation for any "OEM industrial device → educational courseware + operable simulator" project.

```
stage 0 — scope & legal           (subject, audience, fair-use, no public redistribute)
stage 1 — research & x-validate   (官方 + 学术镜像 + 开源 + 行业标准,≥2 independent sources per claim)
stage 2 — OEM PDF deep extraction (≤20 pages/batch, 章节代码标注,术语保留原文)
stage 3 — dual-artifact design    (manual tabs + simulator FSM + shared aesthetics)
stage 4 — single-file HTML manual (defers to single-file-courseware skill)
stage 5 — industrial-grade simulator
                                  (8 mandatory layers: FSM + interlocks + sensor physics
                                   + fault injection + Web Audio + status bar + error codes
                                   + training scenarios)
stage 6 — MCP automated QA        (3 templates: physics / interlock / MutationObserver)
stage 7 — delivery & archive      (12-dim manual self-check + 18-dim simulator self-check)
```

This skill is **rigid for safety/legal and stages 0/1/6** (no shortcuts on cross-validation or QA), **flexible for visual/structural choices in 2/3/4/5** (adapt to subject).

---

## When to fire

- User asks to build a web simulator or operator-training courseware for a real industrial device (dicing saw, wire bonder, stepper, etch tool, CMP, CNC, PLC-driven equipment, lab instrument, HVAC).
- Source material is an OEM operation manual PDF (often vendor-stamped "DO NOT COPY") + audience cannot run dev servers.
- User demands "工业级" / "industrial-grade" / "尽可能真" / "权威先进的方案".
- Output must be one or two `.html` files that double-click open offline.
- User pairs request with research demand: "联网查 / 调研最优方案 / 交叉验证".

Do NOT fire for:
- Pure UI mockup with no physics / no real device data → use `frontend-design` alone.
- Multi-page docs / hosted SaaS courseware → use Docusaurus.
- A simple operation cheat sheet without simulator → use `single-file-courseware` alone.
- A simulator without educational artifact → use `frontend-design` + simulation libraries directly.

---

## Non-negotiable architectural rules

1. **Always two artifacts in coherent aesthetic** unless user explicitly requests one. Manual teaches **why + what + procedures**; simulator teaches **operator muscle memory**. They must share CSS variables + font stack + localStorage prefix family (`<device>-` for manual, `<device>-sim-` for simulator).
2. **Single `.html` per artifact, no build pipeline.** Honor the double-click contract. All deps via pinned CDN. No `fetch('content.md')` (CORS-blocks under `file://`). See `single-file-courseware` skill non-negotiables — they all apply here.
3. **Every external technical claim has ≥2 independent verifiable sources before being baked into the deliverable.** "Independent" means not the same vendor / not the same author / not a syndicated copy. Sources are catalogued and the link list lives in the simulator's About panel.
4. **OEM copyright respected.** OEM manuals stamped `<DO NOT COPY>` / `Confidential` / `Proprietary` may be used as fair-use educational reference **for local learning only**. The HTML deliverable must (a) not reproduce verbatim more than short quotes, (b) carry an unambiguous disclaimer: "Educational unofficial replica — not affiliated with, endorsed by, or distributed on behalf of <OEM>". Never publish to public repos / cloud unless OEM legal permission verified.
5. **Industrial-grade = 8 mandatory layers** for the simulator (see `references/02-industrial-grade-criteria.md`). Skipping any layer disqualifies the simulator from being called "工业级" — fall back to honest "教学演示" labelling.
6. **Real device parameters anchor the simulation.** Sensor ranges, RPM limits, interlock conditions, error codes, time constants all come from the OEM PDF — not invented. If a value isn't in the PDF, mark it in code with `// EXTRAPOLATED — not in OEM manual`.
7. **Anti-flicker required for any UI region updating ≥ 10 Hz.** No `innerHTML = '...'` rebuilds in tick loops. Build-once + memoized surgical updates. See `references/03-anti-flicker-patterns.md`.
8. **MCP-verified, not just visually plausible.** All **4** MCP test patterns (physics / interlock / MutationObserver / scenario walkthrough) run before declaring done. Test results stored in `_qa_screenshots/` and printed in the delivery report. **Every MCP test session opens with `localStorage.clear()` + hard reload + http://127.0.0.1:18080 server**(L31 — file:// is blocked by playwright;chrome-devtools-mcp lock collides with user's main Chrome;8765/8080 hit Windows dynamic TCP exclusion. The 18080 + playwright + http:// combination is the only one verified across 5 projects).
9. **Safety information is not paraphrased.** DANGER / WARNING / CAUTION / NOTICE language from the OEM is preserved bilingually (original + 中译). Paraphrasing safety language is a defect.
10. **Auto mode-friendly.** Skill must run with minimal clarification; reasonable defaults are spelled out. The model makes calls and continues; user redirects if needed.

---

## Stage-by-stage workflow

### Stage 0 — Scope & legal (must complete before any other stage)

Confirm or infer these. If a value cannot be confirmed, write the model's best inference + label it `INFERRED`:

| Field | Example (DAD3350) | Default if unspecified |
|---|---|---|
| Subject device | DISCO DAD3350 dicing saw, sw v1.5 | (must be specified) |
| OEM | DISCO Corporation | from PDF cover |
| Audience | Semiconductor packaging engineers / operators | "技术操作员 + 学习者" |
| Primary language | 中文 + 必要术语英文 | 中文 + 术语英文 |
| Deliverable count | 2 (manual + simulator) | 2 |
| Distribution scope | LOCAL ONLY — not public | LOCAL ONLY |
| Output directory | `E:\claude_ask\bilibili_learn\` | working directory |
| File-name prefix | `<DeviceModel>-` | inferred from subject |
| localStorage namespace | `dad3350-` / `dad3350-sim-` | `<model-lowercase>-` / `<model-lowercase>-sim-` |

Write a one-paragraph scope statement and surface it to the user inline (no `tasks/scope.md` file unless asked). Get tacit approval by continuing — auto-mode is acceptable since the user is informed.

**Gate 0 → 1**: Scope paragraph stated. No legal red flag (e.g., user asks to put the artifact on a public CDN with OEM marks — refuse unless authorized).

### Stage 1 — Research & cross-validation

Use `WebSearch` and `WebFetch` (or research subagents) to collect authoritative material. Required source classes:

| Source class | Why | Example for DAD3350 |
|---|---|---|
| OEM official | Authoritative on parameters | https://www.disco.co.jp/eg/products/dicer/dad3350.html |
| OEM training / e-learning | Reveals expected pedagogical scope | https://www.disco.co.jp/eg/training/ |
| Academic mirror of manual | Verifies manual content + provides fallback link | https://wiki.nanofab.usc.edu/images/4/47/Dicing_Saw_Manual.pdf |
| Open-source reference impl | Cross-check architecture choices | https://cnc.js.org/ (CNCjs), https://github.com/cncjs/cncjs |
| Commercial HMI exemplar | Best-of-breed reference | https://inductiveautomation.com/ignition/modules/perspective (Ignition Perspective) |
| State-machine library evidence | Justify FSM approach | https://stately.ai/docs/xstate (XState v5) |
| E-learning standard | If training-record tracking matters | https://xapi.com/scorm-vs-the-experience-api-xapi/ (xAPI) |
| OT/ICS training analogue | Domain analogue for simulator design | https://www.mitre.org/resources/caldera-ot, https://medium.com/@mitrecaldera (HVACSim, 2026-03) |
| Industry standard / regulation | Safety + compliance | SEMI S2/S8/S22, ANSI/RIA R15.06, IEC 60204-1, IEC 61508 (if relevant) |
| Process chemistry / reaction kinetics(若设备含化学反应) | Drive sensor ODE when 物理类含化学 | Polymer Innovation Blog(EMC cure); MDPI Polymers(Kamal-Sourour autocatalytic 系数); NIST publications(EMC kinetics); CAPLINQ blog(rheology + gelation)。**封装模塑机 v1 首次引入** — 设备含化学反应必加 |

**Cross-validation rule**: every technical claim that lands in the simulator (RPM rating, interlock list, error code) MUST cite ≥ 2 sources — typically (a) OEM PDF page #, (b) one external link. Sources collected here are recorded in `references/01-research-protocol.md` as a table during the build and surfaced in the simulator's About panel.

See `references/01-research-protocol.md` for the full research checklist + accept/reject heuristics for source quality.

**Gate 1 → 2**: ≥ 5 distinct authoritative sources catalogued. Each major technical assertion (state machine choice, audio approach, anti-flicker pattern, interlock list) has ≥ 2 independent sources.

### Stage 2 — OEM PDF deep extraction

PDF reading protocol (anchored to the DAD3350 388-page experience):

- **Batches of ≤ 20 pages** per `Read` call (PDFs > 10 pages require `pages` parameter).
- After each batch, **immediately distill to notes** (state machine states encountered, sensor names, interlock conditions, error codes, screen codes, timing values). Do NOT keep full PDF text in conversation memory.
- **Preserve chapter codes** (e.g., `[1.0]`, `[C-15]`, `B.2.3`) verbatim — they let users cross-reference the deliverable back to the OEM manual.
- **Quote DANGER / WARNING / CAUTION / NOTICE blocks verbatim** in the notes (these go into deliverables as-is, not paraphrased).
- **Don't extract figures as images** — describe them in words (top-bar layout, screen constituents) so they re-render as ASCII / SVG / HTML structure.

Maintain a running extraction table:

| Aspect | Source page | Notes / verbatim quote | Used in |
|---|---|---|---|
| Spindle max RPM | p.42 | "60,000 r/min (DAD3350: 30k-60k variable)" | Simulator SPDL sensor cfg |
| Interlock: air pressure | p.103 | ">= 0.4 MPa required before start" | Simulator INTERLOCKS[] |
| Error E0203 | p.298 | "Blade contact during approach. Recovery: ..." | Simulator error matrix |
| ... | ... | ... | ... |

See `references/06-pdf-extraction-protocol.md` for the structured extraction template.

**Gate 2 → 3**: Every chapter of the OEM manual has ≥ 1 entry in the extraction table. All planned state-machine states, interlocks, error codes, sensor configs traced back to specific page numbers.

### Stage 3 — Dual-artifact design

Design BOTH artifacts together to keep them coherent.

**Shared design tokens** (one source of truth):

```css
:root {
  --bg:      <subject-pigment-1>;   /* page surface */
  --paper:   <subject-pigment-2>;   /* card surface */
  --ink:     <subject-pigment-3>;   /* primary text */
  --accent:  <subject-pigment-4>;   /* DANGER / 章节强调 */
  --warn:    <subject-pigment-5>;   /* WARNING */
  --nav:     <subject-pigment-6>;   /* nav / titles */
  --rule:    <subject-pigment-7>;   /* dividers */
  --muted:   <subject-pigment-8>;   /* secondary text */
}
```

DAD3350 reference palette:
- `--bg #f5f3ee` 米白纸 / `--paper #fbf9f3` / `--ink #171513` 深炭墨 / `--accent #bd2828` 朱印红 / `--warn #d99700` / `--nav #0e2d4a` 技术海军蓝 / `--rule #cfc8b8` / `--muted #665e4e`

Font pairing (per subject, see `single-file-courseware` skill Step 3 for the matrix). Always include a `Latin emphasis italic` for OEM model names (Cormorant Garamond italic works near-universally).

**Manual artifact** (defers to `single-file-courseware`):
- 7-12 tabs mapping to OEM chapter structure
- 50+ question quiz weighted by chapter (safety 16% / operations 60% / maintenance 14% / errors 10%)
- localStorage prefix `<device>-`
- All chapter codes preserved

**Simulator artifact** (this skill's distinctive layer):
- ~20+ state FSM modelled on real HMI screen navigation (each screen ≈ state)
- 13+ interlock chain (power → e-stop → cover → utilities → consumables → calibration → workpiece → warm-up)
- 5+ phase machine cycle (rampup → approach → operate → retract → index)
- Web Audio engine (process hum + utility hiss + alarm beeps)
- ≥ 8 training scenarios covering: cold-start, full-auto, alignment, consumable change, multiple error recoveries, emergency stop drill
- ≥ 4 error codes with independent CLEAR interlocks
- localStorage prefix `<device>-sim-`

**Gate 3 → 4**: One design doc (in conversation, not necessarily a file) shows shared CSS variables, both artifact's tab/state inventory, localStorage namespace.

### Stage 4 — Build manual

Invoke / follow the `single-file-courseware` skill end-to-end with the design from Stage 3. Output to `<output-dir>\<DeviceModel>-操作完整手册.html` (or English equivalent — match the user's content language).

Apply all 12 cross-validation dimensions from `single-file-courseware` before claiming done.

**Gate 4 → 5**: `single-file-courseware` 12-dimension self-check passes. Manual file size is in the 150-350 KB range for a ~300-400 page OEM PDF.

### Stage 5 — Build industrial-grade simulator

The 8 mandatory layers (see `references/02-industrial-grade-criteria.md` for the rigorous criteria + smell tests):

1. **Finite state machine** — 20+ states reflecting real HMI screen navigation. One global `APP.currentState` + transition function. Library-free vanilla JS is fine; XState v5 only if scope justifies.

2. **Interlock chain** — array of named predicates evaluated in `preFlightStatus()`. Every "start cycle" gate enumerates them and produces structured pass/fail output (so MCP tests can query without DOM scraping).

3. **Sensor physics** — tick loop at 10 Hz minimum, each sensor follows `approach(value, target, rate * dt)` with subject-appropriate ramp rates. Add jitter ONLY when target > 0 or current value > threshold. Clamp negatives if device cannot read negative. **Idle sensors classify as `idle` (gray + `—`)**, not `bad`.

4. **Fault injection** — probabilistic events biased by consumable wear / operational stress. Each fault triggers a real error-code path (alarm sound + status-bar transition + clearing interlock). **Per-scenario `faultRate` 字段必填**(KS iConn v9.7 / 封装模塑机 sediment):正面教学 scenario(冷启动 / 装载 / 切线)默认 `faultRate=0` 完全 gate;量产监控类(连续生产 / SPC)按实机 SEMI 水平 `faultRate=0.2-0.5`(K&S iConn ~0.5%/wire,跑 100 wire 期望 0-1 NSOP);fault-recovery 教学的 `scenario.initial` 显式 `triggerError('Exxxx')`,不依赖随机;Free play(无 scenario)= 1 保留原密度。任意一类错配 = 教学闭环断裂。

5. **Web Audio engine** — Web Audio API only (no audio files). For rotating machinery: `OscillatorNode` (sawtooth ≈ process freq) modulated by spindle RPM. For fluid utilities: `AudioBufferSourceNode` of generated white noise → biquad high-pass. For alarm: short square-wave beep.

6. **Status bar** — persistent 1-line panel showing system mode (`OFFLINE`/`POST`/`IDLE`/`READY`/`RUNNING`/`PAUSED`/`ERROR`/`EMERGENCY`), active error code, runtime counter. Memoized updates only (no `textContent` writes when value unchanged).

7. **Error code matrix** — ≥ 4 codes from the OEM error guide, each with: trigger condition, alarm severity, blocking behavior, recovery sequence, independent CLEAR interlock check. **Every error MUST carry a `clearHint:` 字段**(KS iConn v9.7 sediment / L29) — 人话写明「按钮 X → 按钮 Y」恢复路径,在 status bar 永久显示 `{code} {name} · 处置:{clearHint}`。silent failure(CLEAR 按钮 enabled 但点了没反应,因 `clear` 谓词依赖的下层条件没满足)在工业 HMI 上是经典反模式 — SEMI / OEM 实机都有 alarm banner + recovery hint。三种实现任选(优先级降序):(a) clearHint 字段直接外露;(b) CLEAR 按钮 enable 谓词与「真能执行」对齐 `[...active].some(c => ERRORS[c].clear(APP))`;(c) `runCmd` 失败时 `showToast(reason)` 浮提示 3s。

8. **Training scenarios** — ≥ 8 scripted scenarios that walk the user through canonical operations + drills. Each scenario has: precondition, goal, success criteria (queried from APP state), completion logging to localStorage.

9. **(条件)Vision Workview HMI** — devices with a camera-based primary operator surface(wire bonder / die bonder / prober / dicing align / stepper / optical metrology)MUST add this layer. See full design template in `references/07-vision-workview-design.md`. 8 elements:permanent dark canvas + HUD 4 corners + phase chip + physical anchor layer + dynamic moving elements + scale ruler + scanline + cycle trail accumulation. Critical: frame-iterating animations(Z 平滑、scrub wiggle、spark fade)called **unconditionally every frame**(J06,not inside dirty gates),all SVG `setAttribute` writes through `_tf`/`_op`/`_d` memo guards. For wafer-class devices,dual-anchor pattern(main view + mini wafer map)with `R_max > R_use + pitch/2` geometry constraint(J07). Card-type/recipe-type dynamic build hooked from ALL 5+ entry points(POWER / CARD_x / CHANGE / CLEAN / DOMContentLoaded). Closed-chamber / hidden-process devices(模塑机 / CMP / furnace)omit this layer but **document the omission** in delivery report. **Each step MUST have explicit `check:` + `act:` 双轨**(L10),act 用于教练代操作 / headless test。**`scenario.initial` 推到的 APP 状态不能恰好满足 step 1 check**(L28) — 第一步是教学第一句话,initial 满足 step 1 = 跳步 bug。**最终 step act 必须能从 dirty state 恢复**(L28 + L29):RUNNING 期 fault 注入后,act 至少做三件事 — (i) 把目标计数 / 标志推到 check 要求的目标值,(ii) `activeErrors.clear()` + 把 mode 从 FAULT/PAUSED/MAINT 拉回正路,(iii) 把 clear 谓词依赖的下层状态也铺好(`capLife=Math.min(capLife,5000)` + `capInstalled=true`)。**check 用工业实际阈值**:NSOP rate ≤ 1%(SEMI 合规) / NSOP rate ≤ 0.5%(高端 OSAT)— 不写「= 0」的绝对阈值。**按钮分组按功能本质,不按出现顺序**(L26) — 至少分:配置 mode / SETUP 子流程 / 调参 TUNE / MAINT 故障处置 四类;调参类按钮带实时状态 dot(绿在工艺窗 / 琥珀偏离 / 灰未开),memoized 写 style 不闪烁。**E-STOP 物理切断范围严格按 SEMI S2 + OEM procedure**(L27) — 切断:运动 + 键合电气 + 易燃 / 有毒工艺气(H2 / SiH4 / Cl2);保留:facility 气(AIR / N2)、heater(防热冲击)、wire / film tension。不要一刀切 `resetTargets(true)` 横扫所有 sensor。

Output to `<output-dir>\<DeviceModel>-仿真训练器.html`. Target size 100-200 KB(vision workview adds 15-20 KB SVG markup — KS iConn shipped at 100 KB,探针台 v1.1 at 119 KB).

Apply the 18-dim simulator self-check (see Stage 7 below).

**Gate 5 → 6**: All 8 mandatory layers present in code(+ Layer 9 if device has camera HMI). Static grep proves each: `INTERLOCKS = [`, `cutPhase` / `phase` state machine, `audioCtx`, `errorHistory` / similar, ≥ 8 scenario entries with `faultRate:` field, every error has `clearHint:` field, `ensureReady` explicitly resets every transient flag(J05), vision workview animation function called unconditionally(grep `updateWorkview\(\);` inside `render()` body but OUTSIDE any `if (dirty.has` block — J06).

### Stage 6 — MCP automated QA

Run **all 4 mandatory** MCP test patterns(+ 2 conditional)against the simulator. See `references/04-mcp-test-templates.md` for full scripts. **Every session opens with `localStorage.clear()` + hard reload + http://127.0.0.1:18080 server**(L31).

1. **Physics validation**(multi-time-point sampling)— trigger a representative scenario, sample `APP.sensors` and `APP.running.phase` at t = 500ms / 2s / 5s / 18s. Verify state machine advances on the expected schedule; verify sensors converge to physically plausible values.

2. **Interlock coverage**(state queries + single-kill isolation)— call `preFlightStatus()` and verify exact count + pass/fail map. Run **15 single-kill isolated** tests:each kill should trigger **exactly one** failed interlock. Any kill triggering 2+ fails = J05 bug,`ensureReady` leaks transient state — fix per Pattern 8.

3. **Flicker objectivity**(MutationObserver)— attach observer to each high-update region(sensor panel, status bar, scenario list, aux bar, **+ workview if Layer 9 included**). 1.5-second sample with no value changes must yield **0 childList mutations**. Trail accumulation regions(wire trail / scrub marks)allowed child+ during cycles — those are intentional accumulation,not flicker.

4. **Scenario walkthrough**(J03)— in one `evaluate_script`, run `for sc of SCENARIOS: startScenario(sc.id); coachAct loop until step >= total`. All scenarios reach final step with `errors === []` at completion. Stuck count must be 0.

**Conditional patterns**(when Layer 9 included):
5. **Frame-iterating animation convergence**(J06)— pause mode, set each phase Z target, wait 1.5s, read SVG `transform`,verify `|observed - target| < 0.5` for all phases. A stalled value = updateWorkview is inside a dirty gate.
6. **Theme toggle workview stability** — toggle data-theme,workview background `getComputedStyle` unchanged.

Test results MUST be captured. Persist in `<output-dir>\_qa_screenshots\` named `<device>-sim-v<N>-<NN>-<description>.png` + one trace file `<device>-sim-v<N>-mcp-qa-trace.txt` listing all assertion results. Final QA report cites the screenshots and trace path.

**Gate 6 → 7**: All 4 mandatory patterns pass(+ 5/6 if Layer 9)with documented evidence. Any failure = NOT done — return to Stage 5.

### Stage 7 — Delivery & archive

Final report (concise, in conversation, surface to user):

| Metric | Value |
|---|---|
| Manual file | path / size / line count / tab count / quiz count |
| Simulator file | path / size / state count / interlock count / scenario count |
| OEM sources | PDF path + page count + key extracted pages |
| External sources | ≥ 5 verified URLs |
| 12-dim manual check | pass / pass / ... (per dimension) |
| 18-dim simulator check | pass / pass / ... (per dimension) |
| MCP physics test | spindle ramp time / phase progression timing |
| MCP interlock test | N interlocks defined, M demanded for start |
| MCP flicker test | 0 DOM writes / 1.5s on each tracked region |
| Safety disclaimer | "Educational unofficial replica — not affiliated with <OEM>" placement verified |

The simulator's About panel must contain:
1. Disclaimer (verbatim, see Rule 4).
2. OEM PDF reference (model + version + page count).
3. External sources list (verified during Stage 1, all 5+ links).
4. Build date and skill version.

Optional: add a memory entry pointing to the two deliverable paths + aesthetic conventions + localStorage prefix family.

---

## 18 + 5-dimension simulator self-check

(12 from `single-file-courseware` apply; 6 are simulator-mandatory; 5 are sediment-driven additions from探针台 v1.0/v1.1 + KS iConn v9.7. Run all 23 before declaring done.)

| # | Dim | Check | Verification |
|---|---|---|---|
| 1-12 | Inherited from `single-file-courseware` |(transport/encoding/offline/first-paint/tabs/persistence/quiz/print/mobile/a11y/console/size)| as-spec |
| 13 | State machine completeness | `Object.keys(STATES).length >= 20` | MCP `evaluate_script` |
| 14 | Interlock chain | `INTERLOCKS.length >= 13` and each has `.check()` that returns boolean | MCP |
| 15 | Sensor physics realism | Multi-time-point sampling: ramp from 0 → target in OEM-documented time; sensors converge | MCP Pattern 1 |
| 16 | Fault injection live | After scenario-appropriate duration: fault rate matches `faultRate` field; positive scenarios = 0 faults; production scenarios = avg 0.5-1.0/run | MCP wall-clock + 30-run Monte Carlo |
| 17 | Audio non-error | Web Audio context created on POWER click(not page load);`audioCtx.state === 'running'` after user gesture | MCP Pattern 4 |
| 18 | Anti-flicker objective | MutationObserver shows 0 childList writes on `#sensorPanel`, `#statusBar`, `#scenarioList`, `#fkeyRow`,`+ workview if Layer 9` during 1.5s idle | MCP Pattern 3 |
| 19 | **clearHint coverage**(L29)| Every entry in `ERRORS` has a non-empty `clearHint:` string;status bar renders it on alarm |grep + MCP |
| 20 | **faultRate per-scenario**(L30)| Every entry in `SCENARIOS` declares `faultRate:` field;0 for positive flow, 0.2-0.5 for production monitoring | grep + Monte Carlo distribution check |
| 21 | **ensureReady completeness**(J05)| 15 single-kill isolated tests all return exactly one fail;no cross-contamination | MCP Pattern 8 |
| 22 | **Scenario walkthrough end-to-end**(J03)| All N scenarios reach final step via `coachAct` loop;0 stuck;0 errors at completion | MCP Pattern 6 |
| 23 | **Vision Workview animation convergence**(J06,Layer 9 only)| Each phase Z target converges within 1.5s under exponential smoothing;`|observed - target| < 0.5` | MCP Pattern 7 |

Failing any of dims 13-23 = simulator is "skeleton", not "industrial-grade". Either fix or honestly relabel. **Dims 19-22 are mandatory for every device; dim 23 only if Layer 9 included**(skip-document for closed-chamber / no-camera devices).

---

## Anti-patterns (do not do these)

| Anti-pattern | Why fails |
|---|---|
| Fabricating a parameter not in OEM PDF | Anchors the simulation in fiction — user is here to learn the real machine |
| Skipping cross-validation because "I know this" | Memory degrades / facts change / 2026 ≠ training cutoff |
| Re-using DAD3350 palette on a wire bonder | Cross-subject visual carryover dilutes both deliverables — repigment for each subject |
| Mocking sensor values with `Math.random() * 100` per tick | Not physics — sensors must `approach()` a target with subject-appropriate ramp |
| Adding jitter when target = 0 | Causes false-red alarms on sensors that are correctly idle |
| 10 Hz `innerHTML` rebuild of sensor panel | Causes visible flicker that DAD3350 v1 had — fixed in v2 with memoized surgical updates |
| Letting `tickSensors` re-render error screens | Triggers GPU repaint on neighboring regions (DAD3350 v1 scenarios 6/7/8 flicker bug) |
| Audio files instead of Web Audio synthesis | Breaks single-file contract |
| Putting OEM brand mark on PUBLIC artifact | Legal risk — distribute privately only |
| "Industrial-grade" label without 8 layers | Mis-sells the deliverable |
| Validating only by visual inspection | Subjective — must use MCP patterns for objectivity |
| Grouping buttons by "this row has space" instead of task essence (L26) | KS iConn v6: H2 调参塞进 MAINT 故障处置组 → 用户找不到。配置 / SETUP / 调参 / MAINT 必须独立分组 |
| `resetTargets(true)` one-shot on `transitionTo('EMSTOP')` (L27) | Wipes AIR/N2/HEATER targets that SEMI S2 says must stay live → RESUME 死锁 + thermal shock 隐患 |
| `scenario.initial` 推到的 APP 状态恰好满足 step 1 check (L28) | tickScenario 第一帧立刻把 step 1 标 ✓,用户没看到教学第一句就跳到 step 2 |
| Final step act 只覆盖主线没考虑 RUNNING 期 fault 注入 (L28) | wireCount=100 但 nsopCount=1+fault=active,check `===0` 永真 false,coachAct 也救不回 |
| check 用绝对阈值 `=== 0` / `>= 100%`(L28) | 实机 NSOP rate 永远 > 0(SEMI ≤1% 合规),绝对阈值 = 教学目标背离工业事实 |
| Silent failure:CLEAR 按钮 enable 但 `runCmd` 静默 return (L29) | 互锁谓词依赖的下层条件没满足时用户看不到为什么按了没用 — 必须 clearHint 外露 |
| Error 定义只有 `clear:` 谓词没有 `clearHint:` 文案 (L29) | status bar 不显示恢复路径,用户得回 manual 查 |
| Scenario 期 fault injection 全开 OR 全 gate (L30) | 全开 = 频繁打断流程教学;全 gate = 量产 SPC 教学指标永远 0 失去意义。必须 per-scenario faultRate |
| Frame-iterating animation 放在 `if (dirty.has('phase'))` 块内(J06)| Z 平滑 / scrub wiggle / spark fade 每帧基于上一帧迭代,dirty 不变就跳过 → `_zDisp` 卡在中途。必须 `updateWorkview()` 提到 if 块外 every-frame 调用,内部 `_tf`/`_op` memo guard |
| 圆 wafer mini map R_max ≤ R_use + pitch/2(J07)| 没有 die 落在 edge ring,SEMI M1 边缘排除区视觉缺失。200mm + 7mm pitch 正确值 R_max=98.5 / R_use=94 → 52 edge die |
| `ensureReady` 只 reset 「READY 看起来对」的子集(J05)| `tdCounter`、`nsopCount`、`activeErrors`、`fritted` 漏掉 → 下一个 single-kill 测试 spurious cross-contamination → 15 个 kill 里 5 个被污染 |
| Vision workview 背景用 `var(--bg)`(Layer 9)| 切到 light theme 时 CCD 摄像头变白底 — 物理上不可能。workview 背景必须硬编码 `#080c14` |
| Card-type 动态 build 只 hook 一处入口 | POWER / CARD_x / CHANGE / CLEAN / DOMContentLoaded 5+ 个入口都要 hook,否则做完该操作画面里幻影针 |
| MCP 测试不先 `localStorage.clear()`(L31)| 上次 session 的 `<device>-sim-active-scen` 残留 → 这次 page load 进 LOAD / RUNNING 而不是 OFFLINE → 物理验证起点错乱 |
| MCP server 绑 8765 / 8080 / 9000 端口(L31)| Windows 动态 TCP exclusion 概率命中 → bind 失败。永远用高 5 位 18080 / 23800 |

---

## Files in this skill

- `SKILL.md` — this file (workflow)
- `references/01-research-protocol.md` — research source classes + cross-validation rules + accept/reject heuristics
- `references/02-industrial-grade-criteria.md` — 8 mandatory simulator layers in depth + smell tests + L26-L30 design rules folded in
- `references/03-anti-flicker-patterns.md` — memoization + surgical update patterns + J06 dirty-gated vs every-frame rule + SVG attribute memo pattern
- `references/04-mcp-test-templates.md` — 9 reusable MCP test patterns(physics / interlock / flicker / scenario walk / audio / completion / frame-iter / ensureReady / theme stability)+ L31 mandatory session header
- `references/05-safety-copyright.md` — OEM IP / fair-use / safety language policy
- `references/06-pdf-extraction-protocol.md` — structured PDF reading + extraction table template
- `references/07-vision-workview-design.md` — **conditional Layer 9**:8-element vision-camera HMI design + dual-anchor wafer mini-map + card-type dynamic build hook pattern + J07 geometry constraint
- `README.md` — install / orient for future contributors

---

## Reference deliverables (canonical implementations)

### DAD3350 — DISCO dicing saw (PDF-anchored)
- `E:\claude_ask\bilibili_learn\DAD3350-划片机操作完整手册.html` (225 KB, 12 tabs, 50 quiz) · 米白朱印 + Noto Serif JP
- `E:\claude_ask\bilibili_learn\DAD3350-划片机仿真训练器.html` (126 KB, 21 states, 13 interlocks, 8 scenarios, 4 error codes)
- Inputs: `D:\Downloads\Dicing_Saw_Manual.pdf` (388 pages, DAD3221/3231/3350 v1.5)

### AD8312PLUS — ASMPT die bonder (brochure-anchored, K&S 4526 as architecture-only ref)
- `E:\claude_ask\bilibili_learn\AD8312PLUS-贴片机操作完整手册.html` (113 KB, 11 tabs, 48 quiz) · 洁净厂房 + IBM Plex
- `E:\claude_ask\bilibili_learn\AD8312PLUS-贴片机仿真训练器.html` (66 KB, 22 states, 12 phases, 15 interlocks, 14 sensors, 11 error codes, 10 scenarios, Web Audio, 6 fault injections)
- Inputs: ASMPT product pages + SMT Today / Adsale / iConnect007 (2025-05 INFINITE coverage) + K&S 4526 UNLV manual (ARCHITECTURE-REFERENCE only)

### KS iConn ProCu Plus — K&S wire bonder (multi-source brochure + ELA datasheet anchored)
- `E:\claude_ask\bilibili_learn\KS-iConn-Wire-Bonder-操作完整手册.html` · SI 黑 + 等离子青 + Bricolage Grotesque,11 tab + quiz
- `E:\claude_ask\bilibili_learn\KS-iConn-Wire-Bonder-仿真训练器.html` · vision-camera HMI workview SVG + per-scenario faultRate(L30 prototype)+ clearHint exposure(L29 prototype)+ E-STOP SEMI S2 范围(L27 prototype)
- Inputs: K&S iConn ProCu Plus brochure + ELA wire datasheet + Inseto / NTU best practices + SEMI S2/S8/S22
- **L26-L30 五条 lesson 在此首次系统沉淀,所有后续设备的 baseline**

### 封装模塑机 — Towa Y1R + ASMPT 3Ge transfer/compression molding (multi-source aggregated, 化学动力学首次引入)
- `E:\claude_ask\bilibili_learn\封装模塑机-操作完整手册.html` (95 KB, 11 tab + 50 quiz) · 树脂琥珀 + Fraunces + Manrope + Geist Mono
- `E:\claude_ask\bilibili_learn\封装模塑机-仿真训练器.html` (78 KB, 16 states × 8 phase, 13 interlocks, 10 sensors, 9 errors, 10 scenarios, **化学反应 sensor `alpha` 走 Kamal-Sourour 积分**)
- Inputs: Towa Y1R / YPM / FFT / CPM / Y1E 系列页 + ASMPT 3Ge brochure + Besi Fico AMS-i / FML / AMS-LM + Polymer Innovation Blog Part 2 + CAPLINQ + MDPI Polymers 13/11/1734 + NIST 936408 + SEMI S2/S22
- **首次引入「化学反应物理」一类**(前三台均为纯机械/热学),验证 8-layer 骨架可承载化学动力学 sensor。**L26-L30 框架零纠正迁移成功**

### 探针台 — Accretech UF3000 + FormFactor CM300xi/SUMMIT200(双 OEM aggregated + elec-mech 接触 + 微电流物理 + 双 anchor CCD HMI)
- `E:\claude_ask\bilibili_learn\探针台-操作完整手册.html`(78 KB, 11 tab + 50 quiz)· Probe Card Precision · graphite + probe gold + ESD blue + plasma 青 · Space Grotesk + Atkinson Hyperlegible + JetBrains Mono + EB Garamond italic
- `E:\claude_ask\bilibili_learn\探针台-仿真训练器.html` v1.0 = 103 KB / v1.1 = **119 KB**(21 FSM × 7 phase, 16 interlocks, 14 sensors, 10 errors with clearHint, 10 scenarios with per-scenario faultRate, **+ Layer 9 dual-anchor vision workview**:CCD probe view + 200mm wafer mini map 621 dies / 52 edge + card-type dynamic pad-needle build canti 8 / vert 16 / mems 32 + Z 0.30 exponential smoothing + P3 lateral scrub + P4 spark glow + P6 motion blur + scrub mark cap padCount×26 + pad wear)
- Inputs: Accretech UF3000 / UF3000EX / UF200R + FormFactor CM300xi / SUMMIT200 / Velox 3.4.5 + SWTW(Broz 1998/2007、Vettori 2016、Folk 2008) + Keithley Low Level Measurements Handbook + SEMI E91 PSEM / E5/E30/E37/S2 §10/§11/S8/S22 + IEC 61340-5-1 ESD
- **物理类**:首次引入 **接触力学**(Holm constriction `R_c = ρ/(2a)` + Tabor 塑性 + Al₂O₃ fritting + 高温 a-spot 抬底)+ **Archard 磨损** + **Shockley dark current**(reverse leakage `2^((T-25)/10)` 翻倍 + triax+guard 10fA / BNC 100pA)
- **L26-L30 baseline 零翻车迁移**;v1.1 **首次引入 vision workview Layer 9 dual-anchor pattern**,沉淀 **J05 / J06 / J07** 三条 judgment-call

The five prior projects span the data-availability spectrum + physics-class spectrum:
- **PDF-anchored**(DAD3350):single authoritative OEM PDF, value-rich extraction, deep extraction table possible
- **Brochure-anchored**(AD8312PLUS, KS iConn):no public OEM manual; subject values aggregated from multiple secondary sources, machine architecture borrowed from family-adjacent manual with explicit ARCH-REFERENCE-ONLY labelling
- **Multi-OEM aggregated + chemistry-coupled**(封装模塑机):双 anchor 对比 + 化学动力学 ODE 加入 sensor 层
- **Multi-OEM aggregated + elec-mech contact + low-current**(探针台):无单一权威 PDF,Accretech + FormFactor 双锚定,首次落地 vision workview Layer 9 dual-anchor + 接触力学 + dark current

Compare every future deliverable against the matching anchor-mode + physics-class reference before declaring done.

---

## What this skill does NOT cover

- Authoring the OEM-equivalent reference material from scratch (skill assumes an OEM PDF or equivalent vendor doc exists)
- Real-device control (this is education-only simulation, not a runtime HMI replacement)
- Multi-user collaborative training (single-operator localStorage only)
- LMS / xAPI integration (mentioned as a 2026 standard; not implemented — see `references/01-research-protocol.md` for path forward)
- 3D wafer visualisation / wafer-map editing (Three.js scope; DAD3350 deliverable used 2D SVG)

---

## When to update this skill

After every project of this kind, update:
- `references/01-research-protocol.md` — new authoritative source URLs discovered
- `references/02-industrial-grade-criteria.md` — new "layer" if 8 turns out insufficient for a subject
- `references/04-mcp-test-templates.md` — new test patterns proven on a project
- The reference-deliverable list at the bottom of this file
