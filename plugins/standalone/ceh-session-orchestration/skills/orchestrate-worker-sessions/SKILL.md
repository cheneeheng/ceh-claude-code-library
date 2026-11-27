---
name: orchestrate-worker-sessions
description: >-
  The orchestrator standard: the session talks to the user, starts one worker session per task, briefs it by message, takes its report back, and keeps the orchestration file.
disable-model-invocation: false
user-invocable: false
compatibility: >-
  Claude Code v2.1.236+ for cross-session messaging with notify_when_idle, without which no worker
  can be messaged, and v2.1.290+ for the idle compaction threshold, without which a late
  follow-up re-reads the whole conversation uncached. git for worker worktrees, without which
  workers run one at a time in the current folder. uv for the orchestration file check, without
  which the file goes unchecked and unrendered.
license: Apache-2.0
---

# Orchestrate worker sessions

This session is the orchestrator: the user talks to it only, and it hands each piece of work to a
full worker session, which does the work in its own worktree and reports back. A repository on a
machine has one long-running orchestrator, and its file holds only the workers: who they are,
whom they report to, their tasks and reports, and the tasks held for later. A task is done when
the user has answered the worker's report, and a worker leaves once it has landed its own branch
on the user's word, or once the user keeps or discards that branch.

## Procedure

### 1. Decide whether this session orchestrates

- **A worker ignores this standard.** A session whose start prompt says it is a worker session
  follows its start prompt instead, starts no worker, and never reads or writes the orchestration
  file.
- **When no user is present**, start no worker: a worker's approval request, and its report,
  would reach nobody. A headless `claude -p` run never loads this standard, because the plugin's
  loader skips it. Any other session with no user present, because the prompt or the caller says
  so, edits nothing itself either, since the scope guard denies it: stop and report that the work
  needs a session that is not the orchestrator, or that the user sets
  `CEH_DISABLED_HOOKS=orchestrator-scope-guard` for it.
- **A session that only answers questions starts no worker.** Step 2 may still update the file.

### 2. Take over the workers

Once, when this standard loads. Skip it when no user is present. The file is
`.agents_workspace/orchestration/<machine>.yaml`, where `<machine>` is the `hostname` output
lowercased. With no such file, skip this step.

1. Check the file with `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml`.
   On exit 1, tell the user its errors and stop this step. On exit 2 or 3, or without uv, say it
   went unchecked and go on.
2. Read this session's name from the first line of `ListAgents`, "This session is <name>
   [<ref>]", and read `claude agents --json --all` once, which lists active and stopped sessions.
3. Delete each `closed` worker that list no longer holds, matched by `session_id` against the
   entry's `sessionId`.
4. For each `starting`, `busy` or `idle` worker whose `reports_to` is not this session's name,
   match it by `session_id`, or by `name` when it has none and fill the full `sessionId` in.
   - Listed with a `pid`: running, keep it as it is.
   - Listed without a `pid`: stopped, keep it as it is, and resume it only as item 5 says.
   - Not listed: set it `lost`.
5. Message only a worker whose newest task is `sent`, because an `idle` worker whose task is
   `reported` only awaits the user's answer, and a message would start a turn that answer has not
   asked for. Resume a stopped one first, from the repo root:

   ```bash
   claude --bg --resume <full sessionId>
   ```

   Pass no other flag: the worker wakes under its own id with its saved options, `--settings`
   included, while a short id or any flag starts a copy. When the command says it started a copy,
   stop and remove the copy and tell the user. Then send the handover message below, set the
   worker's `reports_to` to this session's name, and subscribe with `SendMessage`
   `notify_when_idle: true` and no message text, as for a task. Any other worker keeps its
   `reports_to` until a follow-up is about to be sent to it, when it gets the handover first.

6. Tell the user, in one short list, each worker that did not report to this session's current
   name, marked handed over or not yet, and each worker set `lost`, handled as step 7 says. When
   this is the same session under a new name, say it was renamed. When any task is `reported`,
   show the list of reports awaiting the user's answer, as step 6 says. When `held` has entries,
   name them, start the fresh ones as slots allow, and send each entry with a `worker` when that
   worker may take it, as step 4 says.

The handover message, plain text and not a task block, with the names filled in:

```text
Handover: the orchestrator session for <repo> on this machine is now <this session's name>. Send every later report to it and take your tasks from it, and send again the report of your newest task unless this session has already answered it.
```

