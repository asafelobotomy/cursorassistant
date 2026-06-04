# Install website sync (cursorassistant → github.io)

Public URL: [https://asafelobotomy.github.io/cursorassistant/install/](https://asafelobotomy.github.io/cursorassistant/install/)

Hosted in [asafelobotomy.github.io](https://github.com/asafelobotomy/asafelobotomy.github.io). **You do not need a separate workspace** for routine updates.

## Single source of truth (this repo)

| File | Purpose |
| --- | --- |
| `install/index.template.html` | Install page UX (edit here) |
| `scripts/generate_install_page.py` | Local preview generator |
| `VERSION` | Pins MCP deeplink tag |

Generated files (`install/index.html`, `deeplinks.json`) are published to github.io by automation.

## Fully automatic flow

1. Edit `install/index.template.html` and/or bump `VERSION`.
2. Preview locally: `python3 scripts/generate_install_page.py`
3. Merge to **cursorassistant** `master` / `main`.
4. [.github/workflows/publish-install-website.yml](../../.github/workflows/publish-install-website.yml) regenerates artifacts and **pushes directly** to github.io `main`.
5. GitHub Pages rebuilds (usually 1–2 minutes). No PR or squash-merge on github.io.

## One-time setup (maintainer)

1. Create a fine-grained GitHub PAT with **Contents: Read and write** on `asafelobotomy/asafelobotomy.github.io`.
2. Add it to **cursorassistant** → **Settings → Secrets → Actions** as `INSTALL_WEBSITE_TOKEN`.
3. On **github.io**, ensure `main` allows pushes from Actions:
   - If branch protection requires PRs, add bypass for `github-actions[bot]` or disable required PRs for this repo (static site only).

Without the secret, the weekly sync on github.io still updates on schedule.

## Manual / fallback

```sh
# In a clone of asafelobotomy.github.io:
bash scripts/sync-cursorassistant-install.sh
git add cursorassistant/install && git commit && git push
```

Or **workflow_dispatch** on either repo’s publish/sync workflow.

## Other ways to work on github.io

| Approach | When |
| --- | --- |
| **Automated push** (above) | Template or VERSION changes in cursorassistant |
| **Multi-root workspace** | Homepage `projects.json`, shared CSS, other projects |
| **Git worktree** | Second folder on disk without leaving cursorassistant |

## Safety nets

| Mechanism | Repo |
| --- | --- |
| `publish-install-website.yml` on push to `master` | cursorassistant → push github.io |
| `sync-cursorassistant-install.yml` weekly + manual | github.io pulls upstream if cursorassistant push missed |

## Release checklist

1. Bump `VERSION` + `CHANGELOG.md` → merge cursorassistant.
2. Confirm **Publish install website** workflow succeeded on GitHub Actions.
3. Open the live install URL and verify the version line.
