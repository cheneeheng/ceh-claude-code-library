---
schema: plan/v1
title: Make the workspace sync merge at session exit, and cover EnterWorktree
status: building
created: 2026-10-28
---

## Goal

Two gaps found in the live check of `product/plans/sync-agents-workspace.md` (Phase 3). First, a
`claude --worktree ws-test` session that exited with "keep" did not merge its workspace branch:
the `Stop` commit landed at 11:43:11, and the merge came only from the next session's catch-up at
11:45:32. Second, a session that enters a worktree with `EnterWorktree` gets no workspace. After
this change, the exit merges the branch whatever the cause of the first gap, and `EnterWorktree`
creates the workspace the way a session start does.

## Scope

**In:**

- `end` starts a detached worker process and returns at once. The worker does the slow part, so
  the 1.5 s `SessionEnd` budget cannot kill it.
- The worker, in a linked worktree, commits and merges that worktree's branch, as `end` does today.
  In a main checkout, it runs catch-up, which merges every `ceh-ws/<X>/` branch, so the merge happens
  even when Claude Code reports the main checkout as `cwd` at exit.
- A `PostToolUse` hook with matcher `EnterWorktree` runs `start`, so entering a worktree mid-session
  creates its workspace.
- The README's Workspace sync section drops the `EnterWorktree` limit, says the exit merge runs in
  the background and that ending a session in the main checkout runs catch-up, and its hook table,
  scripts table and exit-budget bullet name `PostToolUse` (`EnterWorktree`).

**Out:**

- Proving which cause the first gap had (the budget, or `cwd` pointing at the main checkout): the
  user chose to fix both without a `--debug` run. The worker and the catch-up cover both.
- Pushing: the hook never pushes, and the user's own sync job pushes the workspace.
- `ExitWorktree` mid-session: exiting leaves the branch committed by `Stop`, and the session's
  `SessionEnd` (now catch-up from the main checkout) or the next session start merges it.

## Design

- **Worker launch:** `end` runs `subprocess.Popen([sys.executable, "-I", "-S", __file__,
"end-worker", cwd], cwd=<main checkout>)` with stdin, stdout and stderr on `DEVNULL`. The
  process's own working directory is the main checkout, so it never holds the worktree folder open
  and a "remove" at exit can delete it. On Windows the flags are
  `CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB`: `CREATE_NO_WINDOW`
  keeps a hidden console that the worker's `git.exe` children share, where `DETACHED_PROCESS` would
  flash a window per git call. When the job forbids breakaway (Popen raises `OSError`) it retries
  without `CREATE_BREAKAWAY_FROM_JOB`. On POSIX, `start_new_session=True`. Known limit: a job object
  that kills its children on close and forbids breakaway still kills the worker; the next session
  start's catch-up then merges.
- **Worker:** `end-worker <cwd>` takes `cwd` from `argv` and skips the stdin read. The kill switch
  stays word for word at the top of `main()`, above the `end-worker` branch, so it stops the worker
  too. The worker resolves the checkouts as before. In a linked worktree: commit, then merge. In a
  main checkout: `catch_up`, with its failures dropped, since `SessionEnd` output is discarded and
  the next session start reports them.
- **Concurrent merges:** a worker and a new session's catch-up can merge at once, and the one that
  loses on `index.lock` fails. `catch_up` re-checks `--no-merged` before reporting, so a branch the
  other process merged is not reported as failed.
- **EnterWorktree:** `hooks.json` gains `PostToolUse` with matcher `EnterWorktree` running
  `sync-agents-workspace.py start`. The hooks docs say `cwd` follows Claude into the worktree, so
  `start` reads it unchanged. Phase 2 checks that in a live session.
- **Fixtures:** the worker is still running when the script exits, so an `end` fixture's
  after-check polls for up to 20 s until every expected line is in the main log and the workspace is
  idle: no `MERGE_HEAD`, no `MERGE_AUTOSTASH` (where `--autostash` keeps its stash), and no
  `.git/index.lock`. The `end` fixture waits for `w1`, `m1` and `m2`. Two new fixtures on a second
  worktree `wt2`: `start` with an `EnterWorktree` `PostToolUse` payload creates
  `wt2/.agents_workspace` on `ceh-ws/ws/wt2`, then, after a line `v1` is committed there, `end` with
  the main checkout as `cwd` waits for `v1` and `m2`. That catch-up also retries `wt`'s conflicting
  branch, and the after-check confirms the main `notes.txt` is unchanged. `hooks.py` uses
  `TemporaryDirectory(ignore_cleanup_errors=True)`, so a timed-out poll on Windows reports its
  fixture instead of crashing cleanup.
- **Version:** `ceh-git-workflow` PATCH, 1.4.7.

## Phases

### Phase 1: Detached exit worker and EnterWorktree wiring

- **Builds:** the worker launch and `end-worker` path, the `PostToolUse` wiring, the fixture changes,
  the README edits, the PATCH bump in `plugin.json` and `marketplace.json`, the `CHANGELOG.md` entry
  and the `docs/PLUGIN_VERSIONS.md` row.
- **Check:** `python tools/validate-plugins/checks/hooks.py` prints "OK: hooks check passed", and
  the main-checkout `end` fixture fails before the change. The fixtures call the script directly, so
  they cannot prove the detachment or the `PostToolUse` wiring: Phase 2 does.
- **Status:** done, `python tools/validate-plugins/checks/hooks.py` printed "OK: hooks check
  passed" (fixture 41, `end` in the main checkout, timed out without `v1` before the change); in a
  scratch repo `end` returned in 212 ms and the merge landed about 600 ms later

### Phase 2: Live check in Claude Code

- **Builds:** nothing new.
- **Check:** manual, on Windows (the POSIX launch path stays unverified until run on Linux or
  macOS), because it needs an interactive session with 1.4.7 installed: (a)
  `claude --worktree ws-test3`, append a line to `.agents_workspace/DECISION_LOG.md`, exit and keep;
  within a few seconds the line is in the main checkout's log with no new session started. (b) In a
  session in the main checkout, ask it to enter a worktree; `.agents_workspace` appears in it.
- **Status:** todo. The user ran it on Windows on 2026-10-28 on 1.4.7 and reported (a) and (b)
  working. Exiting with "remove" instead of "keep" also merged the workspace changes. The
  workspace history shows the merged branches (`ceh-ws/ceh-claude-code-library/ws-test3` at
  `c946200`, `testing-1215` at `87f7007`) were in the main workspace's branch before their
  branches were deleted. Left `todo` because a user's report is not a check run. POSIX is still
  unverified

## Open

None.

## Record

- 2026-10-28 Planned: status ready
- 2026-10-28 Reviewed: Revise first, 3 blocking (DETACHED_PROCESS opens a console per git call; stash-list poll misses MERGE_AUTOSTASH and races the next fixture; Phase 1 Check claims end and wt2 start fixtures fail before the change)
- 2026-10-28 Built Phase 1: python tools/validate-plugins/checks/hooks.py, OK: hooks check passed
- 2026-10-28 PR: #170 https://github.com/cheneeheng/ceh-claude-code-library/pull/170
- 2026-10-28 PR: #171 https://github.com/cheneeheng/ceh-claude-code-library/pull/171
