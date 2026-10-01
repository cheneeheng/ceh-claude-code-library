#!/usr/bin/env python3
"""PreToolUse hook: catch bash commands that dump large files into context.

Closes the obvious hole in bulk-read-guard.py — denying the Read tool does
nothing if `cat bigfile` still works.

Opt-in: does nothing unless BULK_READER_MIN_LINES is set.

Passes through:
  - piped commands (`cat f | grep x`) — the pipe is doing the narrowing
  - stdout redirections (`cat f > out`) — not reaching context at all;
    a stderr redirect (`2>/dev/null`) is not one of these and still gets checked
  - head/tail that actually print a small window — see emitted_lines(), which
    resolves `-n +N` and `-n -N` (offsets, not counts) and `-c` (bytes) against
    the real file rather than reading the bare integer as a line count

Several files in one command are summed: `cat a b c` costs their total, not
their max, and a glob (`cat dir/*.py`) is expanded before summing.

Fails open on anything it cannot parse.
"""

import fnmatch
import glob
import json
import os
import re
import shlex
import sys

FALLBACK_MIN_LINES = 350
DUMP_COMMANDS = {"cat", "less", "more", "bat", "batcat"}
WINDOW_COMMANDS = {"head", "tail"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||;")

# A stdout redirect sends the dump to a file instead of to context. `2>` does
# not, so match a bare `>` or an explicit `1>` and nothing else.
STDOUT_REDIRECT = re.compile(r"(?<![0-9])>|(?<![0-9])1>")

# Mirrors ALWAYS_ALLOW in bulk-read-guard.py. Both guards must exempt the same
# files, or `cat uv.lock` is denied while Read on it passes.
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


def is_allowed(path):
    patterns = list(ALWAYS_ALLOW)
    extra = os.environ.get("BULK_READER_ALLOW", "").strip()
    if extra:
        patterns.extend(p for p in extra.split(":") if p)
    base = os.path.basename(path)
    return any(
        fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(base, pat) for pat in patterns
    )


def count_lines(path):
    try:
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as fh:
            if b"\x00" in fh.read(8192):
                return None
        with open(path, "r", encoding="utf-8", errors="strict") as fh:
            return sum(1 for _ in fh)
    except (OSError, UnicodeDecodeError):
        return None


def window_arg(tokens):
    """(flag, raw value) for an explicit head/tail window, else (None, None)."""
    for i, tok in enumerate(tokens):
        if tok in ("-n", "-c") and i + 1 < len(tokens):
            return tok, tokens[i + 1]
        if re.fullmatch(r"-\d+", tok):  # head -20
            return "-n", tok[1:]
        m = re.fullmatch(r"-([nc])([+-]?\d+)", tok)  # head -n20, head -c400
        if m:
            return "-" + m.group(1), m.group(2)
    return None, None


def emitted_lines(cmd, tokens, path, total):
    """Lines this head/tail actually prints, or None when it is already narrow.

    The bare integer is not the answer. `-n +N` and `-n -N` are offsets, so they
    print most of the file however small N is, and `-c` counts bytes, not lines.
    """
    flag, raw = window_arg(tokens)
    if raw is None:
        return None  # no explicit window: head/tail default to 10 lines
    try:
        n = int(raw)
    except ValueError:
        return None

    if flag == "-c":
        if not total:
            return None
        try:
            size = os.path.getsize(path)
        except OSError:
            return None
        # Resolve the offset first: `-c +N` and `-c -N` are the same offsets as
        # their `-n` forms, so reading n as a byte count inverts both.
        if raw.startswith("+"):
            shown = size - n + 1 if cmd == "tail" else n
        elif n < 0:
            shown = size + n if cmd == "head" else -n
        else:
            shown = n
        return max(shown, 0) / max(size / total, 1)
    if raw.startswith("+"):
        # `tail -n +N` prints from line N onward; head treats +N as a plain count.
        return total - n + 1 if cmd == "tail" else n
    if n < 0:
        # `head -n -N` prints all but the last N; `tail -n -N` is just the last N.
        return total + n if cmd == "head" else -n
    return n


def offending_file(segment, threshold):
    if "|" in segment or "<" in segment or STDOUT_REDIRECT.search(segment):
        return None  # narrowed or redirected — not a context dump

    try:
        tokens = shlex.split(segment)
    except ValueError:
        return None
    if not tokens:
        return None

    cmd = os.path.basename(tokens[0])
    if cmd not in WINDOW_COMMANDS and cmd not in DUMP_COMMANDS:
        return None

    counted, total = [], 0
    for tok in tokens[1:]:
        if tok.startswith("-") or not tok:
            continue
        # shlex leaves `dir/*.py` literal, and an unexpanded glob counts as no
        # file at all — the one form that dumps the most while looking smallest.
        for path in sorted(glob.glob(tok)) or [tok]:
            if is_allowed(path):
                continue
            lines = count_lines(path)
            if lines is None:
                continue
            if cmd in WINDOW_COMMANDS:
                # head/tail apply their window per file, so no summing here.
                shown = emitted_lines(cmd, tokens, path, lines)
                if shown is not None and shown >= threshold:
                    return [path], int(shown)
                continue
            counted.append(path)
            total += lines  # `cat a b c` costs the sum, not the largest
            if total >= threshold:
                return counted, total
    return None


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
    threshold = min_lines()
    if threshold is None:
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    command = (payload.get("tool_input") or {}).get("command", "")
    if not command:
        sys.exit(0)

    for segment in SEGMENT_SPLIT.split(command):
        hit = offending_file(segment.strip(), threshold)
        if hit:
            paths, lines = hit
            subject = (
                f"`{paths[0]}` is {lines} lines"
                if len(paths) == 1
                else ", ".join(f"`{p}`" for p in paths) + f" total {lines} lines"
            )
            deny(
                f"Blocked: {subject} (threshold {threshold}) and this "
                f"command would dump that into context. Decide which you need:\n\n"
                f"1. A specific part: narrow it here. Pipe through grep/sed/awk, or use "
                f"head/tail with a small -n; piped and redirected commands pass through. "
                f"This is the right branch if you are about to edit, debug, or review this "
                f"file, since a summary cannot give you the exact text an edit needs.\n\n"
                f"2. An understanding of the file: invoke the Skill tool with "
                f'skill="ceh-core:delegate-bulk-reads", then delegate to the '
                f"`bulk-reader` subagent with your question and this path."
            )
    sys.exit(0)


if __name__ == "__main__":
    main()
