# Browser redirect and Cursor deeplink install (research)

Research date: 2026-06-04. Goal: README **Install cursorAssistant** button → browser → **Cursor opens** → install/setup begins.

## Executive summary

| Approach | Opens Cursor? | Full cursorAssistant install? | README-safe HTTPS? |
| --- | --- | --- | --- |
| **`cursor://` MCP install** | Yes (with confirm) | **No** — MCP entry only | No (needs redirect page) |
| **`cursor://vscode.git/clone`** | Likely (VS Code heritage) | **No** — clone only | No (use `vscode.dev/clone` pattern) |
| **`cursor://` agent/prompt** | N/A | **Not available** (security) | N/A |
| **Plugin install deeplink** | N/A | **Not documented** | N/A |
| **HTTPS landing → `cursor://` + fallback** | Yes | **Partial** — best practical pattern | **Yes** |
| **`curl \| bash` (current)** | No | **Yes** | Via copy-paste only |

**Conclusion:** There is no official one-deeplink equivalent to `install-from-github.sh`. The realistic design is a **redirect landing page** that tries Cursor URLs, then shows the terminal one-liner and in-app setup steps.

## What Cursor documents today

### 1. MCP install deeplink (supported)

```text
cursor://anysphere.cursor-deeplink/mcp/install?name=$NAME&config=$BASE64_ENCODED_CONFIG
```

