"""Repository policy checks for cursorAssistant surfaces."""

from __future__ import annotations

import json
import re
from pathlib import Path

# Legacy VS Code / Copilot tool names that must not appear in skills.
FORBIDDEN_SKILL_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bvscode_", "VS Code tool prefix — use Cursor Agent tools"),
    (r"\bgrep_search\b", "use Grep or SemanticSearch"),
    (r"\bcodebase_search\b", "use SemanticSearch"),
    (r"\brun_terminal_cmd\b", "use Shell"),
    (r"\blist_dir\b", "use Glob or Read"),
    (r"\bedit_file\b", "use StrReplace or Write"),
    (r"\bsearch_replace\b", "use StrReplace"),
    (r"\bcreate_diagram\b", "use mermaid in prose or a canvas when appropriate"),
)

_COMPILED = tuple((re.compile(pat), hint) for pat, hint in FORBIDDEN_SKILL_PATTERNS)


def scan_skill_file(path: Path) -> list[dict[str, str]]:
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
    for base in (repo_root / "skills",):
        if base.is_dir():
            paths.extend(sorted(base.glob("*/SKILL.md")))
    for pack_skill in sorted(repo_root.glob("packs/*/skills/*/SKILL.md")):
        paths.append(pack_skill)
    return paths


def cmd_policy(repo_root: Path, fmt: str) -> int:
    violations: list[dict[str, str]] = []
    for skill in discover_skill_files(repo_root):
        violations.extend(scan_skill_file(skill))

    payload = {
        "ok": len(violations) == 0,
        "violations": violations,
        "skillsScanned": len(discover_skill_files(repo_root)),
    }
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"policy: {payload['skillsScanned']} skills scanned")
        if violations:
            for row in violations:
                print(
                    f"  FAIL {row['path']}:{row['line']} "
                    f"{row['match']!r} — {row['hint']}"
                )
        else:
            print("  ok — no forbidden VS Code tool names in skills")
    return 1 if violations else 0
