# ceh-scenario-library

CEH scenario bundle: working on a Python library — features, fixes, tests, docs, releases.

This plugin ships **no skills, agents, or hooks**. It is a scenario bundle: a manifest whose only
job is to name the set of `ceh-*` plugins that belong together for one situation, so you install
one thing instead of remembering a catalogue.

## Install

```
/plugin install ceh-scenario-library@ceh-claude-code-library --scope user
```

Its dependencies are resolved and installed automatically, and enabling this plugin enables all of
them at the same scope.

## What it pulls in

| Plugin                     |
| -------------------------- |
| `ceh-every-session`        |
| `ceh-coding-conduct`       |
| `ceh-codebase-explanation` |
| `ceh-git-workflow`         |
| `ceh-testing`              |
| `ceh-documentation`        |
| `ceh-python-library`       |
| `ceh-usability-audit`      |
| `ceh-plan-build-review`    |

## Notes

- Disabling any plugin above is refused while this bundle is enabled. Disable the bundle first.
- Experimental plugins are deliberately **not** bundled. Install them on their own when you want
  them.
