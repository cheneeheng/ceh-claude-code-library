---
schema: repeat-mistake/v1
date: 2026-10-28
other_file: none
---

# Repeat mistakes — 2026-10-28

| Mistake                                                                                                                                                                                                                                                    | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Rung | Fix                                                                                                                                                                                                                                                                                   | Proof | Status                                                                              |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ----------------------------------------------------------------------------------- |
| A skill that another skill's procedure names ("following X", "per X", "X sets out how", even "invoke the Skill tool with X") was followed from memory and never loaded: `commit`, `update-changelog`, `update-readme`, `sketch-design`, `write-test-first` | Session `b5d9c329` transcript: the only `Skill` calls are `agent-coding-contract`, `write-less-code`, `whats-next`, `write-build-plan`, `pull-request`, `implement-from-plan`, `test-a-bug-fix`, `prevent-repeat-mistake`. Meanwhile about 15 `git commit -q -F - <<'EOF'` calls ran (first: `docs(product): add the Stage 1 build plan and its review`), `CHANGELOG.md` was edited directly (`### Added` for `mcp-cassette check`, commit ce5c174), `README.md` was rewritten with `Write` (commit 8260d7d), and `src/mcp_cassette/check.py` and `tests/integration/test_check.py` were written right after `implement-from-plan` step 3 named `sketch-design` and `write-test-first`. Correction: the author, "commit, update changelog, update readme skills are not invoked in this session", then "same mistake also with the sketch design and write test first". | 3    | A `PreToolUse` guard, `skill-started-guard.py`, beside the existing `build-record-guard.py`. It denies `git commit`, a `CHANGELOG.md` or `README.md` edit, a test-file write, or a new source file in the project until a skill that owns that moment has been started in the session | yes   | applied (`ceh-git-workflow` 1.5.0, `ceh-testing` 1.5.0, `ceh-coding-conduct` 2.3.0) |

## Why this rung

- Rungs 1 and 2 don't fit. The five skills exist on purpose, so there is no duplicate to delete, and `settings.json` permissions can't express "allow only after skill X ran".
- Rung 5 already failed. `pull-request` step 2 says, word for word, "invoke the Skill tool with skill="ceh-git-workflow:update-changelog"", and that call was still skipped. Rewording the parent skills, or the five descriptions, is the rung this mistake got past.
- Rung 3 catches the exact moments. Each mistake has a mechanical trigger (a command, a file path), and a transcript shows whether the owning skill was started. The library already uses this pattern in `ceh-build-from-plan`'s `build-record-guard.py`.
- Your own rules point two ways here. SOUL says "prefer rewriting their descriptions over enforcing skill use with a hook", because "the skills are not properly triggered". That rule doesn't match this cause. None of the five was skipped for want of a description: a loaded parent skill named each one at the right moment. SOUL also says "measured miss should be the default" before adding a hook, and five misses were measured in one session. So the draft is a hook, and whether to apply it is your call.

## What skipping them cost, verified in this session

- **`commit`:** its rule "Never build a multi-line message with an inline shell heredoc" was broken by every commit. Types, scopes and subjects were right without the skill.
- **`write-test-first`:** "One failing test at a time" was broken. Phase 1 wrote 15 tests plus the stub server, then ran them all red at once. I did watch every test file fail before writing its code.
- **`sketch-design`:** the four checks (illegal states, runs twice, shared state, smallest interface) never ran on `check.py` or `Divergence`. The plan's Design held the shape, but not those checks. Whether they would have found anything is unknown.
- **`update-changelog`:** no visible damage. The entries follow Keep a Changelog under `[Unreleased]`, and the breaking change is marked. The skill's step 5 (Validate) never ran.
- **`update-readme`:** its rule "never rewrite the whole README when a few edits suffice" was broken by phase 5's full rewrite. The plan ordered that rewrite, so the skill would have needed an exception, not a different outcome. Its step 4 (grep for names the diff removed) didn't run. The diff removed none, which I checked by reading only.

## Keep or merge: recommendation per skill

All five are inferred judgments from reading each `SKILL.md` and from this session. Nothing was changed, as asked.

