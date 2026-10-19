# Environment Variables

Every environment variable a plugin reads, in one place. Plugins have no config file of their own:
each setting is an environment variable. Set it under `env` in a Claude Code settings file,
`~/.claude/settings.json` (user: every folder you open Claude Code in) or `.claude/settings.json`
(project: this folder, and everyone who clones it, because that file is committed):

```json
{ "env": { "CEH_BRANCH_GUARD": "off" } }
```

If the file already has an `env` block, add the key to it instead of pasting the whole line over
it. To undo a setting, delete its key: every variable here has a default, shown in the table. To
check `CEH_BRANCH_GUARD`, ask Claude to edit a file while the default branch is checked out. It is
allowed once the setting applies and denied while the guard is on.

Each plugin README documents its own variables in full. This file is the index across plugins, so
a name collision or an undocumented variable is visible at a glance. Add a row in the same commit
that introduces the variable.

| Variable                     | Plugin                                                        | Read by                                                                                                      | Default              | Effect                                                                                                                                                 |
| ---------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `CEH_USAGE_LIMIT_THRESHOLD`  | `ceh-every-session`                                           | `scripts/usage-limit-watch.py`                                                                               | `90`                 | Usage percentage (5-hour or weekly window, whichever is closer to its cap) at which the agent is told to hand off                                      |
| `CEH_USAGE_STALE_MINUTES`    | `ceh-every-session`                                           | `scripts/usage-limit-watch.py`                                                                               | `15`                 | Statusline readings older than this are treated as unknown                                                                                             |
| `BULK_READER_MIN_LINES`      | `ceh-every-session`                                           | `scripts/bulk-read-guard.py`, `bulk-read-bash-guard.py`                                                      | unset (guards inert) | Opt-in. Whole-file reads at or above this many lines are denied and pointed at `delegate-bulk-reads`. `350` is a sane start                            |
| `BULK_READER_ALLOW`          | `ceh-every-session`                                           | `scripts/bulk-read-guard.py`, `bulk-read-bash-guard.py`                                                      | unset                | Colon-separated globs never blocked, on top of the built-in lockfile, minified, image and archive exclusions                                           |
| `CEH_BRANCH_GUARD`           | `ceh-git-workflow`                                            | `scripts/branch-guard.py`                                                                                    | unset (guard on)     | `off` allows file edits on the default branch, for when editing it in place is what the user asked for                                                 |
| `CEH_DISABLED_HOOKS`         | `ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow` | every hook script                                                                                            | unset (all hooks on) | Comma-separated hook script names without the extension (`branch-guard,bulk-read-guard`). A listed hook exits at once and does nothing                 |
| `TEST_DATABASE_URL`          | `ceh-python-service`                                          | `scripts/run-integration-tests.sh`, `run-system-tests.sh`                                                    | unset                | Required by the integration runner (it exits without it). The system runner only warns when this and `APP_BASE_URL` are both unset                     |
| `APP_BASE_URL`               | `ceh-python-service`                                          | `scripts/run-system-tests.sh`                                                                                | unset                | Target of the system tests. Only checked, with `TEST_DATABASE_URL`, to warn when neither is set                                                        |
| `E2E_BASE_URL`, `BASE_URL`   | `ceh-web-frontend`                                            | `scripts/run-e2e.sh`                                                                                         | unset                | Target of the E2E run (`E2E_BASE_URL` wins). A prod-looking URL is refused for anything but `smoke`                                                    |
| `NODE_ENV`                   | `ceh-web-frontend`                                            | `scripts/run-e2e.sh`                                                                                         | unset                | `production` refuses any E2E run but `smoke`, the same guard as a prod-looking URL                                                                     |
| `CEH_WORKFLOW_BUILD_DIR`     | `ceh-workflow-builder`                                        | `interview-workflow-task`, `build-agentic-workflow` (skill prose, no script)                                 | `.agents_workspace/` | Where the workflow spec and build notes are written while authoring                                                                                    |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `ceh-orchestration-lab`                                       | `plan-then-implement`, `orchestrate` (skill prose, no script)                                                | unset                | Claude Code's own variable, not a plugin setting. Read only to record it in each run, because a set value overrides the worker model the run asked for |
| `CEH_WORKFLOW_RUN_DIR`       | `ceh-workflow-builder`, `ceh-workflow-runner`                 | `build-agentic-workflow` and the single skills it generates, `run-agentic-workflow` (skill prose, no script) | `.agents_workspace/` | Where a generated workflow writes its step artifacts and run state; the runner creates `<run-dir>/<name>/<run-id>/` there                              |
