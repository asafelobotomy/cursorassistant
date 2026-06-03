# Agent Routing (cursorAssistant)

Canonical routing for Cursor subagents in this package and in consumer workspaces after install.

## Built-in Cursor subagents

Cursor provides **Explore** (codebase search), **Bash** (shell), and **Browser** (web automation) automatically. Do not define a custom subagent named `explore` — it shadows the built-in.

| Need | Use |
| --- | --- |
| Broad parallel codebase search | Cursor built-in **Explore** |
| Verbose shell output isolated | Cursor built-in **Bash** |
| Browser / DOM work | Cursor built-in **Browser** |
| Structured repo inventory + handoff | **`inventory`** (`/inventory` or Task) |

## Roster

| Subagent | Invoke | Use when |
| --- | --- | --- |
| `cursorLifecycle` | `/cursorLifecycle` or Task | setup, inspect, update, repair managed Cursor surfaces |
| `inventory` | `/inventory` or Task | structured read-only maps, caller lists, architecture notes |
| `review` | `/review` or Task | code review, PR review, architecture review |
| `commit` | `/commit` or Task | git staging, commits, push, PRs, branches |
| `deps` | `/deps` or Task | dependency scan, audit, install, update |
| `docs` | `/docs` or Task | documentation authoring and doc quality checks |
| `debugger` | `/debugger` or Task | failing tests, broken commands, root-cause isolation |
| `planner` | `/planner` or Task | multi-step plans before large changes |
| `researcher` | `/researcher` or Task | external docs, upstream behavior, cited research |
| `triage` | `/triage` or Task | complexity classification before choosing a path |
| `organise` | `/organise` or Task | file moves, folder layout, path fixes after moves |
| `cleaner` | `/cleaner` or Task | prune caches, debris, stale artefacts (with approval) |

## Routing table

| Work type | Subagent |
| --- | --- |
| Install or update cursorAssistant surfaces | `cursorLifecycle` |
| Wide codebase search (parallel) | Cursor built-in **Explore** |
| Structured inventory before a change | `inventory` |
| Review diffs or architecture | `review` |
| Git commits, push, PRs, branches | `commit` |
| Dependency audit or package changes | `deps` |
| README, guides, migration docs | `docs` |
| Diagnose failures with evidence | `debugger` |
| Phased implementation planning | `planner` |
| Source-backed external research | `researcher` |
| Choose minimal execution path | `triage` |
| Structural moves and path repair | `organise` |
| Hygiene, caches, approved deletions | `cleaner` |

## Handoff rules

- `cursorLifecycle` may delegate to `inventory` for layout maps and `planner` for phased remediation.
- `commit` may delegate to `review` before merge and `debugger` when hooks fail.
- `deps` confirms before mutating installed packages; hand off test failures to `debugger`.
- `docs` may delegate to `inventory` for accuracy and `review` for quality passes.
- `debugger` stays read-only; hand off implementation to the main Agent after diagnosis.
- `planner` stays read-only; returns an executable plan with file list and verification steps.
- `review` may delegate to `debugger` when a finding needs reproduction.
- `triage` hands Compound/Complex work to `planner`; does not replace specialists.
- `researcher` stays read-only; hand off implementation to the main Agent or `planner`.
- `organise` may delegate to `inventory` for caller maps and `docs` for migration docs.
- `cleaner` may delegate to `review`, `organise`, `docs`, and `commit` per scope.

## Lifecycle trigger phrases

| Phrase | Route |
| --- | --- |
| `inspect workspace` | `cursorLifecycle` |
| `set up cursorAssistant` | `cursorLifecycle` |
| `update cursorAssistant` | `cursorLifecycle` |
| `health check` (install state) | `cursorLifecycle` |

Natural-language requests to add preferences to instructions are **not** lifecycle operations — use Cursor **User Rules** or project rules instead.
