---
name: setup-workspace
description: Interview and install cursorAssistant into the current project (agents, skills, rules, lockfile).
---

# Set up cursorAssistant in this project

Run after the [GitHub install one-liner](https://github.com/asafelobotomy/cursorassistant#install), or to reconfigure an existing project.

## What this does

1. Runs the setup **interview** (profile, optional packs, optional MCP extensions).
2. Writes managed surfaces into the **current workspace**: `AGENTS.md`, `.cursor/agents/`, `.cursor/skills/`, `.cursor/rules/`, `.cursor/mcp.json`, and `.cursor/cursorAssistant-lock.json`.
3. Saves choices to `.cursor/cursor-assistant-answers.json`.

## Steps

1. Confirm the workspace root is the user's project.
2. If `inspect` shows `not-installed` and there is no global package, tell the user to run first:

   ```sh
   curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash -s -- .
   ```

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
