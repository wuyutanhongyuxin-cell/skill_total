# Reference 02 — Industrial-Grade: The 8 Mandatory Layers

"Industrial-grade" is a claim, and a claim earns the label only when ALL 8 layers are present. Anything less is a "教学演示 demo", and should be labelled as such honestly.

These 8 layers were defined during the DAD3350 v1 → v2 upgrade after the user feedback: 「我要尽可能模拟的，工业级」 — i.e., v1 (a skeleton with screens but no physics) failed the bar; v2 (with all 8 layers) passed.

---

## Layer 1 — Finite state machine

**What**: a global `APP.currentState` that takes values from a fixed set of named states modeling the real HMI screen navigation + system mode (OFFLINE / POST / IDLE / WARMING / READY / RUNNING / PAUSED / ERROR / EMERGENCY).

**Why**: real HMIs are FSMs. You cannot operate a dicing saw "halfway" — you are in screen 1.0, or 1.1, or alarm 0203. Modeling this explicitly makes operator training valid.

**Minimum**: ≥ 20 states for a complex tool (DAD3350 had 21). ≥ 10 states for a simpler instrument.

**Implementation**:
- Vanilla JS object literal `STATES = { '1.0': { ... }, '1.1': { ... } }`
- Each state declares allowed transitions (which F-keys / which screen buttons map to which next state)
- Transition function checks current state, blocks illegal transitions, fires `onExit` / `onEnter` hooks
- XState v5 is acceptable if scope justifies (>50 states, parallel statecharts) — but adds CDN dependency
- **`transitionTo` MUST enumerate side effects per target state**(L20)— mode change is one thing, sensor `target` updates are another, audio start/stop is a third. Forgetting any one means an interlock will stay false forever. Template:
  ```js
  function transitionTo(newState) {
    if (!STATES[APP.currentState].allow.includes(newState)) return;
    STATES[APP.currentState].onExit?.(APP);
    APP.currentState = newState;
    STATES[newState].onEnter?.(APP);
    // Each onEnter explicitly handles:
    //   1. mode = correct value
    //   2. sensor targets that should ramp(WARMUP enters → HEATER.target = 1.5)
    //   3. audio side effects(initAudio / startProcessHum / playAlarm)
    //   4. flag side effects(activeErrors.clear() ? estop=false ?)
  }
  ```
- **E-STOP `onEnter` hook follows SEMI S2 scope, NOT blanket `resetTargets(true)`**(L27 — see Layer 8.5). Enumerate which sensors / power buses / valves to cut and which to preserve.

**Smell test**: try to enter the START operation from a state where the device should not allow it (e.g., from POST during boot). Simulator must block it cleanly with an audible/visual alarm.

---

## Layer 2 — Interlock chain

**What**: an ordered list of named predicates evaluated before any "go" command (start cycle, start warm-up, start auto-align). Each predicate must pass independently for the gate to open.

**Why**: real machine safety is "all conditions met or no go" — partial readiness is dangerous. Operators must learn to read interlock status before pressing START.

**Minimum**: ≥ 13 interlocks for a typical wafer-processing tool. Always enumerate explicitly — never let "start" execute side-effectfully from a single boolean.

**Implementation**:
```js
const INTERLOCKS = [
  { id: 'power',     label: '主电源 ON',         check: () => APP.powered,                       err: '设备未通电' },
  { id: 'estop',     label: '急停未启用',         check: () => !APP.context.eStopEngaged,         err: '急停按下' },
  { id: 'cover',     label: '安全盖关闭',         check: () => APP.context.coverClosed,           err: '安全盖未关闭' },
  { id: 'air',       label: '气压 ≥ 0.4 MPa',     check: () => APP.context.airValve && APP.sensors.PRES >= 0.4, err: '气压不足' },
  { id: 'water',     label: '冷却水正常',         check: () => APP.context.waterValve,            err: '冷却水阀未开' },
  { id: 'blade',     label: '刀片信息已设',       check: () => APP.context.bladeId !== null,      err: '刀片未设置' },
  { id: 'wear',      label: '刀片磨损未超限',     check: () => APP.context.bladeWear < 0.85,      err: '刀片磨损超限,需更换' },
  { id: 'setup',     label: 'Blade Setup OK',     check: () => APP.context.setupDone,             err: '需完成 Setup' },
  { id: 'ncs',       label: 'NCS 已校准',         check: () => APP.context.ncsCalibrated,         err: 'NCS 未校准' },
  { id: 'bbd',       label: 'BBD 已校准',         check: () => APP.context.bbdCalibrated,         err: 'BBD 未校准' },
  { id: 'workpiece', label: '工件已装载',         check: () => APP.context.workpieceLoaded,       err: '工件未装载' },
  { id: 'vacuum',    label: '真空吸附正常',       check: () => APP.context.chuckVacuum,           err: '吸附未稳' },
  { id: 'warmup',    label: '暖机完成',           check: () => APP.context.warmUpProgress >= 1,   err: '暖机未完成' },
];

function preFlightStatus() { return INTERLOCKS.map(l => ({ ...l, ok: l.check() })); }
```

