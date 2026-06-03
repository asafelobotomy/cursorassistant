#!/usr/bin/env bash
# Dogfood with MCP extensions and all packs (local dev / eval workspaces).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ANSWERS="$(mktemp)"
trap 'rm -f "$ANSWERS"' EXIT
cat >"$ANSWERS" <<'EOF'
{
  "mcp.enabled": true,
  "packs.selected": ["lean", "secure", "tdd"]
}
EOF
python3 cursorAssistant.py setup --workspace . --package-root . --answers "$ANSWERS" --json
echo "Dogfood-full complete: extensions (devDocs, memory) + all packs; no git MCP."
