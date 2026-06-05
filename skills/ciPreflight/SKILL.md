---
name: ciPreflight
description: "Use when: running pre-commit or pre-push CI-equivalent checks in any workspace — discovers workflow commands with Cursor tools, filters for local executability, scopes to staged changes, and runs checks cheapest-first."
version: "1.4"
license: MIT
paths:
  - ".github/workflows/**"
  - "**/package.json"
  - "**/pyproject.toml"
  - "Makefile"
---

# CI Preflight (Cursor)

Discover and run locally reproducible CI checks before commit or push. Use **Glob** and **Read** for workflows, **Shell** for git and commands, **AskQuestion** when user confirmation is required.

## When to use

- Before commit or push when CI coverage is unknown or may have changed
- Any language/framework workspace

## When NOT to use

- A project-specific preflight skill exists — prefer that
- User asked to skip verification
- Nothing staged and no proposed file list

## Module 1 — Discover and scope

### 0. Workflow files

**Glob** `.github/workflows/*.yml` and `.github/workflows/*.yaml`. **Read** each file.

**Keep** workflows whose `on:` includes `push` or `pull_request`. **Skip** schedule-only, deploy-only, or secret-only workflows.

### 1. Extract `run:` steps

Include self-contained local commands (`python3`, `npm test`, `make check`, `go test`, etc.).

**Omit** steps using `${{ secrets.* }}`, runner-only env, artifact upload/publish, or deploy/release tools.

### 2. Scope to staged changes

{{skill:ciPreflight:run-policy}}

**Shell:** `git diff --cached --name-only`. Narrow checks to staged ecosystems (e.g. skip Python lint if no `.py` staged).

### 3. Fallback

If no workflow steps apply, infer from project files:

| Signal | Command |
| --- | --- |
| `tests/` + `test_*.py` | `python3 -m unittest discover -s tests` |
| `pytest.ini` / `[tool.pytest]` | `python3 -m pytest` |
| `package.json` `test` script | `npm test` |
| `Makefile` `test` | `make test` |
| `go.mod` | `go test ./...` |
| `Cargo.toml` | `cargo test` |

If nothing credible, report that no local CI equivalent was found.

## Module 2 — Execute

Order: **lint/format → types → unit tests → integration** (skip expensive integration if out of scope).

| Outcome | Action |
| --- | --- |
| Exit 0 | Next check |
| Obvious generate step in output | Re-run generator, stage outputs, retry |
| Test/lint failure | Hand off to `debugger` with output + staged list; minimal fix; retry |
| Needs secrets/infra | Note in summary — not a local blocker |
| Other failure | Show stdout/stderr; **AskQuestion** if user must choose block vs risk |

## Summary

Return: workflows read, commands run, exclusions, pass / block / residual-risk.

## Verify

- [ ] Workflows read from disk, not assumed
- [ ] Staged files used for scoping
- [ ] Cheapest-first order; stopped at first blocker when appropriate
- [ ] Clear pass / block / residual-risk outcome
