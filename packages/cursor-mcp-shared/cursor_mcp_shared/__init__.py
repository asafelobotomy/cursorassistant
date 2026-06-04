"""Shared MCP helpers for Cursor and Copilot workspace servers."""

from cursor_mcp_shared.mcp_util import build_tool_result, tail_text
from cursor_mcp_shared.profiles import CURSOR, XANAD, WorkspaceProfile
from cursor_mcp_shared.workspace import (
    active_profile,
    discover_workspace_root,
    is_workspace_root,
    key_commands_path,
    read_lockfile,
    workspace_is_valid,
)

__all__ = [
    "CURSOR",
    "XANAD",
    "WorkspaceProfile",
    "active_profile",
    "build_tool_result",
    "discover_workspace_root",
    "is_workspace_root",
    "key_commands_path",
    "read_lockfile",
    "tail_text",
    "workspace_is_valid",
]
