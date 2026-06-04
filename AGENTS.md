# Agent Routing (cursorAssistant)

Canonical routing for Cursor subagents. Design detail: [docs/architecture/ROUTING_AND_SUBAGENTS.md](docs/architecture/ROUTING_AND_SUBAGENTS.md).

**Layers:** agent `description` (auto Task) → this file → `core.mdc` → skills (`/name`). Use explicit `/name` or **Task** when mis-routing wastes context; skip subagents when `/task-triage` is Trivial or Simple.

## Built-ins

Never add a custom `explore` agent (shadows the built-in).

| Need | Use |
| --- | --- |
| Parallel codebase search | **Explore** |
| Noisy shell | **Bash** |
| Browser / DOM | **Browser** |
| Structured inventory | `inventory` |
| Unclear complexity | `/task-triage` |

## Core skills (`/name`)

| Skill | Use when |
| --- | --- |
| `task-triage` | Tier + path before subagents |
| `workspaceSearch` | Grep vs SemanticSearch vs Glob |
| `ciPreflight` | Local CI before commit/push |
| `depSearch` | Dep discovery/CVE research (slash-only) |
| `testing` | Run project tests |
| `lifecycleAudit` | Before `.cursor/` mutations |
| `surfaceReview` | Agents/skills/rules before merge |
| `cursorAssistantSetup` | First project install |

Plugin `/cursor-assistant:setup-workspace` = setup skill (requires plugin install).

**Slash-only:** `task-triage`, `lifecycleAudit`, `surfaceReview`, `cursorAssistantSetup`, `depSearch`. **Auto-invoke:** `workspaceSearch`, `ciPreflight`, `testing` only.

## Roster (11 subagents)

| Subagent | Invoke | Use when |
| --- | --- | --- |
| `cursorLifecycle` | `/cursorLifecycle` or Task | setup, inspect, update, repair `.cursor/` |
| `inventory` | `/inventory` or Task | read-only maps, callers, architecture notes |
| `review` | `/review` or Task | code/PR/architecture review (background) |
| `commit` | `/commit` or Task | git, push, PRs (`gh`) |
| `deps` | `/deps` or Task | package install/audit/update |
| `docs` | `/docs` or Task | repo documentation |
| `debugger` | `/debugger` or Task | failing tests, broken commands |
| `planner` | `/planner` or Task | multi-step plans |
| `researcher` | `/researcher` or Task | external cited research (background) |
| `organise` | `/organise` or Task | moves, layout, import paths |
| `cleaner` | `/cleaner` or Task | caches, debris (with approval) |

## Routing table

| Work type | Route |
| --- | --- |
| First-time setup | `cursorAssistantSetup`, `/cursor-assistant:setup-workspace`, or `cursorLifecycle` |
| Install/update surfaces | `cursorLifecycle` |
| Wide search | **Explore** |
| Caller map before refactor | `inventory` |
| Minimal path | `/task-triage` |
| Diff/PR review | `review` |
| Git / PR | `commit` |
| Package changes | `deps` |
| Repo docs | `docs` |
| Instruction-surface QA | `surfaceReview` |
| Root-cause failures | `debugger` |
| Phased planning | `planner` |
| External research | `researcher` |
| Moves / paths | `organise` |
| Hygiene | `cleaner` |

## Conflict resolution

| Situation | Choose | Not |
| --- | --- | --- |
| Wide “find X” | **Explore** | `inventory` |
| Caller map | `inventory` | Explore |
| Repo docs | `docs` | `researcher` |
| External citations | `researcher` | `docs` |
| Package mutate | `deps` | `researcher` |
| Prune artifacts | `cleaner` | `organise` |
| Moves / imports | `organise` | `cleaner` |
| Plan before code | `planner` | main Agent only |
| Test failure RCA | `debugger` | `review`, `planner` |
| PR review only | `review` | `debugger` |
| Git operations | `commit` | main Agent |
| `.cursor/` / lockfile | `cursorLifecycle` | feature agents |

## Handoffs

See [handoff rules](docs/architecture/ROUTING_AND_SUBAGENTS.md#handoff-rules) (not duplicated here).

## Lifecycle phrases

| Phrase | Route |
| --- | --- |
| `inspect workspace` | `cursorLifecycle` |
| `set up cursorAssistant` | `cursorAssistantSetup` or `cursorLifecycle` |
| `update cursorAssistant` | `cursorLifecycle` |
| `health check` (install) | `cursorLifecycle` |

Preference changes → Cursor **User Rules**, not lifecycle.
