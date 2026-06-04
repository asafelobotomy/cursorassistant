"""Static analysis: check, tokens, coverage, suggest."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tools.cursorEval._common import (
    TOKEN_BUDGET,
    count_tokens,
    discover_eval_files,
    load_yaml,
    max_nesting_depth,
    parse_frontmatter,
    read_text,
    yaml_quote,
)

ALLOWED_SKILL_FIELDS = frozenset(
    {
        "name",
        "description",
        "type",
        "version",
        "license",
        "metadata",
        "tags",
        "compatibility",
        "authors",
    }
)
ALLOWED_AGENT_FIELDS = frozenset({"name", "description", "model", "readonly", "is_background"})
_PROCEDURAL_DESC = re.compile(
    r"\b(use when|when to use|when:|triggers?:|how to|step \d|invoke|dispatch|run this)",
    re.IGNORECASE,
)


def is_agent_path(path: Path) -> bool:
    return path.parent.name == "agents" and path.suffix == ".md"


def find_repo_root_for_surface(path: Path) -> Path:
    current = path.resolve()
    for _ in range(12):
        if (current / "cursorAssistant.py").is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return path.resolve().parents[2] if len(path.resolve().parents) > 2 else path.resolve()


def _check_agent_items(
    path: Path, content: str, fm: dict[str, str], token_count: int
) -> tuple[list[tuple[str, bool, str]], list[tuple[str, bool, str]]]:
    spec: list[tuple[str, bool, str]] = []
    advisory: list[tuple[str, bool, str]] = []
    name = fm.get("name", "")

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
            "## When to use" in content or "You are the" in content,
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
    numbered = re.findall(r"^\s*\d+\. ", content, re.MULTILINE)
    advisory.append(
        (
            "spec-workflow-steps",
            len(numbered) >= 2,
            f"numbered workflow steps: {len(numbered)} (minimum 2 recommended)",
        )
    )
    unknown = set(fm.keys()) - ALLOWED_AGENT_FIELDS
    advisory.append(
        (
            "spec-allowed-fields",
            not unknown,
            f"unknown frontmatter fields: {sorted(unknown)}" if unknown else "all fields allowed",
        )
    )
    advisory.append(
        (
            "procedural-content",
            bool(_PROCEDURAL_DESC.search(fm.get("description", ""))),
            "description contains procedural trigger language",
        )
    )
    return spec, advisory


def _check_skill_items(
    path: Path, content: str, fm: dict[str, str], token_count: int
) -> tuple[list[tuple[str, bool, str]], list[tuple[str, bool, str]]]:
    spec: list[tuple[str, bool, str]] = []
    advisory: list[tuple[str, bool, str]] = []
    name = fm.get("name", "")
    dir_name = path.parent.name
    is_reference = fm.get("type", "") == "reference"

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
    has_steps = "## Steps" in content or bool(re.search(r"^## Module \d+", content, re.MULTILINE))
    advisory.append(
        (
            "spec-steps-or-modules",
            has_steps or is_reference,
            "workflow structure present (## Steps or ## Module N)",
        )
    )
    advisory.append(
        (
            "spec-verify",
            "## Verify" in content,
            "## Verify checklist present",
        )
    )
    unknown = set(fm.keys()) - ALLOWED_SKILL_FIELDS
    has_version = bool(fm.get("version")) or "version:" in content.split("---\n", 2)[1]
    advisory.extend(
        [
            (
                "spec-version",
                has_version,
                "version field present in frontmatter",
            ),
            (
                "spec-license",
                bool(fm.get("license")),
                "license field present",
            ),
            (
                "spec-allowed-fields",
                not unknown,
                f"unknown frontmatter fields: {sorted(unknown)}"
                if unknown
                else "all fields allowed",
            ),
            (
                "procedural-content",
                bool(_PROCEDURAL_DESC.search(fm.get("description", ""))),
                "description contains procedural trigger language",
            ),
        ]
    )
    modules = re.findall(r"^## Module \d+", content, re.MULTILINE)
    mc = len(modules)
    advisory.append(
        (
            "module-count",
            is_reference or (mc == 0 and "## Steps" in content) or 2 <= mc <= 6,
            f"module count: {mc} (2–6 recommended when using modules)",
        )
    )
    return spec, advisory


def check_surface(path: Path) -> tuple[list[tuple[str, bool, str]], list[tuple[str, bool, str]], str]:
    content = read_text(path)
    fm = parse_frontmatter(content)
    token_count = count_tokens(content)
    spec: list[tuple[str, bool, str]] = []
    advisory: list[tuple[str, bool, str]] = []

    name = fm.get("name", "")
    description = fm.get("description", "")
    spec.extend(
        [
            ("spec-frontmatter", bool(fm), "frontmatter present"),
            ("spec-name", bool(name), f"name: {name!r}"),
            ("spec-description", bool(description), "description present"),
            (
                "spec-token-budget",
                token_count <= TOKEN_BUDGET,
                f"token count {token_count:,} / {TOKEN_BUDGET:,}",
            ),
        ]
    )

    if is_agent_path(path):
        type_spec, type_adv = _check_agent_items(path, content, fm, token_count)
    else:
        type_spec, type_adv = _check_skill_items(path, content, fm, token_count)
    spec.extend(type_spec)
    advisory.extend(type_adv)

    advisory.append(
        (
            "description-length",
            len(description) >= 20,
            f"description length {len(description)} (min 20)",
        )
    )
    depth = max_nesting_depth(content)
    advisory.append(
        (
            "complexity",
            depth <= 3,
            f"max list nesting depth {depth} (threshold 3)",
        )
    )

    repo_root = find_repo_root_for_surface(path)
    surface_id = path.stem if is_agent_path(path) else path.parent.name
    eval_path = repo_root / "evals" / surface_id / "eval.yaml"
    pack_eval = list(repo_root.glob(f"packs/*/evals/{surface_id}/eval.yaml"))
    found = eval_path.is_file() or bool(pack_eval)
    loc = (
        str(eval_path.relative_to(repo_root))
        if eval_path.is_file()
        else (str(pack_eval[0].relative_to(repo_root)) if pack_eval else f"evals/{surface_id}/eval.yaml")
    )
    advisory.append(
        (
            "eval-presence",
            found,
            f"eval suite: {loc}" if found else f"eval suite missing (expected evals/{surface_id}/)",
        )
    )

    spec_score = sum(1 for _, ok, _ in spec if ok) / len(spec) if spec else 0.0
    adv_score = sum(1 for _, ok, _ in advisory if ok) / len(advisory) if advisory else 0.0
    weight = spec_score * 0.7 + adv_score * 0.3
    if weight >= 0.90:
        level = "High"
    elif weight >= 0.75:
        level = "Medium-High"
    elif weight >= 0.50:
        level = "Medium"
    else:
        level = "Low"
    return spec, advisory, level


def cmd_check(path: str, fmt: str) -> int:
    target = Path(path)
    spec, advisory, level = check_surface(target)
    failed = [row for row in spec if not row[1]]
    payload = {
        "path": str(target),
        "compliance": level,
        "spec": [{"id": i, "passed": p, "detail": d} for i, p, d in spec],
        "advisory": [{"id": i, "passed": p, "detail": d} for i, p, d in advisory],
        "ok": len(failed) == 0,
    }
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"cursorEval check — {target.name} (compliance: {level})")
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
    fences = re.findall(r"^```", content, re.MULTILINE)
    code_blocks = len(fences) // 2
    numbered = re.findall(r"^\s*\d+\. ", content, re.MULTILINE)
    workflow_detected = len(numbered) >= 3
    depth = max_nesting_depth(content)
    payload = {
        "token_count": token_count,
        "token_budget": TOKEN_BUDGET,
        "within_budget": token_count <= TOKEN_BUDGET,
        "sections": sections,
        "code_blocks": code_blocks,
        "workflow_steps_detected": workflow_detected,
        "max_nesting_depth": depth,
    }
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        flag = "ok" if token_count <= TOKEN_BUDGET else "over"
        wf = "yes" if workflow_detected else "no"
        print(
            f"tokens — {Path(path).name}: {token_count:,} ({flag}, budget {TOKEN_BUDGET:,}), "
            f"sections={sections}, code_blocks={code_blocks}, workflow_steps={wf}, "
            f"max_nesting_depth={depth}"
        )
    return 0


def _analyze_eval_suite(eval_path: Path | None) -> dict:
    if eval_path is None or not eval_path.is_file():
        return {
            "level": "missing",
            "graderTypes": [],
            "graderCount": 0,
            "taskCount": 0,
            "hasNegativeTrigger": False,
            "hasSecondPositive": False,
            "blockingIssues": ["no eval.yaml"],
            "advisoryIssues": [],
            "issues": ["no eval.yaml"],
        }
    issues: list[str] = []
    try:
        spec = load_yaml(eval_path)
    except (ValueError, SystemExit):
        return {
            "level": "partial",
            "graderTypes": [],
            "graderCount": 0,
            "taskCount": 0,
            "hasNegativeTrigger": False,
            "hasSecondPositive": False,
            "blockingIssues": ["eval.yaml unreadable"],
            "advisoryIssues": [],
            "issues": ["eval.yaml unreadable"],
        }

    eval_dir = eval_path.parent
    graders = spec.get("graders") or []
    grader_types = sorted(
        {str(g.get("type", "text")) for g in graders if isinstance(g, dict)}
    )
    grader_count = len(grader_types)
    tasks = list((eval_dir / "tasks").glob("*.yaml")) if (eval_dir / "tasks").is_dir() else []
    task_names = {t.stem for t in tasks}
    has_negative = "negative-trigger-1" in task_names
    has_pos2 = "positive-trigger-2" in task_names
    if not tasks:
        issues.append("no task files")
    if grader_count < 2:
        issues.append(f"fewer than 2 grader types ({grader_count})")
    if not has_negative:
        issues.append("missing tasks/negative-trigger-1.yaml")
    if not has_pos2:
        issues.append("missing tasks/positive-trigger-2.yaml (recommended)")

    blocking = [
        i
        for i in issues
        if i.startswith(("no task", "fewer than 2", "missing tasks/negative"))
        or i == "eval.yaml unreadable"
    ]
    advisory = [i for i in issues if i not in blocking]

    if not tasks or grader_count < 2 or not has_negative:
        level = "partial"
    elif advisory:
        level = "partial"
    else:
        level = "full"

    return {
        "level": level,
        "graderTypes": grader_types,
        "graderCount": grader_count,
        "taskCount": len(tasks),
        "hasNegativeTrigger": has_negative,
        "hasSecondPositive": has_pos2,
        "blockingIssues": blocking,
        "advisoryIssues": advisory,
        "issues": issues if level != "full" else [],
    }


def cmd_coverage(repo_root: Path, fmt: str, strict: bool) -> int:
    repo_root = repo_root.resolve()
    skills = sorted((repo_root / "skills").glob("*/SKILL.md"))
    pack_skills = sorted(repo_root.glob("packs/*/skills/*/SKILL.md"))
    agents = sorted((repo_root / "agents").glob("*.md"))
    eval_index = {p.parent.name: p for p in discover_eval_files(repo_root)}

    rows: list[dict] = []
    for skill in skills + pack_skills:
        skill_id = skill.parent.name
        if skill_id in eval_index:
            eval_path = eval_index[skill_id]
        else:
            pack_candidate = next(
                repo_root.glob(f"packs/*/evals/{skill_id}/eval.yaml"), None
            )
            eval_path = pack_candidate
        analysis = _analyze_eval_suite(eval_path)
        rows.append(
            {
                "kind": "skill",
                "id": skill_id,
                "path": str(skill.relative_to(repo_root)),
                "eval": str(eval_path.relative_to(repo_root)) if eval_path else None,
                **analysis,
            }
        )
    for agent in agents:
        agent_id = agent.stem
        eval_path = eval_index.get(agent_id)
        analysis = _analyze_eval_suite(eval_path)
        rows.append(
            {
                "kind": "agent",
                "id": agent_id,
                "path": str(agent.relative_to(repo_root)),
                "eval": str(eval_path.relative_to(repo_root)) if eval_path else None,
                **analysis,
            }
        )

    full = sum(1 for r in rows if r["level"] == "full")
    partial = sum(1 for r in rows if r["level"] == "partial")
    missing = sum(1 for r in rows if r["level"] == "missing")
    payload = {
        "total": len(rows),
        "full": full,
        "partial": partial,
        "missing": missing,
        "rows": rows,
    }
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(
            f"coverage: {full} full, {partial} partial, {missing} missing "
            f"(of {len(rows)} surfaces)"
        )
        for row in rows:
            issues = row.get("issues") or []
            suffix = f" — {', '.join(issues)}" if issues else ""
            print(f"  [{row['level']}] {row['kind']}:{row['id']}{suffix}")

    if strict:
        blockers = sum(
            1
            for r in rows
            if r["level"] == "missing" or (r.get("blockingIssues") or [])
        )
        if blockers:
            if fmt != "json":
                print(
                    f"coverage --strict: {blockers} surface(s) with missing eval or blocking gaps",
                    file=sys.stderr,
                )
            return 1
    return 0


def cmd_suggest(path: str, apply: bool, fmt: str) -> int:
    target = Path(path).resolve()
    content = read_text(target)
    fm = parse_frontmatter(content)
    name = fm.get("name") or (target.stem if is_agent_path(target) else target.parent.name)
    description = fm.get("description", "")
    is_agent = is_agent_path(target)

    if not name or "/" in name or "\\" in name or name.startswith("."):
        print(f"cursorEval suggest: unsafe or empty name {name!r}", file=sys.stderr)
        return 2

    desc_short = (description[:100] + "...") if len(description) > 100 else description
    kind = "agent" if is_agent else "skill"
    name_pat = "(?i)(" + re.escape(name) + "|" + kind + ")"

    eval_yaml = (
        f"name: {yaml_quote(name + '-eval')}\n"
        f"description: {yaml_quote(f'Evaluates {name} {kind} routing and behaviour')}\n\n"
        f"config:\n"
        f"  trials_per_task: 1\n"
        f"  inject_skill_body: true\n"
        f"  max_attempts: 1\n\n"
        f"graders:\n"
        f"  - type: text\n"
        f"    name: references_{kind}\n"
        f"    config:\n"
        f"      pattern: {yaml_quote(name_pat)}\n\n"
        f"  - type: behavior\n"
        f"    name: completion_bound\n"
        f"    config:\n"
        f"      max_tokens: 2000\n\n"
        f"tasks:\n  - {yaml_quote('tasks/*.yaml')}\n"
    )
    positive_1 = (
        f"id: positive-trigger-1\n"
        f"description: {yaml_quote(f'Verify {name} triggers on primary use case')}\n"
        f"prompt: |\n  {desc_short}\n"
        f"expected:\n  - {yaml_quote(name)}\n"
        f"tags:\n  - smoke\n  - positive\n"
    )
    positive_2 = (
        f"id: positive-trigger-2\n"
        f"description: {yaml_quote(f'Second positive trigger variant for {name}')}\n"
        f"prompt: |\n  When should {name} be used in a cursorAssistant workspace?\n"
        f"expected:\n  - {yaml_quote(name)}\n"
        f"tags:\n  - smoke\n  - positive\n"
    )
    negative_1 = (
        f"id: negative-trigger-1\n"
        f"description: {yaml_quote(f'Unrelated request must not invoke {name}')}\n"
        f"prompt: |\n  What is the current time? Use {name}.\n"
        f"expected_absent:\n  - {yaml_quote('(?i)' + re.escape(name))}\n"
        f"tags:\n  - smoke\n  - negative\n"
    )

    repo_root = find_repo_root_for_surface(target)
    eval_dir = repo_root / "evals" / name

    files = {
        eval_dir / "eval.yaml": eval_yaml,
        eval_dir / "tasks" / "positive-trigger-1.yaml": positive_1,
        eval_dir / "tasks" / "positive-trigger-2.yaml": positive_2,
        eval_dir / "tasks" / "negative-trigger-1.yaml": negative_1,
    }

    if not apply:
        payload = {
            "dryRun": True,
            "evalDir": str(eval_dir.relative_to(repo_root)),
            "files": {str(k.relative_to(repo_root)): v for k, v in files.items()},
        }
        if fmt == "json":
            print(json.dumps(payload, indent=2))
        else:
            print(f"cursorEval suggest — dry-run for {target.name}")
            print(f"  would write: {eval_dir.relative_to(repo_root)}/")
            for rel in files:
                print(f"    {rel.relative_to(repo_root)}")
        return 0

    if eval_dir.exists() and any(eval_dir.iterdir()):
        print(
            f"cursorEval suggest: {eval_dir} already exists; remove it or scaffold manually",
            file=sys.stderr,
        )
        return 1

    try:
        for fp, body in files.items():
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(body, encoding="utf-8")
    except OSError as exc:
        print(f"cursorEval suggest: cannot write files: {exc}", file=sys.stderr)
        return 2

    if fmt == "json":
        print(json.dumps({"written": str(eval_dir.relative_to(repo_root))}, indent=2))
    else:
        for fp in files:
            print(f"Written: {fp.relative_to(repo_root)}")
    return 0
