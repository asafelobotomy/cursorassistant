"""Answer-based conditions for managed install entries."""

from __future__ import annotations

from typing import Any


def conditions_match(required_when: dict[str, Any] | None, answers: dict[str, Any] | None) -> bool:
    if not required_when:
        return True
    answers = answers or {}
    if "oneOf" in required_when:
        key = required_when.get("key")
        values = required_when.get("oneOf")
        if not isinstance(key, str) or not isinstance(values, list):
            return False
        return answers.get(key) in values
    for key, expected in required_when.items():
        if key == "oneOf":
            continue
        actual = answers.get(key)
        if isinstance(expected, bool):
            if bool(actual) != expected:
                return False
        elif actual != expected:
            return False
    return True


def mcp_enabled(answers: dict[str, Any] | None) -> bool:
    if not answers:
        return False
    return bool(answers.get("mcp.enabled", False))
