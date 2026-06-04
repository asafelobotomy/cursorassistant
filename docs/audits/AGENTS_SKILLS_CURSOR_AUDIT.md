# Agents & skills audit (Cursor optimization)

> **Snapshot (2026-06-03).** Several follow-ups are done since this audit (e.g. `cursorAssistantSetup` eval, **`surfaceReview`** skill, 8 core skills). For **current** routing and roster, use [ROUTING_AND_SUBAGENTS.md](../architecture/ROUTING_AND_SUBAGENTS.md).

Audit date: 2026-06-03. Scope: core `agents/`, `skills/`, `AGENTS.md`, install policy, plugin bundle, evals.

**Routing deep-dive:** [ROUTING_AND_SUBAGENTS.md](../architecture/ROUTING_AND_SUBAGENTS.md) (description-driven delegation, conflict matrix, eval hardening).

## Summary

| Area | Status |
| --- | --- |
| Built-in vs custom subagents | **Good** — no custom `explore`; built-in Explore/Bash/Browser documented |
| Cursor-native tools in agents/skills | **Good** — Read, Grep, Glob, SemanticSearch, Shell, WebSearch |
| Deprecated MCP (`filesystem`, `web`, `git`, `time`) | **Fixed** — `docs` agent no longer recommends filesystem |
| First-time setup routing | **Fixed** — `cursorAssistantSetup` in install policy + `AGENTS.md`; lifecycle triggers use `configure` |
| Read-only specialists | **Good** — `inventory`, `review`, `debugger`, `planner`, `researcher` use `readonly: true` |
| Eval coverage | **Good** — 11 agents + 6 core skills; no eval for `cursorAssistantSetup` (optional) |

## Built-in Cursor surfaces (do not shadow)

| Cursor provides | Use for |
| --- | --- |
| **Explore** | Broad parallel codebase search |
| **Bash** | Long/noisy shell isolated from main context |
| **Browser** | DOM / web automation |
| **Task** | Invoke roster subagents by name |

cursorAssistant intentionally does **not** ship a custom `explore` agent (would shadow the built-in).

## Core subagents (11)

| Agent | Cursor fit | Notes |
| --- | --- | --- |
| `cursorLifecycle` | Strong | CLI + cursorTools MCP; `configure` for cold start; delegates to lifecycleAudit |
| `inventory` | Strong | Read-only; explicit Explore vs inventory split; workspaceSearch |
| `review` | Strong | `readonly: true`; task-triage gate; **Tools** section added |
| `commit` | Strong | Shell / `gh`; user git-safety rules apply in main Agent |
| `deps` | Strong | Shell audits; secure pack MCP gated on lockfile |
| `docs` | Fixed | Was filesystem MCP → Read/Grep/Glob |
| `debugger` | Strong | `readonly: true`; **Tools** + **Delegation** sections added |
| `planner` | Strong | Read-only plans with verification steps |
| `researcher` | Strong | WebSearch/WebFetch; read-only |
| `organise` | Strong | Mutating by design; inventory/docs delegation |
| `cleaner` | Strong | Approval gates; delegates commit/docs |

**Invoke consistency:** All roster entries should list `/name` **or Task** — `deps` row in `AGENTS.md` was aligned.

## Core skills (7)

| Skill | Cursor fit | Installed to project via policy |
| --- | --- | --- |
| `task-triage` | Strong | Yes |
| `workspaceSearch` | Strong | Yes |
| `ciPreflight` | Strong | Yes |
| `depSearch` | Yes | Yes |
| `testing` | Strong | Yes |
| `lifecycleAudit` | Strong | Yes — now mentions `configure` |
| `cursorAssistantSetup` | Strong | **Yes (added)** — was in catalog only |

**User-scope only:** `/cursor-assistant:setup-workspace` from `.cursor-plugin/plugin.json` (`commands/setup-workspace.md`). Requires plugin symlink or marketplace install; complements project skill after bootstrap.

## Pack skills (optional)

Installed when user selects `lean`, `secure`, or `tdd` in interview. Patterns:

- Reference-type skills with OWASP/TDD content — appropriate for `/skill` invocation
- Cross-references (e.g. `secureReview` → `devopsReview`) assume pack presence — OK when pack selected
- Pack MCP tools (`security`, `workspaceTesting`) correctly gated in agent text

No pack skill changes required for this audit.

## Install & routing gaps fixed

1. **`cursorAssistantSetup`** added to `template/setup/install-policy.json` so `setup`/`configure` copies it to `.cursor/skills/`.
2. **`AGENTS.md`** — skill table, first-time routing row, lifecycle phrase → setup skill / `configure`.
3. **`cursorLifecycle`** trigger: not-installed → `configure` not bare `setup`.
4. **`docs.md`** — deprecated filesystem MCP removed.

## Evals (`evals/`)

| Covered | Missing (low priority) |
| --- | --- |
| All 11 agents (positive/negative triggers) | `cursorAssistantSetup` skill |
| Core skills except setup skill | Pack-only skills (by design) |
| `models-smoke` routing smoke | |

Evals validate **routing phrases**, not runtime tool execution — appropriate for static CI.

## Recommendations (not implemented)

| Item | Rationale |
| --- | --- |
| ~~Add `evals/cursorAssistantSetup/`~~ | Done — positive/negative setup routing tasks |
| `cursorAssistantSetup` — prefer bootstrap script over `curl\|bash` in skill | Align with INSTALL_SECURITY_AUDIT (doc-only) |
| Periodic sync check: `agents/` vs `.cursor/agents/` | Dogfood drift; run `update` after package edits |

## Verification

```sh
python3 scripts/generate.py
python3 -m pytest tests/test_engine.py tests/test_cursor_eval.py -q
python3 scripts/validate_plugin.py
```
