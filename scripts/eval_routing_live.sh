#!/usr/bin/env bash
# Live routing evals via GitHub Models (optional token). Used in CI workflow_dispatch and locally.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MODEL="${CURSOR_EVAL_MODEL:-gpt-4o-mini}"

if [ -z "${GITHUB_MODELS_TOKEN:-}" ] && [ -z "${GITHUB_TOKEN:-}" ] && [ -z "${GH_TOKEN:-}" ]; then
  echo "eval_routing_live: skip — no GITHUB_MODELS_TOKEN / GITHUB_TOKEN / GH_TOKEN"
  exit 0
fi

CE="python3 tools/cursorEval/cursorEval.py --repo-root ."

_run_suite() {
  local suite="$1"
  shift
  echo "eval_routing_live: run ${suite} $*"
  if $CE run "$suite" --model "$MODEL" "$@"; then
    return 0
  fi
  local latest
  latest="$(ls -t .cursorEval/*.json 2>/dev/null | head -1 || true)"
  if [ -n "$latest" ] && grep -q '401' "$latest"; then
    echo "eval_routing_live: skip — GitHub Models 401 (set GITHUB_MODELS_TOKEN)"
    exit 0
  fi
  return 1
}

# Core routing smoke (models-smoke + setup skill)
_run_suite evals/models-smoke/eval.yaml --tags models-smoke
_run_suite evals/cursorAssistantSetup/eval.yaml --tags smoke

# One positive task per core agent (fast routing check)
AGENTS=(inventory review commit deps docs debugger planner researcher organise cleaner cursorLifecycle)
for agent in "${AGENTS[@]}"; do
  if [ -f "evals/${agent}/tasks/positive-trigger-1.yaml" ]; then
    _run_suite "evals/${agent}/eval.yaml" --tags smoke
  fi
done

echo "eval_routing_live: all suites passed"
