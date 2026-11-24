# ceh-testing

Stack-agnostic testing **technique**: which tests to write, and whether the ones you have are worth
anything. Your stack's testing skill owns the runner, fixtures, and mocking library
(`ceh-python-service:write-pytest-service-tests`, `ceh-python-library:write-pytest-library-tests`,
`ceh-web-frontend:write-vitest-playwright-tests`). This plugin owns the questions those do not
answer: which inputs, which scenarios, does a green suite actually catch a defect, and what does a
passing functional suite structurally miss. Load it alongside a stack plugin, not instead of one.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Some parts need more installed:

| Needs                            | For                                                         | Without it                                                      |
| -------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| `python3` on PATH                | The test-file guard                                         | The guard fails open and lets every edit through                |
| [uv](https://docs.astral.sh/uv/) | Checking saved reports and fix records against their format | The agent is told once per session that the file went unchecked |

It also arrives by itself with `ceh-python-library`, `ceh-python-service` and `ceh-web-frontend`,
which depend on it.

## Skills

| Skill                       | Say or type                                                                                             | What it does                                                                                                                                                                                                                                                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test-a-bug-fix`            | "fix this bug", a stack trace, `/ceh-testing:test-a-bug-fix`                                            | Writes the failing test before the fix, proves it goes red without the fix, bisects on it when the behavior used to work, and saves a fix record.                                                                                                                                                                                |
| `design-test-cases`         | Loads by itself when deciding which inputs and scenarios a test should cover                            | Partitions, boundaries, decision tables, state transitions, pairwise, properties, metamorphic relations, fuzzing, forced dependency failure.                                                                                                                                                                                     |
| `audit-test-suite`          | "are these tests any good", "flaky test", `/ceh-testing:audit-test-suite`                               | Finds out whether a passing suite would catch a defect: assertion quality, mutation testing on the diff, flakiness, level and speed, branch coverage.                                                                                                                                                                            |
| `verify-behavior-preserved` | "refactor this", "make sure nothing broke", `/ceh-testing:verify-behavior-preserved`                    | Before a change meant to alter no observable behavior (refactor, extraction, dependency or runtime upgrade, port), pins current behavior with characterization tests, golden files, a differential run.                                                                                                                          |
| `close-test-risk-gaps`      | "is this ready", "before I open the PR", `/ceh-testing:close-test-risk-gaps`                            | A gate before calling work done: triages concurrency, contract drift, performance, authorization, and migration or rollout gaps. A class whose trigger does not fire is skipped explicitly.                                                                                                                                      |
| `write-test-first`          | "implement", "add a feature", "TDD", `/ceh-testing:write-test-first`                                    | Red, green, refactor per slice, whether or not tests were asked for. It worked if each slice in the hand-over quotes the failure seen before its code existed.                                                                                                                                                                   |
| `measure-performance`       | "make this faster", "benchmark this", `/ceh-testing:measure-performance`                                | Vets the measurement against its noise, records a baseline, profiles before changing, one change per measurement and one commit per win. It worked if every number is a median with its spread and a kept change clears the noise band.                                                                                          |
| `explore-app-for-bugs`      | "QA this", "try to break it", `/ceh-testing:explore-app-for-bugs [report \| fix] [area]`                | Tries the running app, not its suite: charters over the changed areas, inputs, sequence, state, and environment tours, each bug reproduced twice. Report-only unless fix mode is asked for. It worked if the QA report lists each bug as confirmed or unconfirmed with its steps and evidence.                                   |
| `write-evidence-report`     | "are we ready to launch", "what have we proven", `/ceh-testing:write-evidence-report [product or path]` | Before a launch or a post about the product, rolls the latest test run and the QA, performance, security, and usability reports into one evidence report, with a dated run added each time. `ceh-blog-and-seo` reads it. It worked if every area shows passed, open issues, stale, or not run, and every claim names its figure. |

## Agents

This plugin has no agents. `audit-test-suite` has a report-only mode for a large or slow suite:
hand the audit to a background subagent with the skill loaded and it returns a ranked report
without editing anything. Writing the missing tests belongs to the stack's own tester agents.

## Hooks

Three hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                         |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Test-file guard      | Stops an edit to a test file until a skill that owns writing tests has been started in the session.                                          |
| Report check         | Checks each saved report and fix record against its format when it is written, and renders its Markdown. Errors go back to the agent to fix. |
| Generated-file guard | Stops a hand edit to a Markdown file generated from a YAML file, and names the YAML to edit instead.                                         |

### Test-file guard

A test file is `test_*.py`, `*_test.py`, or `*.test.*` or `*.spec.*` in JS or TS. The guard allows
the edit once a skill that owns writing tests has been started in the session, by a `Skill` tool
call or a slash command: `write-test-first`, `test-a-bug-fix`, `verify-behavior-preserved`, or a
stack testing skill named above. A skill that another skill's steps only name ("`write-test-first`
sets out how") still has to be started. Files outside the session's project pass, and so do the
six tester agents' writes, since each preloads a testing skill. Its setting switches it off in
every plugin that ships it.

### Report check

The check covers the files this plugin's skills save: the evidence report, the QA report, the
performance reports, the test-suite audit, and the fix record. It also checks a security audit,
`UX_AUDIT.yaml` and `ERROR_MESSAGES.yaml`, so with `ceh-security-audit` or `ceh-usability-audit`
installed an error in one is reported by both plugins. A file with errors keeps its old Markdown
until the errors are fixed.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                  | Default              | Effect                                                                                                  |
| ------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK`      | unset (check on)     | `off` turns the report check and the generated-file guard off                                           |
| `CEH_SKILL_STARTED_GUARD` | unset (guard on)     | `off` turns the test-file guard off                                                                     |
| `CEH_DISABLED_HOOKS`      | unset (all hooks on) | Comma-separated hook names to skip: `skill-started-guard`, `artifact-render-hook`, `generated-md-guard` |

## How it works

### Which skill answers which question

| Question                                 | Owner                                                                 |
| ---------------------------------------- | --------------------------------------------------------------------- |
| Which runner, fixtures, mocks, CI wiring | The stack plugin's testing skill (`ceh-python-*`, `ceh-web-frontend`) |
| Which inputs and scenarios               | `design-test-cases`                                                   |
| Is this suite trustworthy                | `audit-test-suite`                                                    |
| Did this bug get a test                  | `test-a-bug-fix`                                                      |
| Did this new code get a test first       | `write-test-first`                                                    |
| What breaks when a person uses the app   | `explore-app-for-bugs`                                                |
| Did this refactor change behavior        | `verify-behavior-preserved`                                           |
| What does a passing suite still miss     | `close-test-risk-gaps`                                                |
| What has been proven, for the launch     | `write-evidence-report`                                               |

## Not this plugin

Real techniques left out on purpose: either they belong to another plugin, or nothing in a normal
coding session triggers them.

| Technique                                                          | Why not here                                                                                                                                                                                  |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Load, stress, soak, spike, capacity testing                        | A pre-launch capacity exercise with its own harness and environment, not a coding moment. `close-test-risk-gaps` covers the regression half by counting queries and calls instead of seconds. |
| Chaos engineering, infra fault injection, failover and DR drills   | Production-environment practice. Dependency-level fault injection _is_ covered (`design-test-cases`, rung 9).                                                                                 |
| Canary, shadow traffic, progressive rollout, post-deploy smoke     | Deploy-pipeline verification, not a coding moment.                                                                                                                                            |
| SAST, DAST, dependency and secrets scanning, pen testing           | Security review and dependency audits. Authorization testing is the one security technique kept here, because it is a unit/integration test.                                                  |
| Continuous fuzzing at scale (OSS-Fuzz, libFuzzer corpora)          | In-suite fuzzing is rung 8. Standing fuzz infrastructure is a tooling decision, not a technique to apply inline.                                                                              |
| MC/DC, condition and def-use path coverage                         | Cost far exceeds diff-scoped mutation testing outside regulated domains. Noted in `audit-test-suite` rather than taught.                                                                      |
| Model-based testing, usability, localization, cross-browser/device | Either manual practice or a tooling investment, with no in-session trigger moment. Exploratory, charter-based testing is in, as `explore-app-for-bugs`, since "QA this" is a moment.          |
| Runner, fixtures, mocking library, coverage thresholds, CI wiring  | The stack testing skills own these by design.                                                                                                                                                 |

## Where its files live

The plugin saves and reads its files in `.agents_workspace/product/`:

- `EVIDENCE.yaml`, the evidence report
- `qa/<YYYYMMDD-HHMMSS>-<session-id>/QA_REPORT.yaml`, the QA report
- `perf/<metric>.yaml`, a performance report
- `audit/test/`, the test-suite audits
- `fix/<YYYYMMDD-HHMMSS>-<slug>.yaml`, a fix record

Each YAML file has its Markdown rendered beside it. A project with a root `product/` moves each
file to the same sub-path there, or names its location in `CLAUDE.md`.
