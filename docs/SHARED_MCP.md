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

Run this after editing the package sources, before release or CI manifest checks.

## Install as a library

```sh
pip install ./packages/cursor-mcp-shared
```

## xanadAssistant

xanadAssistant can depend on `cursor-mcp-shared` and drop duplicated discovery logic in its MCP scripts. Path markers differ (`.github/` vs `.cursor/`); adapters can wrap `discover_workspace_root` or extend `is_workspace_root` for Copilot lockfiles.

See also [MCP_SYNC.md](MCP_SYNC.md) for script porting from xanad.
