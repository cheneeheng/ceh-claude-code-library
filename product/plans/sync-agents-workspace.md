---
schema: plan/v1
title: Give every git worktree its own worktree of the .agents_workspace repo, and merge it back
status: built
created: 2026-10-28
---

## Goal

A git worktree is a fresh checkout of tracked files, so the nested `.agents_workspace` repo (the
decision log, handoffs, business material) is missing there, and every skill that reads or writes
it sees an empty workspace. Hooks in `ceh-git-workflow` give each linked worktree a git worktree of
the workspace repo at `<worktree>/.agents_workspace`, on its own branch, then commit and merge that
branch back into whichever branch the main checkout's workspace has checked out. The flow that
matters: `claude --worktree <name>`, a skill appends to `.agents_workspace/DECISION_LOG.md` with
Edit, and after the session ends the entry is in the main checkout's log.

## Scope

**In:**

- **Create:** when a session starts in a linked git worktree, and the main checkout has a
  `.agents_workspace` git repo while the worktree has no `.agents_workspace`, the hook runs
  `git worktree add` in the workspace repo to create `<worktree>/.agents_workspace` on the branch
  `ceh-ws/<X>/<worktree folder name>`, where `<X>` is the branch the main workspace has checked
  out. A new branch starts from that `HEAD`; a branch left by an earlier worktree of the same name is
  reused.
- **Commit:** after each turn in such a worktree, the hook commits every change in
  `<worktree>/.agents_workspace` to its `ceh-ws/` branch, so a worktree removed later loses no
  committed workspace file.
- **Merge:** when a session in such a worktree ends, the hook commits once more and merges the
  `ceh-ws/` branch into `<X>` in the main workspace, uncommitted changes there included.
  `DECISION_LOG.md` merges with git's `union` driver, so two sessions appending do not conflict.
- **Catch-up:** when a session starts in a main checkout, the hook prunes workspace worktrees whose
  folder is gone, merges every `ceh-ws/<X>/` branch that is not yet merged into `<X>`, and deletes a
  merged branch that no worktree has checked out. A merge that fails, by conflict or by refusal, is
  aborted, its branch is kept, and the hook names it in the session's context so the agent can
  merge it by hand.
- The hook does nothing outside git, in a worktree whose `.agents_workspace` is not on a `ceh-ws/`
  branch, or when the main checkout has no `.agents_workspace` git repo.
- `CEH_DISABLED_HOOKS=sync-agents-workspace` turns it off, like every other hook here.
- The plugin README documents the hook (hooks table with its column renamed to Hook, the
  Prerequisites line, the scripts table, and the limits: no subagent worktrees, `EnterWorktree` per
  Phase 3), and `docs/CROSS_REFERENCES.md` lists its copy of the kill switch.

**Out:**

- A link (junction or symlink) to the main workspace: tested 2026-10-28, Claude Code's worktree
  isolation refuses Edit and Write through a link to any folder outside the worktree.
- A `WorktreeCreate`/`WorktreeRemove` pair: `WorktreeRemove` fires only for worktrees a
  `WorktreeCreate` hook made, and that hook replaces Claude Code's whole creation (base ref fetch,
  `.worktreeinclude`, pull request worktrees, the cleanup sweep's marker). It also never fires for a
  worktree that is kept, so its work would never merge.
- A git `post-checkout` hook: it needs setup in every repo, and pre-commit's `core.hooksPath`
  conflict rules out a global one. The plugin installs once for all projects.
- `.worktreeinclude`: it copies, and a copy of the nested repo has no branch to merge back.
- Subagent worktrees (`isolation: "worktree"`): `SessionStart`, `Stop` and `SessionEnd` do not fire
  for subagents. `agent-coding-contract` dispatches parallel editing subagents this way and tells
  them to append to the decision log, so their entries stay in their own worktree and are lost with
  it. That is accepted for now: those subagents are short-lived, and their parent session logs the
  decisions that bind the work.
