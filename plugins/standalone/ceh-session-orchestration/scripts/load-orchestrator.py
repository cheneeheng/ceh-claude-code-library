#!/usr/bin/env python3
"""SessionStart hook: make the session an orchestrator by loading its standard.

Wired on startup|resume|clear|compact, so the standard is loaded again after compaction.
SessionStart never fires inside a subagent, so a subagent is never made an orchestrator.

One orchestrator per repository: the session this hook makes an orchestrator writes a lock file
naming it, and while that session runs, the hook loads no standard in another session there and
says so. Reads `cwd` and `session_id` from stdin, and the running sessions from
`claude agents --json`. When the listing cannot be read, the standard still loads.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
if Path(__file__).stem in os.environ.get("CEH_DISABLED_HOOKS", "").replace(
    " ", ""
).split(","):
    sys.exit(0)
# A worker session: the orchestrator starts every worker with this variable set.
if os.environ.get("CEH_ORCHESTRATION_WORKER"):
    sys.exit(0)

SKILL = "ceh-session-orchestration:orchestrate-worker-sessions"
DEFAULT_MAX_WORKERS = 5


def emit(message: str, context: str) -> None:
    # additionalContext reaches only the model, at its first request, so the user is told in
    # systemMessage.
    print(
        json.dumps(
            {
                "systemMessage": message,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                },
            }
        )
    )


def repo_root(cwd: Path) -> Path:
    """The nearest folder holding a .git entry, so a worktree is its own root."""
    for d in (cwd, *cwd.parents):
        if (d / ".git").exists():
            return d
    return cwd


def list_sessions() -> list[dict]:
    """The running sessions. Raises RuntimeError with the reason they could not be read."""
    exe = shutil.which("claude")
    if not exe:
        raise RuntimeError("claude is not on PATH")
    try:
        r = subprocess.run(
            [exe, "agents", "--json"], capture_output=True, text=True, timeout=5
        )
    except (OSError, subprocess.SubprocessError) as e:
        raise RuntimeError(f"claude agents --json failed ({e})") from None
    if r.returncode:
        raise RuntimeError(f"claude agents --json exited {r.returncode}")
    try:
        sessions = json.loads(r.stdout)
    except ValueError:
        raise RuntimeError("claude agents --json printed no JSON") from None
    if not isinstance(sessions, list):
        raise RuntimeError("claude agents --json printed no list")
    return [
        s
        for s in sessions
        if isinstance(s, dict)
        and isinstance(s.get("pid"), int)
        and isinstance(s.get("startedAt"), int)
    ]


try:
    stdin = json.loads(sys.stdin.read() or "{}")
except ValueError:
    stdin = {}
if not isinstance(stdin, dict):
    stdin = {}
cwd = Path(stdin.get("cwd") or os.getcwd()).resolve()
my_id = stdin.get("session_id") or ""
my_pid = os.environ.get("CLAUDE_PID", "")
root = os.path.normcase(str(repo_root(cwd)))
lock = (
    Path(tempfile.gettempdir())
    / "ceh-session-orchestration"
    / f"{hashlib.sha256(root.encode()).hexdigest()[:16]}.json"
)
notes = []

try:
    sessions = list_sessions()
except RuntimeError as e:
    sessions = []
    notes.append(
        f"The check for another orchestrator in this repository could not run: {e}."
    )

try:
    held = json.loads(lock.read_text(encoding="utf-8"))
except (OSError, ValueError):
    held = None
if isinstance(held, dict) and isinstance(held.get("startedAt"), int):
    # Live: the lock's process still runs. A pid reused by a later process started after the
    # lock was written, so its startedAt is newer. A lock written with no pid (no CLAUDE_PID, and
    # the session not listed yet) is matched by its session id.
    live = next(
        (
            s
            for s in sessions
            if (
                s["pid"] == held.get("pid")
                if held.get("pid") is not None
                else held.get("sessionId") and s.get("sessionId") == held["sessionId"]
            )
            and s["startedAt"] <= held["startedAt"]
        ),
        None,
    )
    if live and str(live["pid"]) != my_pid and live.get("sessionId") != my_id:
        emit(
            f"ceh-session-orchestration: {live.get('name') or 'another session'} "
            f"(pid {live['pid']}) is already the orchestrator of this repository, so this "
            "session did not load the orchestrator standard. To make this session the "
            "orchestrator, close that one, then run /clear here.",
            "This session is not an orchestrator, because another session orchestrates this "
            f"repository: do not invoke {SKILL}.",
        )
        sys.exit(0)

me = next(
    (
        s
        for s in sessions
        if (my_pid and str(s["pid"]) == my_pid)
        or (my_id and s.get("sessionId") == my_id)
    ),
    None,
)
# Not listed yet, as at startup: now is after the process started, so the lock stays live.
me = me or {
    "pid": int(my_pid) if my_pid.isdigit() else None,
    "startedAt": int(time.time() * 1000),
    "sessionId": my_id,
}
# less-code: read, then write, with no file lock; add an exclusive create if two sessions
# started in the same second are ever seen to both become orchestrators.
try:
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(
        json.dumps({k: me.get(k) for k in ("pid", "startedAt", "sessionId", "name")}),
        encoding="utf-8",
    )
except OSError as e:
    notes.append(f"Could not save which session is the orchestrator ({e}).")

raw = os.environ.get("CEH_ORCHESTRATION_MAX_WORKERS", "").strip()
try:
    max_workers = int(raw) if raw else DEFAULT_MAX_WORKERS
except ValueError:
    max_workers = 0
if max_workers < 1:
    notes.append(
        f"CEH_ORCHESTRATION_MAX_WORKERS={raw} is not a whole number of at least 1, so the "
        f"limit is {DEFAULT_MAX_WORKERS}."
    )
    max_workers = DEFAULT_MAX_WORKERS

emit(
    " ".join(
        [
            "ceh-session-orchestration: this session is the orchestrator. Send any message to "
            "load it and take over running workers.",
            *notes,
        ]
    ),
    f'Before answering the user, invoke the Skill tool with skill="{SKILL}": this session is '
    "an orchestrator of worker sessions. If your start prompt says you are a worker session, "
    "ignore this and follow your start prompt. This orchestrator runs at most "
    f"{max_workers} workers at once (CEH_ORCHESTRATION_MAX_WORKERS).",
)
