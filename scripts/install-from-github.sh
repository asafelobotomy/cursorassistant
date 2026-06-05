#!/usr/bin/env bash
# Full install: bootstrap package + configure current workspace (interview + project files).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.16.0/scripts/install-from-github.sh | bash
#   curl -fsSL .../install-from-github.sh | bash -s -- /path/to/your-project
#   bash scripts/install-from-github.sh . --answers .cursor/cursor-assistant-answers.json
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_BASE="${CURSOR_ASSISTANT_HOME:-${HOME}/.local/share/cursorassistant}"

WORKSPACE="${1:-.}"
shift || true

ANSWERS_PROVIDED=0
for arg in "$@"; do
  case "$arg" in
    --answers|--answers=*)
      ANSWERS_PROVIDED=1
      ;;
  esac
done

"${SCRIPT_DIR}/bootstrap-from-github.sh"

PKG="${CURSOR_ASSISTANT_PACKAGE_ROOT:-${INSTALL_BASE}/current}"
if [[ ! -f "${PKG}/cursorAssistant.py" ]]; then
  echo "cursorAssistant package not found at ${PKG}" >&2
  exit 1
fi

cd "${WORKSPACE}"

if [[ "$ANSWERS_PROVIDED" -eq 0 ]]; then
  if [[ -t 0 ]]; then
    python3 "${PKG}/cursorAssistant.py" interview --workspace "$(pwd)"
    exec python3 "${PKG}/cursorAssistant.py" configure --workspace "$(pwd)" \
      --answers .cursor/cursor-assistant-answers.json "$@"
  fi
  echo "install-from-github.sh: pass --answers with a completed interview JSON when stdin is not a TTY." >&2
  echo "Or run the interview in Cursor via /cursor-assistant:setup-workspace." >&2
  exit 1
fi

exec python3 "${PKG}/cursorAssistant.py" configure --workspace "$(pwd)" "$@"
