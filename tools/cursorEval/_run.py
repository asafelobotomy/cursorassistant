"""Run and grade eval suites."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from tools.cursorEval._common import (
    aggregate_trials,
    filter_tasks_by_tags,
    grade_response,
    load_tasks,
    load_yaml,
    merge_run_config,
    read_text,
    run_graders,
)
from tools.cursorEval._model import DEFAULT_MODEL, call_model, get_token

RESULTS_DIR = ".cursorEval"
_SURFACE_CHAR_LIMIT = 6000


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for _ in range(12):
        if (current / "cursorAssistant.py").is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start.resolve()


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


def _load_instruction_files(repo_root: Path, paths: list) -> str:
    chunks: list[str] = []
    for entry in paths:
        rel = Path(str(entry))
        full = rel if rel.is_absolute() else repo_root / rel
        if full.is_file():
            chunks.append(read_text(full)[:4000])
    return "\n\n".join(chunks)


def _build_messages(
    repo_root: Path,
    surface: str,
    run_config: dict,
    prompt: str,
) -> list[dict]:
    messages: list[dict] = []
    extra = _load_instruction_files(
        repo_root, run_config.get("instruction_files") or []
    )
    inject = run_config.get("inject_skill_body", True)
    system_parts: list[str] = []
    if extra:
        system_parts.append(extra)
    if inject and surface:
        system_parts.append(surface[:_SURFACE_CHAR_LIMIT])
    if system_parts:
        messages.append({"role": "system", "content": "\n\n".join(system_parts)})
    messages.append({"role": "user", "content": prompt})
    return messages


def _merge_graders(spec_graders: list, task: dict) -> list:
    extra = task.get("graders") or []
    if isinstance(extra, list) and extra:
        return list(spec_graders) + extra
    return list(spec_graders)


def _grade_all_trials(
    responses: list[str],
    graders: list[dict],
    task: dict,
    trial_count: int,
    model: str,
    token: str,
) -> tuple[list[dict], bool, float]:
    trial_rows: list[list[dict]] = [
        grade_response(resp, graders, task, model=model, token=token)
        for resp in responses
        if resp
    ]
    if not trial_rows:
        return [], False, 0.0
    if trial_count > 1 and len(trial_rows) > 1:
        merged = aggregate_trials(trial_rows, trial_count)
    else:
        merged = trial_rows[0]
    graded = [g for g in merged if g.get("passed") is not None]
    passed = bool(graded) and all(g["passed"] for g in graded)
    score = round(sum(g["score"] for g in graded) / len(graded), 3) if graded else 0.0
    return merged, passed, score


def _run_task_with_retries(
    messages: list[dict],
    model: str,
    token: str,
    graders: list[dict],
    task: dict,
    trials: int,
    max_attempts: int,
) -> tuple[list[dict], bool, float, str]:
    grader_rows: list[dict] = []
    passed = False
    score = 0.0
    preview = ""
    last_error: Exception | None = None

    for _attempt in range(max(1, max_attempts)):
        responses: list[str] = []
        for _ in range(max(1, trials)):
            try:
                responses.append(call_model(messages, model, token))
            except RuntimeError as exc:
                last_error = exc
                responses.append("")
        preview = responses[0][:500] if responses else ""
        if not any(responses):
            continue
        grader_rows, passed, score = _grade_all_trials(
            responses, graders, task, trials, model, token
        )
        if passed:
            return grader_rows, passed, score, preview

    if last_error and not preview:
        raise last_error
    return grader_rows, passed, score, preview


def _graders_need_token(graders: list) -> bool:
    return any(g.get("type") in ("prompt_judge", "llm") for g in graders)


def cmd_grade(
    eval_path: str,
    response: str,
    fmt: str,
    model: str = DEFAULT_MODEL,
) -> int:
    spec = load_yaml(Path(eval_path))
    graders = spec.get("graders", [])
    token = get_token()
    if _graders_need_token(graders) and not token:
        print(
            "cursorEval grade: set GITHUB_MODELS_TOKEN, GITHUB_TOKEN, or GH_TOKEN "
            "for prompt_judge/llm graders",
            file=sys.stderr,
        )
        return 2
    rows = run_graders(response, graders, model=model, token=token)
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


def cmd_run(
    eval_path: str,
    model: str,
    fmt: str,
    dry_run: bool,
    tags: list[str] | None,
    trials: int | None,
) -> int:
    eval_file = Path(eval_path).resolve()
    eval_dir = eval_file.parent
    repo_root = find_repo_root(eval_dir)

    spec = load_yaml(eval_file)
    eval_config = dict(spec.get("config") or {})
    graders = spec.get("graders", [])
    all_tasks = load_tasks(eval_dir, spec.get("tasks", []))
    tasks = filter_tasks_by_tags(all_tasks, tags)

    trials_per_task = trials if trials is not None else int(
        eval_config.get("trials_per_task", 1)
    )

    if dry_run:
        payload = {
            "eval": str(eval_file),
            "tasksTotal": len(all_tasks),
            "tasksSelected": len(tasks),
            "tags": tags or [],
            "trialsPerTask": trials_per_task,
            "config": eval_config,
            "graders": [g.get("name") for g in graders],
            "dryRun": True,
        }
        if fmt == "json":
            print(json.dumps(payload, indent=2))
        else:
            print(
                f"dry-run: {len(tasks)}/{len(all_tasks)} tasks, "
                f"{len(graders)} graders, trials={trials_per_task}"
                + (f", tags={tags}" if tags else "")
            )
        return 0 if tasks else 1

    if not tasks:
        print(
            "cursorEval run: no tasks matched"
            + (f" (tags={tags!r})" if tags else ""),
            file=sys.stderr,
        )
        return 2

    token = get_token()
    if not token:
        print(
            "cursorEval run: set GITHUB_MODELS_TOKEN, GITHUB_TOKEN, or GH_TOKEN",
            file=sys.stderr,
        )
        return 2

    surface = _resolve_surface(repo_root, eval_dir)
    suite_name = eval_dir.name
    task_results: list[dict] = []

    for task in tasks:
        task_id = task.get("id", "?")
        run_config = merge_run_config(spec, task)
        prompt = str(task.get("prompt", ""))
        task_trials = int(run_config.get("trials_per_task", trials_per_task))
        max_attempts = int(run_config.get("max_attempts", 1))
        messages = _build_messages(repo_root, surface, run_config, prompt)
        task_graders = _merge_graders(graders, task)

        try:
            grader_rows, passed, score, preview = _run_task_with_retries(
                messages,
                model,
                token,
                task_graders,
                task,
                task_trials,
                max_attempts,
            )
        except RuntimeError as exc:
            task_results.append(
                {"id": task_id, "error": str(exc), "passed": False, "score": 0.0}
            )
            continue

        task_results.append(
            {
                "id": task_id,
                "passed": passed,
                "score": score,
                "trials": task_trials,
                "graders": grader_rows,
                "responsePreview": preview,
                "tags": task.get("tags", []),
            }
        )

    total = len(task_results)
    passed_count = sum(1 for t in task_results if t.get("passed"))
    pass_rate = round(passed_count / total, 3) if total else 0.0
    avg_score = (
        round(sum(t.get("score", 0.0) for t in task_results) / total, 3) if total else 0.0
    )
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()
    summary = {
        "total": total,
        "passed": passed_count,
        "pass_rate": pass_rate,
        "score": avg_score,
        "trials_per_task": trials_per_task,
    }
    payload = {
        "eval": str(eval_file),
        "suite": suite_name,
        "model": model,
        "timestamp": timestamp,
        "tags": tags or [],
        "config": eval_config,
        "summary": summary,
        "tasks": task_results,
        "passed": passed_count == total and total > 0,
    }

    out_dir = repo_root / RESULTS_DIR
    out_dir.mkdir(exist_ok=True)
    safe_model = re.sub(r"[^a-zA-Z0-9._-]", "-", model)
    out_file = out_dir / f"{suite_name}-{now.strftime('%Y%m%dT%H%M%SZ')}-{safe_model}.json"
    out_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"run: {passed_count}/{total} passed "
            f"(pass_rate {pass_rate:.0%}, score {avg_score:.3f}) → {out_file}"
        )
    return 0 if payload["passed"] else 1

