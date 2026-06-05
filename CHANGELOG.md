# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.15.0] - 2026-06-04

### Added

- Mandatory setup interview with progressive disclosure (`setup.depth`: simple / advanced / full).
- Extended interview schema (v0.5.0): personalization, agent batch, workspace scan tokens, `preferences.mdc`.
- `scripts/lifecycle/workspace_scan.py`, `preference_tokens.py`, `agent_customization.py`, `user_rules.py`.
- Post-configure optional **Cursor User Rules** step (`skills/cursorAssistantSetup/references/user-rules-step.md`).
- `inspect.interviewRequired`, `interviewDepth`, `setupAnswersCount`; setup evals (anti-silent-setup, anti-lockfile-replay).
- Interview fixtures: `tests/fixtures/interview-balanced.json`, `interview-advanced.json`, `interview-full.json`.
- [INTERVIEW_RESTORATION_PLAN.md](docs/project/INTERVIEW_RESTORATION_PLAN.md); MIGRATION.md § v0.14 and § v0.15.

### Changed

- **Breaking:** `setup` CLI deprecated (exit 2); `configure` requires explicit `--answers`; no lockfile replay.
- **Breaking:** `update` / `repair` blocked when `interviewRequired: true` without `--answers`.
- **Breaking:** lockfile `schemaVersion` 0.5.0; pre-0.5 workspaces must re-interview.
- Install page step 4: `/cursor-assistant:setup-workspace`, depth tiers, no silent install.
- `cursorLifecycle` reconfigure handoff table; `MODEL_PINNING.md` setup-interview appendix (team forks only).

### Removed

- `--no-interview`, `--yes` on configure, non-TTY configure without `--answers`, lockfile-as-answers seeding.

## [0.13.1] - 2026-06-04

### Added

- [MODEL_PINNING.md](docs/architecture/MODEL_PINNING.md) — agent `model: inherit` audit and optimal pinning policy.

### Changed

- Install website auto-publish via `publish-install-website.yml`; canonical host on asafelobotomy.github.io.

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
[0.15.0]: https://github.com/asafelobotomy/cursorassistant/compare/v0.13.1...v0.15.0
[0.13.1]: https://github.com/asafelobotomy/cursorassistant/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/asafelobotomy/cursorassistant/compare/v0.12.1...v0.13.0
[0.12.1]: https://github.com/asafelobotomy/cursorassistant/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/asafelobotomy/cursorassistant/compare/v0.11.0...v0.12.0
