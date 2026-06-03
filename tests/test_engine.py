"""Tests for cursorAssistant lifecycle engine."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lifecycle import engine, merge, packs

REPO_ROOT = Path(__file__).resolve().parents[1]


class EngineTests(unittest.TestCase):
    def test_inspect_not_installed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertEqual(report["installState"], "not-installed")
            self.assertFalse(report["lockfilePresent"])
            self.assertEqual(report["selectedPacks"], [])

    def test_setup_writes_lockfile_and_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            result = engine.setup(workspace, REPO_ROOT)
            self.assertIn("routing.agents-md", result["written"])
            self.assertTrue((workspace / "AGENTS.md").is_file())
            self.assertTrue((workspace / ".cursor/agents/explore.md").is_file())
            self.assertTrue((workspace / ".cursor/mcp/scripts/cursorToolsMcp.py").is_file())
            lock = json.loads((workspace / ".cursor/cursorAssistant-lock.json").read_text())
            self.assertEqual(lock["package"]["name"], "cursorAssistant")
            self.assertEqual(lock["schemaVersion"], "0.4.0")
            self.assertEqual(lock["profile"], "balanced")
            self.assertEqual(lock["selectedPacks"], [])
            self.assertTrue(lock["mcpEnabled"])

    def test_setup_mcp_disabled_skips_bundle_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            result = engine.setup(
                workspace,
                REPO_ROOT,
                answers={"mcp.enabled": False},
            )
            self.assertIn("mcp.cursorToolsMcp", result["written"])
            self.assertNotIn("mcp.gitMcp", result["written"])
            self.assertFalse((workspace / ".cursor/mcp/scripts/gitMcp.py").exists())
            mcp = json.loads((workspace / ".cursor/mcp.json").read_text())
            self.assertIn("cursorTools", mcp["mcpServers"])
            self.assertNotIn("git", mcp["mcpServers"])

    def test_setup_with_lean_profile_installs_lean_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            result = engine.setup(
                workspace,
                REPO_ROOT,
                answers={"profile.selected": "lean"},
            )
            self.assertIn("packs.lean.leanOutput", result["written"])
            self.assertTrue((workspace / ".cursor/skills/leanOutput/SKILL.md").is_file())
            lock = json.loads((workspace / ".cursor/cursorAssistant-lock.json").read_text())
            self.assertEqual(lock["selectedPacks"], ["lean"])

    def test_setup_with_explicit_secure_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(
                workspace,
                REPO_ROOT,
                answers={"profile.selected": "balanced", "packs.selected": ["secure"]},
            )
            self.assertTrue((workspace / ".cursor/skills/secureReview/SKILL.md").is_file())
            self.assertFalse((workspace / ".cursor/skills/leanOutput/SKILL.md").exists())

    def test_prune_deselected_pack_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(
                workspace,
                REPO_ROOT,
                answers={"packs.selected": ["tdd"]},
            )
            self.assertTrue((workspace / ".cursor/skills/tddCycle/SKILL.md").is_file())
            engine.setup(
                workspace,
                REPO_ROOT,
                answers={"packs.selected": []},
            )
            self.assertFalse((workspace / ".cursor/skills/tddCycle/SKILL.md").exists())

    def test_update_skips_clean_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            result = engine.update(workspace, REPO_ROOT)
            self.assertEqual(result["written"], [])
            self.assertGreater(len(result["skipped"]), 0)

    def test_inspect_detects_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            agent = workspace / ".cursor/agents/explore.md"
            agent.write_text(agent.read_text() + "\n# stale\n", encoding="utf-8")
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertEqual(report["installState"], "needs-update")
            stale = [f for f in report["files"] if f["status"] == "stale"]
            self.assertTrue(any(row["id"] == "agents.explore" for row in stale))

    def test_merge_preserves_user_added_agents_block(self) -> None:
        source = "# Routing\n\nDefault content.\n"
        existing = (
            "# Routing\n\nOld content.\n\n"
            "<!-- user-added -->\n## Custom agents\n\nMy team routes.\n<!-- /user-added -->\n"
        )
        merged = merge.merge_markdown_with_preserved_blocks(existing, source)
        self.assertIn("Default content.", merged)
        self.assertIn("## Custom agents", merged)
        self.assertIn("My team routes.", merged)

    def test_merge_json_mcp_servers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            mcp_path = workspace / ".cursor/mcp.json"
            mcp_path.write_text(
                json.dumps({"mcpServers": {"custom": {"command": "echo"}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            engine.update(workspace, REPO_ROOT)
            payload = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertIn("custom", payload["mcpServers"])
            self.assertIn("cursorTools", payload["mcpServers"])
            self.assertIn("git", payload["mcpServers"])

    def test_repair_fixes_missing_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            (workspace / ".cursor/agents/explore.md").unlink()
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertIn("incomplete-install", report["repairReasons"])
            result = engine.repair(workspace, REPO_ROOT)
            self.assertIn("agents.explore", result["written"])
            self.assertTrue((workspace / ".cursor/agents/explore.md").is_file())

    def test_plan_setup_lists_would_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            plan = engine.plan_setup(workspace, REPO_ROOT)
            self.assertEqual(plan["command"], "plan-setup")
            self.assertGreater(len(plan["wouldWrite"]), 0)

    def test_factory_restore_rewrites_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            agent = workspace / ".cursor/agents/explore.md"
            agent.write_text("# customized\n", encoding="utf-8")
            result = engine.factory_restore(workspace, REPO_ROOT)
            self.assertIn("agents.explore", result["written"])
            self.assertNotEqual(agent.read_text(), "# customized\n")

    def test_pack_registry_lists_active_packs(self) -> None:
        registry = packs.load_pack_registry(REPO_ROOT)
        active = packs.active_pack_ids(registry)
        self.assertEqual(active, {"lean", "secure", "tdd"})


if __name__ == "__main__":
    unittest.main()
