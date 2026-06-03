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

## v0.5 (current)

- [x] Full eval runner (`validate`, `check`, `coverage`, `grade`, `run`)
- [x] Cursor plugin manifest (`.cursor-plugin/plugin.json`)
- [x] MCP sync script (`scripts/sync_mcp_from_xanad.py`)

## v0.6+

- [ ] Shared MCP Python library with xanadAssistant
- [ ] Marketplace publication workflow
- [ ] GitHub Models CI for eval suites
