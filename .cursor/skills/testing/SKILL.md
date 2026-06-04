---
name: testing
description: Use when running workspace tests, choosing a test command, or summarizing results before handoff to debugger.
---

# Testing (Cursor)

Run tests through the project's declared command. Prefer **Shell**; use pack MCP tools only when installed.

## When to use

- Validate a change with targeted or full tests
- Discover the project's test entrypoint instead of guessing

## When not to use

- Root-cause analysis of failures → `debugger`
- Full CI pre-merge gate → **ciPreflight** skill
- Strict TDD coaching when the **tdd** pack is installed → pack skills (`tddCycle`, etc.)

## Process

1. **Glob** / **Read** `package.json`, `pyproject.toml`, `Makefile`, or README for the canonical test command.
2. Run the smallest **Shell** command that covers the changed area.
3. Summarize pass/fail; on failure, hand off to `debugger` with logs.

## Pack MCP (optional)

When the **tdd** pack is installed, `workspaceTesting` or `tddTestRunner` may appear in `.cursor/mcp.json`. Use them for structured runner discovery; otherwise stay on **Shell**.

## Verify

- [ ] Test command taken from project manifests or README (not guessed)
- [ ] Smallest relevant test scope run first
- [ ] Pass/fail summarized; failures handed to `debugger` with logs
