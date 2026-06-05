"""Interview and plan helpers for cursorAssistant setup."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from scripts.lifecycle import agent_customization, packs

DEFAULT_ANSWERS_REL = ".cursor/cursor-assistant-answers.json"
LOCKFILE_TOP_KEYS = frozenset({"profile.selected", "packs.selected", "mcp.enabled"})

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


def question_active(
    question: dict[str, Any],
    answers: dict[str, Any],
    allowed_batches: set[str],
) -> bool:
    batch = question.get("batch", "simple")
    if batch not in allowed_batches:
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
    static = [
        question
        for question in interview.get("questions", [])
        if question_active(question, merged, allowed)
    ]
    if package_root is None:
        return static
    agent_filtered = [
        question
        for question in agent_customization.agent_questions(package_root)
        if question.get("batch", "agent") in allowed
    ]
    return static + agent_filtered


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
        for question in agent_customization.agent_questions(package_root):
            question_id = question["id"]
            if answers and question_id in answers:
                resolved[question_id] = answers[question_id]
            elif "default" in question and question_id not in resolved:
                resolved[question_id] = question["default"]

    return resolved


def answers_to_lockfile_fields(
    answers: dict[str, Any],
    selected_packs: list[str],
) -> dict[str, Any]:
    profile = answers.get("profile.selected", "balanced")
    setup_answers = {
        key: value
        for key, value in answers.items()
        if key not in LOCKFILE_TOP_KEYS
    }
    return {
        "profile": profile,
        "selectedPacks": selected_packs,
        "mcpEnabled": bool(answers.get("mcp.enabled", False)),
        "setupAnswers": setup_answers,
    }


def default_answers_path(workspace: Path) -> Path:
    return workspace / DEFAULT_ANSWERS_REL


def write_answers_file(path: Path, answers: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(answers, indent=2) + "\n", encoding="utf-8")


def run_terminal_interview(
    interview: dict[str, Any],
    *,
    package_root: Path,
    initial: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prompt on stdin; return answer map keyed by question id."""
    resolved: dict[str, Any] = dict(initial or {})
    print("cursorAssistant setup interview\n", file=sys.stderr)

    while True:
        pending = [
            question
            for question in active_questions(interview, resolved, package_root=package_root)
            if question["id"] not in resolved
        ]
        if not pending:
            break
        question = pending[0]
        question_id = question["id"]
        prompt = question.get("prompt", question_id)
        qtype = question.get("type", "choice")
        options = question.get("options", [])
        current = resolved.get(question_id)

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
            continue

        if "default" in question and question_id not in resolved:
            resolved[question_id] = question["default"]

    return resolve_answers(interview, resolved, package_root=package_root)


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
