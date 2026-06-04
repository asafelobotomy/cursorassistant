"""Repository policy checks for cursorAssistant surfaces."""

from __future__ import annotations

import json
import re
from pathlib import Path

# Legacy VS Code / Copilot tool names that must not appear in managed instructions.
FORBIDDEN_TOOL_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bvscode_", "VS Code tool prefix — use Cursor Agent tools"),
    (r"\bgrep_search\b", "use Grep or SemanticSearch"),
    (r"\bcodebase_search\b", "use SemanticSearch"),
    (r"\brun_terminal_cmd\b", "use Shell"),
    (r"\blist_dir\b", "use Glob or Read"),
    (r"\bedit_file\b", "use StrReplace or Write"),
    (r"\bsearch_replace\b", "use StrReplace"),
    (r"\bcreate_diagram\b", "use mermaid in prose or a canvas when appropriate"),
)

_COMPILED = tuple((re.compile(pat), hint) for pat, hint in FORBIDDEN_TOOL_PATTERNS)


def scan_markdown_surface(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    violations: list[dict[str, str]] = []
    for pattern, hint in _COMPILED:
        for match in pattern.finditer(text):
            line = text[: match.start()].count("\n") + 1
            violations.append(
                {
                    "path": str(path),
                    "line": str(line),
                    "match": match.group(0),
                    "hint": hint,
                }
            )
    return violations


def discover_skill_files(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    skills_root = repo_root / "skills"
    if skills_root.is_dir():
        paths.extend(sorted(skills_root.glob("*/SKILL.md")))
    paths.extend(sorted(repo_root.glob("packs/*/skills/*/SKILL.md")))
    return paths


def discover_agent_files(repo_root: Path) -> list[Path]:
    agents_root = repo_root / "agents"
    if not agents_root.is_dir():
        return []
    return sorted(agents_root.glob("*.md"))


def discover_rule_files(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for base in (repo_root / "template" / "rules", repo_root / ".cursor" / "rules"):
        if base.is_dir():
            paths.extend(sorted(base.glob("*.mdc")))
    return paths


def cmd_policy(repo_root: Path, fmt: str) -> int:
    skills = discover_skill_files(repo_root)
    agents = discover_agent_files(repo_root)
    rules = discover_rule_files(repo_root)
    violations: list[dict[str, str]] = []
    for path in skills + agents + rules:
        violations.extend(scan_markdown_surface(path))

    payload = {
        "ok": len(violations) == 0,
        "violations": violations,
        "skillsScanned": len(skills),
        "agentsScanned": len(agents),
        "rulesScanned": len(rules),
    }
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"policy: {len(skills)} skills, {len(agents)} agents, {len(rules)} rules scanned"
        )
        if violations:
            for row in violations:
                print(
                    f"  FAIL {row['path']}:{row['line']} "
                    f"{row['match']!r} — {row['hint']}"
                )
        else:
            print("  ok — no forbidden VS Code tool names")
    return 1 if violations else 0
