#!/usr/bin/env python3
"""Fail if the package repo's dogfood .cursor/ install is incomplete or drifted.

Prefer `python3 scripts/check_package_sync.py` (manifest + dogfood). This script
remains for direct dogfood-only checks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.lifecycle import engine  # noqa: E402


def main() -> int:
    report = engine.inspect(REPO_ROOT, REPO_ROOT)
    missing = [f["id"] for f in report.get("files", []) if f.get("status") == "missing"]
    stale = [f["id"] for f in report.get("files", []) if f.get("status") == "stale"]
    state = report.get("installState")
    ok = state == "installed" and not missing and not stale
    if ok:
        print("dogfood install: ok (installed, no missing/stale managed files)")
        return 0
    payload = {
        "installState": state,
        "missing": missing,
        "stale": stale,
        "repairReasons": report.get("repairReasons", []),
    }
    print(json.dumps(payload, indent=2), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
