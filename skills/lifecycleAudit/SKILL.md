---
name: lifecycleAudit
description: Use before proposing cursorAssistant setup, update, or repair — inspect lockfile and managed file drift.
disable-model-invocation: true
paths:
  - ".cursor/**"
  - "AGENTS.md"
  - "cursorAssistant.py"
  - "template/setup/**"
---

# Lifecycle audit

Read-only check of cursorAssistant install state before mutating managed surfaces.

## When to use

- Before proposing `configure`, `setup`, `update`, or `repair` on managed Cursor surfaces
- When `installState` or lockfile integrity is unclear

## When not to use

- Routine feature work unrelated to cursorAssistant installs
- When the user only wants to edit a single managed file by hand

## Command

```sh
python3 cursorAssistant.py inspect --workspace . --json
python3 cursorAssistant.py plan-setup --workspace . --json
```

## Interpretation

| `installState` | Meaning |
| --- | --- |
| `not-installed` | No lockfile — run `configure` (preferred) or `setup` |
| `installed` | All managed files match package hashes |
| `needs-update` | Stale or missing files — run `update` |
| `needs-repair` | Lockfile or install integrity issue — run `repair` |

## Rules

- Do not edit `.cursor/agents`, `.cursor/skills`, `.cursor/rules`, or `.cursor/mcp.json` directly when `setup`/`update`/`repair` can apply the change.
- After audit, route install work to **cursorLifecycle** or run lifecycle commands with user confirmation.
- Use `factory-restore` only when the user explicitly wants a full managed-surface reset.
