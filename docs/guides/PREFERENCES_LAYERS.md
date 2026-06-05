# Three layers of preferences

cursorAssistant stores customization in three places. Use the right layer so solo
prefs follow you across projects without forcing team-wide IDE settings.

## Quick reference

| Layer | Scope | Written by | Typical keys |
| --- | --- | --- | --- |
| **User defaults** | IDE user (all workspaces) | Explicit save after configure, or `setup.defaults.autoSave` (advanced) | `setup.depth`, `packs.selected`, agent batch, copy-from prefill |
| **`preferences.mdc`** | This repo only | `configure` when depth is `advanced` or `full` | `response.style`, `autonomy.level`, `agent.persona` |
| **Cursor User Rules** | IDE user (all workspaces) | Optional post-configure step (MCP `cursor_dialog` or manual) | Same themes as `preferences.mdc`, IDE-wide |

Interview answers live in **`.cursor/cursor-assistant-answers.json`** (flat, committed).
Pack-specific answers are also nested in the lockfile as **`packAnswers`** (schema 0.6.0).

## User defaults (`~/.cursor/cursor-assistant-defaults.json`)

**When:** you want the next new project to start with the same depth, packs, and agent
customization without re-answering every question.

**How:**

- After configure, the setup skill may ask: “Save as my defaults?”
- MCP: `lifecycle_defaults_save` / `lifecycle_defaults_load`
- Advanced only: `setup.defaults.autoSave` auto-updates defaults after each configure

**Not stored here:** secrets, `setup.copyFrom.*` preflight keys (stripped on save), or
lockfile hashes.

**Prefill:** on a new workspace interview, defaults merge before AskQuestion (explicit
answers and copy-from import still win).

## Project rule (`preferences.mdc`)

**When:** this repo should encode tone and autonomy for anyone who clones it — useful
when the team shares the same agent behavior in that codebase.

**How:** rendered from interview keys at `advanced` or `full` depth during `configure`.
Skipped at `simple` depth (no personalization questions).

**Location:** `.cursor/rules/preferences.mdc` (managed; do not hand-edit — re-run
interview + configure).

## Cursor User Rules

**When:** you want concise/verbose style or ask-first autonomy **everywhere** in Cursor,
not just one repo.

**How:** optional step after configure — see
`skills/cursorAssistantSetup/references/user-rules-step.md`. Uses `cursor_dialog` when
available.

**Not a substitute for:** pack selection, MCP toggles, or per-agent tokens (those stay
in answers + lockfile).

## Decision guide

```text
Same packs/agents on every new repo?     → save user defaults (or autoSave)
This repo’s tone for all collaborators?  → advanced/full interview → preferences.mdc
Your personal style in every IDE chat?   → User Rules (post-configure)
Only this project, minimal ceremony?     → simple depth + committed answers file
```

## Related docs

- [MIGRATION.md](MIGRATION.md) — v0.16–v0.17 interview and lockfile changes
- [TOKEN_AND_PACK_INTERVIEW_PLAN.md](../project/TOKEN_AND_PACK_INTERVIEW_PLAN.md) — D1–D5 design
- [CURSOR_INSTALL_UX.md](CURSOR_INSTALL_UX.md) — install and interview flow
