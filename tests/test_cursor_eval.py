"""Tests for cursorEval static commands."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

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
        self.assertIn("inventory", ids)
        self.assertIn("surfaceReview", ids)
        self.assertNotIn("explore", ids)

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
        agent = REPO_ROOT / "agents/inventory.md"
        result = run_cursor_eval("check", str(agent))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_grade_task_expectations(self) -> None:
        from tools.cursorEval._common import grade_task_expectations

        rows = grade_task_expectations(
            "use inventory subagent",
            {"expected": ["inventory"], "expected_absent": ["(?i)explore subagent"]},
        )
        self.assertTrue(all(r["passed"] for r in rows))

    def test_models_smoke_validate(self) -> None:
        result = run_cursor_eval("validate", "evals/models-smoke/eval.yaml", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_policy_passes_on_core_sources(self) -> None:
        result = run_cursor_eval("policy", fmt="json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])

    def test_coverage_reports_surfaces(self) -> None:
        result = run_cursor_eval("coverage", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["total"], 10)
        self.assertIn("full", payload)
        self.assertIn("partial", payload)
        self.assertTrue(all("level" in row for row in payload["rows"]))
        self.assertTrue(all("blockingIssues" in row for row in payload["rows"]))

    def test_coverage_strict_passes_repo(self) -> None:
        result = run_cursor_eval("coverage", "--strict")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_coverage_all_full(self) -> None:
        result = run_cursor_eval("coverage", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["partial"], 0)
        self.assertEqual(payload["missing"], 0)
        self.assertEqual(payload["full"], payload["total"])

    def test_tokens_includes_structure_metrics(self) -> None:
        skill = REPO_ROOT / "skills/workspaceSearch/SKILL.md"
        result = run_cursor_eval("tokens", str(skill), fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("max_nesting_depth", payload)
        self.assertIn("code_blocks", payload)

    def test_check_includes_compliance_level(self) -> None:
        agent = REPO_ROOT / "agents/inventory.md"
        result = run_cursor_eval("check", str(agent), fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn(payload["compliance"], ("High", "Medium-High", "Medium", "Low"))
        advisory_ids = {row["id"] for row in payload["advisory"]}
        self.assertIn("procedural-content", advisory_ids)

    def test_suggest_dry_run(self) -> None:
        skill = REPO_ROOT / "skills/testing/SKILL.md"
        result = run_cursor_eval("suggest", str(skill), fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dryRun"])
        self.assertIn("evals/testing/eval.yaml", payload["files"])

    def test_run_dry_run(self) -> None:
        eval_path = REPO_ROOT / "evals/lifecycleAudit/eval.yaml"
        result = run_cursor_eval("run", str(eval_path), "--dry-run", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dryRun"])

    def test_run_dry_run_tags_filter(self) -> None:
        eval_path = REPO_ROOT / "evals/inventory/eval.yaml"
        result = run_cursor_eval(
            "run",
            str(eval_path),
            "--dry-run",
            "--tags",
            "smoke",
            fmt="json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["tasksSelected"], 3)
        self.assertEqual(payload["tasksTotal"], 4)

    def test_aggregate_trials_majority(self) -> None:
        from tools.cursorEval._common import aggregate_trials

        trial_a = [{"name": "g1", "type": "text", "passed": True, "score": 1.0}]
        trial_b = [{"name": "g1", "type": "text", "passed": True, "score": 0.8}]
        trial_c = [{"name": "g1", "type": "text", "passed": False, "score": 0.0}]
        merged = aggregate_trials([trial_a, trial_b, trial_c], 3)
        self.assertEqual(len(merged), 1)
        self.assertTrue(merged[0]["passed"])
        self.assertEqual(merged[0]["trials"], 3)

    def test_merge_run_config_task_override(self) -> None:
        from tools.cursorEval._common import merge_run_config

        cfg = merge_run_config(
            {"config": {"inject_skill_body": True, "trials_per_task": 2}},
            {"config": {"inject_skill_body": False}},
        )
        self.assertFalse(cfg["inject_skill_body"])
        self.assertEqual(cfg["trials_per_task"], 2)

    def test_results_list_empty_dir_fails(self) -> None:
        empty = REPO_ROOT / ".cursorEval-test-empty"
        empty.mkdir(exist_ok=True)
        try:
            result = run_cursor_eval("results", "list", "--dir", str(empty))
            self.assertEqual(result.returncode, 1)
        finally:
            empty.rmdir()


class CursorEvalTokenTests(unittest.TestCase):
    def test_get_token_prefers_models_env(self) -> None:
        from tools.cursorEval._model import get_token

        env = {
            "GITHUB_MODELS_TOKEN": "models-token",
            "GITHUB_TOKEN": "legacy-token",
            "GH_TOKEN": "gh-token",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(get_token(), "models-token")


class CursorEvalPhaseCTests(unittest.TestCase):
    def test_extract_first_json_object_nested(self) -> None:
        from tools.cursorEval._common import extract_first_json_object

        text = 'Here is the result:\n{"score": 0.9, "reasoning": "ok"}'
        obj = extract_first_json_object(text)
        self.assertIsNotNone(obj)
        self.assertEqual(obj["score"], 0.9)

    def test_run_graders_skips_prompt_judge_without_token(self) -> None:
        from tools.cursorEval._common import run_graders

        rows = run_graders(
            "sample response",
            [{"type": "prompt_judge", "name": "j", "config": {"rubric": "good"}}],
            model="gpt-4o-mini",
            token=None,
        )
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0].get("skipped"))

    def test_grade_text_only_without_token(self) -> None:
        eval_path = REPO_ROOT / "evals/lifecycleAudit/eval.yaml"
        with mock.patch.dict(os.environ, {}, clear=True):
            result = run_cursor_eval(
                "grade",
                str(eval_path),
                "--text",
                "lifecycleAudit skill checklist",
            )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_quality_without_token_exits_2(self) -> None:
        skill = REPO_ROOT / "skills/testing/SKILL.md"
        with mock.patch.dict(os.environ, {}, clear=True):
            result = run_cursor_eval("quality", str(skill))
        self.assertEqual(result.returncode, 2)

    def test_report_writes_html(self) -> None:
        agent = REPO_ROOT / "agents/inventory.md"
        out = REPO_ROOT / ".cursorEval-test-report.html"
        try:
            result = run_cursor_eval("report", str(agent), "-o", str(out))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out.is_file())
            html = out.read_text(encoding="utf-8")
            self.assertIn("cursorEval check report", html)
            self.assertIn("inventory", html)
        finally:
            if out.is_file():
                out.unlink()

    def test_validate_accepts_task_prompt_judge(self) -> None:
        result = run_cursor_eval("validate", "evals/lifecycleAudit/eval.yaml", fmt="json")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
