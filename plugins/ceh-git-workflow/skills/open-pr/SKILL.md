---
name: open-pr
description: >-
  Load this skill when creating or opening a pull request, any phrasing —
  create/open/raise/make/submit/send a PR, pull request, or merge request, or pushing a branch for
  review. For opening the PR alone — a compound 'commit, open a PR and merge it' is
  ceh-git-workflow:merge-flow, which sequences this skill with the rest. Covers the PR title, the
  What/Why/How/Testing/Checklist template, size limits, the author self-review checklist, and
  enabling GitHub auto-merge on repos that allow it so the PR lands itself when the gate goes green.
compatibility: >-
  Requires the git CLI on PATH, the GitHub CLI (`gh`) installed and authenticated via `gh auth
  login`, a git repository with a GitHub remote, push permission, and network access. The pre-PR
  checks it recommends run the target repo's own toolchain, not assumed here.
---

# Opening a Pull Request

A PR opens only after the definition of done and the author self-review pass, with a Conventional
Commits title, the What/Why/How/Testing/Checklist body, and auto-merge queued on repos that allow
it.

## Procedure

1. Check the definition of done for the change type and the author self-review (below).
2. Write the PR body to a temp file and pass it with `--body-file`, then delete the file. Never
   inline the body with a shell heredoc or a PowerShell `@'...'@` here-string: the temp-file path
   avoids all shell quoting and behaves identically in PowerShell and Bash. The same applies to
   later edits (`gh pr edit <N> --body-file body.md`).

   ```bash
   # Write the body to body.md:
   #   ## What
   #   ## Why
   #   ## How
   #   ## Testing
   #   ## Checklist
   #   - [ ] All CI checks pass
   #   - [ ] Tests added or updated for new behavior
   #   - [ ] No `any` / `@ts-ignore` / `# type: ignore` introduced
   #   - [ ] No secrets or credentials in code
   #   - [ ] Migrations (if any) are backward-compatible
   #   - [ ] ARCHITECTURE.md Key Decisions updated (if a durable decision was made)
   #   - [ ] Attribution included if AI tooling assisted
   git push -u origin <branch-name>
   gh pr create --title "<type>(<scope>): <short summary>" --body-file body.md
   rm body.md

   # On repos that allow it, queue auto-merge so the PR lands itself when the gate goes green:
   if [ "$(gh api repos/{owner}/{repo} --jq .allow_auto_merge)" = "true" ]; then
     gh pr merge --merge --auto
   fi
   gh api repos/{owner}/{repo} --jq .delete_branch_on_merge   # false: tell the user the branch survives
   ```

3. Open as a **draft** while CI runs or the work is still settling; mark ready for review only once
   the self-review checklist passes. Request the reviewers the approval rules require (see below).

## Size guidelines

| PR type      | Recommended                                               | Max     |
| ------------ | --------------------------------------------------------- | ------- |
| Bug fix      | ≤ 200 LOC                                                 | 300 LOC |
| New feature  | ≤ 400 LOC                                                 | 600 LOC |
| Refactor     | ≤ 500 LOC                                                 | 800 LOC |
| DB migration | Migration file only; split app changes into a separate PR |         |

If a PR exceeds the guideline, split it by layer (schema → service → API).

## PR title

Must follow Conventional Commits format. It titles the PR and seeds the merge commit subject.
Same rules as a commit subject: imperative, lowercase, no trailing period, ≤ 72 chars.

## PR description template

```markdown
## What

<!-- One sentence: what does this change do? -->

## Why

<!-- Why is this change needed? Link to ticket/issue. -->

## How

<!-- Brief explanation of approach if non-obvious. -->

## Testing

<!-- What was tested? What test cases were added? -->

## Checklist

- [ ] All CI checks pass
- [ ] Tests added or updated for new behavior
- [ ] No `any` / `@ts-ignore` / `# type: ignore` introduced
- [ ] No secrets or credentials in code
- [ ] Migrations (if any) are backward-compatible
- [ ] ARCHITECTURE.md Key Decisions updated (if a durable decision was made)
- [ ] Attribution included if AI tooling assisted
```

### How to write each section

- **What** — the change in one sentence, stated as an outcome for the reader, not a list of files.
- **Why** — the problem or request that motivated it; link the ticket/issue (`Closes #NNN`).
- **How** — only the non-obvious decisions: the approach taken and the alternatives rejected. Skip
  if the diff is self-explanatory.
- **Testing** — what you actually ran and what you added, so a reviewer can reproduce it. "Manually
  verified X" is fine when honest; never imply coverage you didn't add.
