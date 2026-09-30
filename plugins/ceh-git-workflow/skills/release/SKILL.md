---
name: release
description: >-
  Load this skill when cutting a release, bumping a version, tagging, or publishing a release:
  following semantic versioning, committing the version bump, tagging main, pushing the tag, and
  creating the release. Trigger when the user says "cut a release", "create a release", "tag a
  release", "create a tag and a release", "bump the version", "bump the versions", "bump and
  release", "ship a release", or "publish a release". Auto-load whenever a version field changes in
  any project manifest (e.g. pyproject.toml, package.json, plugin.json, marketplace.json,
  Cargo.toml, *.csproj, build.gradle), a git tag is being created, or a release is being created.
compatibility: >-
  Requires the git CLI on PATH, the GitHub CLI (`gh`) installed and authenticated via `gh auth
  login`, a git repository with a GitHub remote, permission to push tags, and network access.
---

# Release Tagging

Tags follow semver: `v<major>.<minor>.<patch>`. Apply only to commits on `main` after all CI passes.

| Change type                                             | Bump  |
| ------------------------------------------------------- | ----- |
| Breaking change (`BREAKING CHANGE:` footer or `!` type) | MAJOR |
| New backward-compatible feature                         | MINOR |
| Fixes, chores, docs, refactors                          | PATCH |

When in doubt, bump PATCH. Never lower a version.

Pre-release versions use a suffix: `v1.4.0-rc.1`, `v1.4.0-beta.1`. They sort below the final
`v1.4.0`, so they're safe for staged rollouts.

## Procedure

Before bumping the version, **update the changelog** for this release so the new version section
and release notes are ready to reference — saying "update the changelog" loads the Keep a Changelog
format and what belongs in a release-notes entry. The GitHub release notes (`--notes-file` below)
reuse that version's changelog section.

```bash
# 1. Bump the version in this project's manifest(s) — whatever the project uses
#    (pyproject.toml, package.json, plugin.json, marketplace.json, Cargo.toml, ...), commit.
#    Always multi-line — the subject alone does not say what shipped or why the bump is
#    that level, and the diff only shows version strings. Write msg.txt, use -F, never -m.
#      chore: bump version to v<X.Y.Z>
#
#      <what this release ships, 1-3 sentences, matching the changelog entry>
#      <bump level and the change that forces it; which manifests moved>
#
#      <attribution footer exactly as configured in settings>
git add <manifest files>
git commit -F msg.txt && rm msg.txt
git push origin main

# 2. Tag and push. Use an annotated tag (-a -m): some repos enforce it,
#    and `git tag v<X.Y.Z>` then fails with "no tag message".
git tag -a v<X.Y.Z> -m "v<X.Y.Z> — <summary>"
git push origin v<X.Y.Z>

# 3. (Optional) Publish a GitHub release for the tag. Append the attribution footer to the
#    notes file after the changelog section, then delete the file.
gh release create v<X.Y.Z> --title "v<X.Y.Z>" --notes-file <notes file>
```

## Rules

Both artifacts this skill produces carry the attribution footer the environment supplies —
surfaced verbatim in the session's Git instructions. Reproduce the line exactly; never substitute
a literal from this skill or from memory. If the relevant setting is `false`/empty, or no
attribution line is supplied, omit the footer.

| Artifact                      | Setting              | Where the footer goes           |
| ----------------------------- | -------------------- | ------------------------------- |
| Version-bump commit (step 1)  | `attribution.commit` | Last line of the commit message |
| GitHub release notes (step 3) | `attribution.pr`     | Last line of the notes file     |

The annotated tag message (step 2) takes no attribution — keep it to `v<X.Y.Z> — <summary>`.
