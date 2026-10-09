#!/usr/bin/env python3
"""PreToolUse hook: deny file edits on the default branch, so work branches first.

Matches Edit|Write|MultiEdit|NotebookEdit. Files outside a git work tree pass
(scratchpads, ~/.claude config). CEH_BRANCH_GUARD=off disables it, for the
times editing the default branch in place is what the user asked for.

Fails open: anything unexpected allows the edit, because a guard that blocked
work on its own bugs would cost more than it saves.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def git(cwd, *args):
    out = subprocess.run(
        ["git", "-C", cwd, *args], capture_output=True, text=True, timeout=5
    )
    return out.stdout.strip() if out.returncode == 0 else ""


def denial_number(payload):
    """This hook's denial count in this session, 1 on the first.

    Identical deny blocks push the model into repetition loops, so after the
    third the caller sends one line carrying this ordinal instead.
    """
    session = payload.get("session_id") or "default"
    state = Path(tempfile.gettempdir()) / f"ceh-denials-{Path(__file__).stem}-{session}"
    try:
        n = int(state.read_text(encoding="utf-8")) + 1
    except (OSError, ValueError):
        n = 1
    try:
        state.write_text(str(n), encoding="utf-8")
    except OSError:
        pass
    return n


def main():
    # Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    if os.environ.get("CEH_BRANCH_GUARD", "").strip().lower() == "off":
        return

    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return

    # A new file may sit in a directory that does not exist yet: walk up to one that does.
    cwd = os.path.dirname(os.path.abspath(path))
    while cwd and not os.path.isdir(cwd):
        parent = os.path.dirname(cwd)
        cwd = "" if parent == cwd else parent
    if not cwd or git(cwd, "rev-parse", "--is-inside-work-tree") != "true":
        return

    branch = git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    if not branch or branch == "HEAD":  # detached or unborn
        return

    default = git(cwd, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    default = default.removeprefix("refs/remotes/origin/")
    if branch not in (default, "main", "master"):
        return

    n = denial_number(payload)
    if n <= 3:
        reason = (
            f"On the default branch ({branch}). Create a feature branch first "
            "(ceh-git-workflow:branch: feat/ fix/ chore/ docs/ test/ refactor/), then retry "
            "this edit. Uncommitted work carries over via 'git checkout -b <name>'. If the "
            f"user explicitly asked to edit {branch} in place, tell them to set "
            "CEH_BRANCH_GUARD=off."
        )
    else:
        reason = (
            f"Denied again (denial {n} this session): still on {branch}. Branch first, or "
            "the user sets CEH_BRANCH_GUARD=off."
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


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail open
        pass
    sys.exit(0)
