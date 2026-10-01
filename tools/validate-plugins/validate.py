#!/usr/bin/env python3
"""Validate the ceh-* plugin repo: manifests, skills, agents, references, scripts.

Stdlib-only so it runs locally (Windows/macOS/Linux) and in CI without installs.
Run from the repo root: `python tools/validate-plugins/validate.py`.
Exits non-zero if any check fails.

Checks:
  manifests  - plugin.json valid, name matches dir, semver version; marketplace.json
               lists every plugin with a matching version and an existing source path.
  skills     - every skills/<name>/SKILL.md has name + description frontmatter, name == dir,
               description <= 1024 chars, optional compatibility <= 500 chars.
  agents     - every agents/<name>.md has name + description + model frontmatter, name == file
               stem, description <= 1024 chars.
  keys       - skill/agent names are lowercase-hyphenated (<= 64 chars); every frontmatter key is
               one Claude Code documents; no plugin-agent key Claude Code ignores; no
               TEMPLATE-GUIDANCE comment left over from a template.
  scalars    - `description` uses the folded block scalar `>-`; no other frontmatter key is a
               plain scalar containing ': ' (which strict YAML rejects).
  references - `references/...`, `${CLAUDE_PLUGIN_ROOT}/{scripts,references}/...` and `${CLAUDE_SKILL_DIR}/...`
               mentions in SKILL.md/agent files resolve to a real file.
  skill-refs - `plugin:component` references resolve to a real skill or agent.
  deps       - every `dependencies` entry names a plugin in this repo, the graph is acyclic,
               a ceh-scenario-* directory holds only plugin.json + README.md, and only a
               bundle depends on a bundle.
  invocations- every `Invoke the Skill tool with skill="X"` resolves, is in-plugin or in a
               declared dependency, and does not set `disable-model-invocation: true`.
  scripts    - *.sh pass `bash -n` (+ shellcheck if available); *.py pass py_compile.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_COMPATIBILITY_LEN = 500
TEMPLATE_MARKER = "TEMPLATE-GUIDANCE"

# Claude Code silently ignores unknown frontmatter keys, so a typo reads as working config.
# Sources: https://code.claude.com/docs/en/skills#frontmatter-reference
#          https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields
SKILL_KEYS = {
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "arguments",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "disallowed-tools",
    "model",
    "effort",
    "context",
    "agent",
    "background",
    "hooks",
    "paths",
    "shell",
    "metadata",
    "license",
    "compatibility",
}
AGENT_KEYS = {
    "name",
    "description",
    "tools",
    "disallowedTools",
    "model",
    "maxTurns",
    "skills",
    "memory",
    "background",
    "omitClaudeMd",
    "effort",
    "isolation",
    "color",
    "experimental",
}
# Valid on project agents, but Claude Code ignores them on plugin agents.
PLUGIN_AGENT_IGNORED_KEYS = {"permissionMode", "hooks", "mcpServers", "initialPrompt"}

errors: list[str] = []


def fail(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(p)


def plugin_dirs() -> list[Path]:
    return sorted(p for p in REPO.glob("plugins/ceh-*") if p.is_dir())


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


# --- manifests -------------------------------------------------------------


def load_json(path: Path, where: str) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(where, "file not found")
    except json.JSONDecodeError as e:
        fail(where, f"invalid JSON: {e}")
    return None


def check_manifests() -> dict[str, str]:
    """Validate plugin.json files + marketplace.json. Returns {plugin_name: version}."""
    versions: dict[str, str] = {}
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
        if name and version:
            versions[name] = str(version)

    mp_path = REPO / ".claude-plugin/marketplace.json"
    mp = load_json(mp_path, rel(mp_path))
    if mp is None:
        return versions
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
    return versions


# --- skills & agents -------------------------------------------------------


def check_scalar_style(path: Path) -> None:
    """Enforce the repo's frontmatter scalar conventions.

    `description` must be a folded block scalar (`>-`). It is the only style with no
    escaping burden: ':', '"', "'", '\\' and '#' are all literal inside it, so no
    description can break the block, and '-' strips the trailing newline. Every other
    style needs escaping that has silently broken files here before.

    Any other key must not be a plain scalar containing ': ' — a strict YAML parser
    reads that as a nested mapping and rejects the block. Quote those values.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return
    lines = text.splitlines()
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    for line in lines[1 : end or 1]:
        m = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if key == "description":
            if value != ">-":
                fail(
                    rel(path),
                    "'description' must use the folded block scalar '>-' "
                    f"(found {value[:12]!r}...) - see CLAUDE.md",
                )
        elif value and not value.startswith(("'", '"', ">", "|")) and ": " in value:
            fail(rel(path), f"'{key}' is an unquoted scalar containing ': ' - quote it")


