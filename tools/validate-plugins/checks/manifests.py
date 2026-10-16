"""manifests: plugin.json valid, name matches dir, semver version; marketplace.json lists every
plugin with a matching version and an existing source path."""

from __future__ import annotations

import sys

from common import (
    REPO,
    SEMVER,
    fail,
    load_json,
    main,
    plugin_dirs,
    plugin_versions,
    rel,
)


def check() -> None:
    for d in plugin_dirs():
        where = rel(d / ".claude-plugin/plugin.json")
        data = load_json(d / ".claude-plugin/plugin.json", where)
        if data is None:
            continue
        name = data.get("name")
        version = data.get("version")
        if not name:
            fail(where, "missing 'name'")
        elif name != d.name:
            fail(where, f"name '{name}' does not match directory '{d.name}'")
        if not version:
            fail(where, "missing 'version'")
        elif not SEMVER.match(str(version)):
            fail(where, f"version '{version}' is not semver X.Y.Z")

    versions = plugin_versions()
    mp_path = REPO / ".claude-plugin/marketplace.json"
    mp = load_json(mp_path, rel(mp_path))
    if mp is None:
        return
    listed = {}
    for entry in mp.get("plugins", []):
        ename = entry.get("name", "<unnamed>")
        listed[ename] = entry
        src = entry.get("source", "")
        if not (REPO / src).is_dir():
            fail(rel(mp_path), f"{ename}: source '{src}' does not exist")
        mv = str(entry.get("version", ""))
        pv = versions.get(ename)
        if pv is None:
            fail(rel(mp_path), f"{ename}: listed but has no plugin.json")
        elif mv != pv:
            fail(rel(mp_path), f"{ename}: version {mv} != plugin.json {pv}")
    for name in versions:
        if name not in listed:
            fail(rel(mp_path), f"{name}: plugin not listed in marketplace")


if __name__ == "__main__":
    sys.exit(main(check))
