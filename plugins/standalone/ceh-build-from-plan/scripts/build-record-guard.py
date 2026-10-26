#!/usr/bin/env python3
"""PreToolUse hook: deny a plan's new "Built Phase" Record line unless implement-from-plan ran.

Matches Edit|Write|MultiEdit. A Built Phase line in product/plans/*.md is the evidence that a phase
was built the way implement-from-plan builds it, so writing one by hand, without that skill started
in this session, records a build its procedure never ran. CEH_BUILD_RECORD_GUARD=off disables it.

Fails open: anything unexpected allows the edit, because a guard that blocked work on its own bugs
would cost more than it saves.
"""

import json
import os
import re
import sys
from pathlib import Path

BUILT = re.compile(r"^- \d{4}-\d{2}-\d{2} Built Phase ", re.M)
# The records a started skill leaves, a Skill tool call or a user's slash command, never a mention.
STARTED = re.compile(
    r'"skill":\s*"ceh-build-from-plan:implement-from-plan"'
    r"|<command-name>/ceh-build-from-plan:implement-from-plan</command-name>"
)
REASON = (
    "A Built Phase line records a phase built by ceh-build-from-plan:implement-from-plan, which "
    "has not run in this session. Invoke the Skill tool with "
    'skill="ceh-build-from-plan:implement-from-plan" and build the phase through it. '
    "CEH_BUILD_RECORD_GUARD=off turns this guard off."
)


def old_text(tool: str, ti: dict, path: str) -> str:
    """The text the edit replaces, so Built lines already there do not count as new."""
    if tool == "Write":
        p = Path(path)
        return p.read_text(encoding="utf-8") if p.is_file() else ""
    if tool == "MultiEdit":
        return "".join(e.get("old_string", "") for e in ti.get("edits", []))
    return ti.get("old_string", "")


def main() -> None:
    # Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    if os.environ.get("CEH_BUILD_RECORD_GUARD", "").strip().lower() == "off":
        return

    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {})
    path = ti.get("file_path", "")
    if "/product/plans/" not in path.replace("\\", "/") or not path.endswith(".md"):
        return
    new = ti.get("new_string") or ti.get("content") or ""
    new += "".join(e.get("new_string", "") for e in ti.get("edits", []))
    if len(BUILT.findall(new)) <= len(BUILT.findall(old_text(tool, ti, path))):
        return
    transcript = Path(payload["transcript_path"]).read_text(encoding="utf-8")
    if STARTED.search(transcript):
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": REASON,
                }
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail open
        pass
    sys.exit(0)
