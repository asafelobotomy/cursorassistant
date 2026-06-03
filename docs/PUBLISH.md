# Publishing cursorAssistant to the Cursor Marketplace

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

- `plugin.json` `version` must match [VERSION](../VERSION)
- `name` is kebab-case (`cursor-assistant`)
- Component paths (`agents`, `skills`, `rules`, `mcpServers`) must exist in this repo

The marketplace manifest lists **core** `agents/`, `skills/`, `template/rules/`, and `mcp-core.json` only. **Packs** (lean, secure, tdd) and **MCP extensions** (devDocs, memory) are installed via the lifecycle CLI:

```sh
python3 cursorAssistant.py setup --workspace . --package-root . \
  --answers '{"mcp.enabled": true, "packs.selected": ["secure"]}'
```

Dogfood in this repo: `scripts/dogfood.sh` (lean) vs `scripts/dogfood-full.sh` (extensions + all packs).

## Submit

1. Open [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish)
2. Link the GitHub repository: `https://github.com/asafelobotomy/cursorassistant`
3. Provide description, category, and keywords from `plugin.json`
4. Respond to reviewer feedback on agent/skill frontmatter and MCP safety

## Consumer install (non-marketplace)

Users can still install via lifecycle CLI:

```sh
python3 cursorAssistant.py setup --workspace . --package-root /path/to/cursorassistant
```

Marketplace distribution is optional; the lifecycle engine remains the source of truth for versioned installs.
