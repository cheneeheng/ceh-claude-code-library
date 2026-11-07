#!/usr/bin/env python3
"""
check-semver.py
Validates semantic versioning format in a CHANGELOG.md file.

Usage:
    python3 check-semver.py [path/to/CHANGELOG.md]

Checks:
    - All version headers match semver (MAJOR.MINOR.PATCH[-prerelease][+build])
    - Dates are valid YYYY-MM-DD
    - Versions are in descending order (newest first)
    - No duplicate versions
    - [Unreleased] appears at most once and before any versioned entry

Requires: Python 3.6+, stdlib only.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Regexes ───────────────────────────────────────────────────────────────────

# Full semver: 1.2.3  /  1.2.3-alpha.1  /  1.2.3+build.42  /  1.2.3-rc.1+sha.abc
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# ## [1.2.3] - 2024-01-15   or   ## [1.2.3] — 2024-01-15   or   ## [Unreleased]
# Accept either a hyphen or an em-dash as the date separator.
VERSION_HEADER_RE = re.compile(r"^##\s+\[([^\]]+)\](?:\s+[-—]\s+(\S+))?")


# ── Helpers ───────────────────────────────────────────────────────────────────


def parse_semver(version: str) -> Optional[tuple]:
    """Return (major, minor, patch, pre) tuple or None if invalid."""
    m = SEMVER_RE.match(version)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4) or "")


def semver_key(parsed: tuple) -> tuple:
    """
    Sort key for semver tuples — higher = newer.
    Pre-release versions sort BELOW the release (semver spec §11).
    """
    major, minor, patch, pre = parsed
    # No pre-release → higher precedence than any pre-release
    pre_rank = (1,) if not pre else (0, pre)
    return (major, minor, patch) + pre_rank


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    file_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("CHANGELOG.md")

    if not file_path.exists():
        print(f"ERROR: File not found: {file_path.resolve()}")
        sys.exit(1)

    lines = file_path.read_text(encoding="utf-8").splitlines()

    errors = []
    warnings = []

    versions = []  # list of dicts: {version, parsed, date, line_num}
    unreleased_count = 0
    unreleased_line = None

    # ── Parse version headers ────────────────────────────────────────────────
    for i, line in enumerate(lines, start=1):
        m = VERSION_HEADER_RE.match(line)
        if not m:
            continue

        label = m.group(1).strip()
        date = m.group(2).strip() if m.group(2) else None

        if label.lower() == "unreleased":
            unreleased_count += 1
            unreleased_line = i
            continue

        parsed = parse_semver(label)
        if parsed is None:
            errors.append(
                f"Line {i}: [{label}] is not valid semver. "
                f"Expected MAJOR.MINOR.PATCH (e.g. 1.2.3 or 2.0.0-alpha.1)."
            )
            versions.append(
                {"version": label, "parsed": None, "date": date, "line_num": i}
            )
            continue

        if date is None:
            warnings.append(f'Line {i}: [{label}] has no date. Add " - YYYY-MM-DD".')
        elif not validate_date(date):
            errors.append(
                f'Line {i}: [{label}] has invalid date "{date}". Expected YYYY-MM-DD.'
            )

        versions.append(
            {"version": label, "parsed": parsed, "date": date, "line_num": i}
        )

    # ── [Unreleased] position ────────────────────────────────────────────────
    if unreleased_count > 1:
        errors.append(
            f"Found {unreleased_count} [Unreleased] sections — there should be at most one."
        )
    if unreleased_count == 1 and versions and unreleased_line > versions[0]["line_num"]:
        errors.append(
            f"[Unreleased] (line {unreleased_line}) must appear before the first "
            f"versioned entry [{versions[0]['version']}] (line {versions[0]['line_num']})."
        )

    # ── Duplicate versions ───────────────────────────────────────────────────
    seen: dict = {}
    for v in versions:
        ver = v["version"]
        if ver in seen:
            errors.append(
                f"Duplicate version [{ver}] on lines {seen[ver]} and {v['line_num']}."
            )
        else:
            seen[ver] = v["line_num"]

    # ── Descending order check ───────────────────────────────────────────────
    valid_versions = [v for v in versions if v["parsed"] is not None]
    for i in range(len(valid_versions) - 1):
        curr = valid_versions[i]
        nxt = valid_versions[i + 1]
        if semver_key(curr["parsed"]) < semver_key(nxt["parsed"]):
            errors.append(
                f"Version order error: [{curr['version']}] (line {curr['line_num']}) "
                f"should be newer than [{nxt['version']}] (line {nxt['line_num']}). "
                f"Changelog must be newest-first."
            )

    # ── Report ───────────────────────────────────────────────────────────────
    total = len(versions) + unreleased_count
    print(f"\nChangelog Semver Validator")
    print(f"    File   : {file_path.resolve()}")
    print(
        f"    Entries: {total} ({unreleased_count} unreleased, {len(versions)} versioned)\n"
    )

    if versions:
        print("    Versions found (newest -> oldest):")
        for v in versions:
            date_str = f"  {v['date']}" if v["date"] else "  (no date)"
            print(f"      {v['version']}{date_str}")
        print()

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"    - {w}")
        print()

    if errors:
        print("Errors:")
        for e in errors:
            print(f"    - {e}")
        print()
        print(f"    {len(errors)} error(s) found. Fix before releasing.")
        sys.exit(1)
    else:
        print("OK: All version entries are valid semver. Changelog looks good.")
        sys.exit(0)


if __name__ == "__main__":
    main()
