# cursorAssistant

> Lifecycle management for **Cursor** AI surfaces in any workspace.

cursorAssistant installs and maintains **managed installs**, **lockfile drift detection**, **profiles and packs**, and **specialist routing** using Cursor-native paths (`.cursor/`, `AGENTS.md`).

[![Install cursorAssistant](https://img.shields.io/badge/Install-cursorAssistant-2ea043?style=for-the-badge)](https://github.com/asafelobotomy/cursorassistant#install)

## Install

GitHub cannot run setup inside the README; use this **one command** from your project root (review the [install script](scripts/install-from-github.sh) first):

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash -s -- .
```

Replace `.` with your project path. The script downloads the package to `~/.local/share/cursorassistant/`, links the **local Cursor plugin** at `~/.cursor/plugins/local/cursor-assistant`, runs the setup interview, and writes managed files into your repo. Then **Developer: Reload Window** in Cursor.

From a clone of this repository:

```sh
bash scripts/install-from-github.sh /path/to/your-project
```

Details: [INSTALL.md](INSTALL.md) · [docs/CURSOR_INSTALL_UX.md](docs/CURSOR_INSTALL_UX.md)

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
- `git` (for the install one-liner)

## After install

```sh
python3 cursorAssistant.py inspect --workspace . --json
python3 cursorAssistant.py update --workspace . --json
python3 cursorAssistant.py repair --workspace . --json
```

In chat: **`/cursor-assistant:setup-workspace`**, or ask to **set up cursorAssistant** (**cursorAssistantSetup** / **cursorLifecycle**).

## Key Commands

| Task | Command |
| --- | --- |
| Run tests | `python3 -m unittest discover -s tests` |
| Dogfood this repo | `bash scripts/dogfood.sh` (lean) or `bash scripts/dogfood-full.sh` (extensions + packs) |
| Check all surfaces | `bash scripts/ci_check_surfaces.sh` |
| Verify dogfood install | `python3 scripts/check_dogfood_install.py` |
| Vendor MCP shared | `python3 scripts/vendor_mcp_shared.py` |
| Generate manifest | `python3 scripts/generate.py --package-root .` |
| Lifecycle inspect | `python3 cursorAssistant.py inspect --workspace . --json` |

## Use in Cursor

1. Open the consumer workspace in Cursor.
2. Ensure **project rules** load from `.cursor/rules/` and **`AGENTS.md`** is in context.
3. Invoke subagents via **Task** or `/name` (e.g. `/inventory`, `/cursorLifecycle`). Use Cursor's built-in **Explore** for broad codebase search — do not add a custom agent named `explore`.
4. Enable MCP servers in **Settings → MCP** when you opted in during setup.

## Documentation

| Doc | Topic |
| --- | --- |
| [INSTALL.md](INSTALL.md) | Install and update |
| [docs/CURSOR_INSTALL_UX.md](docs/CURSOR_INSTALL_UX.md) | Install flow in Cursor |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Policy, engine, install flow |
| [docs/MIGRATION.md](docs/MIGRATION.md) | v0.9 → v0.10 upgrades |
| [SECURITY.md](SECURITY.md) | MCP and secrets guidance |
| [docs/MCP_LAYOUT.md](docs/MCP_LAYOUT.md) | Layered MCP manifests |
| [docs/MCP_MAINTENANCE.md](docs/MCP_MAINTENANCE.md) | MCP scripts and vendoring |
| [docs/HOOKS.md](docs/HOOKS.md) | Optional user-owned hooks |
| [docs/PUBLISH.md](docs/PUBLISH.md) | Distribution (GitHub + local plugin) |

## Shared MCP library

`packages/cursor-mcp-shared/` provides workspace discovery for MCP stdio servers. See [docs/SHARED_MCP.md](docs/SHARED_MCP.md).

## Local plugin manifest

`.cursor-plugin/plugin.json` defines the bundle for Cursor’s **local plugin** path (created by the install script). It is not a public Marketplace listing. See [docs/PUBLISH.md](docs/PUBLISH.md).

Upgrading from v0.9? See [docs/MIGRATION.md](docs/MIGRATION.md).

## Eval tooling

```sh
python3 tools/cursorEval/cursorEval.py validate --repo-root .
python3 tools/cursorEval/cursorEval.py coverage --repo-root .
python3 tools/cursorEval/cursorEval.py run evals/lifecycleAudit/eval.yaml --dry-run
bash scripts/eval_models_pr_smoke.sh   # GitHub Models (3 tasks; skips without token)
```

## Repository layout

```text
cursorAssistant.py          # CLI entry
scripts/install-from-github.sh  # Primary consumer install
scripts/lifecycle/          # inspect, setup, update engine
template/
  setup/install-policy.json # source of truth
  cursor/mcp-core.json      # layered MCP
  rules/                    # default .mdc rules
agents/                     # subagent sources
skills/                     # skill sources
packs/                      # optional packs (lean, secure, tdd)
mcp/scripts/                # MCP servers
.cursor-plugin/             # local plugin manifest
docs/
tests/
```

## Version

See [VERSION](VERSION). Pre-1.0 API and policy shapes may change.

## License

MIT — see [LICENSE](LICENSE).
