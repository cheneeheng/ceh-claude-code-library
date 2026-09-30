---
name: merge-flow
description: >-
  Load this skill when landing the branch you are on: log the change under Unreleased in the
  changelog, refresh the README if user-facing, commit, open the PR, merge it, and clean up — with
  no version bump, no tag, and no GitHub release. Handles compound requests like "commit, open a PR
  and merge it", "get this branch into main", "wrap up this branch", "PR this and land it". This
  skill only sequences the steps and gates between them; each step is delegated to the skill that
  owns it (update-changelog, commit, open-pr, merge). Use ceh-git-workflow:release-flow when the
  same branch should also bump the version and publish a release, and the individual open-pr or
  merge skills for one step alone.
compatibility: >-
  Requires the git CLI on PATH, the GitHub CLI (`gh`) installed and authenticated via `gh auth
  login`, a git repository with a GitHub remote, push permission, and network access. The steps it
  delegates to may need the target repo's own toolchain; none is assumed.
---

# Merge Flow

Land a finished branch in one pass: **changelog (Unreleased) → README → commit → PR → merge →
cleanup**. No version bump, no tag, no release — the changes wait under `## [Unreleased]` until a
later release picks them up. This skill owns only the **ordering and the gate between each step**;
every step is delegated to the skill that already owns it, so nothing here is duplicated.

This is the sibling of `ceh-git-workflow:release-flow`: same pipeline, stopped at the merge.

## Procedure

It starts on the branch you are already on. Do **not** cut a fresh branch. The work being landed
is already committed or staged somewhere, and that branch is the one that gets the PR. Only two
states need handling before step 1:

- **On `main`** — the work has nowhere to go. Create a branch first (invoke the Skill tool with
  skill="ceh-git-workflow:branch"), carrying the uncommitted work over with `git checkout -b`.
- **Behind `main`** — rebase or merge `main` in before opening the PR, so the gate in step 5 is
  measuring the right tree.

Then run top to bottom. Each step gates the next — do not proceed past a red gate.

| #   | Step                                                                                                                                                           | Delegate to                                                                                        | Gate before next step                                                               |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | Confirm the branch — on a non-default branch, up to date with `main`                                                                                           | see above                                                                                          | Named feature branch, rebased on latest `main`                                      |
| 2   | Log the change under `## [Unreleased]` — **no version, no date header**                                                                                        | Invoke the Skill tool with skill="ceh-git-workflow:update-changelog" — tell it **Unreleased mode** | Bullets under `[Unreleased]`, no new versioned section, no manifest version touched |
| 3   | Refresh the README if the change is user-facing                                                                                                                | `ceh-readme:update-readme` if that plugin is installed, else a surgical edit                       | Updated, or "no update needed" recorded                                             |
| 4   | Commit the work + docs                                                                                                                                         | Invoke the Skill tool with skill="ceh-git-workflow:commit"                                         | Conventional Commits subject, attribution footer present, tree clean                |
| 5   | Open the PR — on repos that allow auto-merge, `open-pr` already queues it here                                                                                 | Invoke the Skill tool with skill="ceh-git-workflow:open-pr"                                        | PR open, self-review + definition-of-done passed                                    |
| 6   | Merge and clean up — if step 5 queued auto-merge, this just confirms it lands; otherwise prefer `--auto` (or a direct merge once green). Don't poll CI by hand | Invoke the Skill tool with skill="ceh-git-workflow:merge"                                          | CI green, approvals met, merged to `main`, remote-branch state reported             |

Stop at step 6. Tagging and publishing are `ceh-git-workflow:release-flow`'s job, on a later run.

## Rules

- **No version anywhere.** No manifest version changes, no `## [X.Y.Z]` changelog header, no tag,
  no GitHub release. If the branch turns out to need a release, stop and switch to
  `ceh-git-workflow:release-flow` rather than bolting a bump onto step 4.
- **The changelog entry is not optional.** Every landed branch leaves a trace under `[Unreleased]`,
  which is what makes the next release's notes writable from the changelog alone. A genuinely
  invisible change (a typo fix, a test-only tweak) is the one exception — record the skip.
- **Never merge on a red gate.** CI green and required approvals met before step 6. Surface a red
  gate and wait; do not merge around it.
- **Clean up after the merge.** Delete the local branch, report whether the remote branch survived,
  return to `main`, and pull — step 6's skill owns the detail.
