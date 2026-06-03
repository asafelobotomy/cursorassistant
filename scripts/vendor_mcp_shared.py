#!/usr/bin/env python3
"""Copy cursor-mcp-shared package modules into mcp/scripts vendored shims."""

from __future__ import annotations

from pathlib import Path

VENDOR_MAP = {
    "workspace.py": "_cursor_workspace.py",
    "mcp_util.py": "_cursor_mcp_util.py",
}

HEADER = '''"""Vendored from packages/cursor-mcp-shared — run scripts/vendor_mcp_shared.py to refresh."""

from __future__ import annotations

'''


def strip_module_docstring(body: str) -> str:
    stripped = body.lstrip()
    if not (stripped.startswith('"""') or stripped.startswith("'''")):
        return body
    quote = stripped[:3]
    rest = stripped[3:]
    close = rest.find(quote)
    if close < 0:
        return body
    return rest[close + 3 :].lstrip("\n")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    src_root = repo_root / "packages" / "cursor-mcp-shared" / "cursor_mcp_shared"
    dest_root = repo_root / "mcp" / "scripts"
    for src_name, dest_name in VENDOR_MAP.items():
        source = src_root / src_name
        dest = dest_root / dest_name
        body = strip_module_docstring(source.read_text(encoding="utf-8"))
        dest.write_text(HEADER + body, encoding="utf-8")
        print(f"vendored → {dest.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
