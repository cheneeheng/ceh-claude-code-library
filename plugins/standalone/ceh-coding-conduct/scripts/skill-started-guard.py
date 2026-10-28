#!/usr/bin/env python3
"""PreToolUse hook: deny a call whose owning skill has not been started in this session.

Matches the tools its RULES name. Each rule names a moment (a command, a file) and the skills that
own it; the call is denied until one of them was started, by a Skill tool call or a user's slash
command, never a mention. A parent skill that only names a child ("following X", "X sets out how")
does not count: that wording is how the child got skipped. CEH_SKILL_STARTED_GUARD=off disables it.

Each plugin ships this script with only its own rows in RULES, so it works installed alone.

Fails open: anything unexpected allows the call, because a guard that blocked work on its own bugs
would cost more than it saves.
"""

import json
import os
import re
import sys
from pathlib import Path

# (tools, (what the rule matches, pattern), owning skills: any one started is enough)
RULES = [
    (
        {"Write"},
        ("new_source", re.compile(r"\.(py|ts|tsx|js)$")),
        ["ceh-coding-conduct:sketch-design"],
    ),
]


def started(skill: str, transcript: str) -> bool:
    name = re.escape(skill)
    return bool(
        re.search(rf'"skill":\s*"{name}"', transcript)
        or re.search(rf"<command-name>/{name}</command-name>", transcript)
    )


def subject(kind: str, ti: dict, cwd: str) -> str:
    """The text a rule matches against, or "" when the rule does not apply."""
    if kind == "command":
        return ti.get("command", "")
    path = ti.get("file_path", "").replace("\\", "/")
    root = cwd.replace("\\", "/").rstrip("/")
    if root and os.path.isabs(path) and not path.lower().startswith(root.lower() + "/"):
        return ""  # scratch files outside the project are nobody's deliverable
    if kind == "path":
        return path
    # new_source: a new code file outside tests and scripts, the moment sketch-design owns
    skip = re.search(
        r"(^|/)(tests?|__tests__|scripts)/|(^|/)test_|_test\.|\.(test|spec)\.", path
    )
    return "" if skip or Path(path).exists() else path


def main() -> None:
    # Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    if os.environ.get("CEH_SKILL_STARTED_GUARD", "").strip().lower() == "off":
        return

    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {})
    transcript = None
    for tools, (kind, pattern), skills in RULES:
        if tool not in tools or not pattern.search(
            subject(kind, ti, payload.get("cwd", ""))
        ):
            continue
        if transcript is None:
            transcript = Path(payload["transcript_path"]).read_text(encoding="utf-8")
        if any(started(s, transcript) for s in skills):
            continue
        reason = (
            f"This {tool} call is owned by {' or '.join(skills)}, which has not been started "
            "in this session; a skill named inside another skill's steps still has to be "
            f'loaded. Invoke the Skill tool with skill="{skills[0]}" first, then retry. '
            "CEH_SKILL_STARTED_GUARD=off turns this guard off."
        )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail open
        pass
    sys.exit(0)
