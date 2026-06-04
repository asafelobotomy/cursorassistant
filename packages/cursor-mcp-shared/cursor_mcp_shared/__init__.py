"""Shared MCP helpers for Cursor workspace servers."""

from cursor_mcp_shared.mcp_util import build_tool_result, tail_text
from cursor_mcp_shared.workspace import (
    discover_workspace_root,
    is_workspace_root,
    key_commands_path,
    read_lockfile,
    workspace_is_valid,
)

__all__ = [
    "build_tool_result",
    "discover_workspace_root",
    "is_workspace_root",
    "key_commands_path",
    "read_lockfile",
    "tail_text",
    "workspace_is_valid",
]
