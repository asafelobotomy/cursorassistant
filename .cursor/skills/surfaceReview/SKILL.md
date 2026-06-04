---
name: surfaceReview
description: "Use when: reviewing agents/*.md, skills/*/SKILL.md, or .mdc rules for contradictions, ambiguity, persona drift, cognitive load, coverage gaps, and composition conflicts before merge."
version: "1.0"
license: MIT
---

# Surface review

Systematic quality review of Cursor instruction surfaces managed by cursorAssistant. Run all six modules in sequence; each produces zero or more labelled findings. Collect every finding before returning the summary.

Use **Read**, **Grep**, and **Glob** to load the target file and any imports. Use **Shell** for `cursorEval` metrics when the package root contains `tools/cursorEval/cursorEval.py`.

## When to use

- Before merging changes to `agents/*.md`, `skills/*/SKILL.md`, `template/rules/*.mdc`, or installed `.cursor/rules/*.mdc`
- When a skill or subagent behaves unexpectedly and the cause may be instruction quality
- When asked to audit, review, or improve a Cursor surface file (not application source code)

## When NOT to use

- **Code or PR review** — use the **review** subagent (`/review` or Task)
- **Authoring a new surface from scratch** — edit using project conventions, then run this skill before commit
- **YAML frontmatter syntax only** — fix syntax directly
- **Lifecycle install drift** — use **lifecycleAudit** or **cursorLifecycle** first

## Surface paths (cursorAssistant)

| Kind | Typical path |
| --- | --- |
| Subagent | `agents/<name>.md` → `.cursor/agents/<name>.md` |
| Skill | `skills/<name>/SKILL.md` → `.cursor/skills/<name>/SKILL.md` |
| Rule | `template/rules/*.mdc` → `.cursor/rules/*.mdc` |
| Routing | `AGENTS.md` (orchestration, not a skill body) |

---

## Module 1 — Contradiction detection

Identify directives that produce conflicting instructions when applied together.

Rate overall contradiction risk: **Low / Medium / High / Critical**.

**What to look for:**

- Positive rule followed by negative rule on the same condition
- "When to use" and "When NOT to use" ranges that overlap
- Body text that contradicts YAML `description` routing
- Step sequences where a later step undoes a prior postcondition
- Rules that conflict with `AGENTS.md` roster for the same trigger

**Severity:**

| Type | Severity |
| --- | --- |
| Behavioral (must act vs must not act) | Critical |
| Scope or tool constraint | High |
| When to use / When NOT overlap | Medium |
| Minor ordering inconsistency | Low |

**Output:** `contradiction: [severity] <section> — <description>. Suggested fix: <fix>`

---

## Module 2 — Semantic ambiguity

Find directives that lack a precise, observable definition.

Score overall **Clarity** 0–1 (1 = all directives precisely actionable). ≤ 0.5 → treat as High severity.

**What to look for:**

- Vague verbs: "handle appropriately", "be careful", "as needed"
- Undefined referents ("it", "the result") without antecedent
- Implicit prerequisites never established in the file
- "Always" / "never" without stated exceptions

**Output:** `ambiguity: [severity] <section> — <description>. Suggested rewrite: <rewrite>`

---

## Module 3 — Persona consistency

Verify coherent identity and tone throughout.

Rate persona stability: **Stable / Drifting / Conflicted**.

**What to look for:**

- Voice drift (I / you / the agent) without convention
- Tone register shifts (formal vs casual)
- Conflicting style ("be concise" vs "explain in detail")
- Multiple named roles in one agent file
- Subagent `description` that does not match body boundaries

**Output:** `persona: [severity] <section> — <description>. Suggested fix: <fix>`

---

## Module 4 — Cognitive load assessment

Warn when structural complexity makes reliable execution unlikely.

**Metrics (from repo root when cursorEval is available):**

```sh
python3 tools/cursorEval/cursorEval.py check <path>
python3 tools/cursorEval/cursorEval.py tokens <path>
```

Use `max_nesting_depth`, `code_blocks`, compliance tier, and advisory flags from `check`. If cursorEval is unavailable, estimate by inspection.

