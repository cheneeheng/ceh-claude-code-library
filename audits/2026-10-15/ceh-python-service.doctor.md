| # | Topic | Outcome | Status |
|---|---|---|---|
| 1 | Scope and assumptions | I audited all 12 prompt-bearing files in `ceh-python-service` against Claude Sonnet 5.5. Group 3 and Group 4 do not apply. | done |
| 2 | Capitalised hard rules | The testers' `NEVER`/`ALWAYS` lines mix real safety constraints with style rules. I propose rewriting 6 lines at normal volume. | inferred |
| 3 | System-test cap | The "3–8" and "NEVER more than 8" numeric ceilings are an output clamp. I propose replacing them with the goal and its reason. | inferred |
| 4 | Pytest skill examples | The integration example queries the wrong table and uses undefined names. A leaked app-specific rule says "Mock the LLM API client". | inferred |
| 5 | Env skill style lines | The file says "88 characters, follow Google Python Style Guide" but Google's limit is 80. Two other lines are padding or misplaced. | inferred |
| 6 | Full-suite runs | Two testers run the full suite unprompted, which the `agent-coding-contract` skill restricts to explicit requests. | your call |
| 7 | Behavioral probes | I ran no before/after probes, so none of these findings is behavior-verified. | unverified |

**Scope and assumptions**

- **Scope:** I audited `plugins/standalone/ceh-python-service`, which was the whole request. The inventory is 4 skills (`configure-python-service-env`, `write-fastapi-endpoints`, `write-postgresql-code`, `write-pytest-service-tests`), 4 agents (the unit, integration and system testers, and `python-service-reviewer`), `plugin.json`, the README and 3 shell scripts. I read the instruction files in full. For the scripts I only confirmed they exist at the paths the agents cite. I read no settings or credential files.
- **Target model:** The four agents pin `model: sonnet`, so I audited them against Claude Sonnet 5.5, `claude-sonnet-5-5`. The skills load into the running session, so I used the same target for them.
- **Group counts:** Group 1 has 3 findings (topics 2, 3 and part of 5). Group 2 has 3 (topics 4, 5 and 6). Group 3 is not applicable because there are no tool definitions. Group 4 is not applicable because there is no request-building code.
- **What I did not do:** The git history is commit-level only (`git log` shows three or four cleanup commits). I did not `git blame` individual lines, so I did not trace any line to a retired model.

**Capitalised hard rules**

- `agents/pytest-unit-tester.md:76-79`, `pytest-integration-tester.md:111-114` and `pytest-system-tester.md:124-128` use `NEVER`/`ALWAYS` on every line (pattern 1a, medium confidence). The production-database lines (`integration:111`, `system:124`) and "never modify source" (`unit:76`) are real constraints, so I propose keeping them and only lowering the volume. The style-only lines, such as `assert True` and "NEVER test implementation details", get a plain statement with a reason.
- Hunk 2 shows the unit-tester change. The integration and system testers follow the same pattern.

```diff
--- a/agents/pytest-unit-tester.md
+++ b/agents/pytest-unit-tester.md
@@ Hard rules
-- NEVER modify source files (only test files)
-- NEVER write tests that depend on each other
-- NEVER leave trivially-passing tests (`assert True`)
-- NEVER test implementation details — test behavior and contracts
+- Modify only test files. Report a source bug to the parent instead of fixing it.
+- Each test passes or fails on its own, in any order.
+- Assert on behavior and contracts, not internals, so a refactor does not break the suite.
+  A test that cannot fail (`assert True`) proves nothing.
```

**System-test cap**

- `agents/pytest-system-tester.md:28` ("Write 3–8 high-value scenarios") and `:125` ("NEVER write more than 8 system tests") are numeric output ceilings (pattern 1f, medium confidence). The line at `:125` already carries a reason, but 1f says a stated reason does not convert a clamp into a keeper. The intro at `:15-19` already says "Write fewer, high-value scenarios", so the goal is stated three times.
- I propose keeping one statement of the goal and its reason, with no number.

