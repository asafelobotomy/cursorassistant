"""Tests for cursorEval static commands."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CURSOR_EVAL = REPO_ROOT / "tools" / "cursorEval" / "cursorEval.py"


def run_cursor_eval(command: str, *args: str, fmt: str | None = None) -> subprocess.CompletedProcess[str]:
    argv = [sys.executable, str(CURSOR_EVAL), "--repo-root", str(REPO_ROOT)]
    if fmt:
        argv.extend(["--format", fmt])
    argv.append(command)
    argv.extend(args)
    return subprocess.run(
        argv,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class CursorEvalTests(unittest.TestCase):
    def test_list_discovers_core_and_pack_evals(self) -> None:
        result = run_cursor_eval("list", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        ids = {suite["id"] for suite in payload["suites"]}
        self.assertIn("lifecycleAudit", ids)
        self.assertIn("leanOutput", ids)
        self.assertIn("commit", ids)

    def test_validate_all_passes(self) -> None:
        result = run_cursor_eval("validate", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["failed"], 0)

    def test_check_skill_passes(self) -> None:
        skill = REPO_ROOT / "skills/lifecycleAudit/SKILL.md"
        result = run_cursor_eval("check", str(skill))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_check_agent_passes(self) -> None:
        agent = REPO_ROOT / "agents/explore.md"
        result = run_cursor_eval("check", str(agent))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_coverage_reports_surfaces(self) -> None:
        result = run_cursor_eval("coverage", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["total"], 10)

    def test_run_dry_run(self) -> None:
        eval_path = REPO_ROOT / "evals/lifecycleAudit/eval.yaml"
        result = run_cursor_eval("run", str(eval_path), "--dry-run", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dryRun"])


if __name__ == "__main__":
    unittest.main()
