#!/usr/bin/env bash
# Run cursorEval check on every core and pack skill and agent source file.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
run_check() {
  python3 tools/cursorEval/cursorEval.py --repo-root . check "$1"
}
for skill in skills/*/SKILL.md; do
  run_check "$skill"
done
for skill in packs/*/skills/*/SKILL.md; do
  run_check "$skill"
done
for agent in agents/*.md; do
  run_check "$agent"
done
echo "ci_check_surfaces: all core and pack skills and agents passed check"