- `config` = Base64(JSON) of a **single** server block (same shape as `mcp.json` `mcpServers` entry).
- Flow: browser → OS handler → Cursor → **user confirms** → server added to MCP config.
- Docs: [MCP install links](https://cursor.com/docs/mcp/install-links), [Plugins](https://cursor.com/docs/plugins).

**cursorAssistant implication:** You can deeplink **cursorTools** only after `.cursor/mcp/scripts/cursorToolsMcp.py` exists in the workspace (i.e. after `configure`). Deeplink alone cannot run the lifecycle interview, plugin symlink, or lockfile.

Example core config (from `template/cursor/mcp-core.json`):

```json
{
  "command": "uvx",
  "args": ["--from", "mcp[cli]", "mcp", "run", "${workspaceFolder}/.cursor/mcp/scripts/cursorToolsMcp.py"]
}
```

`${workspaceFolder}` is resolved when the server runs in an **opened project**, not at click time.

### 2. Agent / prompt deeplink (not supported)

Community requests ([agent prompt](https://forum.cursor.com/t/new-deep-link-to-trigger-agent-requests/108832), [composer population](https://forum.cursor.com/t/deep-link-support-for-chat-composer-population/120411)) were declined or not shipped for arbitrary web → Agent text (malicious prompt risk). Cursor staff noted limited **Fix in Cursor** links for Cursor-generated contexts only.

**Implication:** You cannot deeplink “Run `/cursor-assistant:setup-workspace`” or paste a setup prompt from GitHub.

### 3. Plugin install from Git URL (no public deeplink)

Plugins install via Marketplace UI, team marketplace import, or **local folder** `~/.cursor/plugins/local/<name>`. No documented:

```text
cursor://anysphere.cursor-deeplink/plugin/install?repo=...
```

Our `install-from-github.sh` already implements the local-plugin path via symlink.

### 4. VS Code git clone deeplink (likely works in Cursor)

VS Code Git extension registers:

```text
vscode://vscode.git/clone?url=<git-url>&ref=<branch|tag>
```

README-friendly HTTPS redirect (VS Code pattern):

```text
https://vscode.dev/clone?url=https://github.com/asafelobotomy/cursorassistant&ref=v0.12.0
```

`vscode.dev` redirects to the `vscode://` handler. **Cursor may honor the same paths** with `cursor://` instead of `vscode://` (fork shares Git URI handler); verify on each OS:

```sh
cursor --open-url "cursor://vscode.git/clone?url=https://github.com/asafelobotomy/cursorassistant.git&ref=v0.12.0"
```

This **clones/opens the cursorAssistant repo**, not the user’s project, and does **not** run `configure` in the consumer workspace.

## GitHub README constraints

- Markdown badges must use **`https://`** targets; raw `cursor://` in `href` is blocked or unreliable on github.com.
- Browsers do not execute shell from a link click.
- Pattern used elsewhere: **HTTPS landing page** → JavaScript / meta redirect → custom scheme.

## Implemented flow (v0.12+)

See [install/index.html](../install/index.html) and [INSTALL_SECURITY_AUDIT.md](INSTALL_SECURITY_AUDIT.md):

1. README badge → HTTPS setup page.
2. **Install in Cursor** → MCP deeplink runs **pinned `git clone`** (no `curl|bash`), then `mcp/scripts/mcp-launch.sh` → `cursorToolsMcp.py`.
3. User opens project → Reload → **`lifecycle_configure`** / setup-workspace / Agent interview.

Bootstrap: `scripts/bootstrap-from-github.sh` or `mcp-launch.sh`. Full terminal: `install-from-github.sh`.

## Earlier research: recommended product flow (phased)

### Phase A — Landing page (highest ROI)

Host `install.html` (GitHub Pages or `https://raw.githubusercontent.com/...` is static-only; prefer **GitHub Pages** on `asafelobotomy.github.io/cursorassistant/install` or repo Pages).

Button target:

```text
https://<pages>/cursorassistant/install.html
```

Page behavior:

1. **Try open Cursor** (optional): redirect to `cursor://vscode.git/clone?url=...` for users who want the package repo open first.
2. **Primary CTA:** copyable `curl … install-from-github.sh | bash -s -- .` with short explanation.
3. **Secondary:** “Already installed?” → link to docs for `configure` / `/cursor-assistant:setup-workspace`.
4. **After install:** optional button → MCP deeplink for **cursorTools** (generated by script below).

README badge:

```markdown
[![Install cursorAssistant](https://img.shields.io/badge/Install-cursorAssistant-2ea043?style=for-the-badge)](https://asafelobotomy.github.io/cursorassistant/install.html)
```

### Phase B — MCP deeplink generator (maintainer tool)

Add `scripts/generate_mcp_deeplink.py`:

- Input: `template/cursor/mcp-core.json` (or post-install workspace path).
- Output: `cursor://anysphere.cursor-deeplink/mcp/install?name=cursorTools&config=...`
- Document in INSTALL.md as **step 3 after configure**, not as full install.

### Phase C — In-Cursor setup (no deeplink)

Once the user has the package (script) and a project folder open:

1. **Reload Window** (local plugin).
2. Agent: **Set up cursorAssistant in this workspace** → `cursorAssistantSetup` / `configure`.
3. Enable MCP if needed.

This remains the only path for **lockfile + packs + project `.cursor/`**.

### Phase D — Future / upstream

- Cursor **plugin install** deeplink from GitHub URL (feature request).
- Cursor **safe** setup deeplink (e.g. allowlisted prompts for known publishers).
- `workspaceOpen` hook in plugin to load bundle when lockfile present ([Plugins docs](https://cursor.com/docs/plugins)) — does not replace first install.

## Security notes

- MCP deeplinks can install servers that run arbitrary commands ([CursorJack analysis](https://www.proofpoint.com/us/blog/threat-insight/cursorjack-weaponizing-deeplinks-exploit-cursor-ide)). Users must confirm in Cursor; only publish links from trusted docs.
- Do not embed secrets in deeplink `config`.
- Prefer pinning install script URLs to **version tags** (`v0.12.0`), not floating `main`.

## What not to do

| Anti-pattern | Why |
| --- | --- |
| MCP deeplink that runs `curl \| bash` via `command` | Dangerous; likely rejected by users and security reviewers |
| Claim README button “installs everything” via deeplink only | False for project `configure` |
| Drop `install-from-github.sh` | Still required for full install |
| Rely on clone deeplink alone | Opens wrong repo; no consumer workspace setup |

## Open questions (to validate manually)

1. Does `cursor://vscode.git/clone?...` work on Windows/macOS/Linux for Cursor 3.6+?
2. Is there a Cursor equivalent of `https://vscode.dev/clone?...` (HTTPS redirect service)?
3. Does MCP deeplink write to **user** `~/.cursor/mcp.json` or **project** `.cursor/mcp.json` when a folder is open?
4. Maximum URL length for `config=` Base64 (large args may break on some browsers)?

## References

- [Cursor MCP install links](https://cursor.com/docs/mcp/install-links)
- [Cursor Plugins](https://cursor.com/docs/plugins)
- [VS Code git clone URI handler](https://github.com/microsoft/vscode/blob/main/extensions/git/src/protocolHandler.ts)
- [VS Code issue: HTTPS clone button via vscode.dev](https://github.com/microsoft/vscode/issues/235627)
- [Forum: agent prompt deeplink](https://forum.cursor.com/t/new-deep-link-to-trigger-agent-requests/108832)
- [INSTALL.md](../INSTALL.md) — supported install path today
