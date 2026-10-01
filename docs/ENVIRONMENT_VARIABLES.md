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

| Variable                    | Plugin             | Read by                                                 | Default              | Effect                                                                                                                      |
| --------------------------- | ------------------ | ------------------------------------------------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `CEH_USAGE_LIMIT_THRESHOLD` | `ceh-core`         | `scripts/usage-limit-watch.py`                          | `90`                 | Usage percentage (5-hour or weekly window, whichever is closer to its cap) at which the agent is told to hand off           |
| `CEH_USAGE_STALE_MINUTES`   | `ceh-core`         | `scripts/usage-limit-watch.py`                          | `15`                 | Statusline readings older than this are treated as unknown                                                                  |
| `BULK_READER_MIN_LINES`     | `ceh-core`         | `scripts/bulk-read-guard.py`, `bulk-read-bash-guard.py` | unset (guards inert) | Opt-in. Whole-file reads at or above this many lines are denied and pointed at `delegate-bulk-reads`. `350` is a sane start |
| `BULK_READER_ALLOW`         | `ceh-core`         | `scripts/bulk-read-guard.py`, `bulk-read-bash-guard.py` | unset                | Colon-separated globs never blocked, on top of the built-in lockfile, minified, image and archive exclusions                |
| `CEH_BRANCH_GUARD`          | `ceh-git-workflow` | `scripts/branch-guard.py`                               | unset (guard on)     | `off` allows file edits on the default branch, for when editing it in place is what the user asked for                      |
