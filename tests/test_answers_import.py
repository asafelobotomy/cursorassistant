"""Tests for GitHub copy-from answer import."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from scripts.lifecycle import answers_import, interview

REPO_ROOT = Path(__file__).resolve().parents[1]


class AnswersImportTests(unittest.TestCase):
    def test_parse_github_repo_formats(self) -> None:
        owner, repo = answers_import.parse_github_repo("asafelobotomy/cursorassistant")
        self.assertEqual((owner, repo), ("asafelobotomy", "cursorassistant"))
        owner, repo = answers_import.parse_github_repo(
            "https://github.com/asafelobotomy/cursorassistant"
        )
        self.assertEqual((owner, repo), ("asafelobotomy", "cursorassistant"))

    def test_parse_rejects_branch_urls(self) -> None:
        with self.assertRaises(answers_import.AnswersImportError):
            answers_import.parse_github_repo(
                "https://github.com/o/r/tree/main/.cursor"
            )

    def test_flatten_lockfile_to_answers(self) -> None:
        lock = {
            "profile": "lean",
            "selectedPacks": ["lean"],
            "mcpEnabled": True,
            "setupAnswers": {"setup.depth": "simple", "response.style": "concise"},
            "packAnswers": {"secure": {"secure.review.default": "owasp-focused"}},
        }
        flat = answers_import.flatten_lockfile_to_answers(lock)
        self.assertEqual(flat["profile.selected"], "lean")
        self.assertEqual(flat["packs.selected"], ["lean"])
        self.assertTrue(flat["mcp.enabled"])
        self.assertEqual(flat["setup.depth"], "simple")

    def test_sanitize_drops_unknown_and_ephemeral(self) -> None:
        raw = {
            "setup.depth": "simple",
            "unknown.key": "x",
            "setup.copyFrom.enabled": True,
            "profile.selected": "balanced",
        }
        merged, dropped, _warnings = answers_import.sanitize_imported_answers(
            raw, package_root=REPO_ROOT
        )
        self.assertIn("unknown.key", dropped)
        self.assertIn("setup.copyFrom.enabled", dropped)
        self.assertIn("setup.depth", merged)

    def test_validate_answers_no_secrets(self) -> None:
        warnings = answers_import.validate_answers_no_secrets(
            {"api_key": "sk-abcdefghijklmnopqrstuvwxyz1234567890"}
        )
        self.assertTrue(warnings)

    def test_import_from_repo_merges_public_fixture(self) -> None:
        fixture = {
            "setup.depth": "advanced",
            "profile.selected": "balanced",
            "packs.selected": [],
            "mcp.enabled": False,
            "response.style": "concise",
            "autonomy.level": "ask-first",
            "agent.persona": "professional",
            "agent.commit.messageStyle": "conventional-subject-first",
            "agent.docs.outputStyle": "corpus-match",
            "agent.planner.planFormat": "tight-phased",
            "agent.review.reportingThreshold": "critical-high",
        }
        with mock.patch.object(
            answers_import, "_fetch_public_answers", return_value=fixture
        ):
            result = answers_import.import_from_repo(
                "asafelobotomy/cursorassistant",
                package_root=REPO_ROOT,
                base_answers={"setup.copyFrom.enabled": True},
            )
        self.assertEqual(result["imported"]["setup.depth"], "advanced")
        self.assertTrue(result["merged"]["setup.copyFrom.enabled"])

    def test_import_rejects_secrets(self) -> None:
        with mock.patch.object(
            answers_import,
            "_fetch_public_answers",
            return_value={"api_key": "sk-abcdefghijklmnopqrstuvwxyz1234567890"},
        ):
            with self.assertRaises(answers_import.AnswersImportError):
                answers_import.import_from_repo("o/r", package_root=REPO_ROOT)


class InterviewSanitizeTests(unittest.TestCase):
    def test_sanitize_strips_copy_from_keys(self) -> None:
        answers = {
            "setup.depth": "simple",
            "setup.copyFrom.enabled": True,
            "setup.copyFrom.repo": "o/r",
        }
        saved = interview.sanitize_answers_for_save(answers)
        self.assertNotIn("setup.copyFrom.enabled", saved)
        self.assertIn("setup.depth", saved)


if __name__ == "__main__":
    unittest.main()