The named structure lets MCP query the state directly:

```js
evaluate_script: () => {
  const status = preFlightStatus();
  return status.filter(s => !s.ok).map(s => s.id);
}
```

**Smell test**: kill ONE interlock at a time (e.g., set `coverClosed = false`), attempt START. The matching error message must surface, no others.

---

## Layer 3 — Sensor physics

**What**: sensor values evolve over time toward targets using `approach(currentValue, target, ramp * dt)`. Each sensor has subject-appropriate ramp rate, jitter envelope, and idle classification.

**Why**: real sensors don't snap to values — they ramp. Operators learn timing by watching the ramp. A simulator with instant-snap sensors trains the wrong intuition.

**Minimum**: ≥ 6 sensors (pressure, flow, RPM, position, temperature, vacuum) for a wafer tool. Each has documented ramp rate from OEM manual.

**Implementation**:
```js
function approach(v, target, ramp) {
  const d = target - v;
  if (Math.abs(d) <= ramp) return target;
  return v + Math.sign(d) * ramp;
}

function tickSensors(dt) {
  const s = APP.sensors;
  // Air pressure
  const airTarget = APP.context.airValve ? 0.5 : 0;
  s.PRES = approach(s.PRES, airTarget, 0.15 * dt);
  if (airTarget > 0) s.PRES += jitter(0.005);  // jitter ONLY when demanded

  // Spindle — air spindle ramps slower at high RPM
  const ramp = (s.SPDL < 40000 ? 1800 : 1200) * dt;
  s.SPDL = approach(s.SPDL, s.SPDL_TARGET, ramp);
  if (APP.running.cutPhase === 'cut') {
    s.SPDL_LOAD = approach(s.SPDL_LOAD, 35 + Math.random() * 8, 4);
    s.SPDL -= s.SPDL_LOAD * 0.5;  // modest drag — air spindle characteristic
  }
  // ... more sensors
}

function jitter(amplitude) { return (Math.random() - 0.5) * 2 * amplitude; }
```

**Anti-rule** (DAD3350 v1 bug): never apply jitter when target = 0. Causes sensor to oscillate around 0 → negative → classified as `bad` → false red alarm. Either guard with `target > 0` or classify the sensor as `idle` (gray + `—`).

**Smell test**: leave the simulator at POWER OFF for 10 seconds. All sensors should classify as `idle`, not `bad`. After power-on and air-valve open, sensors must take 2-5 seconds (subject-appropriate) to reach normal range — not snap.

---

## Layer 4 — Fault injection

**What**: probabilistic events fired during operation that trigger real error-code paths. Probabilities biased by consumable wear, operational stress, or scenario-specific scripts. **Per-scenario `faultRate` gate is mandatory**(L30 sediment — KS iConn v9.7).

**Why**: operators learn error recovery only by encountering errors. A simulator that never fails is a screen-saver. But a simulator that fails too often during teaching-positive scenarios(cold-start、loading)becomes unusable noise — and one that never fails during production-monitoring scenarios kills the SPC教学 purpose. Both extremes are bugs.

**Minimum**: ≥ 4 distinct error codes from OEM error guide. ≥ 1 random fault every 5 minutes of high-stress operation (worn blade, harsh feed rate). Plus scripted faults for training scenarios.

