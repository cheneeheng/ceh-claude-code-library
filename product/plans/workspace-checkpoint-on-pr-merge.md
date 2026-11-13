---
schema: plan/v2
generated_from: workspace-checkpoint-on-pr-merge.yaml
generated_note: "Do not edit. artifact.py renders this file from workspace-checkpoint-on-pr-merge.yaml: edit the YAML, then run artifact.py render."
title: A merged pull request leaves a checkpoint commit in the agents workspace
status: building
created: 2026-11-13
---

<!-- prettier-ignore-start -->

## Goal

When a session merges a pull request, the `ceh-git-workflow` hooks commit the workspace repo in
`.agents_workspace/` with a subject naming the PR and a body holding its URL and merge commit,
so the workspace history shows which artifacts belong to which source change. The commit is made
by the existing `sync-agents-workspace.py` at Stop, after the agent has finished its records for
the turn, in the checkout that ran the merge, and only once GitHub reports the PR as merged.

## Scope

**In:**

- A `merge` event in `sync-agents-workspace.py`, wired to PreToolUse on Bash: when the command
  is about to run `gh pr merge`, it records the PR, by number or by branch, and the checkout
  as pending. It calls no network.
- The `commit` event (Stop) in `sync-agents-workspace.py`: for each entry pending for its own
  checkout that GitHub reports as `MERGED` after the entry was written, it makes one
  checkpoint commit in that checkout's workspace and clears the entry. A `CLOSED` PR, a PR
  merged before its entry was written, and an entry older than 14 days are cleared without a
  commit.
- A failure that leaves a pending entry without a checkpoint (no `gh`, a failed call, a failed
  commit) is shown to the user once per session and reason, naming the pending folder.
- Fixtures in `tools/validate-plugins/checks/hooks.py`, the `ceh-git-workflow` README, a PATCH
  bump from the version `workspace-sync-commit-message` leaves, the changelog entry and the
  `docs/PLUGIN_VERSIONS.md` row. Both phases land in one PR, so no released version records
  entries that nothing clears.

**Out:**

- Pushing the workspace repo: The daily sync already pushes, and a push from a hook is an outward action nobody asked
  for. It can be added once the checkpoint has run for a while.
- A checkpoint record file: The commit body holds the URL and the merge commit, and
  `git log --grep "checkpoint source pr"` lists every checkpoint. A file would repeat it.
- Merges made outside the session, in the browser or by auto-merge after the last session ends: No hook sees them. An entry left by a queued auto-merge is checked again at the next Stop
  in that checkout, and the checkpoint then holds whatever the workspace holds at that
  time, which the README says.
- Clearing the entry of a merge the user denied or `gh` refused: PreToolUse cannot know the outcome. The entry stays while the PR is `OPEN`, costs one `gh`
  call per Stop in that checkout, and expires after 14 days or when the PR merges or
  closes. The README says so.
- A merge in another repository, `gh pr merge` with `-R` or `--repo`: Its PR would be checked against the session's repo, so it is not recorded.
- Staging only the files that belong to the merged PR: Nothing records which workspace file belongs to which PR, and the daily sync already
  commits everything.
- A step in `ceh-git-workflow:pull-request`: The checkpoint is a fixed operation, so the hook owns it and the skill does not.
- A second hook script: The discussion asks to extend the existing mechanism, which already finds the workspace
  repo, its branch and its worktrees.
- A handler `if` filter such as `Bash(gh pr merge *)` in `hooks.json`: Whether it matches a merge inside a compound command, and from which Claude Code version,
  is unconfirmed, and a missed match is a missed checkpoint. The script filters the command
  itself. The cost is one Python start per Bash call, about what `skill-started-guard.py`
  already adds, and the filter can be added once measured.

## Design

- **Why a hook with no observed failure:** The user asked for this hook on 2026-11-13, which the vision's evidence bar accepts in
  place of an observed failure, as `decision-artifact-validation.md` records for the render
  hooks. `workspace-sync-commit-message` is built first, because this plan reuses its
  `chore(workspace):` form and edits the same script.
