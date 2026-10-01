---
name: package-library
description: >-
  Load this skill when packaging or publishing a Python library: choosing a build backend,
  configuring pyproject.toml build metadata, laying out a src/ package, building wheels and sdists,
  or publishing to PyPI. Auto-load whenever build-system config is edited, a release is built with
  uv build, or a publish to PyPI/TestPyPI is prepared. Not for application deployment.
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires Python 3.12+ and the `uv` package manager on PATH, plus network access to PyPI for
  resolving dependencies and for `uv publish`. Nothing is assumed to be installed globally: build
  and publish run through `uv`.
license: Apache-2.0
---

# Package and Publish a Library

## Build system

Declare an explicit build backend in `pyproject.toml`. Default to **hatchling**; `uv_build` is fine if the project is uv-native.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "your-library"
version = "1.2.0"
description = "One-line summary of what the library does."
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
authors = [{ name = "...", email = "..." }]
dependencies = []  # minimal — every dependency is imposed on consumers

[project.urls]
Homepage = "https://github.com/owner/your-library"
```

## src layout (mandatory)

```
your-library/
├── pyproject.toml
├── README.md
├── src/
│   └── your_library/
│       ├── __init__.py        # defines the public API (see ceh-python-library:define-public-api)
│       └── py.typed           # ship type information (PEP 561)
└── tests/
```

The `src/` layout prevents accidentally importing the working tree instead of the installed package —
tests run against the built/installed library, catching missing-data and packaging bugs before release.

Always ship `py.typed` so consumers get your type hints.

## Build and publish

```bash
uv build                      # produces dist/*.whl and dist/*.tar.gz (wheel + sdist)
uv run twine check dist/*     # validate metadata before upload
uv publish --publish-url https://test.pypi.org/legacy/   # TestPyPI dry run first
uv publish                    # then the real PyPI
```

- Always build **both** a wheel and an sdist.
- Publish to **TestPyPI** and install from it once before publishing to real PyPI.
- A version is published exactly once — PyPI rejects re-uploads. Bump the version to fix a bad release.

## No web dependencies

A library must not pull in application/web-server dependencies (`fastapi`, `uvicorn`, `asyncpg`, web
frameworks). If web behavior is needed, expose a clean API and let the consuming application wire the
transport. Optional integrations go under `[project.optional-dependencies]`, never the base set.
