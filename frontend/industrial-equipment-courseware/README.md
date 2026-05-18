# industrial-equipment-courseware

Skill for building a paired single-file HTML deliverable set — **operation manual + industrial-grade simulator** — from an OEM PDF + online cross-validated research.

> v2(2026-05-18)— 5 个项目(DAD3350 / AD8312PLUS / KS iConn / 封装模塑机 / 探针台)沉淀加固。规则层落 L01-L31 + J01-J07 共 32 条具体翻车经验。

## Quick start

When a user asks for "给 <设备> 做操作学习手册 + 仿真训练器", invoke this skill via the `Skill` tool:

```
Skill: industrial-equipment-courseware
```

The skill walks 8 stages (scope → research → extract → design → manual → simulator → QA → delivery) with gates between each.

## What's in v2

| 维度 | v1 | v2 | Δ |
|---|---|---|---|
| Simulator layers | 8 mandatory | **8 mandatory + 1 conditional**(Vision Workview HMI) | +1 |
| MCP test patterns | 3 mandatory + 2 bonus | **6 mandatory + 3 bonus** | +4 |
| Self-check dimensions | 18 | **23** | +5 |
| References files | 6 | **7** | +1 |
| Anti-patterns 条目 | 13 | **20** | +7 |
| Reference deliverables | 1(DAD3350)| **5** | +4 |

## Canonical deliverables

| 项目 | anchor 模式 | 物理类 | Layer 9 |
|---|---|---|---|
| DAD3350 划片机 | OEM PDF 388 页 | 机械 + 切削 | 否(cut phase no camera primary) |
| AD8312PLUS 贴片机 | Brochure-anchored | 运动学 | 是(基本) |
| KS iConn wire bonder | Brochure + ELA + Inseto | 超声 + 电气 | **是(L06 prototype)** |
| 封装模塑机 | Multi-OEM(Towa + ASMPT) | 化学动力学(Kamal-Sourour) | 否(closed chamber) |
| 探针台 | Multi-OEM(Accretech + FormFactor) | **elec-mech 接触 + 微电流** | **是(v1.1 double-anchor)** |

## Files in this skill

- `SKILL.md` — the workflow(8 stages × 9 layers × 23-dim self-check)
- `references/01-research-protocol.md` — Stage 1: source classes + cross-validation + 已验证 URL 池
- `references/02-industrial-grade-criteria.md` — Stage 5: 9 mandatory layers + Layer 8 5 critical rules + smell tests
- `references/03-anti-flicker-patterns.md` — memoization + dirty-gated vs every-frame 对照表 + SVG attribute memo pattern(`_tf` / `_op` / `_d`)
- `references/04-mcp-test-templates.md` — 6 mandatory + 3 bonus chrome-devtools / playwright MCP scripts + L31 mandatory session header
- `references/05-safety-copyright.md` — OEM IP / fair-use / safety language policy
- `references/06-pdf-extraction-protocol.md` — OEM PDF → extraction table
- `references/07-vision-workview-design.md` — **NEW** — Layer 9 conditional Vision Workview HMI(8 elements + dual-anchor + card-type dynamic build + J07 geometry constraint)

## Companion skills

- `single-file-courseware` (sibling) — used for Stage 4 (manual artifact build)
- `frontend-design` (plugin) — invoked for aesthetic commitment in Stage 3

## Updating this skill

After each project, update:
- The reference-deliverable list at the bottom of `SKILL.md`
- New authoritative source URLs in `references/01-research-protocol.md`
- Any new mandatory layer in `references/02-industrial-grade-criteria.md`(currently 8 mandatory + 1 conditional)
- New MCP test patterns in `references/04-mcp-test-templates.md`(currently 6 mandatory + 3 bonus)
- New anti-patterns in `SKILL.md` 末尾的 anti-patterns 表(currently 20)
