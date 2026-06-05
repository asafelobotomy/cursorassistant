"""Tests for D4 skill and extended agent token wiring."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lifecycle import engine, interview, skill_customization

REPO_ROOT = Path(__file__).resolve().parents[1]
BALANCED = REPO_ROOT / "tests/fixtures/interview-balanced.json"


class SkillCustomizationTests(unittest.TestCase):
    def test_skill_questions_include_ci_preflight(self) -> None:
        questions = skill_customization.skill_questions(REPO_ROOT)
        ids = {question["id"] for question in questions}
        self.assertIn("skill.ciPreflight.runPolicy", ids)

    def test_agent_and_skill_question_order(self) -> None:
        ordered = interview.agent_and_skill_questions(REPO_ROOT)
        ids = [question["id"] for question in ordered]
        self.assertLess(
            ids.index("agent.debugger.diagnosisDepth"),
            ids.index("skill.ciPreflight.runPolicy"),
        )
        self.assertLess(
            ids.index("skill.ciPreflight.runPolicy"),
            ids.index("agent.deps.auditThreshold"),
        )

    def test_materialized_debugger_has_no_raw_tokens(self) -> None:
        answers = json.loads(BALANCED.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT, answers=answers)
            text = (workspace / ".cursor/agents/debugger.md").read_text(encoding="utf-8")
            self.assertNotIn("{{agent:debugger:diagnosis-style}}", text)
            self.assertIn("smallest credible fix step", text)

    def test_ci_preflight_skill_receives_run_policy_token(self) -> None:
        answers = json.loads(BALANCED.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT, answers=answers)
            text = (workspace / ".cursor/skills/ciPreflight/SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("{{skill:ciPreflight:run-policy}}", text)
            self.assertIn("staged files", text)

    def test_auto_save_defaults_strips_from_project_file(self) -> None:
        from scripts.lifecycle import user_defaults

        answers = {
            "setup.depth": "advanced",
            "setup.defaults.autoSave": True,
            "profile.selected": "balanced",
        }
        saved = interview.sanitize_answers_for_save(answers)
        self.assertNotIn("setup.defaults.autoSave", saved)
        defaults_payload = user_defaults.answers_for_defaults_file(answers)
        self.assertTrue(defaults_payload["setup.defaults.autoSave"])


if __name__ == "__main__":
    unittest.main()
