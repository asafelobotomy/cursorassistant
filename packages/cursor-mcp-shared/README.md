# cursor-mcp-shared

Shared Python helpers for MCP stdio servers used by **cursorAssistant** and (planned) **xanadAssistant**.

## Modules

| Module | Purpose |
| --- | --- |
| `cursor_mcp_shared.workspace` | Discover consumer workspace root, read lockfile |
| `cursor_mcp_shared.mcp_util` | Build MCP tool result dicts |

## Install

```sh
pip install ./packages/cursor-mcp-shared
```

## Vendor into cursorAssistant

From the cursorAssistant repo root:

```sh
python3 scripts/vendor_mcp_shared.py
```

This copies modules into `mcp/scripts/_cursor_*.py` so consumer workspaces receive stdio servers without a separate pip install.

## xanadAssistant adoption

xanad can add `cursor-mcp-shared` as a dependency and replace duplicated workspace-discovery logic in MCP scripts, using path adapters for `.github/` vs `.cursor/` markers.
