# cursorAssistant vs xanadAssistant

cursorAssistant reuses the **product model** from xanadAssistant (lifecycle, lockfile, packs, specialist routing) but targets **Cursor** configuration paths and formats.

## Surface mapping

| Concern | xanadAssistant | cursorAssistant (v0.8+) |
| --- | --- | --- |
| Routing | `AGENTS.md` + `copilot-instructions.md` | `AGENTS.md` + `.cursor/rules/*.mdc` |
| Specialists | `.github/agents/*.agent.md` | `.cursor/agents/*.md` (no custom `explore` — use built-in Explore) |
| Skills | `.github/skills/` | `.cursor/skills/` (Cursor tool names) |
| MCP config | `.vscode/mcp.json` | `.cursor/mcp.json` |
| Lockfile | `.github/xanadAssistant-lock.json` | `.cursor/cursorAssistant-lock.json` |
| Interview / plan / repair / factory-restore | Full engine | Full engine |
| MCP script bundle | 12+ servers | **Opt-in** bundle; default **cursorTools** only |
| Agents | 12 | **12** (inventory replaces explore) |
| Core skills | 11 | **5** (+ packs) |

## Shared DNA

- Install policy as source of truth
- Hash-based drift detection
- Backups under `.cursor/.cursorAssistant-backup/`
- Specialist roster in `AGENTS.md`
- Layer model: core / pack / profile / catalog

## Cursor-first differences (v0.8 Phase A)

- Custom agent **`inventory`** instead of **`explore`** (avoids shadowing Cursor built-in Explore)
- Skills rewritten for **Grep**, **Glob**, **SemanticSearch**, **Read**, **Shell** — not VS Code APIs
- **`mcp.enabled`** interview default **false**; **cursorTools** always installed
- Rules prefer built-in subagents and Agent tools over generic “prefer MCP”

## Not goals

- Replacing xanadAssistant for VS Code + Copilot workspaces
- Running both installers into the same paths without coordination

## Optional dual-IDE workspaces

Teams can use **xanad** for Copilot users and **cursorAssistant** for Cursor users in the same repo. Use separate lockfiles and document which surfaces are canonical for edits.
