# Documentation index

cursorAssistant docs are grouped by purpose. **Supported install path:** [INSTALL.md](../INSTALL.md) (repo root).

## Guides (operators & consumers)

| Doc | Topic |
| --- | --- |
| [guides/CURSOR_INSTALL_UX.md](guides/CURSOR_INSTALL_UX.md) | Install flow inside Cursor |
| [guides/MIGRATION.md](guides/MIGRATION.md) | Upgrading from v0.9 → v0.10+ |
| [guides/HOOKS.md](guides/HOOKS.md) | Optional user-owned hooks (not lifecycle-managed) |
| [guides/PUBLISH.md](guides/PUBLISH.md) | GitHub distribution, plugin manifest, releases |

## Architecture & routing

| Doc | Topic |
| --- | --- |
| [architecture/ARCHITECTURE.md](architecture/ARCHITECTURE.md) | Policy, lifecycle engine, install flow |
| [architecture/ROUTING_AND_SUBAGENTS.md](architecture/ROUTING_AND_SUBAGENTS.md) | Subagent roster, delegation, eval routing |
| [architecture/PERFORMANCE.md](architecture/PERFORMANCE.md) | Token budgets, skill scoping, merge checklist |
| [guides/CURSOR_AUTOMATIONS.md](guides/CURSOR_AUTOMATIONS.md) | Optional automations and hooks (zero default cost) |
| [architecture/MCP_LAYOUT.md](architecture/MCP_LAYOUT.md) | Layered `mcp-core` / extensions / packs |
| [architecture/SHARED_MCP.md](architecture/SHARED_MCP.md) | `packages/cursor-mcp-shared` vendoring |

## Operations (maintainers)

| Doc | Topic |
| --- | --- |
| [operations/MCP_MAINTENANCE.md](operations/MCP_MAINTENANCE.md) | MCP scripts, deprecation, vendoring workflow |
| [operations/PACKAGE_REPO_MAINTENANCE.md](operations/PACKAGE_REPO_MAINTENANCE.md) | Regenerate manifest and dogfood `.cursor/` after source edits |
| [operations/INSTALL_WEBSITE_SYNC.md](operations/INSTALL_WEBSITE_SYNC.md) | Install page template here → PR on github.io |

## Project history

| Doc | Topic |
| --- | --- |
| [project/ROADMAP.md](project/ROADMAP.md) | Version milestones (historical names through v0.12+) |

## Audits (point-in-time)

Dated reviews; cross-check against current tree before treating as authoritative.

| Doc | Date / scope |
| --- | --- |
| [audits/FULL_AUDIT_2026-06-04.md](audits/FULL_AUDIT_2026-06-04.md) | 2026-06-04 — v0.13.0 full audit + remediation |
| [audits/AGENTS_SKILLS_CURSOR_AUDIT.md](audits/AGENTS_SKILLS_CURSOR_AUDIT.md) | 2026-06-04 — agents/skills Cursor fit (v0.13) |
| [audits/CURSOR_EVAL_AUDIT.md](audits/CURSOR_EVAL_AUDIT.md) | cursorEval vs xanadEval / waza |
| [audits/INSTALL_SECURITY_AUDIT.md](audits/INSTALL_SECURITY_AUDIT.md) | Install / deeplink / bootstrap threats |

**Current routing:** prefer [architecture/ROUTING_AND_SUBAGENTS.md](architecture/ROUTING_AND_SUBAGENTS.md) over the agents/skills audit snapshot.

## Research

| Doc | Topic |
| --- | --- |
| [research/DEEPLINK_INSTALL_RESEARCH.md](research/DEEPLINK_INSTALL_RESEARCH.md) | `cursor://` install options and landing-page design |

## Archive

| Doc | Topic |
| --- | --- |
| [archive/README.md](archive/README.md) | Index of deferred / superseded material |
| [archive/MARKETPLACE_PUBLISH.md](archive/MARKETPLACE_PUBLISH.md) | Marketplace listing (not used; GitHub install primary) |

## Root-level docs (outside `docs/`)

| Doc | Topic |
| --- | --- |
| [../README.md](../README.md) | Project overview |
| [../INSTALL.md](../INSTALL.md) | Install and update |
| [../SECURITY.md](../SECURITY.md) | MCP, secrets, eval tokens |
| [../CHANGELOG.md](../CHANGELOG.md) | Release notes |
| [../AGENTS.md](../AGENTS.md) | Subagent routing (installed to consumer workspaces) |
