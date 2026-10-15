# Model audit: ceh-python-service

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no
- WARNING: 1 tool call(s) were denied, so the report may be incomplete.

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-python-service.doctor.md](ceh-python-service.doctor.md).

## Kept changes

### skills/write-pytest-service-tests/SKILL.md:66-80
Rules 1 and 3. The example posts to `/sessions/{session_id}/message` and then queries `FROM orders WHERE order_id = $1`. The names `session_id` and `order_id` are never defined. This is a model-independent defect, and it breaks the "relevant" standard for examples.

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "Relevant: Mirror your actual use case closely." and "Diverse: Cover edge cases and vary enough that Claude doesn't pick up unintended patterns."

Before:
```python
class TestSessionsAPI:
    async def test_post_message_creates_event(self, async_client: AsyncClient, test_db):
        response = await async_client.post(
            f"/sessions/{session_id}/message",
            json={"content": "I think we should rewrite in Rust"},
        )
        assert response.status_code == 200
        row = await test_db.fetchrow(
            "SELECT * FROM orders WHERE order_id = $1", order_id
        )
        assert row is not None
```
After:
```python
class TestOrdersAPI:
    async def test_post_order_persists_row(self, async_client: AsyncClient, test_db):
        response = await async_client.post("/orders", json={"sku": "A-1", "qty": 2})
        assert response.status_code == 201
        order_id = response.json()["order_id"]
        row = await test_db.fetchrow(
            "SELECT * FROM orders WHERE order_id = $1", order_id
        )
        assert row is not None
```

### skills/write-pytest-service-tests/SKILL.md:57-63
Rule 1, added beyond the report. The unit example uses the app-specific `ReasoningEngine` and `ReasoningEvent`. It also relies on an undefined `state` and an `...` placeholder. The report flags these names as copied from another app but only fixes the integration example.

Quote (same page): "Relevant: Mirror your actual use case closely."

Before:
```python
class TestReasoningEngine:
    async def test_validate_rejects_unknown_event_type(self):
        engine = ReasoningEngine()
        event = ReasoningEvent(event_type="invented_type", ...)
        result = await engine.validate(event, state)
        assert result.is_invalid
        assert "invalid event type" in result.reason
```
After:
```python
class TestOrderService:
    async def test_reserve_rejects_qty_above_stock(self):
        service = OrderService(stock={"A-1": 1})
        result = await service.reserve("A-1", qty=2)
        assert result.is_invalid
        assert "insufficient stock" in result.reason
```

### skills/write-pytest-service-tests/SKILL.md:86
Rule 4. The line is an app-specific leak, and the generic rule on the next line already covers it. The Procedure ("Mock external APIs only") and the structure comment at line 47 ("mock only external APIs (LLM, payment)") cover it too. Deleting it changes nothing the model does.

Quote (repo `CLAUDE.md`, a repo rule rather than a model guide): "App-specific patterns are not standards. Anything bound to one application's schema or design is removed rather than kept as a niche plugin."

Before:
```
- Mock the LLM API client in all tests (no real API calls)
- Mock external HTTP services
```
After:
```
- Mock external HTTP services
```

### skills/configure-python-service-env/SKILL.md:91
Rule 3. The line says "88 characters — follow Google Python Style Guide". Google's guide sets 80, so the two halves of the instruction contradict each other. The report's fix gives the real reason for 88. I did not look up Google's limit myself, so that figure comes from the report.

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals".

Before: `- Line length: **88 characters** — follow Google Python Style Guide`
After: `- Line length: **88 characters** — ruff/Black default, set in `pyproject.toml``

### skills/configure-python-service-env/SKILL.md:93
Rule 4. The model writes `list[str]` by default on a 3.12 target. The `UP` ruff rule set at line 66 also enforces it. Deleting the line changes nothing the model does.

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, Claude 4.6 migration list): "Tune anti-laziness prompting: If your prompts previously encouraged the model to be more thorough or use tools more aggressively, dial back that guidance." This is only loosely related. The real basis is that the sentence is redundant.

Before: `- Use Python 3.12 built-in generics: `list[str]`, not `List[str]``
After: (line removed)

