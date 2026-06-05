# Package repo maintenance (cursorAssistant sources)

This repository **dogfoods** its own lifecycle: managed sources live under `agents/`, `skills/`, `template/rules/`, and repo-root `AGENTS.md`, and are mirrored into committed `.cursor/` for CI and local Cursor use.

## Rule

After editing any **managed package source**, regenerate hashes and refresh dogfood **before** you push:

```sh
bash scripts/sync_managed_surfaces.sh
git add template/setup/install-manifest.json template/setup/catalog.json .cursor/
# plus AGENTS.md if you changed routing at the repo root
git commit -m "your message"
```

Equivalent manual steps:

```sh
python3 scripts/generate.py --package-root .
python3 cursorAssistant.py update --workspace . --answers tests/fixtures/interview-balanced.json
```

## What enforces it

| Layer | Mechanism | Catches |
| --- | --- | --- |
| **CI** (`ci.yml`) | `python3 scripts/check_package_sync.py` | Stale `install-manifest.json`, `catalog.json`, or committed `.cursor/` / lockfile |
| **Local (optional)** | Git hook | Same check before commit when managed paths are staged |

Enable the pre-commit hook once per clone:

```sh
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

Verify without committing:

```sh
python3 scripts/check_package_sync.py
```

Fast check (manifest only, skips dogfood inspect):

```sh
python3 scripts/check_package_sync.py --skip-dogfood
```

## Paths that trigger the hook

- `AGENTS.md`
- `agents/*.md`
- `skills/*/SKILL.md`
- `template/rules/*.mdc`
- `template/setup/install-policy.json`
- `packs/*/skills/*/SKILL.md`

Adding a **new** core skill also requires an entry in `install-policy.json` (then run sync).

## Consumer workspaces

End-user projects run `setup` / `update` in **their** repo; they do not commit this package’s `.cursor/` snapshot. This rule applies to **maintainers of the cursorAssistant package repo** only.
