"""registry: every line of ceh-every-session's find-available-guide registry has eight non-empty
cells, a known kind and method, an https source, and a real past checked date, and no name and
install pair repeats.

Line format: name | aliases | kind | beats | method | install | source | checked
"""

from __future__ import annotations

import datetime
import sys

from common import REPO, fail, main, rel

REGISTRY = (
    REPO
    / "plugins/standalone/ceh-every-session/skills/find-available-guide/references/registry.txt"
)
REGISTRY_KINDS = {"skill", "plugin", "mcp"}
REGISTRY_METHODS = {"plugin", "mcp-add", "skill-copy"}


def check() -> None:
    if not REGISTRY.exists():
        if (REGISTRY.parent.parent / "SKILL.md").exists():
            fail(rel(REGISTRY), "registry is missing but find-available-guide exists")
        return
    today = datetime.datetime.now(datetime.timezone.utc).date()
    seen: set[tuple[str, str]] = set()
    for n, line in enumerate(REGISTRY.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        where = f"{rel(REGISTRY)}:{n}"
        cells = [c.strip() for c in line.split("|")]
        if len(cells) != 8 or not all(cells):
            fail(
                where,
                "needs 8 non-empty cells: name | aliases | kind | beats | method | install | source | checked",
            )
            continue
        name, _, kind, _, method, install, source, checked = cells
        if kind not in REGISTRY_KINDS:
            fail(where, f"kind '{kind}' is not one of {sorted(REGISTRY_KINDS)}")
        if method not in REGISTRY_METHODS:
            fail(where, f"method '{method}' is not one of {sorted(REGISTRY_METHODS)}")
        if not source.startswith("https://"):
            fail(where, f"source '{source}' must start with https://")
        try:
            if datetime.date.fromisoformat(checked) > today:
                fail(where, f"checked date {checked} is in the future")
        except ValueError:
            fail(where, f"checked '{checked}' is not a YYYY-MM-DD date")
        key = (name.lower(), install.lower())
        if key in seen:
            fail(where, f"name '{name}' with this install command is listed twice")
        seen.add(key)


if __name__ == "__main__":
    sys.exit(main(check))
