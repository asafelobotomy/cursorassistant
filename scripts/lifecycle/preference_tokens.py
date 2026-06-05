"""Render interview personalization answers into instruction tokens."""

from __future__ import annotations

from typing import Any

RESPONSE_STYLE: dict[str, str] = {
    "concise": "Prefer code with minimal prose; skip rationale unless asked.",
    "balanced": "Provide code with brief explanation of non-obvious choices.",
    "verbose": "Provide code with full step-by-step explanation.",
}

AUTONOMY_LEVEL: dict[str, str] = {
    "ask-first": "When intent is ambiguous, ask before acting.",
    "act-then-tell": "Make a reasonable choice on low-risk ambiguity, then explain.",
    "best-judgement": "Act on best judgement for low-risk choices; ask only when irreversible.",
}

AGENT_PERSONA: dict[str, str] = {
    "professional": "Use a concise, neutral, precise tone.",
    "mentor": "Use a patient, explanatory, teaching-focused tone.",
    "pair-programmer": "Use a collaborative, iterative, direct tone.",
    "direct": "Minimize chat; maximize useful output.",
}

TESTING_PHILOSOPHY: dict[str, str] = {
    "always": "Write or update tests alongside every code change unless explicitly told not to.",
    "suggest": "Propose tests for meaningful changes but do not block on them.",
    "skip": "Do not write or suggest tests unless asked.",
}

LEAN_REASONING_MODE: dict[str, str] = {
    "compressed": (
        "Use compressed state receipts for routine tasks; reserve explicit reasoning "
        "for critical findings and irreversible decisions."
    ),
    "silent": "Emit results only; no reasoning narration; one line per action taken.",
}


def preference_tokens(answers: dict[str, Any] | None) -> dict[str, str]:
    if not answers:
        return {}
    tokens: dict[str, str] = {}
    depth = str(answers.get("setup.depth", "simple"))
    if depth in {"advanced", "full"}:
        style = str(answers.get("response.style", "balanced"))
        tokens["RESPONSE_STYLE"] = RESPONSE_STYLE.get(style, RESPONSE_STYLE["balanced"])
        autonomy = str(answers.get("autonomy.level", "ask-first"))
        tokens["AUTONOMY_LEVEL"] = AUTONOMY_LEVEL.get(autonomy, AUTONOMY_LEVEL["ask-first"])
        persona = str(answers.get("agent.persona", "professional"))
        tokens["AGENT_PERSONA"] = AGENT_PERSONA.get(persona, AGENT_PERSONA["professional"])
    if depth == "full":
        testing = str(answers.get("testing.philosophy", "always"))
        tokens["TESTING_PHILOSOPHY"] = TESTING_PHILOSOPHY.get(testing, TESTING_PHILOSOPHY["always"])
    lean_mode = answers.get("lean.reasoning.mode")
    if lean_mode in LEAN_REASONING_MODE:
        tokens["pack:reasoning-mode"] = LEAN_REASONING_MODE[str(lean_mode)]
    return tokens
