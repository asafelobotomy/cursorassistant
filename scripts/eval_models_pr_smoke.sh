#!/usr/bin/env bash
# Low-cost GitHub Models smoke for PRs. Skips cleanly when no token is set.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ -z "${GITHUB_MODELS_TOKEN:-}" ] && [ -z "${GITHUB_TOKEN:-}" ] && [ -z "${GH_TOKEN:-}" ]; then
  echo "eval_models_pr_smoke: skip — no GITHUB_MODELS_TOKEN / GITHUB_TOKEN / GH_TOKEN"
  exit 0
fi
python3 tools/cursorEval/cursorEval.py --repo-root . run evals/models-smoke/eval.yaml --model gpt-4o-mini
echo "eval_models_pr_smoke: passed"
