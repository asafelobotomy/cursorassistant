# Performance governance (cursorAssistant)

Minimize **auto-loaded** context; measure with `cursorEval tokens` and routing evals.

## Budgets

| Surface | Target |
| --- | --- |
| `template/rules/core.mdc` | ≤ 400 tokens |
| `AGENTS.md` | ≤ 1,400 tokens |
| Core skill `SKILL.md` body | ≤ 800 tokens (detail → `references/`) |
| Auto-invokable core skills | ≤ 3 (`workspaceSearch`, `ciPreflight`, `testing`) |

## Checklist before merge (instruction surfaces)

1. New skill? Default **`disable-model-invocation: true`** unless it must auto-run (only the three skills above).
2. Narrow scope with **`paths`** when the skill only applies to specific trees.
3. Move long checklists to **`skills/<name>/references/`**; keep `SKILL.md` as invocation + verify.
4. Do not add roster agents without a routing eval and `install-policy.json` entry.
5. Run `python3 tools/cursorEval/cursorEval.py tokens <path>` on changed surfaces.
6. After package source edits: `bash scripts/sync_managed_surfaces.sh` and `python3 scripts/check_package_sync.py`.

## Slash-only skills

`task-triage`, `lifecycleAudit`, `surfaceReview`, `cursorAssistantSetup`, `depSearch` — invoke with `/name`; not ambient procedures.

## Verification

```sh
python3 tools/cursorEval/cursorEval.py validate
python3 scripts/check_package_sync.py
python3 -m unittest discover -s tests -q
```
