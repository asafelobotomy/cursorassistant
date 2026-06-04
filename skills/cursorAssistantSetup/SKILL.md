---
name: cursorAssistantSetup
description: Use when the user wants to install or customize cursorAssistant in the current project (GitHub install or configure).
---

# cursorAssistant project setup

Guides **individual developers** after the README setup page (MCP bootstrap) through the **project interview** (lockfile, packs, MCP).

## When to use

- User clicked **Install in Cursor** on the setup page and opened this project
- User wants to **set up** cursorAssistant in this repo
- `inspect` shows `installState: not-installed`

## When not to use

- Updating an existing install with no preference changes → `update` or **cursorLifecycle**
- Personal Cursor preferences only → User Rules, not lifecycle

## Prerequisites

- Bootstrap complete (`~/.local/share/cursorassistant/current` or MCP **cursorAssistant** server running)
- Consumer workspace open in Cursor
- **cursorTools** / **cursorAssistant** MCP enabled after setup-page install

## Preferred flow

1. Inspect:

   ```sh
   python3 cursorAssistant.py inspect --workspace . --json
   ```

2. Configure (interview + project install):

   ```sh
   python3 cursorAssistant.py configure --workspace . --json
   ```

   Or MCP tool **`lifecycle_configure`** (same as configure).

3. If bootstrap missing, user runs setup page again or:

   ```sh
   curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/bootstrap-from-github.sh | bash
   ```

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
