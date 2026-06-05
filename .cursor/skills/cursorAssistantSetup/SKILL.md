---
name: cursorAssistantSetup
description: Use when the user wants to install or customize cursorAssistant in the current project (GitHub install or configure).
disable-model-invocation: true
paths:
  - ".cursor/**"
  - "AGENTS.md"
  - "cursorAssistant.py"
  - "template/setup/**"
---

# cursorAssistant project setup

Guides developers through the **mandatory setup interview** (lockfile, packs, MCP, personalization).

## When to use

- User clicked **Install in Cursor** and opened this project
- User wants to **set up** cursorAssistant in this repo
- `inspect` shows `interviewRequired: true`

## Canonical flow

Follow [references/interview-flow.md](references/interview-flow.md):

1. `inspect --json`
2. Ask **`setup.depth`**, then every active question → write `.cursor/cursor-assistant-answers.json`
3. `plan-setup --answers …` → user confirms
4. `configure --answers …`
5. `inspect` — `interviewRequired: false`
6. **Optional:** if depth is `advanced` or `full`, offer Cursor **User Rules** — [user-rules-step.md](references/user-rules-step.md)

## Question groups

**Simple:** `setup.depth`, `profile.selected`, `packs.selected`, `mcp.enabled`, agent batch (4 keys).

**Advanced (+):** `response.style`, `autonomy.level`, `agent.persona`.

**Full (+):** `testing.philosophy`.

**Conditional:** `lean.reasoning.mode` when lean profile or pack selected.

## Rules

- Do not infer answers from the lockfile.
- Never call deprecated `setup`.
- `lifecycle_configure` requires `answersPath`.

## Verify

- [ ] `interviewRequired: false`
- [ ] Answers file includes all active keys for chosen depth
- [ ] User confirmed plan before configure
