# Reference 05 — Safety, Copyright, & IP Policy

Industrial OEM manuals come with hard legal constraints. Violating them turns a useful learning artifact into a liability. This file is the non-negotiable policy.

---

## OEM Copyright

OEM manuals are typically marked:
- `<DO NOT COPY>` (DISCO style)
- `Confidential — Property of <OEM>`
- `Proprietary and Confidential`
- `For Authorized Customer Use Only`

**Rules**:

1. **Local educational use is fair use** in most jurisdictions (US 17 USC §107, EU Directive 2001/29 art 5). Building a personal study tool from an OEM PDF you (or your employer) lawfully obtained is generally permitted.

2. **Verbatim reproduction is NOT fair use.** Quoting short passages (≤ ~50 words) of safety language is acceptable; reproducing whole pages, whole tables of error codes, or whole UI screenshots is NOT. Paraphrase / restructure / re-render in your own words and figures.

3. **DO NOT publish or distribute publicly.** No GitHub public repos, no Cloudflare-deployed pages, no Slack channels, no Discord. The artifact stays on the user's local disk or private/encrypted storage.

4. **The deliverable MUST carry a disclaimer.** Mandatory text in the About / Footer section:

   > 教育用途非官方仿制 — 与 <OEM> 无关联、不代表 <OEM>、不替代 <OEM> 官方文档。本工具仅供本地学习使用。<br>
   > Educational unofficial replica — not affiliated with, endorsed by, or distributed on behalf of <OEM>. For local educational use only.

5. **Trademark restraint.** OEM logos / brand marks should NOT be reproduced visually. Reference by text name only ("DISCO DAD3350") is acceptable; pasting the corporate logo is not.

6. **Watermark the document.** Add to the printed view + the About panel: `本地学习版 — Local Educational Build — <date>`. This deters unintended redistribution.

7. **If the user requests public distribution**: refuse, explain the constraint, suggest:
   - Contact OEM legal for written permission
   - Replace OEM-specific values with generic ranges + relabel as "generic <class-of-device> trainer"
   - Have an OEM employee build it (then OEM owns the IP cleanly)

---

## Safety Information Handling

Real industrial equipment can kill or maim. Safety language is the most consequential text in the OEM manual. Rules:

1. **DANGER / WARNING / CAUTION / NOTICE** levels are technical terms with specific meanings (ANSI Z535 / ISO 3864). Preserve the level in the deliverable. Do not downgrade DANGER to "important note".

2. **Verbatim original + 中译 双语呈现** for every safety message. The Chinese translation can be your own, but the original English must be present so operators can cross-reference the OEM manual.

3. **Do NOT use emoji as safety icons.** Use established hazard symbols (ISO 7010 W001 general warning triangle, etc.) or text labels. Emoji read as decorative and undermine the seriousness.

4. **No emoji in industrial-tone content generally.** Violates the discipline aesthetic.

5. **No "summary" or "key takeaways" interpretation of safety language.** Operators must read the original. A summary risks omitting a critical condition.

6. **All safety chapters in the manual artifact are reproduced in full** (paraphrased where appropriate, verbatim for the actual DANGER/WARNING/CAUTION blocks). Skipping a safety chapter to fit a tab is a defect.

7. **In the simulator**: when an alarm fires, the displayed error description must match the OEM error guide's exact "Cause" and "Recovery" text. Paraphrasing here trains the wrong recovery procedure.

---

## Data Collected from User

If the simulator records anything (quiz scores, scenario completion times):

1. localStorage only — NO `fetch()`, NO POST to any backend.
2. The user can clear via DevTools Application → Storage → Clear Storage.
3. Document what is recorded in the About panel:

   > 本应用仅在浏览器本地存储中记录:主题、当前 tab、quiz 最佳成绩、训练情景完成状态。所有数据存储在你本机 localStorage,不上传任何服务器。

---

## Legal Disclaimers Boilerplate

In the simulator About panel, paste verbatim (substitute OEM + model):

```
免责声明 / Disclaimer

本工具是 <OEM> <Model> 设备的教育用途非官方仿真器。本工具:

1. 与 <OEM> 无任何官方关联,不代表 <OEM> 的官方意见。
2. 不替代 <OEM> 官方培训、官方手册或现场操作经验。
3. 不应作为实际设备操作的唯一依据。任何实际操作必须以 <OEM>
   官方手册、现场培训师指导、设备所在工厂的 SOP 为准。
4. 因使用本工具的信息或仿真结果而导致的任何设备损坏、人身伤害、
   财务损失,本工具作者不承担任何责任。

参考资料: <OEM> 官方手册 <PDF 标题> <版本号>,公开镜像
<academic-mirror-URL>。设备规格官方页面: <oem-product-page-URL>。

本地学习版 — 不公开分发 — <build-date>

This is an educational unofficial simulator for the <OEM> <Model>. It
is not affiliated with, endorsed by, or distributed on behalf of <OEM>.
It does not replace official OEM training, manuals, or hands-on
experience. Do not use as the sole reference for actual device
operation. The author assumes no liability for damages from use.
```

---

## What to refuse

- Producing a simulator that demonstrates how to bypass interlocks → refuse. Industrial interlocks save lives. A simulator that teaches bypassing is a hazard.
- Producing a simulator with falsified safety values (lower than OEM) → refuse. Misleads training.
- Reproducing OEM trademarks on a public site → refuse unless OEM legal approval verified.
- Generating fake "OEM certification" badges or "operator certified" mock documents → refuse. Could be misused for credential fraud.

---

## When OEM has its own training simulator

If OEM offers an official training simulator (e.g., Siemens TIA Portal + S7-PLCSIM, Allen-Bradley Studio 5000 Logix Emulate):

1. Recommend the official tool first.
2. The locally-built simulator is a supplement for users who lack access (no license, no install on personal Windows machine).
3. Cite the official tool in the About panel.

---

## Future review trigger

Re-read this file (or this skill's reference set) if:
- User requests public distribution → reinforce policy
- User requests an artifact for a device with regulated industries (medical, aerospace, defense) → escalate to additional safety standards
- OEM contacts the user about the artifact → defer to OEM
