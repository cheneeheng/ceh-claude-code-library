# ceh-python-library

Python engineering standards for distributable libraries: packaging, public API discipline, and
semantic versioning on the uv + ruff + mypy + pytest foundation. No web-service dependencies.

Load this plugin for library and SDK projects. Use `ceh-python-service` for FastAPI web services.

## Skills

| Skill                          | Invoke                                             | Triggers when                                                                                 |
| ------------------------------ | -------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `configure-python-library-env` | `/ceh-python-library:configure-python-library-env` | Editing `pyproject.toml`, running uv commands, writing type hints, or configuring ruff/mypy   |
| `write-pytest-library-tests`   | `/ceh-python-library:write-pytest-library-tests`   | Creating or modifying test files, fixtures, or mocks                                          |
| `package-library`              | `/ceh-python-library:package-library`              | Configuring the build backend, src layout, building wheels, or publishing to PyPI             |
| `define-public-api`            | `/ceh-python-library:define-public-api`            | Editing `__init__.py` or `__all__`, changing a public signature, or classifying a semver bump |

The plugin ships no hooks. The skills load from their descriptions alone, so nothing is injected into
a session that does not touch these moments.

## Dependencies

`write-pytest-library-tests` invokes `ceh-testing:design-test-cases` on every run, so the plugin
declares `ceh-testing` as a dependency and Claude Code installs it automatically.

## Shared standards

`configure-python-library-env` and `write-pytest-library-tests` are duplicated from
`ceh-python-service` (`configure-python-service-env` and `write-pytest-service-tests`) per the repo's
Shared-Standards Duplication Policy. The library copies drop web-service dependencies (`fastapi`,
`uvicorn`, `asyncpg`) and the uvicorn dev-server command. See `docs/CROSS_REFERENCES.md` and edit
both copies in the same session.