- **Recording the merge (`merge` event):** `hooks.json` gains a PreToolUse entry with matcher `Bash` running
  `sync-agents-workspace.py merge` with `"timeout": 10`, as the other PreToolUse entries
  have. It prints nothing and exits 0, so the command runs unchanged. It records before the
  command runs, because afterwards the branch may be deleted and `gh pr merge` prints
  nothing when its output is not a terminal. The script returns at once without a
  `gh pr merge` mention, before it starts any git process. Otherwise it splits simple shell
  command segments at separators outside quoted or escaped text, then tokenizes each
  segment with `shlex.split`. It drops leading shell words (`if`, `then`, `elif`, `else`,
  `do`, `while`, `until`, `!`, `{`, `time`) and leading `NAME=value` assignments, so
  `then gh pr merge 12` and `GH_PAGER= gh pr merge 12` count. Only a segment that then
  begins with the three tokens `gh`, `pr`, `merge` is considered, so
  quoted command mentions are ignored and quoted subjects may contain separators.
  It returns for `-R`, `--repo` and their attached forms. The PR
  reference is the first token that is not a flag and does not follow one of the flags that
  take a value (`-b`, `--body`, `-F`, `--body-file`, `-t`, `--subject`, `-A`,
  `--author-email`, `--match-head-commit`): digits, the number in a URL ending in
  `/pull/<n>`, or a branch name. With no such token it is the current branch, from
  `git branch --show-current` in `cwd`, and with a detached HEAD nothing is recorded. It
  never calls `gh`, so it adds no network wait before a merge, and the Open block of
  `ceh-git-workflow:pull-request`, which runs `gh pr create` and `gh pr merge --merge --auto`
  in one command before the PR exists, records the branch. So
  `sleep 30 && gh pr merge --merge` records the current branch and never 30.
- **The pending entry:** One file per reference in `<main checkout>/.agents_workspace/.git/ceh-checkpoint-pending/`,
  named `pr-<n>` or `branch-<SHA-256 hex digest of the complete reference>`. The fixed-length
  lowercase digest avoids slash/underscore and Windows case collisions and long filenames. Line 1
  is the top-level path of the checkout that ran the merge and line 2 the reference as
  written. The folder path comes from `checkouts()`, which the script already calls, so no
  extra process finds it. Creating, renaming and deleting a file is atomic, so two sessions
  never rewrite each other's entries, and a repeated `merge` event for one PR rewrites the
  same file.
- **Where the pending check sits (`commit` event):** In a main checkout it replaces the early return: the script lists the pending folder under
  `top`, and returns as today when the folder is missing or empty, which costs one directory
  read and no process. With entries it goes on to `workspace_repo()` and
  `current_branch()`. In a linked worktree it runs in the final branch of `main()`, right
  before the existing `commit(top, branch)` and under the same guard, the workspace being
  on `branch`, so the turn's changes go into the checkpoint and the regular commit then
  finds nothing. It does nothing while the workspace has `MERGE_HEAD`, `MERGE_AUTOSTASH` or
  `index.lock` in its git directory, so it never runs into the end-worker's
  `merge --autostash`.
- **Which entries a Stop handles:** Only entries whose line 1 is its own top level. A main checkout also takes an entry whose
  checkout no longer exists, and only when `git for-each-ref --no-merged=HEAD
  refs/heads/ceh-ws/<x>/<folder>` prints nothing, so that worktree's files are already
  merged back. It claims each entry first with `os.replace(<name>, <name>.<session id>)`,
  and a second session in the same checkout, finding the name gone, skips it. An entry kept
  for later is restored with an atomic hard link that refuses to overwrite a newer entry,
  then its claim is removed. A claimed file left by a crash expires like any other.
- **What happens to an entry:** Expiry first: a file whose modification time is over 14 days old is deleted with no call
  and no commit. Then `gh pr view <reference> --json state,number,url,mergeCommit,mergedAt`
  in the source checkout. All calls share one budget of 12 seconds inside the hook's 30,
  each getting the time that is left, with `subprocess.TimeoutExpired` caught as a failed
  call, and entries not reached wait for the next Stop. `MERGED` with `mergedAt` at or after
  the file's modification time less 60 seconds is committed, and the file deleted after the
  commit succeeds. `MERGED` earlier than that is an older PR, or a line in a heredoc that
  looked like a merge: the file is deleted with no commit. Before committing, search local
  workspace Git history for the PR URL and merge commit body line. An existing checkpoint
  clears a repeated event without another commit. `CLOSED` deletes the file. `OPEN`
  or a failed call keeps it.
- **The commit:** `git add -A`, then `git commit --allow-empty` in the workspace of that checkout: the main
  workspace on its branch, or the linked worktree's workspace on its `ceh-ws/` branch, which
  the end-of-session merge carries back. `--allow-empty` because a linked worktree commits at
  every Stop and is usually clean when the merge is confirmed, so without it most PRs would
  get no checkpoint. Subject `chore(workspace): checkpoint source pr #<n>`. For several PRs
  it is `chore(workspace): checkpoint source prs #<n>, #<m>`, and when that passes 72
  characters, `chore(workspace): checkpoint <k> source prs`, so a number is never cut. Body,
  one line per PR: `<url> merged as <mergeCommit.oid>`. Two `-m` arguments, no attribution
  line. A commit that fails keeps the entries, renamed back, for the next Stop.
