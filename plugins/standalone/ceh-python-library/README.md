# ceh-python-library

Python engineering standards for distributable libraries: packaging, public API discipline, and
semantic versioning on the uv + ruff + mypy + pytest foundation. No web-service dependencies. Load
this plugin for library and SDK projects.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). The skills expect Python 3.12+ and
[uv](https://docs.astral.sh/uv/) on PATH, plus network access to PyPI. `ruff`, `mypy` and `pytest`
need not be installed globally: uv installs them into the project. `ceh-testing` arrives with this
plugin as a dependency, because `write-pytest-library-tests` calls its `design-test-cases` skill on
every run.

## Skills

| Skill                          | Say or type                                                                                                                                           | What it does                                                                                                                               |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `configure-python-library-env` | Loads by itself when you edit `pyproject.toml`, run a uv command, write type hints, or configure ruff or mypy                                         | Sets the library's environment and code style: uv dependencies, `pyproject.toml`, type hints, docstrings, naming                           |
| `write-pytest-library-tests`   | Loads by itself when you create or change a test file, fixture or mock                                                                                | Writes unit and public-API tests, with fixtures, and says what to mock and what to test for real                                           |
| `publish-python-library`       | `/ceh-python-library:publish-python-library`, or loads by itself on a build config or `__all__` edit, a changed public signature, or a `uv build` run | Covers the build backend, src layout, wheels and PyPI publishing, `__init__.py` and `__all__`, deprecations, and classifying a semver bump |

## Agents

This plugin has no agents.

## Hooks

This plugin has no hooks. The skills load from their descriptions alone, so nothing is injected
into a session that does not touch these moments.

## Settings

This plugin reads no settings.

## How it works

Nothing beyond the skills above.

## Not this plugin

- A FastAPI web service: `ceh-python-service`.

## Where its files live

This plugin saves no files of its own.
