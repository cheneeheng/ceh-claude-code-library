#!/usr/bin/env bash
set -euo pipefail
mkdir -p product/plans
cat >product/plans/slug.md <<'EOF'
---
schema: plan/v1
title: Slug helper
status: building
created: 2026-10-20
---

## Goal

A `slugify` function that turns a post title into a URL slug, for the blog's link builder.

## Scope

**In:**

- `slugify(text)` lowercases, replaces each run of characters other than a-z and 0-9 with one hyphen, and trims hyphens from both ends.
- `slugify(text, max_len)` cuts the slug to at most `max_len` characters without ending on a hyphen.
- `slugify(text, max_len, sep)` joins words with `sep` instead of a hyphen.

**Out:**

- Unicode transliteration: titles are ASCII today.
- A command-line interface: only the link builder calls it.

## Design

- Python 3 standard library only: one module `slug.py`, tests in `test_slug.py` with `unittest`.
- Interface: `slugify(text: str, max_len: int | None = None, sep: str = "-") -> str`.

## Phases

### Phase 1: Basic slug

- **Builds:** `slugify(text)` per Scope bullet 1.
- **Check:** `python -m unittest test_slug` passes.
- **Status:** done: `python -m unittest test_slug`, OK (1 test)

### Phase 2: Length limit

- **Builds:** the `max_len` argument per Scope bullet 2.
- **Check:** `python -m unittest test_slug` passes.
- **Status:** todo

### Phase 3: Separator

- **Builds:** the `sep` argument per Scope bullet 3.
- **Check:** `python -m unittest test_slug` passes.
- **Status:** todo

## Open

None

## Record

- 2026-10-20 Planned: status ready
- 2026-10-21 Built Phase 1: `python -m unittest test_slug`, OK (1 test)
EOF
cat >slug.py <<'EOF'
import re


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
EOF
cat >test_slug.py <<'EOF'
import unittest

from slug import slugify


class SlugTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("  Hello, World! "), "hello-world")


if __name__ == "__main__":
    unittest.main()
EOF
git init -q -b main
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -qm 'chore: seed'
