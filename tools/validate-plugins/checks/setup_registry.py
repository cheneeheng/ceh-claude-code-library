"""setup-registry: tools/setup/setup.py's TOOLS and PLUGINS match the repo's plugins, skills,
dependencies and `compatibility` fields, so a plugin or skill cannot ship without its entry.

Reads the two dicts with ast.literal_eval, so nothing from setup.py is imported or run.
"""

from __future__ import annotations

import ast
import json
import re
import sys

from common import REPO, fail, main, parse_frontmatter, plugin_deps, plugin_dirs, rel

SETUP = REPO / "tools/setup/setup.py"
GROUPS = {"core", "shape", "build", "prove", "tell", "stack", "later"}
VERSION = re.compile(r"Claude Code v?(\d+\.\d+\.\d+)\+")


def load_registry() -> tuple[dict, dict]:
    tree = ast.parse(SETUP.read_text(encoding="utf-8"))
    found = {
        node.targets[0].id: ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in ("TOOLS", "PLUGINS")
    }
    return found.get("TOOLS", {}), found.get("PLUGINS", {})


def check() -> None:
    if not SETUP.exists():
        return
    where = rel(SETUP)
    tools, plugins = load_registry()
    market = json.loads(
        (REPO / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
    )
    listed = {p["name"] for p in market["plugins"]}
    for name in sorted(listed - plugins.keys()):
        fail(where, f"{name} is in marketplace.json but not in PLUGINS")
    for name in sorted(plugins.keys() - listed):
        fail(where, f"{name} is in PLUGINS but not in marketplace.json")

    for tool, spec in tools.items():
        for alt in spec.get("alternatives", []):
            if alt not in tools:
                fail(where, f"tool {tool}: alternative '{alt}' is not a TOOLS key")

    deps = plugin_deps()
    dirs = {d.name: d for d in plugin_dirs()}
    for name, spec in plugins.items():
        if name not in dirs:
            continue
        skill_dirs = sorted(p.parent.name for p in dirs[name].glob("skills/*/SKILL.md"))
        skills = spec.get("skills", [])
        if sorted(skills) != skill_dirs:
            fail(where, f"{name}: skills {sorted(skills)} differ from {skill_dirs}")
        if sorted(spec.get("dependencies", [])) != sorted(deps.get(name, [])):
            fail(where, f"{name}: dependencies differ from its plugin.json")
        if spec.get("group") not in GROUPS:
            fail(
                where,
                f"{name}: group '{spec.get('group')}' is not one of {sorted(GROUPS)}",
            )
        requires = spec.get("requires", [])
        degrades = spec.get("degrades", {})
        for tool in [*requires, *degrades]:
            if tool not in tools:
                fail(where, f"{name}: tool '{tool}' is not a TOOLS key")
        for tool, names in degrades.items():
            for skill in names:
                if skill != "hooks" and skill not in skills:
                    fail(
                        where, f"{name}: degrades {tool} names unknown skill '{skill}'"
                    )
        min_claude = {
            skill: version
            for version, names in spec.get("min_claude", {}).items()
            for skill in names
        }
        for skill in skill_dirs:
            fm = parse_frontmatter(dirs[name] / "skills" / skill / "SKILL.md") or {}
            text = fm.get("compatibility", "")
            matched = {
                tool
                for tool, t in tools.items()
                if any(re.search(w, text) for w in t.get("words", []))
            }
            for tool in sorted(matched):
                if tool in requires or skill in degrades.get(tool, []):
                    continue
                # "Bun (or Node.js 20+)": one entry under the primary tool covers both.
                if any(
                    tool in tools[p].get("alternatives", [])
                    and p in matched
                    and skill in degrades.get(p, [])
                    for p in tools
                ):
                    continue
                fail(
                    where,
                    f"{name}: {skill}'s compatibility names {tool}, which is neither in "
                    f"requires nor under degrades for that skill",
                )
            stated = VERSION.findall(text)
            if stated and stated != [min_claude.get(skill)]:
                fail(
                    where,
                    f"{name}: {skill}'s compatibility needs Claude Code {stated[0]}, "
                    f"min_claude says {min_claude.get(skill)}",
                )
            elif skill in min_claude and not stated:
                fail(
                    where,
                    f"{name}: min_claude lists {skill}, whose compatibility names no version",
                )


if __name__ == "__main__":
    sys.exit(main(check))
