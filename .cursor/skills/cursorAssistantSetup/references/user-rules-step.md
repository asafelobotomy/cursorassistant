# Optional: Cursor User Rules (post-configure)

Repo surfaces (`.cursor/rules/preferences.mdc`) hold **project-wide** prefs from the interview.
**Cursor User Rules** are IDE-wide and follow the user across workspaces — use them when the user
wants the same tone/autonomy everywhere.

## When to offer

After successful `configure` when `setup.depth` is `advanced` or `full` and answers include
`response.style`, `autonomy.level`, or `agent.persona`.

Skip when depth is `simple` (no personalization questions were asked).

## Workflow

1. Read `.cursor/cursor-assistant-answers.json`.
2. Build snippets from the mapping below (or run):

   ```sh
   python3 -c "
   import json
   from pathlib import Path
   from scripts.lifecycle.user_rules import combined_user_rule
   answers = json.loads(Path('.cursor/cursor-assistant-answers.json').read_text())
   print(combined_user_rule(answers) or '(no user rules for this depth)')
   "
   ```

3. Ask: “Save these preferences as **Cursor User Rules** (IDE-wide)?”
4. If yes and **cursor_dialog** MCP is available:
   - `cursor_dialog` with `item="rule"`, `action="list"` first (avoid duplicates)
   - `action="add"` with the combined markdown from `combined_user_rule()`
5. If MCP unavailable: paste the markdown for the user to add under **Cursor Settings → Rules**.

## Mapping

| Interview key | User Rule theme |
| --- | --- |
| `response.style` | concise / balanced / verbose output |
| `autonomy.level` | ask-first vs act-then-tell vs best-judgement |
| `agent.persona` | professional / mentor / pair-programmer / direct |

Do **not** write User Rules into the lockfile or managed `.cursor/` files.