```diff
-4. **Write 3–8 high-value scenarios** — see below
+4. **Write the few scenarios that cover the main user flows** — see below
@@ Hard rules
-- NEVER write more than 8 system tests — write high-value scenarios only, because each one runs the
-  full stack and is slow and flaky enough that it must earn its cost
+- Each scenario runs the full stack and is slow and flaky, so add one only when a lower tier cannot
+  show the behavior.
```

**Pytest skill examples**

- `skills/write-pytest-service-tests/SKILL.md:66-80` is the "Integration tests" example, and it is internally inconsistent (medium confidence). It posts to `/sessions/{session_id}/message`, then queries `FROM orders WHERE order_id = $1`. Both `session_id` and `order_id` are undefined. The unit example at `:57-60` uses `ReasoningEngine` and `ReasoningEvent`, and the payload says "rewrite in Rust". These look copied from another application. The repo's `CLAUDE.md` says app-specific patterns are removed rather than kept. Example over-indexing also applies, because this single gold example freezes its shape.
- `:86` ("Mock the LLM API client in all tests") is app-specific. It sits beside a generic "Mock external HTTP services" rule that already covers it, so I propose removing the line.

```diff
-class TestSessionsAPI:
-    async def test_post_message_creates_event(self, async_client: AsyncClient, test_db):
-        response = await async_client.post(
-            f"/sessions/{session_id}/message",
-            json={"content": "I think we should rewrite in Rust"},
-        )
-        assert response.status_code == 200
+class TestOrdersAPI:
+    async def test_post_order_persists_row(self, async_client: AsyncClient, test_db):
+        response = await async_client.post("/orders", json={"sku": "A-1", "qty": 2})
+        assert response.status_code == 201
+        order_id = response.json()["order_id"]
         row = await test_db.fetchrow(
             "SELECT * FROM orders WHERE order_id = $1", order_id
         )
         assert row is not None
@@ Mocking rules
-- Mock the LLM API client in all tests (no real API calls)
 - Mock external HTTP services
```

**Env skill style lines**

- `skills/configure-python-service-env/SKILL.md:91` says "Line length: 88 characters — follow Google Python Style Guide" (medium confidence). The same file sets `line-length = 88` in the config at `:63`. From my own knowledge, Google's guide says 80, so the attribution is wrong. I did not look the guide up. I propose giving the real reason for 88.
- `:93` ("Use Python 3.12 built-in generics") restates what the model does by default on a 3.12 target, so I propose removing it (low-to-medium confidence). `:138` puts "Never use `time.sleep()`" on the Pydantic v2 line, where it does not belong. I propose moving it next to "all I/O calls use `await`" at `:95`.

```diff
-- Line length: **88 characters** — follow Google Python Style Guide
+- Line length: **88 characters** — ruff/Black default, set in `pyproject.toml`
-- Use Python 3.12 built-in generics: `list[str]`, not `List[str]`
@@
 - All `async def` route handlers; all I/O calls use `await`
+- Blocking calls stall the event loop: use `await asyncio.sleep()`, never `time.sleep()`
@@
-**Pydantic v2:** Use `BaseModel` for all API request/response types and domain entities. Never use `time.sleep()` — use `await asyncio.sleep()`.
+**Pydantic v2:** Use `BaseModel` for all API request/response types and domain entities.
```

**Full-suite runs**

- `agents/pytest-unit-tester.md:23` and `pytest-integration-tester.md:32` tell the agent to run the full suite to confirm no regressions. The `agent-coding-contract` skill, loaded in this session from another plugin, says the full suite runs only when explicitly requested. I can't tell whether these agents inherit that contract. The agents are only dispatched when the user asked for tests, so the conflict may not bite in practice. A hunk would edit either an agent that works today or a file outside this plugin. I did not draft one.

---

I read the files and ran grep signals, and I checked that the referenced scripts exist. I applied no edits. The contested hunks (3 and 5) should be probed on a scratch copy before you accept them.

**Decision: How should the full-suite conflict be resolved?**

1. Leave the agents as they are, since a dispatch already means the user asked for tests (recommended)
2. Change both agents to run only the new tests and report the full-suite command for the user to run
3. Apply the hunks above (topics 2 to 5) now and leave this item for later