| Metric | Warning | Block |
| --- | --- | --- |
| Conditional nesting depth | > 2 | > 3 |
| Rules per section | > 7 | > 10 |
| Steps in one sequence | > 8 | > 12 |
| Repeated constraints across sections | 3+ | 5+ |

**cursorEval advisories (SKILL.md):**

| Flag | Level |
| --- | --- |
| `complexity` | block |
| `module-count` | warning |
| `over-specificity` | warning |
| `procedural-content` | low |
| `eval-presence` | medium |

Emit `cognitive-load: warning` or `cognitive-load: block` with metric, value, and threshold.

**Output:** `cognitive-load: [warning|block] <section> — <metric> = <value> (threshold: <t>). Suggested fix: <fix>`

---

## Module 5 — Semantic coverage

Identify gaps between stated intent and documented behavior.

Rate **Completeness**: **Complete / Gaps-present / Incomplete**.

Emit standalone line after module rows: `scope-coverage: [well-defined | bleeding] — <description>`

**Checklist (all surface types):**

- [ ] Clear happy path from trigger to completion
- [ ] At least one failure or error path
- [ ] "When NOT to use" (required for skills; recommended for agents)
- [ ] External deps (other agents, MCP) have failure or fallback notes
- [ ] Multi-step workflows define termination on the last step

**Agent files (`agents/*.md`):**

- [ ] Handoffs for scope-unclear, failure, and out-of-domain cases
- [ ] No custom agent named `explore` (shadows Cursor built-in Explore)
- [ ] Delegation matches `AGENTS.md` roster

**Skill files (`SKILL.md`):**

- [ ] `## Verify` checklist present
- [ ] `cursorEval check` spec failures reported as coverage-gap (High for `spec-frontmatter`, `spec-name`, `spec-dir-match`)
- [ ] Missing eval suite → Medium (`eval-presence`); suggest `cursorEval suggest <path>`

**Rule files (`.mdc`):**

- [ ] `alwaysApply` or globs are justified; rules are imperative ("Do X")

**Output:** `coverage-gap: [severity] <section> — <description>. Suggested addition: <addition>`

---

## Module 6 — Composition conflict analysis

Detect conflicts between the file under review and files it references.

**Step 1 — Imports:** markdown links, `AGENTS.md` references, pack tokens, related skills/agents named in body. **Read** each resolved path; unresolved → `composition: [high] import unresolved — <path>`.

**Step 2 — Compare pairs:** direct contradiction, shadowing, duplicate drift, circular reference, pack vs body conflict.

**Output:** `composition: [severity] <parent> ↔ <import> — <description>. Suggested resolution: <resolution>`

---

## Finding output format

Consolidated table after all six modules:

| Severity | Module | Section | Finding | Suggested fix |
| --- | --- | --- | --- | --- |
| … | … | … | … | … |

Severity labels: **Critical**, **High**, **Medium**, **Low**. Zero findings in a module → one row: `— | <module> | — | No findings. | —`.

Emit `scope-coverage:` as a standalone line after Module 5 rows (not in the table).

Close with:

> **Result:** `N` critical, `N` high, `N` medium, `N` low — [ready to merge | needs revision before merge | block: restructure required]

| Outcome | Rule |
| --- | --- |
| Any Critical | **block: restructure required** |
| Any High | **needs revision before merge** |
| Medium or lower only | **ready to merge** (suggestions noted) |

Optional follow-up when scores are low: `cursorEval quality <path>` or `cursorEval dev <path>` (requires `GITHUB_MODELS_TOKEN`).

---

## Verify

- [ ] All six modules run; each has at least a "no findings" row
- [ ] Module 4: cursorEval `tokens`/`check` used or unavailability noted
- [ ] SKILL.md: spec violations in coverage-gap findings
- [ ] Composition: linked files read before conflict findings
- [ ] Ambiguity rows include rewrite suggestions
- [ ] Cognitive-load rows include metric and threshold
- [ ] Findings table closes with **Result:** merge decision line
