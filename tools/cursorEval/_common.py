"""Shared helpers and graders for cursorEval."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOKEN_BUDGET = 16_000
_CHARS_PER_TOKEN = 4

try:
    import yaml as _yaml
except ImportError:
    _yaml = None  # type: ignore[assignment]

try:
    import tiktoken as _tiktoken
except ImportError:
    _tiktoken = None  # type: ignore[assignment]

_TK_ENC = None


def _encoding():
    global _TK_ENC
    if _TK_ENC is not None:
        return _TK_ENC
    if _tiktoken is None:
        return None
    try:
        _TK_ENC = _tiktoken.get_encoding("cl100k_base")
    except Exception:
        _TK_ENC = None
    return _TK_ENC


def read_text(path: str | Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cursorEval: cannot read {path}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def parse_frontmatter(content: str) -> dict[str, str]:
    content = content.lstrip("\ufeff").replace("\r\n", "\n")
    parts = content.split("---\n", 2)
    if len(parts) < 3:
        return {}
    result: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, _, rest = line.partition(":")
            result[key.strip()] = rest.strip().strip("\"'")
    return result


def count_tokens(content: str) -> int:
    enc = _encoding()
    if enc is not None:
        return len(enc.encode(content))
    return len(content) // _CHARS_PER_TOKEN


def load_yaml(path: Path) -> dict:
    if _yaml is None:
        print("cursorEval: PyYAML required — pip install pyyaml", file=sys.stderr)
        raise SystemExit(2)
    data = _yaml.safe_load(read_text(path))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping root")
    return data


def load_tasks(eval_dir: Path, task_refs: list) -> list[dict]:
    tasks: list[dict] = []
    for ref in task_refs:
        if isinstance(ref, str):
            for fp in sorted(eval_dir.glob(ref)):
                parsed = load_yaml(fp)
                tasks.append(parsed)
        elif isinstance(ref, dict):
            tasks.append(ref)
    return tasks


def discover_eval_files(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for pattern in ("evals/*/eval.yaml", "packs/*/evals/*/eval.yaml"):
        paths.extend(sorted(repo_root.glob(pattern)))
    return paths


def grade_text(response: str, config: dict) -> tuple[bool, float]:
    checks: list[bool] = []
    for item in config.get("contains", []):
        checks.append(str(item).lower() in response.lower())
    for item in config.get("not_contains", []):
        checks.append(str(item).lower() not in response.lower())
    pattern = config.get("pattern")
    if pattern:
        checks.append(bool(re.search(pattern, response, re.IGNORECASE)))
    for pat in config.get("regex_match", []):
        checks.append(bool(re.search(str(pat), response)))
    for pat in config.get("regex_not_match", []):
        checks.append(not bool(re.search(str(pat), response)))
    expected = config.get("expected")
    if expected:
        for item in expected:
            checks.append(str(item).lower() in response.lower())
    if not checks:
        return True, 1.0
    passed = all(checks)
    score = round(sum(1 for c in checks if c) / len(checks), 3)
    return passed, score


def grade_behavior(response: str, config: dict) -> tuple[bool, float]:
    checks: list[bool] = []
    max_tokens = config.get("max_tokens")
    if max_tokens is not None:
        checks.append(count_tokens(response) <= int(max_tokens))
    min_tokens = config.get("min_tokens")
    if min_tokens is not None:
        checks.append(count_tokens(response) >= int(min_tokens))
    if not checks:
        return True, 1.0
    passed = all(checks)
    score = round(sum(1 for c in checks if c) / len(checks), 3)
    return passed, score


def run_graders(response: str, graders: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for grader in graders:
        gtype = grader.get("type", "text")
        name = grader.get("name", gtype)
        config = grader.get("config", {})
        if gtype == "text":
            passed, score = grade_text(response, config)
        elif gtype == "behavior":
            passed, score = grade_behavior(response, config)
        else:
            rows.append(
                {
                    "name": name,
                    "type": gtype,
                    "passed": None,
                    "score": None,
                    "skipped": True,
                    "reason": f"grader type {gtype!r} requires runtime or API",
                }
            )
            continue
        rows.append({"name": name, "type": gtype, "passed": passed, "score": score})
    return rows
