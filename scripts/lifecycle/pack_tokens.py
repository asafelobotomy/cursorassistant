"""Load and merge capability-pack instruction tokens."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scripts.lifecycle import packs

# Core interview maps lean.reasoning.mode → pack:reasoning-mode via preference_tokens.py.
RESERVED_LEGACY_ALIASES = frozenset({"pack:reasoning-mode"})

_NAMESPACED_RE = re.compile(r"^pack:([a-z0-9-]+):(.+)$")


def pack_tokens_path(package_root: Path, pack_id: str, pack_registry: dict[str, Any] | None = None) -> Path:
    registry = pack_registry if pack_registry is not None else packs.load_pack_registry(package_root)
    for pack in registry.get("packs", []):
        if pack.get("id") == pack_id:
            rel = pack.get("tokensPath")
            if isinstance(rel, str) and rel.strip():
                return package_root / rel
    return package_root / "packs" / pack_id / "tokens.json"


def normalize_token_key(pack_id: str, raw_key: str) -> str:
    key = raw_key.strip()
    match = _NAMESPACED_RE.match(key)
    if match:
        if match.group(1) == pack_id:
            return key
        return f"pack:{pack_id}:{match.group(2)}"
    if key.startswith("pack:"):
        return f"pack:{pack_id}:{key[len('pack:'):]}"
    return f"pack:{pack_id}:{key}"


def legacy_alias_key(namespaced_key: str, pack_id: str) -> str | None:
    prefix = f"pack:{pack_id}:"
    if not namespaced_key.startswith(prefix):
        return None
    short = namespaced_key[len(prefix) :]
    if not short:
        return None
    return f"pack:{short}"


def load_pack_token_file(package_root: Path, pack_id: str) -> dict[str, str]:
    path = pack_tokens_path(package_root, pack_id)
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"pack tokens must be a JSON object: {path}")
    return {str(key): str(value) for key, value in payload.items()}


def pack_tokens(package_root: Path, selected_packs: list[str]) -> dict[str, str]:
    """Merge namespaced pack tokens and one-release legacy aliases (v0.16.1).

    Legacy aliases (`pack:review-depth`, etc.) resolve to the last selected pack
    in sorted pack-id order that defines the short key. Reserved aliases owned by
    core interview (e.g. `pack:reasoning-mode`) are never emitted here.
    """
    merged: dict[str, str] = {}
    aliases: dict[str, str] = {}
    for pack_id in sorted(selected_packs):
        raw = load_pack_token_file(package_root, pack_id)
        for raw_key, value in raw.items():
            namespaced = normalize_token_key(pack_id, raw_key)
            merged[namespaced] = value
            alias = legacy_alias_key(namespaced, pack_id)
            if alias and alias not in RESERVED_LEGACY_ALIASES:
                aliases[alias] = value
    merged.update(aliases)
    return merged
