# cursorAssistant vs xanadAssistant

cursorAssistant reuses the **product model** from xanadAssistant (lifecycle, lockfile, packs, specialist routing) but targets **Cursor** configuration paths and formats.

## Surface mapping

| Concern | xanadAssistant | cursorAssistant (v0.10+) |
| --- | --- | --- |
| Routing | `AGENTS.md` + `copilot-instructions.md` | `AGENTS.md` + `.cursor/rules/*.mdc` |
| Specialists | `.github/agents/*.agent.md` | `.cursor/agents/*.md` (11 core; no custom `explore`) |
| Skills | `.github/skills/` | `.cursor/skills/` (6 core + packs; Cursor tool names) |
| Complexity routing | `triage` agent (xanad) | **`task-triage`** skill (not a subagent) |
| Git operations | often `git` MCP | **`commit`** subagent + Shell/`gh` (no `git` MCP) |
| MCP config | `.vscode/mcp.json` | `.cursor/mcp.json` (layered manifests) |
| Lockfile | `.github/xanadAssistant-lock.json` | `.cursor/cursorAssistant-lock.json` |
| Interview / plan / repair / factory-restore | Full engine | Full engine |
| MCP script bundle | 12+ servers | **Opt-in** extensions; default **cursorTools** only |

## Shared DNA

- Install policy as source of truth
- Hash-based drift detection
- Backups under `.cursor/.cursorAssistant-backup/`
- Specialist roster in `AGENTS.md`
- Layer model: core / pack / profile / catalog
- Shared library: [`cursor-mcp-shared`](../packages/cursor-mcp-shared/README.md) (v0.7+)

## Cursor-first differences

- Custom agent **`inventory`** instead of **`explore`** (avoids shadowing Cursor built-in Explore)
- Skills use **Grep**, **Glob**, **SemanticSearch**, **Read**, **Shell** — not VS Code APIs (`cursorEval policy` enforces)
- **`mcp.enabled`** interview default **false**; **cursorTools** always installed
- Deprecated MCP: `web`, `filesystem`, `time`, **`git`**
- Rules prefer built-in subagents and Agent tools over generic “prefer MCP”

## Not goals

- Replacing xanadAssistant for VS Code + Copilot workspaces
- Running both installers into the same paths without coordination

## Optional dual-IDE workspaces

Teams can use **xanad** for Copilot users and **cursorAssistant** for Cursor users in the same repo. Use separate lockfiles and document which surfaces are canonical for edits.

## Upgrading cursorAssistant

See [MIGRATION.md](MIGRATION.md) for v0.9 → v0.10 changes.
