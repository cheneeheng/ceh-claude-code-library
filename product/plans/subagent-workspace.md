---
schema: plan/v2
generated_from: subagent-workspace.yaml
generated_note: "Do not edit. artifact.py renders this file from subagent-workspace.yaml: edit the YAML, then run artifact.py render."
title: A subagent in its own worktree gets the workspace and merges it back
status: draft
created: 2026-11-14
---

<!-- prettier-ignore-start -->

## Goal

A subagent started with `isolation: "worktree"` runs in `<project>/.claude/worktrees/agent-<id>/`,
which holds the source repo only. It finds no `.agents_workspace`, so it cannot read a plan or
write a record, which a test on 2026-11-14 confirmed (`ls -a` in the worktree). A `gh pr merge`
it runs is recorded as pending with its worktree as owner, and the main session's Stop skips that
entry while the worktree exists, so the checkpoint waits until the worktree is deleted or expires
after 14 days with no warning. After this plan, `ceh-git-workflow` gives such a subagent its own
workspace worktree when it starts, and when it stops, commits that workspace, makes its pending
PR checkpoints and merges its branch back into the main workspace, as a session in a linked
worktree already does.

## Scope

**In:**

- A live check, before any code, that settles the three unknowns listed under Open about
  `SubagentStop` and `SubagentStart`.
- `SubagentStart` and `SubagentStop` entries in
  `plugins/standalone/ceh-git-workflow/hooks/hooks.json` that run the existing
  `sync-agents-workspace.py` events.
- `sync-agents-workspace.py` acting on the two subagent events in a linked worktree only, and
  naming the event it was called for in its output.
- Fixtures in `tools/validate-plugins/checks/hooks.py` for both events.
- The `ceh-git-workflow` README, `docs/CATALOG.md` if a row names the hooks, the changelog, a
  PATCH bump of `ceh-git-workflow` and its `docs/PLUGIN_VERSIONS.md` row.

**Out:**

- A `WorktreeCreate` hook: The hooks docs say it replaces Claude Code's own worktree creation: the script would create
  every worktree itself, match Claude Code's branch naming and base, and a failure would stop
  any subagent from getting a worktree. `SubagentStart` adds to the default instead, and its
  payload carries the worktree as `cwd` (seen on 2026-11-14).
- Subagents that run in the main checkout: They already see the main workspace. The subagent events do nothing there (Design), so an
  `Explore` or `bulk-reader` dispatch costs one process and no git call.
- Pushing the workspace repo: Unchanged from `product/plans/workspace-checkpoint-on-pr-merge.yaml`: the daily sync pushes.
- A real `gh pr merge` inside a subagent: The fixtures cover the recorded entry and the Stop that handles it with a `gh` stub, as the
  checkpoint plan's fixtures do. A real merge spends a PR on a disposable repo for no extra
  proof.

## Design

- **What 2026-11-14 already showed:** A temporary hook in `.claude/settings.local.json` logged the stdin JSON while one Haiku
  `general-purpose` subagent with `isolation: "worktree"` ran `pwd && ls -a`. `SubagentStart`
  carried `cwd` = `<project>/.claude/worktrees/agent-<id>`, `agent_id` and `agent_type`.
  `PreToolUse` inside the subagent carried the same `cwd`, `agent_id` and `agent_type`. The
  worktree had no `.agents_workspace`. Claude Code removed the worktree and its branch after the
  run, since the subagent changed nothing. A hook added to the settings file took effect without
  a restart. Results are in
  `.agents_workspace/plugin-audit/20261114-165001-68ee59cd-936d-4a20-bd34-12e16e4f5f05-open-items.md`.
- **Hook wiring:** `SubagentStart` runs `sync-agents-workspace.py start`, which in a linked worktree commits the
  main workspace and calls `create()`, the path `EnterWorktree` already takes. `SubagentStop`
  runs `commit`, then `end`, in that order in one entry: `commit` makes the pending PR
  checkpoints whose owner is this worktree and commits the workspace synchronously, and `end`
  starts the detached `end-worker`, which merges `ceh-ws/<X>/agent-<id>` into the main
  workspace's branch. No matcher, so every agent type is covered. Timeouts as the existing
  entries: 30 seconds each.
- **Main checkout:** When `hook_event_name` is `SubagentStart` or `SubagentStop` and `cwd` is not a linked
  worktree (`main_checkout` is `None` after `checkouts()`), `main()` returns before any further
  git call. A subagent in the main checkout shares the main workspace, and the main session's
  own Stop and SessionStart already do the catch-up and checkpoints there.
- **Event name in output:** The catch-up note that `start` prints names `"hookEventName": "SessionStart"`. It takes the
  payload's `hook_event_name` instead, defaulting to `SessionStart`, so the note is valid for
  `PostToolUse` too. With the main-checkout return above, `SubagentStart` never reaches that
  note, and the change only keeps the output honest for the existing events.
- **Item 6 follows from this:** A merge inside the subagent is recorded with the subagent's worktree as owner. Its own
  `SubagentStop` runs `commit` with that worktree as `cwd`, so `same(owner, top)` holds and the
  checkpoint is made there, then merged back by `end-worker`. The main session's Stop no longer
  depends on the worktree being deleted. A subagent stopped by a crash leaves the entry to the
  existing path: the main Stop takes it once the worktree is gone and its workspace branch is
  merged, or it expires after 14 days.
