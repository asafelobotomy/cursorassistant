# Roadmap

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

- [x] Shared MCP bundle ported from xanad (git, web, testing, memory, security, fs, time, devDocs)
- [x] `mcp.enabled` interview toggle
- [x] Core agents: commit, deps, docs
- [x] Core skills: workspaceSearch, ciPreflight, depSearch
- [x] Eval scaffold (`evals/`, `tools/cursorEval/`)

## v0.5

- [x] Full eval runner (`validate`, `check`, `coverage`, `grade`, `run`)
- [x] Cursor plugin manifest (`.cursor-plugin/plugin.json`)
- [x] MCP sync script (`scripts/sync_mcp_from_xanad.py`)

## v0.6

- [x] Shared MCP modules (`_cursor_workspace`, `_cursor_mcp_util`)
- [x] GitHub Actions CI (tests, manifest drift, cursorEval)
- [x] Eval workflow (validate + dry-run; optional Models run)
- [x] Marketplace publish guide (`docs/PUBLISH.md`, `scripts/validate_plugin.py`)

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
- [x] Catalog lists all 12 agents; scrub xanad strings in `webMcp.py`

## v0.9 (current) — Cursor Canonical Phase B

- [x] Layered MCP manifests (`mcp-core`, `mcp-extensions`, `mcp-packs/*`)
- [x] Deprecate `web`, `filesystem`, `time` servers; move scripts to `_deprecated/`
- [x] Pack-scoped MCP install (secure, tdd, lean) + prune on deselect
- [x] `inspect` `mcpWarnings` for legacy servers/scripts
- [x] Agents/skills: Shell-first; MCP only when lockfile/pack enables it

## v1.0+

- [ ] xanadAssistant consumes `cursor-mcp-shared` as a dependency
- [ ] Additional skills from xanad as optional packs
