#!/usr/bin/env bash
# MCP entrypoint: ensure bootstrap package exists (git only), then run cursorToolsMcp.
# Referenced from install deeplinks — no curl|bash in this path.
set -euo pipefail

DEFAULT_VERSION="0.12.1"
ALLOWED_REPO="https://github.com/asafelobotomy/cursorassistant.git"
REPO_URL="${CURSOR_ASSISTANT_REPO:-$ALLOWED_REPO}"
VERSION="${CURSOR_ASSISTANT_VERSION:-$DEFAULT_VERSION}"
INSTALL_BASE="${CURSOR_ASSISTANT_HOME:-${HOME}/.local/share/cursorassistant}"
INSTALL_DIR="${INSTALL_BASE}/${VERSION}"
CURRENT="${INSTALL_BASE}/current"
PLUGIN_LINK="${CURSOR_ASSISTANT_PLUGIN_DIR:-${HOME}/.cursor/plugins/local/cursor-assistant}"

if [[ "${REPO_URL}" != "${ALLOWED_REPO}" ]]; then
  echo "cursorAssistant: unsupported CURSOR_ASSISTANT_REPO=${REPO_URL}" >&2
  echo "Allowed: ${ALLOWED_REPO}" >&2
  exit 1
fi

bootstrap() {
  if [[ -f "${INSTALL_DIR}/cursorAssistant.py" ]]; then
    return 0
  fi
  if ! command -v git >/dev/null 2>&1; then
    echo "cursorAssistant bootstrap requires git on PATH." >&2
    exit 1
  fi
  mkdir -p "${INSTALL_BASE}"
  echo "Cloning cursorAssistant v${VERSION} to ${INSTALL_DIR} ..." >&2
  if ! git clone --depth 1 --branch "v${VERSION}" "${REPO_URL}" "${INSTALL_DIR}"; then
    echo "cursorAssistant: failed to clone tag v${VERSION}. Set CURSOR_ASSISTANT_VERSION or run scripts/bootstrap-from-github.sh." >&2
    exit 1
  fi
}

link_plugin() {
  if [[ "${CURSOR_ASSISTANT_SKIP_PLUGIN:-}" == "1" ]]; then
    return 0
  fi
  mkdir -p "$(dirname "${PLUGIN_LINK}")"
  if [[ -e "${PLUGIN_LINK}" && ! -L "${PLUGIN_LINK}" ]]; then
    echo "Note: ${PLUGIN_LINK} is not a symlink; skipping." >&2
    return 0
  fi
  ln -sfn "${INSTALL_DIR}" "${PLUGIN_LINK}"
}

bootstrap
link_plugin
ln -sfn "${INSTALL_DIR}" "${CURRENT}"

TOOLS="${CURRENT}/mcp/scripts/cursorToolsMcp.py"
if [[ ! -f "${TOOLS}" ]]; then
  echo "cursorAssistant: missing ${TOOLS}" >&2
  exit 1
fi

exec uvx --from mcp[cli] mcp run "${TOOLS}"
