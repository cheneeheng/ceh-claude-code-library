#!/usr/bin/env python3
"""Validate the ceh-* plugin repo by running every check in checks/.

Stdlib-only so it runs locally (Windows/macOS/Linux) and in CI without installs.
Run from anywhere: `python tools/validate-plugins/validate.py`.
Exits non-zero if any check fails.

Each check is one module in checks/ and also runs alone, e.g.
`python tools/validate-plugins/checks/skills.py`. See README.md for what each one verifies.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "checks"))

from common import report, run_check  # noqa: E402

# Run in this order. A module name with `_` shows as `-` in the report.
CHECKS = [
    "manifests",
    "skills",
    "agents",
    "keys",
    "scalars",
    "references",
    "budget",
    "skill_refs",
    "deps",
    "invocations",
    "repo_rules",
    "registry",
    "hygiene",
    "scripts",
    "hooks",
]


def main() -> int:
    results = {
        name.replace("_", "-"): run_check(importlib.import_module(name).check)
        for name in CHECKS
    }
    return report(results)


if __name__ == "__main__":
    sys.exit(main())