- Mid-session `EnterWorktree`: `CwdChanged` fires on a shell `cd`, and the docs do not say it fires
  on `EnterWorktree`. The hook covers sessions that start in a worktree (`claude --worktree`, or
  `claude` launched inside one). Phase 3 records whether `EnterWorktree` is covered too.
- Union merge for other Markdown files: a union merge keeps both sides' lines, which garbles a file
  edited in place, such as `BUSINESS_PLAN.md` or a handoff. Those merge normally and report a
  conflict.
- Pushing `ceh-ws/` branches: the hook never pushes. The `<X>` segment in the name keeps one
  project's branches apart from another's if a sync outside this plugin pushes every branch of a
  workspace remote that holds one branch per project.
- Bare repos and separate git dirs: the main checkout is the parent of the common `.git`
  directory, and the hook does nothing when that directory is not named `.git`.

## Design

- **Home:** `ceh-git-workflow`, because the hook is git worktree and branch mechanics, and the
  plugin already ships the Python hook shape it copies (`branch-guard.py`). `ceh-coding-conduct` owns
  the decision log rule, but the workspace also holds handoffs, business material and research
  notes that no coding plugin writes, and `ceh-coding-conduct` has no Python hook today.
- **One script**, `plugins/standalone/ceh-git-workflow/scripts/sync-agents-workspace.py`, stdlib
  only, run as `python3 -I -S` with the event as its argument:
  - `SessionStart` (matcher `startup|resume`), argument `start`: in a linked worktree, create; in a
    main checkout, catch up.
  - `Stop`, argument `commit`.
  - `SessionEnd`, argument `end`: commit, then merge. It merges even when the commit fails, and does
    nothing when the `cwd` folder no longer exists.
- **Where it runs:** the script reads `cwd` from the hook payload and never uses `os.getcwd()`. It
  exits 0 when `cwd` is missing. The fixture runner starts every script from the repo root, so this
  keeps a fixture off the developer's real `.agents_workspace`.
- **Finding the checkouts:** one git spawn,
  `git -C <cwd> rev-parse --path-format=absolute --show-toplevel --git-dir --git-common-dir`. A
  linked worktree is one whose `--git-dir` differs from `--git-common-dir`, and its main checkout is
  the parent of `--git-common-dir` when that directory is named `.git`. The workspace repo is
  `<main checkout>/.agents_workspace` when `git -C` there reports its own top level as that path.
- **Create:** `git worktree prune`, then `git worktree add <path> <branch>` when the branch exists,
  otherwise `git worktree add -b <branch> <path>`.
- **Commit:** `git status --porcelain --branch` in `<worktree>/.agents_workspace` gives the branch
  and the changes in one spawn. When the branch starts with `ceh-ws/` and there are changes,
  `git add -A` then `git commit -m "ceh-ws: <worktree folder name>"`. A quiet turn costs two spawns.
- **Merge:** in the main workspace, skipped when a merge is already in progress there
  (`MERGE_HEAD` exists), so the hook never aborts the user's own merge. Otherwise
  `git -c core.attributesFile=<plugin>/assets/union.attributes merge --autostash --no-edit <branch>`.
  `--autostash` (git 2.27+) stashes the main workspace's uncommitted changes and reapplies them,
  because git refuses a merge over a dirty file and `DECISION_LOG.md` is usually dirty there. The
  attributes file holds `DECISION_LOG.md merge=union`. It is passed per command, so neither the
  user's repo nor their global config changes. When the merge fails and left a merge in progress,
  the hook runs `git merge --abort`, and the branch is kept either way.
- **SessionEnd budget:** the docs give SessionEnd hooks 1.5 s by default, and a plugin hook's
  `timeout` does not raise it. `end` took 0.98 s on Windows against a copy of this repo's
  workspace, inside the budget but not by much. When the budget is missed, catch-up merges the
  branch at the next main-checkout session start.