### Per-scenario faultRate(L30)

Three教学 modes, three faultRate strategies:

| Scenario type | Example | faultRate | Why |
|---|---|---|---|
| Positive flow(cold-start / load / parameter setup)| S01 boot / S02 wafer load | `0` 完全 gate | Fault is noise here — interrupts the teaching narrative |
| Production monitoring | S10 「100 wire continuous production」 | `0.2-0.5` 按实机 SEMI 水平 | SPC的教学价值就是「NSOP rate 偶发但 in-control」— rate=0 抹杀这一点 |
| Fault recovery teaching | S05 「E0203 recovery」 | scenario.initial **显式** `triggerError('E0203')`,faultRate 不参与 | Recovery teaching needs 100% reproducible fault, not stochastic |
| Free play(无 scenario)| — | `1`(base rate)| Industrial-feel density |

Implementation:
```js
function tickFaults(dt) {
  let gate = 1;
  if (APP.activeScenario) {
    const scen = CFG.SCENARIOS.find(s => s.id === APP.activeScenario);
    gate = scen?.faultRate ?? 0;  // 默认 0 — positive scenarios safe by default
  }
  if (gate === 0) return;
  const baseRate = 0.005 * gate;
  // ...
}
```

faultRate calibration via Monte Carlo:run 30 × scenario_duration → check distribution。Sweet spot ≈ 0.5-1 fault average / run with < 10% of runs hitting ≥ 3 faults。

**Implementation**:
```js
function tickFaults(dt) {
  if (APP.running.cutPhase !== 'cut') return;
  const wear = APP.context.bladeWear;
  const baseRate = 0.005;  // 0.5%/s base
  const rate = baseRate * (1 + wear * 3) * dt;
  if (Math.random() < rate) {
    triggerError('E0203');  // blade contact / vibration
  }
  // ...
}

function triggerError(code) {
  APP.error = code;
  APP.systemMode = 'ERROR';
  APP.alarmCount++;
  APP.errorHistory.push({ code, ts: Date.now(), state: APP.currentState });
  playAlarmBeep();
  navigateToErrorScreen(code);
}
```

Errors must NOT be cleared by just pressing CLEAR. Each error has its own clearing interlock:

```js
const ERROR_CLEAR = {
  'E0203': () => APP.context.bladeWear < 0.6 && APP.context.coverClosed,
  'E0301': () => APP.context.coverClosed,
  'E0401': () => APP.context.chuckVacuum,
  'E0501': () => !APP.context.eStopEngaged,
};
```

**Smell test**: trigger E0203, press CLEAR — should remain in error if wear ≥ 0.6. Operator must change the blade (a separate scenario) before CLEAR works.

---

## Layer 5 — Web Audio engine

**What**: real-time synthesized audio from Web Audio API. Three kinds:
- Process hum (rotating machinery): `OscillatorNode` sawtooth at `f(RPM)`
- Utility hiss (fluid flow): white-noise `AudioBufferSourceNode` → `BiquadFilterNode` (high-pass)
- Alarm: short `OscillatorNode` square wave

**Why**: a quiet simulator misses 30% of operator situational awareness. Real operators hear the spindle, hear the air valve open, hear the alarm before seeing it.

**Implementation skeleton**:
```js
let audioCtx, spindleOsc, spindleGain, waterNoise, waterGain;
function initAudio() {
  audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  spindleOsc = audioCtx.createOscillator();
  spindleOsc.type = 'sawtooth';
  spindleGain = audioCtx.createGain();
  spindleGain.gain.value = 0;
  spindleOsc.connect(spindleGain).connect(audioCtx.destination);
  spindleOsc.start();
  // ... water noise via createBuffer
}
function updateAudio() {
  const rpm = APP.sensors.SPDL;
  const freq = Math.max(20, rpm / 60 * 4 + 30);
  spindleOsc.frequency.setTargetAtTime(freq, audioCtx.currentTime, 0.05);
  spindleGain.gain.setTargetAtTime(rpm > 100 ? 0.04 : 0, audioCtx.currentTime, 0.1);
  // ... water gain by water flow
}
```

