#!/usr/bin/env bash
# Install cursorAssistant surfaces into this package repo for local development.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ANSWERS="$(mktemp)"
trap 'rm -f "$ANSWERS"' EXIT
printf '%s\n' '{"mcp.enabled": false}' >"$ANSWERS"
python3 cursorAssistant.py setup --workspace . --package-root . --answers "$ANSWERS" --json
echo "Dogfood complete: .cursor/ updated (MCP bundle off; cursorTools only)."
