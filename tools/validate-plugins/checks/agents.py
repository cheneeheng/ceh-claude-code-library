"""agents: every agents/<name>.md has name + description + model frontmatter, name == file stem,
description <= 300 chars."""

from __future__ import annotations

import sys

from common import (
    agent_files,
    check_name_and_description,
    fail,
    main,
    parse_frontmatter,
    rel,
)


def check() -> None:
    for agent in agent_files():
        fm = parse_frontmatter(agent)
        if fm is None:
            fail(rel(agent), "missing YAML frontmatter block")
            continue
        check_name_and_description(agent, fm, agent.stem)
        if not fm.get("model"):
            fail(rel(agent), "frontmatter missing 'model' - set it, even as 'inherit'")


if __name__ == "__main__":
    sys.exit(main(check))
