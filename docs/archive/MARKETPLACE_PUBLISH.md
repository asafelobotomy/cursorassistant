# Archived: Cursor Marketplace publishing

> **Status:** Archived. cursorAssistant is **not** listed on the public Cursor Marketplace.
> **Primary install:** [INSTALL.md](../../INSTALL.md) and `scripts/install-from-github.sh`.

This document is kept for maintainers who may submit a listing later. End users should not follow these steps.

## Prerequisites

- [Cursor plugin manifest](https://cursor.com/docs/reference/plugins) at `.cursor-plugin/plugin.json`
- Repository public (or accessible to Cursor reviewers)
- `validate_plugin.py` passes locally

## Pre-flight checklist

```sh
python3 scripts/validate_plugin.py
python3 scripts/generate.py --package-root .
python3 -m unittest discover -s tests
python3 tools/cursorEval/cursorEval.py --repo-root . validate
python3 tools/cursorEval/cursorEval.py --repo-root . coverage
```

## Manifest alignment

- `plugin.json` `version` must match [VERSION](../../VERSION)
- `name` is kebab-case (`cursor-assistant`)
- Component paths (`agents`, `skills`, `rules`, `commands`) must exist in this repo

## Submit (if pursuing listing)

1. Open [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish)
2. Link the GitHub repository
3. Respond to reviewer feedback

Even with a future listing, users still run **project setup** via `install-from-github.sh` or `configure` for lockfile, packs, and selective MCP.
