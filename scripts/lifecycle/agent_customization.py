"""Plan-time agent customization questions and token rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_agent_registry(package_root: Path) -> dict[str, Any]:
    path = package_root / "template" / "setup" / "agent-registry.json"
    if not path.is_file():
        return {"agents": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _installed_agent_ids(package_root: Path) -> set[str]:
    policy_path = package_root / "template" / "setup" / "install-policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    return {
        entry["id"]
        for entry in policy.get("entries", [])
        if entry.get("id", "").startswith("agents.")
    }


def agent_questions(package_root: Path) -> list[dict[str, Any]]:
    registry = load_agent_registry(package_root)
    installed = _installed_agent_ids(package_root)
    questions: list[dict[str, Any]] = []
    for agent in registry.get("agents", []):
        if agent.get("status") != "active":
            continue
        entry_id = agent.get("manifestEntryId")
        if entry_id not in installed:
            continue
        customization = agent.get("customization") or {}
        for item in customization.get("questions") or []:
            answer_key = item.get("answerKey")
            if not isinstance(answer_key, str) or not answer_key:
                continue
            questions.append(
                {
                    "id": answer_key,
                    "prompt": item.get("prompt", answer_key),
                    "type": item.get("type", "choice"),
                    "options": list(item.get("options") or []),
                    "default": item.get("default"),
                    "batch": "agent",
                    "agentId": agent.get("id"),
                }
            )
    return questions


def agent_tokens(package_root: Path, answers: dict[str, Any] | None) -> dict[str, str]:
    if not answers:
        return {}
    registry = load_agent_registry(package_root)
    tokens: dict[str, str] = {}
    for agent in registry.get("agents", []):
        customization = agent.get("customization") or {}
        for item in customization.get("questions") or []:
            answer_key = item.get("answerKey")
            token_key = item.get("token")
            render = item.get("render") or {}
            if not isinstance(answer_key, str) or not isinstance(token_key, str):
                continue
            selected = answers.get(answer_key)
            if selected is None:
                default = item.get("default")
                if default is not None:
                    selected = default
            if selected is None:
                continue
            rendered = render.get(str(selected))
            if rendered:
                tokens[token_key] = str(rendered)
    return tokens