- **If Phase 1 shows the worktree is removed before SubagentStop:** Then the workspace worktree inside it is gone too, with any uncommitted edit, and Phase 2 as
  written loses work. The builder stops after Phase 1, records the result, and Phase 2 is
  replanned with a `Design changed` entry before any code. The candidate then is a
  `PostToolUse` entry on `Edit|Write|MultiEdit` that runs `commit` inside a subagent's linked
  worktree, read from `agent_id`.

## Phases

### Phase 1: Settle the three unknowns with one live run

- **Builds:** Temporary logging hooks in `.claude/settings.local.json` on `SubagentStart`, `SubagentStop`
  and `PreToolUse` (any tool), each appending its stdin JSON, a timestamp and
  `os.path.isdir(cwd)` to a log file in the session's scratchpad. The `SubagentStart` hook also
  sleeps three seconds and then writes `<cwd>/.probe-start`. One Haiku `general-purpose`
  subagent with `isolation: "worktree"` runs `ls -a`, then writes one line to
  `.agents_workspace/probe.txt` in its worktree. The repo's `.gitignore` ignores
  `.agents_workspace/`, so the source tree looks unchanged, as it will with a real workspace
  worktree there. The `SubagentStop` log entry records whether `probe.txt` still existed. The
  hooks are removed afterwards and `git worktree list` shows no leftover. The
  answers go into this plan's Open and Record.
- **Check:** The log holds one `SubagentStart` and one `SubagentStop` entry for the subagent, and the
  Record entry names: the `cwd` in `SubagentStop`; whether the worktree directory still existed
  when `SubagentStop` ran; whether the subagent's first `PreToolUse` came after the
  `SubagentStart` entry's timestamp plus three seconds and its `ls -a` listed `.probe-start`.
  A manual check, because it is a real model call. It needs the user's go before it runs.
- **Status:** todo

### Phase 2: The subagent events in the sync hook

- **Builds:** The two entries in `ceh-git-workflow/hooks/hooks.json` (Design, "Hook wiring"). In
  `sync-agents-workspace.py`: the main-checkout return for the subagent events, the event name in
  the catch-up note, and the module docstring naming `SubagentStart` and `SubagentStop`.
  Fixtures in `checks/hooks.py`, on the sync project already built there: `start` with a
  `SubagentStart` payload in a linked worktree creates its workspace on `ceh-ws/ws/<name>`;
  the same payload in the main checkout makes no commit and prints nothing; `commit` with a
  `SubagentStop` payload in a linked worktree turns a pending entry owned by that worktree into
  a checkpoint commit through the `gh` stub; `SubagentStop` in the main checkout leaves a
  pending entry in place. README, changelog, PATCH bump of `ceh-git-workflow`,
  `docs/PLUGIN_VERSIONS.md`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the four new fixtures in its hooks
  output and the existing sync fixtures passing, and each new fixture failed once with its
  assertion inverted.
- **Status:** todo

### Phase 3: One live run of the built hook

- **Builds:** With the Phase 2 plugin loaded from the checkout, one Haiku subagent with
  `isolation: "worktree"` reads a plan planted uncommitted in the main workspace and appends one
  line to `.agents_workspace/notes/subagent.txt`. After it stops, the main workspace holds that
  line on its branch, `git -C .agents_workspace branch --list "ceh-ws/*"` shows the subagent's
  branch merged, and no worktree is left.
- **Check:** `git -C .agents_workspace log -1 -p -- notes/subagent.txt` shows the line in the main
  workspace, and `git -C .agents_workspace branch --no-merged` prints nothing. A manual check,
  because it is a real model call. It needs the user's go before it runs.
- **Status:** todo

## Open

- Has a session lost a record, or waited on a checkpoint, because a subagent ran in its own worktree?: No. The user parked this plan on 2026-11-14 until one does, so nothing here is built. Until
  then the caller passes a worktree subagent what it must read and writes the records itself.
  Before building, the two engineering findings of the 2026-11-14 review are fixed in Design:
  `.agents_workspace/product/plan-reviews/20261114-185908-6f0d566f-9e02-4dd6-9b24-a22e9220cb81-subagent-workspace.md`.
- What `cwd` does `SubagentStop` carry for a subagent in its own worktree?: The worktree root, as `SubagentStart` did on 2026-11-14. Phase 1 confirms it.
- Does Claude Code run `SubagentStop` before it removes an unchanged worktree?: Yes, since the hook reports the subagent's end and the removal is cleanup after it. Phase 1
  confirms it. If not, Design "If Phase 1 shows the worktree is removed before SubagentStop"
  applies.
- Does `SubagentStart` finish before the subagent's first tool call?: Yes, as `SessionStart` finishes before the first turn. Phase 1 confirms it with the
  three-second sleep and the probe file.
- Does the detached `end-worker` survive the end of a subagent?: Yes. It is started in its own process group for `SessionEnd`, whose budget is shorter, and a
  subagent's end does not end the Claude Code process. Phase 3 shows it, since the merge-back
  is the worker's job.

## Record

- 2026-11-14 Planned: status ready. The user reviews it, so no review-build-plan run.
- 2026-11-14 Reviewed: Rethink, 2 blocking (no observed need, so park the plan; parallel subagents' detached
  merges into the main workspace can lose the index lock with no retry in the session)

<!-- prettier-ignore-end -->
