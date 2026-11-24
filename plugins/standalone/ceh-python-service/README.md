# ceh-python-service

Python web-service engineering standards for the FastAPI + uv + asyncpg + PostgreSQL stack. Its
skills load by themselves while you write endpoints, database code, environment setup, or tests,
and its agents write and review the tests.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). The tester agents preload
`ceh-testing:design-test-cases` and `write-pytest-service-tests` invokes it on every run, so the
plugin declares `ceh-testing` as a dependency and Claude Code installs it automatically.

When `write-fastapi-endpoints` records an API version's timeline in `ARCHITECTURE.yaml`, it checks
the file against its model and renders `ARCHITECTURE.md` through
[uv](https://docs.astral.sh/uv/), which installs pydantic and PyYAML on first use. Without uv the
file is saved unchecked and unrendered.

## Skills

The skills have no slash command. Each loads by itself at the moment in "Say or type".

| Skill                          | Say or type                                                                                                                                                                                                                  | What it does                                                                                      |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `write-fastapi-endpoints`      | Loads by itself when writing route handlers, dependencies, lifespan, exception handlers, layer boundaries, REST API design, structlog logging, metrics, `/health`, correlation IDs, CORS, rate limiting, or input validation | Sets the standards for FastAPI endpoints, services and middleware                                 |
| `write-postgresql-code`        | Loads by itself when designing a schema, entity IDs, status enums, writing asyncpg queries, transactions, tenant isolation, pool config, or Alembic migrations                                                               | Sets the standards for PostgreSQL code in a Python service                                        |
| `configure-python-service-env` | Loads by itself when editing `pyproject.toml`, running uv commands, writing type hints, configuring ruff/mypy, or handling secrets and `.env` files                                                                          | Sets the standards for the service's environment, code style and secrets                          |
| `write-pytest-service-tests`   | Loads by itself when creating or modifying test files, fixtures, or mocks                                                                                                                                                    | Sets the standards for unit and integration tests, fixtures, and what to mock versus run for real |

## Agents

| Agent                       | What it does                                                                                                                                                                            |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pytest-unit-tester`        | Writes isolated unit tests for a function or class                                                                                                                                      |
| `pytest-integration-tester` | Writes tests for module boundaries and DB interactions                                                                                                                                  |
| `pytest-system-tester`      | Writes full E2E scenario tests (explicit request only, slow)                                                                                                                            |
| `python-service-reviewer`   | Reviews the Python service files of a large diff in parallel, dispatched by `ceh-git-workflow:write-code-review`. Read-only. Every finding quotes its `path:line` from the head version |

## Hooks

This plugin has no hooks.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable            | Default | Effect                                                                                                                                         |
| ------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `TEST_DATABASE_URL` | unset   | Required by the integration test runner, which exits without it. The system test runner only warns when this and `APP_BASE_URL` are both unset |
| `APP_BASE_URL`      | unset   | Target of the system tests. Only checked, with `TEST_DATABASE_URL`, to warn when neither is set                                                |

## How it works

### How the tester agents run tests

The three testers preload `ceh-python-service:write-pytest-service-tests` and
`ceh-testing:design-test-cases`. `python-service-reviewer` preloads nothing: it loads only the
skills whose files the diff touches.

The testers run the suites with `uv run pytest` from a bash script, so they need bash and `uv` on
`PATH`. Unit tests run with nothing else. Integration tests need `TEST_DATABASE_URL`. System tests
start the services from `docker-compose.test.yml` with Docker when the project has that file.

## Not this plugin

- Distributable libraries (packaging, public API, semver, no web deps): `ceh-python-library`.

## Where its files live

The plugin saves and reads product files in `.agents_workspace/product/`. A project with a root
`product/` folder moves each file to the same sub-path under `.agents_workspace/product/`, or names
its own location in `CLAUDE.md`.
