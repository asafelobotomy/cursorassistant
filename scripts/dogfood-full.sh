#!/usr/bin/env bash
# Dogfood with MCP extensions and all packs (local dev / eval workspaces).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ANSWERS="$(mktemp)"
trap 'rm -f "$ANSWERS"' EXIT
cat >"$ANSWERS" <<'EOF'
{
  "setup.depth": "full",
  "profile.selected": "balanced",
  "mcp.enabled": true,
  "packs.selected": ["lean", "secure", "tdd"],
  "response.style": "balanced",
  "autonomy.level": "ask-first",
  "agent.persona": "professional",
  "testing.philosophy": "always",
  "lean.reasoning.mode": "compressed",
  "agent.commit.messageStyle": "conventional-subject-first",
  "agent.docs.outputStyle": "corpus-match",
  "agent.planner.planFormat": "tight-phased",
  "agent.review.reportingThreshold": "critical-high"
}
EOF
python3 cursorAssistant.py configure --workspace . --package-root . --answers "$ANSWERS" --json
echo "Dogfood-full complete: extensions (devDocs, memory) + all packs; no git MCP."