### skills/configure-python-service-env/SKILL.md:95 and :138
Rule 1. "Never use `time.sleep()`" sits on the Pydantic v2 line, where it does not belong. The change moves it next to the `await` rule and adds the reason. The page asks for the reason behind a rule, and the bare "Never use…" is the form it rates "less effective".

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "Less effective: NEVER use ellipses. More effective: Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them."

Before:
```
- All `async def` route handlers; all I/O calls use `await`
...
**Pydantic v2:** Use `BaseModel` for all API request/response types and domain entities. Never use `time.sleep()` — use `await asyncio.sleep()`.
```
After:
```
- All `async def` route handlers; all I/O calls use `await`
- Blocking calls stall the event loop: use `await asyncio.sleep()`, never `time.sleep()`
...
**Pydantic v2:** Use `BaseModel` for all API request/response types and domain entities.
```

### skills/write-postgresql-code/SKILL.md:20-23
Rule 4, added beyond the report. The opening has no statement of when the task is done. The other three skills each carry a "Done when…" sentence, and the Procedure steps define the criteria.

Quote: the rule 4 wording in the task brief itself, "a missing statement of when the task is done, added to the file's opening."

Before: `...Plain parameterized SQL keeps every query visible in review, where an ORM hides it. Never modify the database schema by hand.`
After: `...Plain parameterized SQL keeps every query visible in review, where an ORM hides it. Never modify the database schema by hand. Done when every schema change is an Alembic migration with a working `downgrade()` and every query is parameterized and scoped by `owner_id`.`

### skills/write-fastapi-endpoints/SKILL.md:166
Rule 1, added beyond the report. This is a negative instruction that says the same thing as its positive form.

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "Tell Claude what to do instead of what not to do".

Before: `Always declare `response_model=SomePydanticModel`. Never return raw dicts.`
After: `Declare `response_model=SomePydanticModel` on every route and return model instances.`

### Considered and left out
- Full-suite runs (report topic 6): the report's own decision block recommends leaving the agents unchanged. The affected testers are also pinned files.
- Capitalised `NEVER`/`ALWAYS` lines and the system-test cap (report topics 2 and 3): all of them sit in the pinned agent files.
- The `Do not return 200 for errors` pair and the `Do not use the deprecated @app.on_event` line: the positive rewrite would not say exactly the same thing, so they fail rule 4.

## Pinned tuning: `agents/pytest-integration-tester.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Line 39: asyncpg fixture heading (rule given without its reason)

Guide: "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses. [...] Claude is smart enough to generalize from the explanation." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
**asyncpg — rollback after each test (required — no SQLAlchemy):**
```

After:

```markdown
**asyncpg, rolled back after each test.** The service stack uses asyncpg directly with no ORM, so
fixtures use asyncpg, not SQLAlchemy. The rollback leaves the next test a clean database:
```

#### Process step 5: Run & fix (real check, failed starts, loosened assertions)

Guide: "If you see changes reported as complete without test or build output in the transcript, add this paragraph [...]: 'When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done [...]. A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile [...], never via sudo or the system package manager, unless told not to. Only if no real check can run here, say which one you did not run and why instead of reporting the change as done.'" https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

Guide: "If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
5. **Run & fix** — execute tests, check env vars and test DB if connection errors appear;
   run full suite to confirm no regressions
```

After:

```markdown
5. **Run & fix** — run the new tests with the script below, then the full suite to confirm no
   regressions. A run that fails to start, such as a connection error or a missing
   `TEST_DATABASE_URL`, does not count as a check. Check the env vars and the test database, and
   if only the project's declared dependencies are missing, install them with `uv sync`, never
   sudo or the system package manager. If no real run is possible, report it as "not run" with
   the reason. When a test fails because the source behaves wrongly, keep the assertion that
   states the correct behavior and report the bug. Do not loosen the assertion to make it pass.
```

#### Line 69: marker comment (capitalized emphasis)

