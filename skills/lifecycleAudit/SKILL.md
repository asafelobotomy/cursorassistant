---
name: lifecycleAudit
description: Use before proposing cursorAssistant setup, update, or repair — inspect lockfile and managed file drift.
---

# Lifecycle audit

Read-only check of cursorAssistant install state before mutating managed surfaces.

## Command

```sh
python3 cursorAssistant.py inspect --workspace . --package-root <cursorAssistant-root> --json
```

## Interpretation

| `installState` | Meaning |
| --- | --- |
| `not-installed` | No lockfile — run `setup` |
| `installed` | All managed files match package hashes |
| `needs-update` | Stale or missing files — run `update` |

## Rules

- Do not edit `.cursor/agents`, `.cursor/skills`, `.cursor/rules`, or `.cursor/mcp.json` directly when `setup`/`update` can apply the change.
- After audit, route install work to **cursorLifecycle** or run `setup`/`update` with user confirmation.
