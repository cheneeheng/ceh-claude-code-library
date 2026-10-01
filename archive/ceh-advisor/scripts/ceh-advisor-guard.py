#!/usr/bin/env python3
"""ceh-advisor-guard.py - PreToolUse hook (matcher: Bash)

Hard-trigger backstop for ceh-advisor. Denies destructive bash commands
unless a fresh advisor acknowledgement exists, forcing the main session
to consult ceh-advisor before irreversible actions.

Protocol:
  1. Destructive command detected, no fresh ack -> deny with instructions.
  2. Main session invokes ceh-advisor (Task tool) with a handoff block.
  3. Main session writes the advisor's one-line verdict into the ack file
     (this doubles as an audit trail).
  4. Re-run the command; ack is fresh -> allowed.

Fails CLOSED. Allow and deny are both signalled the documented way - JSON on
stdout with exit 0 - so a deny always carries a readable reason. An unparseable
payload denies rather than allows, because a guard that cannot tell whether a
command is destructive must not wave it through.

Exit 2 is reserved for the backstop: hooks.json appends `|| exit 2`, so a
missing interpreter (127) or an unhandled crash (1) still blocks the command.
Without that suffix Claude Code would treat those exits as non-blocking and
the guard would fail open exactly when it is most broken.

Config (env or defaults):
  CEH_ADVISOR_ACK_TTL   seconds an ack stays valid (default 900 = 15 min)
  CEH_ADVISOR_PATTERNS  extra patterns file, one regex per line (optional)
"""

import json
import os
import re
import sys
import time
from pathlib import Path

# Destructive patterns, one regex per line. Ported from the POSIX ERE the shell
# version used; [[:space:]] became \s. Semantics are unchanged except for the
# `git push` line: the old `.*(--force|\s-f(\s|$))` never matched a bare
# `git push -f origin main`, because the `\s` before `-f` needed a space the
# preceding `\s` had already consumed. The `(.*\s)?` prefix now lets the flag sit
# in first position or later, and both flags are anchored by `(\s|$)` so
# `git push origin hotfix-f` stays allowed.
PATTERNS = r"""
rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\s
git\s+push\s+(.*\s)?(--force|-f)(\s|$)
git\s+reset\s+--hard
git\s+clean\s+-[a-zA-Z]*f
git\s+branch\s+-D
DROP\s+(TABLE|DATABASE|SCHEMA)
TRUNCATE\s+TABLE
(prisma|alembic|rails|django-admin|manage\.py|npx\s+prisma)\s+.*migrate
terraform\s+(apply|destroy)
kubectl\s+delete
docker\s+(system|volume|image)\s+prune
aws\s+s3\s+(rm|rb)
"""


def emit(decision: str, reason: str, system_message: str | None = None) -> None:
    out: dict = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }
    if system_message:
        out["systemMessage"] = system_message
    print(json.dumps(out))


def deny(reason: str, system_message: str) -> None:
    """Deny via JSON on stdout + exit 0 - the documented PreToolUse path, which
    carries a readable reason. Exit 2 is NOT used here: it is reserved for the
    crash/no-interpreter backstop that hooks.json bolts on with `|| exit 2`."""
    emit("deny", reason, system_message)
    sys.exit(0)


def consult_protocol(ttl: int) -> str:
    return (
        "This command is irreversible. Before re-running it: (1) invoke the ceh-advisor "
        "subagent via the Task tool with a full handoff block (Situation / Options considered / "
        "Leaning toward / Relevant files) covering WHY this command is necessary and its blast "
        "radius; (2) write the advisor's one-line verdict into .claude/.ceh-advisor-ack; "
        f"(3) re-run the command. The ack expires after {ttl} seconds."
    )


def main() -> None:
    raw = sys.stdin.read()
    ttl = int(os.environ.get("CEH_ADVISOR_ACK_TTL", "900"))

    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        deny(
            "ceh-advisor guard could not parse the hook payload - failing closed.",
            "The ceh-advisor guard received an unreadable PreToolUse payload and denied the "
            "command rather than risk allowing a destructive one. If this repeats, the hook "
            "payload shape has changed: report it, and disable the hook in hooks.json to unblock.",
        )
        return

    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        sys.exit(0)

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    ack_file = project_dir / ".claude" / ".ceh-advisor-ack"

    patterns = [p for p in PATTERNS.strip().splitlines() if p.strip()]
    extra = os.environ.get("CEH_ADVISOR_PATTERNS") or str(
        project_dir / ".claude" / "ceh-advisor-patterns.txt"
    )
    if Path(extra).is_file():
        for line in Path(extra).read_text(encoding="utf-8").splitlines():
            if line.strip():
                # Accept POSIX ERE classes from pre-Python pattern files.
                patterns.append(line.replace("[[:space:]]", r"\s"))

    matched = next((p for p in patterns if re.search(p, cmd)), None)
    if not matched:
        sys.exit(0)

    # Destructive: allow only on a fresh advisor ack.
    if ack_file.is_file():
        age = time.time() - ack_file.stat().st_mtime
        if age <= ttl:
            verdict = ack_file.read_text(encoding="utf-8", errors="replace")[:200]
            verdict = " ".join(verdict.split())
            emit("allow", f"ceh-advisor consulted (ack fresh): {verdict}")
            sys.exit(0)

    # No fresh ack. A subagent cannot run the consult protocol - it has no Task
    # tool, so "invoke ceh-advisor" is a dead end that leaves it stuck. Deny with
    # an instruction it can actually act on. Deliberately still a deny: skipping
    # the guard here would let any destructive command through by delegating it.
    if payload.get("agent_id"):
        deny(
            f"Destructive command blocked by ceh-advisor guard: {cmd}",
            "You are running as a subagent and cannot invoke ceh-advisor via the Task tool. "
            "Stop and report to your caller that this command needs an advisor consult before "
            "it can run, and let the caller decide. Do not write the ack file yourself - you "
            "are not in a position to have had the consult.",
        )

    deny(
        f"Destructive command blocked by ceh-advisor guard: {cmd}",
        consult_protocol(ttl),
    )


if __name__ == "__main__":
    main()
