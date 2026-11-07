"""copies: a file under a skill's `assets/`, `references/` or `scripts/` is byte-identical to every
file at the same path inside another skill folder, in any plugin. A plugin root's `assets/` and
`references/` count as a folder of their own, and its artifact scripts join the `scripts/<name>`
group, so the render hook's `artifact.py` matches the skills' copies."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from artifact_models import SHARED_SCRIPTS
from common import fail, main, plugin_dirs, rel

BUNDLED = ("assets", "references", "scripts")


def _files(owner: Path, subs: tuple[str, ...]) -> list[tuple[str, Path]]:
    return [
        (f.relative_to(owner).as_posix(), f)
        for sub in subs
        for f in sorted((owner / sub).rglob("*"))
        if f.is_file() and "__pycache__" not in f.parts
    ]


def check() -> None:
    groups: dict[str, list[Path]] = defaultdict(list)
    for d in plugin_dirs():
        found = _files(d, ("assets", "references"))
        found += [(f"scripts/{s}", d / "scripts" / s) for s in SHARED_SCRIPTS]
        for skill in sorted(p for p in (d / "skills").glob("*") if p.is_dir()):
            found += _files(skill, BUNDLED)
        for key, path in found:
            if path.is_file():
                groups[key].append(path)

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
