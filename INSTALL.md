# Installing cursorAssistant

Full UX notes: [docs/CURSOR_INSTALL_UX.md](docs/CURSOR_INSTALL_UX.md)

## Quick start (one command)

From your **project root** (read the script before piping to `bash`):

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash -s -- .
```

Or open the repo README and use the green **Install from GitHub** badge (same command).

The script:

1. Clones cursorAssistant to `~/.local/share/cursorassistant/<version>`
2. Symlinks `~/.cursor/plugins/local/cursor-assistant` (Cursor local plugin)
3. Runs the setup **interview** and **`configure`** into your workspace
4. You **Developer: Reload Window** in Cursor

## Already have this repo cloned

```sh
bash scripts/install-from-github.sh /path/to/your-project
# or, from the clone only:
bash scripts/cursor-assistant-init.sh /path/to/your-project
```

## In Cursor (after install)

- Chat: **`/cursor-assistant:setup-workspace`** or ask to **set up cursorAssistant**
- Skill: **cursorAssistantSetup**
- Subagent: **cursorLifecycle** for inspect / update / repair

## Update this project

```sh
python3 cursorAssistant.py update --workspace .
```

Re-run the GitHub installer to refresh the global package copy:

```sh
CURSOR_ASSISTANT_VERSION=0.12.0 curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash -s -- .
```

Or ask the Agent to **update cursorAssistant**.

`--package-root` is optional (lockfile, `~/.local/share/cursorassistant`, or local plugin path).

## Non-interactive setup

```sh
python3 cursorAssistant.py configure --workspace . \
  --answers .cursor/cursor-assistant-answers.json --yes --json
```

Example answers:

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

## Repair and reset

| Situation | Command |
| --- | --- |
| Drift / incomplete install | `python3 cursorAssistant.py repair --workspace . --json` |
| Full managed-surface reset | `factory-restore` (destructive; confirm first) |

## Requirements

- Python 3.10+
- [Cursor](https://cursor.com/)
- `git` (for the one-liner download)

## Interview fields

| Field | Meaning |
| --- | --- |
| `profile.selected` | `balanced` or `lean` |
| `packs.selected` | `lean`, `secure`, `tdd` (optional) |
| `mcp.enabled` | Optional devDocs + memory MCP (default `false`) |

## Optional: commit install to git

Teams may commit `.cursor/`, `AGENTS.md`, and the lockfile so everyone shares the same surfaces. Each developer still needs the global package (install script) for `update` unless `packageRoot` in the lockfile points at a shared path.

## See also

- [README.md](README.md)
- [docs/PUBLISH.md](docs/PUBLISH.md) — distribution (not marketplace)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
