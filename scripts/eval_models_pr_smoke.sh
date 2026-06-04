#!/usr/bin/env bash
# Low-cost GitHub Models smoke for PRs. Skips cleanly when no token is set.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ -z "${GITHUB_MODELS_TOKEN:-}" ] && [ -z "${GITHUB_TOKEN:-}" ] && [ -z "${GH_TOKEN:-}" ]; then
  echo "eval_models_pr_smoke: skip — no GITHUB_MODELS_TOKEN / GITHUB_TOKEN / GH_TOKEN"
  exit 0
fi
MODEL="${CURSOR_EVAL_MODEL:-gpt-4o-mini}"
CE="python3 tools/cursorEval/cursorEval.py --repo-root ."

_run_suite() {
  local suite="$1"
  if $CE run "$suite" --model "$MODEL"; then
    return 0
  fi
  local latest
  latest="$(ls -t .cursorEval/*.json 2>/dev/null | head -1 || true)"
  if [ -n "$latest" ] && grep -q '401' "$latest"; then
    echo "eval_models_pr_smoke: skip — GitHub Models 401 (set GITHUB_MODELS_TOKEN for live routing)"
    exit 0
  fi
  return 1
}

_run_suite evals/models-smoke/eval.yaml
_run_suite evals/cursorAssistantSetup/eval.yaml
echo "eval_models_pr_smoke: passed"
