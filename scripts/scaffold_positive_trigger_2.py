#!/usr/bin/env python3
"""Write positive-trigger-2.yaml for eval suites that lack it (idempotent)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# eval_dir relative to REPO -> (description, prompt, expected[, expected_absent])
TASKS: dict[str, tuple] = {
    "evals/ciPreflight": (
        "Natural language pre-commit workflow phrase routes to ciPreflight",
        "I changed several files and want the cheapest local checks mirrored from "
        ".github/workflows before I git commit. Which cursorAssistant skill?",
        ["ciPreflight"],
    ),
    "evals/depSearch": (
        "Manifest discovery without mutating packages routes to depSearch",
        "List lockfiles and package manifests and check import usage before we remove "
        "anything — discovery only, no installs. Which skill?",
        ["depSearch"],
    ),
    "evals/lifecycleAudit": (
        "Pre-update health check phrase routes to lifecycleAudit",
        "Before cursorAssistant update, which skill inspects installState, repair "
        "reasons, and lockfile validity?",
        ["lifecycleAudit"],
    ),
    "evals/task-triage": (
        "Complexity classification phrase routes to task-triage",
        "This request might be a one-liner or need multiple subagents — what skill "
        "classifies tier and minimal path first in cursorAssistant?",
        ["task-triage"],
    ),
    "evals/testing": (
        "Run tests and summarize phrase routes to testing skill",
        "Pick the project's test command, run the suite, and summarize failures for "
        "debugger handoff. Which skill?",
        ["testing"],
    ),
    "evals/workspaceSearch": (
        "Search strategy choice phrase routes to workspaceSearch",
        "For finding where a symbol is defined, should the Agent use Grep, "
        "SemanticSearch, or Glob? Which cursorAssistant skill guides that?",
        ["workspaceSearch"],
    ),
    "evals/cleaner": (
        "Hygiene and cache pruning phrase routes to cleaner subagent",
        "Prune __pycache__, stale build artifacts, and old .cursorEval JSON with "
        "user approval — no feature edits. Which subagent?",
        ["cleaner"],
    ),
    "evals/commit": (
        "Commit and PR phrase routes to commit subagent",
        "Stage my changes, write a Conventional Commit message, and open a PR with gh. "
        "Which subagent in cursorAssistant?",
        ["commit"],
    ),
    "evals/cursorLifecycle": (
        "Managed surface repair phrase routes to cursorLifecycle",
        "Hand-edited .cursor/agents broke the lockfile — run repair or factory-restore "
        "on managed surfaces. Which subagent?",
        ["cursorLifecycle"],
    ),
    "evals/debugger": (
        "Root-cause isolation phrase routes to debugger subagent",
        "pytest failed on CI — diagnose root cause read-only without implementing fixes "
        "yet. Which subagent?",
        ["debugger"],
    ),
    "evals/deps": (
        "Package install and audit phrase routes to deps subagent",
        "Run npm audit, upgrade vulnerable packages after confirmation, and update "
        "the lockfile. Which subagent?",
        ["deps"],
    ),
    "evals/docs": (
        "Documentation authoring phrase routes to docs subagent",
        "Draft MIGRATION.md and update INSTALL.md for the new configure flow. Which "
        "subagent should write repo docs?",
        ["docs"],
    ),
    "evals/inventory": (
        "Structured map phrase routes to inventory not Explore",
        "Build a caller map of cursorAssistant.py and list eval suites — structured "
        "inventory, not parallel Explore. Which subagent?",
        ["inventory"],
    ),
    "evals/organise": (
        "Moves and import repair phrase routes to organise subagent",
        "Move scripts/lifecycle into scripts/pkg/lifecycle and fix all import paths. "
        "Which subagent owns structural moves?",
        ["organise"],
    ),
    "evals/planner": (
        "Phased rollout phrase routes to planner subagent",
        "Refactor three modules with migrations, tests, and docs — need a phased plan "
        "before coding. Which subagent plans first?",
        ["planner"],
    ),
    "evals/researcher": (
        "External cited research phrase routes to researcher subagent",
        "Look up GitHub Models chat completions limits with citations before we wire CI. "
        "Which subagent?",
        ["researcher"],
    ),
    "evals/review": (
        "PR diff review phrase routes to review not surfaceReview",
        "Review this pull request diff for regressions and design — do not edit source. "
        "Which subagent?",
        ["review"],
        ["(?i)\\bsurfaceReview\\b"],
    ),
    "packs/lean/evals/leanAndon": (
        "Andon stop-or-proceed phrase routes to leanAndon skill",
        "The agent is unsure whether to stop for user confirmation or proceed on a "
        "destructive step. Which lean pack skill applies?",
        ["leanAndon"],
    ),
    "packs/lean/evals/leanContext": (
        "Tight context phrase routes to leanContext skill",
        "Working context is full of stale notes and duplicate summaries. Which lean "
        "skill keeps context tight and actionable?",
        ["leanContext"],
    ),
    "packs/lean/evals/leanOutput": (
        "Minimal output phrase routes to leanOutput skill",
        "User wants counts and facts only — no filler or routine narration. Which lean "
        "skill governs response shape?",
        ["leanOutput"],
    ),
    "packs/lean/evals/leanVerification": (
        "Concise test report phrase routes to leanVerification skill",
        "Summarize pass/fail from the last test run with minimal bullets for triage. "
        "Which lean pack skill?",
        ["leanVerification"],
    ),
    "packs/secure/evals/dependencyAudit": (
        "OSV lockfile audit phrase routes to dependencyAudit skill",
        "Query OSV.dev for CVEs in our lockfile packages and triage severity. Which "
        "secure pack skill?",
        ["dependencyAudit"],
    ),
    "packs/secure/evals/secretScanning": (
        "Pre-commit secret scan phrase routes to secretScanning skill",
        "Scan staged files for API keys and tokens before this commit lands. Which "
        "skill?",
        ["secretScanning"],
    ),
    "packs/secure/evals/secureReview": (
        "OWASP code review phrase routes to secureReview skill",
        "Review authentication handlers for OWASP Top 10 issues with severities. Which "
        "secure pack skill?",
        ["secureReview"],
    ),
    "packs/secure/evals/threatModel": (
        "STRIDE modeling phrase routes to threatModel skill",
        "Produce a STRIDE threat model with trust boundaries for a new REST endpoint. "
        "Which skill?",
        ["threatModel"],
    ),
    "packs/tdd/evals/tddCycle": (
        "Red-green-refactor phrase routes to tddCycle skill",
        "Write one failing test, minimal green implementation, optional commit on green. "
        "Which tdd pack skill?",
        ["tddCycle"],
    ),
    "packs/tdd/evals/testArchitecture": (
        "Test boundary phrase routes to testArchitecture skill",
        "Decide unit vs integration boundaries and what a test must not cross. Which "
        "tdd pack skill?",
        ["testArchitecture"],
    ),
    "packs/tdd/evals/testCoverage": (
        "Coverage diagnostic phrase routes to testCoverage skill",
        "Interpret coverage.xml gaps and weak assertions as diagnostics, not a percent "
        "goal. Which skill?",
        ["testCoverage"],
    ),
    "packs/tdd/evals/testDoubles": (
        "Test doubles phrase routes to testDoubles skill",
        "Pick stubs, mocks, or fakes to isolate a flaky integration test. Which tdd "
        "pack skill?",
        ["testDoubles"],
    ),
}


def render_task(
    description: str,
    prompt: str,
    expected: list[str],
    expected_absent: list[str] | None = None,
) -> str:
    lines = [
        "id: positive-trigger-2",
        f'description: "{description}"',
        "prompt: |",
    ]
    # wrap prompt at reasonable width
    words = prompt.split()
    buf: list[str] = []
    current: list[str] = []
    for w in words:
        if sum(len(x) + 1 for x in current) + len(w) > 72 and current:
            buf.append("  " + " ".join(current))
            current = [w]
        else:
            current.append(w)
    if current:
        buf.append("  " + " ".join(current))
    lines.extend(buf)
    lines.append("expected:")
    for e in expected:
        lines.append(f'  - "{e}"')
    if expected_absent:
        lines.append("expected_absent:")
        for e in expected_absent:
            lines.append(f'  - "{e}"')
    lines.extend(["tags:", "  - smoke", "  - positive", ""])
    return "\n".join(lines)


def main() -> int:
    written = 0
    skipped = 0
    for rel, spec in sorted(TASKS.items()):
        if len(spec) == 3:
            desc, prompt, expected = spec
            absent = None
        else:
            desc, prompt, expected, absent = spec
        out = REPO / rel / "tasks" / "positive-trigger-2.yaml"
        if out.is_file():
            skipped += 1
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            render_task(desc, prompt, list(expected), list(absent) if absent else None),
            encoding="utf-8",
        )
        print(f"wrote {out.relative_to(REPO)}")
        written += 1
    print(f"done: {written} written, {skipped} skipped (already present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
