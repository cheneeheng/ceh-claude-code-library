"""retired-names: no file outside the records names a plugin that was archived or renamed."""

from __future__ import annotations

from pathlib import Path
import re
import sys

from common import REPO, fail, main, plugin_dirs, rel
from hygiene import HYGIENE_SUFFIXES, committable_files

# Old plugin name -> the plugin that replaced it. A merge adds its old names in its own PR.
RENAMED: dict[str, str] = {
    "ceh-session-diagnosis": "ceh-session-learning",
    "ceh-session-to-skill": "ceh-session-learning",
    "ceh-blog": "ceh-blog-and-seo",
    "ceh-seo": "ceh-blog-and-seo",
    "ceh-build-planning": "ceh-build-plan",
    "ceh-build-from-plan": "ceh-build-plan",
}
# Retired name -> repo-relative files that may still name it, because they state history.
ALLOWED: dict[str, set[str]] = {
    "ceh-evaluation": {
        ".claude/rules/decision-evaluation.md",
        ".claude/skills/evaluate-plugin/SKILL.md",
    },
    "ceh-ops": {"docs/CROSS_REFERENCES.md"},
    "ceh-scaffolding": {"docs/CROSS_REFERENCES.md"},
    "ceh-plan-build-review": {"docs/IDEAS.md"},
}
# product/, audits/, archive/ and CHANGELOG.md are records of what was true when written.
ROOTS = ("plugins", "docs", "tools", ".claude", ".github", "examples")
MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
TOKEN_PAT = re.compile(r"\bceh-[a-z0-9]+(?:-[a-z0-9]+)*")


def check() -> None:
    live = {d.name for d in plugin_dirs()}
    retired = {
        p.name: "archived"
        for p in (REPO / "archive").glob("ceh-*")
        if p.is_dir() and p.name not in live
    } | {old: f"replaced by {new}" for old, new in RENAMED.items()}
    for path in committable_files():
        if not path.is_file() or path == Path(__file__).resolve():
            continue
        if path != MARKETPLACE and (
            path.suffix not in HYGIENE_SUFFIXES
            or path.name == "CHANGELOG.md"
            or (
                path.relative_to(REPO).parts[0] not in ROOTS
                and not (path.parent == REPO and path.suffix == ".md")
            )
        ):
            continue
        where = rel(path)
        lines = path.read_text(encoding="utf-8").splitlines()
        for n, line in enumerate(lines, 1):
            for name in dict.fromkeys(TOKEN_PAT.findall(line)):
                if name in retired and where not in ALLOWED.get(name, ()):
                    fail(
                        f"{where}:{n}",
                        f"retired plugin name '{name}' ({retired[name]})",
                    )


if __name__ == "__main__":
    sys.exit(main(check))
