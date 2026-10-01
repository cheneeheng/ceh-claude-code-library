# Testing Workflow

How the four testing-related plugins fit together in a session: what loads, when it loads, and what
the sequence looks like for the moments that actually come up.

Per-skill detail lives in `plugins/standalone/ceh-testing/README.md` and each plugin's own README.
This guide covers only what no single plugin can document: the routing _between_ them.

## The split

| Plugin               | Tier          | Owns                                                                   | Surface                                                            |
| -------------------- | ------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------ |
| `ceh-testing`        | cross-cutting | **Technique**: which inputs, which scenarios, is the suite trustworthy | 5 skills, no agents                                                |
| `ceh-python-service` | stack         | **Tooling**: pytest, test DB, httpx, fixtures                          | `write-pytest-service-tests` + 3 tester agents + runner scripts    |
| `ceh-python-library` | stack         | **Tooling**: pytest, public-API surface                                | `write-pytest-library-tests` (skill only)                          |
| `ceh-web-frontend`   | stack         | **Tooling**: Vitest, Testing Library, MSW, Playwright                  | `write-vitest-playwright-tests` + 3 tester agents + runner scripts |

`ceh-testing` is loaded **alongside** a stack plugin, never instead of one. The test for what belongs
where: would the content be byte-identical across stacks? Boundary analysis is, `asyncio_mode` is not.
`ceh-testing` deliberately shares no content with the three stack testing skills. A technique block
appearing in a stack skill means the boundary slipped.

## How each layer loads

Three different mechanisms, and the difference decides whether you have to say anything:

| Layer                | Mechanism                                                                                | Consequence                                                                |
| -------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| Stack testing skills | `paths:` globs (`**/test_*.py`, `**/*.test.{ts,tsx}`, `**/conftest.py`) plus description | Loads passively when you touch a test file, no phrasing needed             |
| `ceh-testing` skills | Description only, no `paths:`                                                            | Fires on _what you say_, not what you open. Every trigger is a moment verb |
| Tester agents        | Description auto-delegation + `skills:` preload                                          | Preloaded skills are the agent's only standards channel                    |

`SessionStart` hooks do not fire for subagents, so `skills:` in an agent's frontmatter is the only
way a standard reaches one. All six tester agents preload their stack skill plus
`ceh-testing:design-test-cases`. That preload is why the stack plugins declare `ceh-testing` as a
dependency (see `docs/PLUGIN_DEPENDENCIES.md`), so the technique skill is always installed with them.

## Routing: what you say to what runs

| Moment                                                                              | Loads                                                              |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Opening or creating a test file                                                     | Stack testing skill (passive)                                      |
| "write tests for this", "what should I test", "cover the edge cases"                | `design-test-cases` + stack skill                                  |
| "write unit/integration/system tests" (many at once)                                | Tester agents + stack skill + `design-test-cases`                  |
| "fix this bug", a pasted stack trace, "this worked last week"                       | `test-a-bug-fix`                                                   |
| "refactor this", "extract this", "upgrade this dependency"                          | `verify-behavior-preserved`                                        |
| "shrink the diff", "simplify the branch before the PR"                              | `verify-behavior-preserved` **and** `ceh-coding-agent:shrink-diff` |
| "is this ready", "before I open the PR", "race condition", "is this migration safe" | `close-test-risk-gaps`                                             |
| "are these tests any good", "why didn't the tests catch this", "flaky test"         | `audit-test-suite`, in report-only mode when the run is slow       |

## Scenario A: tests for a new feature

The common case. Phrasing matters more than it looks:

```
create unit/integration/system tests. make sure the tests have 100% code coverage.
```

1. Stack skill loads on the test paths: folder layout, what is real vs mocked, fixture patterns.
2. The unit and integration tester agents delegate. The system tester fires because you named it.
   Each spawns with the stack skill + `design-test-cases`, writes into its folder, runs its script.
3. `audit-test-suite` should pick up after the batch lands ("after generating a batch of tests").

