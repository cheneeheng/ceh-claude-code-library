# ceh-session-orchestration

Talk to one Claude Code session and let it run the others. With this plugin, the session you
start becomes an orchestrator: it starts a full worker session for each piece of work, in its own
git worktree, sends it a task, takes its report back, and, when you say land, has the worker land
its own branch and then removes it. A repository on a machine has one long-running orchestrator,
and every worker, task, report and held task is written to one checked file for that machine, so
the orchestrator still knows its workers after compaction or in a new session.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). No other plugin depends on this one, and
it depends on none. It needs Claude Code v2.1.236+ for cross-session messaging, git for the worker worktrees, `python3` on
`PATH` for the hooks, and `uv` to check and render the orchestration file. The merge check after
a land needs `gh` when the repository merges by squash or rebase. Without uv the agent is told once per session that the file went unchecked.
The role label needs a Claude Code build with mods, and without one no label shows.

Every session you start where the plugin is enabled becomes an orchestrator, so enable it in the
scope where you want that, such as one project. A repository on a machine has only one
orchestrator: while it runs, a second session there does not become one, and its startup line
names the orchestrator. To make the second session the orchestrator, close the first, then run
`/clear` in the second. An ordinary session, with `CEH_DISABLED_HOOKS=load-orchestrator` set for
it as [Settings](#settings) says, never counts as the orchestrator.

## Skills

| Skill                         | Say or type                        | What it does                                                                                                                                          |
| ----------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `orchestrate-worker-sessions` | Nothing: it loads at session start | The orchestrator standard: when to delegate, how to start and brief a worker, the task and report blocks, the orchestration file, landing and closing |

## Agents

This plugin has no agents.

## Hooks

Five hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off,
except the role label, which has no switch of its own: the `orchestrator` label goes with
`load-orchestrator` off, and a worker keeps its label.

| Hook                 | What it does for you                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Orchestrator loader  | At session start and after compaction, makes the session load the orchestrator standard and prints a line saying so, unless another orchestrator already runs in the repository, which the line then names. A worker session skips it. A headless `claude -p` run, which Claude Code marks with `CLAUDE_CODE_SESSION_ATTENDED=0` (observed, not documented), skips it too                                                                                                                                                        |
| Scope guard          | Stops the orchestrator editing project files, other than its own workspace files and the backlog, or starting subagents itself, and says to start a worker. It also counts the orchestrator's Read, Grep, Glob, Bash and PowerShell calls on each message you or a worker send and, past its limit, denies each one unless it is run again, which passes once, so a look that grows into a task goes to a worker. The limit was set from 124 turns of 13 past orchestrator sessions. Workers and other sessions are not affected |
| File check           | Checks each written orchestration file and renders its Markdown beside it                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Generated-file guard | Stops a hand edit to the generated Markdown, which the next render would overwrite                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Role label           | On a Claude Code build with mods, the footer shows `orchestrator` in the orchestrator session and `worker` in a worker session, beside any other mode labels, so you can tell which session to talk to. A session with neither role, such as one the loader refused because another session orchestrates the repository, shows no label. Terminal and desktop only                                                                                                                                                               |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                        | Default              | Effect                                                                                                                                                                                                                                                |
| ------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK`            | unset (check on)     | `off` turns the file check and the generated-file guard off                                                                                                                                                                                           |
| `CEH_DISABLED_HOOKS`            | unset (all hooks on) | Comma-separated hook names to skip: `load-orchestrator`, `orchestrator-scope-guard`, `artifact-render-hook`, `generated-md-guard`. `load-orchestrator` keeps the session from becoming an orchestrator. A headless `claude -p` run skips it by itself |
| `CEH_ORCHESTRATION_MAX_WORKERS` | `5`                  | The most workers one orchestrator runs at once. A value that is not a whole number of at least 1 gives 5, and the startup line says so                                                                                                                |
| `CEH_ORCHESTRATION_WORKER`      | unset                | Set by the orchestrator on each worker it starts, to the name of its own folder. Any value makes the session a worker, which does not load the orchestrator standard. Not for you to set                                                              |

## How it works

### One task, start to finish

1. You give the orchestrator a task. It adds a worker to the machine's orchestration file, then
   starts it with `claude --bg --worktree`, named `<hub>-w<n>` after the orchestrator's folder,
   whose start prompt says it is a worker and what the orchestrator may ask of it.
2. The worker does the task in `.claude/worktrees/<worker>` of its repository and sends back a
   YAML report: status,
   summary, files changed, checks run, and anything only you can answer.
3. The orchestrator relays the report, and when the worker's branch has new commits the report
   asks whether to land it. You answer by item number:
   - **land**: the orchestrator sends the same worker a landing task that quotes your words, and
     the worker lands its branch with the repository's own landing procedure. Once a merge check
     confirms the branch is in the default branch, the orchestrator stops the worker, removes it
     with `claude rm`, deletes it from the file and tells you to pull, with no second question.
     Land needs a remote, and is offered only on the last task of a chain.
   - **keep the branch** (**accept** when there is no branch): the worker is stopped with
     `claude stop` and marked closed, its branch left for later. Saying land later resumes it, or, more than 55 minutes
     after it last spoke, starts a new session in its worktree, as Reusing a worker says.
     A report whose commits sit only in `.agents_workspace` is answered accept, and the
     orchestrator then checks the worker's workspace branch and merges that workspace branch itself
     when it is not in yet. It does the same after every stop of a worker.
   - **reject**: you say whether a follow-up goes to the worker or it closes.
   - **reply**, for a blocked report: your answer goes to the same worker as its next task.

A worker runs on the orchestrator's own model unless you name one for the task. A task that needs
no plan first runs on a smaller model: `haiku` for moves, renames and one-line edits, `sonnet` for
the rest.

### Several tasks at once

The orchestrator splits a request into tasks and starts one worker per task that can run in
parallel, up to `CEH_ORCHESTRATION_MAX_WORKERS`. Tasks that must run in order, because one needs
another's result or both edit the same files, go to one worker, one task after another, each with
its own report. At the limit, the orchestrator writes the tasks it holds to the file, so a new
session still has them, and starts each as a worker closes. In a folder that is no git repository
it runs one worker there at a time, since those workers share one folder. Two workers that finish
together land one after the other.

Each reply that relays a report lists every report still awaiting your answer, oldest first, so
reports from several workers never scatter across the session. A report leaves the list once you
answer it. When the last report of a request split over several workers is in, the orchestrator
says the request is complete and sums up each task.

A worker may ask you for a permission approval directly, through Claude Code's notification. The
orchestrator tells you when that can happen, because it gets no signal for it.

### Running from a hub

A hub is a folder, a git repository or a plain one, that holds the nested repositories you work
on, git-ignored by the hub. Start the orchestrator in the hub, and it starts each worker inside
the repository its task belongs to: the nearest folder above the task's files that holds a `.git`
entry, or the hub itself. A `.agents_workspace` folder never counts, so a task on a plan goes to
the code repository around it. The worker's worktree and branch are made in that repository, its
git checks run there, and the orchestration file records it as the worker's `repo`. A request
that names no repository gets one question. A task that spans two repositories is split into one
worker each, and when the second needs the first's result, it waits in the file and starts once
the first has landed. If the first ends any other way, the orchestrator asks you what to do with
the second.

- Keep no `CLAUDE.md` in the hub: a session in a nested repository loads every `CLAUDE.md` above
  it. Keep the hub free of `.claude/rules/` too, since whether those load in a nested repository
  is unverified.
- Each nested repository's first worker stops at "Workspace not trusted", because trust does not
  reach into a nested repository. Run `claude` in that repository once, accept, and close that
  session, since with the plugin on it becomes that repository's orchestrator.
- A nested worker gets its own repository's settings and plugins and your user-level ones,
  never the hub's.
- The orchestrator's scope guard covers the nested repositories too, so their edits always go to a
  worker.

### What the orchestrator does not do

It edits no project file and starts no subagent: anything that edits files goes to a worker. Its
own files are the exceptions: the orchestration file, handoffs, the decision log, the backlog
(`.agents_workspace/BACKLOG.md`), its `.gitignore` line, and the merge of a stopped worker's
workspace branch into the main workspace branch, which it never pushes. It
never lands a code branch itself, since a worker lands its own on your word, and it never deletes a worktree with uncommitted changes,
which it leaves to you. A headless `claude -p` run, such as a scheduled job, never becomes the
orchestrator, so it does its work as an ordinary session. The `orchestrator-scope-guard` hook
enforces this section: it denies the orchestrator's own edits in the repository and its subagent
calls. It also stops a quick look growing into the task: it counts the orchestrator's Read, Grep,
Glob, Bash and PowerShell calls on each incoming message and, past its limit, denies each one
unless it is run again, which passes once, telling it to start a worker with what it has found.
The limit was set from 124 turns of 13 past orchestrator sessions.

### Starting a new session

When a new session becomes the orchestrator, because no other orchestrator runs in the repository,
it reads the machine's file at your first message,
of any kind, and takes over every worker that reports to another session. Until then a worker
whose report could not be sent waits for the handover. It resumes each stopped worker that still has a task out
and sends it a handover message, so later reports come to the new session, then lists the
workers it took over. A worker that is gone is marked lost, and it offers to send that worker's
unfinished task to a fresh worker. A worker leaves the file once it is removed or reported lost,
so the file holds only workers that still exist.

### Reusing a worker

A follow-up in the same area, such as a change you ask for before answering a report, goes to the
same worker while it is idle. A new unrelated task still gets a fresh worker.

A follow-up more than 55 minutes after the worker last spoke goes to a new session instead, started
in the same worktree and branch, under the same name, with the earlier report and the new task.
Claude Code documents idle compaction only for interactive sessions, and it was never seen in a
background worker, so once the worker's one-hour prompt cache expires, a message to it would read
its whole conversation again uncached. The new
session pays for its own start and knows the earlier work only through the report. When the
worker is removed, the orchestrator removes each of its sessions, and the first one's removal
takes the worktree and branch with it.

## Not this plugin

- Delegating to subagents inside one session: Claude Code's own `Agent` tool.
- Running a repeatable multi-stage flow: `ceh-workflow-runner`.
- The landing procedure itself: the worker follows its repository's own, such as
  `ceh-git-workflow:pull-request`.

## Where its files live

Each machine's file is `.agents_workspace/orchestration/<machine>.yaml`, named by the machine's
hostname, with its Markdown rendered beside it. The orchestrator adds `.agents_workspace/` to `.gitignore` when the
repo does not ignore it. Workers live in `<repo>/.claude/worktrees/<worker>`, `<repo>` being the
worker's repository inside the hub, on the branch `worktree-<worker>`.
