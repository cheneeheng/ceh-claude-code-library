# ceh-testing

Stack-agnostic testing **technique**: which tests to write, and whether the ones you have are worth
anything.

Your stack's testing skill owns the runner, fixtures, and mocking library
(`ceh-python-service:write-pytest-service-tests`, `ceh-python-library:write-pytest-library-tests`,
`ceh-web-frontend:write-vitest-playwright-tests`). This plugin owns the questions those do not
answer: which inputs, which scenarios, does a green suite actually catch a defect, and what does a
passing functional suite structurally miss. Load it alongside a stack plugin, not instead of one.

## Skills

| Skill                       | Invoke                                   | Triggers when                                                                                                                                                                                                                                                                                                          |
| --------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test-a-bug-fix`            | `/ceh-testing:test-a-bug-fix`            | A bug, crash, regression, or incident is being fixed: write the failing test before the fix, prove it goes red without the fix, bisect on it when the behavior used to work                                                                                                                                            |
| `design-test-cases`         | `/ceh-testing:design-test-cases`         | Deciding which inputs and scenarios to cover: partitions, boundaries, decision tables, state transitions, pairwise, properties, metamorphic relations, fuzzing, forced dependency failure                                                                                                                              |
| `audit-test-suite`          | `/ceh-testing:audit-test-suite`          | Finding out whether a passing suite would catch a defect: assertion quality, mutation testing on the diff, flakiness, level and speed, branch coverage                                                                                                                                                                 |
| `verify-behavior-preserved` | `/ceh-testing:verify-behavior-preserved` | Before a change meant to alter no observable behavior: refactor, extraction, dependency or runtime upgrade, port. Pins current behavior with characterization tests, golden files, a differential run                                                                                                                  |
| `close-test-risk-gaps`      | `/ceh-testing:close-test-risk-gaps`      | Pre-completion gate: triage concurrency, contract drift, performance, authorization, and migration/rollout gaps. A class whose trigger does not fire is skipped explicitly                                                                                                                                             |
| `write-test-first`          | `/ceh-testing:write-test-first`          | About to write code that adds or changes behavior, asked for tests or not: red, green, refactor per slice. It's working if each slice in the hand-over quotes the failure seen before its code existed                                                                                                                 |
| `measure-performance`       | `/ceh-testing:measure-performance`       | Speed, memory, or size is the task: vet the measurement against its noise, record a baseline, profile before changing, one change per measurement and one commit per win. It's working if every number is a median with its spread and a kept change clears the noise band                                             |
| `explore-app-for-bugs`      | `/ceh-testing:explore-app-for-bugs`      | The running app must be tried for bugs, not its suite: charters over the changed areas, inputs, sequence, state, and environment tours, each bug reproduced twice. Report-only unless fix mode is asked for. It's working if `QA_REPORT.md` lists each bug as confirmed or unconfirmed with its steps and evidence     |
| `write-evidence-report`     | `/ceh-testing:write-evidence-report`     | Before a launch or a post about the product: one committed `docs/EVIDENCE.md` rolled up from the latest test run and the QA, performance, security, and usability reports, read by `ceh-blog` and `ceh-seo`. It's working if every area shows passed, open issues, stale, or not run, and every claim names its figure |

The plugin ships no agents. `audit-test-suite` has a report-only mode for a large or slow suite: hand
the audit to a background subagent with the skill loaded and it returns a ranked report without
editing anything. Writing the missing tests belongs to the stack's own tester agents.

## Relation to the stack testing skills

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

## Deliberately out of scope

Real techniques left out on purpose: either they belong to another plugin, or nothing in a normal
coding session triggers them. Listed so a gap reads as a decision rather than an oversight.

| Technique                                                          | Why not here                                                                                                                                                                                  |
| ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Load, stress, soak, spike, capacity testing                        | A pre-launch capacity exercise with its own harness and environment, not a coding moment. `close-test-risk-gaps` covers the regression half by counting queries and calls instead of seconds. |
| Chaos engineering, infra fault injection, failover and DR drills   | Production-environment practice. Dependency-level fault injection _is_ covered (`design-test-cases`, rung 9).                                                                                 |
| Canary, shadow traffic, progressive rollout, post-deploy smoke     | Deploy-pipeline verification, not a coding moment.                                                                                                                                            |
| SAST, DAST, dependency and secrets scanning, pen testing           | Security review and dependency audits. Authorization testing is the one security technique kept here, because it is a unit/integration test.                                                  |
| Continuous fuzzing at scale (OSS-Fuzz, libFuzzer corpora)          | In-suite fuzzing is rung 8; standing fuzz infrastructure is a tooling decision, not a technique to apply inline.                                                                              |
| MC/DC, condition and def-use path coverage                         | Cost far exceeds diff-scoped mutation testing outside regulated domains. Noted in `audit-test-suite` rather than taught.                                                                      |
| Model-based testing, usability, localization, cross-browser/device | Either manual practice or a tooling investment; no in-session trigger moment. Exploratory, charter-based testing is in, as `explore-app-for-bugs`, since "QA this" is a moment.               |
| Runner, fixtures, mocking library, coverage thresholds, CI wiring  | The stack testing skills own these by design.                                                                                                                                                 |
