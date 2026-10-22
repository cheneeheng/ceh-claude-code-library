"""templates: every output template declares its versioned schema, is cited by its plugin, has a
cited schema file beside it, and matches its copies in other plugins; a skill whose Output section
names a saved file cites a template."""

from __future__ import annotations

import re
import sys
from collections import defaultdict

from common import fail, main, plugin_dirs, rel, skill_files

# `schema: <name>/v<N>` is the template's first frontmatter key.
SCHEMA_PAT = re.compile(r"^schema: ([a-z0-9]+(?:-[a-z0-9]+)*)/v([1-9]\d*)$")
SUFFIX = ".template.md"
# The schema explaining a template: references/<name>-schema.md, a sibling of its assets/ folder.
SCHEMA_SUFFIX = "-schema.md"
# A template holds placeholders, not explanation: a placeholder that is not a `a | b` choice stays
# short, and frontmatter carries no `# comment`. The explanation lives in the schema.
LONG_PLACEHOLDER_PAT = re.compile(r"<[^<>|]{31,}>")
YAML_COMMENT_PAT = re.compile(r"^[a-z_]+: .* #", re.M)
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
            body = t.read_text(encoding="utf-8")
            for bad in LONG_PLACEHOLDER_PAT.findall(body) + YAML_COMMENT_PAT.findall(
                body
            ):
                fail(where, f"explanation '{bad}' belongs in its schema file")
            if "<!--" in body:
                fail(where, "comments belong in its schema file")
            m = SCHEMA_PAT.match(schema_line(body))
            if not m:
                fail(where, f"must open with 'schema: {stem}/v<N>'")
            elif m.group(1) != stem:
                fail(where, f"schema name '{m.group(1)}' != file name '{stem}'")
            if t.parent.name != "assets":
                fail(where, "templates live in an assets/ folder")
            if t.name not in cited:
                fail(where, "no skill, agent, or reference file in its plugin cites it")
            by_name[t.name].append(t)
            schema = t.parent.parent / "references" / (stem + SCHEMA_SUFFIX)
            if not schema.is_file():
                fail(where, f"no schema file {rel(schema)}")
                continue
            if t.name not in schema.read_text(encoding="utf-8"):
                fail(rel(schema), f"does not name its template {t.name}")
            if schema.name not in cited.replace(schema.read_text(encoding="utf-8"), ""):
                fail(
                    rel(schema),
                    "no skill, agent, or other reference file in its plugin cites it",
                )
            by_name[schema.name].append(schema)

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
