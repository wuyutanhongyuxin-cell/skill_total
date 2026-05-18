# Reference 04 — chrome-devtools MCP Test Templates

Reusable MCP `evaluate_script` patterns for objective QA of an industrial-grade simulator. **All 6 numbered patterns(1-6)are required;Pattern 4-5 are optional bonus.** Patterns 7-8 are sediment-driven from探针台 v1.0/v1.1.

Prerequisites:
- chrome-devtools MCP **or** playwright MCP available + Chrome / chromium running
- Simulator HTML served via local HTTP(NOT file://). The verified-working environment is:
  ```powershell
  cd "<output-dir>"
  python -m http.server 18080 --bind 127.0.0.1
  # → playwright_navigate http://127.0.0.1:18080/<file>
  ```
- **NEVER use ports 8765 / 8080 / 9000** — they fall in Windows dynamic TCP exclusion(WinNAT / Hyper-V reserved range). Use high 5-digit port like 18080 / 23800. Verify with `netstat -ano | findstr ":<port>"` before binding.
- **NEVER pass `file://` to playwright** — it blocks the protocol(Access to "file:" protocol is blocked). chrome-devtools-mcp can do file:// but locks the user's main Chrome profile,so playwright + http:// is the durable combination.
- Expose key APP state globals so MCP can read them without DOM scraping(`window.APP`, `preFlightStatus`, `STATES`, `SCENARIOS`, `INTERLOCKS`, `runCmd`, `triggerError`, `startScenario`, `coachAct`)— see L15.

If Chrome refuses to launch("browser is already running for ...chrome-profile"), use PowerShell:

```powershell
Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 800
```

Then retry `mcp__chrome-devtools__new_page`. **Better**: skip chrome-devtools-mcp entirely and use playwright MCP — fewer profile collisions.

---

## Mandatory test session header(L31)

**Every test session** opens with this code block before any Pattern runs. It defeats localStorage pollution from previous sessions:

```js
// Run as first evaluate_script BEFORE any pattern
() => {
  Object.keys(localStorage).filter(k => k.startsWith('<device>-sim-')).forEach(k => localStorage.removeItem(k));
  // Or, more aggressively:
  // localStorage.clear();
  return 'localStorage cleared';
}
```

Then hard reload(`navigate_page` again with `ignoreCache: true` if available, else `location.reload(true)`). Without this, `<device>-sim-active-scen` / `<device>-sim-completion` etc. from prior sessions cause APP to boot into stale state — symptom: `mode='RUNNING'` or `'LOAD'` instead of expected `OFFLINE` at page load.

After test cleanup, release the http server:
```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 18080 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue
```

---

## Pattern 1 — Physics Validation

Trigger a representative scenario from cold start; sample sensors + state at multiple time points; verify state machine advances + sensors converge.

```js
async () => {
  // 1. Cold start
  document.getElementById('powerBtn').click();           // or APP.powerOn()
  await new Promise(r => setTimeout(r, 3200));           // POST boot

  // 2. Utilities + warm-up
  document.getElementById('auxAir').click();
  document.getElementById('auxWater').click();
  document.getElementById('auxVacuum').click();
  await new Promise(r => setTimeout(r, 3500));           // PRES ramps to 0.5 MPa
  document.getElementById('btnWarmUp').click();          // startWarmUp()
  await new Promise(r => setTimeout(r, 8500));           // warm-up to 100%

  // 3. Select scenario + START
  document.getElementById('scenario-fullauto').click();
  document.getElementById('btnStart').click();

  // 4. Multi-time-point sampling
  const snaps = [];
  for (const dt of [500, 1500, 3500, 13000]) {
    await new Promise(r => setTimeout(r, dt));
    snaps.push({
      ms_after_start: snaps.reduce((a, b) => a + b.ms_after_start, 0) + dt,
      state: APP.currentState,
      mode: APP.systemMode,
      phase: APP.running.cutPhase,
      spdl: Math.round(APP.sensors.SPDL),
      load: Math.round(APP.sensors.SPDL_LOAD || 0),
      cut: APP.running.currentCut,
    });
  }
  return { snaps, finalMode: APP.systemMode, alarms: APP.alarmCount };
}
```

**Assertions** (do them in the calling code, not in script):
- Snap 1 (500ms after start): `phase === 'rampup'`, `spdl > 0 && spdl < target`
- Snap 2 (2000ms total): `phase` in `['rampup', 'approach']`, `spdl > 50% of target`
- Snap 3 (5500ms total): `phase` in `['cut', 'retract']`, `spdl ≈ target ± 5%`
- Snap 4 (18500ms total): cut count incremented, no alarms (unless fault-injection scenario)

**Common failures + fixes**:
- Snap 1 phase is `'cut'` already → START bypasses rampup → fix `cutPhase = 'rampup'` initial, advance from rampup→approach only when `SPDL >= 0.95 * SPDL_TARGET`
- Snap 3 spdl significantly below target → load drag too aggressive → reduce drag coefficient (DAD3350 v1 used 6, v2 used 0.5)
- All snaps in `IDLE` → warm-up bailed early (PRES not ready) → wait longer before `startWarmUp()`

---

## Pattern 2 — Interlock Coverage

Query `preFlightStatus()` and verify exact count + pass/fail map.

```js
() => {
  const status = preFlightStatus();
  const fails = status.filter(s => !s.ok).map(s => ({ id: s.id, err: s.err }));
  return {
    interlockCount: status.length,
    passCount: status.length - fails.length,
    failCount: fails.length,
    failedInterlocks: fails,
  };
}
```

**Assertions**:
- `interlockCount >= 13` (subject minimum)
- At cold start: most fail (only `power` passes initially, then everything else fails)
- After full prep sequence (power + utilities + workpiece + warm-up): `failCount === 0`
- Kill ONE specific context flag (e.g., `APP.context.coverClosed = false`), re-run — exactly ONE interlock should now fail, and it should be the cover one

```js
// Targeted interlock kill test
() => {
  const before = preFlightStatus();
  APP.context.coverClosed = false;
  const after = preFlightStatus();
  const newlyFailed = after.filter((s, i) => s.ok === false && before[i].ok === true);
  APP.context.coverClosed = true;  // restore
  return { newlyFailed: newlyFailed.map(s => s.id) };  // expect ['cover']
}
```

---

## Pattern 3 — Flicker Objectivity (MutationObserver)

Attach a MutationObserver to a region; sample for 1.5 seconds during a period of no value change; expect 0 writes.

```js
async () => {
  // Setup: device is on but idle, no scenario running
  // (caller responsibility — must be in a stable state)

  const targets = ['sensorPanel', 'statusBar', 'scenarioList', 'fkeyRow', 'auxBar'];
  const results = {};

  for (const id of targets) {
    const el = document.getElementById(id);
    if (!el) { results[id] = { writes: 'not_found' }; continue; }
    let writes = 0;
    const obs = new MutationObserver(muts => { writes += muts.length; });
    obs.observe(el, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeOldValue: false,
      characterDataOldValue: false,
    });
    await new Promise(r => setTimeout(r, 1500));
    obs.disconnect();
    results[id] = { writes };
  }
  return results;
}
```

**Assertions**:
- Every region's `writes === 0` during stable idle (sensor values not changing, no scenario running, status bar stable)
- If `writes > 0`: identify the source via `MutationRecord.target` in the observer callback; common culprits:
  - Sensor `textContent` writes when memo failing → check `_sensorState[key].val` comparison
  - Width style writes from `pct.toFixed(1)` strings → use threshold like `Math.abs(memo.pct - pct) > 0.5`
  - Periodic `render()` called from tick loop → remove all `render()` calls from `tickSensors`

**Note**: if the simulator is mid-scenario with sensors actively changing, this test will see writes (expected). Test in idle state OR test a region that shouldn't update (scenario list, F-key row).

---

## Pattern 4 (optional) — Audio Sanity

Verifies Web Audio engine didn't throw on init:

```js
() => ({
  ctxExists: typeof audioCtx !== 'undefined' && audioCtx !== null,
  ctxState: audioCtx?.state || 'no_ctx',
  spindleOscType: spindleOsc?.type || 'no_osc',
})
```

**Assertions**:
- `ctxExists === true` after first user gesture (POWER ON click)
- `ctxState === 'running'` (not `'suspended'`)
- `spindleOscType === 'sawtooth'`

---

## Pattern 5 (optional) — Scenario completion log read

Read the localStorage completion log to verify persistence:

```js
() => {
  const log = JSON.parse(localStorage.getItem('<device>-sim-scenarioLog') || '{}');
  const scenarios = SCENARIOS.map(s => s.id);
  return {
    total: scenarios.length,
    completed: scenarios.filter(id => log[id]?.completed),
    pending: scenarios.filter(id => !log[id]?.completed),
  };
}
```

---

## Pattern 6 — Scenario walkthrough via startScenario + coachAct(MANDATORY, J03)

Validate **all N scenarios** in a single `evaluate_script` by walking each via `startScenario` + `coachAct` loop. This replaces the verbose per-step button-click validation(10 scenarios × ~10 steps × tick wait = ~100 MCP rounds — unfeasible). One evaluate run = full coverage.

```js
async () => {
  const safeMax = 50;     // ceiling per scenario to prevent runaway
  const results = [];
  for (const sc of CFG.SCENARIOS) {
    // Reset between scenarios so each starts clean
    if (typeof stopScenario === 'function') stopScenario();
    activeErrors?.clear?.();
    APP.activeErrors?.clear?.();
    // Start + walk
    startScenario(sc.id);
    let iter = 0;
    while (APP.scenarioStep < sc.steps.length && iter < safeMax) {
      coachAct();
      iter++;
      await new Promise(r => setTimeout(r, 30));   // let tickScenario flush
    }
    results.push({
      id: sc.id,
      name: sc.name,
      total: sc.steps.length,
      reached: APP.scenarioStep,
      completed: APP.scenarioStep >= sc.steps.length,
      iter,
      stuck: iter >= safeMax && APP.scenarioStep < sc.steps.length,
      errors: [...(APP.activeErrors || [])],
      mode: APP.mode,
    });
  }
  return {
    total: results.length,
    completed: results.filter(r => r.completed).length,
    stuck: results.filter(r => r.stuck).length,
    failedToFinish: results.filter(r => !r.completed && !r.stuck).length,
    details: results,
  };
}
```

**Assertions**:
- `total === completed`(all scenarios reach final step)
- `stuck === 0`(no scenario hits the safeMax ceiling — means a step.act doesn't actually satisfy step.check)
- For each result:`reached === total`(no scenario half-runs)
- `errors === []` at completion(final-step act cleared activeErrors per L29)

**Why coachAct is equivalent to real button clicks**:`coachAct()` calls `step.act(APP)` + forced sensor sync + tickScenario. User's real button click goes `runCmd → state mutation`,which writes to the same APP fields. The validation goal — step.check progression + initial-not-presatisfying-step-1 + act-from-dirty-state recovery — all live on the same code path. See J03 sediment.

**Limitations**(must be covered by other tests):
- Doesn't validate cmdEnabled gating(use real button-click test for that)
- Doesn't validate render flicker(use Pattern 3 MutationObserver)
- Doesn't validate mouse drag / multi-key shortcuts(none of the 5 reference deliverables use these)

**Screenshot archival**: take one screenshot per scenario at terminal state(N scenarios = 2N tool rounds — evaluate + screenshot each). Naming: `<device>-sim-vN-walk-S01.png` through `<device>-sim-vN-walk-S10.png`.

---

## Pattern 7 — Frame-iterating animation convergence(J06)

When the workview uses exponential smoothing / scrub wiggle / spark fade / mini-marker tracking, verify that the animation function is called every frame(not stuck in a dirty gate). This catches J06 regressions.

```js
async () => {
  // Setup: device powered, paused for clean Z phase control
  APP.powered = true;
  APP.mode = 'PAUSED';
  // Test each phase Z target
  const samples = {};
  const Z_TABLE = window.Z_TABLE || { 'P1': 0, 'P3': 42, 'P4': 42, 'P6': 0 };
  for (const [phase, zTgt] of Object.entries(Z_TABLE)) {
    APP.phase = phase;
    await new Promise(r => setTimeout(r, 1500));    // ~90 frames at 60Hz
    // Read back SVG transform
    const needlesG = document.getElementById('needles');
    if (!needlesG) { samples[phase] = { err: 'needles_not_found' }; continue; }
    const tf = needlesG.getAttribute('transform') || '';
    const m = tf.match(/translate\(0\s+(-?[\d.]+)\)/);
    samples[phase] = { 
      zTgt, 
      zObserved: m ? parseFloat(m[1]) : NaN, 
      converged: m ? Math.abs(parseFloat(m[1]) - zTgt) < 0.5 : false,
    };
  }
  return samples;
}
```

**Assertions**:
- For every phase:`converged === true`
- A stalled value(e.g. P3 target 42 but observed 16.5)= J06 bug:`updateWorkview()` is inside a dirty gate. Fix per `03-anti-flicker-patterns.md` § "Dirty-gated vs every-frame".

This pattern applies whenever the simulator has SVG attribute interpolation between frames. Skip if all view updates are discrete state changes.

---

## Pattern 8 — ensureReady completeness for interlock kill isolation(J05)

Verify that the baseline `ensureReady(APP, true)` resets **all** transient state, not just the subset that "looks like READY". If any transient flag leaks, single-kill isolation tests cross-contaminate.

```js
async () => {
  const results = [];
  // INTERLOCKS list assumed exposed; kills are specified per-interlock
  const KILLS = [
    { id: 'EMO',         apply: A => { A.estop = true; },                  expect: 'I2' },
    { id: 'DOOR',        apply: A => { A.coverClosed = false; },           expect: 'I3' },
    { id: 'CARD_LIFE',   apply: A => { A.tdCounter = 999999; },            expect: 'I11' },
    { id: 'OVERDRIVE',   apply: A => { A.overdrive = 110; },               expect: 'I12' },
    // ... full kill list
  ];
  for (const kill of KILLS) {
    ensureReady(APP, false);               // baseline reset
    kill.apply(APP);                       // single kill
    const fails = preFlightStatus().filter(s => !s.ok).map(s => s.id);
    const isolated = fails.length === 1 && fails[0] === kill.expect;
    results.push({ kill: kill.id, expected: kill.expect, gotFails: fails, isolated });
  }
  return {
    total: results.length,
    isolated: results.filter(r => r.isolated).length,
    contaminated: results.filter(r => !r.isolated),
  };
}
```

**Assertions**:
- `total === isolated`(all 13-16 kills are single-fail isolated)
- `contaminated === []`

**If a kill triggers multiple fails**(e.g., OVERDRIVE also triggers I11 CARD_LIFE):
- Root cause:`ensureReady` did NOT reset `tdCounter`(or whichever counter that other interlock depends on)
- Fix:Add the missing transient reset to `ensureReady`. Template:
  ```js
  function ensureReady(A, andRunning) {
    A.powered = true; A.estop = false; A.coverClosed = true;
    A.cardClamped = true; A.cardLife = 95;
    // ALL transient state — explicit list, no implicit defaults
    A.tdCounter = 0; A.dieCount = 0; A.nsopCount = 0;
    A.activeErrors.clear();
    A.fritted = false; A.soakStable = true; A.heaterFault = false;
    A.guardOn = true; A.leakFloorRecalibrated = true;
    // ... every transient flag explicitly
    if (andRunning) { A.mode = 'RUNNING'; A.phase = startingPhase(); }
    else A.mode = 'READY';
  }
  ```

See J05 for full sediment.

---

## Pattern 9 — Theme toggle does NOT recolor workview(Vision Workview Layer 9 V8)

For devices with vision workview, verify dark canvas stays dark across theme toggles:

```js
async () => {
  const workview = document.querySelector('.workview svg');
  if (!workview) return { skipped: 'no_workview' };
  // Take baseline
  const bgDark = getComputedStyle(workview.parentElement).backgroundColor;
  // Toggle theme
  document.documentElement.setAttribute('data-theme', 
    document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
  );
  await new Promise(r => setTimeout(r, 100));
  const bgAfter = getComputedStyle(workview.parentElement).backgroundColor;
  // Restore
  document.documentElement.setAttribute('data-theme', 
    document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'
  );
  return { 
    bgDark, bgAfter, 
    stable: bgDark === bgAfter,
  };
}
```

**Assertion**: `stable === true`. If false, workview is binding background to a theme CSS variable instead of hard-coding `#080c14`.

---

## Test result archival

For each MCP test run:

1. Capture screenshot via `mcp__chrome-devtools__take_screenshot` to `<output-dir>\_qa_screenshots\<device>-sim-v<N>-<NN>-<descriptor>.png`
2. Record the raw JSON return value from `evaluate_script`
3. Append both to the final delivery report

Naming convention example: `dad3350-sim-v2-01-cold-start.png`, `dad3350-sim-v2-02-physics-snaps.png`, `dad3350-sim-v2-03-flicker-zero.png`.

---

## Generic conventions

- MCP `evaluate_script` CAN be `async` and use `setTimeout` / Promises
- The outermost `return` must be JSON-serializable — never return DOM nodes
- Read big-state via globals: `Object.keys(STATES).length`, `INTERLOCKS.length`, `SCENARIOS.length`
- Sleeps + timeouts use real wall-clock; be patient with multi-stage scenarios (full cold-start to first cut completion ≈ 20 seconds)
- If a test is flaky, look first for race conditions (clicking button before previous transition completed) — add `await waitFor(predicate)`

```js
async function waitFor(predicate, timeoutMs = 5000) {
  const start = Date.now();
  while (!predicate()) {
    if (Date.now() - start > timeoutMs) throw new Error('waitFor timeout');
    await new Promise(r => setTimeout(r, 50));
  }
}
```

---

## When to NOT use MCP

- If the test is a static code check (grep for `innerHTML` in tick functions, count interlocks) → use Grep, not MCP. Faster.
- If user can't run Chrome at test time → fall back to static analysis + claim "objective QA pending"; do not silently skip.
