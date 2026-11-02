"""hygiene: no invisible Unicode and no personal absolute path in tracked text; every skill and
agent is named in backticks in its plugin README."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

from common import REPO, fail, main, plugin_dirs, rel

INVISIBLE_PAT = re.compile("[\\u200b-\\u200f\\u202a-\\u202e\\u2060-\\u2064\\ufeff]")
USER_PATH_PAT = re.compile(
    r"[A-Za-z]:[\\/]Users[\\/]\w|/Users/\w|/home/\w|[A-Za-z]--Users-\w"
)
HYGIENE_ROOTS = (
    "plugins",
    "docs",
    "tools",
    ".claude",
    ".github",
    "product",
    "audits",
    "examples",
)
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


def committable_files() -> list[Path]:
    """Tracked files plus new ones git would accept, so git-ignored output never fails the gate."""
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=REPO,
        check=True,
    ).stdout
    return [REPO / name for name in listed.split("\0") if name]


def check() -> None:
    files = [
        p
        for p in committable_files()
        if p.is_file()
        and p.suffix in HYGIENE_SUFFIXES
        and (
            p.parent == REPO
            and p.suffix == ".md"
            or p.relative_to(REPO).parts[0] in HYGIENE_ROOTS
        )
    ]
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
