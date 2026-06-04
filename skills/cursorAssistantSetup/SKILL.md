---
name: cursorAssistantSetup
description: Use when the user wants to customize and install cursorAssistant into the current project after adding the marketplace plugin.
---

# cursorAssistant project setup

Guides **individual developers** from marketplace plugin → customized **project** install (lockfile, selective packs, MCP choice).

## When to use

- User installed **cursor-assistant** from Cursor Marketplace and wants it **in this repo**
- User asks to **set up**, **configure**, or **customize** cursorAssistant
- `inspect` shows `installState: not-installed`

## When not to use

- Updating an existing install with no preference changes → `update` or **cursorLifecycle**
- Personal Cursor preferences only → User Rules, not lifecycle

## Prerequisites

- **cursor-assistant** plugin installed (Marketplace → Add to Cursor), **or** a local clone of this repository
- Consumer workspace open in Cursor
- Python 3.10+ available in the environment running shell commands

## Preferred flow (in chat)

1. Run inspect (auto-detects package root when omitted):

   ```sh
   python3 cursorAssistant.py inspect --workspace . --json
   ```

2. If `not-installed`, run **configure** (interview + setup). In a terminal the user can answer prompts; in Agent-only sessions, ask the interview questions below, write answers, then run setup.

   ```sh
   python3 cursorAssistant.py configure --workspace . --json
   ```

   Non-interactive (after collecting answers):

   ```sh
   python3 cursorAssistant.py configure --workspace . \
     --answers .cursor/cursor-assistant-answers.json --yes --json
   ```

3. Tell the user to **Developer: Reload Window** and, if they enabled MCP in the interview, enable **cursorTools** under **Settings → Features → MCP**.

4. Route ongoing maintenance to **cursorLifecycle** or `update` / `repair`.

## Agent-driven interview

When stdin is not available, ask these questions and write `.cursor/cursor-assistant-answers.json`:

| Key | Question | Options / default |
| --- | --- | --- |
| `profile.selected` | Behavior profile | `balanced` (default) or `lean` |
| `packs.selected` | Optional packs | `lean`, `secure`, `tdd` — default `[]`; lean profile defaults to `["lean"]` |
| `mcp.enabled` | Install devDocs + memory MCP extensions | default `false` (cursorTools still installed) |

Then:

```sh
python3 cursorAssistant.py plan-setup --workspace . \
  --answers .cursor/cursor-assistant-answers.json --json
```

Show `wouldWrite` summary; on confirmation:

```sh
python3 cursorAssistant.py setup --workspace . \
  --answers .cursor/cursor-assistant-answers.json --json
```

## Package root

Omit `--package-root` when possible. Resolution order: `CURSOR_ASSISTANT_PACKAGE_ROOT` → lockfile → parent walk → `~/.cursor/plugins/**` → installed CLI anchor.

## Rules

- Do not hand-edit managed `.cursor/` files when lifecycle can apply the change.
- Marketplace plugin alone does not write the project lockfile; **configure** / **setup** does.
- Do not enable `mcp.enabled` unless the user wants extra MCP servers (requires `uvx`).
