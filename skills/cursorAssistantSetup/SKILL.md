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

## When not to use

- Package bootstrap only (global MCP + plugin) — use the install page or `bootstrap-from-github.sh`
- `update` / `repair` when interview answers already exist — use `cursorLifecycle`
- Changing IDE-wide tone without re-interview — Cursor **User Rules**, not this skill

## Canonical flow

Follow [references/interview-flow.md](references/interview-flow.md):

1. `lifecycle_inspect` or `inspect --json`
2. `lifecycle_defaults_load` — prefill draft from `~/.cursor/cursor-assistant-defaults.json` when present
3. **Preflight:** `setup.copyFrom.enabled` / `setup.copyFrom.repo` — when enabled, `lifecycle_interview_import` then confirm merge
4. Ask pending questions (batched **AskQuestion**) → `lifecycle_interview_save` or write `.cursor/cursor-assistant-answers.json`
5. `lifecycle_plan_setup` / `plan-setup --answers …` — confirm profile, packs, token summary, `wouldWrite`
6. `lifecycle_configure` / `configure --answers …`
7. `inspect` — `interviewRequired: false`
8. **Optional:** advanced/full → Cursor **User Rules** — [user-rules-step.md](references/user-rules-step.md)
9. **Optional:** explicit “Save as my defaults?” → `lifecycle_defaults_save` (never auto-save)

## Question groups

**Preflight:** `setup.copyFrom.enabled`, `setup.copyFrom.repo` (stripped from committed answers).

**Simple:** `setup.depth`, `profile.selected`, `packs.selected`, `mcp.enabled`, agent batch (4 keys).

**Advanced (+):** `response.style`, `autonomy.level`, `agent.persona`.

**Full (+):** `testing.philosophy`.

**Pack (when selected):** per-pack questions from `packs/<id>/interview.json`.

**Conditional:** `lean.reasoning.mode` when lean profile or pack selected.

## Rules

- Do not infer answers from the lockfile.
- Never call deprecated `setup`.
- `lifecycle_configure` requires `answersPath`.
- Do not commit secrets or API keys in answers — see [SECURITY.md](../../SECURITY.md).
- `setup.copyFrom.*` keys are interview-only; they are stripped on save.

## Verify

- [ ] `interviewRequired: false`
- [ ] Answers file includes all active keys for chosen depth
- [ ] User confirmed plan before configure
