"""Saved eval result listing, view, and compare."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _as_float(value: object) -> float | None:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _normalize_summary(data: dict) -> dict:
    summary = data.get("summary")
    if isinstance(summary, dict) and summary:
        return summary
    results = data.get("results") or data.get("tasks") or []
    total = len(results)
    passed = sum(1 for r in results if r.get("passed"))
    scores: list[float] = []
    for row in results:
        gr = row.get("graders") or []
        gr_scores = [float(g["score"]) for g in gr if g.get("score") is not None]
        if gr_scores:
            scores.append(sum(gr_scores) / len(gr_scores))
        elif row.get("passed"):
            scores.append(1.0)
        else:
            scores.append(0.0)
    return {
        "total": total,
        "passed": passed,
        "pass_rate": round(passed / total, 3) if total else 0.0,
        "score": round(sum(scores) / len(scores), 3) if scores else 0.0,
    }


def _task_score(task: dict) -> float:
    graders = task.get("graders") or []
    scores = [float(g["score"]) for g in graders if g.get("score") is not None]
    if scores:
        return round(sum(scores) / len(scores), 3)
    return 1.0 if task.get("passed") else 0.0


def cmd_results_list(results_dir: Path, fmt: str) -> int:
    if not results_dir.is_dir():
        print(f"cursorEval results: directory not found: {results_dir}", file=sys.stderr)
        return 1
    files = sorted(results_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        print(f"cursorEval results: no result files in {results_dir}", file=sys.stderr)
        return 1

    records: list[dict] = []
    for fp in files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        summary = _normalize_summary(data)
        records.append(
            {
                "file": fp.name,
                "suite": data.get("suite") or data.get("skill", "?"),
                "model": data.get("model", "?"),
                "timestamp": data.get("timestamp", "?"),
                "pass_rate": summary.get("pass_rate"),
                "score": summary.get("score"),
            }
        )
    if not records:
        print(f"cursorEval results: no valid JSON in {results_dir}", file=sys.stderr)
        return 1

    if fmt == "json":
        print(json.dumps(records, indent=2))
    else:
        print(f"cursorEval results — {results_dir}")
        for row in records:
            pr = _as_float(row["pass_rate"])
            sc = _as_float(row["score"])
            pr_s = f"{pr:.0%}" if pr is not None else "?"
            sc_s = f"{sc:.3f}" if sc is not None else "?"
            print(f"  {row['file']:<55}  {pr_s}  score {sc_s}")
    return 0


def cmd_results_view(results_path: Path, fmt: str) -> int:
    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cursorEval results view: {exc}", file=sys.stderr)
        return 2

    summary = _normalize_summary(data)
    tasks = data.get("tasks") or data.get("results") or []

    if fmt == "json":
        print(json.dumps(data, indent=2))
        return 0

    print(f"cursorEval results view — {results_path.name}")
    print(f"  suite:     {data.get('suite', data.get('skill', '?'))}")
    print(f"  model:     {data.get('model', '?')}")
    print(f"  timestamp: {data.get('timestamp', '?')}")
    pr = _as_float(summary.get("pass_rate"))
    print(f"  pass_rate: {pr:.0%}" if pr is not None else "  pass_rate: ?")
    print(f"  score:     {summary.get('score', '?')}")
    print()
    for task in tasks:
        icon = "pass" if task.get("passed") else "fail"
        print(f"  [{icon}] {task.get('id', '?'):<40}  score {_task_score(task):.3f}")
    return 0


def cmd_results_compare(files: list[str], fmt: str) -> int:
    if len(files) < 2:
        print("cursorEval results compare: provide at least 2 result files", file=sys.stderr)
        return 2

    loaded: list[tuple[str, dict]] = []
    for path in files:
        try:
            loaded.append((path, json.loads(Path(path).read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"cursorEval results compare: cannot load {path}: {exc}", file=sys.stderr)
            return 2

    base_name, base_data = loaded[0]
    base_tasks = {
        t["id"]: {**t, "score": _task_score(t)}
        for t in (base_data.get("tasks") or base_data.get("results") or [])
        if t.get("id")
    }
    deltas: list[dict] = []

    for fname, data in loaded[1:]:
        other_tasks = {
            t["id"]: {**t, "score": _task_score(t)}
            for t in (data.get("tasks") or data.get("results") or [])
            if t.get("id")
        }
        for tid in sorted(set(base_tasks) | set(other_tasks)):
            if tid in base_tasks and tid in other_tasks:
                bs = base_tasks[tid]["score"]
                cs = other_tasks[tid]["score"]
                deltas.append(
                    {
                        "task": tid,
                        "baseline_score": bs,
                        "compare_score": cs,
                        "delta": round(cs - bs, 3),
                        "compare_file": fname,
                    }
                )

    payload = {
        "baseline": base_name,
        "baseline_summary": _normalize_summary(base_data),
        "comparisons": [
            {"file": f, "summary": _normalize_summary(d)} for f, d in loaded[1:]
        ],
        "task_deltas": deltas,
    }

    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print("cursorEval results compare")
        print(f"  baseline: {base_name}")
        bs = payload["baseline_summary"]
        print(f"    pass_rate {bs.get('pass_rate')}  score {bs.get('score')}")
        for comp in payload["comparisons"]:
            print(f"  compare:  {comp['file']}")
            print(f"    pass_rate {comp['summary'].get('pass_rate')}  score {comp['summary'].get('score')}")
        if deltas:
            print("\n  task deltas:")
            for d in deltas:
                arrow = "↑" if d["delta"] > 0 else ("↓" if d["delta"] < 0 else "=")
                print(
                    f"    {d['task']:<40}  {d['baseline_score']:.3f} {arrow} "
                    f"{d['compare_score']:.3f}  (Δ{d['delta']:+.3f})"
                )
    return 0
