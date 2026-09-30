---
name: merge
description: >-
  Load this skill when merging and cleaning up after, any phrasing — merge/land/integrate a PR or a
  local branch, 'merge it', 'merge and delete the branch', 'clean up the branch', 'merge this branch
  into main'. For the merge alone — a compound 'commit, open a PR and merge it' is
  ceh-git-workflow:merge-flow, which sequences this skill with the rest. Covers both the PR-merge
  case (gh pr merge, including auto-merge) and the local no-PR branch-merge case (git merge --no-ff
  into main), the pre-merge gate (CI green, approvals, rebased, clean history), merge-commit
  strategy (no squash/rebase-merge), and post-merge cleanup (delete the local branch, report whether
  the remote branch survived, return to main, pull).
compatibility: >-
  Requires the git CLI on PATH and a git working tree. The PR path additionally requires the
  GitHub CLI (`gh`) installed and authenticated via `gh auth login`, a GitHub remote, push
  permission, and network access; the local no-PR path needs git alone.
---

# Merging

Owns the merge and cleanup moment for two cases:

- **PR merge** — landing a pull request through GitHub (immediately, or queued via auto-merge).
  To author the PR first, say "open a PR". On repos that allow auto-merge, `open-pr` already queues
  the merge at PR-creation time — use this skill when you want to merge _now_, or to queue a PR on a
  repo where it wasn't enabled at creation.
- **Local branch merge** — integrating a local feature branch into `main` with no PR (solo repos,
  low-risk work, or the no-PR variant of the release flow). See "Local branch merge" below.

Both cases share the same merge-commit strategy and post-merge cleanup; the pre-merge gate applies
to whichever signals exist (CI/approvals only apply when the branch is on a remote with them).

## Procedure

1. Check the pre-merge gate (below). If the branch won't merge cleanly, resolve conflicts first.
2. Merge: PR merge & cleanup, or Local branch merge (below).
3. Report the remote branch state.

## Pre-merge gate

Do not merge until all hold:

- [ ] All CI checks pass — never merge red, never bypass CI
- [ ] Required approvals met (1 for bug fixes / small features; 2 for new API surfaces, schema, or
      security)
- [ ] Rebased on latest `main`
- [ ] History clean — fixup/WIP/debug commits squashed or dropped; every commit Conventional
      Commits format

### Reading CI status

Read the gate with `gh run` (Actions API), anchored to the **commit**, never to the branch:

```bash
gh run list -c "$(git rev-parse HEAD)"                    # runs for this exact commit
gh run watch "$(gh run list -c "$(git rev-parse HEAD)" -L1 --json databaseId -q '.[0].databaseId')" --exit-status
gh run view <run-id> --log-failed                          # why it went red
```

`gh run watch --exit-status` blocks until the run finishes and exits non-zero on failure, so it
chains with `&&` into the merge command.

Three traps, all of which make a red build look green or a green build look broken:

- **`gh pr checks` and `gh pr view --json statusCheckRollup` fail with a fine-grained PAT** that
  lacks the `checks=read` permission — HTTP 403, named in the response's
  `X-Accepted-Github-Permissions` header. That is a _permissions_ error, not a red gate. Do not
  report it as CI failure and do not merge around it; use `gh run` instead. Other `gh pr view`
  fields (`state`, `mergeable`, `mergeStateStatus`, `reviewDecision`) work fine.
- **`gh api repos/{owner}/{repo}/commits/<sha>/status` is not a substitute.** It returns HTTP 200,
  which makes it look usable, but it is the legacy Commit Statuses API and Actions never writes to
  it — `{"state":"pending","total_count":0}` forever. Anything gating on it never sees red.
- **`gh run` only sees GitHub Actions runs in this repo.** It is blind to checks posted by third
  parties (Codecov, Sonar, any GitHub App). On a repo that has those, `gh run` alone is not the
  full gate — either read the rollup (requires `checks=read` on the token) or check them by hand.

`gh pr view <N> --json mergeStateStatus` does reflect check state without the `checks` permission
(`CLEAN` / `UNSTABLE` / `BLOCKED`) and is a valid merge gate — but `UNSTABLE` cannot distinguish a
pending non-required check from a failing one, so it diagnoses nothing. Use it to gate, `gh run`
to diagnose.

## Resolving conflicts

If the branch won't merge cleanly, rebase it on `main` and resolve there — never resolve inside
the merge commit:

