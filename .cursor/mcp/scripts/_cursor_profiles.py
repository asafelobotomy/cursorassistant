"""Vendored from packages/cursor-mcp-shared — run scripts/vendor_mcp_shared.py to refresh."""

from __future__ import annotations

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

LOCKFILE_CURSOR = Path(".cursor") / "cursorAssistant-lock.json"
LOCKFILE_XANAD = Path(".github") / "xanadAssistant-lock.json"


@dataclass(frozen=True)
class WorkspaceProfile:
    name: str
    lockfile_rel: Path
    marker_dirs: tuple[str, ...]
    package_marker: str | None = None


CURSOR = WorkspaceProfile(
    name="cursor",
    lockfile_rel=LOCKFILE_CURSOR,
    marker_dirs=(".cursor",),
    package_marker="cursorAssistant.py",
)

XANAD = WorkspaceProfile(
    name="xanad",
    lockfile_rel=LOCKFILE_XANAD,
    marker_dirs=(".github",),
    package_marker="xanadAssistant.py",
)


def lockfile_rel_for(profile: WorkspaceProfile | str | None) -> Path:
    if profile is None or profile == "cursor" or profile == CURSOR:
        return CURSOR.lockfile_rel
    if profile == "xanad" or profile == XANAD:
        return XANAD.lockfile_rel
    if isinstance(profile, WorkspaceProfile):
        return profile.lockfile_rel
    raise ValueError(f"unknown workspace profile: {profile!r}")
