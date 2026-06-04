#!/usr/bin/env python3
"""Generate install/index.html and install/deeplinks.json for the README setup button."""

from __future__ import annotations

import base64
import json
from pathlib import Path

REPO = "asafelobotomy/cursorassistant"
REPO_GIT = f"https://github.com/{REPO}.git"
ROOT = Path(__file__).resolve().parents[1]
INSTALL_DIR = ROOT / "install"
TEMPLATE = INSTALL_DIR / "index.template.html"


def read_version() -> str:
    text = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return text.splitlines()[0]


def mcp_install_deeplink(name: str, server: dict) -> str:
    payload = base64.b64encode(json.dumps(server, separators=(",", ":")).encode()).decode()
    return f"cursor://anysphere.cursor-deeplink/mcp/install?name={name}&config={payload}"


def combined_cursor_assistant_mcp(version: str) -> dict:
    """Pinned git clone on first start, then mcp-launch.sh (no curl|bash)."""
    base = "${userHome}/.local/share/cursorassistant"
    ver_dir = f"{base}/v{version}"
    current = f"{base}/current"
    launch = f"{current}/mcp/scripts/mcp-launch.sh"
    inner = (
        f'if [ ! -f "{launch}" ]; then '
        f'mkdir -p "{base}" && '
        f'git clone --depth 1 --branch "v{version}" "{REPO_GIT}" "{ver_dir}" && '
        f'ln -sfn "{ver_dir}" "{current}"; '
        f"fi; "
        f'exec bash "{launch}"'
    )
    return {"command": "bash", "args": ["-lc", inner]}


def cursor_tools_mcp(version: str) -> dict:
    """cursorTools only — requires bootstrap (see manual path on install page)."""
    launch = "${userHome}/.local/share/cursorassistant/current/mcp/scripts/mcp-launch.sh"
    return {
        "command": "bash",
        "args": ["-lc", f'exec bash "{launch}"'],
    }


def main() -> int:
    version = read_version()
    tag = f"v{version}"
    bootstrap_curl = (
        f"curl -fsSL https://raw.githubusercontent.com/{REPO}/{tag}/scripts/bootstrap-from-github.sh | bash"
    )
    bootstrap_git = (
        f'git clone --depth 1 --branch "{tag}" {REPO_GIT} '
        f'"$HOME/.local/share/cursorassistant/{version}"'
    )

    deeplinks = {
        "version": version,
        "bootstrapCurl": bootstrap_curl,
        "bootstrapGit": bootstrap_git,
        "mcpCombined": mcp_install_deeplink("cursorAssistant", combined_cursor_assistant_mcp(version)),
        "mcpCursorTools": mcp_install_deeplink("cursorTools", cursor_tools_mcp(version)),
    }

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    (INSTALL_DIR / "deeplinks.json").write_text(
        json.dumps(deeplinks, indent=2) + "\n",
        encoding="utf-8",
    )

    if not TEMPLATE.is_file():
        raise SystemExit(f"Missing template: {TEMPLATE}")

    html = TEMPLATE.read_text(encoding="utf-8")
    for key, value in (
        ("@@VERSION@@", version),
        ("@@REPO@@", REPO),
        ("@@BOOTSTRAP_CURL@@", bootstrap_curl),
        ("@@BOOTSTRAP_GIT@@", bootstrap_git),
        ("@@MCP_COMBINED@@", deeplinks["mcpCombined"]),
        ("@@MCP_CURSOR_TOOLS@@", deeplinks["mcpCursorTools"]),
    ):
        html = html.replace(key, value)
    (INSTALL_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"Wrote {INSTALL_DIR / 'index.html'}")
    print(f"Wrote {INSTALL_DIR / 'deeplinks.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
