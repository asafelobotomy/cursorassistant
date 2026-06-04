# Distribution

cursorAssistant is installed from **GitHub**, not the Cursor Marketplace.

## Primary install

See [INSTALL.md](../INSTALL.md) and the README **Install** section:

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash -s -- /path/to/your-project
```

## Plugin manifest (maintainers)

`.cursor-plugin/plugin.json` describes the bundle layout for Cursor’s **local plugin** loader. The install script symlinks the package to `~/.cursor/plugins/local/cursor-assistant` and reloads Cursor — no marketplace required.

Validate before release:

```sh
python3 scripts/validate_plugin.py
```

## Archived: Marketplace submission

If we pursue a public listing later, see [docs/archive/MARKETPLACE_PUBLISH.md](archive/MARKETPLACE_PUBLISH.md).
