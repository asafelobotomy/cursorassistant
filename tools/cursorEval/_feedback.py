"""LLM improvement loop: quality and dev commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tools.cursorEval._model import DEFAULT_MODEL, call_model, get_token
from tools.cursorEval._common import extract_first_json_object, read_text

QUALITY_DIMENSIONS = (
    "clarity",
    "completeness",
    "trigger_precision",
    "scope_coverage",
    "anti_patterns",
)

_SKILL_QUALITY_PROMPT = """\
You are a Cursor skill reviewer for cursorAssistant. Score this SKILL.md on 5 dimensions (each 0.0–1.0):
1. clarity — Purpose, scope, and steps are unambiguous; uses Cursor tools (Read, Grep, Glob, SemanticSearch, Shell) not legacy VS Code names.
2. completeness — When to use, When NOT to use, workflow (Steps or Modules), Verify checklist where appropriate.
3. trigger_precision — Description enables correct /skill invocation without false positives.
4. scope_coverage — Covers the stated purpose without major gaps.
5. anti_patterns — Absence of vague triggers, missing guardrails, or Copilot-only assumptions. 1.0 = none found.

SKILL.md:
```
{content}
```

Return ONLY valid JSON:
{{"clarity":<f>,"completeness":<f>,"trigger_precision":<f>,"scope_coverage":<f>,"anti_patterns":<f>,"overall":<f>,"summary":"<one sentence>"}}
"""

_AGENT_QUALITY_PROMPT = """\
You are a Cursor subagent reviewer for cursorAssistant. Score this agent file on 5 dimensions (each 0.0–1.0):
1. clarity — Role, boundaries, and handoffs are clear; mentions Task or /name invocation where relevant.
2. completeness — When to use, When not to use, tools/delegation, output expectations.
3. trigger_precision — YAML description routes correctly (proactive phrasing, negative boundaries); fits AGENTS.md roster.
4. scope_coverage — Covers the specialist role without scope creep into other agents.
5. anti_patterns — No deprecated MCP (filesystem, web), no shadowing built-in Explore. 1.0 = none found.

Agent file:
```
{content}
```

Return ONLY valid JSON:
{{"clarity":<f>,"completeness":<f>,"trigger_precision":<f>,"scope_coverage":<f>,"anti_patterns":<f>,"overall":<f>,"summary":"<one sentence>"}}
"""

_DEV_PROMPT = """\
You are a Cursor surface expert (skills and subagents). Analyse this file and return JSON with:
- Scores for clarity, completeness, trigger_precision, scope_coverage, anti_patterns (each 0.0–1.0)
- overall (0.0–1.0)
- improvements: top 3 concrete, actionable strings for Cursor/cursorAssistant
- summary: one sentence on the most important issue

Context: cursorAssistant uses built-in Explore/Bash/Browser, Task subagents, /skill-name skills, AGENTS.md routing.

File:
```
{content}
```

Return ONLY valid JSON:
{{"clarity":<f>,"completeness":<f>,"trigger_precision":<f>,"scope_coverage":<f>,"anti_patterns":<f>,"overall":<f>,"improvements":["...","...","..."],"summary":"..."}}
"""


def _is_agent_path(path: Path) -> bool:
    return path.parent.name == "agents" and path.suffix == ".md"


def _quality_prompt(path: Path) -> str:
    template = _AGENT_QUALITY_PROMPT if _is_agent_path(path) else _SKILL_QUALITY_PROMPT
    return template.format(content=read_text(path)[:8000])


def _print_score_bars(scores: dict, label: str, model: str) -> None:
    print(f"cursorEval quality — {label}  [{model}]")
    for dim in QUALITY_DIMENSIONS:
        score = float(scores.get(dim, 0))
        filled = int(score * 10)
        bar = "█" * filled + "░" * (10 - filled)
        print(f"  {dim:<20} {bar}  {score:.2f}")
    overall = float(
        scores.get(
            "overall",
            sum(float(scores.get(d, 0)) for d in QUALITY_DIMENSIONS) / len(QUALITY_DIMENSIONS),
        )
    )
    print(f"\n  overall: {overall:.2f}")


def cmd_quality(path: str, model: str, fmt: str, fail_under: float | None) -> int:
    token = get_token()
    if not token:
        print(
            "cursorEval quality: set GITHUB_MODELS_TOKEN, GITHUB_TOKEN, or GH_TOKEN",
            file=sys.stderr,
        )
        return 2

    target = Path(path)
    try:
        reply = call_model(
            [{"role": "user", "content": _quality_prompt(target)}],
            model,
            token,
        )
    except RuntimeError as exc:
        print(f"cursorEval quality: model error — {exc}", file=sys.stderr)
        return 1

    scores = extract_first_json_object(reply)
    if scores is None:
        print(f"cursorEval quality: could not parse JSON:\n{reply[:300]}", file=sys.stderr)
        return 1

    summary = str(scores.pop("summary", ""))
    bad = [d for d in (*QUALITY_DIMENSIONS, "overall") if not isinstance(scores.get(d), (int, float))]
    if bad:
        print(f"cursorEval quality: non-numeric fields: {', '.join(bad)}", file=sys.stderr)
        return 1

    overall = float(
        scores.get(
            "overall",
            sum(float(scores.get(d, 0)) for d in QUALITY_DIMENSIONS) / len(QUALITY_DIMENSIONS),
        )
    )

    if fmt == "json":
        print(
            json.dumps(
                {
                    "path": str(target),
                    "kind": "agent" if _is_agent_path(target) else "skill",
                    "model": model,
                    "scores": scores,
                    "overall": overall,
                    "summary": summary,
                },
                indent=2,
            )
        )
    else:
        _print_score_bars({**scores, "overall": overall}, target.name, model)
        if summary:
            print(f"  {summary}")

    if fail_under is not None and overall < fail_under:
        return 1
    return 0


def cmd_dev(path: str, model: str, fmt: str) -> int:
    token = get_token()
    if not token:
        print(
            "cursorEval dev: set GITHUB_MODELS_TOKEN, GITHUB_TOKEN, or GH_TOKEN",
            file=sys.stderr,
        )
        return 2

    target = Path(path)
    try:
        reply = call_model(
            [{"role": "user", "content": _DEV_PROMPT.format(content=read_text(target)[:8000])}],
            model,
            token,
        )
    except RuntimeError as exc:
        print(f"cursorEval dev: model error — {exc}", file=sys.stderr)
        return 1

    analysis = extract_first_json_object(reply)
    if analysis is None:
        print(f"cursorEval dev: could not parse JSON:\n{reply[:300]}", file=sys.stderr)
        return 1

    bad = [d for d in (*QUALITY_DIMENSIONS, "overall") if not isinstance(analysis.get(d), (int, float))]
    if bad:
        print(f"cursorEval dev: non-numeric fields: {', '.join(bad)}", file=sys.stderr)
        return 1

    overall = float(analysis.get("overall", 0))
    improvements = analysis.get("improvements", [])
    if not isinstance(improvements, list):
        improvements = []

    if fmt == "json":
        print(json.dumps({"path": str(target), "model": model, "analysis": analysis}, indent=2))
    else:
        _print_score_bars(analysis, target.name, model)
        summary = str(analysis.get("summary", ""))
        if summary:
            print(f"  {summary}")
        if improvements:
            print("\n  improvements:")
            for index, item in enumerate(improvements[:5], 1):
                print(f"    {index}. {item}")
        if overall >= 0.90:
            print("\n  skill/agent is already high quality")
        else:
            print(f"\n  re-run after edits: cursorEval quality {path}")
    return 0