def check_frontmatter_doc(
    path: Path, expected_name: str, allowed_keys: set[str]
) -> None:
    where = rel(path)
    check_scalar_style(path)
    if TEMPLATE_MARKER in path.read_text(encoding="utf-8"):
        fail(
            where,
            f"{TEMPLATE_MARKER} comment from the template is still present - delete it",
        )
    fm = parse_frontmatter(path)
    if fm is None:
        fail(where, "missing YAML frontmatter block")
        return
    for key in fm:
        if key not in allowed_keys:
            why = (
                "is ignored on plugin agents"
                if key in PLUGIN_AGENT_IGNORED_KEYS
                else "is not a documented key, so Claude Code ignores it silently"
            )
            fail(where, f"frontmatter '{key}' {why} - remove it")
    name = fm.get("name")
    if not name:
        fail(where, "frontmatter missing 'name'")
    elif not NAME.match(name) or len(name) > MAX_NAME_LEN:
        fail(
            where,
            f"name '{name}' must be lowercase letters, digits and single hyphens, "
            f"max {MAX_NAME_LEN} chars",
        )
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


def check_skills() -> None:
    for d in plugin_dirs():
        for skill_dir in sorted((d / "skills").glob("*")):
            if not skill_dir.is_dir():
                continue
            sm = skill_dir / "SKILL.md"
            if not sm.exists():
                fail(rel(skill_dir), "skill directory has no SKILL.md")
                continue
            check_frontmatter_doc(sm, skill_dir.name, SKILL_KEYS)


def check_agents() -> None:
    for d in plugin_dirs():
        for agent in sorted((d / "agents").glob("*.md")):
            check_frontmatter_doc(agent, agent.stem, AGENT_KEYS)
            fm = parse_frontmatter(agent)
            if fm is not None and not fm.get("model"):
                fail(
                    rel(agent),
                    "frontmatter missing 'model' - set it, even as 'inherit'",
                )


# --- references ------------------------------------------------------------


def doc_files() -> list[Path]:
    docs = []
    for d in plugin_dirs():
        docs += sorted((d / "skills").glob("*/SKILL.md"))
        docs += sorted((d / "agents").glob("*.md"))
    return docs


def check_references() -> None:
    # Anchor on a top-level `references/` token (not preceded by another path
    # segment) so example paths like `docs/references/...` are not matched.
    ref_pat = re.compile(r"(?<![\w./-])references/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+")
    script_pat = re.compile(
        r"\$\{CLAUDE_PLUGIN_ROOT\}/((?:scripts|references)/[A-Za-z0-9_./-]+)"
    )
    # ${CLAUDE_SKILL_DIR} is substituted by Claude Code with the skill's own directory,
    # so these resolve relative to the SKILL.md, not the plugin root.
    skill_dir_pat = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([A-Za-z0-9_./-]+)")
    for doc in doc_files():
        where = rel(doc)
        # SKILL.md -> plugins/ceh-<plugin>/skills/<name>/SKILL.md ; agent -> plugins/ceh-<plugin>/agents/<name>.md
        plugin_root = (
            doc.parents[2] if doc.parent.parent.name == "skills" else doc.parents[1]
        )
        base_dir = doc.parent
        text = doc.read_text(encoding="utf-8")
        for rec in dict.fromkeys(ref_pat.findall(text)):
            if not (base_dir / rec).exists():
                fail(where, f"reference '{rec}' not found")
        for rec in dict.fromkeys(script_pat.findall(text)):
            if not (plugin_root / rec).exists():
                fail(where, f"plugin-root reference '{rec}' not found")
        for rec in dict.fromkeys(skill_dir_pat.findall(text)):
            if not (base_dir / rec).resolve().exists():
                fail(where, f"skill-dir reference '{rec}' not found")


# --- skill references (plugin:component) -----------------------------------


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


def check_skill_refs() -> None:
    comps = known_components()
    plugins = {d.name for d in plugin_dirs()}
    ref_pat = re.compile(r"\bceh-[a-z0-9-]+:[a-z0-9-]+\b")
    for doc in doc_files():
        where = rel(doc)
        text = doc.read_text(encoding="utf-8")
        for ref in dict.fromkeys(ref_pat.findall(text)):
            plugin = ref.split(":", 1)[0]
            if plugin in plugins and ref not in comps:
                fail(where, f"skill reference '{ref}' does not resolve")


