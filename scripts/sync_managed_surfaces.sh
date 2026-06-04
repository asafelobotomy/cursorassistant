#!/usr/bin/env bash
# Regenerate install manifest/catalog and refresh the package repo dogfood .cursor/ install.
# Run after editing AGENTS.md, agents/, skills/, template/rules/, or install-policy.json.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "sync_managed_surfaces: generate manifest + catalog"
python3 scripts/generate.py --package-root .

echo "sync_managed_surfaces: update dogfood install (.cursor/)"
python3 cursorAssistant.py update --workspace . --package-root .

echo "sync_managed_surfaces: verify"
python3 scripts/check_package_sync.py

cat <<'EOF'

Next: stage and commit generated artifacts, for example:

  git add template/setup/install-manifest.json template/setup/catalog.json .cursor/
  git add AGENTS.md   # if you edited routing in the repo-root AGENTS.md

EOF
