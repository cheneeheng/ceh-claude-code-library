# Orchestration instance schema

The file `orchestrate-worker-sessions` keeps for one orchestration instance: the orchestrator
session and every worker it started, with each task and report. It is saved as
`.agents_workspace/orchestration/<YYYYMMDD-HHMMSS>-<instance name>.yaml`, the time from one
`date +%Y%m%d-%H%M%S` call when the instance is opened, and edited in place after every event, so
its name carries no session id. A new instance is a copy of
`../assets/orchestration-instance.template.yaml`, relative to this file.

The YAML is the source. The `.md` of the same stem is generated beside it, opens with
`generated_from: <file>.yaml` and a do-not-edit `generated_note`, and shows the instance header and
one table of workers with each one's newest task and its status. Nobody edits the Markdown. The
format in code is `orchestration-instance-model.py` beside this file, and `scripts/artifact.py` in
the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `workers.0.tasks.1`
is the first worker's second task.

## Keys

Each required unless marked optional, and no other key allowed:

- `schema`: `orchestration-instance/v1`.
- `name`: the instance name, kebab-case, from the user or from the first task.
- `status`: `open` or `closed`.
- `created` and `updated`: `"YYYY-MM-DD HH:MM"`, quoted. `updated` changes on every write.
- `orchestrator`: `session_id`, the orchestrator's session id, and `session_name`, its name as
  the first line of `ListAgents` gives it. Workers address their reports to that name.
- `worker_model`: the model every worker starts on, or `inherit` for no `--model` flag.
- `workers`: a list, `[]` when none. Each worker has:
  - `name`: `<instance name>-w<n>`, n counting from 1 and never reused.
  - `session_id` (optional): the id the start command printed, double-quoted, since an id such as
    `12345678` is otherwise read as a number. Absent while `starting`.
  - `worktree`: the worker's worktree as a repo-relative path, or `none` outside a git repo.
  - `branch`: the worktree's branch, or `none`.
  - `status`: `starting` (written before the start command runs), `busy` (a task is out),
    `idle` (its turn ended), `closed` (stopped with `claude stop`) or `lost` (its session no
    longer exists).
  - `started` and `last_active`: times as above. `last_active` is the time of the worker's last
    message or report, and decides whether it may take a follow-up.
  - `tasks`: a list, `[]` allowed, each task sent to this worker.
- `workers[].tasks[]`: the task block's `id` (`t<n>`), `goal`, `scope`, `inputs` (repo-relative
  paths, `[]` when none), `done_when` and `commit` (`true` or `false`), plus:
  - `sent`: the time the task message went out.
  - `status`: `sent`, `reported` (a report came back), `accepted` or `rejected` (the user's
    verdict on the report).
  - `report` (optional): `received` (time), and the report block's `status` (`done`, `blocked` or
    `failed`), `summary`, `files` (paths changed, `[]` when none), `checks` (each `command` and
    `result`, `[]` when none) and `needs_user` (the question or approval only the user can give,
    or `none`).

Every value and list item is one line.

## Rules the model checks

Across keys, these four and only these:

1. A task's `report` is present exactly when its `status` is not `sent`.
2. Task ids are unique across all workers of the instance.
3. Worker names are unique.
4. An instance with `status: closed` has no worker whose `status` is `starting`, `busy` or
   `idle`.

The model cannot see whether a worker's session still exists. The orchestrator sets a worker
`lost` when `claude agents --json` no longer lists it.

## Quoting

Single-quote any value that starts with `*`, contains `: ` or ` #`, or holds a backslash, such as
`'Run: pytest'` or `'Fix issue #12'`. YAML reads a leading `*` as an alias, `: ` as a key, ` #` as a
comment, and a backslash in double quotes as an escape. Every value is strict, so quote a value
such as `0` or `1.10` that must stay text, as in a check's `result: '0'`.
