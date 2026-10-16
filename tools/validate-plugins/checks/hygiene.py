"""hygiene: no invisible Unicode and no personal absolute path in tracked text; every skill and
agent is named in backticks in its plugin README."""

from __future__ import annotations

import re
import sys

from common import REPO, fail, main, plugin_dirs, rel

INVISIBLE_PAT = re.compile("[\\u200b-\\u200f\\u202a-\\u202e\\u2060-\\u2064\\ufeff]")
USER_PATH_PAT = re.compile(r"[A-Za-z]:[\\/]Users[\\/]\w|/Users/\w|/home/\w")
HYGIENE_ROOTS = ("plugins", "docs", "tools", ".claude", ".github")
HYGIENE_SUFFIXES = {
    ".md",
    ".json",
    ".py",
    ".sh",
    ".ps1",
    ".yml",
    ".yaml",
    ".html",
    ".txt",
}


def check() -> None:
    files = list(REPO.glob("*.md"))
    for root in HYGIENE_ROOTS:
        files += [p for p in (REPO / root).rglob("*") if p.suffix in HYGIENE_SUFFIXES]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for n, line in enumerate(text.splitlines(), 1):
            if m := INVISIBLE_PAT.search(line):
                fail(f"{rel(path)}:{n}", f"invisible character U+{ord(m.group()):04X}")
            if m := USER_PATH_PAT.search(line):
                fail(f"{rel(path)}:{n}", f"personal absolute path '{m.group()}...'")

    for d in plugin_dirs():
        readme = d / "README.md"
        text = readme.read_text(encoding="utf-8") if readme.exists() else ""
        names = [p.name for p in (d / "skills").glob("*") if p.is_dir()]
        names += [p.stem for p in (d / "agents").glob("*.md")]
        for name in sorted(names):
            if f"`{name}`" not in text:
                fail(rel(readme), f"no row names component `{name}`")


if __name__ == "__main__":
    sys.exit(main(check))
