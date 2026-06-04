#!/usr/bin/env bash
# Full install: bootstrap package + configure current workspace (interview + project files).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash
#   curl -fsSL .../install-from-github.sh | bash -s -- /path/to/your-project
#   bash scripts/install-from-github.sh . -y
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_BASE="${CURSOR_ASSISTANT_HOME:-${HOME}/.local/share/cursorassistant}"

WORKSPACE="${1:-.}"
shift || true

"${SCRIPT_DIR}/bootstrap-from-github.sh"

PKG="${CURSOR_ASSISTANT_PACKAGE_ROOT:-${INSTALL_BASE}/current}"
if [[ ! -f "${PKG}/cursorAssistant.py" ]]; then
  echo "cursorAssistant package not found at ${PKG}" >&2
  exit 1
fi

cd "${WORKSPACE}"
exec python3 "${PKG}/cursorAssistant.py" configure --workspace "$(pwd)" "$@"
