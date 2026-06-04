# Cursor automations and hooks (optional)

cursorAssistant does **not** ship enabled hooks by default — zero always-on token cost until you opt in.

## Automations (Cursor product)

Use Cursor **Automations** for scheduled or event-driven agent runs (PR babysit, CI triage, doc refresh). Prefer the built-in Automations UI or the `automate` skill in user scope; do not duplicate automation logic inside `AGENTS.md`.

## Hooks (project-local)

1. Copy `template/hooks/hooks.json.example` to `.cursor/hooks.json` (or merge into an existing file).
2. Adjust script paths; keep hooks **fast** and **non-interactive**.
3. Do not commit secrets; hooks run in the developer environment.

See [Cursor hooks documentation](https://cursor.com/docs/agent/hooks) for event names and payload shape.

## When to use what

| Need | Use |
| --- | --- |
| One-off agent task in chat | Main Agent + `AGENTS.md` routing |
| Repeatable workflow | Automation or hook + narrow prompt |
| Pre-commit quality | `ciPreflight` skill or git hook script |
