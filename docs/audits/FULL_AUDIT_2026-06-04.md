# Full audit (2026-06-04) — v0.13.0

Point-in-time audit after the performance-first release. Supersedes stale counts in older audit snapshots where noted.

## Automated gates (all pass)

| Gate | Result |
| --- | --- |
| `check_package_sync.py` | OK |
| Unit tests (65) | OK |
| `cursorEval validate` | OK (32 suites) |
| `coverage --strict` | 31/31 full |
| `cursorEval policy` | OK |
| `ci_check_surfaces.sh` | OK |
| Dogfood `inspect` | installed, 0 stale, 0 missing |

## Routing & skills

| Item | Status |
| --- | --- |
| Core agents | 11 |
| Core skills | 8 |
| Custom `explore` | absent |
| Eval `positive-trigger-2` | all 11 core agents |
| Slash-only skills | 5 (`task-triage`, `lifecycleAudit`, `surfaceReview`, `cursorAssistantSetup`, `depSearch`) |
| Auto-invoke skills | 3 (`workspaceSearch`, `ciPreflight`, `testing`) |

## Token budgets (post-remediation)

| Surface | Target | Actual |
| --- | ---: | ---: |
| `AGENTS.md` | ≤ 1,400 | **1,076** after 2026-06-04 trim |
| `core.mdc` | ≤ 400 | ~372 |
| `surfaceReview` SKILL | ≤ 800 | ~604 |

## Remediation applied (2026-06-04)

1. Trimmed `AGENTS.md` to meet token budget.
2. Added `## Verify` to `task-triage`, `lifecycleAudit`, `cursorAssistantSetup`, `testing`.
3. `disable-model-invocation` on `depSearch` (≤3 auto skills).
4. Refreshed [AGENTS_SKILLS_CURSOR_AUDIT.md](AGENTS_SKILLS_CURSOR_AUDIT.md) and [CURSOR_EVAL_AUDIT.md](CURSOR_EVAL_AUDIT.md).
5. Cross-linked [HOOKS.md](../guides/HOOKS.md) ↔ [CURSOR_AUTOMATIONS.md](../guides/CURSOR_AUTOMATIONS.md).
6. Live routing: `bash scripts/eval_routing_live.sh` (skips on missing token or 401; verified locally 2026-06-04).

## Live evals (operator)

```sh
export GITHUB_MODELS_TOKEN=...
bash scripts/eval_routing_live.sh
# or: gh workflow run evals.yml (workflow_dispatch)
```

Static routing evals run on every PR; live model runs remain optional.
