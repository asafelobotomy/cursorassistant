"""Import setup answers from a remote GitHub repository."""

from __future__ import annotations

import json
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from scripts.lifecycle import interview

ANSWERS_REL = ".cursor/cursor-assistant-answers.json"
LOCKFILE_REL = ".cursor/cursorAssistant-lock.json"
RAW_ANSWERS_URL = (
    "https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{answers_rel}"
)

REF_PATH_RE = re.compile(r"/(tree|blob)/", re.IGNORECASE)
GITHUB_HTTPS_RE = re.compile(
    r"^https?://(?:www\.)?github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)
GITHUB_SSH_RE = re.compile(
    r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
    re.IGNORECASE,
)
SHORT_REPO_RE = re.compile(r"^(?P<owner>[^/]+)/(?P<repo>[^/]+)$")

SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|secret|password|passwd|credential|private[_-]?key|auth[_-]?token|"
    r"access[_-]?token|pat|bearer)",
    re.IGNORECASE,
)
SECRET_VALUE_RE = re.compile(
    r"(sk-[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|"
    r"AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{10,})"
)


class AnswersImportError(ValueError):
    """Raised when copy-from import cannot proceed."""


def parse_github_repo(url: str) -> tuple[str, str]:
    text = url.strip()
    if REF_PATH_RE.search(text):
        raise AnswersImportError(
            "copy-from supports default branch only in v0.16 — omit /tree/ or /blob/ paths"
        )
    for pattern in (GITHUB_HTTPS_RE, GITHUB_SSH_RE, SHORT_REPO_RE):
        match = pattern.match(text)
        if match:
            return match.group("owner"), match.group("repo")
    raise AnswersImportError(
        "copy-from repo must be owner/repo or a GitHub URL without branch/path suffix"
    )


def _http_get_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _http_get_text(url: str) -> str:
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def _gh_available() -> bool:
    try:
        completed = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        return completed.returncode == 0
    except OSError:
        return False


def _fetch_public_answers(owner: str, repo: str) -> dict[str, Any] | None:
    url = RAW_ANSWERS_URL.format(
        owner=owner, repo=repo, answers_rel=ANSWERS_REL.lstrip("/")
    )
    try:
        payload = json.loads(_http_get_text(url))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _fetch_private_answers(owner: str, repo: str) -> dict[str, Any] | None:
    if not _gh_available():
        return None
    api_path = f"repos/{owner}/{repo}/contents/{ANSWERS_REL.lstrip('/')}"
    try:
        completed = subprocess.run(
            ["gh", "api", api_path, "--jq", ".content"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    import base64

    raw = base64.b64decode(completed.stdout.strip()).decode("utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        return None
    return payload


def _fetch_public_lockfile(owner: str, repo: str) -> dict[str, Any] | None:
    url = RAW_ANSWERS_URL.format(
        owner=owner, repo=repo, answers_rel=LOCKFILE_REL.lstrip("/")
    )
    try:
        payload = json.loads(_http_get_text(url))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def flatten_lockfile_to_answers(lock: dict[str, Any]) -> dict[str, Any]:
    flat: dict[str, Any] = {}
    setup_answers = lock.get("setupAnswers")
    if isinstance(setup_answers, dict):
        flat.update(setup_answers)
    pack_answers = lock.get("packAnswers")
    if isinstance(pack_answers, dict):
        for pack_id, pack_map in pack_answers.items():
            if isinstance(pack_map, dict):
                for key, value in pack_map.items():
                    flat[f"{pack_id}.{key}"] = value
                    flat[key] = value
    for top_key in ("profile", "selectedPacks", "mcpEnabled"):
        if top_key == "profile" and isinstance(lock.get("profile"), str):
            flat.setdefault("profile.selected", lock["profile"])
        if top_key == "selectedPacks" and isinstance(lock.get("selectedPacks"), list):
            flat.setdefault("packs.selected", list(lock["selectedPacks"]))
        if top_key == "mcpEnabled" and "mcpEnabled" in lock:
            flat.setdefault("mcp.enabled", bool(lock["mcpEnabled"]))
    return flat


def known_question_ids(package_root: Path) -> set[str]:
    data = interview.load_interview(package_root)
    ids = {question["id"] for question in data.get("questions", [])}
    from scripts.lifecycle import agent_customization

    ids.update(question["id"] for question in agent_customization.agent_questions(package_root))
    return ids


def validate_answers_no_secrets(answers: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for key, value in answers.items():
        if SECRET_KEY_RE.search(key):
            warnings.append(f"suspicious key name: {key}")
        if isinstance(value, str) and SECRET_VALUE_RE.search(value):
            warnings.append(f"suspicious value pattern for key: {key}")
    return warnings


def sanitize_imported_answers(
    raw: dict[str, Any],
    *,
    package_root: Path,
) -> tuple[dict[str, Any], list[str], list[str]]:
    known = known_question_ids(package_root)
    merged: dict[str, Any] = {}
    dropped: list[str] = []
    warnings: list[str] = []
    for key, value in raw.items():
        if interview.is_ephemeral_key(key):
            dropped.append(key)
            continue
        if key not in known:
            dropped.append(key)
            continue
        merged[key] = value
    warnings.extend(validate_answers_no_secrets(merged))
    return merged, dropped, warnings


def fetch_remote_answers(owner: str, repo: str) -> tuple[dict[str, Any], str]:
    answers = _fetch_public_answers(owner, repo)
    if answers is not None:
        return answers, ANSWERS_REL
    answers = _fetch_private_answers(owner, repo)
    if answers is not None:
        return answers, ANSWERS_REL
    lock = _fetch_public_lockfile(owner, repo)
    if lock is not None:
        return flatten_lockfile_to_answers(lock), LOCKFILE_REL
    raise AnswersImportError(
        f"Could not fetch {ANSWERS_REL} or {LOCKFILE_REL} from {owner}/{repo} "
        "(public raw URL or gh auth for private repos)"
    )


def import_from_repo(
    repo_url: str,
    *,
    package_root: Path,
    base_answers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    owner, repo = parse_github_repo(repo_url)
    raw, source_path = fetch_remote_answers(owner, repo)
    secret_hits = validate_answers_no_secrets(raw)
    if secret_hits:
        raise AnswersImportError(
            "imported answers contain probable secrets — remove them from the source repo: "
            + "; ".join(secret_hits)
        )
    merged, dropped, warnings = sanitize_imported_answers(raw, package_root=package_root)
    post_sanitize_hits = validate_answers_no_secrets(merged)
    if post_sanitize_hits:
        raise AnswersImportError(
            "imported answers contain probable secrets — remove them from the source repo: "
            + "; ".join(post_sanitize_hits)
        )
    draft = dict(base_answers or {})
    draft.update(merged)
    return {
        "merged": draft,
        "imported": merged,
        "droppedKeys": dropped,
        "warnings": warnings,
        "source": f"github:{owner}/{repo}:{source_path}",
        "owner": owner,
        "repo": repo,
    }
