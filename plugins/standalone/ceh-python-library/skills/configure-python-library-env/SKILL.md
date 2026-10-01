---
name: configure-python-library-env
description: >-
  Load this skill when setting up or configuring the Python environment for a library: installing
  dependencies with uv, editing pyproject.toml, writing type hints or docstrings, choosing naming
  conventions, or configuring ruff/mypy. Auto-load whenever a pyproject.toml is edited, a uv command
  is run, or a question arises about code style, type annotations, or import ordering. Not for web
  service environments with uvicorn or asyncpg (use ceh-python-service:configure-python-service-env).
disable-model-invocation: false
user-invocable: false
compatibility: >-
  Requires Python 3.12+ and the `uv` package manager on PATH, plus network access to PyPI for `uv
  sync` / `uv add`. `ruff`, `mypy`, and `pytest` are not assumed to be installed globally - `uv`
  installs them into the project environment and every command runs via `uv run`.
license: Apache-2.0
---

# Configure the Python Library Environment

Keep a library's environment on uv, with a minimal runtime dependency set and one lint and type
config. Done when `ruff` and `mypy` pass and `pyproject.toml` matches the config below.

## Procedure

1. Run every command through `uv run`, and change dependencies only with `uv add` / `uv sync`.
2. Before adding a runtime dependency, check that every consumer should inherit it. If not, make it
   a dev dependency or an optional extra.
3. Write code to the coding style below.
4. Before every PR, run the three checks under Linting and type checking.

## Rules

### Environment

- Python: **3.12** | Package manager: **uv** | Virtual env: `.venv/` (managed by uv)
- Project manifest: `pyproject.toml` | Lockfile: `uv.lock` (never edit manually)

| Action                      | Command                  |
| --------------------------- | ------------------------ |
| Install all dependencies    | `uv sync`                |
| Add a production dependency | `uv add <package>`       |
| Add a dev dependency        | `uv add --dev <package>` |
| Run any command             | `uv run <command>`       |
| Run tests                   | `uv run pytest`          |
| Lint                        | `uv run ruff check .`    |
| Format                      | `uv run ruff format .`   |
| Type check                  | `uv run mypy .`          |

**Never edit `uv.lock` manually. Never commit `.env`.**

Keep the runtime dependency set minimal — a library inherits onto every consumer. Do not add web-service
dependencies (`fastapi`, `uvicorn`, `asyncpg`); those belong to applications, not libraries.

`pyproject.toml` configuration:

```toml
[project]
name = "your-library"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []  # keep minimal; every dependency is imposed on consumers

[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "N", "B"]

[tool.ruff.lint.isort]
known-first-party = ["your_library"]

[tool.mypy]
strict = true
python_version = "3.12"
ignore_missing_imports = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Coding style

- Line length: **88 characters** — follow Google Python Style Guide
- Type hints required on all function signatures and class attributes
- Use Python 3.12 built-in generics: `list[str]`, not `List[str]`
- Do not use `Any` without a comment explaining why

**Docstrings** (Google style, required on all public symbols):

```python
def parse_duration(text: str) -> timedelta:
    """Parses a human duration string into a timedelta.

    Args:
        text: Duration like "1h30m" or "45s".
    Returns:
        The parsed timedelta.
    Raises:
        ValueError: If the string cannot be parsed.
    """
```

One-line summary, then `Args` / `Returns` / `Raises` sections as needed. Omit sections that don't apply.

**Naming:**

| Kind                 | Convention            | Example                         |
| -------------------- | --------------------- | ------------------------------- |
| Variables, functions | `snake_case`          | `parse_duration`, `max_retries` |
| Classes              | `PascalCase`          | `RetryPolicy`                   |
| Constants            | `UPPER_SNAKE_CASE`    | `DEFAULT_TIMEOUT`               |
| Private members      | `_leading_underscore` | `_normalize`                    |

**Imports** (three groups, separated by blank lines):

```python
# 1. Standard library
import asyncio

# 2. Third-party
from pydantic import BaseModel

# 3. Local package
from your_library.core import RetryPolicy
```

Never use `time.sleep()` in async code — use `await asyncio.sleep()`.

### Linting and type checking

**ruff** for linting and formatting (do not add flake8, pylint, isort, or Black). **mypy** for type checking.

Required before every PR:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

Do not use `# type: ignore` without a comment. Do not downgrade `strict = true` to silence errors.
