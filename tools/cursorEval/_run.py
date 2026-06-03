"""Run and grade eval suites."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from tools.cursorEval._common import (
    load_tasks,
    load_yaml,
    read_text,
    run_graders,
)


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for _ in range(12):
        if (current / "cursorAssistant.py").is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start.resolve()

_GITHUB_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"
_DEFAULT_MODEL = "gpt-4o-mini"
_RESULTS_DIR = ".cursorEval"


def _get_token() -> str | None:
    return (
        os.environ.get("GITHUB_MODELS_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
    )


def _call_model(messages: list[dict], model: str, token: str) -> str:
    payload = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        _GITHUB_MODELS_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def _resolve_surface(repo_root: Path, eval_dir: Path) -> str:
    name = eval_dir.name
    candidates = [
        repo_root / "skills" / name / "SKILL.md",
        repo_root / "agents" / f"{name}.md",
    ]
    candidates.extend(sorted(repo_root.glob(f"packs/*/skills/{name}/SKILL.md")))
    for path in candidates:
        if path.is_file():
            return read_text(path)
    return ""


def cmd_grade(eval_path: str, response: str, fmt: str) -> int:
    spec = load_yaml(Path(eval_path))
    graders = spec.get("graders", [])
    rows = run_graders(response, graders)
    passed = all(r.get("passed") for r in rows if r.get("passed") is not None)
    payload = {"ok": passed, "graders": rows}
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        for row in rows:
            if row.get("skipped"):
                print(f"  [skip] {row['name']}: {row.get('reason')}")
            else:
                mark = "pass" if row["passed"] else "fail"
                print(f"  [{mark}] {row['name']} (score {row['score']})")
    return 0 if passed else 1


def cmd_run(eval_path: str, model: str, fmt: str, dry_run: bool) -> int:
    eval_file = Path(eval_path).resolve()
    eval_dir = eval_file.parent
    repo_root = find_repo_root(eval_dir)

    spec = load_yaml(eval_file)
    tasks = load_tasks(eval_dir, spec.get("tasks", []))
    graders = spec.get("graders", [])

    if dry_run:
        payload = {
            "eval": str(eval_file),
            "tasks": len(tasks),
            "graders": [g.get("name") for g in graders],
            "dryRun": True,
        }
        print(json.dumps(payload, indent=2) if fmt == "json" else f"dry-run: {len(tasks)} tasks, {len(graders)} graders")
        return 0

    token = _get_token()
    if not token:
        print(
            "cursorEval run: set GITHUB_MODELS_TOKEN, GITHUB_TOKEN, or GH_TOKEN",
            file=sys.stderr,
        )
        return 2

    surface = _resolve_surface(repo_root, eval_dir)
    results: list[dict] = []
    for task in tasks:
        messages: list[dict] = []
        if surface:
            messages.append({"role": "system", "content": surface[:6000]})
        messages.append({"role": "user", "content": str(task.get("prompt", ""))})
        try:
            response = _call_model(messages, model, token)
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
            results.append({"id": task.get("id"), "error": str(exc), "passed": False})
            continue
        grader_rows = run_graders(response, graders)
        task_passed = all(r.get("passed") for r in grader_rows if r.get("passed") is not None)
        results.append(
            {
                "id": task.get("id"),
                "passed": task_passed,
                "graders": grader_rows,
                "responsePreview": response[:500],
            }
        )

    all_passed = all(r.get("passed") for r in results if "passed" in r)
    out_dir = repo_root / _RESULTS_DIR
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = out_dir / f"{eval_dir.name}-{stamp}.json"
    payload = {"eval": str(eval_file), "model": model, "results": results, "passed": all_passed}
    out_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"run: {sum(1 for r in results if r.get('passed'))}/{len(results)} passed → {out_file}")
    return 0 if all_passed else 1
