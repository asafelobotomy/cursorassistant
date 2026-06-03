# Agent Routing (cursorAssistant)

Canonical routing for Cursor subagents in this package and in consumer workspaces after install.

## Roster

| Subagent | Invoke | Use when |
| --- | --- | --- |
| `cursorLifecycle` | `/cursorLifecycle` or Task | setup, inspect, update, repair managed Cursor surfaces |
| `explore` | `/explore` or Task | read-only codebase exploration |
| `review` | `/review` or Task | code review, PR review, architecture review |
| `commit` | `/commit` or Task | git staging, commits, push, PRs, branches |
| `deps` | `/deps` or Task | dependency scan, audit, install, update |
| `docs` | `/docs` or Task | documentation authoring and doc quality checks |
| `debugger` | `/debugger` or Task | failing tests, broken commands, root-cause isolation |
| `planner` | `/planner` or Task | multi-step plans before large changes |

## Routing table

| Work type | Subagent |
| --- | --- |
| Install or update cursorAssistant surfaces | `cursorLifecycle` |
| Broad read-only exploration | `explore` |
| Review diffs or architecture | `review` |
| Git commits, push, PRs, branches | `commit` |
| Dependency audit or package changes | `deps` |
| README, guides, migration docs | `docs` |
| Diagnose failures with evidence | `debugger` |
| Phased implementation planning | `planner` |

## Handoff rules

- `cursorLifecycle` may delegate to `explore` for inventory and `planner` for phased remediation.
- `commit` may delegate to `review` before merge and `debugger` when hooks fail.
- `deps` confirms before mutating installed packages; hand off test failures to `debugger`.
- `docs` may delegate to `explore` for accuracy and `review` for quality passes.
- `debugger` stays read-only; hand off implementation to the main Agent after diagnosis.
- `planner` stays read-only; returns an executable plan with file list and verification steps.
- `review` may delegate to `debugger` when a finding needs reproduction.

## Lifecycle trigger phrases

| Phrase | Route |
| --- | --- |
| `inspect workspace` | `cursorLifecycle` |
| `set up cursorAssistant` | `cursorLifecycle` |
| `update cursorAssistant` | `cursorLifecycle` |
| `health check` (install state) | `cursorLifecycle` |

Natural-language requests to add preferences to instructions are **not** lifecycle operations — use Cursor **User Rules** or project rules instead.