**Smell test**: spin up the spindle from idle → 60k rpm; audio pitch rises smoothly. Open the cooling-water valve; hiss begins after the flow ramps up.

**Note**: Web Audio requires user gesture before `audioCtx.resume()`. Tie `initAudio()` to first POWER ON click, NOT page load — `new AudioContext()` from `DOMContentLoaded` creates a `suspended` context that never produces sound. Browsers also block `audioCtx.resume()` if called outside a user-gesture stack; the POWER button click is the canonical entry point. MCP audio sanity test must include a `click` on `#powerBtn` before checking `audioCtx.state === 'running'`.

---

## Layer 6 — Status bar

**What**: a persistent 1-line panel always visible showing: system mode, active error code, runtime counter, alarm count.

**Why**: real HMIs have this — operators glance for situational awareness without leaving the current screen.

**Anti-rule**: status bar updates 10 Hz from tick loop. MUST use memoized updates (compare to last value, only `textContent =` when changed) — otherwise becomes a flicker source.

**Implementation**:
```js
const _sbMemo = {};
function setSbVal(key, value) {
  if (_sbMemo[key] === value) return;
  _sbMemo[key] = value;
  document.getElementById('sb-' + key).textContent = value;
}
function renderStatusBar() {
  setSbVal('mode', APP.systemMode);
  setSbVal('error', APP.error || '—');
  setSbVal('runtime', formatRuntime(APP.runtime));
  setSbVal('alarms', String(APP.alarmCount));
}
```

---

## Layer 7 — Error code matrix

**What**: ≥ 4 OEM-documented error codes implemented with: trigger condition, severity (blocking / non-blocking / critical), display sequence (screen navigation + audio cue), recovery sequence, independent CLEAR interlock, **+ `clearHint:` 人话恢复路径字段(L29 mandatory)**.

**Why**: error recovery is half of operator training. Without real codes + real recovery paths, simulator misses the most stressful part of the job. **Silent failure**(CLEAR button enabled but click is a no-op because the underlying `clear` predicate is unmet)is the classic anti-pattern in industrial HMI — SEMI / OEM real machines all show an alarm banner with recovery hint. Forgetting this layer in the simulator = operator unable to learn recovery.

**Implementation**: see Layer 4 + the error map. Each error MUST carry a `clearHint:` field rendered into the status bar so the operator sees what to do next:

```js
const ERRORS = {
  'E2001': {
    name: 'Capillary EOL',
    clear: A => A.capLife < 10000 && A.capInstalled,
    clearHint: '更换 capillary → 按 [CHANGE CAP] → [清除告警]',
    sev: 'block',
  },
  'E0203': {
    name: 'Blade contact',
    clear: A => A.bladeWear < 0.6 && A.coverClosed,
    clearHint: '更换刀片(磨损 <60%)→ 关安全盖 → [清除告警]',
    sev: 'block',
  },
  // ...
};

// Status bar permanently shows: `{code} {name} · 处置: {clearHint}`
function renderAlarm() {
  const code = [...APP.activeErrors][0];
  if (!code) { setSbVal('alarm', '—'); return; }
  const e = ERRORS[code];
  setSbVal('alarm', `${code} ${e.name} · 处置: ${e.clearHint}`);
}
```

Three strategies for preventing silent failure(priority descending):

1. **`clearHint:` 字段外露**(recommended)— hint always visible in status bar regardless of cmdEnabled state
2. **`cmdEnabled('CLEAR')` aligned with reality**:`[...activeErrors].some(c => ERRORS[c].clear(APP))` — disabled state明示「点了也没用」
3. **`runCmd` 失败时 `showToast(reason)`** — 临时浮提示 3s

Plus an error-screen rendering function that displays the matching OEM "Recovery: ..." text verbatim from the manual.

**Status bar layout note**:alarm field 携带长 hint 文本时,status bar 必须 `flex-wrap: wrap` 才不会挤死 mode / runtime / counter 字段。

DAD3350 implemented: E0203 (blade contact), E0301 (cover interlock), E0401 (vacuum loss), E0501 (e-stop drill).
KS iConn implemented: E2001-E2006(6 codes,每条都带 clearHint)。
探针台 implemented: 10 codes,clearHint 全覆盖。

