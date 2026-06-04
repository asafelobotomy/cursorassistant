"""Tests for package root discovery."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.lifecycle import engine, paths

REPO_ROOT = Path(__file__).resolve().parents[1]


class PathsTests(unittest.TestCase):
    def test_module_anchor_is_repo(self) -> None:
        anchor = paths.module_anchor_root()
        self.assertIsNotNone(anchor)
        self.assertEqual(anchor, REPO_ROOT.resolve())

    def test_find_from_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            with mock.patch.dict(os.environ, {"CURSOR_ASSISTANT_PACKAGE_ROOT": str(REPO_ROOT)}):
                root = paths.find_package_root(workspace)
            self.assertEqual(root, REPO_ROOT.resolve())

    def test_find_from_lockfile_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            lock_path = workspace / ".cursor" / "cursorAssistant-lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["package"]["packageRoot"] = str(REPO_ROOT)
            lock_path.write_text(json.dumps(lock, indent=2), encoding="utf-8")
            root = paths.find_package_root(workspace)
            self.assertEqual(root, REPO_ROOT.resolve())

    def test_walk_parent_finds_nested_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "apps" / "demo"
            nested.mkdir(parents=True)
            root = paths.find_package_root(nested)
            self.assertEqual(root, REPO_ROOT.resolve())
