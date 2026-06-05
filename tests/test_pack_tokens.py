"""Tests for pack token loading."""

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

    def test_pack_tokens_namespaced_only_no_legacy_aliases(self) -> None:
        tokens = pack_tokens.pack_tokens(REPO_ROOT, ["lean"])
        self.assertIn("pack:lean:review-depth", tokens)
        self.assertNotIn("pack:review-depth", tokens)

    def test_collision_keeps_both_namespaced_keys(self) -> None:
        tokens = pack_tokens.pack_tokens(REPO_ROOT, ["lean", "tdd"])
        self.assertIn("pack:lean:review-depth", tokens)
        self.assertIn("pack:tdd:review-depth", tokens)
        self.assertNotIn("pack:review-depth", tokens)

    def test_inspect_includes_pack_tokens_when_selected(self) -> None:
        answers = {
            "setup.depth": "simple",
            "profile.selected": "balanced",
            "packs.selected": ["tdd"],
            "mcp.enabled": False,
            "tdd.cycle.strictness": "guided",
            "agent.commit.messageStyle": "conventional-subject-first",
            "agent.docs.outputStyle": "corpus-match",
            "agent.planner.planFormat": "tight-phased",
            "agent.review.reportingThreshold": "critical-high",
            "agent.debugger.diagnosisDepth": "minimal-fix-first",
            "skill.ciPreflight.runPolicy": "staged-only",
            "agent.deps.auditThreshold": "critical-high",
            "agent.inventory.mapDepth": "layout-and-callers",
        }
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            plan = engine.plan_setup(workspace, REPO_ROOT, answers=answers)
            pack_group = plan["tokenSummary"].get("pack", {})
            self.assertTrue(
                any(key.startswith("pack:tdd:") for key in pack_group),
                msg=f"expected pack:tdd:* tokens, got {pack_group}",
            )


if __name__ == "__main__":
    unittest.main()
