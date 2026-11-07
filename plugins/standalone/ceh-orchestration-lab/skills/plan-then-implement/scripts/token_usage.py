"""Token usage by model for one Claude Code session, main transcript plus its subagents.

Usage: python token_usage.py <session-id> [--since <ISO-8601 UTC timestamp>]

Prints a Markdown table. Reads ~/.claude/projects/*/<session-id>.jsonl and
~/.claude/projects/*/<session-id>/subagents/*.jsonl. A message is written once per content
block with the same usage, so usage is counted once per message id.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

FIELDS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session_id")
    ap.add_argument(
        "--since", default="", help="count only messages at or after this timestamp"
    )
    args = ap.parse_args()

    projects = Path.home() / ".claude" / "projects"
    files = list(projects.glob(f"*/{args.session_id}.jsonl"))
    files += list(projects.glob(f"*/{args.session_id}/subagents/*.jsonl"))
    if not files:
        raise SystemExit(
            f"no transcript for session {args.session_id} under {projects}"
        )

    messages: dict[str, tuple[str, str, dict]] = {}
    advisors: set[str] = set()
    for f in files:
        role = "subagent" if f.parent.name == "subagents" else "main"
        for line in f.open(encoding="utf-8"):
            rec = json.loads(line)
            msg = rec.get("message")
            if (
                rec.get("type") != "assistant"
                or not isinstance(msg, dict)
                or "usage" not in msg
            ):
                continue
            # ISO-8601 UTC strings in one format compare correctly as text.
            if rec.get("timestamp", "") < args.since:
                continue
            if rec.get("advisorModel"):
                advisors.add(rec["advisorModel"])
            messages[msg.get("id") or rec.get("uuid", "")] = (
                role,
                msg.get("model", "unknown"),
                msg["usage"],
            )

    totals: dict[tuple[str, str], list[int]] = defaultdict(
        lambda: [0] * (len(FIELDS) + 1)
    )
    for role, model, usage in messages.values():
        row = totals[(role, model)]
        row[0] += 1
        for i, field in enumerate(FIELDS, 1):
            row[i] += usage.get(field) or 0

    all_output = sum(row[4] for row in totals.values()) or 1
    print(
        "| Where | Model | Messages | Input | Cache write | Cache read | Output | Output share |"
    )
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for (role, model), row in sorted(totals.items()):
        cells = " | ".join(f"{n:,}" for n in row)
        print(f"| {role} | {model} | {cells} | {row[4] / all_output:.0%} |")
    # The advisor's own calls may not appear in the transcript, so this says only whether it was on.
    print(f"\nAdvisor configured: {', '.join(sorted(advisors)) or 'none recorded'}")


if __name__ == "__main__":
    main()
