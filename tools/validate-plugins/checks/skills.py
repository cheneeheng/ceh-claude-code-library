"""skills: every skills/<name>/SKILL.md has name + description frontmatter, name == dir,
description <= 300 chars, optional compatibility <= 500 chars, and states
disable-model-invocation, user-invocable and license explicitly."""

from __future__ import annotations

import sys

from common import (
    check_name_and_description,
    fail,
    main,
    parse_frontmatter,
    plugin_dirs,
    rel,
)

# Stated on every skill even at their defaults, so the frontmatter says who invokes it.
EXPLICIT_SKILL_KEYS = ("disable-model-invocation", "user-invocable", "license")


def check() -> None:
    for d in plugin_dirs():
        for skill_dir in sorted((d / "skills").glob("*")):
            if not skill_dir.is_dir():
                continue
            sm = skill_dir / "SKILL.md"
            if not sm.exists():
                fail(rel(skill_dir), "skill directory has no SKILL.md")
                continue
            fm = parse_frontmatter(sm)
            if fm is None:
                fail(rel(sm), "missing YAML frontmatter block")
                continue
            check_name_and_description(sm, fm, skill_dir.name)
            for key in EXPLICIT_SKILL_KEYS:
                if key not in fm:
                    fail(rel(sm), f"frontmatter must state '{key}' explicitly")


if __name__ == "__main__":
    sys.exit(main(check))
