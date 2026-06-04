# Cursor hooks (optional)

cursorAssistant does not install hooks by default. Use Cursor **hooks** when you want deterministic automation around agent events (for example format-on-save after an edit, or a pre-commit reminder).

See also: [CURSOR_AUTOMATIONS.md](CURSOR_AUTOMATIONS.md) (automations vs hooks, package template path).

## When to add hooks

- Repeatable guardrails that should run without relying on the model (lint, secret scan, test smoke)
- Team workflows that must fire on every agent session in a repo

## When not to

- One-off tasks — use skills (`/ciPreflight`, `/task-triage`) or subagents instead
- Anything already covered by CI on the remote — hooks complement, not replace, GitHub Actions

## Template

Package example: `template/hooks/hooks.json.example` (copy into the consumer workspace). Or create `.cursor/hooks.json` manually (not managed by core install):

```json
{
  "version": 1,
  "hooks": []
}
```

Populate `hooks` per [Cursor hooks documentation](https://cursor.com/docs). Keep scripts small, idempotent, and fast — agents time out on long hook chains.

## Lifecycle

`inspect` / `update` do not manage `hooks.json`. Treat hooks as **user-owned** configuration alongside User Rules.
