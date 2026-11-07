"""copies: a file under a skill's `assets/`, `references/` or `scripts/` is byte-identical to every
file at the same path inside another skill folder, in any plugin. A plugin root's artifact scripts
join the `scripts/<name>` group, so the render hook's `artifact.py` matches the skills' copies.

It also guards the layout that makes a skill folder work on its own: a plugin root holds no
`assets/` or `references/`, no skill or agent cites `${CLAUDE_PLUGIN_ROOT}/assets/` or
`${CLAUDE_PLUGIN_ROOT}/references/`, and a skill's reference file names neither
`${CLAUDE_PLUGIN_ROOT}` nor `<plugin root>`, because a copied file can only point inside its skill."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from artifact_models import SHARED_SCRIPTS
from common import agent_files, fail, main, plugin_dirs, rel, skill_files

BUNDLED = ("assets", "references", "scripts")
PLUGIN_BUNDLE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/(?:assets|references)/")
PLUGIN_ROOT = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}|<plugin root>")


def _files(owner: Path) -> list[tuple[str, Path]]:
    return [
        (f.relative_to(owner).as_posix(), f)
        for sub in BUNDLED
        for f in sorted((owner / sub).rglob("*"))
        if f.is_file() and "__pycache__" not in f.parts
    ]


def check() -> None:
    groups: dict[str, list[Path]] = defaultdict(list)
    for d in plugin_dirs():
        for sub in ("assets", "references"):
            if (d / sub).is_dir():
                fail(rel(d / sub), "bundled files live in the skill that uses them")
        found = [(f"scripts/{s}", d / "scripts" / s) for s in SHARED_SCRIPTS]
        for skill in sorted(p for p in (d / "skills").glob("*") if p.is_dir()):
            found += _files(skill)
        for key, path in found:
            if path.is_file():
                groups[key].append(path)
        for ref in sorted(d.glob("skills/*/references/**/*.md")):
            if PLUGIN_ROOT.search(ref.read_text(encoding="utf-8")):
                fail(rel(ref), "a skill's reference file points only inside its skill")

    for doc in skill_files() + agent_files():
        if PLUGIN_BUNDLE.search(doc.read_text(encoding="utf-8")):
            fail(
                rel(doc),
                "cite bundled files from the skill folder, not the plugin root",
            )

    for paths in groups.values():
        first = paths[0].read_bytes()
        for other in paths[1:]:
            if other.read_bytes() != first:
                every = ", ".join(rel(p) for p in paths)
                fail(
                    rel(other),
                    f"differs from its copy {rel(paths[0])}; copies: {every}",
                )


if __name__ == "__main__":
    sys.exit(main(check))