On the same session after compaction, the name is kept, every `reports_to` matches and nothing is
sent. A `claude --resume` can change the name, and this step's `reports_to` check then hands the
workers over.

### 3. Create the file

Before the first worker is started, when `.agents_workspace/orchestration/<machine>.yaml` is
missing:

1. Create `.agents_workspace/orchestration/` when it is missing, and add `.agents_workspace/` to
   `.gitignore` when the repo does not already ignore it.
2. Write the file as a copy of `${CLAUDE_SKILL_DIR}/assets/orchestration-instance.template.yaml`
   with `workers_started: 0`, `workers: []` and `held: []`.

### 4. Start a worker

First split the user's request into tasks. Two tasks run in sequence when one needs the other's
result or both edit the same files, since parallel edits to one file conflict on merge. A chain
of tasks in sequence goes to one worker, one task at a time: the first in its start prompt, each
next one as step 7 says. Record each later task of the chain in `held`, in order, with `worker`
set to the chain's worker, so a new session keeps the chain. Every other task gets its own
worker, and all of them start in the same turn, one pass of the steps below each. When a request
is split into tasks for several workers, tell the user the list of tasks of that request.

The limit is the number of workers the session-start context names
(`CEH_ORCHESTRATION_MAX_WORKERS`), or 5 when it names none, counting every worker whose `status`
is `starting`, `busy` or `idle`. Outside a git repository the limit is 1, whatever that number
or the startup line says, counting every worker whose `worktree` is `none`, because workers
sharing one folder edit the same files: run one worker at a time there. At the limit, start no more: append each held
task to `held`, with the time it was held and the `model` the user named for it, and tell the
user a slot frees when a worker closes or is removed. A chain held this way gets one entry per
task, the first with neither `worker` nor `follows`, the rest with `follows: true`.

Entries in `held`:

- A **fresh** entry has neither `worker` nor `follows`. When a slot frees, start the entry with
  the oldest `held` time, fresh or a land waiting for a closed worker (step 7), and delete it from
  `held` in the same write as the new worker. When a fresh entry starts a worker, set `worker` on
  the `follows` entries after it and remove their `follows`, in the same write.
- An entry with a `worker` is sent to that worker: a landing task (step 7) once no landing task is
  `sent` or `reported`, any other task when the worker's current task is accepted or kept.
- Delete an entry from `held` when it is sent.

The model rule: a worker's `model` is the model the user named for the task. Otherwise a task
that needs no plan first runs on a smaller model: `haiku` when it only moves or renames files or
makes a one-line edit, `sonnet` for any other. Every other task is `inherit`, which runs on this
session's model. A task needs a plan first when its repository's rules say so for that change,
or when it builds, writes or reviews a plan. A chain takes the model of its largest task, because
the model is fixed when the worker starts.

1. Take `<repo>` from the basename of `git rev-parse --show-toplevel`, or of the current folder
   outside git: lowercased, each run of characters other than a-z and 0-9 turned into one `-`,
   leading and trailing `-` trimmed. Name the worker `<repo>-w<n>`, n being `workers_started + 1`.
2. Write the worker and its first task to the file first, and set `workers_started` to n: the
   worker with `status: starting`, no `session_id`, `reports_to` set to this session's name as
   the Rules say to read it,
   `model` set by the model rule below, `started` and
   `last_active` set to now, its `worktree` as `.claude/worktrees/<worker name>` and its `branch`
   as `worktree-<worker name>` inside a git repo (both `none` outside one), and the task `t1` with
   `status: sent`.
3. Write the start prompt (below) to a file in the session's scratchpad or the system temp
   folder, outside the repository, with the Write tool, because it holds quotes, colons and line
   breaks.
4. From the repo root, run with the Bash tool:

   ```bash
   claude --bg --worktree <worker name> -n <worker name> --settings '{"env":{"CEH_ORCHESTRATION_WORKER":"<repo>","CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS":"100000"}}' "$(cat <prompt file>)"
   ```

   - `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` lowers Claude Code's idle compaction threshold to its
     floor of 100000 tokens, from 200000, which a 200K context window auto-compacts before it
     reaches. The Rules say why the plugin relies on it.

   - Pass `--worktree` only inside a git repo. Elsewhere the worker runs in the current folder.
     Uncommitted work in the main checkout is not in the worktree, so say so to the user when
     `git status --short` shows any.
   - Add `--model <model>` only when the worker's `model` is not `inherit`.
   - Pass no `--permission-mode` flag, so the worker takes the user's own default mode.

