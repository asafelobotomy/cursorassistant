#!/usr/bin/env python3
"""cursorTools MCP server — wraps cursorAssistant lifecycle CLI."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP

from _cursor_mcp_util import build_tool_result, tail_text
from _cursor_package_root import find_package_root as discover_package_root
from _cursor_package_root import validate_package_root
from _cursor_workspace import discover_workspace_root, read_lockfile

WORKSPACE_ROOT = discover_workspace_root(Path(__file__))


def resolve_package_root(package_root: str | None) -> tuple[Path | None, str | None]:
    if package_root:
        root = validate_package_root(Path(package_root))
        if root is None:
            return None, f"packageRoot is not a cursorAssistant package: {package_root}"
        return root, None
    discovered = discover_package_root(WORKSPACE_ROOT)
    if discovered is not None:
        return discovered, None
    lock = read_lockfile(WORKSPACE_ROOT)
    package_block = lock.get("package") if isinstance(lock, dict) else None
    if isinstance(package_block, dict):
        value = package_block.get("packageRoot")
        if isinstance(value, str) and value.strip():
            raw = Path(value).expanduser()
            root = (WORKSPACE_ROOT / raw).resolve() if not raw.is_absolute() else raw.resolve()
            if root.is_dir():
                return root, None
    return (
        None,
        "Install the cursor-assistant plugin, clone cursorAssistant, or pass packageRoot. "
        "After the first project setup, packageRoot is stored in the lockfile.",
    )


def resolve_answers_path(answers_path: str | None) -> tuple[Path | None, dict | None]:
    if not answers_path:
        return None, None
    candidate = Path(answers_path).expanduser()
    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / candidate
    resolved = candidate.resolve()
    if not resolved.is_file():
        return None, tool_result(
            "unavailable",
            "answersPath must point to an existing file within the workspace.",
        )
    if not resolved.is_relative_to(WORKSPACE_ROOT.resolve()):
        return None, tool_result(
            "unavailable",
            "answersPath must point to an existing file within the workspace.",
        )
    return resolved, None


def tool_result(
    status: str,
    summary: str,
    *,
    command: str | None = None,
    exit_code: int | None = None,
    stdout: str = "",
    stderr: str = "",
    payload: dict | None = None,
) -> dict:
    result = build_tool_result(
        status=status,
        summary=summary,
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
    )
    if payload is not None:
        result["payload"] = payload
    return result


def _lifecycle_imports() -> tuple[Path | None, Any | None, Any | None, Any | None, str | None]:
    root, reason = resolve_package_root(None)
    if root is None:
        return None, None, None, None, reason or "package root unavailable"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from scripts.lifecycle import answers_import, interview, user_defaults

    return root, interview, answers_import, user_defaults, None


def run_lifecycle(command: str, *, package_root: str | None = None, answers_path: str | None = None) -> dict:
    root, reason = resolve_package_root(package_root)
    if root is None:
        return tool_result("unavailable", reason or "package root unavailable")
    cli = root / "cursorAssistant.py"
    if not cli.is_file():
        return tool_result("unavailable", f"Missing cursorAssistant CLI at {cli}")

    argv = [
        sys.executable,
        str(cli),
        command,
        "--workspace",
        str(WORKSPACE_ROOT),
        "--package-root",
        str(root),
        "--json",
    ]
    resolved_answers, answers_error = resolve_answers_path(answers_path)
    if answers_error is not None:
        return answers_error
    if resolved_answers is not None:
        argv.extend(["--answers", str(resolved_answers)])

    completed = subprocess.run(
        argv,
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    payload = None
    if completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
            if isinstance(parsed, dict):
                payload = parsed
        except json.JSONDecodeError:
            payload = None

    ok = completed.returncode == 0 and (payload is None or payload.get("ok", True))
    status = "ok" if ok else "failed"
    summary = f"Lifecycle command {command} completed." if ok else f"Lifecycle command {command} failed."
    return tool_result(
        status,
        summary,
        command=shlex.join(argv),
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        payload=payload,
    )


mcp = FastMCP("cursorTools")


@mcp.tool()
def lifecycle_inspect(packageRoot: str | None = None) -> dict:
    """Read cursorAssistant install state for the current workspace."""
    return run_lifecycle("inspect", package_root=packageRoot)


@mcp.tool()
def lifecycle_plan_setup(packageRoot: str | None = None, answersPath: str | None = None) -> dict:
    """Plan setup/update without writing managed files."""
    return run_lifecycle("plan-setup", package_root=packageRoot, answers_path=answersPath)


@mcp.tool()
def lifecycle_setup(packageRoot: str | None = None, answersPath: str | None = None) -> dict:
    """Deprecated. Use lifecycle_configure with a required answersPath from a completed interview."""
    _ = (packageRoot, answersPath)
    return tool_result(
        "unavailable",
        "lifecycle_setup is deprecated. Run lifecycle_configure with answersPath "
        f"pointing to {'.cursor/cursor-assistant-answers.json'}.",
    )


@mcp.tool()
def lifecycle_configure(
    packageRoot: str | None = None,
    answersPath: str | None = None,
) -> dict:
    """Install cursorAssistant using interview answers (answersPath required)."""
    if not answersPath:
        return tool_result(
            "unavailable",
            "answersPath is required. Complete the setup interview, write "
            ".cursor/cursor-assistant-answers.json, then pass answersPath.",
        )
    return run_lifecycle("configure", package_root=packageRoot, answers_path=answersPath)


@mcp.tool()
def lifecycle_update(packageRoot: str | None = None, answersPath: str | None = None) -> dict:
    """Update stale or missing managed cursorAssistant surfaces."""
    return run_lifecycle("update", package_root=packageRoot, answers_path=answersPath)


@mcp.tool()
def lifecycle_repair(packageRoot: str | None = None, answersPath: str | None = None) -> dict:
    """Repair lockfile drift or incomplete cursorAssistant installs."""
    return run_lifecycle("repair", package_root=packageRoot, answers_path=answersPath)


@mcp.tool()
def lifecycle_factory_restore(packageRoot: str | None = None, answersPath: str | None = None) -> dict:
    """Force reinstall of all managed cursorAssistant surfaces."""
    return run_lifecycle("factory-restore", package_root=packageRoot, answers_path=answersPath)


def _parse_json_object(raw: str | None, label: str) -> tuple[dict | None, dict | None]:
    if not raw or not raw.strip():
        return {}, None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, tool_result("failed", f"{label} must be valid JSON: {exc}")
    if not isinstance(parsed, dict):
        return None, tool_result("failed", f"{label} must be a JSON object")
    return parsed, None


@mcp.tool()
def lifecycle_interview_questions(
    packageRoot: str | None = None,
    partialAnswersJson: str | None = None,
) -> dict:
    """Return active/pending setup interview questions for AskQuestion batches."""
    root, interview_mod, _, _, err = _lifecycle_imports()
    if root is None:
        return tool_result("unavailable", err or "package root unavailable")
    partial, error = _parse_json_object(partialAnswersJson, "partialAnswersJson")
    if error is not None:
        return error
    interview_data = interview_mod.load_interview(root)
    draft = interview_mod.prefill_answers(
        interview_data,
        package_root=root,
        partial=partial,
    )
    payload = interview_mod.interview_questions_payload(
        interview_data,
        draft,
        package_root=root,
        explicit_keys=set(partial or {}),
    )
    return tool_result("ok", "Interview questions ready.", payload=payload)


@mcp.tool()
def lifecycle_interview_import(
    repo: str,
    packageRoot: str | None = None,
    partialAnswersJson: str | None = None,
) -> dict:
    """Fetch and validate answers from a GitHub repo; merge without writing."""
    root, interview_mod, answers_import_mod, _, err = _lifecycle_imports()
    if root is None:
        return tool_result("unavailable", err or "package root unavailable")
    partial, error = _parse_json_object(partialAnswersJson, "partialAnswersJson")
    if error is not None:
        return error
    try:
        result = answers_import_mod.import_from_repo(
            repo,
            package_root=root,
            base_answers=partial,
        )
    except (answers_import_mod.AnswersImportError, ValueError) as exc:
        return tool_result("failed", str(exc))
    return tool_result("ok", f"Imported answers from {result.get('source')}.", payload=result)


@mcp.tool()
def lifecycle_interview_save(
    answersJson: str,
    packageRoot: str | None = None,
    answersPath: str | None = None,
) -> dict:
    """Validate interview answers and write .cursor/cursor-assistant-answers.json."""
    root, interview_mod, _, _, err = _lifecycle_imports()
    if root is None:
        return tool_result("unavailable", err or "package root unavailable")
    answers, error = _parse_json_object(answersJson, "answersJson")
    if error is not None:
        return error
    interview_data = interview_mod.load_interview(root)
    if not interview_mod.answers_complete(interview_data, answers, package_root=root):
        return tool_result(
            "failed",
            "Interview answers are incomplete for the active depth and packs.",
        )
    target = (
        Path(answersPath).expanduser()
        if answersPath
        else WORKSPACE_ROOT / interview_mod.DEFAULT_ANSWERS_REL
    )
    if not target.is_absolute():
        target = WORKSPACE_ROOT / target
    target = target.resolve()
    if not target.is_relative_to(WORKSPACE_ROOT.resolve()):
        return tool_result("unavailable", "answersPath must stay within the workspace.")
    interview_mod.write_answers_file(target, answers)
    saved = interview_mod.sanitize_answers_for_save(answers)
    return tool_result(
        "ok",
        f"Wrote interview answers to {target.relative_to(WORKSPACE_ROOT)}.",
        payload={
            "answersPath": str(target.relative_to(WORKSPACE_ROOT)),
            "answers": saved,
            "keyCount": len(saved),
        },
    )


@mcp.tool()
def lifecycle_defaults_load() -> dict:
    """Read ~/.cursor/cursor-assistant-defaults.json when present."""
    _, _, _, user_defaults_mod, err = _lifecycle_imports()
    if user_defaults_mod is None:
        return tool_result("unavailable", err or "package root unavailable")
    try:
        defaults = user_defaults_mod.load_defaults()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return tool_result("failed", str(exc))
    return tool_result(
        "ok",
        "User defaults loaded." if defaults else "No user defaults file yet.",
        payload={
            "defaults": defaults,
            "defaultsPath": str(user_defaults_mod.defaults_path()),
            "present": defaults is not None,
        },
    )


@mcp.tool()
def lifecycle_defaults_save(answersJson: str) -> dict:
    """Write user defaults after explicit user confirmation (post-configure)."""
    _, interview_mod, _, user_defaults_mod, err = _lifecycle_imports()
    if interview_mod is None:
        return tool_result("unavailable", err or "package root unavailable")
    answers, error = _parse_json_object(answersJson, "answersJson")
    if error is not None:
        return error
    try:
        path = user_defaults_mod.save_defaults(answers)
    except OSError as exc:
        return tool_result("failed", str(exc))
    saved = interview_mod.sanitize_answers_for_save(answers)
    return tool_result(
        "ok",
        f"Saved user defaults to {path}.",
        payload={"defaultsPath": str(path), "keyCount": len(saved)},
    )


if __name__ == "__main__":
    mcp.run()
