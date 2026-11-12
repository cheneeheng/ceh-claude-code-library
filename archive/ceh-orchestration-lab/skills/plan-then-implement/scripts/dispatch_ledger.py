"""Dispatch ledger for one Claude Code session: every subagent dispatch, resume, and report.

Usage: python dispatch_ledger.py <session-id> [--since <ISO-8601 UTC timestamp>]

Prints one Markdown bullet per event, read from ~/.claude/projects/*/<session-id>.jsonl, then the
counts for the run.md Dispatches field. Edits and writes the main session made itself are listed
too, except those under .agents_workspace/orchestration-lab/, the run log's own bookkeeping.
"""

import argparse
import json
import re
from pathlib import Path

AGENT_ID = re.compile(r"agentId: (\w+)")
HAND_BACK = re.compile(r'<agent-message from="(\w+)">')


def first_status(text: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith("Status:"):
            return line.strip()
    return text.strip().splitlines()[0][:100] if text.strip() else "(empty report)"


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session_id")
    ap.add_argument(
        "--since", default="", help="list only events at or after this timestamp"
    )
    args = ap.parse_args()

    projects = Path.home() / ".claude" / "projects"
    files = list(projects.glob(f"*/{args.session_id}.jsonl"))
    if not files:
        raise SystemExit(
            f"no transcript for session {args.session_id} under {projects}"
        )

    calls: dict[str, tuple[str, str]] = {}  # tool_use_id -> (tool name, piece)
    pieces: dict[str, str] = {}  # agent id -> piece
    lines: list[str] = []
    counts = {"dispatch": 0, "resume": 0, "report": 0, "self-edit": 0}

    def log(ts: str, kind: str, text: str) -> None:
        counts[kind] += 1
        lines.append(f"- {ts[11:19]}Z {kind}: {text}")

    for line in files[0].open(encoding="utf-8"):
        rec = json.loads(line)
        ts = rec.get("timestamp", "")
        if ts < args.since:
            continue
        content = (rec.get("message") or {}).get("content")
        if rec.get("type") == "assistant":
            for b in content or []:
                if b.get("type") != "tool_use":
                    continue
                i = b.get("input") or {}
                if b["name"] in ("Agent", "Task"):
                    piece = i.get("description", "?")
                    calls[b["id"]] = ("Agent", piece)
                    mode = "background" if i.get("run_in_background") else "foreground"
                    log(
                        ts,
                        "dispatch",
                        f"{piece} ({i.get('subagent_type', '?')}, "
                        f"{i.get('model', 'inherit')}, {mode}, brief {len(i.get('prompt', ''))} chars)",
                    )
                elif b["name"] == "SendMessage":
                    piece = pieces.get(i.get("to", ""), i.get("to", "?"))
                    calls[b["id"]] = ("SendMessage", piece)
                    log(
                        ts,
                        "resume",
                        f"{piece} ({len(text_of(i.get('message', '')))} chars)",
                    )
                elif b["name"] in ("Edit", "Write"):
                    path = i.get("file_path", "").replace("\\", "/")
                    if "/.agents_workspace/orchestration-lab/" not in path:
                        log(ts, "self-edit", path)
        elif rec.get("type") == "user":
            if isinstance(content, str):
                m = HAND_BACK.search(content)
                if m:
                    log(
                        ts,
                        "report",
                        f"{pieces.get(m.group(1), m.group(1))}: {first_status(content)}",
                    )
                continue
            for b in content or []:
                if not isinstance(b, dict) or b.get("type") != "tool_result":
                    continue
                name, piece = calls.get(b.get("tool_use_id"), ("", ""))
                if name != "Agent":
                    continue
                text = text_of(b.get("content"))
                m = AGENT_ID.search(text)
                if m:
                    pieces[m.group(1)] = piece
                # A background launch reports later, as a hand-back message.
                if "Async agent launched" not in text:
                    log(ts, "report", f"{piece}: {first_status(text)}")

    print("\n".join(lines) or "- no dispatches")
    print(
        f"\nDispatches: {counts['dispatch']}, resumes: {counts['resume']}, "
        f"reports: {counts['report']}, self-edits: {counts['self-edit']}"
    )


if __name__ == "__main__":
    main()