Guide: "If your prompts were designed to reduce undertriggering on tools or skills, these models may now overtrigger. The fix is to dial back any aggressive language. Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```python
@pytest.mark.integration  # REQUIRED — runner filters by this marker
```

After:

```python
@pytest.mark.integration  # the runner selects tests by this marker, so every class needs it
```

#### Lines 80-81: Coverage targets (scope stated explicitly)

Guide: "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another [...]. If you need Claude to apply an instruction broadly, state the scope explicitly (for example, 'Apply this formatting to every section, not just the first one')." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

```markdown
**Coverage targets:** happy path, failure propagation, data integrity, transaction/rollback
behavior, auth/permission boundaries.
```

After:

```markdown
**Coverage targets**, for every boundary you test, not only the first: happy path, failure
propagation, data integrity, transaction/rollback behavior, auth/permission boundaries. Skip a
target only when the boundary does not have it, such as an endpoint with no auth, and say so in
the report.
```

#### Lines 92-104: Output to parent session (one example, success case only)

Guide: "When adding examples, make them: [...] **Diverse:** Cover edge cases and vary enough that Claude doesn't pick up unintended patterns. **Structured:** Wrap examples in `<example>` tags (multiple examples in `<examples>` tags) so Claude can distinguish them from instructions." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Guide: "Positive examples showing how Claude can communicate with the appropriate level of concision tend to be more effective than negative examples or instructions that tell the model what not to do." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

````markdown
- Bugs found in source (report, do NOT fix silently)

```
PASS — 9 tests added in tests/integration/test_user_service_integration.py.
Boundary: POST /users -> UserService -> users table.
Needs: TEST_DATABASE_URL pointing at a migrated test database.
Bugs: none.
```
````

After:

````markdown
- Bugs found in source (report them, and leave the source unchanged, because fixing source is
  the parent's call)

<examples>
<example>
```
PASS — 9 tests added in tests/integration/test_user_service_integration.py.
Boundary: POST /users -> UserService -> users table.
Needs: TEST_DATABASE_URL pointing at a migrated test database.
Bugs: none.
```
</example>
<example>
```
FAIL — 6 tests added in tests/integration/test_order_service_integration.py, 5 pass, 1 fails.
Boundary: POST /orders -> OrderService -> orders, order_items tables.
Needs: TEST_DATABASE_URL pointing at a migrated test database.
Bugs: OrderService.create commits the orders row before inserting items, so a failed item
insert leaves an orphan order (test_failed_item_insert_rolls_back_order).
```
</example>
<example>
```
NOT RUN — 4 tests added in tests/integration/test_invoice_integration.py, not executed.
Boundary: GET /invoices/{id} -> InvoiceRepo -> invoices table.
Needs: TEST_DATABASE_URL is unset, and no test database is reachable here.
Bugs: none found by reading. Parent: provide a test database, then rerun the script.
```
</example>
</examples>
````

#### Lines 106-116: Hard rules (capitalized emphasis, no reasons, carrying work through, unrequested additions)

Guide: "Where you might have said 'CRITICAL: You MUST use this tool when...', you can use more normal prompting like 'Use this tool when...'." and "Providing context or motivation behind your instructions [...] can help Claude better understand your goals." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Guide: "On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might [...] stop after one part of a multipart task to ask whether to continue. [...] 'Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.'" and "The model tends to add tests, documentation, and small supporting files that fit your repository's conventions, even when you don't ask for them. [...] If you prefer changes limited to what was explicitly requested, add only the second paragraph [...]: 'When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it.'" https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

Before:

```markdown
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
- Report a check you could not run as "not run" with the reason. Never imply it passed.
- NEVER use the production database — always require `TEST_DATABASE_URL`
- NEVER leave DB state between tests — rollback via transaction fixture
- NEVER mock internal components (that's unit testing)
- ALWAYS mock third-party external services
- Each test independently runnable (no ordering dependencies)
- Fixture scope tight — prefer function scope unless session-level setup is expensive
```

After:

```markdown
- You cannot ask questions, and your final message ends the run. Keep working until every
  boundary the parent named is tested and run. Stop early only when you are blocked, and then
  make the blocker your final message: what you finished, what stopped you, what the parent
  should decide.
- When the requested tests are written and run, stop and report. Do not add docs, CI config,
  source changes, or tests for boundaries the parent did not name. Mention any you think would
  help at the end of the report instead.
- Report a check you could not run as "not run" with the reason. Never imply it passed.
- Connect only through `TEST_DATABASE_URL`, never to the production database, because the tests
  write and roll back data.
- Roll back every test's database changes through the transaction fixture, so no test depends on
  state another one left behind.
- Use the real internal components. Mocking them turns the test into a unit test and hides the
  integration this agent exists to check.
- Mock every third-party external service, so tests stay fast, free, and deterministic, and never
  touch a real account.
- Make each test runnable on its own, with no dependence on the order tests run in.
- Keep fixture scope tight: function scope, unless a session-level setup is expensive.
```

## Pinned tuning: `agents/pytest-system-tester.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Line 29, Process step 5 "Run & fix"

> "When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done [...] A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile [...] never via sudo or the system package manager"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

> "If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
5. **Run & fix** — execute, investigate infra/timing/cleanup failures before touching source
```

After:

```markdown
5. **Run & fix** — run the new tests with the script under Running tests. A collection-only run
   or a command that failed to start does not count as a run. If only the project's declared
   dependencies are missing, install them from its lockfile (`uv sync`), never with sudo or the
   system package manager. Fix infra, timing, and cleanup failures in the test code. When a
   failure traces to the application, keep the assertion on the correct behavior and report it
   as a bug. Leave the source and the assertion unchanged, because the parent decides the fix.
```

#### Line 30, Process step 6 "Report"

> "When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

Before:

```markdown
6. **Report.** Return the output below as your final message.
```

After:

```markdown
6. **Report.** When the system tests are written and run, stop and return the output below as
   your final message. Don't add unit or integration tests, docs, or source changes that weren't
   asked for. If you think one would help, mention it in the report instead.
```

#### Line 63, DB reset after each scenario

> "It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make. [...] If you need Claude to apply an instruction broadly, state the scope explicitly"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

```markdown
Use an `autouse` fixture to reset DB state after each scenario (truncate tables or re-run migrations).
```

After:

```markdown
Use an `autouse` fixture to reset every stateful service the scenarios touch after each scenario:
the DB (truncate tables or re-run migrations), queues (purge), and any cache or file store.
```

#### Line 70, the `pytest.mark.system` comment

> "The fix is to dial back any aggressive language. Where you might have said "CRITICAL: You MUST use this tool when...", you can use more normal prompting like "Use this tool when...""
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```python
@pytest.mark.system  # REQUIRED — prevents accidental execution by other runners
```

After:

```python
@pytest.mark.system  # required on every system test class: keeps other runners from collecting it
```

#### Line 108, Output "Bugs discovered"

> "Tell Claude what to do instead of what not to do"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
- Bugs discovered (report clearly, do NOT fix silently)
```

After:

```markdown
- Bugs discovered: each with the failing scenario and the observed versus expected behavior, source left unchanged
```

#### Lines 124 to 128, Hard rules in capitals

> "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses." and "The fix is to dial back any aggressive language."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
- NEVER run against production — always require explicit test environment config
- NEVER write more than 8 system tests — write high-value scenarios only, because each one runs the
  full stack and is slow and flaky enough that it must earn its cost
- ALWAYS clean up state between scenarios (order-independent)
- NEVER assert on internal implementation — only externally observable behavior
```

After:

```markdown
- Run only against an environment the config names as test (such as `TEST_DATABASE_URL`). If none
  is set, stop and report it, because system tests write, truncate, and tear down real data.
- Write at most 8 system tests, high-value scenarios only, because each one runs the full stack
  and is slow and flaky enough that it must earn its cost.
- Reset state between scenarios so they pass in any order, because a scenario that depends on
  another's leftovers fails when run alone.
- Assert only on externally observable behavior (responses, persisted records, emitted messages),
  so the tests survive refactors of internals.
```

#### Line 130, `pytest-timeout`

> "Claude Sonnet 5 interprets prompts literally and explicitly [...] it does not infer requests you didn't make."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

```markdown
- Requires `pytest-timeout`: `uv add --dev pytest-timeout`
```

After:

```markdown
- The tests require `pytest-timeout`. If it is not already a declared dev dependency, list
  `uv add --dev pytest-timeout` under Manual setup instead of adding it yourself.
```

## Pinned tuning: `agents/pytest-unit-tester.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Line 23, Process step 4 "Run & fix"

> "On agentic coding tasks, Claude Sonnet 5.5 generally checks its work before it reports a change as done. At `low` effort, though, it sometimes reports a change as done without running a check that exercises it. For example, it might skip the project's tests because the project's dependencies aren't installed. [...] A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#verification-on-coding-tasks

Before:

```markdown
4. **Run & fix** — execute tests, fix failures, then run the full suite to confirm no regressions
```

After:

```markdown
4. **Run & fix** — run the new tests with the script below, fix failures, then run the full suite
   to confirm no regressions. A run counts only when pytest collected and executed the tests. An
   import check, or a command that failed to start, does not count. If all that is missing is the
   project's declared dependencies, install them with its own package manager and lockfile (e.g.
   `uv sync`, `pip install -r requirements.txt`), never via sudo or the system package manager.
```

#### Lines 40 and 42, Mocking

> "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses. [...] Claude is smart enough to generalize from the explanation."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance

> "The fix is to dial back any aggressive language. Where you might have said "CRITICAL: You MUST use this tool when...", you can use more normal prompting like "Use this tool when..."."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
- Mock ALL external dependencies (DB, HTTP, filesystem, time)
- Use `unittest.mock.patch` or `pytest-mock`'s `mocker` fixture
- Mock at the point of use, not definition
```

After:

```markdown
- Mock every external dependency (DB, HTTP, filesystem, time), so each test runs fast and gives
  the same result on every machine
- Use `unittest.mock.patch` or `pytest-mock`'s `mocker` fixture
- Patch the name where the module under test looks it up (`patch("app.pricing.requests.get")`),
  not where it is defined, because `patch` replaces a name in one namespace only
```

#### Lines 54-55, failing tests

> "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5#more-literal-instruction-following

> "Tests are there to verify correctness, not to define the solution. [...] If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#avoid-focusing-on-passing-tests-and-hardcoding

The current "fix the test, not the source, unless a genuine bug is confirmed" contradicts the hard rule "NEVER modify source files". A literal reader can take the "unless" as permission to edit source. It also never forbids the usual workaround: changing an expected value to match buggy output.

Before:

```markdown
If tests fail: fix the test, not the source, unless a genuine bug is confirmed. Report bugs
clearly; do not silently change source.
```

After:

```markdown
If a test fails, decide from the signature, docstring, and callers whether the test or the source
is wrong. Fix a wrong test. Leave wrong source as it is: keep the test asserting the documented
behavior and report the bug under Bugs. Never change an expected value only to match what the code
returns, because then the test pins the bug instead of catching it.
```

#### Lines 73-74, Hard rules: blocked

> "On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might pause to confirm a plan, ask a question it could answer itself, or stop after one part of a multipart task to ask whether to continue. [...] Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step. When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#steer-initiative-and-scope

> "The model tends to add tests, documentation, and small supporting files that fit your repository's conventions, even when you don't ask for them. It does this at every effort level, and more at higher effort."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5#steer-initiative-and-scope

Before:

```markdown
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
```

After:

```markdown
- You cannot ask questions, so keep working until every test you were asked for is written and
  run. Stop early only when you can't go on, and then make the blocker your final message: what
  you finished, what stopped you, what the parent should decide.
- When the requested tests are written and the suite has run, stop and report. Don't add tests for
  code you were not asked to cover, docs, helpers, or refactors of existing tests.
```

#### Lines 76-79, Hard rules: NEVER block

> "**Tell Claude what to do instead of what not to do**"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#control-the-format-of-responses

> "**Less effective:** `NEVER use ellipses` **More effective:** `Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them.`"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance

Before:

```markdown
- NEVER modify source files (only test files)
- NEVER write tests that depend on each other
- NEVER leave trivially-passing tests (`assert True`)
- NEVER test implementation details — test behavior and contracts
```

After:

```markdown
- Change only test files, `conftest.py` included. Report source bugs instead, because the parent
  session decides how source changes.
- Give each test its own setup through fixtures, so it passes alone and in any order.
- Make every assertion able to fail: check a return value, a raised exception, or a mock's call.
  An `assert True` test proves nothing.
- Assert on behavior a caller can see (return values, raised exceptions, calls to mocked
  dependencies), not private attributes or internal call order, so a refactor that keeps behavior
  keeps the tests green.
```

## Pinned tuning: `agents/python-service-reviewer.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Process step 4 (lines 25-28): the review areas are examples, not a closed list

> "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make. [...] If you need Claude to apply an instruction broadly, state the scope explicitly"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

```
4. **Review in this order**: correctness (edge cases, swallowed errors, transaction and session
   handling, async misuse), security (SQL built from strings, unvalidated input reaching a query,
   secrets in code or logs), migrations (reversible, safe on a live table), tests (does new
   behavior have one, does it assert behavior), then the loaded standards.
```

After:

```
4. **Review in this order**: correctness (edge cases, swallowed errors, transaction and session
   handling, async misuse), security (SQL built from strings, unvalidated input reaching a query,
   secrets in code or logs), migrations (reversible, safe on a live table), tests (does new
   behavior have one, does it assert behavior), then the loaded standards. The items in
   parentheses are examples of what each area covers, not the whole of it: report any problem
   that belongs to the area.
```

#### Process step 4 (line 28): say the job is coverage, and set the bar in concrete terms

> "If your harness has a separate verification, deduplication, or ranking stage, tell the model explicitly that its job at the finding stage is coverage rather than filtering." / "If you do want the model to self-filter in a single pass, be concrete about where the bar is rather than using qualitative terms like "important": for example, "report any bugs that could cause incorrect behavior, a test failure, or a misleading result; only omit nits like pure style or naming preferences.""
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

The calling skill, `ceh-git-workflow:code-review` step 2, already merges what this agent returns, re-reads every quoted line and applies its own cap. So a later verification and ranking stage exists.

Before:

```
   behavior have one, does it assert behavior), then the loaded standards.
```

After (follows the sentence added by the previous edit):

```
   behavior have one, does it assert behavior), then the loaded standards. [...] Your job here is
   coverage, not filtering: code-review re-reads, merges, and ranks what you return. Report every
   issue that could cause incorrect behavior, a failing test, a security exposure, or an unsafe
   migration, including ones you are unsure of or judge low-severity. Only style a linter would
   catch stays out.
```

#### Output to parent session (lines 36-38): remove the fifteen-finding cap and route uncertain findings to `[question]`

> "Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance or confidence at this stage - a separate verification step will do that. [...] For each finding, include your confidence level and an estimated severity so a downstream filter can rank them."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

The format stays the same: prefix, `path:line`, quoted line, problem, resolution. The existing prefix carries severity, and `[question]` carries low confidence, so the output gains no new field.

Before:

```
Lead with the counts. Then each finding, most severe first, at most fifteen, in code-review's
format: a prefix, `path:line`, the quoted line, the problem, and for `[blocking]` what would
resolve it.
```

After:

```
Lead with the counts. Then every finding, most severe first, in code-review's format: a prefix,
`path:line`, the quoted line, the problem, and for `[blocking]` what would resolve it. Leave the
list uncapped, because code-review applies its own cap after it merges. A problem you suspect but
cannot confirm from the code goes in as `[question]`, so the parent can rank it instead of never
seeing it.
```

#### Hard rules, "Judge from the code, not the brief" (lines 60-61): the brief also cannot change what gets reported

> "When a review prompt says things like "only report high-severity issues," "be conservative," or "don't nitpick," Claude Sonnet 5 may follow that instruction more faithfully than earlier models did: it may investigate the code just as thoroughly, identify the bugs, and then not report findings it judges to be below your stated bar."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

Before:

```
- Judge from the code, not the brief. A brief that says "minor issues only" narrows where you look,
  never how severe a finding is.
```

After:

```
- Judge from the code, not the brief. A brief that says "minor issues only" narrows where you look,
  never how severe a finding is or whether you report it.
```