- **Output:** silent on success. Catch-up prints `hookSpecificOutput.additionalContext` only for a
  branch whose merge failed, naming it and the command to merge it by hand. Every other failure
  exits 0 silently, because a convenience hook must never stop a session. It follows
  `branch-guard.py`'s shape: the `CEH_DISABLED_HOOKS` kill switch first, then `main()` under
  `if __name__ == "__main__"`.
- **Removal:** a removed worktree takes `<worktree>/.agents_workspace` with it, but its commits stay
  on the `ceh-ws/` branch in the shared workspace repo. Only a change made after the last `Stop` is
  lost, and catch-up prunes the stale worktree entry.
- **Fixture runner:** `checks/hooks.py` runs each fixture as one process and checks only exit code,
  stdout and stderr. It gains two optional fixture keys: `before`, a function run just before the
  script, and `after`, a function run just after it that returns an error message or `None`, which
  the runner reports with `fail`. Fixtures already run in list order, so a sequence of fixtures
  shares one tmp repo.
- **Fixtures:** one tmp project with a workspace repo on branch `ws` and a linked worktree `wt`.
  Every fixture's env sets `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME` and
  `GIT_COMMITTER_EMAIL`, because the CI runner has no git identity. In order:
  1. `start` in `wt` with the kill switch: `wt/.agents_workspace` does not exist after.
  2. `start` in `wt`: `wt/.agents_workspace/DECISION_LOG.md` exists, on `ceh-ws/ws/wt`.
  3. `commit` in `wt` after appending `w1` to the worktree's log: the branch has the commit.
  4. `end` in `wt` after the main workspace commits a line `m1` and leaves `m2` uncommitted: the
     main log holds `w1`, `m1` and `m2`, `m2` is still uncommitted, and no merge is in progress.
  5. `start` in the main checkout after a conflicting edit to a non-union file on both sides:
     stdout names `ceh-ws/ws/wt`, no merge is in progress, and the main file is unchanged.
  6. `start` in `wt` after removing `wt/.agents_workspace` by hand: the folder is back, on the
     reused branch.
  7. `start` in the main checkout with no `cwd` in the payload: no output, nothing changed.
- **Version:** one PR, `ceh-git-workflow` PATCH, because a hook is neither a skill nor an agent nor
  a dependency change.

## Phases

### Phase 1: Create the workspace worktree

- **Builds:** the fixture runner's `before` and `after` keys, the script's `start` path for a linked
  worktree, the `SessionStart` wiring in `hooks/hooks.json`, fixtures 1, 2, 6 and 7.
- **Check:** `python tools/validate-plugins/validate.py` passes, and its `hooks` check runs the new
  fixtures.
- **Status:** done, `python tools/validate-plugins/checks/hooks.py` printed "OK: hooks check
  passed" (fixtures 34 to 37 failed with "no hooks.json runs this script" before the script);
  `validate.py`'s only failures are 25 hygiene hits in the git-ignored `docs/starlight/node_modules/`
  and `plugins/*/*/evals/results/`

### Phase 2: Commit, merge and catch up

- **Builds:** the `commit` and `end` paths, the main-checkout `start` path (catch-up),
  `assets/union.attributes`, the `Stop` and `SessionEnd` wiring, fixtures 3 to 5, the README edits,
  the `docs/CROSS_REFERENCES.md` row, the PATCH bump in `plugin.json` and `marketplace.json`, the
  `CHANGELOG.md` entry and the `docs/PLUGIN_VERSIONS.md` row.
- **Check:** `python tools/validate-plugins/validate.py` passes. Then a scratchpad copy of this
  repo's real `.agents_workspace` as the workspace of a tmp project with a worktree, run through
  `start`, an appended line in the worktree's log, `end` with an uncommitted line in the main log,
  and `start` in the main checkout: the main log holds both lines and `git -C <copy> log` shows the
  merge.
- **Status:** done, `python tools/validate-plugins/checks/hooks.py` printed "OK: hooks check
  passed" (fixtures 36 to 38 failed before the code); the scratchpad run on a copy of the real
  workspace left both lines in the main log, `2fbeae7 ceh-ws: t` on top of `<X>`, and the main
  workspace's uncommitted and untracked files in place

