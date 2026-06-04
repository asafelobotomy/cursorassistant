# Distribution

cursorAssistant is installed from **GitHub**, not the Cursor Marketplace.

## Primary install

See [INSTALL.md](../INSTALL.md) and the README **Install** section:

```sh
curl -fsSL https://raw.githubusercontent.com/asafelobotomy/cursorassistant/v0.12.0/scripts/install-from-github.sh | bash -s -- /path/to/your-project
```

## Plugin manifest (maintainers)

`.cursor-plugin/plugin.json` describes the bundle layout for Cursor’s **local plugin** loader. The install script symlinks the package to `~/.cursor/plugins/local/cursor-assistant` and reloads Cursor — no marketplace required.

Validate before release:

```sh
python3 scripts/validate_plugin.py
python3 scripts/changelog_release.py verify
python3 -m unittest discover -s tests
```

## Automated GitHub Release

On push to `master` / `main`, when **`VERSION`** changes, [.github/workflows/release.yml](../.github/workflows/release.yml) will:

1. Verify **CHANGELOG.md** has a `## [x.y.z] - date` section for the new version.
2. Create annotated tag **`vX.Y.Z`** and a GitHub Release with that section as the body.

**Maintainer steps for each release:**

1. Move notes from `## [Unreleased]` into a new `## [X.Y.Z] - YYYY-MM-DD` section at the top of [CHANGELOG.md](../CHANGELOG.md).
2. Bump [VERSION](../VERSION) to match (and `.cursor-plugin/plugin.json` if needed).
3. Run `python3 scripts/generate_install_page.py` if install URLs embed the version.
4. Push to `master`. The release workflow runs after CI paths match.

To draft notes locally:

```sh
python3 scripts/changelog_release.py extract -o /tmp/release-notes.md
```

## Archived: Marketplace submission

If we pursue a public listing later, see [../archive/MARKETPLACE_PUBLISH.md](../archive/MARKETPLACE_PUBLISH.md).
