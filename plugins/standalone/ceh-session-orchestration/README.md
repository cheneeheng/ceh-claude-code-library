# ceh-session-orchestration

Talk to one Claude Code session and let it run the others. With this plugin, the session you
start becomes an orchestrator: it starts a full worker session for each piece of work, in its own
git worktree, sends it a task, takes its report back, and closes it once you accept the result.
A repository on a machine has one long-running orchestrator, and every worker, task and report is
written to one checked file for that machine, so the orchestrator still knows its workers after
compaction or in a new session.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). No other plugin depends on this one, and
it depends on none. It needs Claude Code v2.1.236+ for cross-session messaging, git for the
worker worktrees, `python3` on `PATH` for the hooks, and `uv` to check and render the
orchestration file. Without uv the agent is told once per session that the file went unchecked.

Every session you start where the plugin is enabled becomes an orchestrator, so enable it in the
scope where you want that, such as one project. A repository on a machine has only one
orchestrator: while it runs, a second session there does not become one, and its startup line
names the orchestrator. To make the second session the orchestrator, close the first, then run
`/clear` in the second. An ordinary session, with `CEH_DISABLED_HOOKS=load-orchestrator` set for
it as [Settings](#settings) says, never counts as the orchestrator.

## Skills

| Skill                         | Say or type                        | What it does                                                                                                                              |
| ----------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `orchestrate-worker-sessions` | Nothing: it loads at session start | The orchestrator standard: when to delegate, how to start and brief a worker, the task and report blocks, the orchestration file, closing |

## Agents

This plugin has no agents.

## Hooks

Four hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                                                                                                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Orchestrator loader  | At session start and after compaction, makes the session load the orchestrator standard and prints a line saying so, unless another orchestrator already runs in the repository, which the line then names. A worker session skips it. A headless `claude -p` run, which Claude Code marks with `CLAUDE_CODE_SESSION_ATTENDED=0` (observed, not documented), skips it too |
| Scope guard          | Stops the orchestrator editing project files or starting subagents itself, and says to start a worker. Workers and other sessions are not affected                                                                                                                                                                                                                        |
| File check           | Checks each written orchestration file and renders its Markdown beside it                                                                                                                                                                                                                                                                                                 |
| Generated-file guard | Stops a hand edit to the generated Markdown, which the next render would overwrite                                                                                                                                                                                                                                                                                        |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                        | Default              | Effect                                                                                                                                                                                                                                                |
| ------------------------------- | -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK`            | unset (check on)     | `off` turns the file check and the generated-file guard off                                                                                                                                                                                           |
| `CEH_DISABLED_HOOKS`            | unset (all hooks on) | Comma-separated hook names to skip: `load-orchestrator`, `orchestrator-scope-guard`, `artifact-render-hook`, `generated-md-guard`. `load-orchestrator` keeps the session from becoming an orchestrator. A headless `claude -p` run skips it by itself |
| `CEH_ORCHESTRATION_MAX_WORKERS` | `5`                  | The most workers one orchestrator runs at once. A value that is not a whole number of at least 1 gives 5, and the startup line says so                                                                                                                |
| `CEH_ORCHESTRATION_WORKER`      | unset                | Set by the orchestrator on each worker it starts, to the repository name. Any value makes the session a worker, which does not load the orchestrator standard. Not for you to set                                                                     |

## How it works

### One task, start to finish

1. You give the orchestrator a task. It adds a worker to the machine's orchestration file, then
   starts it with `claude --bg --worktree`, named `<repo>-w<n>`, whose start prompt says it is a
   worker and what the orchestrator may ask of it.
2. The worker does the task in `.claude/worktrees/<worker>` and sends back a YAML report: status,
   summary, files changed, checks run, and anything only you can answer.
3. The orchestrator relays the report. When you accept it, the worker is stopped with
   `claude stop` and marked closed. Its branch stays for you to land.

### Several tasks at once

The orchestrator splits a request into tasks and starts one worker per task that can run in
parallel, up to `CEH_ORCHESTRATION_MAX_WORKERS`. Tasks that must run in order, because one needs
another's result or both edit the same files, go to one worker, one task after another, each with
its own report. At the limit, the orchestrator names the tasks it holds and starts each as a
worker closes.

Each reply that relays a report lists every report still awaiting your verdict, oldest first, so
reports from several workers never scatter across the session. A report leaves the list once you
accept or reject it.

A worker may ask you for a permission approval directly, through Claude Code's notification. The
orchestrator tells you when that can happen, because it gets no signal for it.

### What the orchestrator does not do

It edits no project file and starts no subagent: anything that edits files goes to a worker. It
never merges a worker's branch and never deletes a worktree with uncommitted changes, which it
leaves to you. A headless `claude -p` run, such as a scheduled job, never becomes the
orchestrator, so it does its work as an ordinary session. The `orchestrator-scope-guard` hook
enforces this section: it denies the orchestrator's own edits in the repository and its subagent
calls.

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

A follow-up in the same area, such as a change you ask for before accepting a report, goes to the
same worker while its prompt cache is warm: 60 minutes on a subscription, or 5 if you tell it the
account runs on an API key, usage credits or a cloud provider. After that, or once you have
accepted and the worker is closed, a fresh worker is cheaper.

## Not this plugin

- Delegating to subagents inside one session: Claude Code's own `Agent` tool.
- Running a repeatable multi-stage flow: `ceh-workflow-runner`.
- Landing a worker's branch: `ceh-git-workflow:pull-request`.

## Where its files live

Each machine's file is `.agents_workspace/orchestration/<machine>.yaml`, named by the machine's
hostname, with its Markdown rendered beside it. The orchestrator adds `.agents_workspace/` to `.gitignore` when the
repo does not ignore it. Workers live in `.claude/worktrees/<worker>`, on the branch
`worktree-<worker>`.
