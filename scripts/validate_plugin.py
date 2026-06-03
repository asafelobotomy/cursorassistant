#!/usr/bin/env python3
"""Validate Cursor marketplace plugin manifest against package sources."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    plugin_path = repo_root / ".cursor-plugin" / "plugin.json"
    version_path = repo_root / "VERSION"

    if not plugin_path.is_file():
        print(f"ERROR: missing {plugin_path}", file=sys.stderr)
        return 1

    plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    version = version_path.read_text(encoding="utf-8").strip().splitlines()[0]
    errors: list[str] = []

    name = plugin.get("name", "")
    if not NAME_PATTERN.match(name):
        errors.append(f"plugin name must be kebab-case: {name!r}")

    if plugin.get("version") != version:
        errors.append(f"plugin version {plugin.get('version')!r} != VERSION {version!r}")

    for key in ("agents", "skills", "rules"):
        value = plugin.get(key)
        if value is None:
            continue
        paths = value if isinstance(value, list) else [value]
        for rel in paths:
            if not (repo_root / rel).exists():
                errors.append(f"plugin path missing: {rel}")

    mcp_ref = plugin.get("mcpServers")
    if mcp_ref and not (repo_root / mcp_ref).is_file():
        errors.append(f"mcpServers path missing: {mcp_ref}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1

    print(f"plugin ok: {name} v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
