#!/usr/bin/env bash
# Primary consumer install for cursorAssistant (GitHub one-liner).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash
#   curl -fsSL .../install-from-github.sh | bash -s -- /path/to/your-project
#   bash scripts/install-from-github.sh . -y
#
# Environment:
#   CURSOR_ASSISTANT_VERSION   Tag or branch (default: read from VERSION in clone, else 0.12.0)
#   CURSOR_ASSISTANT_HOME      Install base (default: ~/.local/share/cursorassistant)
#   CURSOR_ASSISTANT_REPO      Git remote (default: this GitHub repo)
#   CURSOR_ASSISTANT_YES=1     Non-interactive configure (same as -y)
#   CURSOR_ASSISTANT_SKIP_PLUGIN=1  Do not symlink ~/.cursor/plugins/local/cursor-assistant
set -euo pipefail

REPO_URL="${CURSOR_ASSISTANT_REPO:-https://github.com/asafelobotomy/cursorassistant.git}"
DEFAULT_VERSION="0.12.0"
VERSION="${CURSOR_ASSISTANT_VERSION:-$DEFAULT_VERSION}"
INSTALL_BASE="${CURSOR_ASSISTANT_HOME:-${HOME}/.local/share/cursorassistant}"
INSTALL_DIR="${INSTALL_BASE}/${VERSION}"
PLUGIN_LINK="${CURSOR_ASSISTANT_PLUGIN_DIR:-${HOME}/.cursor/plugins/local/cursor-assistant}"

WORKSPACE="${1:-.}"
shift || true
EXTRA_CONFIGURE=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes) EXTRA_CONFIGURE+=(--yes) ;;
    --dry-run) EXTRA_CONFIGURE+=(--dry-run) ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done
if [[ "${CURSOR_ASSISTANT_YES:-}" == "1" ]]; then
  EXTRA_CONFIGURE+=(--yes)
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required (3.10+)." >&2
  exit 1
fi
if ! command -v git >/dev/null 2>&1; then
  echo "git is required to download cursorAssistant." >&2
  exit 1
fi

install_package() {
  if [[ -f "${INSTALL_DIR}/cursorAssistant.py" ]]; then
    echo "Package already present: ${INSTALL_DIR}"
    return
  fi
  mkdir -p "${INSTALL_BASE}"
  echo "Downloading cursorAssistant (${VERSION}) to ${INSTALL_DIR} ..."
  if git clone --depth 1 --branch "v${VERSION}" "${REPO_URL}" "${INSTALL_DIR}" 2>/dev/null; then
    :
  elif git clone --depth 1 --branch "${VERSION}" "${REPO_URL}" "${INSTALL_DIR}" 2>/dev/null; then
    :
  else
    echo "Tag v${VERSION} not found; cloning default branch into ${INSTALL_DIR} ..."
    git clone --depth 1 "${REPO_URL}" "${INSTALL_DIR}"
    if [[ -f "${INSTALL_DIR}/VERSION" ]]; then
      VERSION="$(head -n1 "${INSTALL_DIR}/VERSION" | tr -d '\r')"
      echo "Using VERSION from clone: ${VERSION}"
    fi
  fi
}

link_plugin() {
  if [[ "${CURSOR_ASSISTANT_SKIP_PLUGIN:-}" == "1" ]]; then
    return
  fi
  mkdir -p "$(dirname "${PLUGIN_LINK}")"
  if [[ -e "${PLUGIN_LINK}" && ! -L "${PLUGIN_LINK}" ]]; then
    echo "Note: ${PLUGIN_LINK} exists and is not a symlink; skipping plugin link." >&2
    return
  fi
  ln -sfn "${INSTALL_DIR}" "${PLUGIN_LINK}"
  echo "Cursor local plugin: ${PLUGIN_LINK} -> ${INSTALL_DIR}"
  echo "In Cursor: Developer → Reload Window (plugin agents/skills/commands)."
}

run_configure() {
  export CURSOR_ASSISTANT_PACKAGE_ROOT="${INSTALL_DIR}"
  cd "${WORKSPACE}"
  WORKSPACE="$(pwd)"
  echo "Configuring workspace: ${WORKSPACE}"
  python3 "${INSTALL_DIR}/cursorAssistant.py" configure \
    --workspace "${WORKSPACE}" \
    --package-root "${INSTALL_DIR}" \
    "${EXTRA_CONFIGURE[@]}"
  echo ""
  echo "Done. Reload Cursor, then enable cursorTools under Settings → MCP if you use MCP."
}

install_package
link_plugin
run_configure