### Phase 3: Live check in Claude Code

- **Builds:** nothing new: it proves the wiring in a real session.
- **Check:** manual, because it needs an interactive session with the updated plugin installed:
  `claude --worktree ws-test`, ask it to append a line to `.agents_workspace/DECISION_LOG.md` with
  Edit, exit and keep the worktree. Passing: the line is in the main checkout's
  `.agents_workspace/DECISION_LOG.md`. Then repeat with `EnterWorktree`, and record the result in
  the README's limits line.
- **Status:** done, by the user's manual run on Windows on 2026-10-28 on 1.4.7, which this check
  needs because it takes an interactive session. Before that, the user's run on 1.4.6: the line reached the main log only when
  the next session's catch-up merged it (`Stop` commit 11:43:11, merge 11:45:32), not at exit, and
  `EnterWorktree` created no workspace. Both are fixed by
  `product/plans/sync-agents-workspace-exit.md`, whose Phase 2 repeats this check. On 1.4.7 both
  work, see that plan's Phase 2

## Open

None. The merge trigger (on `SessionEnd`, a commit every turn, catch-up at the next main-checkout
session start) was chosen by the user on 2026-10-28. The review's two owner questions were taken
by their recommended answers: `--autostash`, which leaves the user's uncommitted work uncommitted,
and union merge for `DECISION_LOG.md` only.

## Record

- 2026-10-28 Planned: status ready
- 2026-10-28 Reviewed: Revise first, 1 blocking (Phase 1 omits hook fixtures in tools/validate-plugins/checks/hooks.py, so validate.py fails)
- 2026-10-28 Design changed: was "A hook in `ceh-git-workflow` makes `.agents_workspace` in a linked worktree a link to the main checkout's copy", now "a git worktree of the workspace repo on a `ceh-ws/` branch, committed each turn and merged back", because Claude Code's worktree isolation refused Edit and Write through a link in a live test
- 2026-10-28 Reviewed: Revise first, 3 blocking (hooks.py fixtures cannot assert file or branch state; script's cwd source unstated, so fixtures could hit the real workspace; merge refuses a dirty main DECISION_LOG.md, so use --autostash)
- 2026-10-28 Design changed: was "plan file `product/plans/link-agents-workspace.md`", now "`product/plans/sync-agents-workspace.md`", because the plan no longer links anything; both reviews in `.agents_workspace/product/plan-reviews/` name the old path
- 2026-10-28 Built Phase 1: python tools/validate-plugins/checks/hooks.py, OK: hooks check passed
- 2026-10-28 Built Phase 2: python tools/validate-plugins/checks/hooks.py, OK: hooks check passed
- 2026-10-28 Design changed: was "A commit and a merge are about six git spawns, roughly 0.3 s on Windows", now "`end` took 0.98 s on Windows", because the scratchpad run measured it
- 2026-10-28 PR: #169 https://github.com/cheneeheng/ceh-claude-code-library/pull/169
- 2026-10-28 PR: #171 https://github.com/cheneeheng/ceh-claude-code-library/pull/171
- 2026-10-28 Built Phase 3: the user's manual run in Claude Code on Windows on 1.4.7, exit merge and EnterWorktree both work
- 2026-10-28 Checked: 29 Built, 2 Deviation, 1 Extra; Deviation: Design "`SessionEnd` ... `end`: commit, then merge" is now a detached end-worker (sync-agents-workspace.py:14, superseded by product/plans/sync-agents-workspace-exit.md); Deviation: Design "When the branch starts with `ceh-ws/`" is an exact match on the computed branch (sync-agents-workspace.py commit()); Extra: Out "Mid-session `EnterWorktree`" is now covered (hooks.json:17 `"matcher": "EnterWorktree"`, planned by the exit plan)
- 2026-10-28 PR: #172 https://github.com/cheneeheng/ceh-claude-code-library/pull/172
