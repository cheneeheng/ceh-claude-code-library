"""scalars: `description` uses the folded block scalar `>-`; no other frontmatter key is a plain
scalar containing ': ' (which strict YAML rejects).

`description` must be a folded block scalar (`>-`). It is the only style with no escaping burden:
':', '"', "'", '\\' and '#' are all literal inside it, so no description can break the block, and
'-' strips the trailing newline. Every other style needs escaping that has silently broken files
here before.

Any other key must not be a plain scalar containing ': ' - a strict YAML parser reads that as a
nested mapping and rejects the block. Quote those values.
"""

from __future__ import annotations

import re
import sys

from common import doc_files, fail, main, rel


def check() -> None:
    for path in doc_files():
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        lines = text.splitlines()
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        for line in lines[1 : end or 1]:
            m = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", line)
            if not m:
                continue
            key, value = m.group(1), m.group(2).strip()
            if key == "description":
                if value != ">-":
                    fail(
                        rel(path),
                        "'description' must use the folded block scalar '>-' "
                        f"(found {value[:12]!r}...) - see .claude/rules/decision-frontmatter-scalars.md",
                    )
            elif value and not value.startswith(("'", '"', ">", "|")) and ": " in value:
                fail(
                    rel(path),
                    f"'{key}' is an unquoted scalar containing ': ' - quote it",
                )


if __name__ == "__main__":
    sys.exit(main(check))