---

## Layer 8 — Training scenarios

**What**: ≥ 8 scripted scenarios that walk the user through canonical workflows. Each has:
- Precondition `initial:`(auto-set device state to scenario start)
- Goal text shown to user
- Success criteria(queried from APP state)
- Completion log to localStorage
- **Per-step `check:` + `act:` + `hint:` triple**(L10)— check is user-operation completion predicate, act is coach-代操作 state mutation, hint is human-readable button reference
- **`faultRate:` field**(L30 — see Layer 4)— 0 / 0.2-0.5 / N.A. per scenario type

### Five critical scenario-design rules

#### 8.1 `scenario.initial` MUST NOT satisfy `step 1.check`(L28)

```js
// ❌ WRONG — initial pushes APP into a state where step 1's check is immediately true
{ id:'S10', steps:[
    { check:A => A.mode==='RUNNING', hint:'按 START' },   // step 1
    // ...
  ],
  initial:A => { ensureReady(A, true); A.mode='RUNNING'; },  // ← already RUNNING
}
// → tickScenario first frame marks step 1 ✓ — operator never sees the teaching first sentence

// ✅ RIGHT — step 1 is a user-interaction ACK, distinct from any pre-set state
{ id:'S10', steps:[
    { check:A => A.lastCmd==='JOB' && A.mode==='RUNNING', hint:'按 [F1 JOB] 查看当前任务' },
    // ...
  ],
  initial:A => { ensureReady(A, true); A.mode='RUNNING'; },
}
```

Self-check:apply each step.check to APP-after-initial. Any `step.idx <= 0` that returns true is a skip-step bug.

#### 8.2 Final step.act MUST recover from any dirty state(L28 + L29)

RUNNING-phase scenarios collide with `tickFaults` random injection. The final step's `act:` must:
- Push counters / flags to check-required targets
- `activeErrors.clear()` + mode reset(FAULT/PAUSED/MAINT → RUNNING/READY)
- Cap fault-affected counters to compliance thresholds(`nsopCount=Math.min(nsopCount, threshold)`)
- Bring **clear-predicate dependencies** into satisfaction(if clearHint refers to "change capillary", `act` should set `capLife=Math.min(capLife,5000)` + `capInstalled=true`)

#### 8.3 `check:` uses industry-real thresholds, NOT absolute 0/100%(L28)

```js
// ❌ WRONG — absolute zero is unachievable in production
check: A => A.wireCount >= 100 && A.nsopCount === 0,

// ✅ RIGHT — SEMI-compliant relative threshold
check: A => A.wireCount >= 100 && 
            A.nsopCount <= Math.max(1, Math.floor(A.wireCount * 0.01)),
// SEMI E10 NSOP rate ≤ 1% — allows wireCount=100 to have 0-1 NSOP and still pass
```

Whenever a check involves `=== 0` or `>= 100%`,ask: "Does this metric on a real machine ever achieve 0 / 100% within process window?" If no, use compliance threshold.

#### 8.4 Button grouping by task-essence, NOT row position(L26)

UI buttons MUST be grouped semantically:
- `配置 mode`(wire mode / process type)
- `SETUP 子流程`(wire-feed / pre-align)
- `调参 / TUNE`(H2 / Heater / EFO / GAS_DIAL — process-window tuning)
- `MAINT / 故障处置`(error clear / E-STOP release / exit MAINT)

Each tune-class button carries a real-time dot indicator(绿=in-window / 琥珀=out-of-window / 灰=off)— memoized style write via `el._c !== c`. Button text concise:`H2 工艺窗` better than `H2 调到工艺窗`.

#### 8.5 E-STOP physical-cut scope strict per SEMI S2 + OEM procedure(L27)

`transitionTo('EMSTOP')` hook MUST NOT use `resetTargets(true)` blanket-reset. Enumerate sensor list explicitly:

| What E-STOP cuts | Why |
|---|---|
| Motion(BOND_F / stage / probe Z)| Operator's primary danger |
| Bond electrical(US_PWR / EFO_HV)| Live energy storage |
| Flammable / toxic process gas(H2 / SiH4 / Cl2 / BCl3)| Fire / poison risk |

