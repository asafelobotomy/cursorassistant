#!/usr/bin/env python3
"""Verify cursor-mcp-shared XANAD profile (integration readiness for xanadAssistant)."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PKG = REPO_ROOT / "packages" / "cursor-mcp-shared"
sys.path.insert(0, str(PKG))

from cursor_mcp_shared.profiles import XANAD  # noqa: E402
from cursor_mcp_shared.workspace import discover_workspace_root, is_workspace_root, read_lockfile  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".github").mkdir()
        lock = root / ".github" / "xanadAssistant-lock.json"
        lock.write_text('{"schemaVersion":"0.1.0"}', encoding="utf-8")
        script = root / ".github" / "mcp" / "scripts" / "exampleMcp.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("# stub\n", encoding="utf-8")
        if not is_workspace_root(root, profile=XANAD):
            print("FAIL: XANAD profile did not detect .github lockfile", file=sys.stderr)
            return 1
        if discover_workspace_root(script, profile=XANAD) != root.resolve():
            print("FAIL: discover_workspace_root(XANAD) returned wrong root", file=sys.stderr)
            return 1
        payload = read_lockfile(root, profile=XANAD)
        if not payload:
            print("FAIL: read_lockfile(XANAD) returned empty", file=sys.stderr)
            return 1
    print("verify_xanad_profile: ok — see docs/XANAD_INTEGRATION.md for xanad repo steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
