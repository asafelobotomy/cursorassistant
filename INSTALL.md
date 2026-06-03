# Installing cursorAssistant

## Into another project (Cursor)

1. Clone or copy this repository anywhere on disk.
2. From the consumer project root:

```sh
python3 /path/to/cursorassistant/cursorAssistant.py setup \
  --workspace . \
  --package-root /path/to/cursorassistant \
  --json
```

3. Open the project in **Cursor**. Reload the window if rules or MCP do not appear.
4. Confirm:
   - `AGENTS.md` at the repo root
   - `.cursor/agents/`, `.cursor/skills/`, `.cursor/rules/`
   - `.cursor/cursorAssistant-lock.json`

To preserve custom routing in `AGENTS.md` across updates, wrap additions in:

```markdown
<!-- user-added -->
## Your section
...
<!-- /user-added -->
```

Custom MCP servers in `.cursor/mcp.json` are merged with the package template on update.

## Update after pulling a new cursorAssistant release

```sh
python3 /path/to/cursorassistant/cursorAssistant.py update \
  --workspace . \
  --package-root /path/to/cursorassistant \
  --json
```

If the lockfile is malformed or files are missing, use `repair`. For a full reset of managed surfaces, use `factory-restore` (destructive).

Non-interactive setup with interview answers:

```sh
python3 /path/to/cursorassistant/cursorAssistant.py setup \
  --workspace . \
  --package-root /path/to/cursorassistant \
  --answers /path/to/answers.json \
  --json
```

## Install into this package repo (dogfooding)

```sh
cd /path/to/cursorassistant
bash scripts/dogfood.sh
```

This writes `.cursor/*` into the package tree for local development (MCP bundle off; `cursorTools` only). Commit the resulting snapshot so the package repo uses the same surfaces as consumers.

## MCP scripts

v0.4 installs **cursorTools** plus a shared MCP bundle (git, web, testing, memory, security, filesystem, time, devDocs) when `mcp.enabled` is true (default).

Disable the bundle:

```json
{ "mcp.enabled": false }
```

List eval suites:

```sh
python3 tools/cursorEval/cursorEval.py list --repo-root .
python3 tools/cursorEval/cursorEval.py validate --repo-root .
python3 tools/cursorEval/cursorEval.py coverage --repo-root .
```

Run evals (requires a Models API token):

```sh
python3 tools/cursorEval/cursorEval.py run evals/lifecycleAudit/eval.yaml --repo-root .
```

Use **`GITHUB_MODELS_TOKEN`** in your shell (not `GITHUB_TOKEN`). Exporting `GITHUB_TOKEN` overrides `gh` and `git push` with that value. Store the Models token in GNOME Keyring as `service=github-models` and load it in `~/.bashrc` as `GITHUB_MODELS_TOKEN` (see this repo’s INSTALL notes or your local shell config).

## Packs and profiles

Setup interview supports:

- **Profiles:** `balanced` (default), `lean` (auto-selects lean pack)
- **Packs:** `lean`, `secure`, `tdd` (multi-select via `--answers`)

Example answers file:

```json
{
  "profile.selected": "balanced",
  "packs.selected": ["secure", "tdd"]
}
```