# --- scripts ---------------------------------------------------------------


def check_scripts() -> None:
    have_shellcheck = shutil.which("shellcheck") is not None
    have_bash = shutil.which("bash") is not None

    def run(cmd: list[str]) -> subprocess.CompletedProcess:
        # cwd=REPO + POSIX-relative paths so Git Bash on Windows resolves them.
        return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)

    for d in plugin_dirs():
        for script in sorted((d / "scripts").glob("*")):
            where = rel(script)
            if script.suffix == ".sh":
                if have_bash:
                    r = run(["bash", "-n", where])
                    if r.returncode != 0:
                        fail(where, f"bash syntax error: {r.stderr.strip()}")
                if have_shellcheck:
                    r = run(["shellcheck", "-S", "error", where])
                    if r.returncode != 0:
                        fail(where, f"shellcheck error:\n{r.stdout.strip()}")
            elif script.suffix == ".py":
                r = run([sys.executable, "-m", "py_compile", where])
                if r.returncode != 0:
                    fail(where, f"py_compile error: {r.stderr.strip()}")


# --- dependencies & invocations --------------------------------------------


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


def check_dependencies() -> None:
    """Deps resolve, the graph is acyclic, and ceh-scenario-* dirs hold a manifest only."""
    deps = plugin_deps()
    for name, targets in deps.items():
        where = rel(REPO / f"plugins/{name}/.claude-plugin/plugin.json")
        for t in targets:
            if t not in deps:
                fail(where, f"dependency '{t}' is not a plugin in this repo")
            elif t.startswith("ceh-scenario-") and not name.startswith("ceh-scenario-"):
                fail(
                    where, f"only a scenario bundle may depend on scenario bundle '{t}'"
                )

    # acyclicity (iterative DFS with a colour map, so the cycle path is reportable)
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

    for d in plugin_dirs():
        if not d.name.startswith("ceh-scenario-"):
            continue
        where = rel(d / ".claude-plugin/plugin.json")
        if not deps[d.name]:
            fail(where, "scenario bundle has no 'dependencies'")
        allowed = {d / ".claude-plugin/plugin.json", d / "README.md"}
        for f in sorted(d.rglob("*")):
            if f.is_file() and f not in allowed:
                fail(
                    rel(f), "scenario bundle may contain only plugin.json and README.md"
                )


INVOKE_PAT = re.compile(r'Invoke the Skill tool with skill="([^"]+)"')


def check_invocations() -> None:
    """An explicit Skill call must resolve, be installed by declaration, and be invocable."""
    comps = known_components()
    deps = plugin_deps()
    skill_fm: dict[str, dict[str, str]] = {}
    for d in plugin_dirs():
        for skill_dir in (d / "skills").glob("*"):
            if (skill_dir / "SKILL.md").exists():
                skill_fm[f"{d.name}:{skill_dir.name}"] = (
                    parse_frontmatter(skill_dir / "SKILL.md") or {}
                )

    def reachable(root: str) -> set[str]:
        seen, stack = {root}, [root]
        while stack:
            for t in deps.get(stack.pop(), []):
                if t not in seen:
                    seen.add(t)
                    stack.append(t)
        return seen

    for doc in doc_files():
        where = rel(doc)
        source = doc.relative_to(REPO / "plugins").parts[0]
        allowed = reachable(source)
        for ref in dict.fromkeys(INVOKE_PAT.findall(doc.read_text(encoding="utf-8"))):
            if ref not in comps:
                fail(where, f"invocation target '{ref}' does not resolve")
                continue
            target = ref.split(":", 1)[0]
            if target not in allowed:
                fail(
                    where,
                    f"invokes '{ref}' but '{source}' does not depend on '{target}'",
                )
            if (
                str(skill_fm.get(ref, {}).get("disable-model-invocation", "")).lower()
                == "true"
            ):
                fail(
                    where, f"invokes '{ref}', which sets disable-model-invocation: true"
                )


def main() -> int:
    check_manifests()
    check_skills()
    check_agents()
    check_references()
    check_skill_refs()
    check_dependencies()
    check_invocations()
    check_scripts()

    if errors:
        print(f"FAIL: {len(errors)} problem(s) found\n")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: all plugin checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
