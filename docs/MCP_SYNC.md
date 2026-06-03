# MCP script sync with xanadAssistant

cursorAssistant v0.4+ ships MCP servers adapted from [xanadAssistant](https://github.com/asafelobotomy/xanadassistant). Scripts live in `mcp/scripts/` and are installed to `.cursor/mcp/scripts/` in consumer workspaces.

## Maintainer sync

When xanad updates shared servers, re-sync from a local xanad checkout:

```sh
python3 scripts/sync_mcp_from_xanad.py \
  --xanad-root /path/to/xanadassistant \
  --package-root .
```

`cursorToolsMcp.py` is **not** overwritten — it is Cursor-specific.

## Adaptations applied

| xanad | cursorAssistant |
| --- | --- |
| `.github/` workspace marker | `.cursor/` |
| `copilot-instructions.md` | `README.md` (Key Commands) |
| `xanadAssistant-lock.json` | `cursorAssistant-lock.json` |
| Memory DB under `.github/xanadAssistant/` | `.cursor/cursorAssistant/` |
| `FastMCP("xanad…")` | `FastMCP("cursor…")` |

## Shared modules (v0.6+)

These files are **cursorAssistant-owned** and installed with every workspace (not overwritten by xanad sync):

| Module | Role |
| --- | --- |
| `_cursor_workspace.py` | Workspace root discovery, lockfile read |
| `_cursor_mcp_util.py` | Tool result formatting |
| `cursorToolsMcp.py` | Lifecycle CLI wrapper |

When syncing from xanad, `sync_mcp_from_xanad.py` skips `cursorToolsMcp.py` and `_cursor_*.py`. A single pip package shared with xanadAssistant is still planned for later.
