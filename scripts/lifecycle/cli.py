"""Argument parsing and JSON CLI for cursorAssistant."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.lifecycle import engine, interview, paths

SETUP_DEPRECATED_HINT = (
    "The setup command is deprecated. Run: "
    "python3 cursorAssistant.py interview --workspace . "
    "then configure --answers .cursor/cursor-assistant-answers.json"
)


def _resolve_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _load_answers(path: str | None) -> dict | None:
    if not path:
        return None
    payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("--answers file must contain a JSON object")
    return payload


def _add_workspace_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workspace",
        default=".",
        help="Consumer workspace root (default: current directory)",
    )


def _add_package_root_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--package-root",
        help="cursorAssistant package root (auto-detected when omitted)",
    )


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    _add_workspace_arg(parser)
    _add_package_root_arg(parser)
    parser.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    parser.add_argument(
        "--answers",
        help="Path to JSON file with interview answers (required for non-interactive configure)",
    )


def _resolve_roots(parser: argparse.ArgumentParser, args: argparse.Namespace) -> tuple[Path, Path]:
    workspace = _resolve_path(args.workspace)
    if not workspace.is_dir():
        parser.error(f"workspace is not a directory: {workspace}")
    try:
        package_root = find_package_root(parser, args, workspace)
    except FileNotFoundError as exc:
        parser.error(str(exc))
    return workspace, package_root


def find_package_root(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    workspace: Path,
) -> Path:
    if getattr(args, "package_root", None):
        root = _resolve_path(args.package_root)
        if not paths.is_package_root(root):
            parser.error(f"package-root is not a cursorAssistant package: {root}")
        return root
    return paths.find_package_root(workspace)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cursorAssistant",
        description="Cursor surface lifecycle (plugin-first: auto-detects package root)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("inspect", "Read-only install state"),
        ("plan-setup", "Plan setup/update without writing files"),
        ("interview", "Run setup interview; save answers JSON in the workspace"),
        ("configure", "Interview (TTY) or --answers + install into workspace"),
        ("setup", "Deprecated — use interview + configure --answers"),
        ("update", "Write stale or missing managed files only"),
        ("repair", "Fix lockfile drift and incomplete installs"),
        ("factory-restore", "Force reinstall of all managed files"),
    ):
        subparser = sub.add_parser(name, help=help_text)
        _add_common_args(subparser)
        if name == "interview":
            subparser.add_argument(
                "--save-answers",
                metavar="PATH",
                help=f"Where to write answers (default: {interview.DEFAULT_ANSWERS_REL})",
            )
        if name == "configure":
            subparser.add_argument(
                "--dry-run",
                action="store_true",
                help="Run interview and plan-setup only; do not write managed files",
            )
    return parser


def _interview_required_error() -> ValueError:
    return ValueError(
        "interview_required: pass --answers with a completed interview JSON file, "
        f"or run interview/configure in a terminal (TTY). "
        f"Expected path: {interview.DEFAULT_ANSWERS_REL}"
    )


def _run_interview(
    workspace: Path,
    package_root: Path,
    *,
    answers: dict | None,
    save_answers: str | None,
) -> dict:
    interview_data = interview.load_interview(package_root)
    if answers is not None:
        resolved = interview.resolve_answers(
            interview_data, answers, package_root=package_root
        )
    elif sys.stdin.isatty():
        resolved = interview.run_terminal_interview(
            interview_data,
            package_root=package_root,
        )
    else:
        raise _interview_required_error()

    out_path = (
        _resolve_path(save_answers)
        if save_answers
        else interview.default_answers_path(workspace)
    )
    interview.write_answers_file(out_path, resolved)
    return {
        "command": "interview",
        "answers": resolved,
        "answersPath": str(out_path.relative_to(workspace)),
    }


def _load_configure_answers(
    workspace: Path,
    package_root: Path,
    args: argparse.Namespace,
) -> dict:
    if args.answers:
        loaded = _load_answers(args.answers) or {}
        interview_data = interview.load_interview(package_root)
        if not interview.answers_complete(interview_data, loaded, package_root=package_root):
            raise ValueError(
                "interview_required: --answers file is missing required interview keys"
            )
        return loaded

    if sys.stdin.isatty():
        interview_data = interview.load_interview(package_root)
        return interview.run_terminal_interview(
            interview_data,
            package_root=package_root,
        )

    raise _interview_required_error()


def _run_configure(
    workspace: Path,
    package_root: Path,
    args: argparse.Namespace,
) -> dict:
    answers = _load_configure_answers(workspace, package_root, args)
    answers_path = interview.default_answers_path(workspace)
    interview.write_answers_file(answers_path, answers)

    plan = engine.plan_setup(workspace, package_root, answers=answers)
    result: dict = {
        "command": "configure",
        "answers": answers,
        "answersPath": str(answers_path.relative_to(workspace)),
        "plan": plan,
    }

    if args.dry_run:
        result["applied"] = False
        result["reason"] = "dry-run"
        return result

    if sys.stdin.isatty():
        to_write = plan.get("wouldWrite") or plan.get("filesToWrite") or []
        count = len(to_write) if isinstance(to_write, list) else plan.get("summary", {}).get("toWrite", "?")
        raw = input(f"Apply setup ({count} managed files)? [Y/n]: ").strip().lower()
        if raw in {"n", "no"}:
            result["applied"] = False
            result["reason"] = "user-declined"
            return result

    setup_result = engine.setup(workspace, package_root, answers=answers)
    result["applied"] = True
    result["setup"] = setup_result
    return result


def _emit_deprecated_setup(*, as_json: bool) -> int:
    payload = {
        "ok": False,
        "error": "deprecated_command",
        "hint": SETUP_DEPRECATED_HINT,
    }
    print(SETUP_DEPRECATED_HINT, file=sys.stderr)
    if as_json:
        print(json.dumps(payload, indent=2))
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace, package_root = _resolve_roots(parser, args)

    if args.command == "setup":
        return _emit_deprecated_setup(as_json=args.json)

    try:
        answers = _load_answers(getattr(args, "answers", None))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {"ok": False, "error": f"Invalid --answers: {exc}"}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(payload["error"], file=sys.stderr)
        return 1

    try:
        if args.command == "inspect":
            result = engine.inspect(workspace, package_root, answers=answers)
        elif args.command == "plan-setup":
            result = engine.plan_setup(workspace, package_root, answers=answers)
        elif args.command == "interview":
            result = _run_interview(
                workspace,
                package_root,
                answers=answers,
                save_answers=getattr(args, "save_answers", None),
            )
        elif args.command == "configure":
            result = _run_configure(workspace, package_root, args)
        elif args.command == "update":
            result = {"command": "update", **engine.update(workspace, package_root, answers=answers)}
        elif args.command == "repair":
            result = engine.repair(workspace, package_root, answers=answers)
        elif args.command == "factory-restore":
            result = engine.factory_restore(workspace, package_root, answers=answers)
        else:
            parser.error(f"unknown command: {args.command}")
            return 2
    except FileNotFoundError as exc:
        payload = {"ok": False, "error": str(exc)}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(payload["error"], file=sys.stderr)
        return 1
    except ValueError as exc:
        message = str(exc)
        code = "interview_required" if message.startswith("interview_required") else "error"
        payload = {"ok": False, "error": code, "message": message}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(message, file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({"ok": True, "result": result}, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
