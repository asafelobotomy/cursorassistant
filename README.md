# cursorAssistant

> Lifecycle management for **Cursor** AI surfaces in any workspace.

cursorAssistant installs and maintains **managed installs**, **lockfile drift detection**, **profiles and packs**, and **specialist routing** using Cursor-native paths (`.cursor/`, `AGENTS.md`).

## What it manages

| Surface | Installed to | Notes |
| --- | --- | --- |
| `AGENTS.md` | repo root | Specialist routing (merge-safe user blocks) |
| Subagents | `.cursor/agents/` | Cursor subagent format (`*.md`) |
| Skills | `.cursor/skills/` | `SKILL.md` per skill |
| Rules | `.cursor/rules/` | `.mdc` with `alwaysApply` / `globs` |
| MCP config | `.cursor/mcp.json` | Layered: `cursorTools` + optional extensions + pack servers ([MCP_LAYOUT](docs/MCP_LAYOUT.md)) |
| MCP scripts | `.cursor/mcp/scripts/` | stdio Python servers (`cursorTools` wraps lifecycle CLI) |

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

Repair lockfile drift or incomplete installs:

```sh
python3 cursorAssistant.py repair --workspace /path/to/your-project --package-root . --json
```

Plan without writing:

```sh
python3 cursorAssistant.py plan-setup --workspace /path/to/your-project --package-root . --json
```

## Key Commands

| Task | Command |
| --- | --- |
| Run tests | `python3 -m unittest discover -s tests` |
| Dogfood this repo | `bash scripts/dogfood.sh` (lean) or `bash scripts/dogfood-full.sh` (extensions + packs) |
| Check all surfaces | `bash scripts/ci_check_surfaces.sh` |
| Verify dogfood install | `python3 scripts/check_dogfood_install.py` |
| Vendor MCP shared | `python3 scripts/vendor_mcp_shared.py` |
| Generate manifest | `python3 scripts/generate.py --package-root .` |
| Lifecycle inspect | `python3 cursorAssistant.py inspect --workspace . --package-root . --json` |

## Use in Cursor

1. Open the consumer workspace in Cursor.
2. Ensure **project rules** load from `.cursor/rules/` and **`AGENTS.md`** is in context (Cursor reads it automatically).
3. Invoke subagents via **Task** or `/name` (e.g. `/inventory`, `/cursorLifecycle`). Use Cursor's built-in **Explore** for broad codebase search — do not add a custom agent named `explore`.
4. Enable MCP servers in **Cursor Settings → MCP** (or trust the project `.cursor/mcp.json`).

Ask the main Agent: **Set up cursorAssistant in this workspace** — it should run `cursorAssistant.py setup` with the correct `--package-root`.

## Documentation

| Doc | Topic |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Policy, engine, install flow |
| [docs/MIGRATION.md](docs/MIGRATION.md) | v0.9 → v0.10 upgrades |
| [SECURITY.md](SECURITY.md) | MCP and secrets guidance |
| [docs/MCP_LAYOUT.md](docs/MCP_LAYOUT.md) | Layered MCP manifests |
| [docs/MCP_MAINTENANCE.md](docs/MCP_MAINTENANCE.md) | MCP scripts and vendoring |
| [docs/HOOKS.md](docs/HOOKS.md) | Optional user-owned hooks |
| [docs/PUBLISH.md](docs/PUBLISH.md) | Cursor Marketplace |

## Shared MCP library

`packages/cursor-mcp-shared/` provides workspace discovery for MCP stdio servers. See [docs/SHARED_MCP.md](docs/SHARED_MCP.md).

## Plugin / marketplace

Publish as a Cursor plugin using `.cursor-plugin/plugin.json`. The plugin ships **core** agents, skills, rules, and **cursorTools** MCP only — optional packs and extensions require `cursorAssistant.py setup` ([docs/PUBLISH.md](docs/PUBLISH.md)). Submit via [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) when ready.

Upgrading from v0.9? See [docs/MIGRATION.md](docs/MIGRATION.md).

## Eval tooling

```sh
python3 tools/cursorEval/cursorEval.py validate --repo-root .
python3 tools/cursorEval/cursorEval.py coverage --repo-root .
python3 tools/cursorEval/cursorEval.py run evals/lifecycleAudit/eval.yaml --dry-run
bash scripts/eval_models_pr_smoke.sh   # GitHub Models (3 tasks; skips without token)
```

PRs run **eval-models-pr** when `GITHUB_MODELS_TOKEN` is configured in repo secrets.

## Repository layout

```text
cursorAssistant.py          # CLI entry
scripts/lifecycle/          # inspect, setup, update engine
template/
  setup/install-policy.json # source of truth
  cursor/mcp-core.json      # layered MCP (see docs/MCP_LAYOUT.md)
  rules/                    # default .mdc rules
agents/                     # subagent sources
skills/                     # skill sources
packs/                      # optional packs (lean, secure, tdd)
mcp/scripts/                # MCP servers (cursorTools + shared bundle)
tools/cursorEval/           # eval validate, check, coverage, run, grade
.cursor-plugin/             # Cursor Marketplace plugin manifest
docs/                       # architecture, migration, MCP, hooks, publish
tests/
```

## Version

See [VERSION](VERSION). Pre-1.0 API and policy shapes may change.

## License

MIT — see [LICENSE](LICENSE).