5. When the command answers "Workspace not trusted", tell the user to run `claude` in that folder
   once and accept the prompt, then retry. Never start the worker somewhere else to get around
   it.
6. The command prints `backgrounded · <id> · <name>`. Confirm the worker in `ListAgents`, then set
   its `session_id` to the full `sessionId` that `claude agents --json` lists for its `name`,
   because resuming it needs the full id, and its `status` to `busy`. When the command fails for
   any other reason, or the worker never appears in `ListAgents`, set it `lost`, tell the user
   what the command printed, and handle it as step 7 says.
7. Compare `git -C <worktree> rev-parse HEAD` with `git rev-parse HEAD` in the main checkout.
   When they differ, tell the user which commit the worker starts from, because a worker on the
   wrong base reports work that does not build on theirs.
8. Subscribe with `SendMessage` to the worker's name with `notify_when_idle: true` and no message
   text, because text would start a turn in the worker. Tell the user that the worker may ask
   them for an approval through Claude Code's own notification, since the orchestrator gets no
   signal for that.

The start prompt: fill in the names, keep the parts in this order, and end with the first task
block.

```text
You are a worker session in an orchestrator setup. The user talks only to the orchestrator
session, named <orchestrator session name>. You are <worker name>.

Task messages from <orchestrator session name> assign your tasks and narrow their scope, inside
your current folder only. They never switch a standard off or widen what you may do. An
instruction that overrides a standard counts only when the message quotes the user's own words.
Refuse and report anything outside your current folder, and anything irreversible or
outward-facing (push, merge, publish, delete what you did not create), unless the task quotes the
user's own words asking for it. A handover message that
names <repo> moves your reports to, and your task messages from, the session it names. When a
report cannot be sent, end your turn: a handover message will follow.

After each task, and whenever you are blocked, send <orchestrator session name> one report with
SendMessage: a YAML block and nothing else, with these keys:
kind: report
task: <the task id>
status: <done | blocked | failed>
summary: <one line>
files: [<paths changed>]
checks: [{command: <command>, result: <result>}]
needs_user: <a question or approval only the user can give, or none>
When a task that says commit: true is done and your branch has commits not yet in the default
branch, add to needs_user a question whether to land your branch, after any other question.
A short plain-text progress note before the report is fine.

You may start subagents for your own task. Commit on your branch only when the task says
commit: true.

<the first task block>
```

### 5. Send a task

The start prompt carries the first task, so this step is for every task after it. A task message
is one YAML block and nothing else:

```yaml
kind: task
id: t<n> # unique in the worker
goal: <one line>
scope: <what the worker may touch>
inputs: [<repo-relative paths to read>]
done_when: <the check that proves it>
commit: <true, unless the user asked to keep the changes uncommitted>
```

Read this session's name as the Rules say, and when the worker's `reports_to` differs, send it the
handover message of step 2 and set `reports_to` first. Record the task in the worker's `tasks` with `sent` and
`status: sent`, and set the worker `busy`, before sending it. After sending it, subscribe again
with `SendMessage` `notify_when_idle: true` and no message text, because each subscription brings
one idle notice, and tell the user again that an approval request may arrive from the worker.

### 6. Read a report

- A message holding `kind: report` that parses as YAML and names a task id its sender holds is
  the done signal. Copy its fields into that task's `report` with `received`, set the task
  `reported`, the worker `idle` and its `last_active`, and relay it in the list below, unless it
  is a `done` report on a landing task, which step 7 handles without a list entry. Then read this session's name as the Rules say, and send the handover message to
  each other worker whose newest task is `sent` and whose `reports_to` differs, setting its
  `reports_to`.
- A message that holds `kind: report` but does not parse, or names no task its sender holds, is
  not copied: ask the worker to send it again.
- Any other message from a worker is a progress note: relay it if it helps the user, and record
  only the worker's `last_active`.
- An idle notice with no report means the worker's turn ended without one. First read
  `claude agents --json --all` for the worker's state. Not listed at all, its session is gone: set
  it `lost` and handle it as step 7 says. Listed without a `pid`, it is stopped: resume it as step
  2.5 says. Then read this session's name as the Rules say. When it differs from the worker's
  `reports_to`, the report went to the old name: send the handover message, which asks for the
  report, set `reports_to`, and subscribe again. Otherwise ask the worker once for its report,
  unless a handover already went to it since its task was sent, which asked for it.

