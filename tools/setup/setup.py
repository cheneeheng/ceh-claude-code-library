# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Set up a machine and a folder for the ceh-claude-code-library plugins.

Finds the tools the picked plugins need, installs each one after a yes, installs or enables the
picked plugins for this folder, and sets the Claude Code settings they rely on. `--check`, or no
terminal to answer, reports all of it and changes nothing. See tools/setup/README.md.

TOOLS and PLUGINS are literal dicts: tools/validate-plugins/checks/setup_registry.py reads them
with ast.literal_eval and fails when they drift from the plugins.
"""

from __future__ import annotations

import argparse
import json
import ntpath
import os
import posixpath
import re
import shutil
import subprocess
import sys
import textwrap
import time
import urllib.request
from pathlib import Path

MARKETPLACE = "ceh-claude-code-library"
MARKETPLACE_REPO = "cheneeheng/ceh-claude-code-library"
SCOPE_RANK = {"user": 0, "project": 1, "local": 2}
# The guard's default, CEH_USAGE_STALE_MINUTES in ceh-every-session's usage-limit-watch.py.
STALE_MINUTES = 15
STATUSLINE_TAG = "slh-v0.4.0"
STATUSLINE_RAW = (
    "https://raw.githubusercontent.com/cheneeheng/claude-code-command-center/"
    f"{STATUSLINE_TAG}/tools/statusline-hook/statusline-hook"
)
STATUSLINE_README = (
    "https://github.com/cheneeheng/claude-code-command-center/tree/"
    f"{STATUSLINE_TAG}/tools/statusline-hook#quota-export"
)
STATUSLINE_OFF = "C4_STATUSLINE_DISABLE_EXPORT"
# The skill listing budget, a fraction of the context window (Claude Code's default is 0.01).
BUDGET_KEY = "skillListingBudgetFraction"
BUDGET = 0.02
BUDGET_VAR = "SLASH_COMMAND_TOOL_CHAR_BUDGET"

# Tool name -> how to find it, which version it needs, what names it in a `compatibility`
# field, and how to install it per platform (None: no known installer).
TOOLS = {
    "python3": {
        "probe": ["python3", "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
        "min_version": (3, 10),
        "alternatives": [],
        "words": [r"\bpython3\b"],
        "install": {
            "windows": ["winget", "install", "Python.Python.3.13"],
            "darwin": ["brew", "install", "python"],
            "linux": ["sudo", "apt-get", "install", "-y", "python3"],
        },
    },
    "bash": {
        "probe": ["bash", "--version"],
        "alternatives": [],
        "words": [r"\bbash\b"],
        "install": {
            "windows": ["winget", "install", "Git.Git"],
            "darwin": None,
            "linux": None,
        },
    },
    "git": {
        "probe": ["git", "--version"],
        "alternatives": [],
        "words": [r"\bgit\b", r"git CLI"],
        "install": {
            "windows": ["winget", "install", "Git.Git"],
            "darwin": ["brew", "install", "git"],
            "linux": ["sudo", "apt-get", "install", "-y", "git"],
        },
    },
    "gh": {
        "probe": ["gh", "--version"],
        "alternatives": [],
        "words": [r"\bgh\b", r"GitHub CLI"],
        "install": {
            "windows": ["winget", "install", "GitHub.cli"],
            "darwin": ["brew", "install", "gh"],
            "linux": ["sudo", "apt-get", "install", "-y", "gh"],
        },
    },
    "uv": {
        "probe": ["uv", "--version"],
        "alternatives": [],
        "words": [r"\buv\b"],
        "install": {
            "windows": [
                "powershell",
                "-ExecutionPolicy",
                "ByPass",
                "-c",
                "irm https://astral.sh/uv/install.ps1 | iex",
            ],
            "darwin": ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
            "linux": ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
        },
    },
    "bun": {
        "probe": ["bun", "--version"],
        "alternatives": ["node"],
        "words": [r"\b[Bb]un\b"],
        "install": {
            "windows": ["powershell", "-c", "irm bun.sh/install.ps1 | iex"],
            "darwin": ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"],
            "linux": ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"],
        },
    },
    "node": {
        "probe": ["node", "--version"],
        # less-code: one floor per tool (the web skills' 20); per-skill floors only if reported.
        "min_version": (20, 0),
        "alternatives": [],
        "words": [r"Node\.js"],
        "install": {
            "windows": ["winget", "install", "OpenJS.NodeJS.LTS"],
            "darwin": ["brew", "install", "node"],
            # Ubuntu 24.04's apt nodejs is 18.19, below the floor.
            "linux": None,
        },
    },
    "chrome-extension": {
        "probe": None,
        "note": (
            "need the Claude in Chrome extension to walk a live web UI. The script cannot "
            "check for it, so check it yourself."
        ),
        "alternatives": [],
        "words": [r"Claude in Chrome"],
        "install": {"windows": None, "darwin": None, "linux": None},
    },
}

GROUPS = ("core", "shape", "build", "prove", "tell", "stack", "later")

# Plugin name -> its docs/GETTING_STARTED.md group, its plugin.json dependencies, its skills, the
# tools without which it is not installed, and the skills (or "hooks") each tool's absence
# degrades. min_claude: Claude Code version -> the skills that need it.
PLUGINS = {
    "ceh-every-session": {
        "group": "core",
        "dependencies": [],
        "skills": [
            "audit-anything",
            "delegate-bulk-reads",
            "find-available-guide",
            "hand-off-session",
            "prevent-repeat-mistake",
            "record-project-decisions",
            "review-anything",
            "stress-test-plan",
            "usage-limit-handoff",
            "whats-next",
            "write-questionnaire",
            "write-research-note",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "audit-anything",
                "hand-off-session",
                "prevent-repeat-mistake",
                "record-project-decisions",
                "review-anything",
                "whats-next",
            ],
        },
    },
    "ceh-git-workflow": {
        "group": "core",
        "dependencies": [],
        "skills": [
            "address-review-comments",
            "commit",
            "pull-request",
            "release",
            "write-period-retro",
            "update-changelog",
            "update-readme",
            "write-code-review",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks"],
            "git": [
                "hooks",
                "commit",
                "pull-request",
                "release",
                "write-period-retro",
                "update-changelog",
                "update-readme",
            ],
            "gh": [
                "address-review-comments",
                "pull-request",
                "release",
                "write-period-retro",
            ],
        },
    },
    "ceh-coding-conduct": {
        "group": "core",
        "dependencies": [],
        "skills": [
            "agent-coding-contract",
            "find-root-cause",
            "refactor-repo",
            "shrink-diff",
            "write-less-code",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "bash": ["hooks"],
            "uv": ["hooks", "find-root-cause"],
            "git": ["refactor-repo", "shrink-diff"],
        },
    },
    "ceh-product-direction": {
        "group": "shape",
        "dependencies": [],
        "skills": [
            "develop-business-plan",
            "find-product-market-fit",
            "plan-go-to-market",
            "review-business-plan",
            "run-premortem",
            "set-operating-plan",
            "sharpen-strategy",
            "stress-test-unit-economics",
            "write-investor-materials",
            "write-product-requirements",
            "write-vision-and-strategy",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "develop-business-plan",
                "find-product-market-fit",
                "plan-go-to-market",
                "review-business-plan",
                "run-premortem",
                "set-operating-plan",
                "sharpen-strategy",
                "stress-test-unit-economics",
                "write-investor-materials",
                "write-product-requirements",
                "write-vision-and-strategy",
            ],
            "node": ["develop-business-plan"],
        },
    },
    "ceh-competitor-analysis": {
        "group": "shape",
        "dependencies": ["ceh-ui-design"],
        "skills": ["analyze-competitor", "compare-competitors"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "analyze-competitor", "compare-competitors"],
            "git": ["analyze-competitor"],
        },
    },
    "ceh-build-plan": {
        "group": "build",
        "dependencies": [],
        "skills": ["implement-from-plan", "review-build-plan", "write-build-plan"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "implement-from-plan",
                "review-build-plan",
                "write-build-plan",
            ],
        },
    },
    "ceh-documentation": {
        "group": "build",
        "dependencies": [],
        "skills": [
            "write-api-reference",
            "write-concept-docs",
            "write-examples",
            "write-guides-and-runbooks",
            "write-project-docs",
        ],
        "requires": [],
        "degrades": {
            "git": ["write-api-reference", "write-concept-docs", "write-project-docs"],
            "uv": ["write-concept-docs", "write-examples"],
            "bun": ["write-examples"],
        },
    },
    "ceh-check-build-against-plan": {
        "group": "prove",
        "dependencies": [],
        "skills": ["check-build-against-plan"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "check-build-against-plan"],
        },
    },
    "ceh-testing": {
        "group": "prove",
        "dependencies": [],
        "skills": [
            "audit-test-suite",
            "close-test-risk-gaps",
            "design-test-cases",
            "explore-app-for-bugs",
            "measure-performance",
            "test-a-bug-fix",
            "verify-behavior-preserved",
            "write-evidence-report",
            "write-test-first",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "audit-test-suite",
                "close-test-risk-gaps",
                "explore-app-for-bugs",
                "measure-performance",
                "test-a-bug-fix",
                "verify-behavior-preserved",
                "write-evidence-report",
            ],
            "bun": [
                "audit-test-suite",
                "close-test-risk-gaps",
                "test-a-bug-fix",
                "verify-behavior-preserved",
            ],
            "git": [
                "test-a-bug-fix",
                "verify-behavior-preserved",
                "write-evidence-report",
            ],
            "chrome-extension": ["explore-app-for-bugs"],
        },
    },
    "ceh-usability-audit": {
        "group": "prove",
        "dependencies": [],
        "skills": [
            "audit-error-messages",
            "audit-interface",
            "simulate-newcomer-first-run",
            "write-plain-language",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": [
                "hooks",
                "audit-error-messages",
                "audit-interface",
                "simulate-newcomer-first-run",
            ],
            "git": ["simulate-newcomer-first-run"],
            "chrome-extension": ["audit-interface"],
        },
    },
    "ceh-security-audit": {
        "group": "prove",
        "dependencies": [],
        "skills": ["audit-codebase-security"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "audit-codebase-security"],
            "git": ["audit-codebase-security"],
            "bun": ["audit-codebase-security"],
        },
    },
    "ceh-blog-and-seo": {
        "group": "tell",
        "dependencies": [],
        "skills": [
            "draft-post",
            "edit-post",
            "make-page-crawlable",
            "repurpose-post",
            "write-llms-txt",
            "write-project-listing-text",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "draft-post", "edit-post", "write-project-listing-text"],
        },
    },
    "ceh-python-service": {
        "group": "stack",
        "dependencies": ["ceh-testing"],
        "skills": [
            "configure-python-service-env",
            "write-fastapi-endpoints",
            "write-postgresql-code",
            "write-pytest-service-tests",
        ],
        "requires": ["uv"],
        "degrades": {},
    },
    "ceh-python-library": {
        "group": "stack",
        "dependencies": ["ceh-testing"],
        "skills": [
            "configure-python-library-env",
            "publish-python-library",
            "write-pytest-library-tests",
        ],
        "requires": ["uv"],
        "degrades": {},
    },
    "ceh-web-frontend": {
        "group": "stack",
        "dependencies": ["ceh-testing", "ceh-ui-design"],
        "skills": [
            "check-visual-parity",
            "configure-bun-vite-env",
            "make-ui-accessible",
            "visualize-graph-cytoscape",
            "write-react-vite-code",
            "write-sveltekit-code",
            "write-vitest-playwright-tests",
        ],
        "requires": [],
        "degrades": {
            "bun": [
                "configure-bun-vite-env",
                "visualize-graph-cytoscape",
                "write-react-vite-code",
                "write-sveltekit-code",
                "write-vitest-playwright-tests",
            ],
            "git": ["check-visual-parity"],
        },
    },
    "ceh-codebase-explanation": {
        "group": "later",
        "dependencies": [],
        "skills": [
            "document-architecture",
            "explain-codebase",
            "explain-until-understood",
            "maintain-glossary",
            "trace-code-rationale",
        ],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "document-architecture", "maintain-glossary"],
            "git": ["explain-codebase", "trace-code-rationale"],
            "gh": ["trace-code-rationale"],
        },
    },
    "ceh-ui-design": {
        "group": "later",
        "dependencies": [],
        "skills": ["design-ui"],
        "requires": [],
        "degrades": {},
    },
    "ceh-ag-ui": {
        "group": "later",
        "dependencies": ["ceh-ui-design"],
        "skills": [
            "add-canvas-component",
            "add-human-approval",
            "add-live-state-panel",
            "build-ag-ui",
            "build-ag-ui-agent",
        ],
        "requires": [],
        "degrades": {
            "uv": [
                "add-canvas-component",
                "add-human-approval",
                "add-live-state-panel",
                "build-ag-ui",
                "build-ag-ui-agent",
            ],
            "bun": [
                "add-canvas-component",
                "add-human-approval",
                "add-live-state-panel",
                "build-ag-ui",
            ],
        },
    },
    "ceh-workflow-builder": {
        "group": "later",
        "dependencies": [],
        "skills": ["build-agentic-workflow", "interview-workflow-task"],
        "requires": [],
        "degrades": {
            "python3": ["hooks"],
            "uv": ["hooks", "build-agentic-workflow", "interview-workflow-task"],
        },
        "min_claude": {"2.1.248": ["build-agentic-workflow"]},
    },
    "ceh-workflow-runner": {
        "group": "later",
        "dependencies": [],
        "skills": ["run-agentic-workflow"],
        "requires": [],
        "degrades": {
            "python3": ["hooks", "run-agentic-workflow"],
            "uv": ["hooks", "run-agentic-workflow"],
        },
        "min_claude": {"2.1.269": ["run-agentic-workflow"]},
    },
    "ceh-session-learning": {
        "group": "later",
        "dependencies": [],
        "skills": ["diagnose-session", "turn-session-into-skill"],
        "requires": [],
        "degrades": {"python3": ["hooks"], "uv": ["hooks"]},
    },
}


# ---- decisions: pure functions, tested in test_setup.py ----


def version_of(text: str) -> tuple[int, int] | None:
    """The first N.N in a probe's output, such as 3.13 from "3.13" or 18.19 from "v18.19.1"."""
    m = re.search(r"(\d+)\.(\d+)", text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def closure(picks: list[str]) -> list[str]:
    """The picks plus every plugin their dependencies bring, in pick order."""
    out: list[str] = []

    def add(name: str) -> None:
        if name in PLUGINS and name not in out:
            out.append(name)
            for dep in PLUGINS[name]["dependencies"]:
                add(dep)

    for name in picks:
        add(name)
    return out


def plugin_states(
    entries: list[dict], cwd: str, windows: bool
) -> dict[str, tuple[str, str]]:
    """Plugin name -> ("on" or "off", the winning scope) for this folder, from
    `claude plugin list --json`. Absent: not installed for this folder."""
    path = ntpath if windows else posixpath

    def norm(p: str) -> str:
        return path.normcase(path.normpath(p))

    here = norm(cwd)
    best: dict[str, tuple[str, str]] = {}
    for e in entries:
        name, _, market = e.get("id", "").partition("@")
        scope = e.get("scope")
        if market != MARKETPLACE or scope not in SCOPE_RANK:
            continue
        if scope != "user" and norm(e.get("projectPath") or "") != here:
            continue
        # local beats project beats user, as Claude Code's settings precedence does.
        if name not in best or SCOPE_RANK[scope] > SCOPE_RANK[best[name][1]]:
            # `enabled`, never `projectEnabled`, which reads false for enabled local installs.
            best[name] = ("on" if e.get("enabled") else "off", scope)
    return best


def resolve(
    picks: list[str], unmet: set[str], claude_version: tuple[int, int, int] | None
) -> tuple[list[str], list[str]]:
    """The picks plus their dependencies to set up, and the warning lines."""
    plugins: list[str] = []
    lines: list[str] = []
    for name in closure(picks):
        spec = PLUGINS[name]
        missing = [t for t in spec["requires"] if t in unmet]
        if missing:
            lines.append(
                f"{name} will not be installed: it needs {', '.join(missing)}. "
                f"Skills not installed: {', '.join(spec['skills'])}"
            )
            continue
        plugins.append(name)
        for tool, what in spec["degrades"].items():
            if tool in unmet:
                lines.append(
                    f"{name}: without {tool}, these lose function: {', '.join(what)}"
                )
            elif TOOLS[tool]["probe"] is None:
                lines.append(f"{name}: {', '.join(what)} {TOOLS[tool]['note']}")
        for version, skills in spec.get("min_claude", {}).items():
            need = tuple(int(x) for x in version.split("."))
            if claude_version and claude_version < need:
                have = ".".join(map(str, claude_version))
                lines.append(
                    f"{name}: {', '.join(skills)} need Claude Code {version} or later, "
                    f"you have {have}"
                )
    return plugins, lines


def statusline_command(
    settings: dict, windows: bool, has_pwsh: bool, path: str
) -> str | None:
    """The statusLine command to set, the one statusline-hook's own setup scripts write, or
    None when a statusLine is already set."""
    if settings.get("statusLine"):
        return None
    if not windows:
        return f'bash "{path}"'
    return f'{"pwsh" if has_pwsh else "powershell"} -NoProfile -File "{path}"'


def merge_budget(settings: dict, value: float) -> dict | None:
    """The settings with skillListingBudgetFraction raised to value, or None when it is
    already at least that. Every other key is kept."""
    current = settings.get(BUDGET_KEY)
    if isinstance(current, (int, float)) and current >= value:
        return None
    return {**settings, BUDGET_KEY: value}


def statusline_state(settings: dict, environ: dict, root: Path, now: float) -> str:
    """ "disabled", "fed" or "not fed", from the files the usage-limit guard reads."""
    if "1" in (
        environ.get(STATUSLINE_OFF),
        settings.get("env", {}).get(STATUSLINE_OFF),
    ):
        return "disabled"
    times = [p.stat().st_mtime for p in root.glob("*/*.jsonl") if p.is_file()]
    return "fed" if times and now - max(times) < STALE_MINUTES * 60 else "not fed"


# ---- the machine: commands, probes, files ----


def say(line: str = "") -> None:
    print(line, flush=True)


# ---- display ----

COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
try:
    "✓✗→─".encode(sys.stdout.encoding or "ascii")
    UNICODE = True
except (UnicodeEncodeError, LookupError):
    UNICODE = False  # a legacy code page, such as output piped on Windows
RULE = "─" if UNICODE else "-"
MARKS = {
    "ok": ("✓" if UNICODE else "+", "32"),  # green
    "bad": ("✗" if UNICODE else "x", "31"),  # red
    "warn": ("!", "33"),  # yellow
    "todo": ("→" if UNICODE else ">", "36"),  # cyan: would do, or not done yet
}


def paint(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if COLOR else text


def heading(title: str) -> None:
    say()
    say(paint(f"{RULE * 2} {title} ", "1") + paint(RULE * max(4, 60 - len(title)), "2"))


def row(kind: str, label: str, detail: str = "", width: int = 30) -> None:
    mark, code = MARKS[kind]
    say(
        f"  {paint(mark, code)} {label:<{width}} {paint(detail, '2') if detail else ''}".rstrip()
    )


def note(text: str, indent: int = 6) -> None:
    """A wrapped line under a row, for a command or an explanation."""
    width = max(60, min(shutil.get_terminal_size().columns, 110)) - indent
    for line in textwrap.wrap(text, width, break_on_hyphens=False) or [""]:
        say(" " * indent + line)


def short_version(text: str) -> str:
    m = re.search(r"\d+(\.\d+)+", text)
    return m.group(0) if m else text


def run(cmd: list[str], timeout: int = 60) -> tuple[int | None, str]:
    """Exit code and output, or (None, "") when the command cannot start."""
    exe = shutil.which(cmd[0]) or (cmd[0] if os.path.isabs(cmd[0]) else None)
    if not exe:
        return None, ""
    try:
        r = subprocess.run(
            [exe, *cmd[1:]], capture_output=True, text=True, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    return r.returncode, (r.stdout + r.stderr).strip()


def git_bash() -> str | None:
    """Git Bash on Windows, never System32's bash.exe, which starts WSL."""
    git = shutil.which("git")
    if not git:
        return None
    directory = Path(git).resolve().parent
    root = directory.parent
    # Git for Windows puts git.exe under cmd/, mingw64/bin/, ucrt64/bin/ or clang64/bin/.
    if root.name in ("mingw64", "mingw32", "ucrt64", "clang64", "clangarm64", "usr"):
        root = root.parent
    for candidate in (
        directory / "bash.exe",
        root / "bin/bash.exe",
        root / "usr/bin/bash.exe",
    ):
        if candidate.is_file():
            return str(candidate)
    return None


def probe(tool: str) -> tuple[bool, str]:
    """(present, what was found) for a tool with a probe."""
    cmd = list(TOOLS[tool]["probe"])
    if tool == "bash" and sys.platform == "win32":
        bash = git_bash()
        if not bash:
            return False, "missing (Git Bash)"
        cmd[0] = bash
    code, out = run(cmd)
    if code is None:
        return False, "missing"
    first = out.splitlines()[0] if out else ""
    if code != 0:
        return False, f"not working: {first or 'exit ' + str(code)}"
    floor = TOOLS[tool].get("min_version")
    if floor and (version_of(out) or (0, 0)) < floor:
        return False, f"{first} is older than {floor[0]}.{floor[1]}"
    return True, first


def claude_json(*args: str) -> list | None:
    code, out = run(["claude", *args])
    if code != 0:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def settings_path() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude"
    return Path(base) / "settings.json"


def read_settings(path: Path) -> dict | None:
    """The settings, {} when the file is missing, None when it cannot be read or parsed."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def recommended_core(git_repo: bool) -> list[str]:
    core = ["ceh-every-session"]
    if git_repo:
        core += ["ceh-git-workflow", "ceh-coding-conduct"]
    return core


def write_settings(path: Path, settings: dict) -> None:
    """Write through a temporary file that replaces the original, so a failed write leaves the
    old file whole."""
    write_file(path, json.dumps(settings, indent=2) + "\n")


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def ask(question: str, default: bool) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    try:
        answer = (
            input(f"  {paint('?', '35')} {question} {paint(hint, '2')} ")
            .strip()
            .lower()
        )
    except EOFError:
        return False
    return default if not answer else answer in ("y", "yes")


def run_shown(cmd: list[str]) -> int | None:
    """Run with the person's terminal attached, for installers that print or ask (sudo)."""
    exe = shutil.which(cmd[0])
    if not exe:
        return None
    try:
        return subprocess.run([exe, *cmd[1:]]).returncode
    except OSError:
        return None


def pick_plugins(states: dict, core: list[str], git_repo: bool) -> list[str]:
    """Step 3: a numbered list grouped as docs/GETTING_STARTED.md, Enter takes the core."""
    names = [n for g in GROUPS for n in PLUGINS if PLUGINS[n]["group"] == g]
    group = None
    for i, name in enumerate(names, 1):
        if PLUGINS[name]["group"] != group:
            group = PLUGINS[name]["group"]
            say(f"  {paint(group, '1')}")
        state = states.get(name, ("", ""))[0]
        tag = (
            paint("  on", "32")
            if state == "on"
            else paint("  off", "33")
            if state
            else ""
        )
        say(f"    {paint(f'{i:2}', '36')}  {name}{tag}")
    say()
    note(
        "Recommended core: ceh-every-session always, ceh-git-workflow if you work in a git "
        "repo, ceh-coding-conduct if you write code with Claude.",
        indent=2,
    )
    note(
        "This folder is "
        + (
            "a git repo, so Enter takes all three."
            if git_repo
            else "not a git repo, so Enter takes ceh-every-session."
        ),
        indent=2,
    )
    while True:
        try:
            answer = input("\n  Numbers to set up, separated by spaces (Enter: core): ")
        except EOFError:
            return core
        if not answer.strip():
            return core
        try:
            chosen = [names[int(n) - 1] for n in re.split(r"[\s,]+", answer.strip())]
        except (ValueError, IndexError):
            say(f"  Type numbers from 1 to {len(names)}, or press Enter.")
            continue
        return list(dict.fromkeys(chosen))


def install_statusline(windows: bool) -> str:
    """Download statusline-hook from the pinned tag and point statusLine at it."""
    path = settings_path()
    settings = read_settings(path)
    if settings is None:
        return f"not installed: {path} cannot be read as JSON"
    ext = "ps1" if windows else "sh"
    if not windows and not shutil.which("jq"):
        return "not installed: the sh statusline needs jq, which is missing"
    url = f"{STATUSLINE_RAW}.{ext}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            script = r.read().decode("utf-8")
    except (OSError, ValueError) as e:
        return f"not installed: download of {url} failed ({e})"
    dest = path.parent / f"statusline-hook.{ext}"
    command = statusline_command(
        settings, windows, bool(shutil.which("pwsh")), str(dest)
    )
    if command is None:
        return "already set"
    write_file(dest, script)
    settings["statusLine"] = {
        "type": "command",
        "command": command,
        "refreshInterval": 60,
    }
    write_settings(path, settings)
    return f"installed: {command}"


# ---- the run ----


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Set up this machine and folder for the ceh-claude-code-library plugins."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report only: install, enable and write nothing",
    )
    parser.add_argument(
        "--scope",
        choices=["local", "project", "user"],
        default="local",
        help="scope for plugins it installs (default: local, this folder only)",
    )
    parser.add_argument(
        "--plugins",
        help="comma-separated plugins to set up, instead of choosing from the list",
    )
    args = parser.parse_args(argv)
    windows = sys.platform == "win32"
    picks_given = [p.strip() for p in (args.plugins or "").split(",") if p.strip()]
    unknown = [p for p in picks_given if p not in PLUGINS]
    if unknown:
        parser.error(f"unknown plugins: {', '.join(unknown)}")

    # 1. Preflight
    # Symbols must never crash a redirected run on a legacy code page.
    sys.stdout.reconfigure(errors="replace")
    if windows and COLOR:
        os.system("")  # less-code: turns on ANSI colours in a classic Windows console.
    report_only = args.check or not sys.stdin.isatty()
    say(paint("ceh-claude-code-library setup", "1"))
    if args.check:
        note("Report only (--check): nothing is installed, enabled or written.", 0)
    elif report_only:
        note(
            "Report only: there is no terminal to answer, so nothing is installed, enabled or written.",
            0,
        )
        if windows:
            note(
                "Git Bash's mintty may not count as a terminal: run the script from "
                "PowerShell or Windows Terminal to install.",
                0,
            )
    else:
        note("Every install and every write asks you first.", 0)
    platform = {"win32": "windows", "darwin": "darwin"}.get(sys.platform, "linux")
    done: list[str] = []
    failed: list[str] = []  # claude commands that failed: the run exits 1
    heading("Claude Code")
    if not shutil.which("claude"):
        row("bad", "claude", "not on PATH")
        note("Install Claude Code first, then run this again.")
        return 2
    code, out = run(["claude", "--version"])
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", out or "")
    claude_version = tuple(int(x) for x in m.groups()) if m else None
    row("ok", "claude", m.group(0) if m else "version unknown")

    # 2. Marketplace
    markets = claude_json("plugin", "marketplace", "list", "--json")
    if markets is None:
        row("bad", "marketplaces", "`claude plugin marketplace list --json` failed")
        return 1
    has_market = MARKETPLACE in {m.get("name") for m in markets}
    add_cmd = ["claude", "plugin", "marketplace", "add", MARKETPLACE_REPO]
    if has_market:
        row("ok", MARKETPLACE, "marketplace added")
    elif report_only:
        row("todo", MARKETPLACE, "marketplace missing, would add it")
        note(" ".join(add_cmd), 6)
    elif ask(f"Add the {MARKETPLACE} marketplace?", True):
        has_market = run_shown(add_cmd) == 0
        if not has_market:
            failed.append(f"adding the {MARKETPLACE} marketplace")
        row(
            "ok" if has_market else "bad",
            MARKETPLACE,
            "marketplace added" if has_market else "adding failed",
        )
        if has_market:
            done.append(f"marketplace {MARKETPLACE} added")
    if not has_market and not report_only:
        note(
            "Without the marketplace no plugin can be installed, so plugins are skipped."
        )

    # 3. Picks
    entries = claude_json("plugin", "list", "--json")
    if entries is None:
        row("bad", "plugins", "`claude plugin list --json` failed")
        return 1
    cwd = os.path.realpath(os.getcwd())
    states = plugin_states(entries, cwd, windows)
    git_repo = run(["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"])[0] == 0
    core = recommended_core(git_repo)
    heading("Choose plugins")
    note(f"Folder: {cwd}", 2)
    if picks_given:
        picks = picks_given
    elif report_only:
        picks = list(dict.fromkeys([*states, *core]))
    else:
        say()
        picks = pick_plugins(states, core, git_repo)
    note("Picked: " + ", ".join(picks), 2)

    # 4. Tools
    heading("Tools")
    wanted = closure(picks)
    tools = ["python3"] + [
        t
        for t in TOOLS
        if t != "python3"
        and TOOLS[t]["probe"] is not None
        and any(
            t in PLUGINS[p]["requires"] or t in PLUGINS[p]["degrades"] for p in wanted
        )
    ]
    unmet: set[str] = set()
    found: dict[str, bool] = {}
    for tool in tools:
        ok, what = probe(tool)
        row("ok" if ok else "bad", tool, short_version(what) if ok else what, 10)
        cmd = TOOLS[tool]["install"][platform]
        if not ok and cmd and shutil.which(cmd[0]):
            if report_only:
                note("would offer: " + " ".join(cmd))
            elif ask(f"Install {tool} with `{' '.join(cmd)}`?", False):
                if run_shown(cmd) == 0:
                    ok, what = probe(tool)
                    if ok:
                        row("ok", tool, "installed, " + short_version(what), 10)
                        done.append(f"{tool} installed")
                    else:
                        note(
                            f"{tool} installed, but this shell cannot see it yet: open a "
                            "new terminal and run the script again."
                        )
                else:
                    note(f"The {tool} install failed.")
        elif not ok:
            note(f"No known installer here: install {tool} from its own install page.")
        found[tool] = ok
        if not ok:
            unmet.add(tool)

    # 5. Resolve
    plugins, warnings = resolve(picks, unmet, claude_version)
    degraded_by = {t for p in plugins for t in PLUGINS[p]["degrades"]}
    if "gh" in degraded_by and found.get("gh"):
        if run(["gh", "auth", "status"])[0] == 0:
            row("ok", "gh login", "logged in", 10)
        else:
            row("warn", "gh login", "not logged in", 10)
            warnings.append("gh is not logged in: run gh auth login")
    if "git" in degraded_by and found.get("git"):
        for key in ("user.name", "user.email"):
            code, out = run(["git", "config", key])
            if code == 0 and out:
                row("ok", f"git {key.split('.')[1]}", "set", 10)
            else:
                row("warn", f"git {key.split('.')[1]}", "not set", 10)
                warnings.append(
                    f'git {key} is not set: run git config --global {key} "<value>"'
                )

    # 6. Plugins
    heading("Plugins")
    to_install = []
    for name in plugins:
        state = states.get(name)
        plugin_id = f"{name}@{MARKETPLACE}"
        if state and state[0] == "on":
            row("ok", name, f"on ({state[1]})")
        elif state and report_only:
            row("todo", name, f"off, would enable ({state[1]})")
        elif state and has_market:
            # Picking it was the yes.
            ok = (
                run(["claude", "plugin", "enable", plugin_id, "--scope", state[1]])[0]
                == 0
            )
            row(
                "ok" if ok else "bad",
                name,
                f"enabled ({state[1]})" if ok else "enabling failed",
            )
            if ok:
                done.append(f"{name} enabled")
            else:
                failed.append(f"enabling {name}")
        elif report_only:
            row("todo", name, f"not installed, would install ({args.scope})")
        else:
            row("todo", name, "not installed")
            to_install.append(name)
    if to_install and has_market:
        if ask(f"Install {len(to_install)} plugins at {args.scope} scope?", True):
            for name in to_install:
                cmd = ["claude", "plugin", "install", f"{name}@{MARKETPLACE}"]
                ok = run([*cmd, "--scope", args.scope], timeout=300)[0] == 0
                row(
                    "ok" if ok else "bad",
                    name,
                    f"installed ({args.scope})" if ok else "install failed",
                )
                if ok:
                    done.append(f"{name} installed at {args.scope} scope")
                else:
                    failed.append(f"installing {name}")
        else:
            note("Nothing installed.")

    # 7. Settings
    heading("Skill listing budget")
    note(
        "With many skills installed, Claude Code drops the descriptions of the least-used ones, "
        "and a skill without its description is not matched to a request.",
        2,
    )
    path = settings_path()
    settings = read_settings(path)
    if settings is None:
        row("bad", "settings.json", f"{path} cannot be read as JSON, nothing written")
        return 1
    merged = merge_budget(settings, BUDGET)
    current = settings.get(BUDGET_KEY, "not set, default 0.01")
    if merged is None:
        row("ok", BUDGET_KEY, f"{current}, at least {BUDGET}")
    elif report_only:
        row("todo", BUDGET_KEY, f"{current}, would set {BUDGET}")
    elif ask(f"Set {BUDGET_KEY} to {BUDGET} in {path}?", True):
        write_settings(path, merged)
        row("ok", BUDGET_KEY, f"set to {BUDGET}")
        done.append(f"{BUDGET_KEY} set to {BUDGET}")
    else:
        row("todo", BUDGET_KEY, f"{current}, left as it is")
    if os.environ.get(BUDGET_VAR):
        note(
            f"{BUDGET_VAR} is set to {os.environ[BUDGET_VAR]} and may override the fraction. "
            "Run /doctor in Claude Code to see the budget in effect."
        )

    if "ceh-every-session" in plugins:
        heading("Statusline")
        note("The usage-limit guard reads its quota from the statusline.", 2)
        settings = read_settings(settings_path())
        if settings is None:
            row("bad", "settings.json", f"{settings_path()} cannot be read as JSON")
            return 1
        if settings.get("statusLine"):
            state = statusline_state(
                settings,
                dict(os.environ),
                Path.home() / ".claude/statusline",
                time.time(),
            )
            kind = {"fed": "ok", "disabled": "warn"}.get(state, "bad")
            detail = {
                "fed": "set, and the guard gets readings",
                "disabled": "set, but its export is turned off",
            }.get(state, "set, but the guard gets no readings")
            row(kind, "statusLine", detail)
            if state == "not fed":
                note(f"See {STATUSLINE_README}")
        elif report_only:
            row(
                "todo",
                "statusLine",
                f"not set, would offer statusline-hook {STATUSLINE_TAG}",
            )
        elif ask(f"Install the statusline-hook statusline ({STATUSLINE_TAG})?", False):
            result = install_statusline(windows)
            row("ok" if result.startswith("installed") else "bad", "statusLine", result)
            if result.startswith("installed"):
                done.append(f"statusline-hook {STATUSLINE_TAG} installed")

    # 8. Summary
    heading("Summary")
    for line in done:
        row("ok", line)
    for line in failed:
        row("bad", f"Failed: {line}")
    if unmet:
        row("bad", "Tools missing: " + ", ".join(sorted(unmet)))
    if not done and not unmet and not warnings and not failed:
        row("ok", "Everything is in place.")
    for line in warnings:
        # "<plugin>: <what>" reads as a heading and its wrapped detail.
        head, _, rest = line.partition(": ")
        row("warn", head if rest else line)
        if rest:
            note(rest)
    if done:
        say()
        note("Next: run /reload-plugins in any open Claude Code session.", 2)
    elif report_only and not args.check:
        say()
        note(
            "To install, run this again from PowerShell or Windows Terminal."
            if windows
            else "To install, run this again from a terminal.",
            2,
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
