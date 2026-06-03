"""MCP script discovery for cursorAssistant installs."""

from __future__ import annotations

from pathlib import Path

from scripts.lifecycle.models import ManagedEntry


def mcp_script_entries(package_root: Path, *, include_bundle: bool) -> list[ManagedEntry]:
    scripts_dir = package_root / "mcp" / "scripts"
    if not scripts_dir.is_dir():
        return []

    entries: list[ManagedEntry] = []
    always_install = {"cursorToolsMcp.py"}
    shared_modules = ("_cursor_workspace.py", "_cursor_mcp_util.py")
    for name in shared_modules:
        path = scripts_dir / name
        if path.is_file():
            entries.append(
                ManagedEntry(
                    entry_id=f"mcp.shared.{path.stem}",
                    source_rel=f"mcp/scripts/{name}",
                    target_rel=f".cursor/mcp/scripts/{name}",
                    layer="core",
                    strategy="replace",
                    required_when=None,
                )
            )
    for path in sorted(scripts_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        required_when = None if path.name in always_install else {"mcp.enabled": True}
        if not include_bundle and path.name not in always_install:
            continue
        stem = path.stem
        entries.append(
            ManagedEntry(
                entry_id=f"mcp.{stem}",
                source_rel=f"mcp/scripts/{path.name}",
                target_rel=f".cursor/mcp/scripts/{path.name}",
                layer="core",
                strategy="replace",
                required_when=required_when,
            )
        )

    if include_bundle:
        for path in sorted(scripts_dir.glob("_*.py")):
            entries.append(
                ManagedEntry(
                    entry_id=f"mcp.shared.{path.stem}",
                    source_rel=f"mcp/scripts/{path.name}",
                    target_rel=f".cursor/mcp/scripts/{path.name}",
                    layer="core",
                    strategy="replace",
                    required_when={"mcp.enabled": True},
                )
            )
    return entries
