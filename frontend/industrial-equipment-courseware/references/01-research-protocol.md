# Reference 01 — Research Protocol & Cross-Validation

Stage 1 of the skill. The single rule:

> Every technical claim that lands in the simulator MUST cite ≥ 2 independent verifiable sources.

"Independent" means different vendor / different author / not syndicated copies of the same press release.

---

## Required source classes (each project)

For each industrial-equipment courseware project, collect ≥ 1 source from each row below:

| Class | Why | DAD3350 example | Generic equivalent |
|---|---|---|---|
| OEM product page | Authoritative on official model spec | https://www.disco.co.jp/eg/products/dicer/dad3350.html | `<oem-domain>/products/<model>` |
| OEM training page | Reveals expected pedagogical scope | https://www.disco.co.jp/eg/training/ | OEM e-learning / customer education |
| Academic mirror of OEM manual | Verifies content + provides citable URL | https://wiki.nanofab.usc.edu/images/4/47/Dicing_Saw_Manual.pdf | Look at nanofab.<edu>/ / cleanroom.<edu> / fab.<edu> |
| Open-source reference impl | Cross-check architecture | https://cnc.js.org/, https://github.com/cncjs/cncjs | Search GitHub for `<class-of-device> web HMI` |
| Commercial HMI exemplar | Architecture / UX best-of-breed | https://inductiveautomation.com/ignition/modules/perspective | Ignition Perspective is generally the standard |
| State-machine library or pattern reference | Justify FSM approach | https://stately.ai/docs/xstate (XState v5) | XState v5 is the current default for 2026 |
| E-learning standard (only if record-tracking matters) | Industry standard for training records | https://xapi.com/scorm-vs-the-experience-api-xapi/ | xAPI > SCORM for 2026 projects |
| Domain analogue simulator | Architecture proof-of-pattern | https://www.mitre.org/resources/caldera-ot, https://medium.com/@mitrecaldera (HVACSim 2026-03) | Search for ICS / OT training analogues |
| Regulatory / safety standard | Compliance anchor | SEMI S2/S8 (semiconductor) ; ANSI/RIA R15.06 (robotics) ; IEC 61508 (functional safety) | Pick standards relevant to subject industry |

---

## Cross-validation rule, in detail

For each major technical assertion you bake into the simulator:

1. Locate the assertion in the OEM PDF (page number).
2. Find one external independent corroboration (vendor whitepaper, academic citation, alternative source).
3. Record both in a sources table.

Examples of assertions that need this treatment:

- **Spindle RPM range** → OEM brochure page X + DISCO product page bullet point
- **Air pressure interlock value** → OEM manual + general SEMI standard or another vendor's similar machine
- **State machine choice** → architecture rationale + XState/Ignition reference
- **Web Audio synthesis approach** → MDN docs + AudioWorklet best practices
- **Anti-flicker pattern** → React reconciliation principles + at least one MutationObserver tutorial

---

## Source quality heuristics

ACCEPT:
- OEM official site (`*.disco.co.jp`, `*.kla.com`, etc.) — primary authority
- University fab wikis (`*.edu/.../<vendor>-...`) — well-curated mirror
- ACM / IEEE / SEMI / IEC standards portals
- Vendor's own product documentation portal
- GitHub repositories with ≥ 100 stars + recent commits (last 12 months)
- Inductive Automation forum (https://forum.inductiveautomation.com/) — high signal-to-noise
- MDN, W3C, web.dev for browser-API claims

REJECT or treat as low-weight:
- LLM-generated summaries (most "tutorial" sites since 2024)
- Datasheet aggregators (alldatasheet, datasheet5) — frequently stale
- Forum threads without citations
- Reseller pages (they pitch, they don't spec)
- Wikipedia for the niche technical detail (general overview only)
- Translation aggregators (Scribd, etc.) — IP + integrity issues
- Anything behind a paywall you can't actually read

---

## Recording sources

Create (or update) a working source table during Stage 1. It does NOT live in a file — it lives in the conversation, then is **transferred to the simulator's About panel verbatim**. Format:

```
| # | Class | URL | Used for | Verified date |
|---|---|---|---|---|
| 1 | OEM official | https://www.disco.co.jp/eg/products/dicer/dad3350.html | Spec confirmation | 2026-05-12 |
| 2 | OEM manual mirror | https://wiki.nanofab.usc.edu/.../Dicing_Saw_Manual.pdf | Full extraction source | 2026-05-12 |
| 3 | HMI exemplar | https://inductiveautomation.com/ignition/modules/perspective | Architecture cross-check | 2026-05-12 |
| 4 | State machine ref | https://stately.ai/docs/xstate | FSM justification | 2026-05-12 |
| 5 | Open-source analogue | https://github.com/cncjs/cncjs | Reference impl | 2026-05-12 |
| ... | ... | ... | ... | ... |
```

≥ 5 entries is the minimum-to-be-credible gate.

---

## When the source quest fails

If you cannot find ≥ 2 independent sources for a specific claim:

1. Mark that value in code with `// EXTRAPOLATED — not in OEM manual, single source: <URL>` and label the simulator's About panel "Some parameters extrapolated".
2. Surface the gap in the delivery report — do not silently smooth over it.
3. Reduce the strength of the claim in user-facing copy ("typical air-spindle ramps in 25-35s" not "DAD3350 ramps in 30s exactly").

The integrity of "industrial-grade" comes from honesty about what is anchored vs. inferred.

---

## Useful pre-built search templates

When kicking off Stage 1 on a new subject, run these (adapt subject):

```
WebSearch: "<OEM> <Model> operation manual PDF"
WebSearch: "<OEM> <Model> nanofab cleanroom"
WebSearch: "<class-of-device> web HMI 2026 open source"
WebSearch: "<class-of-device> industrial training simulator"
WebSearch: "XState v<latest> documentation"   // confirm current version
WebSearch: "Ignition Perspective best practices 2026"
WebSearch: "<subject-protocol> training simulator MITRE"
WebSearch: "<subject-industry> safety standard SEMI ANSI IEC"
```

Run them in PARALLEL via single message with multiple WebSearch calls.

---

## Updating this protocol

After each project, update the per-subject example column in the table above with a new row capturing the device-specific sources discovered. Skill evolution > rigid skill.