| What E-STOP preserves | Why |
|---|---|
| Facility gas(AIR / N2)| Cooling / inerting still needed |
| Heater target | Thermal shock cracks capillary / chuck |
| Wire / film tension | Mechanical lock-in, preserves alignment |
| Control / safety circuit power | Operator UI must remain responsive |

Scenario `step.check` for RESUME path:`mode !== 'EMSTOP' && !estop` — does NOT hard-bind to READY(Cu/H2-dependent processes legitimately resume into IDLE pending H2 re-open). Hint text: `(Au 互锁全过 → READY;Cu 因 H2 仍 0 → IDLE,需再补 H2 重 RESUME)`。

Render cache trigger for mode-dependent display must include `dirty.has('mode')` — mode transitions(EMSTOP↔IDLE↔FAULT↔PAUSED)often don't change phase, so phase-only triggers miss(phase-label residual ⚠ EMERGENCY STOP after release).

**Why**: a simulator without scenarios is a sandbox — operators don't know what to practice. Scenarios codify the actual exam.

DAD3350 scenarios:
1. Cold-start to ready (full boot + warm-up sequence)
2. Full-auto cut completion
3. Alignment (manual two-channel)
4. Blade change (D.1 chapter walkthrough)
5. E0203 recovery (blade contact)
6. E0301 cover interlock recovery
7. E0401 vacuum recovery
8. E-stop drill

Each scenario card in the UI shows: name, brief description, completion checkmark from localStorage. Click → load scenario state → user operates → success criteria fires → mark complete.

**Smell test**: complete scenario 1, refresh page, scenario 1 should still show checkmark.

---

## Honest labelling

If the simulator has only 5 of 8 layers — call it a "教学演示 demo" or "操作流程演示". Do not call it "工业级". This honesty is the foundation of user trust.

---

## Layer 9(conditional)— Vision Workview HMI

**When mandatory**: any device whose OEM HMI uses a live camera feed as the operator's primary alignment / control surface — wire bonder, die bonder, prober, dicing-saw alignment, stepper alignment, optical metrology, inspection.

**Reference**: full design template in `07-vision-workview-design.md`. The 8 elements:
1. Permanent dark canvas(hard-coded `#080c14`, NOT theme-variable)
2. HUD 4 corners(CAM/REC + process state + frame info + counter)
3. Phase chip centered bottom(big text)
4. Physical anchor layer(static — die / pad / wafer outline)
5. Dynamic moving elements(per-frame — needle / capillary / spark / scrub)
6. Scale ruler(small corner, real µm units)
7. Scanline / grain overlay(CCD authenticity, < 3% alpha)
8. Cycle trail accumulation(wire trail / scrub marks / kerf lines)

**Critical rules**:
- Frame-iterating animations(Z 平滑、scrub wiggle、spark fade、mini-marker)called **unconditionally** every frame, NOT inside dirty gates(J06 — see `03-anti-flicker-patterns.md`)
- All `setAttribute` writes go through `_tf` / `_op` / `_d` memo guards
- For wafer-class devices, dual-anchor pattern: main view + mini wafer map BR. Mini wafer geometry: `R_max > R_use + pitch/2`(J07)
- Card-type / recipe-type dynamic build hooked from ALL entry points(POWER / CARD_x / CHANGE / CLEAN / DOMContentLoaded)
- Theme toggle must NOT recolor workview background

**Reference deliverables**:
- KS iConn(wire bonder · L06 prototype · wire trail accumulation)
- 探针台 v1.1(prober · dual anchor · scrub mark accumulation · card-type-dynamic pad-needle array)

**Omission rules**:
- Devices with no camera-primary HMI(DAD3350 cut phase、封装模塑机 closed chamber、CMP recipe-driven、furnace)— skip this layer but **document the omission** in delivery report.

---

## Adding a 10th layer

If future projects encounter a need for a 10th layer (e.g., recipe management, multi-station coordination, SECS/GEM upstream), update this file to add the layer with the same depth as 1-9. Skill evolves with experience.
