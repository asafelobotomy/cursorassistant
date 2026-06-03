"""Compose .cursor/mcp.json from core, optional extensions, and pack manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scripts.lifecycle import conditions, merge

_TOKEN_PATTERN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def _render_tokens(text: str, tokens: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        return tokens.get(match.group(1), match.group(0))

    return _TOKEN_PATTERN.sub(repl, text)

DEPRECATED_SERVER_KEYS = frozenset({"web", "filesystem", "time", "git"})
DEPRECATED_SCRIPT_NAMES = frozenset(
    {"webMcp.py", "fsMcp.py", "timeMcp.py", "gitMcp.py"}
)

CORE_REL = "template/cursor/mcp-core.json"
EXTENSIONS_REL = "template/cursor/mcp-extensions.json"
PACK_MANIFEST_RELS = {
    "secure": "template/cursor/mcp-packs/secure.json",
    "tdd": "template/cursor/mcp-packs/tdd.json",
    "lean": "template/cursor/mcp-packs/lean.json",
}


def _load_fragment(package_root: Path, rel: str) -> dict[str, Any]:
    path = package_root / rel
    if not path.is_file():
        return {}
    return merge.parse_json_object(path.read_text(encoding="utf-8"))


def sanitize_mcp_config(config: dict[str, Any]) -> dict[str, Any]:
    servers = config.get("mcpServers")
    if isinstance(servers, dict):
        for key in list(servers.keys()):
            if key in DEPRECATED_SERVER_KEYS:
                del servers[key]
    return config


def build_mcp_config(
    package_root: Path,
    answers: dict[str, Any],
    selected_packs: list[str],
    tokens: dict[str, str],
) -> dict[str, Any]:
    merged = _load_fragment(package_root, CORE_REL)
    if conditions.mcp_enabled(answers):
        merged = merge.merge_json_objects(merged, _load_fragment(package_root, EXTENSIONS_REL))
    for pack_id in selected_packs:
        rel = PACK_MANIFEST_RELS.get(pack_id)
        if rel:
            merged = merge.merge_json_objects(merged, _load_fragment(package_root, rel))
    merged = sanitize_mcp_config(merged)
    text = _render_tokens(json.dumps(merged, indent=2) + "\n", tokens)
    return merge.parse_json_object(text)


def mcp_warnings(workspace_mcp: dict[str, Any] | None) -> list[str]:
    if not workspace_mcp:
        return []
    servers = workspace_mcp.get("mcpServers")
    if not isinstance(servers, dict):
        return []
    warnings: list[str] = []
    for key in sorted(servers.keys()):
        if key in DEPRECATED_SERVER_KEYS:
            hint = (
                "use Shell/gh for git"
                if key == "git"
                else "use Cursor WebSearch/WebFetch or Agent file tools"
            )
            warnings.append(f"deprecated-mcp-server:{key} — removed in v0.9+; {hint}")
    return warnings


def deprecated_scripts_on_disk(scripts_dir: Path) -> list[str]:
    if not scripts_dir.is_dir():
        return []
    found: list[str] = []
    for name in sorted(DEPRECATED_SCRIPT_NAMES):
        if (scripts_dir / name).is_file():
            found.append(name)
    return found
