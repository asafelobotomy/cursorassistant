# cursorAssistant vs xanadAssistant

cursorAssistant reuses the **product model** from xanadAssistant (lifecycle, lockfile, packs, specialist routing) but targets **Cursor** configuration paths and formats.

## Surface mapping

| Concern | xanadAssistant | cursorAssistant (v0.1) |
| --- | --- | --- |
| Routing | `AGENTS.md` + `copilot-instructions.md` | `AGENTS.md` + `.cursor/rules/*.mdc` |
| Specialists | `.github/agents/*.agent.md` | `.cursor/agents/*.md` |
| Skills | `.github/skills/` | `.cursor/skills/` |
| MCP config | `.vscode/mcp.json` | `.cursor/mcp.json` |
| Lockfile | `.github/xanadAssistant-lock.json` | `.cursor/cursorAssistant-lock.json` |
| Interview / plan / repair / factory-restore | Full engine | **Planned** (v0.1: inspect, setup, update only) |
| MCP script bundle | 12+ servers | Empty template; vendor or share later |

## Shared DNA

- Install policy as source of truth
- Hash-based drift detection
- Backups under `.cursor/.cursorAssistant-backup/`
- Specialist roster in `AGENTS.md`
- Layer model: core / pack / profile / catalog (packs in roadmap)

## Not goals

- Replacing xanadAssistant for VS Code + Copilot workspaces
- Running both installers into the same paths without coordination

## Optional dual-IDE workspaces

Teams can use **xanad** for Copilot users and **cursorAssistant** for Cursor users in the same repo. Use separate lockfiles and document which surfaces are canonical for edits.
