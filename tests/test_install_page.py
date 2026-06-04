"""Install page generator stays aligned with VERSION."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _run_generate() -> None:
    path = REPO / "scripts" / "generate_install_page.py"
    spec = importlib.util.spec_from_file_location("generate_install_page", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


class TestInstallPage(unittest.TestCase):
    def test_generate_pins_version_in_deeplink(self) -> None:
        version = (REPO / "VERSION").read_text(encoding="utf-8").strip().splitlines()[0]
        _run_generate()
        deeplinks = json.loads((REPO / "install/deeplinks.json").read_text(encoding="utf-8"))
        self.assertEqual(deeplinks["version"], version)
        self.assertIn(f"v{version}", deeplinks["bootstrapGit"])
        html = (REPO / "install/index.html").read_text(encoding="utf-8")
        self.assertIn(f"Version <strong>{version}</strong>", html)
        self.assertNotIn("v0.12.1", deeplinks["mcpCombined"])


if __name__ == "__main__":
    unittest.main()
