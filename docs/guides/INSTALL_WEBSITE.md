# Install website (GitHub Pages)

Public URL: [https://asafelobotomy.github.io/cursorassistant/install/](https://asafelobotomy.github.io/cursorassistant/install/)

Root [https://asafelobotomy.github.io/cursorassistant/](https://asafelobotomy.github.io/cursorassistant/) redirects to `install/`.

## Purpose

| Phase | Where | What |
| --- | --- | --- |
| Bootstrap | HTTPS setup page | Pinned `cursor://` MCP deeplink → `git clone` tag `vVERSION` |
| Project install | Cursor chat | Interview via `cursorAssistantSetup` / `lifecycle_configure` |

The page does **not** run the interview (no agent deeplink — security). It makes bootstrap **transparent**, **progress-tracked**, and **copy-friendly**.

## Secure design

- MCP button uses **git clone of release tag only** (see `scripts/generate_install_page.py`).
- Human-readable **MCP preview** on the page matches `install/deeplinks.json`.
- Users can diff `deeplinks.json` on GitHub against the tag before approving MCP.
- `curl | bash` remains in a collapsed manual section with review guidance.

## Maintainer workflow

```sh
# After VERSION bump:
python3 scripts/generate_install_page.py
python3 scripts/check_install_page.py
git add install/ index.html
```

CI runs `check_install_page.py` on every push. **GitHub Pages** workflow deploys `_site` (root redirect + `install/`) on install-related changes.

## UX features (install page)

- Primary **Install in Cursor** + **Copy setup phrase**
- Browser-local **progress checklist** (four steps)
- **What you get** table (agents/skills counts from `catalog.json`)
- **Troubleshooting** and manual bootstrap
- Links to release tag and `INSTALL.md`

## Future enhancements (optional)

| Idea | Notes |
| --- | --- |
| Post-setup status page | Would need a non-secret callback or user-pasted `inspect` JSON — not in v0.13 |
| Plugin marketplace deeplink | Not documented by Cursor yet |
| i18n | Single locale for now |

See also [CURSOR_INSTALL_UX.md](CURSOR_INSTALL_UX.md), [DEEPLINK_INSTALL_RESEARCH.md](../research/DEEPLINK_INSTALL_RESEARCH.md).
