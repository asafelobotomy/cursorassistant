---
name: setup-workspace
description: Interview and install cursorAssistant into the current project (agents, skills, rules, lockfile).
---

# Set up cursorAssistant in this project

For **individual developers** who already added the **cursor-assistant** plugin from the marketplace.

## What this does

1. Runs the setup **interview** (profile, optional packs, optional MCP extensions).
2. Writes managed surfaces into the **current workspace**: `AGENTS.md`, `.cursor/agents/`, `.cursor/skills/`, `.cursor/rules/`, `.cursor/mcp.json`, and `.cursor/cursorAssistant-lock.json`.
3. Saves choices to `.cursor/cursor-assistant-answers.json` for later updates.

## Steps

1. Confirm the workspace root is the user's project (not a parent monorepo unless intended).
2. Run:

   ```sh
   python3 cursorAssistant.py configure --workspace . --json
   ```

   Omit `--package-root` — the CLI finds the plugin install or a nearby clone.

3. If the user is not at a terminal, use the **cursorAssistantSetup** skill: ask interview questions, write `.cursor/cursor-assistant-answers.json`, then run configure with `--answers` and `--yes`.
4. After success, tell the user:
   - **Developer: Reload Window**
   - If MCP was enabled: turn on **cursorTools** (and other servers) in **Settings → Features → MCP**
5. Suggest `/inventory` or **cursorLifecycle** for later updates.

## Dry run

```sh
python3 cursorAssistant.py configure --workspace . --dry-run --json
```
