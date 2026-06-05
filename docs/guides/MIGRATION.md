# Migration guide

## v0.16–v0.17 overview (Phases D1–D5)

Shipped across **v0.16.0 → v0.17.2**. Full design: [TOKEN_AND_PACK_INTERVIEW_PLAN.md](../project/TOKEN_AND_PACK_INTERVIEW_PLAN.md).

| Release | What changed | Action if upgrading |
| --- | --- | --- |
| **0.16.0** | Copy-from preflight, user defaults, MCP interview tools | Optional — new projects only |
| **0.16.1** | Pack `tokens.json` → namespaced keys in materialize | Re-run `configure` after selecting packs |
| **0.17.0** | Pack interview layer; lockfile **0.6.0** + `packAnswers` | Re-interview pack layer if packs selected |
| **0.17.1** | 4 new simple-depth agent/skill keys (8-key batch) | Re-interview + `configure --answers` |
| **0.17.2** | Docs, install fixtures, evals (no schema break) | Read [PREFERENCES_LAYERS.md](PREFERENCES_LAYERS.md) |

**Fixtures** (non-interactive CI or quick dogfood):

- `tests/fixtures/interview-balanced.json` — simple depth, balanced profile
- `tests/fixtures/interview-with-secure.json` — secure pack + pack interview answers
- `tests/fixtures/interview-balanced-lean.json` — lean pack combo

**Preferences:** user defaults vs `preferences.mdc` vs User Rules — [PREFERENCES_LAYERS.md](PREFERENCES_LAYERS.md).

---

## v0.17.1 — extended agent/skill tokens (breaking for existing answers files)

### Interview expansion (D4)

- **Agent batch** grows from 4 → **8** keys at `simple` depth: adds `debugger`, `deps`, `inventory`, and `skill.ciPreflight.runPolicy`.
- Tokens render into `.cursor/agents/{debugger,deps,inventory}.md` and `.cursor/skills/ciPreflight/SKILL.md`.
- **Advanced:** optional `setup.defaults.autoSave` (stored in user defaults file only; auto-updates defaults after configure when true).

### Action

Re-run interview and `configure --answers` with updated fixtures or answer the four new simple-depth keys. Example:

```sh
python3 cursorAssistant.py configure --workspace . --answers tests/fixtures/interview-balanced.json
```

## v0.17.0 — pack interview and lockfile packAnswers (breaking for pack users)

### Schema and lockfile

- **Lockfile `schemaVersion` 0.6.0** — adds nested **`packAnswers`** grouped by pack id.
- **`packs/<id>/interview.json`** — one question per pack (batch `pack`) when the pack is in `packs.selected`.
- **Flat** `.cursor/cursor-assistant-answers.json` unchanged for copy-from; `configure` splits pack keys into lockfile `packAnswers`.
- **Removed** legacy short pack token aliases (`pack:review-depth`); use namespaced `{{pack:<packId>:<name>}}`.

### Action

Workspaces on lockfile **0.5.x** with packs selected must re-run the pack interview layer, then `configure --answers`:

```sh
python3 cursorAssistant.py interview --workspace . --answers .cursor/cursor-assistant-answers.json
python3 cursorAssistant.py configure --workspace . --answers .cursor/cursor-assistant-answers.json
```

Fixtures: `tests/fixtures/interview-with-secure.json`, `interview-balanced-lean.json`.

Partial reconfigure: changing `packs.selected` drops deselected pack keys from `packAnswers`; newly selected packs require their pack questions before `configure`.

## v0.16.1 — pack token loading

### Pack tokens

- **`packs/<id>/tokens.json`** is loaded when a pack is in `packs.selected`.
- Token keys are **namespaced**: `pack:<packId>:<name>` (e.g. `pack:tdd:scope-discipline`).
- **Legacy aliases** (`pack:review-depth`, etc.) are emitted for one release when templates still use short keys; the last selected pack in sorted pack-id order wins on collision.
- **`pack:reasoning-mode`** stays owned by core interview (`lean.reasoning.mode` via `preference_tokens.py`), not pack aliases.

### Action

No lockfile migration. Re-run `configure` or `update` after selecting packs so managed surfaces receive pack tokens in `plan-setup` / `inspect`.

