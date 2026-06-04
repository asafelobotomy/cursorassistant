# Installing cursorAssistant

## Recommended (README button → Cursor)

1. Open the [setup page](https://asafelobotomy.github.io/cursorassistant/install/) (or [install/index.html](install/index.html) locally).
2. Click **Install in Cursor** and approve the MCP install dialog.
3. Open **your project** in Cursor → **Developer: Reload Window**.
4. In chat: **Set up cursorAssistant in this workspace**, `/cursor-assistant:setup-workspace`, or MCP tool **`lifecycle_configure`** — this runs the **interview** and installs project files.

The setup page only bootstraps the global package (`~/.local/share/cursorassistant/current`) and **cursorTools** MCP. It does **not** run the interview until step 4 inside Cursor.

Regenerate the setup page after version bumps:

```sh
python3 scripts/generate_install_page.py
```

## Terminal: full install (bootstrap + interview)

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.1/scripts/install-from-github.sh | bash -s -- .
```

## Terminal: bootstrap only

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.1/scripts/bootstrap-from-github.sh | bash
```

Then complete setup in Cursor (step 4 above).

## Update

```sh
python3 cursorAssistant.py update --workspace .
```

Refresh bootstrap:

```sh
CURSOR_ASSISTANT_VERSION=0.12.1 curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.1/scripts/bootstrap-from-github.sh | bash
```

## Requirements

- Python 3.10+, git, [Cursor](https://cursor.com/)
- `uvx` when using MCP (`pip` package `mcp[cli]`)

## See also

- [docs/CURSOR_INSTALL_UX.md](docs/CURSOR_INSTALL_UX.md)
- [docs/DEEPLINK_INSTALL_RESEARCH.md](docs/DEEPLINK_INSTALL_RESEARCH.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
