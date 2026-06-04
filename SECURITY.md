# Security

## MCP stdio servers

cursorAssistant installs Python MCP servers under `.cursor/mcp/scripts/`. They run locally via `uvx` / `mcp[cli]` with access to the workspace path.

- Review enabled servers in **Cursor Settings → MCP** and in `.cursor/mcp.json`.
- Prefer the default install (`mcp.enabled: false`) — **cursorTools** only — unless you need `devDocs`, `memory`, or pack servers.
- Deprecated servers (`web`, `filesystem`, `time`, `git`) are removed on `update`; delete leftover scripts under `.cursor/mcp/scripts/` if `inspect` reports warnings.

## Secrets

- Do not commit API keys into skills, agents, or rules.
- Pack skills such as `secretScanning` guide local scans; they do not replace vault rotation or provider revocation.
- For GitHub Models evals, use **`GITHUB_MODELS_TOKEN`** — avoid setting `GITHUB_TOKEN` to a models-only token if you use `gh` or `git push` in the same shell ([INSTALL.md](INSTALL.md)).

## Lifecycle CLI

`setup`, `update`, `repair`, and `factory-restore` write under `.cursor/` and `AGENTS.md`. Run only from trusted `package-root` paths. `factory-restore` overwrites managed files — confirm before use.

## Install workflow (setup page / bootstrap)

- The README **Install** button opens an HTTPS page that triggers a `cursor://` MCP deeplink. Review the command shown in Cursor before approving.
- Prefer the **git-only** MCP path (`mcp-launch.sh` + pinned tag clone). Avoid untrusted `CURSOR_ASSISTANT_REPO` overrides.
- `curl | bash` bootstrap is optional; read `scripts/bootstrap-from-github.sh` first.
- Do not install MCP deeplinks from unofficial mirrors or forked install pages.
- See [docs/INSTALL_SECURITY_AUDIT.md](docs/INSTALL_SECURITY_AUDIT.md).

Report vulnerabilities via the repository’s GitHub security advisory process.
