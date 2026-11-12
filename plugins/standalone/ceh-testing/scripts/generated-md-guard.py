#!/usr/bin/env python3
"""PreToolUse hook: deny a direct edit to Markdown that is generated from a YAML artifact.

Matches Edit|Write|MultiEdit. A `.md` whose frontmatter holds `generated_from: <file>.yaml` is
written by `scripts/artifact.py render`, so a hand edit would be overwritten by the next render and
would leave the file out of step with its source. The denial names the YAML to edit instead.
CEH_ARTIFACT_CHECK=off disables it.

Fails open: anything unexpected allows the edit, because a guard that blocked work on its own bugs
would cost more than it saves.
"""

import json
import os
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
SOURCE = re.compile(r"^generated_from:\s*(\S+)\s*$", re.M)


def main() -> None:
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    if os.environ.get("CEH_ARTIFACT_CHECK", "").strip().lower() == "off":
        return

    payload = json.load(sys.stdin)
    file = Path(payload.get("tool_input", {}).get("file_path", ""))
    if file.suffix != ".md" or not file.is_file():
        return
    fm = FRONTMATTER.match(file.read_text(encoding="utf-8").replace("\r\n", "\n"))
    src = SOURCE.search(fm.group(1)) if fm else None
    if not src:
        return
    yaml = file.with_name(src.group(1))
    reason = (
        f"{file.name} is generated from {yaml.name}, so an edit here is lost at the next render. "
        f"Edit {yaml} instead: the artifact check renders this file from it. "
        "The user can turn this guard off with `CEH_ARTIFACT_CHECK=off`."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(out))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail open
        pass
    sys.exit(0)