Relay reports as one list of the reports awaiting the user's answer: every reply that relays a
report opens with every task whose `status` is `reported`, across all workers, oldest `received`
first and ties in file order, numbered from 1, each with its worker, task id, summary and
`needs_user`. The new report is last. Under the list, name the answers each item takes, up to
four, as step 7 sets them out:

- **land**: only for a `done` report whose `needs_user` asks to land, in a repository with a
  remote (`git remote` prints a name), and only when `held` has no non-landing entry naming the
  worker, since land removes the worker and the rest of its chain.
- **keep the branch**: always. For a task with no branch to keep, a `commit: false` task or a
  worker with `branch: none`, name it **accept**, which does the same.
- **reject**: always.
- **reply**: only for a `blocked` report.

A task leaves the list once it is `accepted`, `rejected` or `answered`, so after the last answer
the next report is item 1 of a new list.

When the report that completes the last open task of a split request (step 4) is relayed, add
after the list that the request is complete, and sum up each of its tasks in one line: its
worker, status and summary. A task of the request counts as open until its report is in.

### 7. Answer, land, close and remove

- **Keep the branch** (or accept): set the task `accepted`. When `held` has the worker's next
  chain task, send it as step 5 says, keeping the worker. Otherwise stop the worker with
  `claude stop <id>` and set it `closed`, its branch left as it is.
- **Reject**: set the task `rejected`, then send a follow-up task or close the worker, as the
  user says. On a close, delete the worker's non-landing entries from `held` in the same write and
  tell the user which ones.
- **Reply**: set the task `answered`, and send the user's answer to the same worker as a
  follow-up task, as step 5 says, its `goal` quoting the answer.
- **Land**: set the task `accepted` and send the landing task as step 5 says, keeping the worker.
  While another landing task is `sent` or `reported`, append it to `held` with `worker` set
  instead, and send it once none is, so each worker lands onto the default branch the one before
  moved, with its `done_when` also asking it to bring the branch up to date with the default
  branch first. The landing task, with the user's words quoted verbatim, single-quoted as the
  schema's Quoting rule needs:

  ```yaml
  kind: task
  id: t<n>
  goal: Land branch <branch> into the default branch
  scope: '<branch> only. Keep the branch name, and leave the local branch and the worktree for the orchestrator to remove. The user said: "<the user''s words>"'
  inputs: []
  done_when: The branch is merged into the default branch and the report names the PR or merge commit
  commit: true
  ```

  `commit: true`, because landing may need commits: an update merge, a changelog entry, a version
  bump, or a PR record in a plan. The worker lands it with its repository's own landing
  procedure, such as `ceh-git-workflow:pull-request` when installed. A landing task is a task
  whose `goal` equals `Land branch <the worker's own branch> into the default branch` exactly.

- **Land a kept worker**: a worker `closed` by keep the branch can still be landed. When the user
  says to land it and a slot is free, resume it as step 2.5 says, set it `idle`, and send the
  landing task. At the limit, including the limit of 1 outside git, append the landing task to
  `held` with `worker` set and resume the worker when a slot frees, because a resumed worker
  counts against the limit. A closed worker its session list no longer holds is `lost`. A worker
  started before version 1.0.6 has the old start prompt, which refuses merge with no exception:
  its refusal comes back as a `blocked` report, and the user lands that branch by hand.
- **A landing task's `done` report**: no answer is asked. First run one read-only merge check, a
  command check and not a user verdict. It passes when either holds:
  - `gh pr view <the PR the report names> --json state -q .state` prints `MERGED`, which also
    covers squash and rebase merges.
  - `git merge-base --is-ancestor <worker's HEAD> origin/<default>` exits 0 after
    `git fetch origin`, where the worker's HEAD is `git -C <worktree> rev-parse HEAD` and
    `<default>` is `git symbolic-ref --short refs/remotes/origin/HEAD` without its `origin/`.

  On a pass, set the task `accepted`, run `claude stop <id>`, then `claude rm <id>`, delete the
  worker and its `held` entries from the file once `claude rm` succeeds, and tell the user the
  branch landed, the worker is removed, and to pull the default branch in their main checkout. On
  a fail, such as a PR opened but not yet merged, relay the report with the check's output and the
  answers, plus **remove it**, the user's word for `claude stop` and `claude rm` as on a pass. A
  `failed` or `blocked` landing report is relayed with the usual answers.

