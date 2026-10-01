# ceh-python-service

Python web-service engineering standards for the FastAPI + uv + asyncpg + PostgreSQL stack.

For distributable libraries (packaging, public API, semver, no web deps) use `ceh-python-library`.

## Skills

| Skill                          | Invoke                                             | Triggers when                                                                                                 |
| ------------------------------ | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `write-fastapi-endpoints`      | `/ceh-python-service:write-fastapi-endpoints`      | Writing route handlers, dependencies, lifespan, exception handlers, or REST API design                        |
| `write-asyncpg-queries`        | `/ceh-python-service:write-asyncpg-queries`        | Writing database queries, transactions, tenant isolation, or connection pool config                           |
| `design-postgresql-schema`     | `/ceh-python-service:design-postgresql-schema`     | Designing a schema, choosing column types, or adding indexes                                                  |
| `write-alembic-migration`      | `/ceh-python-service:write-alembic-migration`      | Creating or running database migrations; migration deploy safety                                              |
| `configure-python-service-env` | `/ceh-python-service:configure-python-service-env` | Editing `pyproject.toml`, running uv commands, writing type hints, or configuring ruff/mypy                   |
| `write-pytest-service-tests`   | `/ceh-python-service:write-pytest-service-tests`   | Creating or modifying test files, fixtures, or mocks                                                          |
| `add-observability`            | `/ceh-python-service:add-observability`            | Adding structlog logging, metrics, health checks, or correlation IDs                                          |
| `secure-service-code`          | `/ceh-python-service:secure-service-code`          | Secrets management, CORS, rate limiting, or input validation                                                  |
| `model-domain`                 | `/ceh-python-service:model-domain`                 | Designing entities, identifier formats, status enums, state transitions, or route/service/db layer boundaries |

The plugin ships no hooks. The skills load from their descriptions alone, so nothing is injected into
a session that does not touch these moments. If `secure-service-code` or `add-observability` is
observed to under-trigger on implicit mid-turn decisions, sharpen its description rather than add a
hook.

## Agents

| Agent                       | When to use                                                 |
| --------------------------- | ----------------------------------------------------------- |
| `python-unit-tester`        | Write isolated unit tests for a function or class           |
| `python-integration-tester` | Write tests for module boundaries and DB interactions       |
| `python-system-tester`      | Write full E2E scenario tests (explicit request only, slow) |

All three preload `ceh-python-service:write-pytest-service-tests` and `ceh-testing:design-test-cases`.

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
