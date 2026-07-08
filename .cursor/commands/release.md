# Release

Execute the release pipeline for **ha-mawaqeet**. This integration publishes via **GitHub Release → `release.yml` → `mawaqeet.zip`** (HACS `zip_release`). There is no Docker image, no root `VERSION` file, and no Pages gate.

Shell and Python execution must follow `.cursor/rules/shell.mdc`, `.cursor/rules/windows-shell.mdc`, and `.cursor/rules/python.mdc` (bash/Git Bash on Windows; Docker for pytest when host Python cannot run HA).

## Version resolution

Determine `{VERSION}` once (semver, no leading `v` in user text after stripping; Git tag **includes** `v`).

| User invocation | `{VERSION}` |
|-----------------|-------------|
| `/release` (no version) | Bump semver (default **patch**) from `max(latest GitHub release tag without v, manifest.json version)`. |
| `/release 0.4.4` | Explicit stable `0.4.4`. |
| `/release 0.4.4-beta.1` | Explicit pre-release string. |

**Parsing rules** (from user message text after the command):

1. Strip optional leading `v` / `V`.
2. Must match `^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$`.
3. **Pre-release** = version contains `-` after `major.minor.patch`.
4. If user says “beta” / “prerelease” / “rc” **without** a version → stop and ask.
5. **Never invent** a pre-release from manifest alone — pre-releases are always user-specified.

Convention for successive betas on the same base: increment the numeric suffix (`-beta.1` → `-beta.2`).

**Resolving the bump base** (when user omits an explicit version):

```bash
gh release view --json tagName --jq .tagName   # e.g. v0.4.3 → 0.4.3
# and read custom_components/mawaqeet/manifest.json → .version
# base = max(tag_without_v, manifest_version) by semver
# default new version = patch bump of base
```

Canonical in-tree version lives in `custom_components/mawaqeet/manifest.json` (`"version"`, no `v` prefix). Git tag is `v{VERSION}`.

`.github/workflows/release.yml` strips a leading `v`/`V` from the release tag when writing the packaged `manifest.json`, so the HACS zip gets `"version": "{VERSION}"` (not `v{VERSION}`).

## Release kinds

| Kind | `{VERSION}` example | GitHub Release | HACS |
|------|---------------------|----------------|------|
| Stable | `0.4.4` | normal (tag `v0.4.4`) | default channel |
| Pre-release | `0.4.4-beta.1` | `prerelease: true` (tag `v0.4.4-beta.1`) | beta / explicit |

`hacs.json` already has `"zip_release": true` and `"filename": "mawaqeet.zip"` — the Release workflow must attach **`mawaqeet.zip`**.

## 1. Prepare version and docs (single branch)

1. Resolve `{VERSION}` as above.
2. Update `"version"` in `custom_components/mawaqeet/manifest.json` to `{VERSION}` (no `v` prefix).
3. Update README / CONTRIBUTING / translations if user-facing behavior changed.
4. **Do not commit** unless the user explicitly asks; stage changes and report `git status`.

## 2. Local checks (once, before opening the PR)

Run and fix failures before proceeding:

```bash
bash scripts/lint
bash scripts/test
```

On Windows if host pytest fails (`fcntl` / HA), use Docker per `python.mdc`.

If any files under `custom_components/mawaqeet/frontend/` changed, also run:

```bash
python scripts/build_frontend.py
```

Do **not** re-run the full suite after merge if CI will run the same jobs — local checks are the pre-push gate only.

## 3. One PR → merge to `main`

- Create **one** release branch with version bump and code changes together.
- Open a PR and merge to `main` (use `gh` for GitHub tasks).
- Workflows also gate `dev`; publish releases from `main`.

## 4. Gate: CI green on the merge commit

After merge, wait for workflows triggered by that push:

```bash
git fetch origin main
MERGE_SHA="$(git rev-parse origin/main)"
gh run list --commit "$MERGE_SHA" --limit 10
gh run watch --exit-status $(gh run list --workflow=test.yml --commit "$MERGE_SHA" --json databaseId --jq '.[0].databaseId')
gh run watch --exit-status $(gh run list --workflow=lint.yml --commit "$MERGE_SHA" --json databaseId --jq '.[0].databaseId')
gh run watch --exit-status $(gh run list --workflow=validate.yml --commit "$MERGE_SHA" --json databaseId --jq '.[0].databaseId')
gh run watch --exit-status $(gh run list --workflow=frontend.yml --commit "$MERGE_SHA" --json databaseId --jq '.[0].databaseId')
```

**Stop here** until **Test**, **Lint**, **Validate** (hassfest + HACS), and **Frontend** all succeed. Do not create the GitHub Release yet.

## 5. Publish GitHub Release (triggers packaging)

On latest `main` after gates pass, create a **published** GitHub Release for tag `v{VERSION}` (this fires `release.yml` on `release: published`):

```bash
git checkout main && git pull origin main
gh release create "v{VERSION}" --title "v{VERSION}" --generate-notes
# For pre-release:
# gh release create "v{VERSION}" --title "v{VERSION}" --generate-notes --prerelease
```

If the tag already exists locally/remotely without a Release, prefer `gh release create` against that tag rather than deleting/recreating tags.

`.github/workflows/release.yml` then:

- Checks out the repo at the release tag
- Sets packaged `custom_components/mawaqeet/manifest.json` `version` to `{VERSION}` (leading `v`/`V` stripped from the tag)
- Zips `custom_components/mawaqeet/` → `mawaqeet.zip`, excluding `frontend/` (Node sources; keep `www/`), `__pycache__`/`*.pyc`, and `brand/src/` (keep rendered brand PNGs)
- Uploads **`mawaqeet.zip`** to the GitHub Release

## 6. Gate: Release workflow green

```bash
gh run watch --exit-status $(gh run list --workflow=release.yml --limit=1 --json databaseId --jq '.[0].databaseId')
gh release view "v{VERSION}"
gh release view "v{VERSION}" --json assets --jq '.assets[].name'
# must include: mawaqeet.zip
```

For pre-releases, confirm `isPrerelease` / `--prerelease`. Report the release URL and zip asset when complete.

## Pitfalls

| Pitfall | Consequence |
|---------|-------------|
| Tag/Release before CI green | Broken HACS zip from unvalidated code |
| Bump from stale tree `manifest.json` only (ignore GitHub tags) | Under-release (e.g. `0.4.1` after `v0.4.3`) |
| Delete/recreate tag after failed release | Duplicate noise; prefer a patch bump instead |
| Release missing `mawaqeet.zip` | HACS `zip_release` installs break |
| Extra unnamed `.zip` assets on the Release | HACS may pick the wrong file |
| Skip frontend build when card sources changed | CI Frontend fails or stale card in zip |
| Shipping `frontend/` or `brand/src/` inside `mawaqeet.zip` | Bloated/broken HACS install; exclusions live in `release.yml` |
| Windows host pytest without Docker | Often fails; use Docker per `python.mdc` |

## Reporting

At each step, summarize: kind (stable / pre-release), `{VERSION}`, what changed, gate status (Test / Lint / Validate / Frontend / Release), and release URL. If the tree is already release-ready on `main`, skip to step 4.
