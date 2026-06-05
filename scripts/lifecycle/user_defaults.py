"""User-scoped default answers for cursorAssistant setup interviews."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULTS_REL = ".cursor/cursor-assistant-defaults.json"


def defaults_path() -> Path:
    return Path.home() / DEFAULTS_REL


def load_defaults() -> dict[str, Any] | None:
    path = defaults_path()
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"defaults file must contain a JSON object: {path}")
    return payload


def save_defaults(answers: dict[str, Any], *, strip_ephemeral: bool = True) -> Path:
    from scripts.lifecycle import interview

    path = defaults_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    to_write = (
        interview.sanitize_answers_for_save(answers) if strip_ephemeral else dict(answers)
    )
    path.write_text(json.dumps(to_write, indent=2) + "\n", encoding="utf-8")
    return path


def merge_defaults(draft: dict[str, Any], defaults: dict[str, Any] | None) -> dict[str, Any]:
    """User defaults are the baseline; explicit draft keys win."""
    merged: dict[str, Any] = {}
    if defaults:
        merged.update(defaults)
    merged.update(draft)
    return merged
