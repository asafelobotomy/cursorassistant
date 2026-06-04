# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.13.0] - 2026-06-04

### Added

- Skill scoping (`disable-model-invocation`, `paths`) on slash-only and CI skills; `PERFORMANCE.md` and phased plan docs.
- `surfaceReview` reference modules; `task-triage` parallel scope reference; routing eval guardrails.
- Optional hooks template (`template/hooks/`) and [CURSOR_AUTOMATIONS.md](docs/guides/CURSOR_AUTOMATIONS.md).
- Install-policy entries for skill `references/` files.

### Changed

- `surfaceReview` SKILL compressed (~600 tokens); handoffs moved from `AGENTS.md` to routing doc.
- `generate.py` derives `catalog.agents` from `install-policy.json`.
- `cursorEval` allows `paths`, `globs`, and `disable-model-invocation` in skill frontmatter.
- Package maintainer sync checklist in `commit` agent.

## [0.12.1] - 2026-06-03

### Added

- [ROUTING_AND_SUBAGENTS.md](docs/architecture/ROUTING_AND_SUBAGENTS.md) and [AGENTS_SKILLS_CURSOR_AUDIT.md](docs/audits/AGENTS_SKILLS_CURSOR_AUDIT.md).
- Conflict-resolution matrix in `AGENTS.md`; routing table in `task-triage` skill.
- `cursorAssistantSetup` skill in install policy; models-smoke routing conflict eval tasks.

### Changed

- Subagent `description` fields tuned for Cursor auto-delegation (proactive review/debugger, negative boundaries).
- Agent positive eval tasks use concrete prompts and `expected` routing targets.
- `lifecycleAudit` and `cursorLifecycle` prefer `configure` for cold start.

## [0.12.0] - 2026-06-04

### Added

- `configure` and `interview` CLI commands; optional `--package-root` auto-detection.
- GitHub-first install: `install-from-github.sh`, `bootstrap-from-github.sh`, setup page (`install/`).
- `lifecycle_configure` MCP tool; `cursorAssistantSetup` skill and `setup-workspace` command.
- Install security audit and git-only MCP bootstrap via `mcp-launch.sh`.

### Changed

- Primary distribution is GitHub (marketplace docs archived).
- README install badge links to HTTPS setup page with `cursor://` MCP deeplink.

## [0.11.0] - 2026-05-01

### Changed

- Cursor-only product focus; removed XANAD coupling and related docs/scripts.

## [0.10.3] - 2026-04-28

### Fixed

- Dogfood MCP install; pack eval negatives; CI surface checks for pack skills.

## [0.10.2] - 2026-04-25

### Added

- Richer evals; PR Models smoke workflow.

## [0.10.1] - 2026-04-22

### Added

- Architecture, migration, and security documentation updates.
- Evals for all core skills; agent delegation wiring.

## [0.10.0] - 2026-04-18

### Changed

- Dropped git MCP and triage subagent; added task-triage skill.
- MCP sanitization on merge/update; relative lockfile `packageRoot`.

### Added

- `cursorEval` policy; dogfood-full script; hooks documentation.

## [0.9.0] - 2026-04-01

### Added

- Layered MCP layout; Cursor-first skills; inventory agent.

[0.11.0]: https://github.com/asafelobotomy/cursorassistant/compare/v0.10.3...v0.11.0
[0.10.3]: https://github.com/asafelobotomy/cursorassistant/compare/v0.10.2...v0.10.3
[0.10.2]: https://github.com/asafelobotomy/cursorassistant/compare/v0.10.1...v0.10.2
[0.10.1]: https://github.com/asafelobotomy/cursorassistant/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/asafelobotomy/cursorassistant/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/asafelobotomy/cursorassistant/releases/tag/v0.9.0
[0.13.0]: https://github.com/asafelobotomy/cursorassistant/compare/v0.12.1...v0.13.0
[0.12.1]: https://github.com/asafelobotomy/cursorassistant/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/asafelobotomy/cursorassistant/compare/v0.11.0...v0.12.0
