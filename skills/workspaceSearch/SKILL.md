---
name: workspaceSearch
description: "Use when: choosing the right Cursor search strategy for a workspace query, executing and refining searches, and acting on results — exact text, regex, semantic, and file-path discovery."
version: "1.1"
license: MIT
---

# Workspace Search (Cursor)

Procedural skill for selecting, executing, and acting on workspace searches in Cursor. Different intents need different tools; this skill routes first, refines on poor results, then dispatches findings.

## When to use

- When more than one search method could apply and the best fit is unclear
- When initial results are empty, too noisy, or scoped incorrectly
- When results must become a concrete next action (scope list, doc quote, handoff)

## When NOT to use

- Large parallel codebase exploration — use Cursor's built-in **Explore** subagent
- A single obvious **Grep** or **SemanticSearch** call — run it directly
- External sources (issues, web) — use **researcher** or WebSearch/WebFetch

---

## Module 1 — Choose the search method

| Intent | Best method |
| --- | --- |
| Exact string, identifier, or known phrase | **Grep** (fixed string) |
| Regex or alternation | **Grep** (regex) |
| Concept, purpose, natural-language | **SemanticSearch** |
| Files by name or path pattern | **Glob** |
| Read a known path | **Read** |

**Scope before searching:** pass a directory or `glob` to **Grep**/**Glob** when the target area is known.

**Batch:** issue independent searches in parallel when both exact and semantic views help.

---

## Module 2 — Execute and refine

| Symptom | Refinement |
| --- | --- |
| Zero results (exact) | Shorter substring; regex alternation |
| Zero results (semantic) | More concrete query; fall back to **Grep** for a key term |
| Zero results (glob) | Broaden pattern (e.g. `**/*.py`) |
| Too many hits | Narrow directory/glob; tighten pattern |
| Vendor/generated noise | Exclude `node_modules`, `dist`, `.venv`, `__pycache__` from conclusions |

Do not repeat the same query twice. One refinement, then report failure with attempted queries.

---

## Module 3 — Act on results

| Goal | Action |
| --- | --- |
| Summarize scope | Count + representative paths; do not dump every match |
| Refactor scope | File list for the implementation step |
| Documentation | Quote 2–3 representative matches with paths |
| Unused symbol check | Zero imports across **Grep** patterns before claiming unused |

Use workspace-relative paths in summaries.

---

## Verify

- [ ] Method chosen from the routing table (not defaulting to semantic for exact IDs)
- [ ] Scope narrowed when possible
- [ ] One refinement attempted if results were empty or noisy
- [ ] Findings tied to a next action or explicit handoff
