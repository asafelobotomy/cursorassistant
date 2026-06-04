#!/usr/bin/env bash
# Example hook: log event name to stderr (replace with your check).
# Copy to .cursor/hooks/ and point hooks.json at the installed path.
set -euo pipefail
echo "cursorAssistant example hook: ${CURSOR_HOOK_EVENT:-unknown}" >&2
