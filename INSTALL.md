# Installing cursorAssistant

**Individual setup (recommended):** [docs/CURSOR_INSTALL_UX.md](docs/CURSOR_INSTALL_UX.md)

## Quick start (Cursor Marketplace)

1. **Add to Cursor** — install **cursor-assistant** from [Cursor Marketplace](https://cursor.com/marketplace). This downloads the full plugin (agents, skills, rules, commands, lifecycle CLI source under `~/.cursor/plugins/…`).
2. Open **your project** in Cursor.
3. Customize and install into the repo:

   ```sh
   python3 cursorAssistant.py configure --workspace .
   ```

   Or in chat: **`/cursor-assistant:setup-workspace`**.

4. **Developer: Reload Window** once.
5. If you enabled MCP extensions in the interview: **Settings → Features → MCP** → enable **cursorTools**.

Saved choices live in `.cursor/cursor-assistant-answers.json`. Managed surfaces and `.cursor/cursorAssistant-lock.json` are written into the project.

## Update this project

```sh
python3 cursorAssistant.py update --workspace .
```

Or ask the Agent to **update cursorAssistant** (**cursorLifecycle** / cursorTools MCP when enabled).

`--package-root` is optional after the first install (lockfile and plugin discovery).

## Clone instead of Marketplace

```sh
git clone https://github.com/asafelobotomy/cursorassistant.git
cd your-project
bash /path/to/cursorassistant/scripts/cursor-assistant-init.sh .
```

## Non-interactive setup

```sh
python3 cursorAssistant.py configure --workspace . \
  --answers .cursor/cursor-assistant-answers.json --yes --json
```

Example answers file:

```json
{
  "profile.selected": "balanced",
  "packs.selected": [],
  "mcp.enabled": false
}
```

## Preserve custom routing

Wrap custom sections in `AGENTS.md`:

```markdown
<!-- user-added -->
## Your section
...
<!-- /user-added -->
```

Custom MCP servers in `.cursor/mcp.json` are merged on update.

## Repair and reset

| Situation | Command |
| --- | --- |
| Drift / incomplete install | `python3 cursorAssistant.py repair --workspace . --json` |
| Full managed-surface reset | `factory-restore` (destructive; confirm first) |

## Dogfood (this repository)

```sh
cd /path/to/cursorassistant
bash scripts/dogfood.sh
```

Full stack (extensions + all packs): `bash scripts/dogfood-full.sh`

## Interview fields

| Field | Meaning |
| --- | --- |
| `profile.selected` | `balanced` or `lean` |
| `packs.selected` | `lean`, `secure`, `tdd` (optional) |
| `mcp.enabled` | Optional devDocs + memory MCP (default `false`) |

## Team / git (optional)

Teams may commit `.cursor/`, `AGENTS.md`, and the lockfile so everyone shares the same install. That is optional; the primary path is Marketplace + per-developer **configure**.

## See also

- [README.md](README.md)
- [docs/PUBLISH.md](docs/PUBLISH.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
