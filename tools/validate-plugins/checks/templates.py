"""templates: every output template declares its versioned schema, is cited by its plugin, and
matches its copies in other plugins; a skill whose Output section names a saved file cites a
template."""

from __future__ import annotations

import re
import sys
from collections import defaultdict

from common import fail, main, plugin_dirs, rel, skill_files

# `schema: <name>/v<N>` is the template's first frontmatter key.
SCHEMA_PAT = re.compile(r"^schema: ([a-z0-9]+(?:-[a-z0-9]+)*)/v([1-9]\d*)$")
SUFFIX = ".template.md"
# A saved file in an Output section: a path under .agents_workspace/ or product/ with an extension.
SAVED_FILE_PAT = re.compile(
    r"(?:\.agents_workspace|product)/[^`\s]*\.(?:md|ya?ml|json)"
)


def schema_line(text: str) -> str:
    lines = text.splitlines()
    return lines[1] if len(lines) > 1 and lines[0] == "---" else ""


def output_section(text: str) -> str:
    m = re.search(r"^## Output\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def check() -> None:
    by_name = defaultdict(list)
    for d in plugin_dirs():
        templates = sorted(d.rglob("*" + SUFFIX))
        cited = "\n".join(
            p.read_text(encoding="utf-8")
            for p in d.rglob("*.md")
            if not p.name.endswith(SUFFIX)
        )
        for t in templates:
            where = rel(t)
            stem = t.name[: -len(SUFFIX)]
            m = SCHEMA_PAT.match(schema_line(t.read_text(encoding="utf-8")))
            if not m:
                fail(where, f"must open with 'schema: {stem}/v<N>'")
            elif m.group(1) != stem:
                fail(where, f"schema name '{m.group(1)}' != file name '{stem}'")
            if t.parent.name != "references":
                fail(where, "templates live in a references/ folder")
            if t.name not in cited:
                fail(where, "no skill, agent, or reference file in its plugin cites it")
            by_name[t.name].append(t)

    for name, copies in by_name.items():
        first = copies[0].read_bytes()
        for other in copies[1:]:
            if other.read_bytes() != first:
                fail(rel(other), f"differs from its copy {rel(copies[0])}")

    for skill in skill_files():
        text = skill.read_text(encoding="utf-8")
        saved = SAVED_FILE_PAT.search(output_section(text))
        if saved and SUFFIX not in text:
            fail(rel(skill), f"Output names '{saved.group()}' but cites no template")


if __name__ == "__main__":
    sys.exit(main(check))
