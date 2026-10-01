---
name: define-public-api
description: >-
  Load this skill when defining or changing a library's public API: deciding what to export in
  __init__.py / __all__, marking internals private, deprecating a symbol, or classifying a change as
  patch/minor/major for semver. Auto-load whenever __init__.py or __all__ is edited, a public
  function signature changes, or a version bump must be classified for a distributable library.
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires Python 3.12+ to run or type-check the code this skill shapes. Verifying the public
  surface additionally needs `uv` on PATH plus the project's `mypy` and `pytest` dev dependencies,
  which `uv sync` installs - none is assumed to be present globally.
license: Apache-2.0
---

# Define the Public API and Version It

## Define the public surface explicitly

The public API is exactly what `__init__.py` exports — nothing else is a contract.

```python
# src/your_library/__init__.py
from your_library.core import RetryPolicy, parse_duration

__all__ = ["RetryPolicy", "parse_duration"]
```

- Anything not in `__all__` (and any `_leading_underscore` name) is private — consumers must not rely on it, and you may change it freely.
- Keep the surface small. Every public symbol is a maintenance commitment.
- Re-export from a stable top-level path so internal module moves don't break consumers.

## Semantic versioning (driven by the public API)

For a library, the version contract is about the public API, not internal changes.

| Increment | When                                                                                                               |
| --------- | ------------------------------------------------------------------------------------------------------------------ |
| `MAJOR`   | Breaking change to the public API: removed/renamed symbol, changed signature, changed behavior consumers depend on |
| `MINOR`   | Backward-compatible addition: new public symbol, new optional parameter with a default                             |
| `PATCH`   | Bug fixes and internal changes with no public API effect                                                           |

When in doubt, bump the higher level — a surprise break is worse than a cautious bump. Never re-use or lower a version.

## Deprecation before removal

Never remove or change a public symbol without a deprecation period.

```python
import warnings


def old_name(*args, **kwargs):
    warnings.warn(
        "old_name() is deprecated; use new_name(). Removed in 3.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_name(*args, **kwargs)
```

- Emit `DeprecationWarning` with the replacement and the removal version.
- Keep the deprecated path working for at least one MINOR release.
- Remove it only in a MAJOR release, and document it in the changelog.