The second sentence is the problem, see [Coverage](#coverage-what-the-number-is-for). Prefer:

```
create unit/integration/system tests. Walk the design-test-cases ladder and say which
rungs you skipped. Use --cov-branch to find files and branches at zero, then audit the suite.
```

Same three agents, same runners, but the stopping criterion becomes "every partition, boundary,
live decision-table row, invalid transition and dependency-failure path once" instead of a number
that rewards assertion-free tests.

## Scenario B: the same request in a Python library

`write-pytest-library-tests` loads and gives you `tests/unit|api`, public-API-only testing, and the
mocking rules. Then it stops: **the library plugin ships no tester agents and no runner scripts.**
Either the work stays inline in the main session, or, if `ceh-python-service` is also installed,
`pytest-unit-tester` matches "write unit tests" for any Python file and arrives carrying _service_
guidance (test DB, httpx, ASGI transport) for a library with no web dependencies.

If you work on libraries often, say "write these inline" or name the skill explicitly.

## Scenario C: a bug fix

Triggered by ordinary bug phrasing, no special vocabulary needed. `test-a-bug-fix` fires **before**
the fix and enforces the order:

1. Smallest failing test first, in the suite, before any source edit.
2. Run it and read the failure: confirm it fails for the real reason, not an import error.
3. Fix the source.
4. Prove the test is coupled to the fix: take the fix away and confirm the test goes red again. A
   test that stays green without the fix is not testing the fix.
5. Generalize one step (the boundary next to the bug), then stop.

If the behavior used to be correct, the same reproducer becomes the predicate for `git bisect run`.
The stack skill supplies the fixture and runner underneath, the technique skill owns the protocol.

## Scenario D: a refactor, and shrinking a branch

"shrink the diff" is listed as a trigger by **both** `verify-behavior-preserved` and
`ceh-coding-agent:shrink-diff`. That is deliberate: both skills change working code with no behavior
change intended, and the shrink side carries no verification step of its own. The
`Behavior preservation` block in `shrink-diff` and `refactor-repo` points back at the pinning step
for anything past a mechanical transform.

| You say                                                                               | Loads                                                                                        |
| ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| "refactor this", "extract this", "upgrade this dependency", "make sure nothing broke" | `verify-behavior-preserved` only                                                             |
| "shrink the diff", "simplify the branch before the PR"                                | both                                                                                         |
| "consolidate the branch", "can this diff be smaller"                                  | `shrink-diff` primarily                                                                      |
| `/ceh-coding-agent:refactor-repo`                                                     | `refactor-repo`, which is manual only, and it names `verify-behavior-preserved` for the pins |

**Ordering is the thing to watch.** The two want opposite ends of the timeline: pinning must happen
_before_ the edit, but "shrink the diff" is said _after_ the branch is functionally complete. That
is consistent, because the branch's current behavior is the oracle, but if the shrinking happens
first, the pins were written against already-shrunk code and prove nothing. To force the order:

```
/ceh-testing:verify-behavior-preserved     # pin behavior, commit the pins on their own
/ceh-coding-agent:shrink-diff              # then shrink; suite stays green with no test edits
```

Committing the pins separately is what lets a reviewer see they predate the change.

## Scenario E: the pre-PR gate

"is this ready" / "anything else to test" / "before I open the PR" loads `close-test-risk-gaps`.
It is a **triage gate, not a checklist**: five classes that a functional suite structurally cannot
catch: concurrency and non-idempotent retries, contract drift across a process boundary,
performance regression, broken authorization, migration and rolling-deploy incompatibility. Each has
a trigger condition and one minimal test. A class whose trigger does not fire is skipped
**explicitly** and the gate reports the skip.

Sits directly before `ceh-git-workflow:pull-request` in a normal branch flow.

## Scenario F: is this suite worth anything

Inline, `audit-test-suite` runs six checks cheapest-first: assertion audit, delete-the-code check,
mutation testing scoped to the diff, flakiness and order dependence, level and speed, branch
coverage last.

When the suite is large, the run is slow, or mutation output would flood the session, hand the audit
to a background subagent with the skill loaded and tell it to use **report-only mode**. It edits
nothing, caps the mutation run, and hands back about 15 ranked findings. Writing the missing tests
goes back to the stack's tester agents.

The highest-value defect, a test computing its expectation with the same logic as the code under
test, is invisible to every automated check and has to be read for.

## Tests that were not requested

Every `ceh-testing` skill carries a "not requested" block: writing tests and running a suite happen
only when asked. Otherwise the skill writes and runs nothing, names the test or check it would add,
and states what stays unverified so you can ask for it. The block is registered in
`docs/CROSS_REFERENCES.md` ("Tests not requested").

## Coverage: what the number is for

Every layer here agrees, and it is worth stating once because it contradicts the reflex:

- Coverage tells you which lines _ran_, never whether an assertion would have noticed them being wrong.
- Always pass `--cov-branch`. Line coverage counts an `if` with no `else` as fully covered when only
  the true side ran: green exactly where the untested half lives.
- Use it to find files and branches **at zero**. Do not chase it as a score: coverage rises fastest
  by executing code without asserting on it.
- Surviving mutants are the metric with teeth.

An explicit "100% coverage" instruction overrides all of that (per the contract's authority
hierarchy, an in-session instruction outranks a skill), and what comes back is the padded,
assertion-thin suite `audit-test-suite` exists to flag. The stack skills' own floors are 80% / 95%
core logic (Python) and 70% for `src/lib/` (frontend).

## Overlaps worth knowing

| Overlap                                                        | Resolution                                                                                                                                                                   |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `design-test-cases` vs stack testing skill                     | Technique vs tooling. Which inputs → `design-test-cases`. Which runner, fixture, mock → stack skill. A technique block appearing in a stack skill means the boundary slipped |
| `verify-behavior-preserved` vs `shrink-diff` / `refactor-repo` | Pair, don't compete: pin first, shrink second (Scenario D)                                                                                                                   |
| `pytest-system-tester` vs `playwright-system-tester`           | Both say **do not use proactively** (slow, start real infrastructure). Name system or E2E tests explicitly                                                                   |
| `pytest-unit-tester` vs `vitest-unit-tester`                   | The Python one runs only when you ask for unit tests. The Vitest one is proactive once you ask to write or improve them                                                      |
| `audit-test-suite` inline vs report-only mode                  | Same checks. Inline for a quick read, report-only in a background subagent when the run is slow or noisy                                                                     |
| `close-test-risk-gaps` vs `design-test-cases`                  | The ladder picks inputs for a function, the gate triages failure classes for a feature about to ship                                                                         |

## Install combinations

Each stack plugin depends on `ceh-testing`, so installing one brings the technique skills with it.
The `ceh-scenario-service`, `ceh-scenario-library`, and `ceh-scenario-webapp` bundles install both.

| Building                    | Install                                   |
| --------------------------- | ----------------------------------------- |
| FastAPI / async service     | `ceh-python-service`                      |
| Python package              | `ceh-python-library`                      |
| SvelteKit or React frontend | `ceh-web-frontend`                        |
| Fullstack                   | `ceh-python-service` + `ceh-web-frontend` |
| Any other stack             | `ceh-testing` alone                       |

```
/plugin install ceh-testing@ceh-claude-code-library --scope user
```

`ceh-testing` alone is usable, because the technique skills need no stack plugin, but you lose the
runner, fixtures, mocking rules, and the tester agents.
