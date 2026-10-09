"""Measure what each ceh-* plugin adds to a session's context, with no model call.

Listing: the skill and agent descriptions, loaded into every session. Hooks: the text each
context-injecting hook prints, run once with a minimal payload, counted per event. Tokens are
estimated at four characters each. Guard hooks (PreToolUse, PostToolUse) are left out: they add
text only when they deny.

Usage: python context_budget.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "tools" / "validate-plugins"))
from validate import parse_frontmatter, plugin_dirs, rel  # noqa: E402

EVENTS = ("SessionStart", "SubagentStart", "UserPromptSubmit")
SCRIPT_PAT = re.compile(r'scripts/([\w.-]+)"\s*(.*)$')


def listing_chars(plugin: Path) -> int:
    docs = [*plugin.glob("skills/*/SKILL.md"), *plugin.glob("agents/*.md")]
    return sum(len((parse_frontmatter(d) or {}).get("description", "")) for d in docs)


def injected_chars(plugin: Path, event: str) -> int:
    hooks = plugin / "hooks" / "hooks.json"
    if not hooks.is_file():
        return 0
    total = 0
    for group in json.loads(hooks.read_text(encoding="utf-8"))["hooks"].get(event, []):
        for hook in group["hooks"]:
            m = SCRIPT_PAT.search(hook.get("command", ""))
            if not m:
                continue
            script = plugin / "scripts" / m.group(1)
            runner = (
                [sys.executable] if script.suffix == ".py" else [shutil.which("bash")]
            )
            out = subprocess.run(
                [*runner, rel(script), *m.group(2).split()],
                cwd=REPO,
                input=json.dumps({"session_id": "budget", "hook_event_name": event}),
                capture_output=True,
                text=True,
                timeout=30,
                env={k: v for k, v in os.environ.items() if k != "CEH_DISABLED_HOOKS"},
            ).stdout
            try:
                ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
            except (ValueError, KeyError, TypeError):
                ctx = out
            total += len(ctx)
    return total


def main() -> None:
    rows = []
    for plugin in plugin_dirs():
        counts = [listing_chars(plugin), *(injected_chars(plugin, e) for e in EVENTS)]
        if any(counts):
            rows.append((plugin.name, counts))
    rows.sort(key=lambda r: -(r[1][0] + r[1][1]))
    print(
        "| Plugin | Listing | SessionStart | SubagentStart | Per prompt | Session total (~tokens) |"
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for name, (listing, start, sub, prompt) in rows:
        print(
            f"| {name} | {listing} | {start} | {sub} | {prompt} | ~{(listing + start) // 4} |"
        )
    listing, start, sub, prompt = (sum(r[1][i] for r in rows) for i in range(4))
    print(
        f"| **all** | {listing} | {start} | {sub} | {prompt} | ~{(listing + start) // 4} |"
    )
    print(
        "\nCharacters, except the last column. Session total counts listing plus SessionStart once."
        " Per prompt repeats on every user message, SubagentStart on every subagent."
    )


if __name__ == "__main__":
    main()
