# Orchestration instance schema

The file `orchestrate-worker-sessions` keeps for the one long-running orchestrator of a repository
on a machine: every worker it started that still exists, with each task and report. It is saved as
`.agents_workspace/orchestration/<machine>.yaml`, where `<machine>` is the `hostname` output
lowercased. It is a singleton, found by that fixed name and edited in place, so it carries no time
prefix and no session id. The machine is in the name because the workspace syncs to its remote, so
another machine's file can arrive with a pull. A new file is a copy of
`../assets/orchestration-instance.template.yaml`, relative to this file, with
`workers_started: 0`, `workers: []` and `held: []`.

The YAML is the source. The `.md` of the same stem is generated beside it, opens with
`generated_from: <file>.yaml` and a do-not-edit `generated_note`, and shows the count of workers
started, one table of workers with each one's newest task and its status, and, when any task is
held, a table of the held tasks. Nobody edits the
Markdown. The format in code is `orchestration-instance-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `workers.0.tasks.1`
is the first worker's second task. A `v1` file, one per instance with a time prefix, is no longer
read and stays as written.

## Keys

Each required unless marked optional, and no other key allowed:

- `schema`: `orchestration-instance/v2`.
- `workers_started`: how many workers this file has ever started, 0 or more. It never goes down,
  so a worker name is never reused after its worker leaves the file.
- `workers`: a list, `[]` when none. Each worker has:
  - `name`: `<hub>-w<n>`. `<hub>` is the basename of the orchestrator's own folder, from
    `git rev-parse --show-toplevel`, or the current folder outside git, lowercased, each run of
    characters other than a-z and 0-9 turned into one `-`, and leading and trailing `-` trimmed.
    n is `workers_started + 1` when the worker is added.
  - `repo` (optional): the worker's repository, relative to the orchestrator's folder (the
    hub), written with `/`, such as `apps/billing`, or `.` for the hub itself. Absent reads as
    `.`. The orchestrator writes it on every new worker. It never starts with `/`, holds no
    drive letter or backslash, and no segment starts with `.`, so it cannot leave the hub.
  - `session_id` (optional): the full `sessionId` that `claude agents --json` lists for the
    worker, double-quoted. Absent while `starting`.
  - `reports_to`: the orchestrator session name the worker sends its reports to, from its start
    prompt or its last handover message.
  - `model`: the model the user named for this worker's task, else `haiku` for a task that only
    moves or renames files or makes a one-line edit, else `sonnet` for any other task that needs
    no plan first, else `inherit` for no `--model` flag.
  - `worktree`: the worker's worktree as a path relative to the worker's repository, or `none`
    when that repository is the hub and the hub is not a git repository.
  - `branch`: the worktree's branch, or `none`.
  - `status`: `starting` (written before the start command runs), `busy` (a task is out),
    `idle` (its turn ended), `closed` (stopped with `claude stop`) or `lost` (its session no
    longer exists, or never started).
  - `started` and `last_active`: `"YYYY-MM-DD HH:MM"`, quoted. `last_active` is the time of the
    worker's last message or report.
  - `tasks`: a list, `[]` allowed, each task sent to this worker.
- `workers[].tasks[]`: the task block's `id` (`t<n>`, counting from 1 within the worker), `goal`,
  `scope`, `inputs` (paths relative to the worker's repository, `[]` when none), `done_when`
  and `commit` (`true` or
  `false`), plus:
  - `sent`: the time the task message went out.
  - `status`: `sent`, `reported` (a report came back), `accepted` or `rejected` (the user's
    verdict on the report), or `answered` (the user replied to a `blocked` report, and the reply
    went to the worker as its next task).
  - `report` (optional): `received` (time), and the report block's `status` (`done`, `blocked` or
    `failed`), `summary`, `files` (paths changed, `[]` when none), `checks` (each `command` and
    `result`, `[]` when none) and `needs_user` (the question or approval only the user can give,
    or `none`).
- `held` (optional): a list, absent or `[]` when nothing is held, of tasks not yet sent, kept
  here so a new orchestrator session still has them. Each entry has the task block's `goal`,
  `scope`, `inputs`, `done_when` and `commit`, plus:
  - `held`: the time the task was held. It shares the list's name on purpose, as a task's time
    is named `sent`.
  - `model` (optional): the model the user named for the task.
  - `worker` (optional): the worker it is queued for, a land or the next task of its chain.
  - `follows` (optional): `true` only, for a task that goes to the same worker as the entry
    before it, in a chain held before its worker started.
  - `repo` (optional): as on a worker, the repository a fresh or waiting entry's worker starts
    in. An entry with `worker` or `follows` carries none, since its worker decides.
  - `after` (optional): a worker name, for an entry that waits for that worker to land, or
    `true`, for one that waits for the worker the nearest fresh entry before it will start,
    skipping that entry's `follows` entries. When that entry starts its worker, `after` becomes
    the worker's name.
  - With `after`, the entry is a **waiting** entry: it never starts when a slot frees. With none
    of `worker`, `follows` and `after`, it is a **fresh** entry and waits for a fresh worker.

Every value and list item is one line. A worker leaves the list when `claude rm` removes it, when
it is `closed` and `claude agents --json --all` no longer lists it, or once the user has been told
it is `lost`. Its history stays in the workspace repo's git log.

## Rules the model checks

Across keys, these six and only these:

1. A task's `report` is present exactly when its `status` is not `sent`.
2. Task ids are unique within a worker.
3. Worker names are unique.
4. Each worker's number n is at most `workers_started`.
5. A held entry's `worker` names a worker in the file, an entry never has both `worker` and
   `follows`, and the first entry has no `follows`. An entry with `worker` or `follows` has no
   `repo` and no `after`. An `after` that is a name names a worker in the file, and an
   `after: true` entry has a fresh entry before it, past any `follows` entries.
6. A worker whose `repo` is not `.` has a `worktree` other than `none`, since a nested
   repository is a git repository.

The model cannot see whether a worker's session still exists. The orchestrator sets a worker
`lost` when `claude agents --json --all` no longer lists it. Listed there without a `pid`, the
worker is stopped and can be resumed, so it is not `lost`.

## Quoting

Single-quote any value that starts with `*`, contains `: ` or ` #`, or holds a backslash, such as
`'Run: pytest'` or `'Fix issue #12'`. YAML reads a leading `*` as an alias, `: ` as a key, ` #` as a
comment, and a backslash in double quotes as an escape. Every value is strict, so quote a value
such as `0` or `1.10` that must stay text, as in a check's `result: '0'`.
