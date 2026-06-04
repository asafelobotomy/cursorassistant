"""Resolve cursorAssistant package root for CLI, MCP, and plugin installs."""

from __future__ import annotations

import json
import os
from pathlib import Path

_PACKAGE_MARKERS = (
    "cursorAssistant.py",
    "template/setup/install-policy.json",
    "VERSION",
)


def is_package_root(path: Path) -> bool:
    root = path.resolve()
    if not root.is_dir():
        return False
    return all((root / marker).exists() for marker in _PACKAGE_MARKERS)


def _lockfile_package_root(workspace: Path) -> Path | None:
    lock_path = workspace / ".cursor" / "cursorAssistant-lock.json"
    if not lock_path.is_file():
        return None
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    package_block = lock.get("package") if isinstance(lock, dict) else None
    if not isinstance(package_block, dict):
        return None
    value = package_block.get("packageRoot")
    if not isinstance(value, str) or not value.strip():
        return None
    raw = Path(value).expanduser()
    root = (workspace / raw).resolve() if not raw.is_absolute() else raw.resolve()
    return root if is_package_root(root) else None


def _walk_parents_for_package(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        if is_package_root(directory):
            return directory.resolve()
    return None


def _scan_cursor_plugin_dirs() -> Path | None:
    home = Path.home()
    bases = (
        home / ".cursor" / "plugins",
        home / ".cursor" / "plugins" / "local",
    )
    candidates: list[Path] = []
    for base in bases:
        if not base.is_dir():
            continue
        for cli in base.rglob("cursorAssistant.py"):
            root = cli.parent
            if is_package_root(root):
                candidates.append(root.resolve())
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def module_anchor_root() -> Path | None:
    """Package root when this code runs from an installed cursorAssistant checkout."""
    anchor = Path(__file__).resolve().parents[2]
    return anchor.resolve() if is_package_root(anchor) else None


def find_package_root(
    workspace: Path,
    explicit: Path | str | None = None,
) -> Path:
    if explicit is not None:
        root = Path(explicit).expanduser().resolve()
        if not is_package_root(root):
            raise FileNotFoundError(
                f"Not a cursorAssistant package (missing markers): {root}"
            )
        return root

    env = os.environ.get("CURSOR_ASSISTANT_PACKAGE_ROOT", "").strip()
    if env:
        root = Path(env).expanduser().resolve()
        if not is_package_root(root):
            raise FileNotFoundError(
                f"CURSOR_ASSISTANT_PACKAGE_ROOT is not a valid package: {root}"
            )
        return root

    current = Path.home() / ".local" / "share" / "cursorassistant" / "current"
    if current.is_symlink() or current.is_dir():
        resolved = current.resolve()
        if is_package_root(resolved):
            return resolved

    from_lock = _lockfile_package_root(workspace)
    if from_lock is not None:
        return from_lock

    from_parents = _walk_parents_for_package(workspace)
    if from_parents is not None:
        return from_parents

    from_plugins = _scan_cursor_plugin_dirs()
    if from_plugins is not None:
        return from_plugins

    anchor = module_anchor_root()
    if anchor is not None:
        return anchor

    raise FileNotFoundError(
        "Could not find cursorAssistant package root. Install the cursor-assistant "
        "install-from-github.sh, a clone of this repository, or set "
        "CURSOR_ASSISTANT_PACKAGE_ROOT."
    )
