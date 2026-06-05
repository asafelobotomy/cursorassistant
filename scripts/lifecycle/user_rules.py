"""Map setup interview answers to optional Cursor User Rules snippets."""

from __future__ import annotations

from typing import Any

from scripts.lifecycle.preference_tokens import (
    AGENT_PERSONA,
    AUTONOMY_LEVEL,
    RESPONSE_STYLE,
)

USER_RULE_FIELDS: tuple[tuple[str, str, dict[str, str]], ...] = (
    ("response.style", "Response style", RESPONSE_STYLE),
    ("autonomy.level", "Autonomy", AUTONOMY_LEVEL),
    ("agent.persona", "Interaction tone", AGENT_PERSONA),
)


def user_rule_candidates(answers: dict[str, Any] | None) -> list[dict[str, str]]:
    """Return rule snippets for advanced/full interviews (IDE-wide prefs, not lockfile)."""
    if not answers:
        return []
    depth = str(answers.get("setup.depth", "simple"))
    if depth not in {"advanced", "full"}:
        return []

    candidates: list[dict[str, str]] = []
    for key, title, mapping in USER_RULE_FIELDS:
        value = answers.get(key)
        if value is None:
            continue
        text = mapping.get(str(value))
        if not text:
            continue
        candidates.append({"key": key, "title": title, "rule": text})
    return candidates


def combined_user_rule(answers: dict[str, Any] | None) -> str | None:
    """Single markdown block suitable for pasting into Cursor User Rules."""
    parts = [item["rule"] for item in user_rule_candidates(answers)]
    if not parts:
        return None
    return "\n\n".join(parts)
