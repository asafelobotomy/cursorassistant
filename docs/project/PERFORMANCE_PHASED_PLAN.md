# Performance-first phased plan (v0.13)

Efficiency priorities: minimize auto-loaded context, freeze roster size, measure with `cursorEval tokens` and routing evals.

## Budget targets

| Surface | Target |
| --- | --- |
| `core.mdc` | ≤ 400 tokens, always-on |
| `AGENTS.md` | ≤ 1,400 tokens |
| Core skill body | ≤ 800 tokens (or `references/` + slash-only) |
| Auto-invokable core skills | ≤ 3 (`workspaceSearch`, `ciPreflight`, `testing`; optional `depSearch`) |
| Core agents | 11 (frozen) |

## Phases (highest ROI first)

### Phase 1 — Skill scoping (zero new files) ✅ done

- Add `disable-model-invocation: true` on: `task-triage`, `cursorAssistantSetup`, `lifecycleAudit`, `surfaceReview`
- Add `paths` on: `surfaceReview`, `lifecycleAudit`, `cursorAssistantSetup`, `ciPreflight`
- **Exit:** `cursorEval check` passes; negative routing evals still pass

### Phase 2 — Compress `surfaceReview` ✅ done

- Slim `SKILL.md` to checklist + module table; move module detail to `references/modules.md`
- Keep six-module behavior; reduce body to ~800 tokens
- **Exit:** `tokens` ≤ 900; `surfaceReview` evals pass

### Phase 3 — Trim `AGENTS.md` ✅ done

- Move verbose handoffs / eval notes to `ROUTING_AND_SUBAGENTS.md`
- Keep roster, skills table, conflict matrix
- **Exit:** `tokens` ≤ 1,400

### Phase 4 — Fold parallel scope into `task-triage` ✅ done

- Add ~25 lines + optional `references/parallel-scope.md`
- One eval task for parallel scope output
- **Exit:** no new skill; task-triage eval passes

### Phase 5 — Maintainer sync without new skill ✅ done

- Extend `commit` agent with package-repo sync checklist (not consumer-facing bloat)
- **Exit:** `managed-surface-review` + commit eval still pass

### Phase 6 — Zero-token optional artifacts ✅ done

- `template/hooks/hooks.json.example` + minimal script
- `docs/guides/CURSOR_AUTOMATIONS.md` (doc only)
- One line in `core.mdc` pointing to HOOKS / automations doc

### Phase 7 — Eval guardrails ✅ done

- 3 tasks: paths block `surfaceReview` on wrong files; slash-only skills absent on generic prompts
- Optional: baseline A/B for `task-triage` (workflow_dispatch only)

### Phase 8 — Maintainer tooling ✅ done

- `generate.py`: derive `catalog.agents` from `install-policy.json`
- `docs/architecture/PERFORMANCE.md` governance checklist
- `bash scripts/sync_managed_surfaces.sh` after all source edits

## Not in v0.13

- New core agents or skills (`releasePrep` skill, `parallelScope` skill, `routing-hints.mdc`)
- `cursorAutomations` skill (doc only in Phase 6)
- Pack changes

## Verification (each phase)

```sh
python3 tools/cursorEval/cursorEval.py check <changed-surface>
python3 tools/cursorEval/cursorEval.py validate
python3 scripts/check_package_sync.py
python3 -m unittest discover -s tests -q
```
