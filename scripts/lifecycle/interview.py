"""Interview and plan helpers for cursorAssistant setup."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from scripts.lifecycle import agent_customization, pack_interview, packs, skill_customization

DEFAULT_ANSWERS_REL = ".cursor/cursor-assistant-answers.json"
LOCKFILE_TOP_KEYS = frozenset({"profile.selected", "packs.selected", "mcp.enabled"})
PREFLIGHT_BATCH = "preflight"
COPY_FROM_KEY_PREFIX = "setup.copyFrom."
USER_DEFAULTS_KEY_PREFIX = "setup.defaults."

DEPTH_BATCHES: dict[str, set[str]] = {
    "simple": {"setup", "simple", "agent"},
    "advanced": {"setup", "simple", "advanced", "agent"},
    "full": {"setup", "simple", "advanced", "full", "agent"},
}


def load_interview(package_root: Path) -> dict[str, Any]:
    path = package_root / "template" / "setup" / "interview.json"
    if not path.is_file():
        return {"questions": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _predicate_matches(predicate: dict[str, Any], answers: dict[str, Any]) -> bool:
    key = predicate.get("key")
    if not isinstance(key, str):
        return False
    actual = answers.get(key)
    if "equals" in predicate:
        return actual == predicate["equals"]
    if "contains" in predicate:
        return isinstance(actual, list) and predicate["contains"] in actual
    return False


def is_ephemeral_key(key: str) -> bool:
    return key.startswith(COPY_FROM_KEY_PREFIX)


def is_user_defaults_only_key(key: str) -> bool:
    return key.startswith(USER_DEFAULTS_KEY_PREFIX)


def sanitize_answers_for_save(answers: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in answers.items()
        if not is_ephemeral_key(key) and not is_user_defaults_only_key(key)
    }


def agent_and_skill_questions(package_root: Path) -> list[dict[str, Any]]:
    """Agent batch in D4 order: commit → docs → planner → review → debugger → ciPreflight → deps → inventory."""
    agents = agent_customization.agent_questions(package_root)
    skills = skill_customization.skill_questions(package_root)
    ordered: list[dict[str, Any]] = []
    inserted_skills = False
    for question in agents:
        ordered.append(question)
        if question.get("agentId") == "debugger" and not inserted_skills:
            ordered.extend(skills)
            inserted_skills = True
    if skills and not inserted_skills:
        ordered.extend(skills)
    return ordered


def question_active(
    question: dict[str, Any],
    answers: dict[str, Any],
    allowed_batches: set[str],
) -> bool:
    batch = question.get("batch", "simple")
    if batch == PREFLIGHT_BATCH:
        allowed = {PREFLIGHT_BATCH}
    elif batch not in allowed_batches:
        return False
    required_when = question.get("requiredWhen")
    if not required_when:
        return True
    if isinstance(required_when.get("any"), list):
        return any(_predicate_matches(item, answers) for item in required_when["any"])
    for key, expected in required_when.items():
        if key == "any":
            continue
        actual = answers.get(key)
        if isinstance(expected, bool):
            if bool(actual) != expected:
                return False
        elif actual != expected:
            return False
    return True


def active_questions(
    interview: dict[str, Any],
    answers: dict[str, Any] | None,
    *,
    package_root: Path | None,
) -> list[dict[str, Any]]:
    resolved = resolve_answers(interview, answers, package_root=package_root)
    merged = dict(resolved)
    if answers:
        merged.update(answers)
    depth = str(merged.get("setup.depth", "simple"))
    allowed = DEPTH_BATCHES.get(depth, DEPTH_BATCHES["simple"])
    preflight: list[dict[str, Any]] = []
    static: list[dict[str, Any]] = []
    for question in interview.get("questions", []):
        batch = question.get("batch", "simple")
        if batch == PREFLIGHT_BATCH:
            if question_active(question, merged, {PREFLIGHT_BATCH}):
                preflight.append(question)
        elif question_active(question, merged, allowed):
            static.append(question)
    if package_root is None:
        return preflight + static
    agent_filtered = [
        question
        for question in agent_and_skill_questions(package_root)
        if question.get("batch", "agent") in allowed
    ]
    selected_packs = packs.resolve_selected_packs(package_root, merged, None)
    allowed_with_pack = set(allowed) | {pack_interview.PACK_BATCH}
    pack_filtered = [
        question
        for question in pack_interview.pack_questions(package_root, selected_packs)
        if question_active(question, merged, allowed_with_pack)
    ]
    return preflight + static + agent_filtered + pack_filtered


def resolve_answers(
    interview: dict[str, Any],
    answers: dict[str, Any] | None,
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

    if package_root is not None:
        for question in agent_and_skill_questions(package_root):
            question_id = question["id"]
            if answers and question_id in answers:
                resolved[question_id] = answers[question_id]
            elif "default" in question and question_id not in resolved:
                resolved[question_id] = question["default"]
        selected_packs = packs.resolve_selected_packs(package_root, resolved, None)
        resolved.update(
            pack_interview.resolve_pack_defaults(package_root, answers, selected_packs)
        )

    return resolved


def answers_to_lockfile_fields(
    answers: dict[str, Any],
    selected_packs: list[str],
    *,
    package_root: Path | None = None,
) -> dict[str, Any]:
    profile = answers.get("profile.selected", "balanced")
    if package_root is None:
        setup_answers = {
            key: value
            for key, value in answers.items()
            if key not in LOCKFILE_TOP_KEYS
            and not is_ephemeral_key(key)
            and not is_user_defaults_only_key(key)
        }
        pack_answers: dict[str, dict[str, Any]] = {}
    else:
        setup_all, pack_answers = pack_interview.split_pack_answers(
            package_root, answers, selected_packs
        )
        setup_answers = {
            key: value
            for key, value in setup_all.items()
            if key not in LOCKFILE_TOP_KEYS
            and not is_ephemeral_key(key)
            and not is_user_defaults_only_key(key)
        }
        pack_answers = {pack_id: pack_map for pack_id, pack_map in pack_answers.items() if pack_id in selected_packs}
    payload: dict[str, Any] = {
        "profile": profile,
        "selectedPacks": selected_packs,
        "mcpEnabled": bool(answers.get("mcp.enabled", False)),
        "setupAnswers": setup_answers,
    }
    if pack_answers:
        payload["packAnswers"] = pack_answers
    return payload


def default_answers_path(workspace: Path) -> Path:
    return workspace / DEFAULT_ANSWERS_REL


def write_answers_file(path: Path, answers: dict[str, Any], *, sanitize: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = sanitize_answers_for_save(answers) if sanitize else dict(answers)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _question_payload(question: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": question["id"],
        "prompt": question.get("prompt", question["id"]),
        "type": question.get("type", "choice"),
        "batch": question.get("batch", "simple"),
    }
    if "options" in question:
        payload["options"] = question["options"]
    if "default" in question:
        payload["default"] = question["default"]
    if "packId" in question:
        payload["packId"] = question["packId"]
    return payload


def interview_questions_payload(
    interview_data: dict[str, Any],
    answers: dict[str, Any] | None,
    *,
    package_root: Path | None,
    explicit_keys: set[str] | None = None,
) -> dict[str, Any]:
    explicit = explicit_keys if explicit_keys is not None else set(answers or {})
    merged = dict(resolve_answers(interview_data, answers, package_root=package_root))
    if answers:
        merged.update(answers)
    active = active_questions(interview_data, merged, package_root=package_root)
    active_ids = [question["id"] for question in active]
    pending_ids = [question["id"] for question in active if question["id"] not in explicit]
    pending_questions = [
        _question_payload(question)
        for question in active
        if question["id"] in pending_ids
    ]
    selected_packs = (
        packs.resolve_selected_packs(package_root, merged, None) if package_root else []
    )
    pending_packs = (
        pack_interview.pending_pack_ids(package_root, selected_packs, explicit_keys=explicit)
        if package_root
        else []
    )
    return {
        "schemaVersion": interview_data.get("schemaVersion"),
        "active": active_ids,
        "pending": pending_ids,
        "pendingPacks": pending_packs,
        "selectedPacks": selected_packs,
        "complete": len(pending_ids) == 0
        and answers_complete(interview_data, merged, package_root=package_root),
        "questions": pending_questions,
        "answers": merged,
    }


def prefill_answers(
    interview_data: dict[str, Any],
    *,
    package_root: Path,
    partial: dict[str, Any] | None = None,
    defaults: dict[str, Any] | None = None,
    imported: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from scripts.lifecycle import user_defaults

    draft: dict[str, Any] = {}
    if defaults is None:
        try:
            defaults = user_defaults.load_defaults()
        except (OSError, json.JSONDecodeError, ValueError):
            defaults = None
    if defaults:
        draft.update(defaults)
    if imported:
        draft.update(imported)
    if partial:
        draft.update(partial)
    return resolve_answers(interview_data, draft, package_root=package_root)


def run_terminal_interview(
    interview_data: dict[str, Any],
    *,
    package_root: Path,
    initial: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prompt on stdin; return answer map keyed by question id."""
    explicit: set[str] = set(initial.keys()) if initial else set()
    resolved: dict[str, Any] = dict(
        prefill_answers(interview_data, package_root=package_root, partial=initial)
    )
    print("cursorAssistant setup interview\n", file=sys.stderr)

    while True:
        pending = [
            question
            for question in active_questions(
                interview_data, resolved, package_root=package_root
            )
            if question["id"] not in explicit
        ]
        if not pending:
            break
        question = pending[0]
        question_id = question["id"]
        prompt = question.get("prompt", question_id)
        qtype = question.get("type", "choice")
        options = question.get("options", [])
        current = resolved.get(question_id)

        if qtype == "string":
            default = str(question.get("default", "")) if current is None else str(current)
            raw = input(f"{prompt} [{default}]: ").strip()
            resolved[question_id] = raw or default
            explicit.add(question_id)
            continue

        if qtype == "boolean":
            default = bool(question.get("default", False)) if current is None else bool(current)
            while True:
                hint = "Y/n" if default else "y/N"
                raw = input(f"{prompt} [{hint}]: ").strip().lower()
                if not raw:
                    resolved[question_id] = default
                    break
                if raw in {"y", "yes", "true", "1"}:
                    resolved[question_id] = True
                    break
                if raw in {"n", "no", "false", "0"}:
                    resolved[question_id] = False
                    break
                print("  Enter y or n.", file=sys.stderr)
            explicit.add(question_id)
            continue

        if qtype == "multi-choice":
            default_list = list(current) if isinstance(current, list) else list(question.get("default", []))
            print(f"{prompt}", file=sys.stderr)
            for index, option in enumerate(options):
                mark = "x" if option in default_list else " "
                print(f"  [{index + 1}] ({mark}) {option}", file=sys.stderr)
            print("  Comma-separated numbers, or Enter for none.", file=sys.stderr)
            raw = input("  Selection: ").strip()
            if not raw:
                resolved[question_id] = default_list
            else:
                picked: list[str] = []
                for part in raw.split(","):
                    part = part.strip()
                    if not part:
                        continue
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < len(options):
                            picked.append(options[idx])
                    elif part in options:
                        picked.append(part)
                resolved[question_id] = picked
            explicit.add(question_id)
            continue

        if qtype == "choice" and options:
            default = str(question.get("default", options[0]))
            if current is not None:
                default = str(current)
            print(f"{prompt}", file=sys.stderr)
            for index, option in enumerate(options):
                mark = "*" if option == default else " "
                print(f"  [{index + 1}] {mark} {option}", file=sys.stderr)
            while True:
                raw = input(f"  Choice [default {default}]: ").strip()
                if not raw:
                    resolved[question_id] = default
                    break
                if raw.isdigit():
                    idx = int(raw) - 1
                    if 0 <= idx < len(options):
                        resolved[question_id] = options[idx]
                        break
                if raw in options:
                    resolved[question_id] = raw
                    break
                print("  Invalid choice.", file=sys.stderr)
            explicit.add(question_id)
            continue

        if "default" in question and question_id not in resolved:
            resolved[question_id] = question["default"]
        explicit.add(question_id)

    return resolve_answers(interview_data, resolved, package_root=package_root)


def answers_complete(
    interview: dict[str, Any],
    answers: dict[str, Any],
    *,
    package_root: Path | None = None,
) -> bool:
    merged = dict(resolve_answers(interview, answers, package_root=package_root))
    merged.update(answers)
    for question in active_questions(interview, merged, package_root=package_root):
        if question["id"] not in merged:
            return False
    return True
