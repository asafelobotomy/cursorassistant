#!/usr/bin/env bash
# Install cursorAssistant into a consumer workspace (individual / plugin-first path).
set -euo pipefail

WORKSPACE="${1:-.}"
shift || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

exec python3 "${PKG_ROOT}/cursorAssistant.py" configure \
  --workspace "${WORKSPACE}" \
  --package-root "${PKG_ROOT}" \
  "$@"
