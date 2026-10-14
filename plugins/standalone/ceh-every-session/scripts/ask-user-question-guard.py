#!/usr/bin/env python3
"""PreToolUse hook: deny AskUserQuestion, steer to a closing decision block.

The dialog holds the turn open, so a background task or subagent that finishes
while it waits goes unread until the user answers. A decision block ends the
turn and asks the same question. Fails open: anything unexpected allows the call.
"""

import json
import os
import sys
from pathlib import Path

REASON = (
    "Blocked: do not ask through AskUserQuestion while ceh-every-session is enabled. "
    "Finish what you can, then end the reply with the question as a decision block: "
    "`**Decision: <question>**` on its own line, then 2 to 4 numbered options, the "
    'recommended one first and marked "(recommended)". Several blocks may follow one '
    "another, and nothing comes after the last. The user answers in their next message."
)


def main():
    # Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if payload.get("tool_name") != "AskUserQuestion":
        sys.exit(0)

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON,
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
