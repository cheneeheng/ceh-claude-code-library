"""invocations: every `Invoke the Skill tool with skill="X"` resolves, is in-plugin or in a declared
dependency, and does not set `disable-model-invocation: true`."""

from __future__ import annotations

import re
import sys

from common import (
    REPO,
    doc_files,
    fail,
    known_components,
    main,
    parse_frontmatter,
    plugin_deps,
    plugin_dirs,
    rel,
)

INVOKE_PAT = re.compile(r'Invoke the Skill tool with skill="([^"]+)"')


def check() -> None:
    comps = known_components()
    deps = plugin_deps()
    skill_fm: dict[str, dict[str, str]] = {}
    for d in plugin_dirs():
        for skill_dir in (d / "skills").glob("*"):
            if (skill_dir / "SKILL.md").exists():
                skill_fm[f"{d.name}:{skill_dir.name}"] = (
                    parse_frontmatter(skill_dir / "SKILL.md") or {}
                )

    def reachable(root: str) -> set[str]:
        seen, stack = {root}, [root]
        while stack:
            for t in deps.get(stack.pop(), []):
                if t not in seen:
                    seen.add(t)
                    stack.append(t)
        return seen

    for doc in doc_files():
        where = rel(doc)
        source = doc.relative_to(REPO / "plugins").parts[1]
        allowed = reachable(source)
        for ref in dict.fromkeys(INVOKE_PAT.findall(doc.read_text(encoding="utf-8"))):
            if ref not in comps:
                fail(where, f"invocation target '{ref}' does not resolve")
                continue
            target = ref.split(":", 1)[0]
            if target not in allowed:
                fail(
                    where,
                    f"invokes '{ref}' but '{source}' does not depend on '{target}'",
                )
            if (
                str(skill_fm.get(ref, {}).get("disable-model-invocation", "")).lower()
                == "true"
            ):
                fail(
                    where, f"invokes '{ref}', which sets disable-model-invocation: true"
                )


if __name__ == "__main__":
    sys.exit(main(check))
