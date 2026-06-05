"""Pack-gated setup interview questions and token rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.lifecycle import packs

PACK_BATCH = "pack"


def pack_interview_path(package_root: Path, pack_id: str, pack_registry: dict[str, Any] | None = None) -> Path:
    registry = pack_registry if pack_registry is not None else packs.load_pack_registry(package_root)
    for pack in registry.get("packs", []):
        if pack.get("id") == pack_id:
            rel = pack.get("interviewPath")
            if isinstance(rel, str) and rel.strip():
                return package_root / rel
    return package_root / "packs" / pack_id / "interview.json"


def load_pack_interview(package_root: Path, pack_id: str) -> dict[str, Any]:
    path = pack_interview_path(package_root, pack_id)
    if not path.is_file():
        return {"questions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def questions_for_pack(package_root: Path, pack_id: str) -> list[dict[str, Any]]:
    data = load_pack_interview(package_root, pack_id)
    questions: list[dict[str, Any]] = []
    for item in data.get("questions", []):
        if not isinstance(item, dict) or "id" not in item:
            continue
        question = dict(item)
        question.setdefault("batch", PACK_BATCH)
        question["packId"] = pack_id
        questions.append(question)
    return questions


def pack_questions(package_root: Path, selected_packs: list[str]) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for pack_id in sorted(selected_packs):
        questions.extend(questions_for_pack(package_root, pack_id))
    return questions


def pack_question_ids(package_root: Path, selected_packs: list[str]) -> set[str]:
    return {question["id"] for question in pack_questions(package_root, selected_packs)}


def question_pack_id(package_root: Path, question_id: str, selected_packs: list[str]) -> str | None:
    for question in pack_questions(package_root, selected_packs):
        if question["id"] == question_id:
            return str(question.get("packId", ""))
    return None


def resolve_pack_defaults(
    package_root: Path,
    answers: dict[str, Any] | None,
    selected_packs: list[str],
) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    explicit = set(answers.keys()) if answers else set()
    for question in pack_questions(package_root, selected_packs):
        question_id = question["id"]
        if answers and question_id in answers:
            resolved[question_id] = answers[question_id]
        elif "default" in question:
            resolved[question_id] = question["default"]
    return resolved


def pack_interview_tokens(
    package_root: Path,
    selected_packs: list[str],
    answers: dict[str, Any] | None,
) -> dict[str, str]:
    if not answers:
        return {}
    tokens: dict[str, str] = {}
    for question in pack_questions(package_root, selected_packs):
        token_key = question.get("token")
        render = question.get("render") or {}
        if not isinstance(token_key, str):
            continue
        selected = answers.get(question["id"])
        if selected is None and "default" in question:
            selected = question["default"]
        if selected is None:
            continue
        rendered = render.get(str(selected))
        if rendered:
            tokens[token_key] = str(rendered)
    return tokens


def split_pack_answers(
    package_root: Path,
    answers: dict[str, Any],
    selected_packs: list[str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    pack_ids = pack_question_ids(package_root, selected_packs)
    setup_answers = {
        key: value
        for key, value in answers.items()
        if key not in pack_ids
    }
    pack_answers: dict[str, dict[str, Any]] = {}
    for pack_id in selected_packs:
        pack_map: dict[str, Any] = {}
        for question in questions_for_pack(package_root, pack_id):
            question_id = question["id"]
            if question_id in answers:
                pack_map[question_id] = answers[question_id]
        if pack_map:
            pack_answers[pack_id] = pack_map
    return setup_answers, pack_answers


def merge_pack_answers_into_flat(
    setup_answers: dict[str, Any],
    pack_answers: dict[str, Any] | None,
) -> dict[str, Any]:
    merged = dict(setup_answers)
    if not isinstance(pack_answers, dict):
        return merged
    for pack_map in pack_answers.values():
        if isinstance(pack_map, dict):
            merged.update(pack_map)
    return merged


def pending_pack_ids(
    package_root: Path,
    selected_packs: list[str],
    *,
    explicit_keys: set[str],
) -> list[str]:
    pending: list[str] = []
    for pack_id in sorted(selected_packs):
        for question in questions_for_pack(package_root, pack_id):
            if question["id"] not in explicit_keys:
                pending.append(pack_id)
                break
    return pending
