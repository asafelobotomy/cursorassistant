# surfaceReview — module reference

Load this file when executing `/surfaceReview`. Parent `SKILL.md` defines order and output format.

## Module 1 — Contradiction detection

Rate risk: **Low / Medium / High / Critical**. Look for: overlapping When to use / When NOT; body vs YAML `description`; steps that undo prior postconditions; conflict with `AGENTS.md` roster.

**Output:** `contradiction: [severity] <section> — <description>. Suggested fix: <fix>`

## Module 2 — Semantic ambiguity

Score **Clarity** 0–1; ≤ 0.5 → High. Vague verbs, undefined referents, implicit prerequisites, unqualified always/never.

**Output:** `ambiguity: [severity] <section> — <description>. Suggested rewrite: <rewrite>`

## Module 3 — Persona consistency

Rate: **Stable / Drifting / Conflicted**. Voice drift, tone shifts, conflicting style, multiple roles, description vs body mismatch.

**Output:** `persona: [severity] <section> — <description>. Suggested fix: <fix>`

## Module 4 — Cognitive load

```sh
python3 tools/cursorEval/cursorEval.py check <path>
python3 tools/cursorEval/cursorEval.py tokens <path>
```

| Metric | Warning | Block |
| --- | --- | --- |
| Nesting depth | > 2 | > 3 |
| Rules per section | > 7 | > 10 |
| Steps per sequence | > 8 | > 12 |

SKILL advisories: `complexity` (block), `module-count`, `eval-presence` (medium).

**Output:** `cognitive-load: [warning|block] <section> — <metric> = <value> (threshold: <t>). Suggested fix: <fix>`

## Module 5 — Semantic coverage

**Completeness:** Complete / Gaps-present / Incomplete. Emit `scope-coverage: [well-defined | bleeding] — <text>` after module 5 rows.

All types: happy path, failure path, When NOT to use, dep failure notes, workflow termination.

Agents: handoffs, no custom `explore`, `AGENTS.md` alignment. Skills: `## Verify`, cursorEval spec gaps, eval-presence. Rules: justified `alwaysApply`, imperative rules.

**Output:** `coverage-gap: [severity] <section> — <description>. Suggested addition: <addition>`

## Module 6 — Composition

Resolve imports (links, AGENTS.md, pack tokens). Compare pairs: contradiction, shadowing, drift, cycles.

**Output:** `composition: [severity] <parent> ↔ <import> — <description>. Suggested resolution: <resolution>`
