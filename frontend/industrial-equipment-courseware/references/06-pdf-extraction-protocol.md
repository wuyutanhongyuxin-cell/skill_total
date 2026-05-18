# Reference 06 — OEM PDF Extraction Protocol

Stage 2 of the skill. An OEM operation manual is typically 200-400 pages of dense technical content. Reading it whole into conversation memory blows context. Extracting it carelessly loses the chapter codes that let users reverse-look-up in the original PDF. This protocol balances both.

---

## Batch size

- Use `Read` tool with `pages` parameter — required for PDFs > 10 pages.
- Maximum 20 pages per batch (Read tool limit).
- Plan total batches: ceil(pages / 20). For a 388-page manual: ~20 batches.

---

## Per-batch ritual

For each batch:

1. **Read 20 pages.**
2. **Immediately distill to notes** (the extraction table — see below). Do not retain full text in memory.
3. **Verbatim-quote** every DANGER / WARNING / CAUTION / NOTICE block — these go to the deliverable as-is. Quote into the extraction table.
4. **Note chapter codes** (e.g., `[1.0]`, `[C-15]`, `B.2.3`) verbatim — these are the user's reverse-lookup keys.
5. **Describe figures in words** — top-bar layout, screen constituents, soft-keyboard layout. We will re-render as HTML structure, not copy as image.

After distilling, the full batch text can leave context.

---

## Extraction table template

Maintain ONE running table across all batches. Format:

```markdown
| Aspect | Source page | Verbatim quote / structured note | Used in |
|---|---|---|---|
| Spindle max RPM | p.42 | "60,000 r/min (DAD3350 model variant: 30k-60k continuously variable)" | Simulator SPDL sensor cfg |
| Interlock: air pressure | p.103 | "≥ 0.4 MPa required for spindle start" | Simulator INTERLOCKS[] |
| Screen [1.0] FULL AUTO | p.78 | "Top-left = run status, top-right = recipe name, F1=START, F2=PAUSE..." | Simulator screen `state-1.0` |
| Error E0203 | p.298 | "BLADE CONTACT — Recovery: 1. Stop cut. 2. Inspect blade. 3. Replace if cracks visible. 4. CLEAR." | Simulator error matrix E0203 |
| Warning (p.99 safety chapter) | p.99 | VERBATIM: "WARNING: Spindle continues rotating after STOP for up to 30 seconds. Do NOT open cover until spindle indicator shows 0 rpm." | Manual safety tab + Simulator alarm panel |
| ... | ... | ... | ... |
```

---

## What MUST land in the extraction table

For an industrial-grade simulator, you cannot skip:

- [ ] Top bar / screen-frame description (button layout, status indicators)
- [ ] List of every "screen" or "menu" referenced (becomes FSM state)
- [ ] List of every interlock condition (preflight checks across all chapters)
- [ ] List of every error code (becomes error matrix)
- [ ] All sensor names + units + ranges + "normal" thresholds + ramp characteristics
- [ ] Timing data (boot duration, warm-up duration, cut time formula, retract time)
- [ ] Every DANGER / WARNING / CAUTION / NOTICE block (verbatim)
- [ ] Maintenance procedures that map to scenarios (blade change, dressing, hairline)
- [ ] Recovery procedures for each error (verbatim Cause + Recovery)

---

## What can be SKIMMED

- Front-matter (Read carefully, table of contents) — read once to confirm structure, do not extract
- Detailed UI button-by-button enumerations — extract function descriptions, not individual button locations
- Maintenance schedule tables — note their existence, extract only items that drive simulator scenarios
- Contact info pages

---

## Cross-reference: chapter code → simulator state

Maintain a side table mapping chapter codes to simulator entities:

```markdown
| Chapter code | Simulator entity |
|---|---|
| [1.0] | state `'1.0'` (FULL AUTO main) |
| [1.0.1] | state `'1.0.1'` (FULL AUTO recipe select) |
| [2.0] | state `'2.0'` (MANUAL OP) |
| [C-15] | scenario `'cut-with-hairline-adjust'` |
| [D.1] | scenario `'blade-replacement'` |
| [E.1.1] | error code `E0203` (blade contact) |
| [E.3.2] | error code `E0301` (cover interlock) |
| ... | ... |
```

This table is the basis for the simulator's `state.docRef` field — each state can show "OEM Chapter [1.0]" in the title bar, letting the user trace back to the PDF.

---

## Quality gate after PDF extraction

Before moving to Stage 3 (design):

- [ ] Every chapter of the OEM manual has ≥ 1 entry in the extraction table.
- [ ] All planned simulator states have a documented chapter source.
- [ ] All planned interlocks trace to a specific page.
- [ ] All planned error codes have verbatim Cause + Recovery quotes.
- [ ] All safety messages are quoted verbatim (will become the bilingual safety blocks in the manual artifact).
- [ ] Figures described in words (no image extraction).
- [ ] Total extraction table is 2-5 KB of markdown, not 200 KB (you have summarized, not copied).

If any gate fails, do another targeted read pass on the affected pages.

---

## Token budget

For a 388-page manual:
- 20 batches × ~ 20K tokens of raw PDF text per batch = ~ 400K raw tokens
- Distilled extraction table at the end: ~ 5 KB markdown = ~ 1500 tokens

This is the value of immediate distillation — you keep 0.4% of the raw token cost in context while preserving all decision-relevant content.

---

## Edge cases

- **PDF too poorly OCR'd**: if text comes out garbled, use the `pages` parameter to read just a few pages at a time + visual inspection. Some sections may need manual transcription from the rendered PDF.
- **PDF behind paywall / not lawfully obtained**: refuse the project. Do not exfiltrate via online resources.
- **PDF with embedded video / interactive content**: extract text only; video is out of scope for single-file HTML.
- **Multilingual PDF (Japanese + English)**: read the English; cross-reference Japanese terms when present.
- **PDF with version diffs from user's actual machine**: clearly note "manual is for sw v1.5; user's machine is v1.6 — variances may exist" in the About panel.
