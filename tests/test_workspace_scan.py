"""Tests for workspace stack scanner."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.lifecycle import workspace_scan


class WorkspaceScanTests(unittest.TestCase):
    def test_detects_python_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[tool.pytest]\n", encoding="utf-8")
            (root / "tests").mkdir()
            tokens = workspace_scan.scan_workspace_stack(root)
            self.assertEqual(tokens.get("PRIMARY_LANGUAGE"), "Python")
            self.assertEqual(tokens.get("TEST_COMMAND"), "pytest")

    def test_empty_workspace_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(workspace_scan.scan_workspace_stack(Path(tmp)), {})


if __name__ == "__main__":
    unittest.main()
