"""copies: every whole-file copy `docs/CROSS_REFERENCES.md` registers is byte-identical to its
canonical file, and no two skills hold an identical file at the same path without registering it.

A row is byte-checked when its Section reads `whole file` and its Diverges reads `none`. It holds
one full path and pairs with the canonical file of the same name on its entry's Canonical line.
The check fails a copy that differs (drift), a path that does not exist (stale), a row or
Canonical line it cannot pair (malformed), and two identical files at the same path inside their
skill folders that no registered pair links (unregistered). Files that only share a name pass.

It also guards the layout that makes a skill folder work on its own: a plugin root holds no
`assets/` or `references/`, no skill or agent cites `${CLAUDE_PLUGIN_ROOT}/assets/` or
`${CLAUDE_PLUGIN_ROOT}/references/`, and a skill's reference file names neither
`${CLAUDE_PLUGIN_ROOT}` nor `<plugin root>`, because a copied file can only point inside its skill."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from common import REPO, agent_files, fail, main, plugin_dirs, rel, skill_files

REGISTRY = REPO / "docs" / "CROSS_REFERENCES.md"
WHERE = "docs/CROSS_REFERENCES.md"
BUNDLED = ("assets", "references", "scripts")
PLUGIN_BUNDLE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/(?:assets|references)/")
PLUGIN_ROOT = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}|<plugin root>")
PATH = re.compile(r"`((?:plugins|\.claude)/[^`]+)`")
WHOLE = re.compile(r"^(?:the )?(?:whole|entire) (?:file|files|script)$")
NOT_ENTRIES = {"Update protocol"}


def _entries() -> list[tuple[str, list[str], list[list[str]]]]:
    """(heading, Canonical paragraph lines, table rows as cells) per entry, fenced lines skipped."""
    entries: list[tuple[str, list[str], list[list[str]]]] = []
    fenced = in_canonical = False
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            entries.append((heading, [], []))
            in_canonical = False
            continue
        if not entries or entries[-1][0] in NOT_ENTRIES:
            continue
        canonical, rows = entries[-1][1], entries[-1][2]
        if line.startswith("**Canonical:**"):
            in_canonical = True
        elif not line.strip():
            in_canonical = False
        if in_canonical:
            canonical.append(line)
        elif line.startswith("|"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
            rows.append(cells)
    return entries


def registered_pairs() -> list[tuple[str, Path, Path]]:
    """(entry, canonical, copy) for every byte-checked row; malformed rows fail and are dropped."""
    pairs = []
    for heading, canonical, rows in _entries():
        names = defaultdict(list)
        for path in PATH.findall(" ".join(canonical)):
            names[Path(path).name].append(path)
        for cells in rows:
            if len(cells) < 3 or not WHOLE.match(cells[1]) or cells[2] != "none":
                continue
            row = "| " + " | ".join(cells) + " |"
            paths = PATH.findall(cells[0])
            if len(paths) != 1 or cells[0].count("`") != 2:
                fail(
                    WHERE,
                    f"{heading}: {row}: a whole-file row holds exactly one full path",
                )
                continue
            match = names.get(Path(paths[0]).name, [])
            if len(match) != 1:
                why = "no" if not match else "more than one"
                fail(WHERE, f"{heading}: {row}: {why} canonical file of that name")
                continue
            pairs.append((heading, REPO / match[0], REPO / paths[0]))
    return pairs


def _layout() -> None:
    for d in plugin_dirs():
        for sub in ("assets", "references"):
            if (d / sub).is_dir():
                fail(rel(d / sub), "bundled files live in the skill that uses them")
        for ref in sorted(d.glob("skills/*/references/**/*.md")):
            if PLUGIN_ROOT.search(ref.read_text(encoding="utf-8")):
                fail(rel(ref), "a skill's reference file points only inside its skill")
    for doc in skill_files() + agent_files():
        if PLUGIN_BUNDLE.search(doc.read_text(encoding="utf-8")):
            fail(
                rel(doc),
                "cite bundled files from the skill folder, not the plugin root",
            )


def check() -> None:
    _layout()

    # Each registered pair links two files; files linked directly or through a shared canonical
    # file are one registered set.
    root: dict[Path, Path] = {}

    def find(p: Path) -> Path:
        while root.setdefault(p, p) != p:
            p = root[p]
        return p

    for heading, canonical, copy in registered_pairs():
        missing = [p for p in (canonical, copy) if not p.is_file()]
        for p in missing:
            fail(WHERE, f"{heading}: {rel(p)} does not exist")
        if missing:
            continue
        root[find(copy.resolve())] = find(canonical.resolve())
        if copy.read_bytes() != canonical.read_bytes():
            fail(rel(copy), f"differs from {rel(canonical)} ({heading})")

    groups: dict[str, list[Path]] = defaultdict(list)
    for d in plugin_dirs():
        for skill in sorted(p for p in (d / "skills").glob("*") if p.is_dir()):
            for sub in BUNDLED:
                for f in sorted((skill / sub).rglob("*")):
                    if f.is_file() and "__pycache__" not in f.parts:
                        groups[f.relative_to(skill).as_posix()].append(f)
    for paths in groups.values():
        for i, a in enumerate(paths):
            for b in paths[i + 1 :]:
                same_set = find(a.resolve()) == find(b.resolve())
                if not same_set and a.read_bytes() == b.read_bytes():
                    fail(
                        rel(b),
                        f"identical to {rel(a)}; register the copy in {WHERE}",
                    )


if __name__ == "__main__":
    sys.exit(main(check))
