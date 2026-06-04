---
name: cursorAssistantSetup
description: Use when the user wants to install or customize cursorAssistant in the current project (GitHub install or configure).
---

# cursorAssistant project setup

Guides **individual developers** from GitHub install → customized **project** install (lockfile, selective packs, MCP choice).

## When to use

- User wants to **install** or **set up** cursorAssistant in this repo
- `inspect` shows `installState: not-installed`
- User pasted the README `curl … install-from-github.sh` command and needs help finishing

## When not to use

- Updating an existing install with no preference changes → `update` or **cursorLifecycle**
- Personal Cursor preferences only → User Rules, not lifecycle

## Prerequisites

- Python 3.10+ and `git` for the one-liner install
- Consumer workspace open in Cursor
- Global package at `~/.local/share/cursorassistant/` or local plugin at `~/.cursor/plugins/local/cursor-assistant` (created by install script)

## Preferred flow

1. If not installed globally, run (user terminal):

   ```sh
   curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash -s -- .
   ```

2. Otherwise inspect:

   ```sh
   python3 cursorAssistant.py inspect --workspace . --json
   ```

3. Configure:

   ```sh
   python3 cursorAssistant.py configure --workspace . --json
   ```

4. **Reload Window**; enable **cursorTools** under **Settings → MCP** if MCP was enabled in the interview.

## Agent-driven interview

When stdin is not available, ask these questions and write `.cursor/cursor-assistant-answers.json`:

| Key | Question | Options / default |
| --- | --- | --- |
| `profile.selected` | Behavior profile | `balanced` (default) or `lean` |
| `packs.selected` | Optional packs | `lean`, `secure`, `tdd` — default `[]` |
| `mcp.enabled` | Install devDocs + memory MCP extensions | default `false` |

Then `plan-setup` → confirm → `setup` with `--answers`.

## Package root

Omit `--package-root` when possible (lockfile, `~/.local/share/cursorassistant`, local plugin symlink).

## Rules

- Do not hand-edit managed `.cursor/` files when lifecycle can apply the change.
- Global install alone does not replace **configure** for the project lockfile and selective packs.
