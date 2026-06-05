#!/usr/bin/env bash
# Minimal bootstrap: download cursorAssistant + local plugin symlink (no project configure).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/bootstrap-from-github.sh | bash
#   bash scripts/bootstrap-from-github.sh
#
# Security: review this script before piping to bash. Prefer cloning the release tag yourself
# if you do not trust raw.githubusercontent.com.
set -euo pipefail

ALLOWED_REPO="https://github.com/asafelobotomy/cursorassistant.git"
REPO_URL="${CURSOR_ASSISTANT_REPO:-$ALLOWED_REPO}"
DEFAULT_VERSION="0.15.0"
VERSION="${CURSOR_ASSISTANT_VERSION:-$DEFAULT_VERSION}"
INSTALL_BASE="${CURSOR_ASSISTANT_HOME:-${HOME}/.local/share/cursorassistant}"
INSTALL_DIR="${INSTALL_BASE}/${VERSION}"
PLUGIN_LINK="${CURSOR_ASSISTANT_PLUGIN_DIR:-${HOME}/.cursor/plugins/local/cursor-assistant}"

if [[ "${REPO_URL}" != "${ALLOWED_REPO}" ]]; then
  echo "Unsupported CURSOR_ASSISTANT_REPO: ${REPO_URL}" >&2
  echo "Allowed: ${ALLOWED_REPO}" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required (3.10+)." >&2
  exit 1
fi
if ! command -v git >/dev/null 2>&1; then
  echo "git is required." >&2
  exit 1
fi

if [[ -f "${INSTALL_DIR}/cursorAssistant.py" ]]; then
  echo "Package already present: ${INSTALL_DIR}"
else
  mkdir -p "${INSTALL_BASE}"
  echo "Cloning cursorAssistant (${VERSION}) to ${INSTALL_DIR} ..."
  if ! git clone --depth 1 --branch "v${VERSION}" "${REPO_URL}" "${INSTALL_DIR}"; then
    echo "Failed to clone tag v${VERSION} from ${REPO_URL}" >&2
    echo "Check the tag exists or set CURSOR_ASSISTANT_VERSION." >&2
    exit 1
  fi
fi

if [[ ! -f "${INSTALL_DIR}/cursorAssistant.py" ]]; then
  echo "Invalid package at ${INSTALL_DIR}" >&2
  exit 1
fi

if [[ "${CURSOR_ASSISTANT_SKIP_PLUGIN:-}" != "1" ]]; then
  mkdir -p "$(dirname "${PLUGIN_LINK}")"
  if [[ -e "${PLUGIN_LINK}" && ! -L "${PLUGIN_LINK}" ]]; then
    echo "Note: ${PLUGIN_LINK} exists (not a symlink); skipping plugin link." >&2
  else
    ln -sfn "${INSTALL_DIR}" "${PLUGIN_LINK}"
    echo "Cursor local plugin: ${PLUGIN_LINK} -> ${INSTALL_DIR}"
  fi
fi

ln -sfn "${INSTALL_DIR}" "${INSTALL_BASE}/current"
echo "Bootstrap complete: ${INSTALL_DIR}"
echo "Next: open your project in Cursor, enable cursorAssistant MCP, then /cursor-assistant:setup-workspace (interview)."
