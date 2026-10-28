"""repo-rules: rules CLAUDE.md states that a machine can check (docs/VISION.md, goal 5).

docs/PLUGIN_VERSIONS.md matches every plugin.json version; each plugin's newest CHANGELOG.md Plugin
versions row matches it too, under the section PLUGIN_VERSIONS.md dates it to; no marketplace entry
declares dependencies; a cross-cutting plugin (CLAUDE.md tier table) depends only on cross-cutting
plugins; a skill a hook script names sets user-invocable: false; every user-only skill is named in
ceh-every-session:whats-next.
"""

from __future__ import annotations

import re
import sys

from common import (
    REPO,
    fail,
    load_json,
    main,
    parse_frontmatter,
    plugin_deps,
    plugin_dirs,
    plugin_versions,
    rel,
)

COMPONENT_PAT = re.compile(r"\b(ceh-[a-z0-9-]+):([a-z0-9-]+)\b")
# Hook scripts that name a skill only to detect that it ran, so the skill may stay user-invocable.
NAMES_TO_DETECT = {
    # Allows a plan's Built Phase line once implement-from-plan started, by Skill call or slash
    # command; making it model-only would remove the slash command this guard accepts.
    "build-record-guard.py",
    # Allows a commit, changelog, README, test or new source write once a skill that owns it
    # started; the owning skills keep the slash commands this guard accepts.
    "skill-started-guard.py",
}


def check() -> None:
    versions = plugin_versions()

    # docs/PLUGIN_VERSIONS.md mirrors every plugin.json version.
    pv_path = REPO / "docs/PLUGIN_VERSIONS.md"
    rows = dict(
        re.findall(
            r"^\| `(ceh-[a-z0-9-]+)` +\| ([^ |]+)",
            pv_path.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    )
    for name, version in versions.items():
        if rows.get(name) != version:
            fail(
                rel(pv_path),
                f"{name}: row says {rows.get(name)}, plugin.json says {version}",
            )
    for name in rows.keys() - versions.keys():
        fail(rel(pv_path), f"{name}: row for a plugin that does not exist")

    # The newest CHANGELOG.md `### Plugin versions` row for a plugin shows its current version,
    # and docs/PLUGIN_VERSIONS.md dates it to that section. Catches a bump that missed the log.
    dates = dict(
        re.findall(
            r"^\| `(ceh-[a-z0-9-]+)` +\| [^ |]+ +\| `([\d-]+)`",
            pv_path.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
    )
    newest: dict[str, tuple[str, str]] = {}
    section, in_table = None, False
    for line in (REPO / "CHANGELOG.md").read_text(encoding="utf-8").splitlines():
        if m := re.match(r"^## (\d{4}-\d{2}-\d{2})", line):
            section, in_table = m.group(1), False
        elif line.startswith("### "):
            in_table = line == "### Plugin versions"
        elif in_table and (m := re.match(r"^\| `(ceh-[a-z0-9-]+)` +\| ([^ |]+)", line)):
            newest.setdefault(m.group(1), (m.group(2), section))
    for name, (version, section) in newest.items():
        if name in versions and version != versions[name]:
            fail(
                "CHANGELOG.md",
                f"{name}: newest row ({section}) says {version}, plugin.json says {versions[name]}",
            )
        if name in dates and dates[name] != section:
            fail(
                rel(pv_path),
                f"{name}: dated {dates[name]}, newest CHANGELOG.md row is under {section}",
            )

    # Dependencies live in plugin.json only, never in a marketplace entry.
    mp_path = REPO / ".claude-plugin/marketplace.json"
    for entry in (load_json(mp_path, rel(mp_path)) or {}).get("plugins", []):
        if "dependencies" in entry:
            fail(
                rel(mp_path),
                f"{entry.get('name')}: declare dependencies in plugin.json only",
            )

    # A cross-cutting plugin depends only on cross-cutting plugins. The tier list is the
    # **Cross-cutting** row of the CLAUDE.md tier table.
    row = re.search(
        r"^\| \*\*Cross-cutting\*\*.*$",
        (REPO / "CLAUDE.md").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if row is None:
        fail("CLAUDE.md", "tier table has no **Cross-cutting** row")
    else:
        cross = set(re.findall(r"`(ceh-[a-z0-9-]+)`", row.group(0)))
        for name, targets in plugin_deps().items():
            if name in cross:
                for t in targets:
                    if t not in cross:
                        fail(
                            f"plugins/standalone/{name}",
                            f"cross-cutting plugin depends on non-cross-cutting '{t}'",
                        )

    # A skill a hook names is model-only: `user-invocable: false`.
    for d in plugin_dirs():
        hooks = d / "hooks/hooks.json"
        if not hooks.exists():
            continue
        wired = re.findall(r"scripts/([\w.-]+)", hooks.read_text(encoding="utf-8"))
        for script in dict.fromkeys(wired):
            path = d / "scripts" / script
            if not path.exists():
                fail(rel(hooks), f"wires scripts/{script}, which does not exist")
                continue
            if script in NAMES_TO_DETECT:
                continue
            text = path.read_text(encoding="utf-8")
            for plugin, skill in dict.fromkeys(COMPONENT_PAT.findall(text)):
                sm = (
                    REPO / "plugins/standalone" / plugin / "skills" / skill / "SKILL.md"
                )
                fm = parse_frontmatter(sm) if sm.exists() else None
                if fm is not None and fm.get("user-invocable", "").lower() != "false":
                    fail(
                        rel(sm),
                        f"named by hook script {script}, so set 'user-invocable: false'",
                    )

    # A user-only skill never reaches the session's skill listing, so whats-next names each one.
    advisor = REPO / "plugins/standalone/ceh-every-session/skills/whats-next/SKILL.md"
    named = advisor.read_text(encoding="utf-8") if advisor.exists() else ""
    for d in plugin_dirs():
        for sm in sorted(d.glob("skills/*/SKILL.md")):
            fm = parse_frontmatter(sm) or {}
            ref = f"{d.name}:{sm.parent.name}"
            if (
                fm.get("disable-model-invocation", "").lower() == "true"
                and f"`{ref}`" not in named
            ):
                fail(rel(advisor), f"user-only skill '{ref}' missing from its table")


if __name__ == "__main__":
    sys.exit(main(check))
