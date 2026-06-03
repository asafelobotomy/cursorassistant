# MCP layout (v0.9+)

cursorAssistant composes `.cursor/mcp.json` from layered manifests instead of a single monolithic bundle.

## Layers

| Layer | Manifest | When applied |
| --- | --- | --- |
| **Core** | `template/cursor/mcp-core.json` | Always — `cursorTools` only |
| **Extensions** | `template/cursor/mcp-extensions.json` | Interview `mcp.enabled: true` — `git`, `devDocs`, `memory` |
| **Pack: secure** | `template/cursor/mcp-packs/secure.json` | Pack `secure` selected |
| **Pack: tdd** | `template/cursor/mcp-packs/tdd.json` | Pack `tdd` selected |
| **Pack: lean** | `template/cursor/mcp-packs/lean.json` | Pack `lean` selected |

Scripts install to `.cursor/mcp/scripts/` from `mcp/scripts/` or `packs/<pack>/mcp/`.

## Deprecated (removed v0.9)

| Server / script | Cursor-native replacement |
| --- | --- |
| `web` / `webMcp.py` | WebSearch, WebFetch |
| `filesystem` / `fsMcp.py` | Read, Write, Grep, Glob |
| `time` / `timeMcp.py` | Not needed for typical workflows |

Deprecated sources live under `mcp/scripts/_deprecated/`. `inspect` reports warnings if legacy servers or scripts remain in the workspace.

## Legacy file

`template/cursor/mcp-bundle.json` is **obsolete** — do not reference in new installs. Use the layered manifests above.
