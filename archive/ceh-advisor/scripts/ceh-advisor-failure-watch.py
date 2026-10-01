#!/usr/bin/env python3
"""ceh-advisor-failure-watch.py - PostToolUse hook (matcher: Bash)

Counts consecutive failed Bash tool calls in the session. When the count
reaches the threshold, feeds a message back to Claude (exit 2) instructing
it to stop iterating and consult ceh-advisor to re-examine the diagnosis.

Advisory, so it fails open: a crash here exits non-zero and Claude Code
surfaces the hook error, but no tool call is blocked.

Config (env or defaults):
  CEH_ADVISOR_FAIL_THRESHOLD  consecutive failures before firing (default 3)
"""

import json
import os
import re
import sys
import tempfile
from pathlib import Path

# Failure detection is heuristic because the PostToolUse payload shape has
# varied across Claude Code versions - extend this on false negatives.
FAILURE_SIGNS = re.compile(
    r"Exit code:? [1-9]|exited with code [1-9]|command not found"
    r"|Traceback \(most recent call last\)|FAILED|AssertionError|npm ERR!"
)


def main() -> None:
    payload = json.loads(sys.stdin.read())
    if payload.get("tool_name") != "Bash":
        return

    session_id = payload.get("session_id") or "default"
    threshold = int(os.environ.get("CEH_ADVISOR_FAIL_THRESHOLD", "3"))
    state = Path(tempfile.gettempdir()) / f"ceh-advisor-failcount-{session_id}"

    response = payload.get("tool_response") or payload.get("tool_result") or {}
    is_error = isinstance(response, dict) and response.get("is_error") is True
    failed = is_error or bool(FAILURE_SIGNS.search(json.dumps(response)))

    if not failed:
        state.unlink(missing_ok=True)  # success resets the streak
        return

    count = 0
    if state.is_file():
        try:
            count = int(state.read_text(encoding="utf-8").strip())
        except ValueError:
            count = 0
    count += 1

    if count < threshold:
        state.write_text(str(count), encoding="utf-8")
        return

    # Reset so we don't fire on every subsequent failure
    state.unlink(missing_ok=True)
    print(
        f"ceh-advisor guard: {count} consecutive failed commands. Stop iterating on the "
        "current fix. Invoke the ceh-advisor subagent via the Task tool with a handoff block "
        "(Situation / what you've tried / current diagnosis / relevant files) and have it "
        "challenge the DIAGNOSIS, not just the patch, before attempting another fix.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - report, never block a tool call
        # Advisory hook: surface one readable line instead of a traceback, and
        # exit 1 (visible warning) rather than 2 (which would block the call).
        print(f"ceh-advisor failure-watch disabled this call: {exc}", file=sys.stderr)
        sys.exit(1)
