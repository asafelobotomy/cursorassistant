"""Vendored from packages/cursor-mcp-shared — run scripts/vendor_mcp_shared.py to refresh."""

from __future__ import annotations

def tail_text(text: str, *, max_lines: int = 20, max_chars: int = 4000) -> str | None:
    if not text:
        return None
    tail = "\n".join(text.splitlines()[-max_lines:])
    if len(tail) > max_chars:
        tail = tail[-max_chars:]
    return tail


def build_tool_result(
    *,
    status: str,
    summary: str,
    command: str | None = None,
    exit_code: int | None = None,
    stdout: str = "",
    stderr: str = "",
) -> dict:
    result: dict = {"status": status, "summary": summary}
    if command is not None:
        result["command"] = command
    if exit_code is not None:
        result["exitCode"] = exit_code
    stdout_tail = tail_text(stdout)
    stderr_tail = tail_text(stderr)
    if stdout_tail:
        result["stdoutTail"] = stdout_tail
    if stderr_tail:
        result["stderrTail"] = stderr_tail
    return result
