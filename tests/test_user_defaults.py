"""Tests for user-scoped default answers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.lifecycle import interview, user_defaults

REPO_ROOT = Path(__file__).resolve().parents[1]


class UserDefaultsTests(unittest.TestCase):
    def test_merge_defaults_partial_wins(self) -> None:
        merged = user_defaults.merge_defaults(
            {"setup.depth": "full"},
            {"setup.depth": "simple", "profile.selected": "lean"},
        )
        self.assertEqual(merged["setup.depth"], "full")
        self.assertEqual(merged["profile.selected"], "lean")

    def test_save_strips_copy_from_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".cursor" / "cursor-assistant-defaults.json"
            with mock.patch.object(user_defaults, "defaults_path", return_value=path):
                user_defaults.save_defaults(
                    {
                        "setup.depth": "simple",
                        "setup.copyFrom.repo": "o/r",
                    }
                )
                payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("setup.copyFrom.repo", payload)
            self.assertEqual(payload["setup.depth"], "simple")

    def test_prefill_answers_applies_defaults(self) -> None:
        data = interview.load_interview(REPO_ROOT)
        with mock.patch.object(
            user_defaults,
            "load_defaults",
            return_value={"profile.selected": "lean"},
        ):
            draft = interview.prefill_answers(
                data,
                package_root=REPO_ROOT,
                partial={"setup.depth": "simple"},
            )
        self.assertEqual(draft["profile.selected"], "lean")
        self.assertEqual(draft["setup.depth"], "simple")


if __name__ == "__main__":
    unittest.main()
