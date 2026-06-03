"""Tests for layered MCP configuration."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.lifecycle import engine, mcp_config

REPO_ROOT = Path(__file__).resolve().parents[1]


class McpConfigTests(unittest.TestCase):
    def test_core_only_by_default(self) -> None:
        payload = mcp_config.build_mcp_config(REPO_ROOT, {"mcp.enabled": False}, [], {})
        servers = set(payload["mcpServers"].keys())
        self.assertEqual(servers, {"cursorTools"})
        self.assertFalse(servers & mcp_config.DEPRECATED_SERVER_KEYS)

    def test_extensions_when_enabled(self) -> None:
        payload = mcp_config.build_mcp_config(REPO_ROOT, {"mcp.enabled": True}, [], {})
        servers = set(payload["mcpServers"].keys())
        self.assertTrue({"cursorTools", "git", "devDocs", "memory"}.issubset(servers))
        self.assertFalse(mcp_config.DEPRECATED_SERVER_KEYS & servers)

    def test_secure_pack_adds_security(self) -> None:
        payload = mcp_config.build_mcp_config(
            REPO_ROOT,
            {"mcp.enabled": False},
            ["secure"],
            {},
        )
        self.assertIn("security", payload["mcpServers"])
        self.assertIn("secureOsv", payload["mcpServers"])

    def test_mcp_warnings_detect_legacy_servers(self) -> None:
        legacy = {"mcpServers": {"web": {"command": "echo"}, "cursorTools": {"command": "echo"}}}
        warnings = mcp_config.mcp_warnings(legacy)
        self.assertTrue(any("deprecated-mcp-server:web" in w for w in warnings))

    def test_setup_secure_pack_installs_pack_mcp_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(
                workspace,
                REPO_ROOT,
                answers={"packs.selected": ["secure"], "mcp.enabled": False},
            )
            self.assertTrue((workspace / ".cursor/mcp/scripts/securityMcp.py").is_file())
            self.assertTrue((workspace / ".cursor/mcp/scripts/secureOsv.py").is_file())
            mcp = json.loads((workspace / ".cursor/mcp.json").read_text(encoding="utf-8"))
            self.assertIn("security", mcp["mcpServers"])
            self.assertNotIn("web", mcp["mcpServers"])

    def test_inspect_reports_deprecated_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            engine.setup(workspace, REPO_ROOT)
            scripts = workspace / ".cursor/mcp/scripts"
            scripts.mkdir(parents=True, exist_ok=True)
            (scripts / "webMcp.py").write_text("# legacy\n", encoding="utf-8")
            report = engine.inspect(workspace, REPO_ROOT)
            self.assertTrue(
                any("deprecated-mcp-script:webMcp.py" in w for w in report.get("mcpWarnings", []))
            )


if __name__ == "__main__":
    unittest.main()
