# ceh-session-orchestration

Talk to one Claude Code session and let it run the others. With this plugin, the session you
start becomes an orchestrator: it starts a full worker session for each piece of work, in its own
git worktree, sends it a task, takes its report back, and closes it once you accept the result.
Every worker, task and report is written to one checked instance file, so the orchestrator still
knows its workers after compaction.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). No other plugin depends on this one, and
it depends on none. It needs Claude Code v2.1.236+ for cross-session messaging, git for the
worker worktrees, `python3` on `PATH` for the hooks, and `uv` to check and render the instance
file. Without uv the agent is told once per session that the file went unchecked.

## Skills

| Skill                         | Say or type                          | What it does                                                                                                                         |
| ----------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `orchestrate-worker-sessions` | Model-only: there is nothing to type | The orchestrator standard: when to delegate, how to start and brief a worker, the task and report blocks, the instance file, closing |

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                               |
| -------------------- | ---------------------------------------------------------------------------------- |
| Instance file check  | Checks each written instance file and renders its Markdown beside it               |
| Generated-file guard | Stops a hand edit to the generated Markdown, which the next render would overwrite |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the instance file check and the generated-file guard off             |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

### One task, start to finish

1. You give the orchestrator a task. It opens an instance file, then starts a worker with
   `claude --bg --worktree`, named `<instance>-w1`, whose start prompt says it is a worker and
   what the orchestrator may ask of it.
2. The worker does the task in `.claude/worktrees/<worker>` and sends back a YAML report: status,
   summary, files changed, checks run, and anything only you can answer.
3. The orchestrator relays the report. When you accept it, the worker is stopped with
   `claude stop` and marked closed. Its branch stays for you to land.

A worker may ask you for a permission approval directly, through Claude Code's notification. The
orchestrator tells you when that can happen, because it gets no signal for it.

### What the orchestrator does not do

It edits no project file and starts no subagent: anything that edits files goes to a worker. It
never merges a worker's branch and never deletes a worktree with uncommitted changes, which it
leaves to you. In a run with no user present, such as a scheduled `claude -p`, it does the work
itself and starts no worker.

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

Each instance is `.agents_workspace/orchestration/<YYYYMMDD-HHMMSS>-<instance>.yaml`, with its
Markdown rendered beside it. The orchestrator adds `.agents_workspace/` to `.gitignore` when the
repo does not ignore it. Workers live in `.claude/worktrees/<worker>`, on the branch
`worktree-<worker>`.