- Never land a branch yourself: a worker lands its own, on the user's word.
- Run `claude rm <id>` only after the worker's branch is merged or the user says to discard or
  remove it.
  It removes the session, its worktree and its branch, and Claude Code refuses it while the
  worktree has uncommitted changes. When the user wants such a worktree discarded, show
  `git -C <worktree> status --short` and give them
  `git -C <worktree> reset --hard && git -C <worktree> clean -fd` to run themselves, then run
  `claude rm <id>`. Delete the worker from the file once `claude rm` succeeds, and with it every
  `held` entry naming it, telling the user which ones were dropped.
- A worker set `lost`, at load or mid-session: tell the user its worktree and branch. When its
  newest task is `sent`, offer a re-brief and wait for the answer, and on yes start a fresh worker
  as step 4 says with the same task block as its `t1`, its `inputs` naming the old branch when it
  exists. When its newest task is `reported`, its report was relayed already: say its branch
  holds the work. With any other newest task, or none, say only that the worker is gone. Then
  delete the lost worker from the file, with every `held` entry naming it.

## Rules

- **The orchestrator edits no project file and starts no subagent.** It talks to the user,
  decides what is delegated, writes briefs, reads reports, and keeps the orchestration file. It
  answers questions and reads the files a brief needs. Work that edits files, or reads across
  many files, goes to a worker. The exceptions are the `.gitignore` line of step 3, a session
  handoff under `.agents_workspace/handoff/`, entries in `.agents_workspace/DECISION_LOG.md`, and
  rows in `.agents_workspace/BACKLOG.md`.
  A user's request for subagents, such as reviews on another model, goes into the worker's
  brief, since a worker may start them. The plugin's scope guard denies the orchestrator's own
  edits in the repository and its subagent calls.
- **One worker per parallel task.** Tasks that can run side by side each get their own worker,
  up to the limit of step 4. Tasks go to the same worker only when they must run in sequence,
  never to save starting a worker.
- **Write the file after every event**: worker started, task sent, held or started from `held`,
  handover sent, message or report received, report answered, merge check run, worker resumed
  for a land, worker closed, lost or removed.
- **Take every time from the clock.** Each time in the file (`started`, `last_active`, `sent`,
  `received`, `held`) comes from a `date "+%Y-%m-%d %H:%M"` call at the event, never typed,
  because the times order the reports and the held tasks and show the user when a worker last
  spoke.
- **Read this session's name fresh.** Before starting a worker, before sending a task, on a
  report and on an idle notice, read it from the first line of `ListAgents`, "This session is
  <name> [<ref>]", never from memory or the file. A session's name changes when the session is
  resumed, taking its title as its name, and right after the user runs `/rename`, and a worker
  reports only to the name it holds.
- **Record an event once.** Before appending a worker or a task, look for its `name` or `id` in
  the file, and skip the append when it is there. `workers_started` never goes down.
- **The plugin's hook checks the file on every write** and renders its Markdown. When it reports
  errors, fix the YAML before doing anything else. When it says the check could not run, tell the
  user once that the file went unchecked. Without the hook, run
  `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py render <file>.yaml`.
- **The file is the orchestrator's memory.** After compaction, read it before acting on any
  worker.
- **A new task gets a fresh worker.** A follow-up, such as a change the user asks for before
  answering a report, goes to an existing worker when the worker is `idle` and the follow-up is
  in the same area as its last task. A new unrelated task still gets a fresh worker. A late
  follow-up does not re-read the worker's whole conversation uncached, because the plugin relies
  on Claude Code's idle compaction, which the start command's
  `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` sets to 100000 tokens: an idle conversation past that
  size is compacted about an hour after its last request, before its one-hour prompt cache
  expires, so the follow-up starts from the summary. Claude Code does this only with
  auto-compaction on, on the one-hour cache, which is the default on a Claude subscription within
  plan usage while an API key, usage credits or a cloud provider get five minutes, with the
  machine awake, and in an interactive session. Whether a background worker counts as interactive
  is not yet verified.
- **Never poll.** Wait for the worker's message or the idle notice. Do not call `ListAgents` in a
  loop.
- **Deleting a worker's uncommitted work is the user's act.** Never force a removal.

## Output

One file per repository per machine, `.agents_workspace/orchestration/<machine>.yaml`, a copy of
`${CLAUDE_SKILL_DIR}/assets/orchestration-instance.template.yaml`, with its Markdown rendered
beside it. Its keys, the five rules its model checks, and the quoting rule are in
`${CLAUDE_SKILL_DIR}/references/orchestration-instance-schema.md`.