| Skill                               | Recommendation                                                                                                                                                                                                                                             | Why                                                                                                                                                                                                                                                                                                                                                                            |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ceh-git-workflow:commit`           | **Retire, and move its distinctive part.** Put the temp-file rule (no heredoc or here-string) and the attribution rule into `pull-request`'s Land step 4 as two lines, and the "one logical change per commit" rule into the always-loaded agent contract. | Most of its 115 lines are Conventional Commits, which this session got right without loading it, about 25 times. Only the heredoc rule was broken. This matches your rule on skills that "mostly restate standard practice": retire them and move the one distinctive part. The cost: a bare "commit this" request loses its trigger, and the contract line has to cover that. |
| `ceh-git-workflow:update-changelog` | **Merge.** Put Unreleased mode (about 6 lines: categorize, add under `[Unreleased]`, no version) into `pull-request` step 2. Put versioned mode, with its semver mapping table, into `release`, its only other caller.                                     | Keep a Changelog is standard and was followed without the skill. The parts that are actually distinctive are the two modes, and each one belongs to exactly one parent. A shared child that both parents name was skipped both times it came up.                                                                                                                               |
| `ceh-git-workflow:update-readme`    | **Keep standalone.**                                                                                                                                                                                                                                       | It has its own trigger outside any PR: "a change alters how someone installs, runs, or configures". It also carries two checks no other skill has: the significance gate, and grepping the README for names the diff removed. Its miss here was a trigger miss, which the guard addresses.                                                                                     |
| `ceh-coding-conduct:sketch-design`  | **Merge into planning.** Move its four checks into `write-build-plan`'s Design step, and into `review-build-plan`'s Engineering lens so they are reviewed. Then retire it.                                                                                 | SOUL requires a reviewed plan before any build, and the plan's Design already holds the types and signatures. So the "before its first test" moment is always covered by a plan. What the plan lacked was the four checks, which belong where the shape is decided. For a change too small for a plan, `write-less-code` already covers the shape.                             |
| `ceh-testing:write-test-first`      | **Keep standalone,** and have `implement-from-plan` step 3.2 invoke it explicitly, or let the guard enforce it.                                                                                                                                            | It is the TDD contract for every change that adds behavior, with or without a plan: one red test at a time, never weaken a test, an integration test per feature, and skip only when there is nothing to assert. `implement-from-plan` restates one line of it. Merging would make two copies to keep in step.                                                                 |

If you take all five: three skills retire into their natural parents (`commit` and `update-changelog` into `pull-request` and `release`, `sketch-design` into planning), two stay, and the guard's `RULES` shrink to `git commit` (pointing at `pull-request` or `release`), `README.md` and test files.

## Pending drafts

### A skill named inside another skill's steps is never loaded

Proof, run 2026-10-28 against this session's real transcript, cut off just before `test-a-bug-fix` was loaded (the state during phases 1 to 5). Every one of the five real calls is denied. The same calls are allowed once the five `Skill` lines are appended, and calls no rule covers pass:

```
== at-phase5                              == with-skills
git commit: DENY                          git commit: allow
Edit CHANGELOG.md: DENY                   Edit CHANGELOG.md: allow
Write README.md: DENY                     Write README.md: allow
Write tests/integration/test_check.py: DENY   ...test_check.py: allow
Write new src/mcp_cassette/check_new.py: DENY ...check_new.py: allow
scratch links.py outside project: allow
git status / Edit existing matching.py / Write existing check.py / Edit product/plans/stage-1.md: allow
```

Where it goes: in each plugin, as `scripts/skill-started-guard.py`, keeping only that plugin's rows in `RULES`, so each plugin still works installed alone. `ceh-git-workflow` gets the `git commit`, `CHANGELOG.md` and `README.md` rows. `ceh-testing` gets the test-file row. `ceh-coding-conduct` gets the new-source row (or none, if `sketch-design` retires). Hook registration, in each plugin's `hooks/hooks.json`, beside its existing entries:

```json
{
  "matcher": "Bash|Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "python3 -I -S \"${CLAUDE_PLUGIN_ROOT}/scripts/skill-started-guard.py\"",
      "timeout": 10
    }
  ]
}
```

Known limits, all inferred and not tested:

- The test-file rule fires on every edit to an existing test as well, including a one-line fixture tweak in a refactor. `verify-behavior-preserved` and `write-pytest-library-tests` are accepted to soften that.
- The transcript is read in full on each matching call. This session's transcript is 5.8 MB and the replay finished well inside the 10-second timeout, but the run wasn't timed.
- Subagents have their own transcripts, so a subagent that commits must load the commit skill itself.

The script, in full (also at the session scratchpad's `skill-started-guard.py`):

```python
#!/usr/bin/env python3
"""PreToolUse hook: deny a write whose owning skill has not been started in this session.

Matches Bash|Edit|Write|MultiEdit. Each rule names a moment (a command, a file) and the skills
that own it; the call is denied until one of them was started, by a Skill tool call or a user's
slash command, never a mention. A parent skill that only names a child ("following X", "X sets
out how") does not count: that wording is how the child got skipped. CEH_SKILL_STARTED_GUARD=off
disables it.

Each plugin ships this script with only its own rows in RULES, so it works installed alone.

Fails open: anything unexpected allows the call, because a guard that blocked work on its own
bugs would cost more than it saves.
"""

