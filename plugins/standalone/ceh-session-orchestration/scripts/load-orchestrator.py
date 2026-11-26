#!/usr/bin/env python3
"""SessionStart hook: make the session an orchestrator by loading its standard.

Wired on startup|resume|clear|compact, so the standard is loaded again after compaction.
SessionStart never fires inside a subagent, so a subagent is never made an orchestrator. Reads no
stdin field and writes no file, so a second run changes nothing.
"""

import json
import os
import sys
from pathlib import Path

# Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
if Path(__file__).stem in os.environ.get("CEH_DISABLED_HOOKS", "").replace(
    " ", ""
).split(","):
    sys.exit(0)
# A worker session: the orchestrator starts every worker with this variable set.
if os.environ.get("CEH_ORCHESTRATION_WORKER"):
    sys.exit(0)

CONTEXT = (
    "Before answering the user, invoke the Skill tool with "
    'skill="ceh-session-orchestration:orchestrate-worker-sessions": this session is an '
    "orchestrator of worker sessions."
)

print(
    json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": CONTEXT,
            }
        }
    )
)
