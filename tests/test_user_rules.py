"""Tests for User Rules mapping from interview answers."""

from __future__ import annotations

import unittest

from scripts.lifecycle import user_rules


class UserRulesTests(unittest.TestCase):
    def test_simple_depth_returns_no_candidates(self) -> None:
        answers = {"setup.depth": "simple", "profile.selected": "balanced"}
        self.assertEqual(user_rules.user_rule_candidates(answers), [])
        self.assertIsNone(user_rules.combined_user_rule(answers))

    def test_advanced_depth_maps_personalization(self) -> None:
        answers = {
            "setup.depth": "advanced",
            "response.style": "concise",
            "autonomy.level": "ask-first",
            "agent.persona": "direct",
        }
        candidates = user_rules.user_rule_candidates(answers)
        keys = {item["key"] for item in candidates}
        self.assertEqual(keys, {"response.style", "autonomy.level", "agent.persona"})
        combined = user_rules.combined_user_rule(answers)
        self.assertIsNotNone(combined)
        self.assertIn("minimal prose", combined or "")


if __name__ == "__main__":
    unittest.main()
