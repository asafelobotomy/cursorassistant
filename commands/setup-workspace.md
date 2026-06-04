---
name: setup-workspace
description: Interview and install cursorAssistant into the current project (agents, skills, rules, lockfile).
---

# Set up cursorAssistant in this project

Run after the [setup page](https://asafelobotomy.github.io/cursorassistant/install/) MCP bootstrap, or to reconfigure an existing project.

## What this does

1. Runs the setup **interview** (profile, optional packs, optional MCP extensions).
2. Writes managed surfaces into the **current workspace**: `AGENTS.md`, `.cursor/agents/`, `.cursor/skills/`, `.cursor/rules/`, `.cursor/mcp.json`, and `.cursor/cursorAssistant-lock.json`.
3. Saves choices to `.cursor/cursor-assistant-answers.json`.

## Steps

1. Confirm the workspace root is the user's project.
2. If bootstrap is missing (`~/.local/share/cursorassistant/current`), send the user to the [setup page](https://asafelobotomy.github.io/cursorassistant/install/) or `bootstrap-from-github.sh`.

3. Run:

   ```sh
   python3 cursorAssistant.py configure --workspace . --json
   ```

4. **Developer: Reload Window**; enable MCP servers if the interview enabled them.
5. Suggest `/inventory` or **cursorLifecycle** for later updates.

## Dry run

```sh
python3 cursorAssistant.py configure --workspace . --dry-run --json
```
