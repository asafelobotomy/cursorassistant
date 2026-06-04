---
name: task-triage
description: Use when task complexity is unclear — classify as Trivial, Simple, Compound, Complex, or Blocked and recommend the minimal path before spawning subagents.
disable-model-invocation: true
---

# Task triage (Cursor)

Classify work before choosing subagents or a large implementation pass. Prefer this skill over a dedicated triage subagent.

## When to use

- The user asks what approach to take, or scope feels ambiguous
- Before invoking `planner` or multiple specialists
- When unsure if built-in **Explore** vs `inventory` vs main Agent is enough

## When NOT to use

- User already chose a path ("just fix the test", "open a PR")
- Single obvious tool call (one Grep, one file edit)

## Tiers

| Tier | Description | Path |
| --- | --- | --- |
| **Trivial** | One lookup or trivial edit | Answer in-chat |
| **Simple** | Few files, one approach | Main Agent |
| **Compound** | Multiple files or approaches | `planner` then implement |
| **Complex** | Migration, subsystem, unclear reqs | `planner` + specialists |
| **Blocked** | Missing info or unconfirmed destructive work | Stop; list blockers |

## Output

```text
Tier: <tier>
Scope: <one line>
Approach: <path>
Blockers: <none | details>
```

Do not over-classify: three related files with one pattern is **Simple**, not **Complex**.

## Parallel work (Compound or Complex only)

Before **two or more** Task subagents:

1. Write a **scope ledger**: parent goal, paths each agent may touch, paths forbidden, proof command (test/lint).
2. **Disjoint paths** — never parallel-edit the same file.
3. After merge, review **interfaces** between scopes (imports, shared types, AGENTS routing).

See [references/parallel-scope.md](references/parallel-scope.md) for a template.

## Route to (after tier is set)

| Need | Route |
| --- | --- |
| Wide parallel codebase search | Built-in **Explore** |
| Structured inventory / caller map | `inventory` |
| External cited research | `researcher` |
| Repo docs (README, guides) | `docs` |
| Packages / CVE / install | `deps` |
| PR or diff review | `review` |
| Test or command failure | `debugger` |
| Plan before multi-file work | `planner` |
| Moves / layout | `organise` |
| Hygiene / prune | `cleaner` |
| Git / PR | `commit` |
| `.cursor/` lifecycle | `cursorLifecycle` or **cursorAssistantSetup** |
| Search method unclear | **workspaceSearch** skill |
| CI before push | **ciPreflight** skill |

If two rows seem to fit, use the **Conflict resolution** table in `AGENTS.md`.
