---
name: write-pytest-service-tests
description: >-
  Load this skill when writing Python tests: adding unit tests, integration tests, test fixtures, or
  mocks. Auto-load whenever a test file is created or modified, a pytest fixture is written, or a
  decision is made about what to mock vs what to test against a real dependency.
disable-model-invocation: false
user-invocable: true
paths:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/tests/**"
  - "**/conftest.py"
compatibility: >-
  Requires Python 3.12+ and the `uv` package manager on PATH, plus network access to PyPI on first
  sync; `pytest`, `pytest-asyncio`, and `httpx` come from `uv sync`, not from a global install.
  Database-backed tests additionally need a reachable PostgreSQL instance dedicated to tests - an
  in-memory substitute will not do.
license: Apache-2.0
---

# Write pytest Tests for a Service

Framework: **pytest** with **pytest-asyncio** (`asyncio_mode = "auto"` in `pyproject.toml`)

HTTP testing: `httpx.AsyncClient` (async, preferred) or FastAPI `TestClient` (sync)

## Test structure

```
backend/
└── tests/
    ├── unit/         # Isolated — no I/O, mock all external dependencies
    ├── integration/  # Real database, mock only external APIs (LLM, payment)
    ├── system/       # Full-stack E2E — real infra, real HTTP
    └── conftest.py   # Shared fixtures: test DB, async client, mock factories
```

Test files mirror source structure. Naming: `test_<what>_<expected_behavior>.py`. One logical behavior per test.

## Choosing what to test

This skill covers the **tooling** — runner, fixtures, mocking, coverage. It does not decide
_which_ inputs and cases a test should cover. Before writing the cases, run:

> Invoke the Skill tool with skill="ceh-testing:design-test-cases"

It supplies equivalence partitions, boundary values, decision tables, pairwise combinations,
properties, and metamorphic relations — stack-agnostic technique that the sections below assume
has already been applied.

## Unit tests: no I/O

```python
class TestReasoningEngine:
    async def test_validate_rejects_unknown_event_type(self):
        engine = ReasoningEngine()
        event = ReasoningEvent(event_type="invented_type", ...)
        result = await engine.validate(event, state)
        assert result.is_invalid
        assert "invalid event type" in result.reason
```

## Integration tests: real database, never mocked

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

Each test that writes data must run in a transaction that rolls back after the test.

## Mocking rules

- Mock the LLM API client in all tests (no real API calls)
- Mock external HTTP services
- Do **not** mock PostgreSQL in integration tests
- Use `unittest.mock` or `pytest-mock`

## Coverage targets

| Area                                  | Minimum |
| ------------------------------------- | ------- |
| Python application package            | 80%     |
| Core business logic / domain services | 95%     |

```bash
uv run pytest --cov=app --cov-report=term-missing
```
