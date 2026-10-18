#!/usr/bin/env python3
"""PreToolUse hook: deny creating a git branch until ceh-git-workflow:branch is loaded.

Matches Bash. A command that creates a branch (git checkout -b/-B, git switch
-c/-C, git branch <name>, git worktree add -b) is denied while the session's
transcript holds no Skill call for ceh-git-workflow:branch, so the name follows
the skill rather than memory. CEH_DISABLED_HOOKS=branch-skill-gate disables it.

Fails open: anything unexpected allows the command.
"""

import json
import os
import re
import sys
from pathlib import Path

SKILL = "ceh-git-workflow:branch"
CREATES_BRANCH = re.compile(
    r"\bgit\s+(?:-C\s+\S+\s+)?"
    r"(?:checkout\s+-[bB]|switch\s+(?:-[cC]|--create|--force-create)"
    r"|worktree\s+add\s+(?:\S+\s+)*-[bB]"
    r"|branch[ \t]+(?!-)[^\s;&|]+)"
)


def skill_loaded(transcript, skill):
    """True when the transcript has a Skill tool call whose skill is exactly `skill`."""
    with open(transcript, encoding="utf-8") as f:
        for line in f:
            if '"Skill"' not in line or skill not in line:
                continue
            content = (json.loads(line).get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if (
                    block.get("type") == "tool_use"
                    and block.get("name") == "Skill"
                    and (block.get("input") or {}).get("skill") == skill
                ):
                    return True
    return False


def main():
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    payload = json.load(sys.stdin)
    command = (payload.get("tool_input") or {}).get("command") or ""
    transcript = payload.get("transcript_path")
    if not CREATES_BRANCH.search(command) or not transcript:
        return
    if skill_loaded(transcript, SKILL):
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"This command creates a branch. Invoke the Skill tool with "
                        f'skill="{SKILL}" first, name the branch by it, then retry.'
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
