#!/usr/bin/env python3
"""PreToolUse hook: stop the orchestrator doing delegated work itself.

Matches Edit|Write|MultiEdit|NotebookEdit|Agent. The session is the orchestrator only when the
lock file `load-orchestrator.py` writes names it, by CLAUDE_PID or by session id. Then it denies
an Agent call, and a file edit inside the repository other than the orchestration file, a
handoff, the decision log and `.gitignore`. Every other session is left alone.

Fails open: anything unexpected allows the call, because a guard that blocked ordinary sessions
on a bad temp file would cost more than it saves.
"""

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

REASON = (
    "This session is the orchestrator of this repository, so it edits no project file and starts "
    "no subagent. Start a worker for this work, as orchestrate-worker-sessions step 4 says. A "
    "worker may start subagents for its own task, so a request for subagents, such as a review on "
    "another model, goes into the worker's brief. To do the work in this session anyway, the user "
    "sets CEH_DISABLED_HOOKS=orchestrator-scope-guard. With no user present, start no worker: "
    "stop and report this."
)


def repo_root(cwd: Path) -> Path:
    """The nearest folder holding a .git entry, so a worktree is its own root.

    Copied from load-orchestrator.py, which is canonical (docs/CROSS_REFERENCES.md)."""
    for d in (cwd, *cwd.parents):
        if (d / ".git").exists():
            return d
    return cwd


def inside(path: str, folder: str) -> bool:
    return path == folder or path.startswith(folder + os.sep)


def main() -> None:
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    # The loader off, a worker, or a headless run: such a session never takes the lock, so a
    # stale lock whose pid it reuses must not guard it.
    if {Path(__file__).stem, "load-orchestrator"} & set(disabled):
        return
    if os.environ.get("CEH_ORCHESTRATION_WORKER"):
        return
    if os.environ.get("CLAUDE_CODE_SESSION_ATTENDED") == "0":
        return

    payload = json.load(sys.stdin)
    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    root = os.path.normcase(str(repo_root(cwd)))
    # The lock path, as load-orchestrator.py writes it.
    lock = (
        Path(tempfile.gettempdir())
        / "ceh-session-orchestration"
        / f"{hashlib.sha256(root.encode()).hexdigest()[:16]}.json"
    )
    held = json.loads(lock.read_text(encoding="utf-8"))
    pid, sid = os.environ.get("CLAUDE_PID", ""), payload.get("session_id") or ""
    is_me = (pid and isinstance(held.get("pid"), int) and str(held["pid"]) == pid) or (
        sid and held.get("sessionId") == sid
    )
    if not is_me:
        return

    if payload.get("tool_name") != "Agent":
        ti = payload["tool_input"]
        path = ti.get(
            "notebook_path" if payload["tool_name"] == "NotebookEdit" else "file_path"
        )
        if not isinstance(path, str) or not path:
            return
        target = os.path.normcase(str((cwd / path).resolve()))

        def at(*parts: str) -> str:
            return os.path.normcase(os.path.join(root, *parts))

        if (
            not inside(target, root)
            or inside(target, at(".agents_workspace", "orchestration"))
            or inside(target, at(".agents_workspace", "handoff"))
            or target in (at(".agents_workspace", "DECISION_LOG.md"), at(".gitignore"))
        ):
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
