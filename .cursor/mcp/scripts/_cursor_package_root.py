"""Package root discovery for cursorTools MCP (no scripts.lifecycle dependency)."""

from __future__ import annotations

import json
import os
from pathlib import Path

_MARKERS = (
    "cursorAssistant.py",
    "template/setup/install-policy.json",
    "VERSION",
)


def is_package_root(path: Path) -> bool:
    root = path.resolve()
    return root.is_dir() and all((root / m).exists() for m in _MARKERS)


def find_package_root(workspace: Path) -> Path | None:
    env = os.environ.get("CURSOR_ASSISTANT_PACKAGE_ROOT", "").strip()
    if env:
        root = Path(env).expanduser().resolve()
        return root if is_package_root(root) else None

    lock_path = workspace / ".cursor" / "cursorAssistant-lock.json"
    if lock_path.is_file():
        try:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            package_block = lock.get("package") if isinstance(lock, dict) else None
            if isinstance(package_block, dict):
                value = package_block.get("packageRoot")
                if isinstance(value, str) and value.strip():
                    raw = Path(value).expanduser()
                    root = (workspace / raw).resolve() if not raw.is_absolute() else raw.resolve()
                    if is_package_root(root):
                        return root
        except (OSError, json.JSONDecodeError):
            pass

    current = workspace.resolve()
    for directory in (current, *current.parents):
        if is_package_root(directory):
            return directory.resolve()

    home = Path.home()
    for base in (home / ".cursor" / "plugins", home / ".cursor" / "plugins" / "local"):
        if not base.is_dir():
            continue
        candidates = [
            cli.parent.resolve()
            for cli in base.rglob("cursorAssistant.py")
            if is_package_root(cli.parent)
        ]
        if candidates:
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            return candidates[0]
    return None
