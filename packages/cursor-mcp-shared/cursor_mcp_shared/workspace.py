"""Workspace discovery for cursorAssistant and xanadAssistant MCP servers."""

from __future__ import annotations

import json
import os
from pathlib import Path

from cursor_mcp_shared.profiles import CURSOR, XANAD, WorkspaceProfile, lockfile_rel_for

_DEFAULT_PROFILE = CURSOR
if os.environ.get("CURSOR_MCP_PROFILE", "").strip().lower() == "xanad":
    _DEFAULT_PROFILE = XANAD


def active_profile(explicit: WorkspaceProfile | str | None = None) -> WorkspaceProfile:
    if explicit is None:
        return _DEFAULT_PROFILE
    if explicit == "cursor" or explicit is CURSOR:
        return CURSOR
    if explicit == "xanad" or explicit is XANAD:
        return XANAD
    if isinstance(explicit, WorkspaceProfile):
        return explicit
    raise ValueError(f"unknown workspace profile: {explicit!r}")


def is_workspace_root(
    candidate: Path,
    profile: WorkspaceProfile | str | None = None,
) -> bool:
    prof = active_profile(profile)
    if (candidate / prof.lockfile_rel).is_file():
        return True
    if any((candidate / name).is_dir() for name in prof.marker_dirs):
        return True
    if prof.package_marker and (candidate / prof.package_marker).is_file():
        return True
    return False


def discover_workspace_root(
    script_path: Path,
    profile: WorkspaceProfile | str | None = None,
) -> Path:
    prof = active_profile(profile)
    resolved = script_path.resolve()
    for candidate in resolved.parents:
        if is_workspace_root(candidate, prof):
            return candidate
    fallback_index = min(3, len(resolved.parents) - 1)
    return resolved.parents[fallback_index]


def workspace_is_valid(root: Path, profile: WorkspaceProfile | str | None = None) -> bool:
    prof = active_profile(profile)
    return any((root / name).is_dir() for name in prof.marker_dirs)


def read_lockfile(root: Path, profile: WorkspaceProfile | str | None = None) -> dict | None:
    path = root / lockfile_rel_for(active_profile(profile))
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def key_commands_path(root: Path) -> Path:
    return root / "README.md"
