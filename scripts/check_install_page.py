#!/usr/bin/env python3
"""Regenerate install page and fail if install/index.html or deeplinks.json drift from VERSION."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL = REPO_ROOT / "install"
VERSION_FILE = REPO_ROOT / "VERSION"


def main() -> int:
    version = VERSION_FILE.read_text(encoding="utf-8").strip().splitlines()[0]
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/generate_install_page.py")],
        cwd=REPO_ROOT,
        check=True,
    )
    html = (INSTALL / "index.html").read_text(encoding="utf-8")
    deeplinks = (INSTALL / "deeplinks.json").read_text(encoding="utf-8")
    issues: list[str] = []
    if f"Version <strong>{version}</strong>" not in html and f"Version {version}" not in html:
        issues.append(f"index.html missing version {version}")
    if f'"version": "{version}"' not in deeplinks:
        issues.append(f"deeplinks.json version mismatch (expected {version})")
    if f"v{version}" not in deeplinks and f'branch \\"v{version}\\"' not in deeplinks:
        issues.append(f"deeplinks.json missing git tag v{version}")
    if f"v0.12." in html or "v0.12." in deeplinks:
        issues.append("install artifacts still reference v0.12.x")
    diff = subprocess.run(
        ["git", "diff", "--", "install/index.html", "install/deeplinks.json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if diff.stdout.strip():
        issues.append(
            "install/index.html or deeplinks.json out of date — run: python3 scripts/generate_install_page.py"
        )
    if issues:
        for item in issues:
            print(f"check_install_page: {item}", file=sys.stderr)
        return 1
    print(f"check_install_page: ok (v{version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
