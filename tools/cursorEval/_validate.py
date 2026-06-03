"""Validate eval suite structure."""

from __future__ import annotations

import json
from pathlib import Path

from tools.cursorEval._common import discover_eval_files, load_tasks, load_yaml


def validate_eval(eval_path: Path) -> dict:
    issues: list[str] = []
    spec = load_yaml(eval_path)
    eval_dir = eval_path.parent
    if "name" not in spec:
        issues.append("missing required field: name")
    if "graders" not in spec or not isinstance(spec.get("graders"), list):
        issues.append("missing or invalid graders list")
    task_refs = spec.get("tasks", [])
    if not task_refs:
        issues.append("missing tasks references")
    try:
        tasks = load_tasks(eval_dir, task_refs)
    except (ValueError, SystemExit) as exc:
        issues.append(f"cannot load tasks: {exc}")
        tasks = []
    for task in tasks:
        task_id = task.get("id")
        if not task_id:
            issues.append("task missing id")
        if not task.get("prompt"):
            issues.append(f"task {task_id or '?'} missing prompt")
    return {
        "path": str(eval_path),
        "taskCount": len(tasks),
        "ok": not issues,
        "issues": issues,
    }


def cmd_validate(repo_root: Path, target: str | None, fmt: str) -> int:
    if target:
        path = Path(target)
        if path.is_dir():
            path = path / "eval.yaml"
        results = [validate_eval(path)]
    else:
        results = [validate_eval(p) for p in discover_eval_files(repo_root)]
    failed = [r for r in results if not r["ok"]]
    if fmt == "json":
        print(json.dumps({"results": results, "failed": len(failed)}, indent=2))
    else:
        for row in results:
            mark = "ok" if row["ok"] else "FAIL"
            print(f"[{mark}] {row['path']} ({row['taskCount']} tasks)")
            for issue in row["issues"]:
                print(f"       - {issue}")
    return 1 if failed else 0