import json
import os
import re
import sys
from pathlib import Path

# (tools, what the call must match, owning skills: any one started is enough)
RULES = [
    (
        {"Bash"},
        ("command", re.compile(r"\bgit\s+commit\b")),
        ["ceh-git-workflow:commit"],
    ),
    (
        {"Edit", "Write", "MultiEdit"},
        ("path", re.compile(r"(^|/)CHANGELOG\.md$")),
        ["ceh-git-workflow:update-changelog", "ceh-git-workflow:release"],
    ),
    (
        {"Edit", "Write", "MultiEdit"},
        ("path", re.compile(r"(^|/)README\.md$")),
        ["ceh-git-workflow:update-readme"],
    ),
    (
        {"Edit", "Write", "MultiEdit"},
        (
            "path",
            re.compile(
                r"(^|/)(test_[^/]+\.py|[^/]+_test\.py|[^/]+\.(test|spec)\.[jt]sx?)$"
            ),
        ),
        [
            "ceh-testing:write-test-first",
            "ceh-testing:test-a-bug-fix",
            "ceh-testing:verify-behavior-preserved",
            "ceh-python-library:write-pytest-library-tests",
        ],
    ),
    (
        {"Write"},
        ("new_source", re.compile(r"\.(py|ts|tsx|js)$")),
        ["ceh-coding-conduct:sketch-design"],
    ),
]


def started(skill: str, transcript: str) -> bool:
    name = re.escape(skill)
    return bool(
        re.search(rf'"skill":\s*"{name}"', transcript)
        or re.search(rf"<command-name>/{name}</command-name>", transcript)
    )


def subject(kind: str, ti: dict, cwd: str) -> str:
    """The text a rule matches against, or "" when the rule does not apply."""
    if kind == "command":
        return ti.get("command", "")
    path = ti.get("file_path", "").replace("\\", "/")
    root = cwd.replace("\\", "/").rstrip("/")
    if root and os.path.isabs(path) and not path.lower().startswith(root.lower() + "/"):
        return ""  # scratch files outside the project are nobody's deliverable
    if kind == "path":
        return path
    # new_source: a new code file outside tests, the moment sketch-design owns
    is_test = re.search(
        r"(^|/)(tests?|__tests__)/|(^|/)test_|_test\.|\.(test|spec)\.", path
    )
    return "" if is_test or Path(path).exists() else path


def main() -> None:
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    if os.environ.get("CEH_SKILL_STARTED_GUARD", "").strip().lower() == "off":
        return

    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {})
    transcript = None
    for tools, (kind, pattern), skills in RULES:
        if tool not in tools or not pattern.search(
            subject(kind, ti, payload.get("cwd", ""))
        ):
            continue
        if transcript is None:
            transcript = Path(payload["transcript_path"]).read_text(encoding="utf-8")
        if any(started(s, transcript) for s in skills):
            continue
        reason = (
            f"This {tool} call is owned by {' or '.join(skills)}, which has not been started "
            "in this session; a skill named inside another skill's steps still has to be "
            f'loaded. Invoke the Skill tool with skill="{skills[0]}" first, then retry. '
            "CEH_SKILL_STARTED_GUARD=off turns this guard off."
        )
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                    }
                }
            )
        )
        return


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail open
        pass
```
