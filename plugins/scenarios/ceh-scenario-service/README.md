# ceh-scenario-service

CEH scenario bundle: working on a Python backend service — features, fixes, tests, docs, releases.

This plugin ships **no skills, agents, or hooks**. It is a scenario bundle: a manifest whose only
job is to name the set of `ceh-*` plugins that belong together for one situation, so you install
one thing instead of remembering a catalogue.

## Install

```
/plugin install ceh-scenario-service@ceh-claude-code-library --scope user
```

Its dependencies are resolved and installed automatically, and enabling this plugin enables all of
them at the same scope.

## What it pulls in

| Plugin                         |
| ------------------------------ |
| `ceh-every-session`            |
| `ceh-coding-conduct`           |
| `ceh-codebase-explanation`     |
| `ceh-git-workflow`             |
| `ceh-testing`                  |
| `ceh-documentation`            |
| `ceh-python-service`           |
| `ceh-usability-audit`          |
| `ceh-build-planning`           |
| `ceh-build-from-plan`          |
| `ceh-check-build-against-plan` |
| `ceh-git-datastore`            |

## Route

The Build and Prove stages of the lifecycle in [`docs/STRATEGY.md`](../../../docs/STRATEGY.md).
Each step writes a committed file the next one reads. Nothing enforces the order.

| Stage | Skill that fires                                                                      | Reads                           | Writes                                                       |
| ----- | ------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------ |
| Build | `ceh-build-planning:write-build-plan`                                                 | `BUSINESS_PLAN.md` when present | `docs/plans/<slug>.md`                                       |
| Build | `ceh-build-from-plan:implement-from-plan`                                             | the plan                        | the code, with `ceh-python-service` skills                   |
| Prove | `ceh-check-build-against-plan:check-build-against-plan`                               | the plan, the code              | a report in the session                                      |
| Build | `ceh-build-from-plan:implement-from-plan`, retire step                                | the built plan                  | Key Decisions in `docs/ARCHITECTURE.md`; the plan is deleted |
| Prove | `ceh-testing:explore-app-for-bugs`, `ceh-usability-audit:simulate-newcomer-first-run` | the running app                 | reports in `.agents_workspace/`                              |
| Prove | `ceh-testing:write-evidence-report`                                                   | the test run, those reports     | `docs/EVIDENCE.md`                                           |

Before: `BUSINESS_PLAN.md` comes from `ceh-scenario-ideation`. After: `ceh-scenario-editorial`
reads `docs/EVIDENCE.md` for the launch.

## Notes

- Disabling any plugin above is refused while this bundle is enabled. Disable the bundle first.
- Experimental plugins are deliberately **not** bundled. Install them on their own when you want
  them.
