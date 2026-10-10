#!/usr/bin/env python3
"""Validate the ceh-* plugin repo: manifests, skills, agents, references, scripts.

Stdlib-only so it runs locally (Windows/macOS/Linux) and in CI without installs.
Run from the repo root: `python tools/validate-plugins/validate.py`.
Exits non-zero if any check fails.

Checks:
  manifests  - plugin.json valid, name matches dir, semver version; marketplace.json
               lists every plugin with a matching version and an existing source path.
  skills     - every skills/<name>/SKILL.md has name + description frontmatter, name == dir,
               description <= 300 chars, optional compatibility <= 500 chars, and states
               disable-model-invocation, user-invocable and license explicitly.
  agents     - every agents/<name>.md has name + description + model frontmatter, name == file
               stem, description <= 300 chars.
  keys       - skill/agent names are lowercase-hyphenated (<= 64 chars); every frontmatter key is
               one Claude Code documents; no plugin-agent key Claude Code ignores; no
               TEMPLATE-GUIDANCE comment left over from a template.
  scalars    - `description` uses the folded block scalar `>-`; no other frontmatter key is a
               plain scalar containing ': ' (which strict YAML rejects).
  references - `references/...`, `${CLAUDE_PLUGIN_ROOT}/{scripts,references}/...` and `${CLAUDE_SKILL_DIR}/...`
               mentions in SKILL.md/agent files resolve to a real file.
  budget     - the sum of all skill and agent descriptions stays under MAX_TOTAL_DESCRIPTION_LEN.
  skill-refs - `plugin:component` references resolve to a real skill or agent.
  deps       - every `dependencies` entry names a plugin in this repo and the graph is acyclic.
  invocations- every `Invoke the Skill tool with skill="X"` resolves, is in-plugin or in a
               declared dependency, and does not set `disable-model-invocation: true`.
  repo-rules - docs/PLUGIN_VERSIONS.md matches every plugin.json version; each plugin's newest
               CHANGELOG.md Plugin versions row matches it too, under the section
               PLUGIN_VERSIONS.md dates it to; no marketplace entry
               declares dependencies; a cross-cutting plugin (CLAUDE.md tier table) depends only
               on cross-cutting plugins; a skill a hook script names sets user-invocable: false;
               every user-only skill is named in ceh-every-session:whats-next.
  hygiene    - no invisible Unicode or personal absolute path in tracked text; every skill and
               agent is named in its plugin README.
  scripts    - *.sh pass `bash -n` (+ shellcheck if available); *.py pass py_compile.
  hooks      - every script a hooks.json runs has fixtures here; each fixture pipes a hand-built
               payload into the script and checks its exit code and output. No model call.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
# Claude Code allows 1024. The repo budget is lower because every description is paid for in
# context on every session that installs the plugin (docs/VISION.md, goal 4), and the skill
# listing drops whole descriptions once it overflows its budget of 1% of the context window.
MAX_DESCRIPTION_LEN = 300
# Ratchet on the sum of every skill and agent description. Lower it when the total drops; raise it
# only in the PR that adds a component, by that component's description length.
MAX_TOTAL_DESCRIPTION_LEN = 27045
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
# Stated on every skill even at their defaults, so the frontmatter says who invokes it.
EXPLICIT_SKILL_KEYS = ("disable-model-invocation", "user-invocable", "license")
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
    return sorted(p for p in REPO.glob("plugins/*/ceh-*") if p.is_dir())


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
            fm = parse_frontmatter(sm) or {}
            for key in EXPLICIT_SKILL_KEYS:
                if key not in fm:
                    fail(rel(sm), f"frontmatter must state '{key}' explicitly")


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
        # SKILL.md -> plugins/standalone/ceh-<plugin>/skills/<name>/SKILL.md ; agent -> plugins/standalone/ceh-<plugin>/agents/<name>.md
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


def check_description_budget() -> None:
    total = sum(
        len((parse_frontmatter(doc) or {}).get("description", ""))
        for doc in doc_files()
    )
    if total > MAX_TOTAL_DESCRIPTION_LEN:
        fail(
            "descriptions",
            f"total is {total} chars, over the {MAX_TOTAL_DESCRIPTION_LEN} ratchet - trim, "
            "or raise MAX_TOTAL_DESCRIPTION_LEN by the new component's description only",
        )


# --- repo hygiene ----------------------------------------------------------

INVISIBLE_PAT = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]")
USER_PATH_PAT = re.compile(r"[A-Za-z]:[\\/]Users[\\/]\w|/Users/\w|/home/\w")
HYGIENE_ROOTS = ("plugins", "docs", "tools", ".claude", ".github")
HYGIENE_SUFFIXES = {".md", ".json", ".py", ".sh", ".ps1", ".yml", ".yaml", ".html"}


def check_hygiene() -> None:
    """No invisible Unicode, no personal absolute paths, every component in its plugin README."""
    files = list(REPO.glob("*.md"))
    for root in HYGIENE_ROOTS:
        files += [p for p in (REPO / root).rglob("*") if p.suffix in HYGIENE_SUFFIXES]
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


# --- hook fixtures ---------------------------------------------------------

HOOK_SCRIPT_PAT = re.compile(r"/scripts/([\w.-]+)")


def hook_fixtures(tmp: Path) -> list[dict]:
    """Build the files the fixtures read, then return one dict per fixture.

    Keys: script, stdin (dict), env, args, repeat (runs on one session; the last is checked),
    code (exit code), out (substring of stdout; "" means stdout must be empty), err (substring
    of stderr).
    """
    big, small = tmp / "big.txt", tmp / "small.txt"
    big.write_text("x\n" * 400, encoding="utf-8")
    small.write_text("x\n" * 5, encoding="utf-8")
    big_p, small_p = big.as_posix(), small.as_posix()

    repos = {}
    for branch in ("main", "feat/x"):
        repo = tmp / branch.replace("/", "-")
        repo.mkdir()
        git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run([*git, "init", "-q", "-b", branch], check=True)
        subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "x"], check=True)
        repos[branch] = (repo / "f.txt").as_posix()

    now_ms = time.time() * 1000
    for name, pct in (("home-95", 95), ("home-50", 50)):
        sl = tmp / name / ".claude" / "statusline" / "p"
        sl.mkdir(parents=True)
        record = {
            "ts": now_ms,
            "data": {"rate_limits": {"five_hour": {"used_percentage": pct}}},
        }
        (sl / "s.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    (tmp / "home-empty").mkdir()

    def home(name: str) -> dict:
        h = str(tmp / name)
        return {"HOME": h, "USERPROFILE": h}

    def edit(path: str) -> dict:
        return {"tool_name": "Edit", "tool_input": {"file_path": path}}

    def read(path: str, **extra) -> dict:
        return {"tool_name": "Read", "tool_input": {"file_path": path, **extra}}

    def bash(cmd: str) -> dict:
        return {"tool_name": "Bash", "tool_input": {"command": cmd}}

    bulk = {"BULK_READER_MIN_LINES": "350"}
    any_tool = {"tool_name": "Read", "tool_input": {}, "transcript_path": "t.jsonl"}
    return [
        # branch-guard: deny on the default branch, allow elsewhere or when switched off.
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "out": "On the default branch"},
        {"script": "branch-guard.py", "stdin": edit(repos["feat/x"]), "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "env": {"CEH_BRANCH_GUARD": "off"}, "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "env": {"CEH_DISABLED_HOOKS": "x, branch-guard"}, "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "repeat": 4, "out": "denial 4"},
        # bulk-read-guard: whole reads of a large file only, and only when opted in.
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "env": bulk, "out": "Blocked:"},
        {"script": "bulk-read-guard.py", "stdin": read(big_p, limit=20), "env": bulk, "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(small_p), "env": bulk, "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "env": {**bulk, "CEH_DISABLED_HOOKS": "bulk-read-guard"}, "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "env": bulk, "repeat": 4, "out": "denial 4"},
        # bulk-read-bash-guard: dumps are denied, narrowed commands pass.
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"cat {big_p}"), "env": bulk, "out": "Blocked:"},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"cat {big_p} | grep x"), "env": bulk, "out": ""},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"head -n 5 {big_p}"), "env": bulk, "out": ""},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"tail -n +2 {big_p}"), "env": bulk, "out": "Blocked:"},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"cat {big_p}"), "env": bulk, "repeat": 4, "out": "denial 4"},
        # usage-limit-watch: warn with no sensor, block over the threshold, quiet under it.
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": home("home-empty"), "code": 1, "err": "INACTIVE"},
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": home("home-95"), "code": 2, "err": "usage-limit-handoff"},
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": home("home-50"), "out": ""},
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": {**home("home-empty"), "CEH_DISABLED_HOOKS": "usage-limit-watch"}, "out": ""},
        # Context injectors: valid JSON naming their skill, silent when switched off.
        {"script": "load-contract.sh", "stdin": {}, "out": "ceh-coding-conduct:agent-coding-contract"},
        {"script": "load-contract.sh", "stdin": {}, "args": ["SubagentStart"], "out": '"hookEventName": "SubagentStart"'},
        {"script": "load-contract.sh", "stdin": {}, "env": {"CEH_DISABLED_HOOKS": "load-contract"}, "out": ""},
        {"script": "inject-less-code-reminder.sh", "stdin": {}, "out": "WRITE LESS CODE"},
        {"script": "inject-less-code-reminder.sh", "stdin": {}, "env": {"CEH_DISABLED_HOOKS": "inject-less-code-reminder"}, "out": ""},
    ]  # fmt: skip


def check_hooks() -> None:
    scripts: dict[str, Path] = {}
    for d in plugin_dirs():
        hooks = d / "hooks" / "hooks.json"
        if hooks.is_file():
            for name in HOOK_SCRIPT_PAT.findall(hooks.read_text(encoding="utf-8")):
                scripts[name] = d / "scripts" / name

    # The full path, not "bash": Windows CreateProcess searches System32 first and finds WSL's
    # bash.exe, which does not pass the fixture's environment variables through.
    bash = shutil.which("bash")
    # The developer's own CEH_* and BULK_READER_* settings must not change a fixture's result.
    base_env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("CEH_", "BULK_READER_"))
    }
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        state = tmp / "state"  # denial counters and warn-once markers land here
        state.mkdir()
        base_env.update({"TMP": str(state), "TEMP": str(state), "TMPDIR": str(state)})
        fixtures = hook_fixtures(tmp)

        for name in sorted(set(scripts) - {f["script"] for f in fixtures}):
            fail(
                rel(scripts[name]),
                "hook script has no fixture in validate.py hook_fixtures()",
            )

        for i, f in enumerate(fixtures):
            script = scripts.get(f["script"])
            where = f"hook fixture {i} ({f['script']})"
            if script is None:
                fail(where, "no hooks.json runs this script")
                continue
            if script.suffix == ".sh" and not bash:
                continue
            cmd = [sys.executable] if script.suffix == ".py" else [bash]
            stdin = json.dumps({"session_id": f"fixture-{i}", **f["stdin"]})
            env = {**base_env, **f.get("env", {})}
            for _ in range(f.get("repeat", 1)):
                r = subprocess.run(
                    # cwd=REPO + POSIX-relative path so Git Bash on Windows resolves it.
                    [*cmd, rel(script), *f.get("args", [])],
                    cwd=REPO,
                    input=stdin,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=30,
                )
            if r.returncode != f.get("code", 0):
                fail(
                    where,
                    f"exit {r.returncode}, expected {f.get('code', 0)}: {r.stderr.strip()}",
                )
            if f.get("out") == "" and r.stdout.strip():
                fail(where, f"expected no output, got: {r.stdout.strip()[:200]}")
            elif f.get("out") and f["out"] not in r.stdout:
                fail(where, f"stdout lacks {f['out']!r}: {r.stdout.strip()[:200]}")
            if f.get("err") and f["err"] not in r.stderr:
                fail(where, f"stderr lacks {f['err']!r}: {r.stderr.strip()[:200]}")
            if r.stdout.strip():
                try:
                    json.loads(r.stdout)
                except ValueError:
                    fail(where, f"stdout is not valid JSON: {r.stdout.strip()[:200]}")


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
    """Deps resolve and the graph is acyclic."""
    deps = plugin_deps()
    dirs = {d.name: d for d in plugin_dirs()}
    for name, targets in deps.items():
        where = rel(dirs[name] / ".claude-plugin/plugin.json")
        for t in targets:
            if t not in deps:
                fail(where, f"dependency '{t}' is not a plugin in this repo")

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
        source = doc.relative_to(REPO / "plugins").parts[1]
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


# --- repo rules from CLAUDE.md -----------------------------------------------

COMPONENT_PAT = re.compile(r"\b(ceh-[a-z0-9-]+):([a-z0-9-]+)\b")


def check_repo_rules(versions: dict[str, str]) -> None:
    """Rules CLAUDE.md states that a machine can check (docs/VISION.md, goal 5)."""
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


def main() -> int:
    versions = check_manifests()
    check_skills()
    check_agents()
    check_references()
    check_description_budget()
    check_skill_refs()
    check_dependencies()
    check_invocations()
    check_repo_rules(versions)
    check_hygiene()
    check_scripts()
    check_hooks()

    if errors:
        print(f"FAIL: {len(errors)} problem(s) found\n")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: all plugin checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
