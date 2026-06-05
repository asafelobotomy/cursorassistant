"""Tests for pack-gated interview questions and lockfile packAnswers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lifecycle import engine, interview, pack_interview, pack_tokens

REPO_ROOT = Path(__file__).resolve().parents[1]
SECURE_FIXTURE = REPO_ROOT / "tests/fixtures/interview-with-secure.json"


class PackInterviewTests(unittest.TestCase):
    def test_pack_questions_active_when_pack_selected(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        answers = {
            "setup.depth": "simple",
            "profile.selected": "balanced",
            "packs.selected": ["secure"],
            "mcp.enabled": False,
        }
        active = interview.active_questions(data, answers, package_root=REPO_ROOT)
        ids = {question["id"] for question in active}
        self.assertIn("secure.review.default", ids)

    def test_pack_questions_inactive_without_pack(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        answers = {
            "setup.depth": "simple",
            "profile.selected": "balanced",
            "packs.selected": [],
            "mcp.enabled": False,
        }
        active = interview.active_questions(data, answers, package_root=REPO_ROOT)
        ids = {question["id"] for question in active}
        self.assertNotIn("secure.review.default", ids)

    def test_split_pack_answers_for_lockfile(self) -> None:
        answers = json.loads(SECURE_FIXTURE.read_text(encoding="utf-8"))
        setup, pack_answers = pack_interview.split_pack_answers(
            REPO_ROOT, answers, ["secure"]
        )
        self.assertNotIn("secure.review.default", setup)
        self.assertEqual(
            pack_answers["secure"]["secure.review.default"], "owasp-focused"
        )

    def test_interview_tokens_override_static_pack_tokens(self) -> None:
        answers = json.loads(SECURE_FIXTURE.read_text(encoding="utf-8"))
        answers["secure.review.default"] = "critical-high-only"
        tokens = pack_tokens.pack_tokens(REPO_ROOT, ["secure"], answers=answers)
        self.assertIn("pack:secure:review-depth", tokens)
        self.assertNotIn("pack:review-depth", tokens)
        self.assertIn("Critical and High findings only", tokens["pack:secure:review-depth"])

    def test_configure_writes_pack_answers_lockfile(self) -> None:
        answers = json.loads(SECURE_FIXTURE.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT, answers=answers)
            lock = json.loads(
                (workspace / ".cursor/cursorAssistant-lock.json").read_text(encoding="utf-8")
            )
            self.assertEqual(lock["schemaVersion"], "0.6.0")
            self.assertIn("packAnswers", lock)
            self.assertEqual(
                lock["packAnswers"]["secure"]["secure.review.default"],
                "owasp-focused",
            )
            self.assertNotIn(
                "secure.review.default",
                lock.get("setupAnswers", {}),
            )


if __name__ == "__main__":
    unittest.main()
