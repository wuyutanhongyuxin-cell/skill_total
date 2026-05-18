# Reference 03 — Anti-Flicker Patterns

The flicker problem: any DOM region updated by a 10 Hz tick loop will visibly flicker on most monitors. This caused two real bugs during DAD3350 development:

- Sensor panel flickering (values + status dots blinking red while idle)
- Scenario buttons 6/7/8 flickering (GPU repaint spreading from re-rendered error screens to neighboring regions)

The pattern below eliminates both classes.

---

## The Rule

For any region that gets touched by a tick loop ≥ 10 Hz:

1. **Build the DOM ONCE** at initialization. Store refs to each updatable child element on a config object.
2. **Memoize the last-rendered values**. Only `textContent =`, `className =`, or `style.X =` when the value has changed.
3. **Never `innerHTML = ...`** in the tick loop. `innerHTML` destroys + recreates child nodes → layout invalidate → GPU repaint.
4. **Never call `render()` of unrelated panels** from the tick loop. The error-screen re-render bug in DAD3350 v1 was exactly this — `tickSensors` called `render()` which rebuilt panels outside the sensor region.

---

## Reference pattern: sensor panel

```js
const SENSOR_CFG = [
  { key: 'PRES', name: 'PRES', unit: 'MPa', max: 0.7, ok: [0.4, 0.55], digits: 2 },
  { key: 'SPDL', name: 'SPDL', unit: 'rpm', max: 60000, ok: [29000, 60000], digits: 0 },
  { key: 'WATER', name: 'WATER', unit: 'L/min', max: 2.5, ok: [1.0, 1.8], digits: 2 },
  { key: 'VAC', name: 'VAC', unit: 'kPa', max: 80, ok: [50, 80], digits: 0, neg: true },
  // ...
];

// Build once
function buildSensorPanel() {
  const root = document.getElementById('sensorPanel');
  root.innerHTML = '';  // initial wipe is fine — only at init
  SENSOR_CFG.forEach(cf => {
    const row = document.createElement('div');
    row.className = 'sensor-row';
    row.innerHTML = `
      <span class="sensor-name">${cf.name}</span>
      <div class="sensor-bar"><div class="sensor-fill"></div></div>
      <span class="sensor-val">—</span>
      <span class="sensor-unit">${cf.unit}</span>
      <span class="sensor-dot"></span>
    `;
    cf._row  = row;
    cf._fill = row.querySelector('.sensor-fill');
    cf._val  = row.querySelector('.sensor-val');
    cf._dot  = row.querySelector('.sensor-dot');
    root.appendChild(row);
  });
}

// Idle-aware classification
function isExpected(key) {
  const c = APP.context, s = APP.sensors;
  switch (key) {
    case 'PRES':  return APP.powered && c.airValve;
    case 'SPDL':  return s.SPDL_TARGET > 0;
    case 'WATER': return c.waterValve;
    case 'VAC':   return c.vacuumPump;
    default:      return APP.powered;
  }
}

function classifyVal(absVal, ok, max, expected) {
  if (!expected) return 'idle';
  if (absVal < ok[0]) return 'warn';
  if (absVal > ok[1]) return 'bad';
  if (absVal > max * 0.95) return 'bad';
  return 'ok';
}

// Memoized update
const _sensorState = {};
function renderSensors() {
  SENSOR_CFG.forEach(cf => {
    const raw = APP.sensors[cf.key];
    const absVal = cf.neg ? Math.abs(raw) : Math.max(0, raw);  // clamp negatives
    const exp = isExpected(cf.key);
    const cls = classifyVal(absVal, cf.ok, cf.max, exp);
    const memo = _sensorState[cf.key] = _sensorState[cf.key] || { cls: '', val: '', pct: -1 };
    const pct = Math.min(100, (absVal / cf.max) * 100);
    const displayVal = exp ? absVal.toFixed(cf.digits) : '—';

    if (memo.cls !== cls) {
      cf._fill.className = 'sensor-fill ' + cls;
      cf._dot.className = 'sensor-dot ' + cls;
      memo.cls = cls;
    }
    if (memo.val !== displayVal) {
      cf._val.textContent = displayVal;
      memo.val = displayVal;
    }
    if (Math.abs(memo.pct - pct) > 0.5) {  // threshold prevents sub-pixel writes
      cf._fill.style.width = pct.toFixed(1) + '%';
      memo.pct = pct;
    }
  });
}
```

