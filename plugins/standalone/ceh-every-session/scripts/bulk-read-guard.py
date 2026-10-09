#!/usr/bin/env python3
"""PreToolUse hook: deny whole-file Reads of large files, steer to delegate-bulk-reads.

Opt-in: does nothing unless BULK_READER_MIN_LINES is set. Denying reads is too
aggressive a default for a plugin that loads in most sessions.

Targeted reads (offset/limit) always pass — knowing which region you need was
never the expensive part. Fails open: anything unexpected allows the read.
"""

import fnmatch
import json
import os
import sys
import tempfile
from pathlib import Path

FALLBACK_MIN_LINES = 350

# Reading these whole is usually the point, or delegation would mangle them.
ALWAYS_ALLOW = (
    "*.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "*.svg",
    "*.min.js",
    "*.min.css",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.ico",
    "*.pdf",
    "*.zip",
    "*.tar",
    "*.gz",
)


def min_lines():
    """Threshold, or None when enforcement is off."""
    raw = os.environ.get("BULK_READER_MIN_LINES", "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return FALLBACK_MIN_LINES


def allowlist():
    patterns = list(ALWAYS_ALLOW)
    extra = os.environ.get("BULK_READER_ALLOW", "").strip()
    if extra:
        patterns.extend(p for p in extra.split(":") if p)
    return patterns


def is_allowed(path):
    base = os.path.basename(path)
    return any(
        fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(base, pat) for pat in allowlist()
    )


def count_lines(path):
    """Line count, or None if the file is binary or unreadable."""
    try:
        with open(path, "rb") as fh:
            if b"\x00" in fh.read(8192):
                return None
        with open(path, "r", encoding="utf-8", errors="strict") as fh:
            return sum(1 for _ in fh)
    except (OSError, UnicodeDecodeError):
        return None


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


def deny(reason):
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def main():
    # Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        sys.exit(0)
    threshold = min_lines()
    if threshold is None:
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if payload.get("tool_name") != "Read":
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path")
    if not path:
        sys.exit(0)

    # Targeted read — the caller already knows what it wants.
    if tool_input.get("offset") is not None or tool_input.get("limit") is not None:
        sys.exit(0)

    if is_allowed(path):
        sys.exit(0)

    lines = count_lines(path)
    if lines is None or lines < threshold:
        sys.exit(0)

    n = denial_number(payload)
    if n > 3:
        deny(
            f"Blocked again (denial {n} this session): {path} is {lines} lines. Read a "
            f"region with offset/limit, or delegate to `bulk-reader`. The user can unset "
            f"BULK_READER_MIN_LINES to switch this guard off."
        )
    deny(
        f"Blocked: {path} is {lines} lines (threshold {threshold}). "
        f"Decide which you need before retrying:\n\n"
        f"1. A specific region: read it directly. Read with offset/limit passes through. "
        f"This is the right branch if you are about to edit, debug, or review this file: a "
        f"summary cannot give you the exact text an edit needs, and you would have to take "
        f"this read anyway. Use Grep first if you do not know the line.\n\n"
        f"2. An understanding of the file: invoke the Skill tool with "
        f'skill="ceh-every-session:delegate-bulk-reads", then delegate to the `bulk-reader` '
        f"subagent with your question and this path. It returns a line-anchored answer "
        f"without the contents entering this context.\n\n"
        f"Do not chunk the whole file into many offset reads; that costs more than one "
        f"delegation. The user can raise BULK_READER_MIN_LINES if this threshold is wrong "
        f"for this repo, or unset it to switch this guard off."
    )


if __name__ == "__main__":
    main()
