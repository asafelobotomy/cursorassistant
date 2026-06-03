"""Static analysis: check, tokens, coverage."""

from __future__ import annotations

import json
import re
from pathlib import Path

from tools.cursorEval._common import (
    TOKEN_BUDGET,
    count_tokens,
    discover_eval_files,
    parse_frontmatter,
    read_text,
)


def is_agent_path(path: Path) -> bool:
    return path.parent.name == "agents" and path.suffix == ".md"


def check_surface(path: Path) -> tuple[list[tuple[str, bool, str]], list[tuple[str, bool, str]]]:
    content = read_text(path)
    fm = parse_frontmatter(content)
    token_count = count_tokens(content)
    spec: list[tuple[str, bool, str]] = []
    advisory: list[tuple[str, bool, str]] = []

    name = fm.get("name", "")
    description = fm.get("description", "")
    spec.append(("spec-frontmatter", bool(fm), "frontmatter present"))
    spec.append(("spec-name", bool(name), f"name: {name!r}"))
    spec.append(("spec-description", bool(description), "description present"))
    spec.append(
        (
            "spec-token-budget",
            token_count <= TOKEN_BUDGET,
            f"token count {token_count:,} / {TOKEN_BUDGET:,}",
        )
    )

    if is_agent_path(path):
        spec.append(
            (
                "spec-filename-match",
                path.stem == name,
                f"filename {path.name!r} matches name",
            )
        )
        spec.append(
            (
                "spec-when-to-use",
                "## When to use" in content or "Your role:" in content,
                "use-case section present",
            )
        )
        spec.append(
            (
                "spec-when-not-to-use",
                "## When not to use" in content or "Do not use" in content,
                "exclusion guidance present",
            )
        )
    else:
        dir_name = path.parent.name
        spec.append(
            (
                "spec-dir-match",
                name == dir_name,
                f"skill name matches directory ({dir_name!r})",
            )
        )
        spec.append(("spec-when-to-use", "## When to use" in content, "## When to use present"))
        spec.append(
            (
                "spec-when-not-to-use",
                "## When not to use" in content or "## When NOT to use" in content,
                "When not to use present",
            )
        )

    advisory.append(
        (
            "description-length",
            len(description) >= 20,
            f"description length {len(description)} (min 20)",
        )
    )
    return spec, advisory


def cmd_check(path: str, fmt: str) -> int:
    target = Path(path)
    spec, advisory = check_surface(target)
    failed = [row for row in spec if not row[1]]
    payload = {
        "path": str(target),
        "spec": [{"id": i, "passed": p, "detail": d} for i, p, d in spec],
        "advisory": [{"id": i, "passed": p, "detail": d} for i, p, d in advisory],
        "ok": len(failed) == 0,
    }
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"cursorEval check — {target.name}")
        for item_id, passed, detail in spec:
            mark = "ok" if passed else "FAIL"
            print(f"  [{mark}] {item_id}: {detail}")
        for item_id, passed, detail in advisory:
            mark = "ok" if passed else "warn"
            print(f"  [{mark}] {item_id}: {detail}")
    return 1 if failed else 0


def cmd_tokens(path: str, fmt: str) -> int:
    content = read_text(path)
    token_count = count_tokens(content)
    sections = len(re.findall(r"^#{1,6} ", content, re.MULTILINE))
    payload = {
        "token_count": token_count,
        "token_budget": TOKEN_BUDGET,
        "sections": sections,
    }
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        flag = "ok" if token_count <= TOKEN_BUDGET else "over"
        print(f"tokens: {token_count:,} ({flag}, budget {TOKEN_BUDGET:,}), sections: {sections}")
    return 0


def cmd_coverage(repo_root: Path, fmt: str) -> int:
    skills = sorted((repo_root / "skills").glob("*/SKILL.md"))
    pack_skills = sorted(repo_root.glob("packs/*/skills/*/SKILL.md"))
    agents = sorted((repo_root / "agents").glob("*.md"))
    eval_index = {p.parent.name: p for p in discover_eval_files(repo_root)}

    rows: list[dict] = []
    for skill in skills + pack_skills:
        skill_id = skill.parent.name
        eval_path = eval_index.get(skill_id)
        rows.append(
            {
                "kind": "skill",
                "id": skill_id,
                "path": str(skill.relative_to(repo_root)),
                "eval": str(eval_path.relative_to(repo_root)) if eval_path else None,
                "covered": eval_path is not None,
            }
        )
    for agent in agents:
        agent_id = agent.stem
        eval_path = eval_index.get(agent_id)
        rows.append(
            {
                "kind": "agent",
                "id": agent_id,
                "path": str(agent.relative_to(repo_root)),
                "eval": str(eval_path.relative_to(repo_root)) if eval_path else None,
                "covered": eval_path is not None,
            }
        )
    covered = sum(1 for r in rows if r["covered"])
    payload = {"total": len(rows), "covered": covered, "rows": rows}
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"coverage: {covered}/{len(rows)} surfaces have eval suites")
        for row in rows:
            mark = "yes" if row["covered"] else "no"
            print(f"  [{mark}] {row['kind']}:{row['id']}")
    return 0
