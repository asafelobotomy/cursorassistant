"""MCP script discovery for cursorAssistant installs."""

from __future__ import annotations

from pathlib import Path

from scripts.lifecycle.mcp_config import DEPRECATED_SCRIPT_NAMES
from scripts.lifecycle.models import ManagedEntry

SHARED_MODULES = ("_cursor_profiles.py", "_cursor_workspace.py", "_cursor_mcp_util.py")
ALWAYS_INSTALL = frozenset({"cursorToolsMcp.py"})
EXTENSION_SCRIPTS = frozenset({"devDocsMcp.py", "memoryMcp.py"})
BUNDLE_HELPERS = frozenset({"_memory_mcp_shared.py", "_workspace_testing_shared.py"})
PACK_SCRIPTS: dict[str, frozenset[str]] = {
    "secure": frozenset({"securityMcp.py", "secureOsv.py"}),
    "tdd": frozenset({"workspaceTestingMcp.py", "tddTestRunner.py"}),
    "lean": frozenset({"leanContextBudget.py", "leanTestReporter.py"}),
}


def _entry(
    *,
    entry_id: str,
    source_rel: str,
    target_rel: str,
    layer: str = "core",
    required_when: dict | None = None,
    pack: str | None = None,
) -> ManagedEntry:
    return ManagedEntry(
        entry_id=entry_id,
        source_rel=source_rel,
        target_rel=target_rel,
        layer=layer,
        strategy="replace",
        required_when=required_when,
        pack=pack,
    )


def mcp_script_entries(
    package_root: Path,
    *,
    mcp_enabled: bool,
    selected_packs: list[str],
) -> list[ManagedEntry]:
    scripts_dir = package_root / "mcp" / "scripts"
    if not scripts_dir.is_dir():
        return []

    entries: list[ManagedEntry] = []
    for name in SHARED_MODULES:
        path = scripts_dir / name
        if path.is_file():
            entries.append(
                _entry(
                    entry_id=f"mcp.shared.{path.stem}",
                    source_rel=f"mcp/scripts/{name}",
                    target_rel=f".cursor/mcp/scripts/{name}",
                )
            )

    for name in sorted(ALWAYS_INSTALL):
        path = scripts_dir / name
        if path.is_file():
            entries.append(
                _entry(
                    entry_id=f"mcp.{path.stem}",
                    source_rel=f"mcp/scripts/{name}",
                    target_rel=f".cursor/mcp/scripts/{name}",
                )
            )

    if mcp_enabled:
        for name in sorted(EXTENSION_SCRIPTS):
            path = scripts_dir / name
            if path.is_file():
                entries.append(
                    _entry(
                        entry_id=f"mcp.{Path(name).stem}",
                        source_rel=f"mcp/scripts/{name}",
                        target_rel=f".cursor/mcp/scripts/{name}",
                        required_when={"mcp.enabled": True},
                    )
                )
        for path in sorted(scripts_dir.glob("_*.py")):
            if path.name in SHARED_MODULES or path.name in DEPRECATED_SCRIPT_NAMES:
                continue
            if path.name in BUNDLE_HELPERS:
                entries.append(
                    _entry(
                        entry_id=f"mcp.shared.{path.stem}",
                        source_rel=f"mcp/scripts/{path.name}",
                        target_rel=f".cursor/mcp/scripts/{path.name}",
                        required_when={"mcp.enabled": True},
                    )
                )

    for pack_id in selected_packs:
        script_names = PACK_SCRIPTS.get(pack_id, frozenset())
        for name in sorted(script_names):
            core_path = scripts_dir / name
            pack_path = package_root / "packs" / pack_id / "mcp" / name
            if pack_path.is_file():
                source_rel = f"packs/{pack_id}/mcp/{name}"
            elif core_path.is_file():
                source_rel = f"mcp/scripts/{name}"
            else:
                continue
            entries.append(
                _entry(
                    entry_id=f"packs.{pack_id}.mcp.{Path(name).stem}",
                    source_rel=source_rel,
                    target_rel=f".cursor/mcp/scripts/{name}",
                    layer="pack",
                    pack=pack_id,
                )
            )

    return entries


def expected_script_names(
    package_root: Path,
    *,
    mcp_enabled: bool,
    selected_packs: list[str],
) -> set[str]:
    names = set(SHARED_MODULES) | set(ALWAYS_INSTALL)
    if mcp_enabled:
        names |= EXTENSION_SCRIPTS | BUNDLE_HELPERS
    for pack_id in selected_packs:
        names |= PACK_SCRIPTS.get(pack_id, frozenset())
    return names
