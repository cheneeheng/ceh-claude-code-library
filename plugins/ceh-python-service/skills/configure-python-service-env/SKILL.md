---
name: configure-python-service-env
description: >-
  Load this skill when setting up or configuring the Python environment: installing dependencies
  with uv, editing pyproject.toml, writing type hints or docstrings, choosing naming conventions,
  configuring ruff/mypy, or handling secrets: loading settings from environment variables, .env and
  .env.example, generating tokens, or auditing dependencies. Auto-load whenever a pyproject.toml is
  edited, a uv command is run, a secret or API key is added, a BaseSettings class is written, or a
  question arises about code style, type annotations, or import ordering. Not for frontend secrets.
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires Python 3.12+ and the `uv` package manager on PATH, plus network access to PyPI for `uv
  sync` / `uv add`. `ruff`, `mypy`, `pytest`, `uvicorn`, `alembic`, `pydantic-settings`, and
  `pip-audit` are not assumed to be installed globally - `uv` installs them into the project
  environment and commands run via `uv run`; `pip-audit` also fetches the vulnerability database
  over the network. Running the service also needs a reachable PostgreSQL instance.
license: Apache-2.0
---

# Configure the Python Service Environment

Keep a service's environment on uv, with secrets loaded from the environment and one lint and type
config. Done when `ruff` and `mypy` pass and `pyproject.toml` matches the config below.

## Procedure

1. Run every command through `uv run`, and change dependencies only with `uv add` / `uv sync`.
2. Load every secret through `pydantic-settings` from the environment, and keep `.env.example` current.
3. Write code to the coding style below.
4. Before every PR, run the three checks under Linting and type checking.

## Rules

### Environment

- Python: **3.12** | Package manager: **uv** | Virtual env: `.venv/` (managed by uv)
- Project manifest: `pyproject.toml` | Lockfile: `uv.lock` (never edit manually)

| Action                      | Command                                |
| --------------------------- | -------------------------------------- |
| Install all dependencies    | `uv sync`                              |
| Add a production dependency | `uv add <package>`                     |
| Add a dev dependency        | `uv add --dev <package>`               |
| Run any command             | `uv run <command>`                     |
| Start development server    | `uv run uvicorn app.main:app --reload` |
| Run tests                   | `uv run pytest`                        |
| Lint                        | `uv run ruff check .`                  |
| Format                      | `uv run ruff format .`                 |
| Type check                  | `uv run mypy .`                        |

**Never edit `uv.lock` manually. Never commit `.env`.**

`pyproject.toml` configuration:

```toml
[project]
name = "your-app"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["fastapi", "uvicorn[standard]", "pydantic-settings", "asyncpg", "alembic", "structlog"]

[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "N", "B"]

[tool.ruff.lint.isort]
known-first-party = ["app"]

[tool.mypy]
strict = true
python_version = "3.12"
ignore_missing_imports = false

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Secrets management

- Never hard-code secrets, API keys, or passwords in source code
- Load secrets via `pydantic-settings` (`BaseSettings`) from environment variables / `.env`
- Never commit `.env`; always maintain `.env.example` with placeholder values
- Generate cryptographic secrets: `python -c "import secrets; print(secrets.token_hex(32))"`
- Run `uv run pip-audit` before every release
- Session tokens: `secrets.token_urlsafe(32)`, never logged, never in URLs

### Coding style

- Line length: **88 characters** — follow Google Python Style Guide
- Type hints required on all function signatures and class attributes
- Use Python 3.12 built-in generics: `list[str]`, not `List[str]`
- Do not use `Any` without a comment explaining why
- All `async def` route handlers; all I/O calls use `await`

**Docstrings** (Google style, required on all public symbols):

```python
def reserve_stock(order: Order, qty: int) -> ReservationResult:
    """Reserves stock for an order.

    Args:
        order: The order requesting stock.
        qty: Units to reserve.
    Returns:
        ReservationResult with success or failure reason.
    Raises:
        InsufficientStockError: If qty exceeds available stock.
    """
```

One-line summary, then `Args` / `Returns` / `Raises` sections as needed. Omit sections that don't apply.

**Naming:**

| Kind                 | Convention            | Example                        |
| -------------------- | --------------------- | ------------------------------ |
| Variables, functions | `snake_case`          | `session_id`, `validate_event` |
| Classes              | `PascalCase`          | `SessionState`                 |
| Constants            | `UPPER_SNAKE_CASE`    | `MAX_CHALLENGES`               |
| Private members      | `_leading_underscore` | `_apply_event`                 |

**Imports** (three groups, separated by blank lines):

```python
# 1. Standard library
import asyncio

# 2. Third-party
from fastapi import HTTPException
from pydantic import BaseModel

# 3. Local application
from app.models.session import SessionState
```

**Pydantic v2:** Use `BaseModel` for all API request/response types and domain entities. Never use `time.sleep()` — use `await asyncio.sleep()`.

### Linting and type checking

**ruff** for linting and formatting (do not add flake8, pylint, isort, or Black). **mypy** for type checking.

Required before every PR:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

Do not use `# type: ignore` without a comment. Do not downgrade `strict = true` to silence errors.
