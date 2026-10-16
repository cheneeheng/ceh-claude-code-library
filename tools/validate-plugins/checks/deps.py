"""deps: every `dependencies` entry names a plugin in this repo and the graph is acyclic."""

from __future__ import annotations

import sys

from common import fail, main, plugin_deps, plugin_dirs, rel


def check() -> None:
    deps = plugin_deps()
    dirs = {d.name: d for d in plugin_dirs()}
    for name, targets in deps.items():
        where = rel(dirs[name] / ".claude-plugin/plugin.json")
        for t in targets:
            if t not in deps:
                fail(where, f"dependency '{t}' is not a plugin in this repo")

    # acyclicity (DFS with a colour map, so the cycle path is reportable)
    colour: dict[str, int] = {}

    def visit(node: str, path: list[str]) -> None:
        colour[node] = 1
        for t in deps.get(node, []):
            if colour.get(t) == 1:
                fail("dependency graph", "cycle: " + " -> ".join(path + [node, t]))
            elif colour.get(t, 0) == 0:
                visit(t, path + [node])
        colour[node] = 2

    for name in deps:
        if colour.get(name, 0) == 0:
            visit(name, [])


if __name__ == "__main__":
    sys.exit(main(check))
