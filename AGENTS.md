# Agent Routing (cursorAssistant)

Canonical routing for Cursor subagents in this package and in consumer workspaces after install.

Full design notes: [docs/architecture/ROUTING_AND_SUBAGENTS.md](docs/architecture/ROUTING_AND_SUBAGENTS.md).

## How routing works in Cursor

1. **`description` in each `.cursor/agents/*.md` file** — primary signal for automatic Task delegation.
2. **This file (`AGENTS.md`)** — parent-agent orchestration, built-ins, and handoffs.
3. **`.cursor/rules/core.mdc`** — always-on reinforcement (triage, Explore, tools).
4. **Skills** (`/name`) — procedures in parent context; not separate subagents.

Prefer **explicit** `/name` or **Task** when the wrong specialist would waste context. Prefer **no subagent** when `/task-triage` says Trivial or Simple.

## Built-in Cursor subagents

Cursor provides **Explore** (codebase search), **Bash** (shell), and **Browser** (web automation) automatically. Do not define a custom subagent named `explore` — it shadows the built-in.

| Need | Use |
| --- | --- |
| Broad parallel codebase search | Cursor built-in **Explore** |
| Verbose shell output isolated | Cursor built-in **Bash** |
| Browser / DOM work | Cursor built-in **Browser** |
| Structured repo inventory + handoff | **`inventory`** (`/inventory` or Task) |
| Unclear complexity before acting | **`/task-triage`** skill (not a subagent) |

## Core skills (invoke with `/name`)

| Skill | Use when |
| --- | --- |
| `task-triage` | Classify tier (Trivial→Blocked) and minimal path before subagents |
| `workspaceSearch` | Pick Grep vs SemanticSearch vs Glob |
| `ciPreflight` | Local CI before commit/push |
| `depSearch` | Dependency discovery and audit research |
| `testing` | Run project tests via Shell |
| `lifecycleAudit` | Before mutating managed `.cursor/` surfaces |
| `surfaceReview` | Before merging changes to agents, skills, or `.mdc` rules |
| `cursorAssistantSetup` | First project install after MCP bootstrap (interview → `configure` / `setup`) |

**Plugin command (user scope):** `/cursor-assistant:setup-workspace` — same flow as `cursorAssistantSetup`; requires plugin install or symlink from `install-from-github.sh`.

## Roster (11 subagents)

| Subagent | Invoke | Use when |
| --- | --- | --- |
| `cursorLifecycle` | `/cursorLifecycle` or Task | setup, inspect, update, repair managed Cursor surfaces |
| `inventory` | `/inventory` or Task | structured read-only maps, caller lists, architecture notes |
| `review` | `/review` or Task | code review, PR review, architecture review (background-capable) |
| `commit` | `/commit` or Task | git staging, commits, push, PRs, branches |
| `deps` | `/deps` or Task | dependency scan, audit, install, update |
| `docs` | `/docs` or Task | documentation authoring and doc quality checks |
| `debugger` | `/debugger` or Task | failing tests, broken commands, root-cause isolation |
| `planner` | `/planner` or Task | multi-step plans before large changes |
| `researcher` | `/researcher` or Task | external docs, upstream behavior, cited research (background-capable) |
| `organise` | `/organise` or Task | file moves, folder layout, path fixes after moves |
| `cleaner` | `/cleaner` or Task | prune caches, debris, stale artefacts (with approval) |

## Routing table

| Work type | Route |
| --- | --- |
| First-time project setup (after bootstrap) | `cursorAssistantSetup` skill, `/cursor-assistant:setup-workspace`, or `cursorLifecycle` (`configure`) |
| Install or update cursorAssistant surfaces | `cursorLifecycle` |
| Wide codebase search (parallel) | Cursor built-in **Explore** |
| Structured inventory before a change | `inventory` |
| Choose minimal execution path | `/task-triage` skill |
| Review diffs or architecture | `review` |
| Git commits, push, PRs, branches | `commit` (Shell / `gh`) |
| Dependency audit or package changes | `deps` |
| README, guides, migration docs | `docs` |
| Quality audit of agents/skills/rules before merge | `surfaceReview` skill |
| Diagnose failures with evidence | `debugger` |
| Phased implementation planning | `planner` |
| Source-backed external research | `researcher` |
| Structural moves and path repair | `organise` |
| Hygiene, caches, approved deletions | `cleaner` |

## Conflict resolution (pick one)

| Situation | Choose | Not |
| --- | --- | --- |
| Wide parallel “find anything about X” | Built-in **Explore** | `inventory` |
| Structured caller map before refactor | `inventory` | Explore |
| Write or update repo docs | `docs` | `researcher` |
| External docs with citations | `researcher` | `docs` |
| Install / audit / remove packages | `deps` | `researcher` |
| Prune caches / dead artifacts | `cleaner` | `organise` |
| Moves, renames, import path repair | `organise` | `cleaner` |
| Multi-file plan before coding | `planner` | main Agent only |
| Failing test or command (root cause) | `debugger` | `review`, `planner` |
| PR or diff review (no fixes) | `review` | `debugger` |
| Git commit / push / PR | `commit` | main Agent |
| Managed `.cursor/` / lockfile | `cursorLifecycle` | feature agents |

## Handoffs

Per-agent delegation chains live in [docs/architecture/ROUTING_AND_SUBAGENTS.md#handoff-rules](docs/architecture/ROUTING_AND_SUBAGENTS.md#handoff-rules) (not duplicated here).

**Slash-only skills** (use `/name`; not auto-invoked): `task-triage`, `lifecycleAudit`, `surfaceReview`, `cursorAssistantSetup`.

## Lifecycle trigger phrases

| Phrase | Route |
| --- | --- |
| `inspect workspace` | `cursorLifecycle` |
| `set up cursorAssistant` | `cursorAssistantSetup` or `cursorLifecycle` (`configure` / `setup`) |
| `update cursorAssistant` | `cursorLifecycle` |
| `health check` (install state) | `cursorLifecycle` |

Natural-language requests to add preferences to instructions are **not** lifecycle operations — use Cursor **User Rules** or project rules instead.
