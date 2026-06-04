# MCP script maintenance

MCP stdio servers live in `mcp/scripts/` and install to `.cursor/mcp/scripts/` in consumer workspaces.

## Owned by cursorAssistant

| Script | Role |
| --- | --- |
| `cursorToolsMcp.py` | Wraps lifecycle CLI |
| `_cursor_workspace.py`, `_cursor_mcp_util.py` | Vendored from `packages/cursor-mcp-shared/` |
| `devDocsMcp.py`, `memoryMcp.py` | Optional extensions |
| Pack scripts under `packs/<pack>/mcp/` | Installed when pack selected |

Do not edit vendored `_cursor_*.py` by hand — run `python3 scripts/vendor_mcp_shared.py` after changing the package.

## Deprecated

Sources under `mcp/scripts/_deprecated/` are not installed. See [MCP_LAYOUT.md](MCP_LAYOUT.md).

## Refresh vendored helpers

```sh
python3 scripts/vendor_mcp_shared.py
python3 -m unittest discover -s tests
bash scripts/dogfood.sh
```
