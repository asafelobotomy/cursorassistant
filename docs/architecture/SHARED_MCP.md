# Shared MCP package (v0.7+)

`packages/cursor-mcp-shared/` is the canonical home for workspace discovery and MCP tool-result helpers used by cursorAssistant MCP stdio servers.

## Layout

| Path | Role |
| --- | --- |
| `cursor_mcp_shared/workspace.py` | `discover_workspace_root`, lockfile read |
| `cursor_mcp_shared/mcp_util.py` | `build_tool_result`, `tail_text` |

## Vendor into the repo

Consumer installs receive vendored shims under `mcp/scripts/_cursor_*.py`:

```sh
python3 scripts/vendor_mcp_shared.py
```

Run this after editing the package sources, before release or CI manifest checks. See [../operations/MCP_MAINTENANCE.md](../operations/MCP_MAINTENANCE.md).

## Install as a library

```sh
pip install ./packages/cursor-mcp-shared
```

## Markers

Workspace discovery looks for:

- `.cursor/cursorAssistant-lock.json`
- `.cursor/` directory
- `cursorAssistant.py` at repo root
