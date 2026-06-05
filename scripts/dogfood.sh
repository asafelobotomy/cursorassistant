#!/usr/bin/env bash
# Install cursorAssistant surfaces into this package repo for local development.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ANSWERS="$(mktemp)"
trap 'rm -f "$ANSWERS"' EXIT
cat >"$ANSWERS" <<'EOF'
{
  "setup.depth": "simple",
  "profile.selected": "balanced",
  "packs.selected": [],
  "mcp.enabled": false,
  "agent.commit.messageStyle": "conventional-subject-first",
  "agent.docs.outputStyle": "corpus-match",
  "agent.planner.planFormat": "tight-phased",
  "agent.review.reportingThreshold": "critical-high"
}
EOF
python3 cursorAssistant.py configure --workspace . --package-root . --answers "$ANSWERS" --json
echo "Dogfood complete: .cursor/ updated (MCP bundle off; cursorTools only)."
