---
name: depSearch
description: "Use when: discovering package manifests, assessing dependency health, finding replacements, or confirming import usage before removal — discovery only; mutating installs are handled by the deps agent."
version: "1.2"
license: MIT
disable-model-invocation: true
---

# Dep Search (Cursor)

Discovery and research for dependency work. Use **Glob**, **Read**, **Grep**, **Shell**, and WebSearch/WebFetch. **security** MCP (`query_osv`, `query_deps`) only when that server is enabled in the workspace lockfile.

## When to use

- Before audit, update, or removal of a package
- Health, CVE, or replacement research
- Confirm imports before proposing removal

## When NOT to use

- Install/update/remove packages — `deps` agent after user confirmation
- Architecture review without dependency changes — `review`

## Module 1 — Manifests

**Glob** common manifests:

| Ecosystem | Patterns |
| --- | --- |
| Python | `requirements*.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, `uv.lock`, `poetry.lock` |
| Node | `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Rust | `Cargo.toml`, `Cargo.lock` |
| Go | `go.mod`, `go.sum` |
| Ruby | `Gemfile`, `Gemfile.lock` |
| .NET | `*.csproj`, `packages.config` |
| JVM | `pom.xml`, `build.gradle*` |

**Read** each found file. Extract name, version/range, runtime vs dev, lockfile presence. If none found, stop.

## Module 2 — Registry metadata

Prefer **security** MCP `query_deps` when available.

| Ecosystem | Shell / web fallback |
| --- | --- |
| Python | `pip index versions <pkg>` or PyPI JSON |
| Node | `npm view <pkg> version` |
| Rust | `cargo search <pkg>` |
| Go | `go list -m <mod>@latest` |
| General | WebSearch for latest stable version |

Record: latest version, gap vs declared, license, maintenance (release within 12 months baseline).

## Module 3 — Vulnerabilities

Prefer **query_osv** when security MCP is enabled.

| Ecosystem | Fallback |
| --- | --- |
| Python | `pip-audit` |
| Node | `npm audit` |
| General | `osv-scanner` or WebSearch on osv.dev |

Flag CVSS ≥ 7 with a fix version first.

## Module 4 — Replacements

When abandoned or unfixable: WebSearch for maintained alternatives; compare with `query_deps` when available. Cite every recommendation.

## Module 5 — Import usage

**Grep** package name and import patterns (`import`, `from`) in source and tests. List evidence before proposing removal. Check transitive deps in lockfiles.

## Verify

- [ ] Manifests found and read
- [ ] Metadata and OSV checked for reviewed packages
- [ ] Citations for recommendations
- [ ] Import usage confirmed before removal proposals
