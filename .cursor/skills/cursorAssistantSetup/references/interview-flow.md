# Setup interview flow (canonical)

## Ordered steps

1. `python3 cursorAssistant.py inspect --workspace . --json`
   - Report `installState`, `interviewRequired`, `interviewDepth`.
2. `lifecycle_defaults_load` (or `defaults-load --json`) when user may have saved defaults.
3. **Preflight** — AskQuestion batch:
   - `setup.copyFrom.enabled` (boolean)
   - `setup.copyFrom.repo` (string, when enabled) — default branch only
   - When enabled: `lifecycle_interview_import` → show `source`, `droppedKeys`, `warnings`; user confirms merge.
4. Ask **pending** questions for active depth (defaults prefill does not skip confirmation).
   - Use **AskQuestion** per layer (preflight → setup.depth → simple → advanced/full).
   - Do **not** read profile/packs/MCP from the lockfile.
5. `lifecycle_interview_save` or write `.cursor/cursor-assistant-answers.json` (ephemeral `setup.copyFrom.*` stripped).
6. `python3 cursorAssistant.py plan-setup --workspace . --answers .cursor/cursor-assistant-answers.json --json`
   - Present profile, packs, MCP, depth, `tokenSummary`, `preflight.copyFromRepo` (if any), and `wouldWrite`; get user confirmation.
7. `python3 cursorAssistant.py configure --workspace . --answers .cursor/cursor-assistant-answers.json --json`
8. `inspect` again — expect `interviewRequired: false` and lockfile `schemaVersion: 0.5.0`.
9. **Optional (advanced/full):** offer Cursor **User Rules** — see [user-rules-step.md](user-rules-step.md).
10. **Optional:** “Save as my defaults?” → `lifecycle_defaults_save` (explicit confirm only).

## Depth batches

| `setup.depth` | Extra questions |
| --- | --- |
| `simple` | Profile, packs, MCP, agent batch |
| `advanced` | + response style, autonomy, persona |
| `full` | + testing philosophy |

Conditional: `lean.reasoning.mode` when lean profile or lean pack is selected.

## Agent batch (always for installed agents)

- `agent.commit.messageStyle`
- `agent.docs.outputStyle`
- `agent.planner.planFormat`
- `agent.review.reportingThreshold`

## MCP interview API

| Tool | Purpose |
| --- | --- |
| `lifecycle_interview_questions` | Partial answers → active/pending questions |
| `lifecycle_interview_import` | GitHub repo → merged draft (no write) |
| `lifecycle_interview_save` | Validate + write answers file |
| `lifecycle_defaults_load` | Read user defaults |
| `lifecycle_defaults_save` | Write user defaults after confirm |

CLI parity: `interview --questions-json [--answers PATH]`, `defaults-load`, `defaults-save --answers PATH`.

## Forbidden

- `python3 cursorAssistant.py setup` (deprecated; exit 2)
- `configure` without `--answers` after an agent-driven interview
- `lifecycle_configure` / `lifecycle_setup` MCP without `answersPath`
- Writing defaults without user input
- Committing `setup.copyFrom.*` or secret values in answers

## Automation fixtures

| Fixture | Depth |
| --- | --- |
| `tests/fixtures/interview-balanced.json` | `simple` |
| `tests/fixtures/interview-advanced.json` | `advanced` |
| `tests/fixtures/interview-full.json` | `full` |

```sh
python3 cursorAssistant.py configure --workspace . --answers tests/fixtures/interview-balanced.json --json
```
