#!/usr/bin/env bash
# Run cursorEval quality on core skills changed vs a base ref (workflow_dispatch / local).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CE=(python3 tools/cursorEval/cursorEval.py --repo-root .)

if [ -z "${GITHUB_MODELS_TOKEN:-}" ] && [ -z "${GITHUB_TOKEN:-}" ] && [ -z "${GH_TOKEN:-}" ]; then
  echo "eval_quality_changed: skip — no GITHUB_MODELS_TOKEN / GITHUB_TOKEN / GH_TOKEN"
  exit 0
fi

BASE="${EVAL_QUALITY_BASE:-origin/master}"
if ! git rev-parse --verify "$BASE" >/dev/null 2>&1; then
  BASE="HEAD~1"
fi

mapfile -t CHANGED < <(
  git diff --name-only "$BASE"...HEAD -- 'skills/*/SKILL.md' 2>/dev/null || true
)

if [ "${#CHANGED[@]}" -eq 0 ]; then
  echo "eval_quality_changed: no core skill changes vs $BASE"
  exit 0
fi

FAIL_UNDER="${EVAL_QUALITY_FAIL_UNDER:-0.65}"
MODEL="${EVAL_QUALITY_MODEL:-gpt-4o-mini}"
FAILED=0

for skill_path in "${CHANGED[@]}"; do
  [ -f "$skill_path" ] || continue
  echo "eval_quality_changed: quality $skill_path (fail-under $FAIL_UNDER)"
  if ! "${CE[@]}" quality "$skill_path" --model "$MODEL" --fail-under "$FAIL_UNDER"; then
    code=$?
    if [ "$code" -eq 1 ]; then
      FAILED=1
      continue
    fi
    echo "eval_quality_changed: skip — model unavailable (exit $code)"
    exit 0
  fi
done

if [ "$FAILED" -ne 0 ]; then
  echo "eval_quality_changed: one or more skills below $FAIL_UNDER"
  exit 1
fi

echo "eval_quality_changed: ok (${#CHANGED[@]} skill(s))"
