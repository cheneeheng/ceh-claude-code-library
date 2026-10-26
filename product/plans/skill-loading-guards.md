---
schema: plan/v1
title: Make write-build-plan trigger on retro fixes, and guard Built Phase lines with a hook
status: building
created: 2026-10-26
---

## Goal

Apply the two approved drafts in `product/retros/2026-10-26-repeat-mistake.md`, so the misses of
session 09b1a5aa do not repeat. An agent asked to implement the fixes a retro or issue lists loads
`ceh-build-planning:write-build-plan` before its first edit. An agent that writes a plan's
`Built Phase` Record line without having run `ceh-build-from-plan:implement-from-plan` is stopped
and told to build the phase through it.

## Scope

**In:**

- `write-build-plan`'s description names the drafted moment: a change with no plan yet, new or a
  multi-file change to existing code or skills, such as the fixes a retro or issue lists.
- A PreToolUse hook in `ceh-build-from-plan` denies an Edit, Write, or MultiEdit that adds a
  `- YYYY-MM-DD Built Phase ` line to a `product/plans/*.md` file, unless the session transcript
  shows `ceh-build-from-plan:implement-from-plan` started, by a `Skill` call or by its slash
  command.
- `CEH_BUILD_RECORD_GUARD=off` turns the hook off, and `CEH_DISABLED_HOOKS=build-record-guard`
  does too, like every other hook here.
- The repeat-mistake file marks both fixes `applied`.

**Out:**

- The paid micro-test of the new description: the user chose the fix without it.
- A matching hook for a new plan's `Planned:` line: the user's rule prefers a description rewrite
  for a skill with a clear moment, and that is the fix chosen for `write-build-plan`.
- A denial counter like `branch-guard.py`'s: it stops repetition loops on a guard that fires on
  every edit, and this one fires only on a Built Phase line.
- A plans folder other than `product/plans/` named in a repo's `CLAUDE.md`: the hook matches the
  default path only, the one every plan in this library's repos uses.

## Design

- The hook lives in `ceh-build-from-plan`, the plugin that owns the Built Phase line, so it is
  present exactly when the skill it requires is installed.
- It matches the two records a started skill leaves in the transcript, not a mention of the name,
  because prose mentions are common and would let a hand-written line through: the `Skill` tool
  call (`"skill": "ceh-build-from-plan:implement-from-plan"`) and the slash command
  (`<command-name>/ceh-build-from-plan:implement-from-plan</command-name>`, the form a user's
  `/` command takes, checked in a real transcript on 2026-10-26).
- It counts Built Phase lines in the new text against the old text, so editing near an existing
  line, or rewriting a plan that already has them, is not a new Built line. The old text is
  `old_string` for Edit, every `edits[].old_string` for MultiEdit, and the file on disk for Write
  (empty when the file does not exist).
- It follows `branch-guard.py`'s shape: the `CEH_DISABLED_HOOKS` kill switch first, then its own
  `off` switch, a `main()` under `if __name__ == "__main__"`, and fail open on any error, because a
  guard that blocks work on its own bugs costs more than it saves.
- Two PRs, one per fix, in phase order: `ceh-build-planning` PATCH, then `ceh-build-from-plan`
  MINOR for the new hook.

## Phases

### Phase 1: write-build-plan description

- **Builds:** the description in `plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md`,
  its `docs/CATALOG.md` row and `plugins/standalone/ceh-build-planning/README.md` row, the PATCH
  bump, the changelog and versions rows, the repeat-mistake row set to `applied`.
- **Check:** `python tools/validate-plugins/validate.py` shows no failure outside the git-ignored
  `docs/starlight/node_modules/`, and `grep -c "the fixes a retro or issue" plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md`
  prints 1.
- **Status:** done, the grep printed 0 before the edit and 1 after; validate.py's only failures are
  the 20 hygiene hits in `docs/starlight/node_modules/`

### Phase 2: build-record-guard hook

- **Builds:** `plugins/standalone/ceh-build-from-plan/hooks/hooks.json`,
  `plugins/standalone/ceh-build-from-plan/scripts/build-record-guard.py`, its fixtures in
  `tools/validate-plugins/checks/hooks.py` (deny an Edit without the skill; allow after a `Skill`
  call; allow after the slash command; allow a non-Built line; allow a non-plan path; allow a Write
  over a file that already holds the line; allow a MultiEdit whose `old_string` holds it; allow
  with each off switch), the README row, the `docs/ENVIRONMENT_VARIABLES.md` rows (a new
  `CEH_BUILD_RECORD_GUARD` row, and `ceh-build-from-plan` added to the `CEH_DISABLED_HOOKS` row),
  `ceh-build-from-plan` added to the `CEH_DISABLED_HOOKS` copy rows in `docs/CROSS_REFERENCES.md`,
  the MINOR bump, the changelog and versions rows, the repeat-mistake row set to `applied`.
- **Check:** the `hooks` fixtures for `build-record-guard.py` fail before the script exists and pass
  after it, with `validate.py` showing no failure outside `docs/starlight/node_modules/`; and the
  real mistake replayed against session 09b1a5aa's transcript,
  `<home>/.claude/projects/<project>/09b1a5aa-4d55-4c15-9f41-356f815dfdca.jsonl`, is denied.
- **Status:** todo

## Open

Whether `transcript_path` inside a subagent names the subagent's own transcript: assumed it does,
so a subagent that builds through the skill is allowed and one that does not is denied, which is
the rule either way.

## Record

- 2026-10-26 Planned: status ready
- 2026-10-26 Reviewed: Revise first, 2 blocking (slash-command invocation not matched; Write/MultiEdit old-line count wrong)
- 2026-10-26 Built Phase 1: `grep -c "the fixes a retro or issue" .../write-build-plan/SKILL.md`, 1