Key tricks:

- `cf._row` etc. — refs cached on the config object so we never re-query DOM in the tick
- `_sensorState[cf.key].cls` etc. — memo per sensor, per channel (cls / val / pct)
- `Math.abs(memo.pct - pct) > 0.5` — width change threshold to prevent sub-pixel updates that the browser would batch anyway
- `displayVal = exp ? value : '—'` — idle suppression: don't show numeric value when sensor not demanded

---

## Reference pattern: status bar / aux bar / scoreboard

Same pattern, smaller:

```js
const _sbMemo = {};
function setSbVal(key, value) {
  if (_sbMemo[key] === value) return;
  _sbMemo[key] = value;
  document.getElementById('sb-' + key).textContent = value;
}
```

Use `setSbVal('mode', APP.systemMode)` instead of direct `textContent =`.

For multi-region tick consumers (status bar, aux bar, scoreboard), have one memo per region: `_sbMemo`, `_auxMemo`, `_scMemo`. Use a thin `setText(memo, id, val)` helper.

---

## Reference pattern: scenario list / lazy-recreation regions

These DON'T tick at 10 Hz — they update only when scenarios complete. So `innerHTML` rebuild is fine ONLY when:

- It's user-triggered, not loop-triggered
- The user is not currently looking at adjacent flicker-sensitive regions
- Frequency < 0.5 Hz

If a scenario-list rebuild is happening every tick because `tickSensors` calls `render()` indirectly, that's the DAD3350 v1 bug. Audit the call graph:

```
tickSensors → renderSensors → (DO NOT call) render() of unrelated regions
```

`renderSensors` must touch ONLY `#sensorPanel`. Other panels render on their own triggers.

---

## Verifying objectively: MutationObserver

After implementing memoization, prove it with MutationObserver. See `04-mcp-test-templates.md` for the script. Expectation: 0 DOM writes during 1.5s with no value changes.

If writes > 0, find which call wrote and fix. Common offenders:

- `Math.random()` jitter applied every tick → values change every tick → memo never matches → memo is pointless. Add a per-sensor "should-jitter" guard.
- `pct.toFixed(1)` strings are always different at sub-pixel level → use the `Math.abs(memo.pct - pct) > 0.5` threshold.
- Subscribing to an event that fires on every animation frame → throttle / debounce.

---

## Dirty-gated vs every-frame — J06 rule

Sediment from 探针台 v1.1(2026-05-18). The anti-flicker pattern above uses `if (memo.X !== Y) write` — a memo gate — and it's correct for **discrete** view state changes(label / class / fill / phase chip color). But it breaks for **frame-iterating animation**, where each frame's output depends on the **previous frame's value**.

### Two render gate styles, two scopes

| Style | When | Example | Why |
|---|---|---|---|
| Dirty-gated(只在 model 变化时写)| Label / class / style / chip color | `phase-bar`、`mode-chip`、`sensor-list`、`scenario-list`、`interlock dots` | Model 没变就没必要写 DOM — memo guard prevents wasted work |
| Every-frame(无条件每帧调用,内部 memo)| Frame-to-frame interpolation animation | `_zDisp += (zTgt - _zDisp) * 0.30`(exponential smoothing); `scrubX = Math.sin(t*ω)`(oscillation); spark fade; mini-marker tracking | Iteration **needs** every-frame ticking — if you skip a frame, the iteration dies. Memo still guards the actual `setAttribute` to keep MutationObserver at 0. |

### The bug pattern(J06)

