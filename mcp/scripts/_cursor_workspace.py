"""Vendored from packages/cursor-mcp-shared — run scripts/vendor_mcp_shared.py to refresh."""

from __future__ import annotations

import json
from pathlib import Path

LOCKFILE_REL = Path(".cursor") / "cursorAssistant-lock.json"
MARKER_DIRS = (".cursor",)
PACKAGE_MARKER = "cursorAssistant.py"


def is_workspace_root(candidate: Path) -> bool:
    if (candidate / LOCKFILE_REL).is_file():
        return True
    if any((candidate / name).is_dir() for name in MARKER_DIRS):
        return True
    return (candidate / PACKAGE_MARKER).is_file()


def discover_workspace_root(script_path: Path) -> Path:
    resolved = script_path.resolve()
    for candidate in resolved.parents:
        if is_workspace_root(candidate):
            return candidate
    fallback_index = min(3, len(resolved.parents) - 1)
    return resolved.parents[fallback_index]


def workspace_is_valid(root: Path) -> bool:
    return (root / ".cursor").is_dir()


def read_lockfile(root: Path) -> dict | None:
    path = root / LOCKFILE_REL
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def key_commands_path(root: Path) -> Path:
    return root / "README.md"
