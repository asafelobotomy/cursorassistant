#!/usr/bin/env python3
"""Sync MCP scripts from xanadAssistant with Cursor path adaptations.

Usage (from cursorAssistant repo root):

    python3 scripts/sync_mcp_from_xanad.py --xanad-root /path/to/xanadassistant

Copies selected scripts into mcp/scripts/ and applies path rewrites. Does not
overwrite cursorToolsMcp.py or `_cursor_*.py` shared modules.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

SKIP_SCRIPTS = {"cursorToolsMcp.py", "_cursor_workspace.py", "_cursor_mcp_util.py"}

DEFAULT_SCRIPTS = [
    "gitMcp.py",
    "timeMcp.py",
    "webMcp.py",
    "devDocsMcp.py",
    "securityMcp.py",
    "fsMcp.py",
    "workspaceTestingMcp.py",
    "_workspace_testing_shared.py",
    "memoryMcp.py",
    "_memory_mcp_shared.py",
]

REWRITES = [
    (".github/copilot-instructions.md", "README.md"),
    ('(".github").is_dir()', '(".cursor").is_dir()'),
    ("/ .github", "/ .cursor"),
    (".github/xanadAssistant-lock.json", ".cursor/cursorAssistant-lock.json"),
    (".github/xanad-assistant-lock.json", ".cursor/cursorAssistant-lock.json"),
    (".github/xanadAssistant/memory", ".cursor/cursorAssistant/memory"),
    (".github/mcp/scripts", ".cursor/mcp/scripts"),
    ('FastMCP("xanad', 'FastMCP("cursor'),
    (".github/copilot-instructions.md", "README.md"),
]


def adapt_content(text: str) -> str:
    for old, new in REWRITES:
        text = text.replace(old, new)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync MCP scripts from xanadAssistant")
    parser.add_argument("--xanad-root", required=True, help="Path to xanadAssistant checkout")
    parser.add_argument("--package-root", default=".", help="cursorAssistant repo root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    xanad_root = Path(args.xanad_root).resolve()
    package_root = Path(args.package_root).resolve()
    src_dir = xanad_root / "mcp" / "scripts"
    dest_dir = package_root / "mcp" / "scripts"

    if not src_dir.is_dir():
        print(f"ERROR: missing {src_dir}")
        return 1

    copied = 0
    for name in DEFAULT_SCRIPTS:
        if name in SKIP_SCRIPTS:
            continue
        source = src_dir / name
        if not source.is_file():
            print(f"skip (missing): {name}")
            continue
        dest = dest_dir / name
        text = source.read_text(encoding="utf-8")
        adapted = adapt_content(text)
        if args.dry_run:
            print(f"would write: {dest.relative_to(package_root)}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(adapted, encoding="utf-8")
            print(f"wrote: {dest.relative_to(package_root)}")
        copied += 1

    print(f"done: {copied} script(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
