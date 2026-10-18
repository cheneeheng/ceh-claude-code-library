#!/usr/bin/env python3
"""PreToolUse hook: deny editing outside product/ while a diagnosed fix note is
open and ceh-testing:test-a-bug-fix is not loaded.

Matches Edit|Write|MultiEdit|NotebookEdit. A fix note is a product/fixes/*.md
file with `status: diagnosed`, written by ceh-coding-conduct:find-root-cause.
Once one appears in the session's transcript (read, attached, or written), the
first edit to any file outside product/ and .agents_workspace/ is denied until
the transcript holds a Skill call for ceh-testing:test-a-bug-fix, so the fix
starts from a failing test. CEH_DISABLED_HOOKS=bug-fix-skill-gate disables it.

Fails open: anything unexpected allows the edit.
"""

import json
import os
import re
import sys
from pathlib import Path

SKILL = "ceh-testing:test-a-bug-fix"
FIX_NOTE = re.compile(r"product[\\/]+fixes[\\/]+[^\"\s]+\.md")
EXEMPT = re.compile(r"[\\/](?:product|\.agents_workspace)[\\/]")


def scan(transcript):
    """(a diagnosed fix note appears, the skill was loaded) for the transcript."""
    note = False
    with open(transcript, encoding="utf-8") as f:
        for line in f:
            if not note and "status: diagnosed" in line and FIX_NOTE.search(line):
                note = True
            if '"Skill"' in line and SKILL in line:
                content = (json.loads(line).get("message") or {}).get("content")
                for block in content if isinstance(content, list) else []:
                    if (
                        block.get("type") == "tool_use"
                        and block.get("name") == "Skill"
                        and (block.get("input") or {}).get("skill") == SKILL
                    ):
                        return note, True
    return note, False


def main():
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    transcript = payload.get("transcript_path")
    if not path or not transcript or EXEMPT.search(os.path.abspath(path)):
        return
    note, loaded = scan(transcript)
    if not note or loaded:
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "A diagnosed fix note (product/fixes/) is open in this session. "
                        f'Invoke the Skill tool with skill="{SKILL}" before the first '
                        "edit, then retry."
                    ),
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
