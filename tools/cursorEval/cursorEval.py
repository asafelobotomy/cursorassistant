#!/usr/bin/env python3
"""cursorEval — skill/agent checks and eval suite runner for cursorAssistant.

Static (no API key):
  list [root]              Discover eval suites
  validate [eval.yaml]     Validate eval.yaml and tasks (all if omitted)
  check <path>             Spec checks on SKILL.md or agent .md
  tokens <path>            Token estimate for a surface file
  coverage [root]          Skill/agent eval coverage report
  policy [root]            Forbid VS Code tool names in skills

Dynamic (GITHUB_MODELS_TOKEN or GITHUB_TOKEN for run):
  run <eval.yaml>          Execute tasks via GitHub Models
  grade <eval.yaml>        Grade a response (--text or --response-file)
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
from tools.cursorEval._run import cmd_grade, cmd_run  # noqa: E402
from tools.cursorEval._static import cmd_check, cmd_coverage, cmd_tokens  # noqa: E402
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
    sub.add_parser("coverage", help="Eval coverage for skills and agents")
    sub.add_parser("policy", help="Scan skills for forbidden VS Code tool names")
    p_run = sub.add_parser("run", help="Run eval via GitHub Models")
    p_run.add_argument("eval_path")
    p_run.add_argument("--model", default="gpt-4o-mini")
    p_run.add_argument("--dry-run", action="store_true")
    p_grade = sub.add_parser("grade", help="Grade a response against eval graders")
    p_grade.add_argument("eval_path")
    p_grade.add_argument("--text", help="Response text to grade")
    p_grade.add_argument("--response-file", help="File containing response text")

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
        return cmd_coverage(repo_root, args.fmt)
    if args.command == "policy":
        return cmd_policy(repo_root, args.fmt)
    if args.command == "run":
        return cmd_run(args.eval_path, args.model, args.fmt, args.dry_run)
    if args.command == "grade":
        if args.response_file:
            response = read_text(args.response_file)
        elif args.text:
            response = args.text
        else:
            parser.error("grade requires --text or --response-file")
        return cmd_grade(args.eval_path, response, args.fmt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
