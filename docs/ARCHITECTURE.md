# Architecture

## Source of truth

| Artifact | Role |
| --- | --- |
| `template/setup/install-policy.json` | Managed file list, merge strategies, layers |
| `agents/`, `skills/`, `template/rules/` | Content installed into consumer workspaces |
| `template/cursor/mcp-*.json` | Layered MCP server definitions |
| `scripts/lifecycle/` | `inspect`, `setup`, `update`, `repair`, engine + merge |

`scripts/generate.py` builds `install-manifest.json` and `catalog.json` from policy + discovered MCP/pack files.

## Install flow

```text
interview.json answers → conditions (mcp, packs, profile)
  → core_entries + pack_entries + mcp_script_entries
  → materialize + apply_write_strategy (replace | merge-json | preserve-markdown-blocks)
  → .cursor/cursorAssistant-lock.json (hashes)
```

## Surfaces in a consumer workspace

| Path | Managed by lifecycle |
| --- | --- |
| `AGENTS.md` | Yes (merge-safe blocks) |
| `.cursor/agents/*.md` | Yes |
| `.cursor/skills/*/SKILL.md` | Yes (+ pack skills) |
| `.cursor/rules/*.mdc` | Yes |
| `.cursor/mcp.json` | Yes (merge + sanitize deprecated servers) |
| `.cursor/mcp/scripts/*.py` | Yes (prune orphans) |
| `.cursor/hooks.json` | No — user-owned ([HOOKS.md](HOOKS.md)) |

## MCP scripts

Shared helpers live in `packages/cursor-mcp-shared/`, vendored to `mcp/scripts/_cursor_*.py`. Pack-specific scripts under `packs/<pack>/mcp/`.

## Quality gates

- `tests/` — lifecycle and MCP composition
- `tools/cursorEval/` — eval suite validate, surface `check`, `policy`, optional GitHub Models `run`

## Local plugin vs project lifecycle

`.cursor-plugin/plugin.json` describes the bundle symlinked to `~/.cursor/plugins/local/cursor-assistant` by `install-from-github.sh`. Cursor loads agents/skills/commands at user scope. **Project** installs (packs, extensions, lockfile) use `configure` / `setup` — see [INSTALL.md](../INSTALL.md).
