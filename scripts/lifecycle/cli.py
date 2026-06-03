"""Argument parsing and JSON CLI for cursorAssistant."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.lifecycle import engine


def _resolve_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cursorAssistant", description="Cursor surface lifecycle")
    parser.add_argument("--workspace", required=True, help="Consumer workspace root")
    parser.add_argument("--package-root", required=True, help="cursorAssistant package root")
    parser.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("inspect", help="Read-only install state")
    sub.add_parser("setup", help="First-time or full refresh install")
    sub.add_parser("update", help="Write stale or missing managed files only")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    workspace = _resolve_path(args.workspace)
    package_root = _resolve_path(args.package_root)
    if not workspace.is_dir():
        parser.error(f"workspace is not a directory: {workspace}")
    if not package_root.is_dir():
        parser.error(f"package-root is not a directory: {package_root}")

    try:
        if args.command == "inspect":
            result = engine.inspect(workspace, package_root)
        elif args.command == "setup":
            result = {"command": "setup", **engine.setup(workspace, package_root)}
        elif args.command == "update":
            result = {"command": "update", **engine.update(workspace, package_root)}
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

    if args.json:
        print(json.dumps({"ok": True, "result": result}, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0
