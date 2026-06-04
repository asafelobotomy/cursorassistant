# Installing cursorAssistant

## Recommended (README button → Cursor)

1. Open the [setup page](https://asafelobotomy.github.io/cursorassistant/install/) (or [install/index.html](install/index.html) locally).
2. Click **Install in Cursor** and approve the MCP install dialog.
3. Open **your project** in Cursor → **Developer: Reload Window**.
4. In chat: **Set up cursorAssistant in this workspace**, `/cursor-assistant:setup-workspace`, or MCP tool **`lifecycle_configure`** — this runs the **interview** and installs project files.

The setup page only bootstraps the global package (`~/.local/share/cursorassistant/current`) and **cursorTools** MCP. It does **not** run the interview until step 4 inside Cursor.

Regenerate the public setup page after version bumps (in the [github.io](https://github.com/asafelobotomy/asafelobotomy.github.io) repo):

```sh
bash scripts/sync-cursorassistant-install.sh
```

## Terminal: full install (bootstrap + interview)

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.13.1/scripts/install-from-github.sh | bash -s -- .
```

## Terminal: bootstrap only

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.13.1/scripts/bootstrap-from-github.sh | bash
```

Then complete setup in Cursor (step 4 above).

## Update

```sh
python3 cursorAssistant.py update --workspace .
```

Refresh bootstrap:

```sh
CURSOR_ASSISTANT_VERSION=0.13.1 curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.13.1/scripts/bootstrap-from-github.sh | bash
```

## Requirements

- Python 3.10+, git, [Cursor](https://cursor.com/)
- `uvx` when using MCP (`pip` package `mcp[cli]`)

## Optional: GitHub Models token for evals

To run live routing evals locally (`cursorEval run`, `bash scripts/eval_models_pr_smoke.sh`):

```sh
export GITHUB_MODELS_TOKEN='ghp_...'   # models-capable PAT; do not reuse for gh if you push in the same shell
python3 tools/cursorEval/cursorEval.py --repo-root . run evals/inventory/eval.yaml --tags smoke
```

Add the same secret to the GitHub repo for CI. See [README.md](README.md#github-models-token-live-evals) and [SECURITY.md](SECURITY.md).

## See also

- [docs/README.md](docs/README.md) — documentation map
- [docs/guides/CURSOR_INSTALL_UX.md](docs/guides/CURSOR_INSTALL_UX.md)
- [docs/research/DEEPLINK_INSTALL_RESEARCH.md](docs/research/DEEPLINK_INSTALL_RESEARCH.md)
- [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
