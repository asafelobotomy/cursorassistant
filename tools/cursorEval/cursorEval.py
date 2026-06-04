#!/usr/bin/env python3
"""cursorEval — skill/agent checks and eval suite runner for cursorAssistant.

Static (no API key):
  list [root]              Discover eval suites
  validate [eval.yaml]     Validate eval.yaml and tasks (all if omitted)
  check <path>             Spec checks on SKILL.md or agent .md
  tokens <path>            Token estimate for a surface file
  coverage [root]          Skill/agent eval coverage report (--strict to fail on gaps)
  suggest <path>           Scaffold eval suite (--apply to write)
  policy [root]            Forbid VS Code tool names in skills
  report [paths...]        HTML report from check results (-o file.html)

Dynamic (GITHUB_MODELS_TOKEN or GITHUB_TOKEN):
  run <eval.yaml>          Execute tasks via GitHub Models (--tags, --trials)
  grade <eval.yaml>        Grade a response (--text or --response-file)
  quality <path>           LLM quality scores for skill or agent file
  dev <path>               LLM improvement suggestions
  results list|view|compare  Inspect saved runs under .cursorEval/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cursorEval._common import discover_eval_files, read_text  # noqa: E402
from tools.cursorEval._results import (  # noqa: E402
    cmd_results_compare,
    cmd_results_list,
    cmd_results_view,
)
from tools.cursorEval._feedback import cmd_dev, cmd_quality  # noqa: E402
from tools.cursorEval._report import cmd_report  # noqa: E402
from tools.cursorEval._model import DEFAULT_MODEL  # noqa: E402
from tools.cursorEval._run import RESULTS_DIR, cmd_grade, cmd_run  # noqa: E402
from tools.cursorEval._static import (  # noqa: E402
    cmd_check,
    cmd_coverage,
    cmd_suggest,
    cmd_tokens,
)
from tools.cursorEval._policy import cmd_policy  # noqa: E402
from tools.cursorEval._validate import cmd_validate  # noqa: E402


def cmd_list(repo_root: Path, fmt: str) -> int:
    suites = []
    for eval_path in discover_eval_files(repo_root):
        task_count = len(list(eval_path.parent.glob("tasks/*.yaml")))
        suites.append(
            {
                "id": eval_path.parent.name,
                "path": str(eval_path.relative_to(repo_root)),
                "tasks": task_count,
            }
        )
    if fmt == "json":
        print(json.dumps({"suites": suites, "count": len(suites)}, indent=2))
    else:
        for suite in suites:
            print(f"{suite['id']}: {suite['tasks']} tasks")
    return 0


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for _ in range(12):
        if (current / "cursorAssistant.py").is_file() and (current / "VERSION").is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(prog="cursorEval")
    parser.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    parser.add_argument("--repo-root", default=".", help="cursorAssistant repository root")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List eval suites")
    p_val = sub.add_parser("validate", help="Validate eval suite(s)")
    p_val.add_argument("target", nargs="?", help="eval.yaml or suite directory")
    p_chk = sub.add_parser("check", help="Spec-check a skill or agent file")
    p_chk.add_argument("path")
    p_tok = sub.add_parser("tokens", help="Token metrics for a surface file")
    p_tok.add_argument("path")
    p_cov = sub.add_parser("coverage", help="Eval coverage for skills and agents")
    p_cov.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when any surface lacks eval, tasks, 2+ grader types, or negative-trigger-1",
    )
    p_sug = sub.add_parser("suggest", help="Scaffold eval.yaml and task files")
    p_sug.add_argument("path", help="SKILL.md or agents/*.md")
    p_sug.add_argument(
        "--apply",
        action="store_true",
        help="Write files (default: dry-run)",
    )
    sub.add_parser("policy", help="Scan skills for forbidden VS Code tool names")
    p_rep = sub.add_parser("report", help="HTML report from check() results")
    p_rep.add_argument("paths", nargs="+", help="SKILL.md or agents/*.md files")
    p_rep.add_argument("-o", "--output", help="Output HTML path")
    p_qual = sub.add_parser("quality", help="LLM quality score for a surface file")
    p_qual.add_argument("path")
    p_qual.add_argument("--model", default=DEFAULT_MODEL)
    p_qual.add_argument(
        "--fail-under",
        type=float,
        default=None,
        metavar="SCORE",
        help="Exit 1 if overall score is below SCORE (e.g. 0.75)",
    )
    p_dev = sub.add_parser("dev", help="LLM improvement suggestions for a surface file")
    p_dev.add_argument("path")
    p_dev.add_argument("--model", default=DEFAULT_MODEL)
    p_run = sub.add_parser("run", help="Run eval via GitHub Models")
    p_run.add_argument("eval_path")
    p_run.add_argument("--model", default=DEFAULT_MODEL)
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument(
        "--tags",
        action="append",
        default=None,
        metavar="TAG",
        help="Run only tasks whose tags include TAG (repeatable)",
    )
    p_run.add_argument(
        "--trials",
        type=int,
        default=None,
        metavar="N",
        help="Override trials_per_task from eval.yaml config",
    )
    p_res = sub.add_parser("results", help="List, view, or compare saved run JSON")
    res_sub = p_res.add_subparsers(dest="results_cmd", required=True)
    p_res_list = res_sub.add_parser("list", help="List result files")
    p_res_list.add_argument(
        "--dir",
        default=RESULTS_DIR,
        help=f"Results directory (default: {RESULTS_DIR})",
    )
    p_res_view = res_sub.add_parser("view", help="View one result file")
    p_res_view.add_argument("path")
    p_res_cmp = res_sub.add_parser("compare", help="Compare two or more result files")
    p_res_cmp.add_argument("paths", nargs="+")
    p_grade = sub.add_parser("grade", help="Grade a response against eval graders")
    p_grade.add_argument("eval_path")
    p_grade.add_argument("--text", help="Response text to grade")
    p_grade.add_argument("--response-file", help="File containing response text")
    p_grade.add_argument("--model", default=DEFAULT_MODEL)

    args = parser.parse_args()
    repo_root = find_repo_root(Path(args.repo_root))

    if args.command == "list":
        return cmd_list(repo_root, args.fmt)
    if args.command == "validate":
        return cmd_validate(repo_root, args.target, args.fmt)
    if args.command == "check":
        return cmd_check(args.path, args.fmt)
    if args.command == "tokens":
        return cmd_tokens(args.path, args.fmt)
    if args.command == "coverage":
        return cmd_coverage(repo_root, args.fmt, getattr(args, "strict", False))
    if args.command == "suggest":
        return cmd_suggest(args.path, getattr(args, "apply", False), args.fmt)
    if args.command == "policy":
        return cmd_policy(repo_root, args.fmt)
    if args.command == "report":
        return cmd_report(args.paths, getattr(args, "output", None), args.fmt)
    if args.command == "quality":
        return cmd_quality(
            args.path, args.model, args.fmt, getattr(args, "fail_under", None)
        )
    if args.command == "dev":
        return cmd_dev(args.path, args.model, args.fmt)
    if args.command == "run":
        return cmd_run(
            args.eval_path,
            args.model,
            args.fmt,
            args.dry_run,
            args.tags,
            args.trials,
        )
    if args.command == "results":
        if args.results_cmd == "list":
            results_path = Path(getattr(args, "dir", RESULTS_DIR))
            if not results_path.is_absolute():
                results_path = repo_root / results_path
            return cmd_results_list(results_path, args.fmt)
        if args.results_cmd == "view":
            return cmd_results_view(Path(args.path), args.fmt)
        if args.results_cmd == "compare":
            return cmd_results_compare(args.paths, args.fmt)
    if args.command == "grade":
        if args.response_file:
            response = read_text(args.response_file)
        elif args.text:
            response = args.text
        else:
            parser.error("grade requires --text or --response-file")
        return cmd_grade(args.eval_path, response, args.fmt, args.model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
