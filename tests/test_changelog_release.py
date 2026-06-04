"""Tests for CHANGELOG release helper."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import changelog_release as cr


class ChangelogReleaseTests(unittest.TestCase):
    def test_parse_and_extract(self) -> None:
        content = """# Changelog

## [Unreleased]

## [1.2.3] - 2026-01-15

### Added
- Widget

## [1.2.2] - 2026-01-01

### Fixed
- Bug
"""
        sections = cr.parse_sections(content)
        self.assertEqual(sections["1.2.3"], "### Added\n- Widget")
        self.assertNotIn("Unreleased", sections)

    def test_section_for_version_from_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHANGELOG.md"
            path.write_text(
                "## [Unreleased]\n\n## [0.1.0] - 2026-06-01\n\n### Added\n- Alpha\n",
                encoding="utf-8",
            )
            body = cr.section_for_version("0.1.0", path)
            self.assertIn("Alpha", body)

    def test_verify_missing_section_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHANGELOG.md"
            path.write_text("## [Unreleased]\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                cr.section_for_version("9.9.9", path)


if __name__ == "__main__":
    unittest.main()
