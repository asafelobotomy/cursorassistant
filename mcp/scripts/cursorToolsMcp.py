#!/usr/bin/env python3
"""cursorTools MCP server — wraps cursorAssistant lifecycle CLI."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

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
    """Install or refresh all managed cursorAssistant surfaces."""
    return run_lifecycle("setup", package_root=packageRoot, answers_path=answersPath)


@mcp.tool()
def lifecycle_configure(
    packageRoot: str | None = None,
    answersPath: str | None = None,
) -> dict:
    """Run setup interview and install cursorAssistant into the open workspace (preferred first-time path)."""
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


if __name__ == "__main__":
    mcp.run()
