"""Tests for cursor-mcp-shared package."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parents[1] / "packages" / "cursor-mcp-shared"
sys.path.insert(0, str(PKG_ROOT))

from cursor_mcp_shared.mcp_util import build_tool_result, tail_text  # noqa: E402
from cursor_mcp_shared.workspace import discover_workspace_root, is_workspace_root  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


class CursorMcpSharedTests(unittest.TestCase):
    def test_is_workspace_root_package_repo(self) -> None:
        self.assertTrue(is_workspace_root(REPO_ROOT))

    def test_discover_from_mcp_script(self) -> None:
        script = REPO_ROOT / "mcp/scripts/cursorToolsMcp.py"
        self.assertEqual(discover_workspace_root(script), REPO_ROOT)

    def test_build_tool_result_shape(self) -> None:
        payload = build_tool_result(
            status="ok",
            summary="done",
            command="echo hi",
            exit_code=0,
            stdout="line\n" * 30,
        )
        self.assertEqual(payload["status"], "ok")
        self.assertIn("stdoutTail", payload)

    def test_tail_text_truncates(self) -> None:
        long = "x" * 5000
        tail = tail_text(long, max_chars=100)
        self.assertIsNotNone(tail)
        assert tail is not None
        self.assertLessEqual(len(tail), 100)


if __name__ == "__main__":
    unittest.main()
