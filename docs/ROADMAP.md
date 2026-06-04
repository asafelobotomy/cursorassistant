# Roadmap

> **Note:** Older sections below record historical names and counts (e.g. `explore`, `triage`, 12 agents). See **v0.10+** for the current roster.

## v0.1

- [x] Minimal lifecycle: `inspect`, `setup`, `update`
- [x] Core subagents: lifecycle, explore, review, debugger, planner
- [x] Core skills: testing, lifecycleAudit
- [x] Project rules templates (`.mdc`)
- [x] Empty `.cursor/mcp.json` scaffold

## v0.2

- [x] `repair` and `factory-restore`
- [x] Interview + `plan setup` (non-interactive JSON answers via `--answers`)
- [x] Merge-safe `AGENTS.md` and `mcp.json` apply
- [x] `scripts/generate.py` for manifest from policy

## v0.3

- [x] Pack registry (lean, secure, tdd)
- [x] Profile registry (`balanced`, `lean`)
- [x] MCP: `cursorTools` server wrapping lifecycle CLI

## v0.4

- [x] Shared MCP bundle (git, web, testing, memory, security, fs, time, devDocs) — later deprecated
- [x] `mcp.enabled` interview toggle
- [x] Core agents: commit, deps, docs
- [x] Core skills: workspaceSearch, ciPreflight, depSearch
- [x] Eval scaffold (`evals/`, `tools/cursorEval/`)

## v0.5

- [x] Full eval runner (`validate`, `check`, `coverage`, `grade`, `run`)
- [x] Cursor plugin manifest (`.cursor-plugin/plugin.json`)
- [x] External MCP script import workflow (removed in v0.11)

## v0.6

- [x] Shared MCP modules (`_cursor_workspace`, `_cursor_mcp_util`)
- [x] GitHub Actions CI (tests, manifest drift, cursorEval)
- [x] Eval workflow (validate + dry-run; optional Models run)
- [x] Plugin manifest validation (`scripts/validate_plugin.py`); marketplace guide archived under `docs/archive/`
- [x] Primary GitHub install (`scripts/install-from-github.sh`, README badge)

## v0.7

- [x] `cursor-mcp-shared` pip package (`packages/cursor-mcp-shared/`, `scripts/vendor_mcp_shared.py`)
- [x] Core agents: researcher, triage, organise, cleaner
- [x] Dogfooded `.cursor/` in package repo (`scripts/dogfood.sh`, committed install snapshot)
- [x] Eval scaffolds for new agents

## v0.8 — Cursor Canonical Phase A

- [x] Rename `explore` → `inventory`; document built-in Explore in `AGENTS.md`
- [x] Rewrite core skills for Cursor tools (`workspaceSearch`, `ciPreflight`, `depSearch`)
- [x] Rules: built-in subagents + Agent tools before MCP
- [x] Interview default `mcp.enabled: false`; conditions aligned
- [x] Catalog lists core agents (later: 11 after inventory rename)

## v0.9 — Cursor Canonical Phase B

- [x] Layered MCP manifests (`mcp-core`, `mcp-extensions`, `mcp-packs/*`)
- [x] Deprecate `web`, `filesystem`, `time` servers; move scripts to `_deprecated/`
- [x] Pack-scoped MCP install (secure, tdd, lean) + prune on deselect
- [x] `inspect` `mcpWarnings` for legacy servers/scripts
- [x] Agents/skills: Shell-first; MCP only when lockfile/pack enables it

## v0.10 — Cursor Canonical Phase C

- [x] Drop `git` MCP; use `commit` subagent + Shell/`gh`
- [x] `triage` subagent → **task-triage** skill; 11 core agents
- [x] `sanitize_mcp_config` on merge/update/repair for deprecated servers
- [x] Eval suites for `review`, `debugger`, `planner`
- [x] `cursorEval policy` — forbid VS Code tool names in skills
- [x] `scripts/dogfood-full.sh` (extensions + all packs)
- [x] `docs/HOOKS.md` (optional user-owned hooks)

## v0.10.1 — review remediation

- [x] Docs: `MIGRATION.md`, `ARCHITECTURE.md`, `SECURITY.md`, updated README
- [x] Evals for all 6 core skills; routing tasks for inventory/debugger
- [x] Agent delegation sections (`task-triage`, handoffs)
- [x] Relative lockfile `packageRoot` when package is workspace; catalog `git` deprecated
- [x] CI: policy + surface checks; evals workflow uses `GITHUB_MODELS_TOKEN`
- [x] Archive obsolete `mcp-bundle.json` / `mcp-minimal.json`

## v0.10.2 — eval and CI depth

- [x] Negative/routing eval tasks for core agents and skills; per-task grading in `cursorEval run`
- [x] PR **eval-models-pr** job (`evals/models-smoke`, 3 tasks; skips without token)
- [x] `cursorEval policy` scans `template/rules` and `.cursor/rules` (`.mdc`)

## v0.10.3 — audit remediation

- [x] Dogfood MCP complete; CI `check_dogfood_install.py`
- [x] Pack eval negative tasks (2 tasks per pack skill suite)
- [x] `ci_check_surfaces` includes pack skills
- [x] `.gitignore` `.cursorEval/`; README doc table; `cursorLifecycle` delegation deduped

## v0.11 (current) — Cursor-only product

- [x] Remove legacy external-tool coupling (comparison doc, sync script, dual IDE profiles)
- [x] `cursor-mcp-shared` Cursor-only workspace discovery
- [x] [MCP_MAINTENANCE.md](MCP_MAINTENANCE.md) replaces external sync guide

## v1.0+

- [ ] Stable 1.0 API for policy and lockfile schema
- [ ] Additional optional capability packs
