# cursor-mcp-shared

Shared Python helpers for MCP stdio servers used by **cursorAssistant** and (planned) **xanadAssistant**.

## Modules

| Module | Purpose |
| --- | --- |
| `cursor_mcp_shared.workspace` | Discover consumer workspace root, read lockfile |
| `cursor_mcp_shared.profiles` | `CURSOR` and `XANAD` workspace profiles |
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

```python
from cursor_mcp_shared import XANAD, discover_workspace_root, read_lockfile

root = discover_workspace_root(Path(__file__), profile=XANAD)
```

Or `export CURSOR_MCP_PROFILE=xanad`. Full checklist: [docs/XANAD_INTEGRATION.md](../../docs/XANAD_INTEGRATION.md) in the cursorAssistant repo.
