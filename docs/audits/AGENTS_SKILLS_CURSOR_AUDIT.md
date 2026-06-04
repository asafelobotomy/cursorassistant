# Agents & skills audit (Cursor optimization)

> **Updated 2026-06-04 (v0.13.0).** For live roster and delegation, use [ROUTING_AND_SUBAGENTS.md](../architecture/ROUTING_AND_SUBAGENTS.md) and root `AGENTS.md`.

Audit scope: core `agents/`, `skills/`, `AGENTS.md`, install policy, plugin bundle, evals.

## Summary

| Area | Status |
| --- | --- |
| Built-in vs custom subagents | **Good** — no custom `explore`; Explore/Bash/Browser documented |
| Cursor-native tools | **Good** — Read, Grep, Glob, SemanticSearch, Shell, WebSearch |
| Deprecated MCP | **Good** — `web`, `filesystem`, `time`, `git` stripped on update |
| First-time setup | **Good** — `cursorAssistantSetup` in policy + evals |
| Read-only specialists | **Good** — `inventory`, `review`, `debugger`, `planner`, `researcher` |
| Eval coverage | **Good** — 11 agents + 8 core skills; `coverage --strict` 31/31 full |
| Performance scoping | **Good** — 3 auto-invoke skills; 5 slash-only (incl. `depSearch`) |

## Core skills (8)

| Skill | Installed | Scoping |
| --- | --- | --- |
| `task-triage` | Yes | slash-only |
| `workspaceSearch` | Yes | auto-invoke |
| `ciPreflight` | Yes | auto-invoke + `paths` |
| `depSearch` | Yes | slash-only (v0.13.0+) |
| `testing` | Yes | auto-invoke |
| `lifecycleAudit` | Yes | slash-only + `paths` |
| `surfaceReview` | Yes | slash-only + `paths`; `references/modules.md` |
| `cursorAssistantSetup` | Yes | slash-only + `paths` |

User-scope: `/cursor-assistant:setup-workspace` (plugin command).

## Core subagents (11)

| Agent | Notes |
| --- | --- |
| `cursorLifecycle` | CLI + cursorTools MCP; `configure` for cold start |
| `inventory` | Read-only; Explore vs inventory split |
| `review` | `readonly`, `is_background` |
| `commit` | Shell/`gh`; surfaceReview before managed commits |
| `deps` | Mutating packages with confirmation |
| `docs` | Repo documentation |
| `debugger` | Read-only RCA |
| `planner` | Read-only plans |
| `researcher` | Read-only, `is_background` |
| `organise` | Moves and import repair |
| `cleaner` | Hygiene with approval |

## Evals

| Covered | Detail |
| --- | --- |
| All 11 agents | positive-trigger-1/2, negative-trigger-1 |
| All 8 core skills | incl. `cursorAssistantSetup`, `surfaceReview` guardrails |
| Conflict routing | `evals/models-smoke` |
| Pack skills | 12 skills, 3 tasks each (strict coverage) |

Evals test **routing phrases**, not runtime tool execution — appropriate for CI.

## Verification

```sh
python3 scripts/check_package_sync.py
python3 tools/cursorEval/cursorEval.py validate
python3 tools/cursorEval/cursorEval.py coverage --strict
bash scripts/ci_check_surfaces.sh
```

See [FULL_AUDIT_2026-06-04.md](FULL_AUDIT_2026-06-04.md) for the complete v0.13 audit snapshot.
