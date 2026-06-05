"""Tests for cursorAssistant lifecycle CLI."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "cursorAssistant.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "interview-balanced.json"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_setup_command_deprecated(self) -> None:
        completed = run_cli("setup", "--workspace", ".", "--json")
        self.assertEqual(completed.returncode, 2)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"], "deprecated_command")

    def test_configure_non_tty_requires_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            completed = run_cli(
                "configure",
                "--workspace",
                str(workspace),
                "--package-root",
                str(REPO_ROOT),
                "--json",
            )
            self.assertEqual(completed.returncode, 1)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"], "interview_required")

    def test_configure_with_answers_installs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            completed = run_cli(
                "configure",
                "--workspace",
                str(workspace),
                "--package-root",
                str(REPO_ROOT),
                "--answers",
                str(FIXTURE),
                "--json",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["ok"])
            self.assertTrue(payload["result"]["applied"])
            self.assertTrue((workspace / ".cursor/cursorAssistant-lock.json").is_file())
            self.assertTrue((workspace / ".cursor/cursor-assistant-answers.json").is_file())

    def test_update_blocks_without_answers_when_interview_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            from scripts.lifecycle import engine

            engine.setup(workspace, REPO_ROOT)
            answers_path = workspace / ".cursor/cursor-assistant-answers.json"
            answers_path.unlink()
            completed = run_cli(
                "update",
                "--workspace",
                str(workspace),
                "--package-root",
                str(REPO_ROOT),
                "--json",
            )
            self.assertEqual(completed.returncode, 1)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["error"], "interview_required")


if __name__ == "__main__":
    unittest.main()
