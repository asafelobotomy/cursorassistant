# xanadAssistant + cursor-mcp-shared

xanadAssistant can depend on the **`cursor-mcp-shared`** package in this repo instead of duplicating workspace discovery in every MCP script.

## Install

From a published wheel/path:

```sh
pip install ./packages/cursor-mcp-shared
```

Or add to `pyproject.toml` / `requirements.txt` once published to PyPI.

## Workspace profile

| Profile | Lockfile | Markers |
| --- | --- | --- |
| `CURSOR` (default) | `.cursor/cursorAssistant-lock.json` | `.cursor/`, `cursorAssistant.py` |
| `XANAD` | `.github/xanadAssistant-lock.json` | `.github/`, `xanadAssistant.py` |

### Python API

```python
from cursor_mcp_shared import CURSOR, XANAD, discover_workspace_root, read_lockfile

root = discover_workspace_root(Path(__file__), profile=XANAD)
lock = read_lockfile(root, profile=XANAD)
```

### Environment

Set before launching MCP stdio servers in a Copilot workspace:

```sh
export CURSOR_MCP_PROFILE=xanad
```

Then `discover_workspace_root(script_path)` without an explicit profile resolves **XANAD** markers.

## Migration checklist (xanad repo)

1. Add `cursor-mcp-shared` dependency (path, git submodule, or PyPI when available).
2. Replace inline lockfile paths with `read_lockfile(root, profile=XANAD)`.
3. Replace parent-walk discovery with `discover_workspace_root(Path(__file__), profile=XANAD)`.
4. Keep Copilot-specific path strings only where profiles cannot cover them (document exceptions).
5. Run xanad’s MCP tests; compare behavior to pre-migration scripts.
6. Optionally vendor into `.github/mcp/scripts/_cursor_*.py` the same way cursorAssistant does (`scripts/vendor_mcp_shared.py`).

## cursorAssistant side

- Canonical sources: `packages/cursor-mcp-shared/`
- Refresh vendored shims: `python3 scripts/vendor_mcp_shared.py`
- Port script changes from xanad: `scripts/sync_mcp_from_xanad.py`

## Verify locally (cursorAssistant repo)

```sh
python3 scripts/verify_xanad_profile.py
```

CI runs this on every push. It does not modify the xanadAssistant repository — apply the checklist above there.

## Versioning

Package version lives in `packages/cursor-mcp-shared/pyproject.toml`. Bump when changing `WorkspaceProfile` fields or discovery semantics.
