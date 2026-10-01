---
name: write-pytest-library-tests
description: >-
  Load this skill when writing Python tests for a library: adding unit tests, tests that exercise
  the public API, fixtures, or mocks. Auto-load whenever a test file is created or modified, a
  pytest fixture is written, or a decision is made about what to mock vs what to test for real. For
  web service testing (real DB / HTTP) use ceh-python-service instead.
disable-model-invocation: false
user-invocable: true
paths:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/tests/**"
  - "**/conftest.py"
compatibility: >-
  Requires Python 3.12+ and the `uv` package manager on PATH, plus network access to PyPI on first
  sync. `pytest` and its plugins are not assumed to be installed globally - `uv sync` installs
  them into the project environment and tests run via `uv run pytest`.
license: Apache-2.0
---

# Write pytest Tests for a Library

Framework: **pytest** with **pytest-asyncio** (`asyncio_mode = "auto"` in `pyproject.toml`)

## Test structure

```
your_library/
└── tests/
    ├── unit/         # Isolated — no I/O, mock all external dependencies
    ├── api/          # Exercise the public package API as a consumer would import it
    └── conftest.py   # Shared fixtures and mock factories
```

Test files mirror source structure. Naming: `test_<what>_<expected_behavior>.py`. One logical behavior per test.

Test against the public API surface (`import your_library`), not private modules — tests that reach
into `_private` internals lock in implementation details and break on every refactor.

## Choosing what to test

This skill covers the **tooling** — runner, fixtures, mocking, coverage. It does not decide
_which_ inputs and cases a test should cover. Before writing the cases, run:

> Invoke the Skill tool with skill="ceh-testing:design-test-cases"

It supplies equivalence partitions, boundary values, decision tables, pairwise combinations,
properties, and metamorphic relations — stack-agnostic technique that the sections below assume
has already been applied.

## Unit tests: no I/O

```python
class TestRetryPolicy:
    def test_backoff_grows_exponentially(self):
        policy = RetryPolicy(base=1.0, factor=2.0)
        assert [policy.delay(n) for n in range(3)] == [1.0, 2.0, 4.0]
```

## Public API tests: import as a consumer

```python
import your_library


def test_public_entry_point_is_importable():
    assert callable(your_library.parse_duration)
    assert your_library.parse_duration("1h") == timedelta(hours=1)
```

## Mocking rules

- Mock external HTTP services and clock/filesystem at the boundary; never mock the code under test.
- Use `unittest.mock` or `pytest-mock`.
- Prefer real objects over mocks when construction is cheap.

## Coverage targets

| Area                                  | Minimum |
| ------------------------------------- | ------- |
| Python application package            | 80%     |
| Core business logic / domain services | 95%     |

```bash
uv run pytest --cov=your_library --cov-report=term-missing
```
