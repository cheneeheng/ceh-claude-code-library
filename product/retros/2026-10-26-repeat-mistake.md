---
schema: repeat-mistake/v1
date: 2026-10-26
other_file: none
---

# Repeat mistakes — 2026-10-26

| Mistake                                                                                                        | Evidence                                                                                                                                                                                                                            | Rung | Fix                                                                                                                                       | Proof        | Status            |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------------- |
| Wrote a build plan by hand instead of loading `ceh-build-planning:write-build-plan`                            | Session 09b1a5aa: a `Write` of `product/plans/visual-business-plan.md` copied from `plan.template.md`, with no `Skill` call for `write-build-plan`, then the user: "why did you not invoke the write and review build plan skills?" | 5    | Rewrite `write-build-plan`'s description so its moment covers changes to existing files from a retro or issue                             | not provable | applied           |
| Wrote `Built Phase` Record lines by hand instead of building through `ceh-build-from-plan:implement-from-plan` | Same session: an `Edit` of `product/plans/visual-business-plan.md` adding "- 2026-10-26 Built Phase 1: ...", with no `Skill` call for `implement-from-plan`                                                                         | 3    | PreToolUse hook `build-record-guard.py` in `ceh-build-from-plan`: deny a new Built Phase line unless the transcript holds that Skill call | yes          | awaiting approval |

## Why this rung

- write-build-plan: rungs 1 to 4 would fit (a hook like the one below on a new plan file's `Planned:` line), but the user's rule is to rewrite a description before enforcing a skill with a hook when the skill has a clear moment, and this one does. The description named "a new app, tool, component, or feature", and a retro's fixes to existing skills did not read as that.
- implement-from-plan: its description already matched the moment ("building from a written plan") and it still did not load, so a rewrite would not change anything. A Built Phase line is a pattern a hook can match, so rung 3 applies. This is a measured miss, which the user's rule asks for before a hook. Rungs 1 and 2 cannot tell whether a skill ran.

## Pending drafts

### Wrote a build plan by hand instead of loading write-build-plan

In `plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md`, replace the description
(292 characters, under the 300 limit), then PATCH-bump `ceh-build-planning` and update its
`docs/CATALOG.md` row:

```yaml
description: >-
  Load this skill before the first edit of a change that has no plan yet: a new app, tool, or
  feature, or a multi-file change to existing code or skills, such as the fixes a retro or issue
  lists. Writes one plan file. Trigger on "build me X", "plan this", "implement the changes in this
  retro".
```

A micro-test (five fresh `claude -p` runs with the plugin on "implement the changes in this
retro", five without) would show whether it now triggers. Each run is a billed model call.

### Wrote Built Phase Record lines by hand instead of building through implement-from-plan

New `plugins/standalone/ceh-build-from-plan/hooks/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -I -S \"${CLAUDE_PLUGIN_ROOT}/scripts/build-record-guard.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

New `plugins/standalone/ceh-build-from-plan/scripts/build-record-guard.py`:

```python
#!/usr/bin/env python3
"""PreToolUse hook: deny a plan's "Built Phase" Record line unless implement-from-plan ran.

Matches Edit|Write|MultiEdit. A Built Phase line in product/plans/*.md is the evidence that a phase
was built the way implement-from-plan builds it, so writing one by hand, without that skill loaded
in this session, records a build its procedure never ran. CEH_BUILD_RECORD_GUARD=off disables it.

Fails open: anything unexpected allows the edit.
"""

import json
import os
import re
import sys

BUILT = re.compile(r"^- \d{4}-\d{2}-\d{2} Built Phase ", re.M)
# The Skill tool call itself, not a mention of the name in prose.
LOADED = re.compile(r'"skill":\s*"ceh-build-from-plan:implement-from-plan"')


def main():
    if os.environ.get("CEH_BUILD_RECORD_GUARD") == "off":
        return
    p = json.load(sys.stdin)
    ti = p.get("tool_input", {})
    path = ti.get("file_path", "").replace("\\", "/")
    if "/product/plans/" not in path or not path.endswith(".md"):
        return
    new = ti.get("new_string") or ti.get("content") or ""
    new += "".join(e.get("new_string", "") for e in ti.get("edits", []))
    old = ti.get("old_string", "")
    if len(BUILT.findall(new)) <= len(BUILT.findall(old)):
        return
    with open(p["transcript_path"], encoding="utf-8") as f:
        if LOADED.search(f.read()):
            return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        "A Built Phase line records a phase built by ceh-build-from-plan:implement-from-plan, "
                        "which has not run in this session. Invoke the Skill tool with "
                        'skill="ceh-build-from-plan:implement-from-plan" and build the phase through it.'
                    ),
                }
            }
        )
    )


try:
    main()
except Exception:  # fail open
    pass
```

Proof, run on 2026-10-26 against the draft in the session scratchpad:

- The real mistake replayed: an Edit adding "- 2026-10-26 Built Phase 2: ..." to
  `product/plans/visual-business-plan.md`, with this session's 1622-line transcript. Result: deny.
- The same Edit with a transcript holding the `Skill` call for `implement-from-plan`: allowed.
- An Edit adding only a PR line, with this session's transcript: allowed.

Applying it also needs: a `CEH_BUILD_RECORD_GUARD` row in `docs/ENVIRONMENT_VARIABLES.md` and the
plugin README, a MINOR bump of `ceh-build-from-plan` (new hook), and the changelog rows.
