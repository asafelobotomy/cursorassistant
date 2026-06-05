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
            self.assertTrue(report["interviewRequired"])
            self.assertFalse(report["lockfilePresent"])
            self.assertEqual(report["selectedPacks"], [])

    def test_inspect_interview_required_without_answers_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            answers_path = workspace / ".cursor/cursor-assistant-answers.json"
            answers_path.unlink()
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertTrue(report["interviewRequired"])

    def test_inspect_interview_not_required_after_setup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertFalse(report["interviewRequired"])

    def test_update_requires_answers_when_interview_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            (workspace / ".cursor/cursor-assistant-answers.json").unlink()
            with self.assertRaises(ValueError) as ctx:
                engine.update(workspace, REPO_ROOT)
            self.assertIn("interview_required", str(ctx.exception))

    def test_setup_writes_lockfile_and_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            result = engine.setup(workspace, REPO_ROOT)
            self.assertIn("routing.agents-md", result["written"])
            self.assertTrue((workspace / "AGENTS.md").is_file())
            self.assertTrue((workspace / ".cursor/agents/inventory.md").is_file())
            self.assertFalse((workspace / ".cursor/agents/explore.md").exists())
            self.assertTrue((workspace / ".cursor/mcp/scripts/cursorToolsMcp.py").is_file())
            lock = json.loads((workspace / ".cursor/cursorAssistant-lock.json").read_text())
            self.assertEqual(lock["package"]["name"], "cursorAssistant")
            self.assertEqual(lock["schemaVersion"], "0.5.0")
            self.assertEqual(lock["profile"], "balanced")
            self.assertEqual(lock["selectedPacks"], [])
            self.assertFalse(lock["mcpEnabled"])

    def test_lockfile_package_root_is_dot_when_workspace_equals_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(engine.lockfile_package_root(root, root), ".")
        self.assertEqual(engine.lockfile_package_root(REPO_ROOT, REPO_ROOT), ".")

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
            agent = workspace / ".cursor/agents/inventory.md"
            agent.write_text(agent.read_text() + "\n# stale\n", encoding="utf-8")
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertEqual(report["installState"], "needs-update")
            stale = [f for f in report["files"] if f["status"] == "stale"]
            self.assertTrue(any(row["id"] == "agents.inventory" for row in stale))

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
            engine.setup(
                workspace,
                REPO_ROOT,
                answers={"mcp.enabled": True},
            )
            mcp_path = workspace / ".cursor/mcp.json"
            mcp_path.write_text(
                json.dumps({"mcpServers": {"custom": {"command": "echo"}}}, indent=2) + "\n",
                encoding="utf-8",
            )
            engine.update(workspace, REPO_ROOT)
            payload = json.loads(mcp_path.read_text(encoding="utf-8"))
            self.assertIn("custom", payload["mcpServers"])
            self.assertIn("cursorTools", payload["mcpServers"])
            self.assertNotIn("git", payload["mcpServers"])
            self.assertNotIn("web", payload["mcpServers"])

    def test_repair_fixes_missing_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            (workspace / ".cursor/agents/inventory.md").unlink()
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertIn("incomplete-install", report["repairReasons"])
            result = engine.repair(workspace, REPO_ROOT)
            self.assertIn("agents.inventory", result["written"])
            self.assertTrue((workspace / ".cursor/agents/inventory.md").is_file())

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
            agent = workspace / ".cursor/agents/inventory.md"
            agent.write_text("# customized\n", encoding="utf-8")
            result = engine.factory_restore(workspace, REPO_ROOT)
            self.assertIn("agents.inventory", result["written"])
            self.assertNotEqual(agent.read_text(), "# customized\n")

    def test_pack_registry_lists_active_packs(self) -> None:
        registry = packs.load_pack_registry(REPO_ROOT)
        active = packs.active_pack_ids(registry)
        self.assertEqual(active, {"lean", "secure", "tdd"})

    def test_core_policy_includes_eleven_agents(self) -> None:
        policy_path = REPO_ROOT / "template/setup/install-policy.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        agent_ids = [
            entry["id"]
            for entry in policy["entries"]
            if entry["id"].startswith("agents.")
        ]
        skill_ids = [
            entry["id"]
            for entry in policy["entries"]
            if entry["id"].startswith("skills.")
        ]
        self.assertEqual(len(agent_ids), 11)
        self.assertIn("skills.task-triage", skill_ids)
        self.assertNotIn("agents.triage", agent_ids)
        for name in (
            "inventory",
            "researcher",
            "organise",
            "cleaner",
        ):
            self.assertIn(f"agents.{name}", agent_ids)
        self.assertNotIn("agents.explore", agent_ids)

    def test_explore_agent_source_removed(self) -> None:
        self.assertFalse((REPO_ROOT / "agents/explore.md").exists())
        self.assertTrue((REPO_ROOT / "agents/inventory.md").is_file())

    def test_dogfood_install_complete(self) -> None:
        lock = REPO_ROOT / ".cursor/cursorAssistant-lock.json"
        if not lock.is_file():
            self.skipTest("dogfood lockfile not present")
        report = engine.inspect(REPO_ROOT, REPO_ROOT)
        missing = [f["id"] for f in report.get("files", []) if f.get("status") == "missing"]
        stale = [f["id"] for f in report.get("files", []) if f.get("status") == "stale"]
        self.assertEqual(report.get("installState"), "installed", report)
        self.assertEqual(missing, [], f"missing managed files: {missing}")
        self.assertEqual(stale, [], f"stale managed files: {stale}")
        self.assertTrue(
            (REPO_ROOT / ".cursor/mcp/scripts/_cursor_workspace.py").is_file(),
            "dogfood must install vendored workspace helper",
        )


if __name__ == "__main__":
    unittest.main()
