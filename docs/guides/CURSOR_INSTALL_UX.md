# Cursor install UX

Minimal steps from the README button to the **setup interview**.

## Flow

```mermaid
flowchart LR
  A[README badge] --> B[HTTPS install page]
  B --> C[cursor:// MCP install]
  C --> D[Bootstrap package on first MCP start]
  D --> E[Open project + Reload]
  E --> F[/cursor-assistant:setup-workspace interview]
  F --> G[Optional User Rules if advanced/full]
```

| Step | User action | What runs |
| --- | --- | --- |
| 1 | Click **Install in Cursor** on [setup page](https://asafelobotomy.github.io/cursorassistant/install/) | `cursor://…/mcp/install` (bootstrap + cursorTools) |
| 2 | Approve MCP in Cursor | `bootstrap-from-github.sh` if package missing |
| 3 | Open project folder | — |
| 4 | Reload Window | Local plugin agents/skills/commands |
| 5 | `/cursor-assistant:setup-workspace` | Mandatory interview (`setup.depth`) → `configure --answers` → `.cursor/` + lockfile |
| 6 | (Optional) User Rules | IDE-wide prefs when depth is `advanced` or `full` — not in lockfile |

## What is *not* in the button path

- No project interview on the web page
- No silent install (`configure` without `--answers`, lockfile replay, or deprecated `setup`)
- No `curl | bash` required if MCP bootstrap succeeds (optional manual bootstrap in page footer)
- `lifecycle_configure` without `answersPath` (interview must complete first)

## Install website (canonical)

Hosted at [asafelobotomy.github.io/cursorassistant/install/](https://asafelobotomy.github.io/cursorassistant/install/). **Edit** [install/index.template.html](../../install/index.template.html) **in this repo**; CI pushes generated files to [asafelobotomy.github.io](https://github.com/asafelobotomy/asafelobotomy.github.io) automatically. See [../operations/INSTALL_WEBSITE_SYNC.md](../operations/INSTALL_WEBSITE_SYNC.md).

```sh
python3 scripts/generate_install_page.py   # local preview
```

## Terminal-first alternative

```sh
curl -fsSL .../install-from-github.sh | bash -s -- .
```

## References

- [INSTALL.md](../INSTALL.md)
- [../research/DEEPLINK_INSTALL_RESEARCH.md](../research/DEEPLINK_INSTALL_RESEARCH.md)
