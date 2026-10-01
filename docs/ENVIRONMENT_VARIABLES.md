# Environment Variables

Every environment variable a plugin reads, in one place. Plugins are configured through environment
variables only, never a settings file. Set them under `env` in `~/.claude/settings.json` (user) or
`.claude/settings.json` (project):

```json
{ "env": { "CEH_BRANCH_GUARD": "off" } }
```

Each plugin README documents its own variables in full. This file is the index across plugins, so
a name collision or an undocumented variable is visible at a glance. Add a row in the same commit
that introduces the variable.

| Variable                    | Plugin                 | Read by                                                                          | Default              | Effect                                                                                                                             |
| --------------------------- | ---------------------- | -------------------------------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `CEH_USAGE_LIMIT_THRESHOLD` | `ceh-core`             | `scripts/usage-limit-watch.py`                                                   | `90`                 | Usage percentage (5-hour or weekly window, whichever is closer to its cap) at which the agent is told to hand off                  |
| `CEH_USAGE_STALE_MINUTES`   | `ceh-core`             | `scripts/usage-limit-watch.py`                                                   | `15`                 | Statusline readings older than this are treated as unknown                                                                         |
| `BULK_READER_MIN_LINES`     | `ceh-core`             | `scripts/bulk-read-guard.py`, `bulk-read-bash-guard.py`                          | unset (guards inert) | Opt-in. Whole-file reads at or above this many lines are denied and pointed at `delegate-bulk-reads`. `350` is a sane start        |
| `BULK_READER_ALLOW`         | `ceh-core`             | `scripts/bulk-read-guard.py`, `bulk-read-bash-guard.py`                          | unset                | Colon-separated globs never blocked, on top of the built-in lockfile, minified, image and archive exclusions                       |
| `CEH_BRANCH_GUARD`          | `ceh-git-workflow`     | `scripts/branch-guard.py`                                                        | unset (guard on)     | `off` allows file edits on the default branch, for when editing it in place is what the user asked for                             |
| `TEST_DATABASE_URL`         | `ceh-python-service`   | `scripts/run-integration-tests.sh`, `run-system-tests.sh`                        | unset                | Required by the integration runner (it exits without it). The system runner only warns when this and `APP_BASE_URL` are both unset |
| `APP_BASE_URL`              | `ceh-python-service`   | `scripts/run-system-tests.sh`                                                    | unset                | Target of the system tests. Only checked, with `TEST_DATABASE_URL`, to warn when neither is set                                    |
| `E2E_BASE_URL`, `BASE_URL`  | `ceh-web-frontend`     | `scripts/run-e2e.sh`                                                             | unset                | Target of the E2E run (`E2E_BASE_URL` wins). A prod-looking URL is refused for anything but `smoke`                                |
| `CEH_WORKFLOW_BUILD_DIR`    | `ceh-workflow-builder` | `interview-workflow-task`, `build-agentic-workflow` (skill prose, no script)     | `.agents_workspace/` | Where the workflow spec and build notes are written while authoring                                                                |
| `CEH_WORKFLOW_RUN_DIR`      | `ceh-workflow-builder` | `build-agentic-workflow` and the workflows it generates (skill prose, no script) | `.agents_workspace/` | Where a generated workflow writes its step artifacts and run state                                                                 |
