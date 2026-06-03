# cursorAssistant

> Lifecycle management for **Cursor** AI surfaces in any workspace.

cursorAssistant is inspired by [xanadAssistant](https://github.com/asafelobotomy/xanadassistant): the same ideas — **managed installs**, **lockfile drift detection**, **profiles and packs**, **specialist routing** — but targeting Cursor-native paths (`.cursor/`, `AGENTS.md`) instead of GitHub Copilot / VS Code surfaces.

## What it manages

| Surface | Installed to | Notes |
| --- | --- | --- |
| `AGENTS.md` | repo root | Specialist routing (merge-safe in a future release) |
| Subagents | `.cursor/agents/` | Cursor subagent format (`*.md`) |
| Skills | `.cursor/skills/` | `SKILL.md` per skill |
| Rules | `.cursor/rules/` | `.mdc` with `alwaysApply` / `globs` |
| MCP config | `.cursor/mcp.json` | `mcpServers` entries |
| MCP scripts | `.cursor/mcp/scripts/` | stdio Python servers (optional at setup) |

## Requirements

- Python 3.10+
- [Cursor](https://cursor.com/) (stdlib-only lifecycle core; MCP scripts need `uvx` + `mcp[cli]` when enabled)

## Quick install

From the **cursorAssistant** package root, install into a consumer workspace:

```sh
python3 cursorAssistant.py setup --workspace /path/to/your-project --package-root .
```

Inspect state:

```sh
python3 cursorAssistant.py inspect --workspace /path/to/your-project --package-root . --json
```

Update stale managed files:

```sh
python3 cursorAssistant.py update --workspace /path/to/your-project --package-root . --json
```

## Use in Cursor

1. Open the consumer workspace in Cursor.
2. Ensure **project rules** load from `.cursor/rules/` and **`AGENTS.md`** is in context (Cursor reads it automatically).
3. Invoke subagents via **Task** or `/name` (e.g. `/explore`, `/cursorLifecycle`).
4. Enable MCP servers in **Cursor Settings → MCP** (or trust the project `.cursor/mcp.json`).

Ask the main Agent: **Set up cursorAssistant in this workspace** — it should run `cursorAssistant.py setup` with the correct `--package-root`.

## Relationship to xanadAssistant

| | xanadAssistant | cursorAssistant |
| --- | --- | --- |
| **IDE** | VS Code + GitHub Copilot | Cursor |
| **Agents** | `.github/agents/*.agent.md` | `.cursor/agents/*.md` |
| **Instructions** | `.github/copilot-instructions.md` | `.cursor/rules/*.mdc` + `AGENTS.md` |
| **MCP config** | `.vscode/mcp.json` | `.cursor/mcp.json` |
| **Lockfile** | `.github/xanadAssistant-lock.json` | `.cursor/cursorAssistant-lock.json` |

The two packages are **siblings**, not forks. Long term, shared MCP scripts may live in a common library; v0 ships a minimal lifecycle engine and Cursor-shaped content only.

## Repository layout

```text
cursorAssistant.py          # CLI entry
scripts/lifecycle/          # inspect, setup, update engine
template/
  setup/install-policy.json # source of truth
  cursor/mcp.json           # MCP template
  rules/                    # default .mdc rules
agents/                     # subagent sources
skills/                     # skill sources
mcp/scripts/                # optional MCP servers (v0: lifecycle CLI; expand over time)
docs/                       # contracts and comparison notes
tests/
```

## Version

See [VERSION](VERSION). Pre-1.0 API and policy shapes may change.

## License

MIT — see [LICENSE](LICENSE).