```bash
git checkout <branch-name>
git fetch origin && git rebase origin/main
# resolve conflicts, then for each file:
git add <file> && git rebase --continue
git push --force-with-lease            # your own feature branch only
```

Re-run CI after the rebase; the pre-merge gate applies to the rebased state, not the pre-conflict
one.

## PR merge & cleanup

Prefer `--auto` when the repo allows it: GitHub queues the merge and lands it the moment the gate
(CI + approvals, enforced server-side via branch protection) goes green. Probe for support and fall
back to a direct merge (which requires the gate already green):

```bash
if [ "$(gh api repos/{owner}/{repo} --jq .allow_auto_merge)" = "true" ]; then
  gh pr merge <number> --merge --auto   # queues; lands when the gate goes green
else
  gh pr merge <number> --merge          # gate must already be green
fi
git checkout main && git pull origin main   # return to main and sync
git branch -d <branch-name>                 # only if a local copy lingers (e.g. merged via UI)
git fetch --prune                           # drop stale remote-tracking refs
```

**Do not pass `--delete-branch`.** Claude Code's permission classifier reads it as a destructive
flag and blocks the whole command, so the merge itself fails. Leave remote-branch cleanup to the
repo setting instead, and report the result — see "Reporting the remote branch" below.

`git branch -d` (lowercase) refuses an unmerged branch — do not force with `-D` unless you intend
to discard unmerged commits. For "create a PR, merge it, delete the branch", chain this after the
PR opens. Never bypass CI — surface a red gate and wait rather than merging red.

## Local branch merge

When there is no PR — a local feature branch going straight into `main` (solo repos, low-risk work,
or the no-PR release flow) — merge with an explicit merge commit and clean up the same way. Still a
**merge commit only** (`--no-ff`); never fast-forward away the branch's history. Apply the pre-merge
gate to whatever signals exist: rebased on latest `main`, history clean, and any local checks
(tests, lint, type-check) green — there are no server-side CI/approval gates to lean on here.

```bash
git checkout <branch-name>
git fetch origin && git rebase origin/main   # rebase first so the merge is a clean fast-forward base
git checkout main && git pull origin main
git merge --no-ff <branch-name>              # explicit merge commit; reuse the Conventional Commits subject
git push origin main
git branch -d <branch-name>                  # lowercase: refuses if somehow unmerged
git push origin --delete <branch-name>       # only if the branch was ever pushed
```

Give the merge commit the same kind of message as the PR case — a Conventional Commits subject plus
a line of "why" — so `git log main` reads on its own. Never `--no-ff` past a failing local check;
fix it on the branch first.

## Rules

- **Merge commit only** — never squash, never rebase-merge. Commits land on `main` as written
  (the per-PR history is kept on purpose as source material for write-ups), so clean the branch
  first.
- The merge commit is a real commit — give it a message that reads on its own in `git log main`,
  not GitHub's default `Merge pull request #N from user/branch`:

  ```
  Merge pull request #<N>: <type>(<scope>): <PR title>

  <one line on what the PR delivers and why it's landing>
  ```

  - Subject: reuse the PR's Conventional Commits title so `main`'s history stays scannable.
  - Body: one or two lines of context — the "why", and anything a future bisect would want
    (e.g. "behind feature flag X", "requires migration 0042"). Skip if the PR title says it all.
  - With the CLI, `gh pr merge <N> --merge --subject "..." --body "..."` sets it explicitly;
    otherwise edit the message in the GitHub merge dialog before confirming. If the body spans
    more than one line, write it to a temp file and pass `--body-file <file>` (then delete it)
    rather than an inline `--body` — the temp-file path avoids shell quoting and works the same
    in PowerShell and Bash.

## Output

### Reporting the remote branch

The merge no longer deletes the head branch, so the remote branch is gone only if the repo has
**Automatically delete head branches** enabled. Read the setting and tell the user which case they
are in — never claim the branch was deleted without checking:

```bash
gh api repos/{owner}/{repo} --jq .delete_branch_on_merge
```

- `true` — report that the PR merged and GitHub deleted the remote branch.
- `false` — report that the PR merged and **the remote branch still exists**, plus the one command
  that removes it: `git push origin --delete <branch-name>`.

Report the same when auto-merge is queued rather than merged now: the branch outlives the queue
either way, and the user should know a stale branch may be left behind.
