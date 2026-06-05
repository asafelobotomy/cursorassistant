---
name: setup-workspace
description: Interview and install cursorAssistant into the current project (agents, skills, rules, lockfile).
---

# Set up cursorAssistant in this project

Run after the [setup page](https://asafelobotomy.github.io/cursorassistant/install/) MCP bootstrap.

## Canonical flow

See `skills/cursorAssistantSetup/references/interview-flow.md`.

1. `inspect --json` — check `interviewRequired`.
2. Ask every `interview.json` question (AskQuestion in chat).
3. Write `.cursor/cursor-assistant-answers.json`.
4. `plan-setup --answers .cursor/cursor-assistant-answers.json --json` — user confirms.
5. `configure --answers .cursor/cursor-assistant-answers.json --json`.
6. **Developer: Reload Window**; enable MCP if interview enabled extensions.
7. **Optional:** if `setup.depth` is `advanced` or `full`, offer Cursor **User Rules** — `skills/cursorAssistantSetup/references/user-rules-step.md`.

## Do not use

- `python3 cursorAssistant.py setup` (deprecated)
- `configure` without `--answers` in Agent chat
- `lifecycle_configure` without `answersPath`

## Dry run

```sh
python3 cursorAssistant.py plan-setup --workspace . --answers .cursor/cursor-assistant-answers.json --json
```
