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
  F --> G[Pack layer if packs selected]
  G --> H[configure --answers]
  H --> I[Optional User Rules if advanced/full]
```

| Step | User action | What runs |
| --- | --- | --- |
| 1 | Click **Install in Cursor** on [setup page](https://asafelobotomy.github.io/cursorassistant/install/) | `cursor://…/mcp/install` (bootstrap + cursorTools) |
| 2 | Approve MCP in Cursor | `bootstrap-from-github.sh` if package missing |
| 3 | Open project folder | — |
| 4 | Reload Window | Local plugin agents/skills/commands |
| 5 | `/cursor-assistant:setup-workspace` | Mandatory interview (`setup.depth`) — optional copy-from prefill and user defaults |
| 6 | Pack questions (if any) | One question per selected pack (`secure`, `tdd`, `lean`) |
| 7 | `configure --answers` | `.cursor/` + lockfile (`packAnswers` when packs selected) |
| 8 | (Optional) User Rules | IDE-wide prefs when depth is `advanced` or `full` — not in lockfile |
| 9 | (Optional) Save defaults | `~/.cursor/cursor-assistant-defaults.json` for the next project |

## Interview layers (v0.16+)

1. **Preflight** — optional copy answers from another GitHub repo (`setup.copyFrom.*`; stripped on save).
2. **Core** — depth, profile, packs, MCP toggle, 8-key agent/skill batch at simple depth.
3. **Pack** — gated questions per selected pack; answers stored in lockfile `packAnswers` (schema 0.6.0).
4. **Personalization** — advanced/full only → `preferences.mdc`.

MCP tools: `lifecycle_interview_questions`, `_import`, `_save`, `lifecycle_defaults_load` / `_save`.

## What is *not* in the button path

- No project interview on the web page
- No silent install (`configure` without `--answers`, lockfile replay, or deprecated `setup`)
- No `curl | bash` required if MCP bootstrap succeeds (optional manual bootstrap in page footer)
- `lifecycle_configure` without `answersPath` (interview must complete first)

## Install website (canonical)

Hosted at [asafelobotomy.github.io/cursorassistant/install/](https://asafelobotomy.github.io/cursorassistant/install/). **Edit** [install/index.template.html](../../install/index.template.html) **in this repo**; CI pushes generated files to [asafelobotomy.github.io](https://github.com/asafelobotomy/asafelobotomy.github.io) automatically. See [../operations/INSTALL_WEBSITE_SYNC.md](../operations/INSTALL_WEBSITE_SYNC.md).

The install page links **fixture templates** under `tests/fixtures/` for non-interactive setup.

```sh
python3 scripts/generate_install_page.py   # local preview
```

## Terminal-first alternative

```sh
curl -fsSL .../install-from-github.sh | bash -s -- .
# or fixture:
bash scripts/install-from-github.sh . --answers tests/fixtures/interview-balanced.json
```

## References

- [INSTALL.md](../../INSTALL.md)
- [PREFERENCES_LAYERS.md](PREFERENCES_LAYERS.md)
- [MIGRATION.md](MIGRATION.md) — § v0.16–0.17
- [../project/TOKEN_AND_PACK_INTERVIEW_PLAN.md](../project/TOKEN_AND_PACK_INTERVIEW_PLAN.md)
- [../research/DEEPLINK_INSTALL_RESEARCH.md](../research/DEEPLINK_INSTALL_RESEARCH.md)
