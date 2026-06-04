#!/usr/bin/env python3
"""Fail when manifest/catalog or dogfood .cursor/ drift from package sources (CI + pre-commit)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "template/setup/install-manifest.json"
CATALOG = REPO_ROOT / "template/setup/catalog.json"
SYNC_HINT = "  → Run: bash scripts/sync_managed_surfaces.sh\n  → Then commit template/setup/*.json and .cursor/"


def _run_generate() -> None:
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/generate.py"), "--package-root", str(REPO_ROOT)],
        cwd=REPO_ROOT,
        check=True,
    )


def _git_diff(paths: list[Path]) -> str:
    rel = [str(p.relative_to(REPO_ROOT)) for p in paths]
    result = subprocess.run(
        ["git", "diff", "--", *rel],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


def check_manifest_catalog() -> list[str]:
    _run_generate()
    issues: list[str] = []
    diff = _git_diff([MANIFEST, CATALOG])
    if diff.strip():
        issues.append(
            "install-manifest.json or catalog.json is out of date (managed source hashes changed)."
        )
    return issues


def check_dogfood() -> list[str]:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from scripts.lifecycle import engine  # noqa: E402

    report = engine.inspect(REPO_ROOT, REPO_ROOT)
    missing = [f["id"] for f in report.get("files", []) if f.get("status") == "missing"]
    stale = [f["id"] for f in report.get("files", []) if f.get("status") == "stale"]
    state = report.get("installState")
    if state == "installed" and not missing and not stale:
        return []
    parts = [f"dogfood installState={state!r}"]
    if missing:
        parts.append(f"missing: {', '.join(missing)}")
    if stale:
        parts.append(f"stale: {', '.join(stale)}")
    return ["; ".join(parts)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-dogfood",
        action="store_true",
        help="Only check manifest/catalog regeneration (faster)",
    )
    args = parser.parse_args()

    issues = check_manifest_catalog()
    if not args.skip_dogfood:
        issues.extend(check_dogfood())

    if not issues:
        print("check_package_sync: ok (manifest, catalog, dogfood)")
        return 0

    print("check_package_sync: FAILED", file=sys.stderr)
    for item in issues:
        print(f"  - {item}", file=sys.stderr)
    print(SYNC_HINT, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