Prefer namespaced placeholders in new content: `{{pack:tdd:scope-discipline}}` instead of `{{pack:scope-discipline}}`.

## v0.16 — copy-from interview and user defaults

### Added

- Preflight `setup.copyFrom.*` (stripped from committed answers); import via MCP `lifecycle_interview_import` or CLI.
- User defaults: `~/.cursor/cursor-assistant-defaults.json` (explicit save only).
- MCP interview API tools; `install-from-github.sh` requires interview or `--answers` non-interactively.

### Action

Existing workspaces: no breaking change. New projects can copy answers from a GitHub repo during interview.

## v0.15 — progressive setup interview (breaking)

### Schema and lockfile

- **`interview.json` `schemaVersion` 0.5.0** — adds `setup.depth`, personalization, agent batch, conditional lean question.
- **Lockfile `schemaVersion` 0.5.0** — pre-0.5 lockfiles report `interviewRequired: true`.
- New managed rule: `.cursor/rules/preferences.mdc` (advanced/full depths only).
- Agent instruction tokens: commit, docs, planner, review customization.

### Action

Re-run full interview at desired depth, then `configure --answers`:

```sh
python3 cursorAssistant.py interview --workspace .
python3 cursorAssistant.py configure --workspace . --answers .cursor/cursor-assistant-answers.json
```

Or use fixtures: `tests/fixtures/interview-balanced.json`, `interview-advanced.json`, `interview-full.json`.

### User Rules (Phase C)

- Advanced/full interviews write prefs to `.cursor/rules/preferences.mdc` (project).
- Optional **Cursor User Rules** for IDE-wide tone/autonomy — not stored in the lockfile.
- `update` alone does not change personalization; re-interview or edit User Rules.

## v0.14 — mandatory setup interview (breaking)

### Removed silent install paths

- **`setup` CLI command** — deprecated (exit 2). Use `interview` then `configure --answers .cursor/cursor-assistant-answers.json`.
- **`configure --no-interview`** — removed.
- **`configure --yes` / `-y`** — removed.
- **Lockfile answer replay** — `configure` and `interview` no longer infer profile/packs from the lockfile.
- **`lifecycle_setup` MCP** — deprecated; use `lifecycle_configure` with required `answersPath`.
- **Non-interactive `configure` without `--answers`** — returns `interview_required`.

### New contract

1. `inspect` — check `interviewRequired`.
2. Complete interview (chat AskQuestion or `interview` in a TTY).
3. `plan-setup --answers .cursor/cursor-assistant-answers.json`
4. `configure --answers .cursor/cursor-assistant-answers.json`
5. `update` / `repair` / `factory-restore` require `--answers` when `interviewRequired` is true.

### Action

Re-run `/cursor-assistant:setup-workspace` or:

```sh
python3 cursorAssistant.py interview --workspace .
python3 cursorAssistant.py configure --workspace . --answers .cursor/cursor-assistant-answers.json
```

Commit `.cursor/cursor-assistant-answers.json` if your team wants non-interactive `update` in CI.

## v0.9 → v0.10

### Removed: `triage` subagent

- **Before:** `/triage` or Task `triage` for complexity classification.
- **After:** Use the **`task-triage`** skill (`/task-triage`) from the main Agent when scope is unclear.
- **Action:** Run `update` or `repair` so `.cursor/agents/triage.md` is pruned. Ensure `skills/task-triage/SKILL.md` is installed.

### Removed: `git` MCP server

- **Before:** `git` in `.cursor/mcp.json` when `mcp.enabled: true`.
- **After:** Git work via **Shell** / **`gh`** and the **`commit`** subagent. Optional extensions are only `devDocs` and `memory`.
- **Action:** Run `update` — deprecated servers are stripped from `mcp.json`. Remove `.cursor/mcp/scripts/gitMcp.py` if still present (or rely on `repair` + orphan prune).

### Unchanged

- **`inventory`** still replaces a custom `explore` agent; use Cursor built-in **Explore** for wide parallel search.
- **Layered MCP** (core + extensions + packs) from v0.9 remains.

```sh
python3 cursorAssistant.py update --workspace . --package-root /path/to/cursorassistant --json
```

See [../architecture/MCP_LAYOUT.md](../architecture/MCP_LAYOUT.md) and [AGENTS.md](../AGENTS.md).
