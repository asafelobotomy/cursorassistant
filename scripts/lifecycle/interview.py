"""Minimal interview and plan helpers for cursorAssistant setup."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.lifecycle import packs


def load_interview(package_root: Path) -> dict[str, Any]:
    path = package_root / "template" / "setup" / "interview.json"
    if not path.is_file():
        return {"questions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_answers(
    interview: dict[str, Any],
    answers: dict[str, Any] | None,
    lockfile: dict[str, Any] | None,
    *,
    package_root: Path | None = None,
) -> dict[str, Any]:
    explicit = set(answers.keys()) if answers else set()
    resolved: dict[str, Any] = {}
    for question in interview.get("questions", []):
        question_id = question["id"]
        if answers and question_id in answers:
            resolved[question_id] = answers[question_id]
            continue
        if lockfile:
            if question_id == "profile.selected" and lockfile.get("profile"):
                resolved[question_id] = lockfile["profile"]
                continue
            if question_id == "packs.selected" and isinstance(lockfile.get("selectedPacks"), list):
                resolved[question_id] = list(lockfile["selectedPacks"])
                continue
            if question_id == "mcp.enabled" and lockfile.get("mcpEnabled") is not None:
                resolved[question_id] = bool(lockfile["mcpEnabled"])
                continue
            setup_answers = lockfile.get("setupAnswers", {})
            if isinstance(setup_answers, dict) and question_id in setup_answers:
                resolved[question_id] = setup_answers[question_id]
                continue
        if question_id == "packs.selected":
            continue
        if "default" in question:
            resolved[question_id] = question["default"]

    if "packs.selected" not in resolved:
        if package_root is not None:
            profile_id = resolved.get("profile.selected", "balanced")
            profile_registry = packs.load_profile_registry(package_root)
            profile = packs.profile_by_id(profile_registry, profile_id)
            resolved["packs.selected"] = list(profile.get("defaultPacks", [])) if profile else []
        else:
            resolved["packs.selected"] = []
    elif (
        "packs.selected" not in explicit
        and resolved["packs.selected"] == []
        and package_root is not None
    ):
        profile_id = resolved.get("profile.selected", "balanced")
        profile_registry = packs.load_profile_registry(package_root)
        profile = packs.profile_by_id(profile_registry, profile_id)
        if profile and profile.get("defaultPacks"):
            resolved["packs.selected"] = list(profile["defaultPacks"])

    return resolved


def answers_to_lockfile_fields(
    answers: dict[str, Any],
    selected_packs: list[str],
) -> dict[str, Any]:
    profile = answers.get("profile.selected", "balanced")
    setup_answers = {
        key: value
        for key, value in answers.items()
        if key not in {"profile.selected", "packs.selected", "mcp.enabled"}
    }
    return {
        "profile": profile,
        "selectedPacks": selected_packs,
        "mcpEnabled": bool(answers.get("mcp.enabled", True)),
        "setupAnswers": setup_answers,
    }
