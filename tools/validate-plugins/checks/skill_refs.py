"""skill-refs: `plugin:component` references in skills, agents, and output styles resolve to a real
skill or agent."""

from __future__ import annotations

import re
import sys

from common import (
    doc_files,
    fail,
    known_components,
    main,
    output_style_files,
    plugin_dirs,
    rel,
)


def check() -> None:
    comps = known_components()
    plugins = {d.name for d in plugin_dirs()}
    ref_pat = re.compile(r"\bceh-[a-z0-9-]+:[a-z0-9-]+\b")
    for doc in doc_files() + output_style_files():
        where = rel(doc)
        text = doc.read_text(encoding="utf-8")
        for ref in dict.fromkeys(ref_pat.findall(text)):
            plugin = ref.split(":", 1)[0]
            if plugin in plugins and ref not in comps:
                fail(where, f"skill reference '{ref}' does not resolve")


if __name__ == "__main__":
    sys.exit(main(check))
