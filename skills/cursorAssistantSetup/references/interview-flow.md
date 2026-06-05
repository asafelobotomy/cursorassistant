# Setup interview flow (canonical)

## Ordered steps

1. `python3 cursorAssistant.py inspect --workspace . --json`
   - Report `installState`, `interviewRequired`, `interviewDepth`.
2. If `interviewRequired` or user asked to reconfigure: run the interview.
   - Ask **`setup.depth`** first (`simple` / `advanced` / `full`).
   - Use **AskQuestion** for each active question (base + agent batch).
   - Do **not** read profile/packs/MCP from the lockfile.
3. Write `.cursor/cursor-assistant-answers.json` (all active keys required).
4. `python3 cursorAssistant.py plan-setup --workspace . --answers .cursor/cursor-assistant-answers.json --json`
   - Present profile, packs, MCP, depth, and `wouldWrite`; get user confirmation.
5. `python3 cursorAssistant.py configure --workspace . --answers .cursor/cursor-assistant-answers.json --json`
6. `inspect` again — expect `interviewRequired: false` and lockfile `schemaVersion: 0.5.0`.
7. **Optional (advanced/full):** offer Cursor **User Rules** for IDE-wide prefs — see [user-rules-step.md](user-rules-step.md).

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

## Forbidden

- `python3 cursorAssistant.py setup` (deprecated; exit 2)
- `configure` without `--answers` after an agent-driven interview
- `lifecycle_configure` / `lifecycle_setup` MCP without `answersPath`
- Writing defaults without user input

## Automation fixtures

| Fixture | Depth |
| --- | --- |
| `tests/fixtures/interview-balanced.json` | `simple` |
| `tests/fixtures/interview-advanced.json` | `advanced` |
| `tests/fixtures/interview-full.json` | `full` |

```sh
python3 cursorAssistant.py configure --workspace . --answers tests/fixtures/interview-balanced.json --json
```
