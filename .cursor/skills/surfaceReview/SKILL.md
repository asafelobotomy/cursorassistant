---
name: surfaceReview
description: "Use when: reviewing agents/*.md, skills/*/SKILL.md, or .mdc rules for contradictions, ambiguity, persona drift, cognitive load, coverage gaps, and composition conflicts before merge."
version: "1.1"
license: MIT
disable-model-invocation: true
paths:
  - "agents/**"
  - "skills/**"
  - "template/rules/**"
  - ".cursor/agents/**"
  - ".cursor/skills/**"
  - ".cursor/rules/**"
  - "AGENTS.md"
---

# Surface review

Six-module audit of Cursor instruction surfaces. Invoke with **`/surfaceReview`** (not auto-applied). For module checklists and severity rules, read [references/modules.md](references/modules.md) when executing.

Use **Read**, **Grep**, **Glob**; run `cursorEval check` / `tokens` on SKILL.md when `tools/cursorEval/` exists.

## When to use

- Before merging changes to agents, skills, or `.mdc` rules
- When routing or instruction quality may explain bad delegation

## When NOT to use

- **Code/PR review** → `review` subagent
- **New surface authoring** → edit first, then `/surfaceReview`
- **Install drift** → `lifecycleAudit` or `cursorLifecycle`

## Modules (run in order)

Label each module in output as **Module 1** … **Module 6** (names below).

| # | Module | Output prefix |
| --- | --- | --- |
| 1 | Contradiction detection | `contradiction:` |
| 2 | Semantic ambiguity | `ambiguity:` (include rewrite) |
| 3 | Persona consistency | `persona:` |
| 4 | Cognitive load | `cognitive-load:` (metric + threshold) |
| 5 | Semantic coverage | `coverage-gap:` + standalone `scope-coverage:` line |
| 6 | Composition conflicts | `composition:` |

## Findings table

After all modules, emit a table: Severity | Module | Section | Finding | Suggested fix. Empty module → one row `— | <module> | — | No findings. | —`.

Close with:

> **Result:** N critical, N high, N medium, N low — [ready to merge | needs revision before merge | block: restructure required]

| Rule | Outcome |
| --- | --- |
| Any Critical | block: restructure required |
| Any High | needs revision before merge |
| Else | ready to merge |

Optional: `cursorEval quality` / `dev` (needs `GITHUB_MODELS_TOKEN`).

## Verify

- [ ] All six modules run (see [references/modules.md](references/modules.md))
- [ ] Module 4 uses cursorEval metrics or notes unavailability
- [ ] **Result:** line present
