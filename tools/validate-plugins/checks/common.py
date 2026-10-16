"""Helpers shared by every check: repo paths, the error collector, frontmatter and manifest readers.

Each check module defines `check()`, which records problems with `fail(where, msg)`. `validate.py`
runs them all. A check also runs alone: `python tools/validate-plugins/checks/<name>.py`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[3]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Claude Code allows 1024. The repo budget is lower because every description is paid for in
# context on every session that installs the plugin (docs/VISION.md, goal 4), and the skill
# listing drops whole descriptions once it overflows its budget of 1% of the context window.
MAX_DESCRIPTION_LEN = 300
MAX_COMPATIBILITY_LEN = 500

errors: list[str] = []


def fail(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(p)


def run_check(check: Callable[[], None]) -> list[str]:
    """Run one check on a clean collector and return the problems it recorded."""
    errors.clear()
    check()
    return list(errors)


def report(results: dict[str, list[str]]) -> int:
    """Print the problems grouped by check name. Return the process exit code."""
    total = sum(len(found) for found in results.values())
    if not total:
        names = (
            "all plugin checks" if len(results) > 1 else f"{next(iter(results))} check"
        )
        print(f"OK: {names} passed")
        return 0
    print(f"FAIL: {total} problem(s) found")
    for name, found in results.items():
        if found:
            print(f"\n[{name}]")
            for e in found:
                print(f"  - {e}")
    return 1


def main(check: Callable[[], None]) -> int:
    """Entry point for running one check module on its own."""
    return report({Path(sys.argv[0]).stem.replace("_", "-"): run_check(check)})


def plugin_dirs() -> list[Path]:
    return sorted(p for p in REPO.glob("plugins/*/ceh-*") if p.is_dir())


def skill_files() -> list[Path]:
    return [p for d in plugin_dirs() for p in sorted((d / "skills").glob("*/SKILL.md"))]


def agent_files() -> list[Path]:
    return [p for d in plugin_dirs() for p in sorted((d / "agents").glob("*.md"))]


def doc_files() -> list[Path]:
    """Every skill and agent file."""
    return skill_files() + agent_files()


def output_style_files() -> list[Path]:
    return sorted(p for d in plugin_dirs() for p in (d / "output-styles").glob("*.md"))


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    """Return top-level scalar keys from the leading `---` YAML block.

    Minimal parser: enough to read `name`/`description` (inline or block scalar).
    Returns None if the file has no frontmatter block.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None
    keys: dict[str, str] = {}
    current: str | None = None
    block = False
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", line)
        if m and not line.startswith((" ", "\t")):
            current = m.group(1)
            value = m.group(2).strip()
            block = value in (">", "|", ">-", "|-", ">+", "|+")
            keys[current] = "" if block else value.strip("'\"")
        elif current and block and line.strip():
            keys[current] = (keys[current] + " " + line.strip()).strip()
    return keys


def check_name_and_description(
    path: Path, fm: dict[str, str], expected_name: str
) -> None:
    """The frontmatter rules a skill and an agent share: name, description, compatibility."""
    where = rel(path)
    name = fm.get("name")
    if not name:
        fail(where, "frontmatter missing 'name'")
    elif name != expected_name:
        fail(
            where, f"frontmatter name '{name}' != file/directory name '{expected_name}'"
        )
    desc = fm.get("description")
    if not desc:
        fail(where, "frontmatter missing 'description'")
    elif len(desc) > MAX_DESCRIPTION_LEN:
        fail(
            where,
            f"description is {len(desc)} chars, exceeds {MAX_DESCRIPTION_LEN} limit",
        )
    compat = fm.get("compatibility")
    if compat and len(compat) > MAX_COMPATIBILITY_LEN:
        fail(
            where,
            f"compatibility is {len(compat)} chars, exceeds {MAX_COMPATIBILITY_LEN} limit",
        )


def load_json(path: Path, where: str) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(where, "file not found")
    except json.JSONDecodeError as e:
        fail(where, f"invalid JSON: {e}")
    return None


def plugin_versions() -> dict[str, str]:
    """{plugin name: version} from every readable plugin.json. Silent: `manifests` reports faults."""
    out: dict[str, str] = {}
    for d in plugin_dirs():
        try:
            data = json.loads((d / ".claude-plugin/plugin.json").read_text("utf-8"))
        except (OSError, ValueError):
            continue
        if data.get("name") and data.get("version"):
            out[data["name"]] = str(data["version"])
    return out


def plugin_deps() -> dict[str, list[str]]:
    """{plugin: [dependency names]}. Accepts bare strings or {"name": ...} objects."""
    out: dict[str, list[str]] = {}
    for d in plugin_dirs():
        data = load_json(d / ".claude-plugin/plugin.json", rel(d)) or {}
        names = []
        for dep in data.get("dependencies", []):
            names.append(dep["name"] if isinstance(dep, dict) else dep)
        out[d.name] = names
    return out


def known_components() -> set[str]:
    comps: set[str] = set()
    for d in plugin_dirs():
        for skill_dir in (d / "skills").glob("*"):
            if (skill_dir / "SKILL.md").exists():
                comps.add(f"{d.name}:{skill_dir.name}")
        for agent in (d / "agents").glob("*.md"):
            comps.add(f"{d.name}:{agent.stem}")
            fm = parse_frontmatter(agent)
            if fm and fm.get("name"):
                comps.add(f"{d.name}:{fm['name']}")
    return comps
