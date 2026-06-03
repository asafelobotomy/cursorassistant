# Migration guide

## v0.9 → v0.10

### Removed: `triage` subagent

- **Before:** `/triage` or Task `triage` for complexity classification.
- **After:** Use the **`task-triage`** skill (`/task-triage`) from the main Agent when scope is unclear.
- **Action:** Run `update` or `repair` so `.cursor/agents/triage.md` is pruned. Ensure `skills/task-triage/SKILL.md` is installed.

### Removed: `git` MCP server

- **Before:** `git` in `.cursor/mcp.json` when `mcp.enabled: true`.
- **After:** Git work via **Shell** / **`gh`** and the **`commit`** subagent. Optional extensions are only `devDocs` and `memory`.
- **Action:** Run `update` — deprecated servers are stripped from `mcp.json`. Remove `.cursor/mcp/scripts/gitMcp.py` if still present (or rely on `repair` + orphan prune).

### Unchanged

- **`inventory`** still replaces a custom `explore` agent; use Cursor built-in **Explore** for wide parallel search.
- **Layered MCP** (core + extensions + packs) from v0.9 remains.

```sh
python3 cursorAssistant.py update --workspace . --package-root /path/to/cursorassistant --json
```

See [MCP_LAYOUT.md](MCP_LAYOUT.md) and [AGENTS.md](../AGENTS.md).
