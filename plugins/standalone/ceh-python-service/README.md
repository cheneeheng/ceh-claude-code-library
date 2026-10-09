# ceh-python-service

Python web-service engineering standards for the FastAPI + uv + asyncpg + PostgreSQL stack.

For distributable libraries (packaging, public API, semver, no web deps) use `ceh-python-library`.

## Skills

| Skill                          | Invoke                       | Triggers when                                                                                                                                                                                           |
| ------------------------------ | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-fastapi-endpoints`      | Model-only, no slash command | Writing route handlers, dependencies, lifespan, exception handlers, layer boundaries, REST API design, structlog logging, metrics, `/health`, correlation IDs, CORS, rate limiting, or input validation |
| `write-postgresql-code`        | Model-only, no slash command | Designing a schema, entity IDs, status enums, writing asyncpg queries, transactions, tenant isolation, pool config, or Alembic migrations                                                               |
| `configure-python-service-env` | Model-only, no slash command | Editing `pyproject.toml`, running uv commands, writing type hints, configuring ruff/mypy, or handling secrets and `.env` files                                                                          |
| `write-pytest-service-tests`   | Model-only, no slash command | Creating or modifying test files, fixtures, or mocks                                                                                                                                                    |

The plugin ships no hooks. The skills load from their descriptions alone, so nothing is injected into
a session that does not touch these moments. The cross-cutting rules (logging, metrics, CORS, rate
limiting, secrets, entity IDs) ride on the skills that load on most service work, because their own
moments occur too rarely to load a skill of their own. If one is observed to under-trigger on
implicit mid-turn decisions, sharpen the host skill's description rather than add a hook.

## Agents

| Agent                       | When to use                                                                                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `pytest-unit-tester`        | Write isolated unit tests for a function or class                                                                                                                                                |
| `pytest-integration-tester` | Write tests for module boundaries and DB interactions                                                                                                                                            |
| `pytest-system-tester`      | Write full E2E scenario tests (explicit request only, slow)                                                                                                                                      |
| `python-service-reviewer`   | Review the Python service files of a large diff in parallel, dispatched by `ceh-git-workflow:code-review`. Read-only. It's working if every finding quotes its `path:line` from the head version |

The three testers preload `ceh-python-service:write-pytest-service-tests` and `ceh-testing:design-test-cases`.
`python-service-reviewer` preloads nothing: it loads only the skills whose files the diff touches.

## Scripts

Called by the tester agents via `bash "${CLAUDE_PLUGIN_ROOT}/scripts/<name>.sh"`.

| Script                                     | Usage                                                |
| ------------------------------------------ | ---------------------------------------------------- |
| `run-unit-tests.sh [path]`                 | Run unit tests only (excludes integration/system)    |
| `run-integration-tests.sh [path]`          | Run integration tests (requires `TEST_DATABASE_URL`) |
| `run-system-tests.sh [path] [--no-docker]` | Run system tests with optional Docker orchestration  |

## Dependencies

The tester agents preload `ceh-testing:design-test-cases` and `write-pytest-service-tests` invokes it
on every run, so the plugin declares `ceh-testing` as a dependency and Claude Code installs it
automatically.
