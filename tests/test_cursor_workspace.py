"""Tests for shared MCP workspace helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mcp" / "scripts"))
from _cursor_workspace import discover_workspace_root, read_lockfile, workspace_is_valid

REPO_ROOT = Path(__file__).resolve().parents[1]


class CursorWorkspaceTests(unittest.TestCase):
    def test_discover_repo_root(self) -> None:
        script = REPO_ROOT / "mcp/scripts/cursorToolsMcp.py"
        root = discover_workspace_root(script)
        self.assertTrue((root / ".cursor-plugin").exists() or (root / "cursorAssistant.py").exists())

    def test_read_lockfile_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".cursor").mkdir()
            self.assertIsNone(read_lockfile(root))

    def test_workspace_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".cursor").mkdir()
            self.assertTrue(workspace_is_valid(root))


if __name__ == "__main__":
    unittest.main()