- **Failures:** The script exits 0 on every path. `gh` is found with `shutil.which("gh")` and run by the
  path it returns. When it is missing, a call fails, or the commit fails, the Stop hook
  prints `{"systemMessage": "..."}` naming the PR, the reason and the pending folder. A
  marker file in the temp directory, named with a hash of the session id and the reason as
  `warn_once` in `artifact-render-hook.py` does, limits it to once per session and reason.
  The `merge` event never prints. `CEH_DISABLED_HOOKS=sync-agents-workspace` still disables
  everything.
- **No workspace repo:** `workspace_repo()` returns None when `.agents_workspace/` is not a git repo of its own. Both
  events then return without writing anything, so a project without a nested workspace repo
  is unaffected.
- **Fixtures:** `checks/hooks.py` writes a stub folder holding `gh` (a `sh` script, mode 0755) and `gh.cmd`,
  both printing the content of a file beside them and exiting with the code in a second
  file, and sets PATH to that folder, `os.pathsep`, and the inherited PATH, so `git` stays
  reachable on Windows and in CI. The new fixtures sit before the existing `sync("end", wt)`
  fixture, so no detached end-worker runs beside them.

  Recording fixtures for `merge`, each expecting one entry: a number, a `/pull/<n>` URL, a
  branch name, no reference (the current branch), `sleep 30 && gh pr merge --merge` (the
  current branch), `if true; then gh pr merge 12 --merge; fi`,
  `GH_PAGER= gh pr merge 12 --merge`, and the same PR twice (one file). Fixtures expecting no entry: `--repo`,
  a Bash command with no merge, `gh pr create --body "run gh pr merge 12"`, the kill switch,
  and no workspace repo.

  Fixtures for `commit`: `MERGED` with a dirty workspace in a main checkout and in a linked
  worktree; `MERGED` with a clean workspace (an empty commit); two PRs in one commit, and
  twelve, whose subject is the counted form; `OPEN` (kept, no commit); `CLOSED` (deleted, no
  commit); `mergedAt` a day before the entry (deleted, no commit); an entry 15 days old
  (deleted, no commit, the stub not called); an entry recorded from `wt` left alone by a
  Stop in `proj`; an entry whose checkout is gone, left alone while its `ceh-ws/` branch is
  unmerged; `MERGE_AUTOSTASH` present (kept, no commit); and a stub exiting 1, which keeps
  the entry and prints one `systemMessage`, then none on a second run with the same
  `session_id`. A missing `gh` takes the same branch as a failed call and gets no fixture,
  because a PATH with `git` and without `gh` cannot be built on the CI runner.

## Phases

### Phase 1: A merge command records its pull request as pending

- **Builds:** The `merge` event, the `hooks.json` entry, and the `merge` fixtures.
- **Check:** With the fixtures written and the event not yet in the script,
  `python tools/validate-plugins/validate.py` exits 1 naming each recording fixture, and the
  fixtures that expect no entry pass. With the event it exits 0, and
  `grep -c "sync-agents-workspace.py.. merge" plugins/standalone/ceh-git-workflow/hooks/hooks.json`
  prints 1.
- **Status:** done, tools/validate-plugins/validate.py first failed on all six positive recording fixtures
  (expected one checkpoint entry, got 0). After adding the merge event and Bash hook,
  it printed "OK: all plugin checks passed" on Windows. Negative fixtures passed too.

### Phase 2: Stop commits the checkpoint for each merged pull request

- **Builds:** The pending check in the `commit` event, the stub `gh`, the commit, the failure message,
  the `commit` fixtures, the README section (the auto-merge note, the denied-merge note and
  the pending folder), the version bump, the changelog entry and the
  `docs/PLUGIN_VERSIONS.md` row.
- **Check:** With the fixtures written first, `python tools/validate-plugins/validate.py` exits 1 naming
  each `commit` fixture that expects a commit or a deletion, and exits 0 once the event
  handles them. Manual, because it needs a real merge on GitHub and a live session: after
  the plugin is reinstalled, land the next PR of this repo through
  `ceh-git-workflow:pull-request` with its branch deleted, and
  `git -C .agents_workspace log -1 --format=%B` shows the checkpoint subject, the PR's URL
  and its merge commit. With `gh` renamed for one turn and an entry pending, the failure
  message appears in the session once.
- **Status:** todo. tools/validate-plugins/validate.py printed "OK: all plugin checks passed" after the
  last code and formatting edits. The completion fixtures failed on nine expected
  behaviors first. Additional regressions pass for branch-reference cleanup,
  repeat Stop idempotence and a refused git commit. The live check after reinstalling the
  plugin, merging a real PR with its branch deleted and observing the failure message in
  Claude Code has not run. This phase stays todo until that required check is completed.

## Open

