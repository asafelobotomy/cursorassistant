# Cursor hooks (optional)

cursorAssistant does not install hooks by default. Use Cursor **hooks** when you want deterministic automation around agent events (for example format-on-save after an edit, or a pre-commit reminder).

## When to add hooks

- Repeatable guardrails that should run without relying on the model (lint, secret scan, test smoke)
- Team workflows that must fire on every agent session in a repo

## When not to

- One-off tasks — use skills (`/ciPreflight`, `/task-triage`) or subagents instead
- Anything already covered by CI on the remote — hooks complement, not replace, GitHub Actions

## Template

Create `.cursor/hooks.json` in the consumer workspace (not managed by cursorAssistant core install):

```json
{
  "version": 1,
  "hooks": []
}
```

Populate `hooks` per [Cursor hooks documentation](https://cursor.com/docs). Keep scripts small, idempotent, and fast — agents time out on long hook chains.

## Lifecycle

`inspect` / `update` do not manage `hooks.json`. Treat hooks as **user-owned** configuration alongside User Rules.
