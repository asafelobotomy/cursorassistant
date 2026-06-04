# Install workflow security and efficiency audit

Audit of the README → setup page → MCP bootstrap → `lifecycle_configure` path (v0.12.0).

## Threat model

| Asset | Risk |
| --- | --- |
| User machine (`~/.local/share/cursorassistant`, `~/.cursor/plugins`) | Malicious or substituted package runs via MCP |
| Consumer workspace `.cursor/` | Lifecycle writes managed files; untrusted `package-root` is dangerous |
| GitHub raw / MITM on download | Supply-chain compromise |
| MCP deeplink in README/page | Social engineering (CursorJack-class prompts) |

## Findings and mitigations

### Critical — `curl | bash` inside MCP server command (fixed)

**Was:** Combined MCP deeplink ran `curl -fsSL raw.githubusercontent.com/.../bootstrap.sh | bash` on every first MCP start.

**Risk:** Pipe-to-bash from network; tag move or account compromise executes arbitrary code; scary trust surface in MCP UI.

**Mitigation:** MCP launcher uses **pinned `git clone --depth 1 --branch vVERSION`** only (same as `bootstrap-from-github.sh`). Manual footer still documents `curl | bash` for users who prefer it, with “review script first” guidance.

### High — bootstrap fallback to default branch (fixed)

**Was:** Missing tag cloned `main` without pin.

**Mitigation:** Bootstrap **fails** if `v$VERSION` cannot be cloned; user must set `CURSOR_ASSISTANT_VERSION` or fix network.

### High — `CURSOR_ASSISTANT_REPO` override (fixed)

**Was:** Any git URL accepted.

**Mitigation:** Allowlist: `https://github.com/asafelobotomy/cursorassistant.git` only (override via env still possible for forks in dev, but validated).

### Medium — `${userHome}` inside `bash -lc` single quotes

**Risk:** If Cursor does not expand variables before spawning bash, paths are wrong.

**Mitigation:** Launcher script uses `$HOME` / explicit paths expanded by bash; MCP config uses `mcp/scripts/mcp-launch.sh` with `command` + `args` (no inline `curl | bash`).

### Medium — `packageRoot` MCP parameter

**Risk:** Agent passes path to non-package directory.

**Mitigation:** `cursorToolsMcp` validates `is_package_root()` before running CLI (same markers as lifecycle).

### Medium — install page hosted on GitHub Pages

**Risk:** Pages account compromise swaps deeplink in `index.html`.

**Mitigation:** Pin install page to **tag** in README; regenerate via `generate_install_page.py` in CI; user can diff `install/deeplinks.json` against release tag.

### Low — no commit-SHA pin

**Status:** Tag pin (`v0.12.0`) is acceptable for solo-dev speed. Optional `CURSOR_ASSISTANT_COMMIT` documented for paranoid installs.

### Efficiency

| Item | Assessment |
| --- | --- |
| Split bootstrap vs configure | **Good** — interview only in Cursor |
| `git clone --depth 1` | **Good** |
| `current` symlink | **Good** — stable MCP path |
| Combined MCP bash wrapper | **Replaced** with thin `mcp-launch.sh` |
| Reload Window step | **Required** by Cursor plugin model — keep |
| `lifecycle_configure` vs Agent skill | **Equivalent** — MCP for automation, skill for interview UX |

## Recommended user path (secure)

1. Setup page → **Install in Cursor** (git bootstrap + cursorTools via `mcp-launch.sh`).
2. Open project → Reload Window.
3. **Set up cursorAssistant in this workspace** (interview).

## Recommended maintainer checklist (each release)

```sh
python3 scripts/generate_install_page.py
python3 scripts/validate_plugin.py
# Diff install/index.html deeplink against tag
git tag -v v$(head -1 VERSION)
```

## References

- [SECURITY.md](../SECURITY.md)
- [DEEPLINK_INSTALL_RESEARCH.md](DEEPLINK_INSTALL_RESEARCH.md)
- [Cursor MCP install links](https://cursor.com/docs/mcp/install-links)
- [CursorJack (MCP deeplink abuse)](https://www.proofpoint.com/us/blog/threat-insight/cursorjack-weaponizing-deeplinks-exploit-cursor-ide)