- Should the checkpoint also push the workspace repo?: No. The daily sync pushes, and the checkpoint stays local.
- The checkpoint in a main checkout stages every change in the workspace, including files
  another session is still writing. Is that acceptable?: Yes. The daily sync does the same today, and a half-written file is completed by a later
  commit.
- Should a PR whose workspace has no changes still get a checkpoint commit? The discussion
  said to skip a checkpoint when nothing changed.: Yes, one empty commit per PR, as the review recommends, because a linked worktree is
  usually clean at that moment and would otherwise never get one.
- Does `gh pr view <branch>` still find a merged PR once its branch is deleted, and does
  `shutil.which` return a `gh.cmd` stub that runs without a shell on Windows?: Yes to both, untested. Phase 2's manual check lands a PR with its branch deleted, and its
  fixtures run on Windows before the PR opens. If the first fails, the `merge` event resolves
  the branch to a number with one `gh pr view` call when the PR already exists.
- Is a Stop hook's `systemMessage` shown to the user, and which `cwd` does PreToolUse carry
  for a Bash call inside a subagent's worktree?: It is shown, from the hooks reference, which does not confirm it in so many words, and
  Phase 2's manual check covers it. A subagent's merge recorded under another `cwd` is
  picked up by that checkout's Stop or expires.

## Record

- 2026-11-13 Planned: status ready
- 2026-11-13 Reviewed: Revise first, 4 blocking (the PR number fallback reads output gh never prints off a
  terminal; a pending line for a closed or unknown PR is never cleared; the pending file
  shared by all worktrees lets another checkout take the checkpoint; the stub and no-gh
  fixtures cannot be built on Windows and CI as written)
- 2026-11-13 Reviewed: Revise first, 1 blocking (the `gh pr merge` regex matches a mention in a heredoc or body,
  and Stop never rejects a PR merged before its entry was recorded)
- 2026-11-13 PR: #270 https://github.com/cheneeheng/ceh-claude-code-library/pull/270
- 2026-11-13 Built Phase 1: tools/validate-plugins/validate.py: OK: all plugin checks passed. The six recording
  fixtures failed first, then passed after the merge event was implemented.
- 2026-11-13 Design changed: Was "An entry kept for later is renamed back". Retained claims now use an atomic
  hard link that refuses to replace a newer pending entry, then remove the claim, so a
  concurrent merge event is not lost. Attached --repo= and -R forms are ignored too.
- 2026-11-13 Checked: 24 Built, 1 Cannot verify: Phase 2's live installed-hook check with a real GitHub merge,
  deleted branch and displayed failure notice has not run. Local automated fixtures,
  the repository validator, plugin validation and configured formatting checks pass.
- 2026-11-13 Design changed: The double-check reproduced quote-unaware command matching, branch filename collisions
  and duplicate checkpoints on repeated merge events. Was raw command regex splitting;
  now command segments respect quotes and escapes. Was punctuation replaced by underscores;
  now branch filenames use a SHA-256 digest, including on case-insensitive filesystems.
  Confirmed PRs are checked against workspace Git history before committing again.
- 2026-11-13 Checked: Follow-up review reproduced and fixed command quoting errors, branch filename collisions
  and repeated checkpoints. Five focused checkpoint regressions and the hook-batch runner
  regression pass. tools/validate-plugins/validate.py prints OK: all plugin checks passed,
  including the new integration fixtures. The live installed-hook check remains unverified.
- 2026-11-13 Checked: 22 Built, 1 Deviation, 2 Extra, 1 Cannot verify. Deviation: the `merge` event does not
  return at once without a `gh pr merge` mention, because `main()` runs `checkouts()`,
  `workspace_repo()` and `current_branch()` (three git processes) before `record_merge`
  tests the command, about 135 ms per Bash call against 24 ms for a bare Python start.
  Extra: `tools/validate-plugins/tests/test_workspace_checkpoints.py` and
  `product/fixes/workspace-checkpoint-recording-and-replay.yaml`. Cannot verify: Phase 2's
  live check with a real merge, a deleted branch and the displayed failure message.
  The validator and the five unit tests pass. A probe also showed that
  `if true; then gh pr merge 12 --merge; fi` and `GH_PAGER= gh pr merge 12` record nothing,
  which matches the design's "segment beginning with the three tokens" as written.
- 2026-11-13 Design changed: The user chose both fixes after the check. Was "Only a segment beginning with the three
  tokens `gh`, `pr`, `merge` is considered"; leading shell words and `NAME=value`
  assignments are now dropped first, with two recording fixtures. The deviation is fixed in
  the code: `main()` tests the command for `gh pr merge` before any git process, proven by
  a unit test that fails when git is called for `ls`.
- 2026-11-13 PR: #284 https://github.com/cheneeheng/ceh-claude-code-library/pull/284

<!-- prettier-ignore-end -->
