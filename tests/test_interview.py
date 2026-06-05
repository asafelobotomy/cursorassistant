"""Tests for setup interview depth gating and agent questions."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.lifecycle import interview

REPO_ROOT = Path(__file__).resolve().parents[1]


class InterviewTests(unittest.TestCase):
    def test_preflight_questions_always_active_first(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        active = interview.active_questions(data, {}, package_root=REPO_ROOT)
        ids = [question["id"] for question in active]
        self.assertEqual(ids[0], "setup.copyFrom.enabled")
        self.assertIn("setup.depth", ids)

    def test_copy_from_repo_inactive_when_disabled(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        answers = {"setup.copyFrom.enabled": False}
        active = interview.active_questions(data, answers, package_root=REPO_ROOT)
        ids = {question["id"] for question in active}
        self.assertIn("setup.copyFrom.enabled", ids)
        self.assertNotIn("setup.copyFrom.repo", ids)

    def test_questions_payload_marks_defaults_as_pending(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        payload = interview.interview_questions_payload(
            data, {}, package_root=REPO_ROOT, explicit_keys=set()
        )
        self.assertIn("setup.copyFrom.enabled", payload["pending"])
        self.assertFalse(payload["complete"])

    def test_simple_depth_excludes_advanced_questions(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        answers = {
            "setup.depth": "simple",
            "profile.selected": "balanced",
            "packs.selected": [],
            "mcp.enabled": False,
        }
        active = interview.active_questions(data, answers, package_root=REPO_ROOT)
        ids = {question["id"] for question in active}
        self.assertIn("setup.depth", ids)
        self.assertIn("profile.selected", ids)
        self.assertNotIn("response.style", ids)
        self.assertNotIn("testing.philosophy", ids)
        self.assertIn("agent.commit.messageStyle", ids)

    def test_advanced_depth_includes_personalization(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        answers = {"setup.depth": "advanced", "profile.selected": "balanced"}
        active = interview.active_questions(data, answers, package_root=REPO_ROOT)
        ids = {question["id"] for question in active}
        self.assertIn("response.style", ids)
        self.assertIn("autonomy.level", ids)
        self.assertNotIn("testing.philosophy", ids)

    def test_lean_reasoning_question_when_lean_profile(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        answers = {"setup.depth": "simple", "profile.selected": "lean"}
        active = interview.active_questions(data, answers, package_root=REPO_ROOT)
        ids = {question["id"] for question in active}
        self.assertIn("lean.reasoning.mode", ids)

    def test_answers_complete_simple_fixture(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        answers = {
            "setup.depth": "simple",
            "profile.selected": "balanced",
            "packs.selected": [],
            "mcp.enabled": False,
            "agent.commit.messageStyle": "conventional-subject-first",
            "agent.docs.outputStyle": "corpus-match",
            "agent.planner.planFormat": "tight-phased",
            "agent.review.reportingThreshold": "critical-high",
        }
        self.assertTrue(
            interview.answers_complete(data, answers, package_root=REPO_ROOT)
        )


if __name__ == "__main__":
    unittest.main()