- **Attribution** — the checklist item is satisfied by the `attribution.pr` value from Claude Code
  settings, surfaced verbatim in the session's Git instructions. Append that line to the end of the
  body exactly as given; never substitute a literal from this skill or from memory. If settings set
  `attribution.pr` to `false`/empty, or no attribution line is supplied, omit it and check the box.

### Filled-in example

```markdown
## What

Cancel bulk orders in one request instead of one call per order.

## Why

Support flagged 30+ manual single-cancels per incident. Closes #342.

## How

New POST /orders/cancel-bulk validates ≤100 IDs, then reuses the existing
cancel_order() service in a single transaction. Rejected a queue-based
approach — synchronous is simpler and the cap keeps it bounded.

## Testing

Unit tests for the 100-ID cap and partial-failure rollback. Integration
test against a seeded DB. `pytest` + `mypy --strict` green locally.

## Checklist

- [x] All CI checks pass
- [x] Tests added or updated for new behavior
- [x] No `any` / `@ts-ignore` / `# type: ignore` introduced
- [x] No secrets or credentials in code
- [x] Migrations (if any) are backward-compatible
- [ ] ARCHITECTURE.md Key Decisions updated (if a durable decision was made)
- [x] Attribution included if AI tooling assisted

<attribution footer exactly as configured in settings — see Attribution above>
```

## Definition of done

Before opening the PR, verify the change meets the bar for its type.

**Bug Fix**

- [ ] Root cause identified and documented in the PR description
- [ ] Failing test added that reproduces the bug
- [ ] Fix applied — the failing test now passes
- [ ] No regressions — full test suite passes
- [ ] Lint and type checks pass

**Feature**

- [ ] Unit tests for new business logic
- [ ] Integration tests for new API surface
- [ ] Lint and type checks pass
- [ ] PR description explains the feature and how it was tested
- [ ] No `any`, `@ts-ignore`, or `# type: ignore` introduced

**Refactor**

- [ ] No behavioral change — proven by existing tests passing unchanged
- [ ] Coverage unchanged (no tests deleted to make the refactor pass)
- [ ] Lint and type checks pass
- [ ] PR description explains what structural problem was addressed

### Coverage targets

| Area                                  | Minimum |
| ------------------------------------- | ------- |
| Python application package            | 80%     |
| Core business logic / domain services | 95%     |
| TypeScript `src/lib/`                 | 70%     |

`mypy --strict` and `tsc --noEmit` must pass with zero errors. Do not reduce strictness to meet
coverage targets — fix the types.

## Author self-review

- [ ] Read full diff (`git diff main...HEAD`) before requesting review
- [ ] No commented-out code or debug logs
- [ ] No `TODO` without a linked ticket
- [ ] Branch is rebased on latest `main`
- [ ] PR is scoped to one concern

## Rules

- Required approvals:
  - Bug fixes and small features: 1 approval
  - New API surfaces, schema changes, security changes: 2 approvals
  - Hotfixes: 1 approval minimum (do not bypass CI)
- **Merge commit only** — never squash, never rebase-merge; every commit lands on `main` as
  written. Because commits are not collapsed at merge time, keep them Conventional Commits format
  and clean the branch as you go. Full merge mechanics and post-merge cleanup load when you say
  "merge the PR".

## Auto-merge

If the repo has auto-merge enabled (`allow_auto_merge`), enable it on the PR right after creating
it so the PR lands itself the moment the gate (CI + approvals, enforced server-side via branch
protection) goes green — no separate "merge it" step and no release flow required. This is the
hands-off path for repos configured for it; on repos without auto-merge, the explicit merge skill
handles landing the PR. A draft PR is safe to queue — auto-merge waits until the PR is marked ready.

```bash
if [ "$(gh api repos/{owner}/{repo} --jq .allow_auto_merge)" = "true" ]; then
  gh pr merge --merge --auto   # queues; lands when CI + approvals go green
fi
```

**Do not pass `--delete-branch`.** Claude Code's permission classifier reads it as a destructive
flag and blocks the whole command, so queuing the merge fails. The head branch is therefore deleted
only when the repo has **Automatically delete head branches** enabled — check with
`gh api repos/{owner}/{repo} --jq .delete_branch_on_merge` and tell the user when the answer is
`false`, so they know the branch will still be there after the PR lands and that
`git push origin --delete <branch-name>` removes it.

To merge immediately (gate already green) or to merge a local branch with no PR, use the merge
skill.
