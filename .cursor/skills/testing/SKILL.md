---
name: testing
description: Use when running workspace tests, choosing a test command, or summarizing results before handoff to debugger.
---

# Testing (Cursor)

Run tests through the workspace's declared command or MCP test tools when available.

## When to use

- Validate a change with targeted or full tests
- Discover the project's test entrypoint instead of guessing

## When not to use

- Root-cause analysis of failures → `debugger`
- Full CI pre-merge gate → run the repo's CI script locally if present
- Strict TDD coaching when a TDD pack is installed (future)

## Process

1. Find `package.json`, `pyproject.toml`, `Makefile`, or README for the canonical test command.
2. Run the smallest command that covers the changed area.
3. Summarize pass/fail; on failure, hand off to `debugger` with logs.

Prefer **workspaceTesting** MCP tools when connected; otherwise use the terminal.