```js
// ❌ WRONG — frame-iterating animation inside a dirty gate
function render() {
  if (dirty.has('phase') || cache.phase !== APP.phase) {
    cache.phase = APP.phase;
    updateWorkview();   // ← contains _zDisp += (zTgt - _zDisp) * 0.30
                        //   when phase doesn't change, this never runs
                        //   _zDisp stalls at frame 1 forever
  }
}
```

Symptom: 设定 Z target = 34,等 1.5 s 后 SVG transform translate(0, 16.45)— 卡在中途。100 帧 0.7^100 ≈ 0 应早收敛,但只跑了 1 帧。

### The fix

```js
// ✅ RIGHT — every-frame animation OUT of the dirty gate
function render() {
  updateWorkview();   // ← unconditional, every frame
                      //   internal _tf / _op memo prevents DOM write spam
  if (dirty.has('phase') || cache.phase !== APP.phase) {
    cache.phase = APP.phase;
    updatePhaseChip();   // ← discrete update OK to dirty-gate
  }
}

function updateWorkview() {
  _zDisp += (zTgt - _zDisp) * 0.30;
  const newTf = `translate(0 ${_zDisp.toFixed(2)})`;
  if (needlesG._tf !== newTf) {       // ← memo guard prevents DOM write when unchanged
    needlesG.setAttribute('transform', newTf);
    needlesG._tf = newTf;
  }
}
```

### SVG attribute memo pattern

For every-frame SVG animation, cache the **string** that would be written as an attribute on the DOM element itself:

```js
// transform
const tf = `translate(${x.toFixed(2)} ${y.toFixed(2)})`;
if (el._tf !== tf) { el.setAttribute('transform', tf); el._tf = tf; }

// opacity
const op = o.toFixed(2);
if (el._op !== op) { el.setAttribute('opacity', op); el._op = op; }

// path d
const d = `M ${x1} ${y1} L ${x2} ${y2}`;
if (el._d !== d) { el.setAttribute('d', d); el._d = d; }

// fill (when status-driven)
if (el._fill !== status) { el.setAttribute('fill', COLORS[status]); el._fill = status; }
```

Using `.toFixed(2)` not raw float ensures sub-pixel jitter doesn't trigger writes(L16 lesson — memo on **formatted display** not raw value).

### Verification(J06 self-check)

After implementing a frame-iterating animation:

```js
// Pause mode, set Z target programmatically, wait 1.5s, read back
APP.phase = 'P3';        // expected zTgt = 42 per Z_TABLE
await new Promise(r => setTimeout(r, 1500));
const tf = needlesG.getAttribute('transform');
const z = parseFloat(tf.match(/translate\(0 (-?[\d.]+)\)/)[1]);
// Expect |z - 42| < 0.5
```

If z stalls below target → animation function is dirty-gated. Move it out.

---

## When `innerHTML` IS acceptable

- Initial DOM build (once)
- User explicitly navigates to a new screen / scenario / error code
- Reset / new-game / new-recipe operations
- Print pre-render

In these cases, `innerHTML` clears state cleanly and is fine. The rule is "not in a tick loop".

---

## Tick loop budget

Target tick rate is 10 Hz (100ms per tick). Budget per tick:

- Read APP state: ~1ms
- Compute new sensor values: ~2ms
- Sensor render (memoized): ~1ms
- Status bar render (memoized): ~0.2ms
- Audio gain ramps: ~0.5ms
- **Total**: < 5ms

If the tick is exceeding 10ms, do not pump faster — first audit for unnecessary work. The DAD3350 v2 tick runs at ~3ms.

---

## Audit checklist before declaring anti-flicker done

1. `grep -n 'innerHTML' simulator.html` — no occurrences inside any `tick*` / `render*` function called by `setInterval` / `requestAnimationFrame`.
2. Memoized state objects exist for each high-update region (`_sensorState`, `_sbMemo`, `_auxMemo`, ...).
3. MCP MutationObserver returns 0 writes on each region during 1.5s idle.
4. Visual inspection at 60 fps: no perceptible blink on any DOM region during normal operation.
