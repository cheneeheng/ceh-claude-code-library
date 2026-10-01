#!/usr/bin/env python3
"""usage-limit-watch.py - PostToolUse hook (all tools)

Samples the account-wide quota that the user's statusline export writes to
~/.claude/statusline/<project-dir>/<session_id>.jsonl and, when any rate-limit
window crosses the threshold, feeds a message back to Claude (exit 2)
instructing it to stop starting new work and run the usage-limit-handoff skill.

The reading is account-wide (it covers claude.ai web, desktop, mobile and
Claude Code together) and refreshes on every API round-trip, so sampling once
per tool call is fresh enough to fire preemptively rather than after a 429.

Records are read from the newest statusline file across *all* sessions and
projects, not just the current one, so a second Claude Code window does not
leave this session acting on a stale number.

Prerequisite (documented in the plugin README): a statusline script that
exports its stdin JSON to that path - e.g. ~/.claude/statusline-hook.ps1 with
C4_STATUSLINE_EXPORT=1. Without it the hook warns once per session rather than
failing silently, since a silent no-op looks identical to being protected.

Config (env or defaults):
  CEH_USAGE_LIMIT_THRESHOLD  used_percentage that triggers handoff (default 90)
  CEH_USAGE_STALE_MINUTES    ignore readings older than this (default 15)

Anti-spam: after firing, re-fires only when usage has climbed 5 more points,
so an ignored warning escalates instead of repeating on every tool call.
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

# Statusline files can be long-lived; only the tail holds the current reading.
TAIL_BYTES = 65536
NEWEST_FILES = 5


def tail_records(path):
    """Newest-first JSON records from the tail of a .jsonl file."""
    with path.open("rb") as fh:
        fh.seek(0, os.SEEK_END)
        fh.seek(max(0, fh.tell() - TAIL_BYTES))
        blob = fh.read()
    for line in reversed(blob.decode("utf-8", "replace").splitlines()):
        if not line.strip():
            continue
        try:
            # A mid-file seek can truncate the first line; that one just fails to parse.
            yield json.loads(line)
        except ValueError:
            continue


def latest_reading():
    """(ts_ms, rate_limits) from the most recent record carrying quota data."""
    root = Path.home() / ".claude" / "statusline"
    if not root.is_dir():
        return None

    files = sorted(
        root.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    best = None
    for path in files[:NEWEST_FILES]:
        for rec in tail_records(path):
            limits = (rec.get("data") or {}).get("rate_limits")
            ts = rec.get("ts")
            if (
                not isinstance(limits, dict)
                or not limits
                or not isinstance(ts, (int, float))
            ):
                continue
            # Newest record in this file wins; compare across files by timestamp.
            if best is None or ts > best[0]:
                best = (ts, limits)
            break
    return best


def worst_window(limits, now):
    """(name, window, pct) for the window closest to its cap.

    Windows whose resets_at has already passed are excluded: the reading was
    taken before that reset, so its used_percentage reflects the spent window,
    not the fresh one that has since started. Without this, a record written
    just before a reset keeps reporting ~90% and fires the handoff on the first
    tool call after the limit restarts - before any API round-trip refreshes it.
    """
    usable = {}
    for name, win in limits.items():
        if not isinstance(win, dict) or win.get("used_percentage") is None:
            continue
        resets_at = win.get("resets_at")
        if resets_at is not None:
            try:
                if float(resets_at) <= now:
                    continue
            except (ValueError, TypeError):
                pass
        usable[name] = win
    if not usable:
        return None
    name, win = max(usable.items(), key=lambda kv: float(kv[1]["used_percentage"]))
    return name, win, int(float(win["used_percentage"]))


def warn_once(marker, message):
    """Visible warning (exit 1) the first time only - never blocks a tool call."""
    if not marker.exists():
        marker.write_text("1", encoding="utf-8")
        print(message, file=sys.stderr)
        sys.exit(1)


def main() -> None:
    payload = json.loads(sys.stdin.read())
    session_id = payload.get("session_id") or "default"
    state_dir = Path(tempfile.gettempdir())

    reading = latest_reading()
    if reading is None:
        warn_once(
            state_dir / f"ceh-usage-nosensor-{session_id}",
            "ceh usage-limit guard: no statusline quota export found - the usage-limit guard "
            "is INACTIVE this session. See the ceh-core README to enable it.",
        )
        return

    ts, limits = reading
    stale_minutes = float(os.environ.get("CEH_USAGE_STALE_MINUTES", "15"))
    age_minutes = (time.time() - ts / 1000) / 60
    if age_minutes > stale_minutes:
        # A stale low reading is worse than none: it reads as safety that is not there.
        warn_once(
            state_dir / f"ceh-usage-stale-{session_id}",
            f"ceh usage-limit guard: newest quota reading is {int(age_minutes)}min old "
            "(stale) - treating usage as unknown. The guard may not fire in time.",
        )
        return

    worst = worst_window(limits, time.time())
    if worst is None:
        return
    name, window, pct = worst

    threshold = int(os.environ.get("CEH_USAGE_LIMIT_THRESHOLD", "90"))
    if pct < threshold:
        return

    # Fire once per 5-point band above the threshold, not on every tool call.
    # Keyed on session_id, which subagents share with the parent, so the whole
    # session escalates together instead of each subagent warning separately.
    state = state_dir / f"ceh-usage-limit-{session_id}"
    last_fired = -999
    if state.is_file():
        try:
            last_fired = int(state.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    if pct < last_fired + 5:
        return
    state.write_text(str(pct), encoding="utf-8")

    label = name.replace("_", " ")
    head = (
        f"ceh usage-limit guard: {label} usage is at {pct}% (threshold {threshold}%). "
    )

    # Exit 2 feeds this to whichever loop made the tool call. In a subagent that
    # is the subagent, which sees only its own slice of the work and whose final
    # report the user never reads - so it reports upward instead of writing the
    # artifact, and the main session owns the handoff.
    if "subagents" in (payload.get("transcript_path") or ""):
        msg = head + (
            "You are a subagent: do NOT write a handoff file. Finish only the current atomic "
            "step, then stop and report this guard trip plus your completed and open work as "
            "your final message to the calling session, which writes the handoff."
        )
    else:
        msg = head + (
            "Do not start new subtasks, tool-call chains, or subagents. Finish only the current "
            "atomic step, then load and follow the ceh-core:usage-limit-handoff "
            "skill: write the handoff artifact, then end the turn. "
            f"Session id prefix for the handoff filename: {session_id[:8]}."
        )

    resets_at = window.get("resets_at")
    if resets_at:
        try:
            msg += f" The {label} window resets at {datetime.fromtimestamp(float(resets_at)):%H:%M}."
        except (ValueError, TypeError, OSError):
            pass

    print(msg, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - report, never block a tool call
        # Advisory hook: surface one readable line instead of a traceback on
        # every tool call, and exit 1 (visible warning) rather than 2 (blocks).
        print(f"ceh usage-limit guard disabled this call: {exc}", file=sys.stderr)
        sys.exit(1)
