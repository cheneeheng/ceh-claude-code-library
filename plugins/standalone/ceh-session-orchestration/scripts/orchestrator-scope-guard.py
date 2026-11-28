#!/usr/bin/env python3
"""PreToolUse and UserPromptSubmit hook: stop the orchestrator doing delegated work itself.

PreToolUse matches Edit|Write|MultiEdit|NotebookEdit|Agent|Read|Grep|Glob|Bash|PowerShell. The
session is the orchestrator only when the lock file `load-orchestrator.py` writes names it, by
CLAUDE_PID or by session id. Then it denies an Agent call, and a file edit inside the repository
other than the orchestration file, a handoff, the decision log, the backlog and `.gitignore`.

It also counts the orchestrator's Read, Grep, Glob, Bash and PowerShell calls on each incoming
message, recognising it as well by any lock whose sessionId matches, since its cwd may sit in a
nested repository such as `.agents_workspace`. Past LIMIT it denies each counted call, and the
same call run again passes once. UserPromptSubmit, which fires on typed prompts, messages from
other sessions and subagent reports, starts the count again. Every other session is left alone.

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

# Set from 124 turns of 13 past orchestrator sessions: every turn that did a worker's task
# passed 10, and every worker start came within 5.
LIMIT = 10
COUNTED = ("Read", "Grep", "Glob", "Bash", "PowerShell")
COUNT_REASON = (
    "This session is the orchestrator, and this is call {n} of its Read, Grep, Glob, Bash or "
    "PowerShell calls on this message, past its limit of {limit}, so the task has outgrown a look. "
    "Stop, and start a worker with what you have found so far, as orchestrate-worker-sessions "
    "step 4 says. Run a call again only when it is a worker start or the orchestrator's own "
    "bookkeeping: the same call run again passes once. With no user present, start no worker: "
    "stop and report this. The user can turn this guard off with "
    "CEH_DISABLED_HOOKS=orchestrator-scope-guard."
)


def read_lock(path: Path) -> dict | None:
    try:
        held = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return held if isinstance(held, dict) else None


def count(folder: Path, sid: str, tool: str, tool_input: dict) -> str | None:
    """Count one call and return a denial reason past LIMIT, or None.

    The count is the writer's own offset after its append, not the file size, so whichever
    process wrote byte LIMIT + 1 is denied, whatever a parallel batch does."""
    folder.mkdir(parents=True, exist_ok=True)
    # less-code: on Windows an append seeks to the end, then writes, so two parallel calls may
    # land on one byte and both see the same count: two denials, never none. A lock file around
    # the append is the upgrade path. Files of ended sessions stay in the temp folder, a few
    # bytes each, for the OS to clean, and the loader may delete them when it takes the lock.
    with open(folder / f"calls-{sid}", "ab", buffering=0) as f:
        f.write(b"x")
        n = f.tell()
    if n <= LIMIT:
        return None
    # A retry that rewords only its description, timeout or background flag still matches.
    key = (
        [tool, tool_input.get("command")]
        if tool in ("Bash", "PowerShell")
        else [tool, tool_input]
    )
    digest = hashlib.sha256(json.dumps(key, sort_keys=True).encode()).hexdigest()[:16]
    marker = folder / f"denied-{sid}-{digest}"
    if marker.exists():
        marker.unlink()
        return None
    marker.touch()
    return COUNT_REASON.format(n=n, limit=LIMIT)


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
    folder = Path(tempfile.gettempdir()) / "ceh-session-orchestration"
    sid = payload.get("session_id") or ""
    # The count's files are named by session id alone, so the reset needs no cwd.
    if payload.get("hook_event_name") == "UserPromptSubmit":
        for path in (folder / f"calls-{sid}", *folder.glob(f"denied-{sid}-*")):
            path.unlink(missing_ok=True)
        return

    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
    root = os.path.normcase(str(repo_root(cwd)))
    # The lock path, as load-orchestrator.py writes it.
    lock = (
        Path(tempfile.gettempdir())
        / "ceh-session-orchestration"
        / f"{hashlib.sha256(root.encode()).hexdigest()[:16]}.json"
    )
    held = read_lock(lock) or {}
    pid = os.environ.get("CLAUDE_PID", "")
    is_me = (pid and isinstance(held.get("pid"), int) and str(held["pid"]) == pid) or (
        sid and held.get("sessionId") == sid
    )

    tool = payload.get("tool_name")
    if tool in COUNTED:
        # A subagent's call is not the orchestrator's. Any lock with this session id also counts,
        # by session id only, since a stale lock of another repository may hold a reused pid.
        if payload.get("agent_id") or not (
            is_me
            or (
                sid
                and any(
                    (read_lock(p) or {}).get("sessionId") == sid
                    for p in folder.glob("*.json")
                )
            )
        ):
            return
        reason = count(folder, sid, tool, payload["tool_input"])
        if reason:
            deny(reason)
        return

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
            or target
            in (
                at(".agents_workspace", "DECISION_LOG.md"),
                at(".agents_workspace", "BACKLOG.md"),
                at(".gitignore"),
            )
        ):
            return
    deny(REASON)


def deny(reason: str) -> None:
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
