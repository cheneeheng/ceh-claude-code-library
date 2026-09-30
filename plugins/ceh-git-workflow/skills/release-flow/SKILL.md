---
name: release-flow
description: >-
  Load this skill when shipping a complete project release in one pass — bump the version, update
  the changelog/README/CLAUDE.md, open a PR, merge it, then tag and publish the release. Trigger on
  "run the release flow", "do the full release", "ship this release end to end", "bump version,
  update docs, open a PR, merge, tag and release". This skill only sequences the steps and gates
  between them; it delegates each step to the skill that owns it (branch, update-changelog,
  update-readme, commit, open-pr, merge, release). Not for landing a branch with no version bump
  and no tag (use ceh-git-workflow:merge-flow), not for tagging alone (use
  ceh-git-workflow:release), and not for an urgent production fix (use ceh-git-workflow:hotfix).
argument-hint: "[version]"
compatibility: >-
  Requires the git CLI on PATH, the GitHub CLI (`gh`) installed and authenticated via `gh auth
  login`, a git repository with a GitHub remote, permission to push branches and tags, and network
  access. Delegated steps may need the target repo's toolchain; none is assumed.
---

# Release Flow

End-to-end project release in one pass: **version bump → changelog → README → CLAUDE.md → commit
→ PR → merge → tag → GitHub release**. This skill owns only the **ordering and the gate between
each step**; every step is delegated to the skill that already owns it, so nothing here is
duplicated.

What it adds over running the steps ad hoc: the version bump lands through a **reviewed PR**, and
the tag + release happen **only after merge, on `main`, pointing at the merge commit** — never on
the feature branch.

## Procedure

Run top to bottom. Each step gates the next — do not proceed past a red gate.

| #   | Step                                                                                                                                                           | Delegate to                                                                                                                                   | Gate before next step                                                                          |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | Decide the semver bump — breaking change → MAJOR, new backward-compatible feature → MINOR, fixes/chores/docs/refactors → PATCH. When in doubt, PATCH           | — decision, no delegation                                                                                                                     | Version chosen, never below current                                                            |
| 2   | Branch `chore/release-vX.Y.Z` from latest `main`                                                                                                               | Invoke the Skill tool with skill="ceh-git-workflow:branch"                                                                                    | On a clean branch off up-to-date `main`                                                        |
| 3   | Bump the version in **every** manifest the project ships (`pyproject.toml`, `package.json`, `plugin.json`, `marketplace.json`, `Cargo.toml`, …)                | — mechanical edit                                                                                                                             | All manifests read the same vX.Y.Z                                                             |
| 4   | Write the vX.Y.Z changelog entry                                                                                                                               | Invoke the Skill tool with skill="ceh-git-workflow:update-changelog"                                                                          | Section written and semver-validated                                                           |
| 5   | Refresh the README if the change is user-facing                                                                                                                | `ceh-readme:update-readme` if that plugin is installed, else a surgical edit                                                                  | Updated, or "no update needed" recorded                                                        |
| 6   | Update CLAUDE.md if project facts/structure changed                                                                                                            | surgical edit (or `revise-claude-md` if that plugin is installed)                                                                             | CLAUDE.md matches reality, or skip logged                                                      |
| 7   | Commit the bump + docs                                                                                                                                         | Invoke the Skill tool with skill="ceh-git-workflow:commit"                                                                                    | Subject `chore: release vX.Y.Z`, **body + attribution footer present** (see below), tree clean |
| 8   | Open the PR — on repos that allow auto-merge, `open-pr` already queues it here                                                                                 | Invoke the Skill tool with skill="ceh-git-workflow:open-pr"                                                                                   | PR open, self-review + definition-of-done passed                                               |
| 9   | Merge and clean up — if step 8 queued auto-merge, this just confirms it lands; otherwise prefer `--auto` (or a direct merge once green). Don't poll CI by hand | Invoke the Skill tool with skill="ceh-git-workflow:merge" (auto-merge probe)                                                                  | CI green, approvals met, merged to `main`, remote-branch state reported                        |
| 10  | Tag and publish the release on `main`                                                                                                                          | Invoke the Skill tool with skill="ceh-git-workflow:release" — **run its tag + release steps only; the bump commit already landed via the PR** | Tag pushed, release created                                                                    |

### Step 7 detail — the release commit is not subject-only

`chore: release vX.Y.Z` is the **subject**, not the whole message. A release commit is the one
place where the diff is least self-explanatory: it shows version strings and changelog prose, but
not what actually shipped or why the bump is that level. Write the full message:

```
chore: release vX.Y.Z

<1–3 sentences: what this release ships, in the same terms as the changelog
entry — the user-visible change, not "bumped files".>

- Bump: <PATCH|MINOR|MAJOR> — <the change that forces this level>
- Manifests: <which ones moved, old -> new>
- Docs: <changelog / README / CLAUDE.md updated, or "no update needed" and why>

<attribution footer exactly as configured in settings — see the commit skill>
```

That is a multi-line message: write it to a temp file and `git commit -F`, never `-m`. Omit the
attribution footer only when settings supply none.

### Step 10 detail — tag and release _after_ merge

The release skill commits the bump to `main` directly; here the bump already landed via the PR, so
**skip its commit step** and run only the tag + release, on `main`, once the merge is in:

```bash
git checkout main && git pull origin main      # the merge commit is now HEAD
git tag -a vX.Y.Z -m "vX.Y.Z — <summary>"      # annotated; points at the merge commit
git push origin vX.Y.Z
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file <changelog-section-file>
```

Reuse the vX.Y.Z section you wrote in step 4 as the release notes (`--notes-file`).

## Rules

- **One version, everywhere.** Every manifest the project ships reads the same vX.Y.Z before the
  commit in step 7.
- **Tag the merge commit on `main`**, never the feature branch — `git pull origin main` after the
  merge first, then tag.
- **Never tag or release on a red gate.** CI must be green and required approvals met (step 9)
  before step 10. Surface a red gate and wait; do not merge or tag around it.
- **Versions only increase.** When the bump level is unclear, PATCH.
