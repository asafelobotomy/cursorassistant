"""Tests for pack token loading and legacy aliases."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.lifecycle import engine, pack_tokens

REPO_ROOT = Path(__file__).resolve().parents[1]


class PackTokenTests(unittest.TestCase):
    def test_normalize_legacy_key_to_namespaced(self) -> None:
        self.assertEqual(
            pack_tokens.normalize_token_key("lean", "pack:review-depth"),
            "pack:lean:review-depth",
        )
        self.assertEqual(
            pack_tokens.normalize_token_key("tdd", "pack:tdd:scope-discipline"),
            "pack:tdd:scope-discipline",
        )

    def test_pack_tokens_includes_namespaced_and_alias(self) -> None:
        tokens = pack_tokens.pack_tokens(REPO_ROOT, ["lean"])
        self.assertIn("pack:lean:review-depth", tokens)
        self.assertIn("pack:review-depth", tokens)
        self.assertEqual(tokens["pack:review-depth"], tokens["pack:lean:review-depth"])

    def test_reserved_reasoning_mode_not_aliased_from_pack(self) -> None:
        tokens = pack_tokens.pack_tokens(REPO_ROOT, ["lean"])
        self.assertIn("pack:lean:reasoning-mode", tokens)
        self.assertNotIn("pack:reasoning-mode", tokens)

    def test_collision_last_pack_wins_alias(self) -> None:
        tokens = pack_tokens.pack_tokens(REPO_ROOT, ["lean", "tdd"])
        self.assertIn("pack:lean:review-depth", tokens)
        self.assertIn("pack:tdd:review-depth", tokens)
        self.assertEqual(tokens["pack:review-depth"], tokens["pack:tdd:review-depth"])

    def test_inspect_includes_pack_tokens_when_selected(self) -> None:
        answers = {
            "setup.depth": "simple",
            "profile.selected": "balanced",
            "packs.selected": ["tdd"],
            "mcp.enabled": False,
            "agent.commit.messageStyle": "conventional-subject-first",
            "agent.docs.outputStyle": "corpus-match",
            "agent.planner.planFormat": "tight-phased",
            "agent.review.reportingThreshold": "critical-high",
        }
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            report = engine.inspect(workspace, REPO_ROOT, answers=answers)
            self.assertIn("tdd", report["selectedPacks"])
            plan = engine.plan_setup(workspace, REPO_ROOT, answers=answers)
            pack_group = plan["tokenSummary"].get("pack", {})
            self.assertTrue(
                any(key.startswith("pack:tdd:") for key in pack_group),
                msg=f"expected pack:tdd:* tokens, got {pack_group}",
            )


if __name__ == "__main__":
    unittest.main()
