"""Tests for cursorAssistant lifecycle engine."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.lifecycle import engine

REPO_ROOT = Path(__file__).resolve().parents[1]


class EngineTests(unittest.TestCase):
    def test_inspect_not_installed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertEqual(report["installState"], "not-installed")
            self.assertFalse(report["lockfilePresent"])

    def test_setup_writes_lockfile_and_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            result = engine.setup(workspace, REPO_ROOT)
            self.assertIn("routing.agents-md", result["written"])
            self.assertTrue((workspace / "AGENTS.md").is_file())
            self.assertTrue((workspace / ".cursor/agents/explore.md").is_file())
            lock = json.loads((workspace / ".cursor/cursorAssistant-lock.json").read_text())
            self.assertEqual(lock["package"]["name"], "cursorAssistant")

    def test_update_skips_clean_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            result = engine.update(workspace, REPO_ROOT)
            self.assertEqual(result["written"], [])
            self.assertGreater(len(result["skipped"]), 0)

    def test_inspect_detects_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            agent = workspace / ".cursor/agents/explore.md"
            agent.write_text(agent.read_text() + "\n# stale\n", encoding="utf-8")
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertEqual(report["installState"], "needs-update")
            stale = [f for f in report["files"] if f["status"] == "stale"]
            self.assertTrue(any(row["id"] == "agents.explore" for row in stale))


if __name__ == "__main__":
    unittest.main()
