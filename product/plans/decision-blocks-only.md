---
title: Every user-only question closes the reply as a decision block, never AskUserQuestion
status: built
created: 2026-10-14
---

## Goal

While `ceh-every-session` is enabled, every question only the user can answer (a fact only they
hold, a yes before an irreversible action) closes the reply as a `**Decision: <question>**` block,
which the plugin's mod draws as options. The agent never calls `AskUserQuestion`, because that tool
pauses the main turn: tested on 2026-10-14, a background `sleep` finished while the dialog was open,
and its completion notice reached the model only after the answer came back. A question that ends
the turn never blocks, whatever is still running (background tasks, subagents, future async
features), so no rule has to list those situations.

## Scope

**In:**

- The output style holds one rule: every user-only question closes the reply as a decision block,
  with the reason (it leaves the agent free to react to work still running). The "when the work can
  wait" condition and the `AskUserQuestion` fallback are removed.
- A `PreToolUse` guard denies `AskUserQuestion` and its reason tells the agent to end the reply with
  a decision block instead. It can be switched off through `CEH_DISABLED_HOOKS`. (Decided by the
  user, 2026-10-14: the guard ships now, before any observed failure of the prose rule.)

**Out:**

- The 11 files in other plugins that name `AskUserQuestion` (`agent-coding-contract`,
  `stress-test-plan`, `run-agentic-workflow`, and others): they must still work for a user without
  `ceh-every-session`, so they keep their wording, and the guard redirects them when the plugin is
  enabled.
- The mod: `hooks/take-decisions.ts` already parses the block, and the format does not change.

## Design

- **Guard:** `plugins/standalone/ceh-every-session/scripts/ask-user-question-guard.py`, stdlib-only
  Python, fails open like the other guards. The `CEH_DISABLED_HOOKS` check at the top of `main()` is
  a copy of the canonical block in `ceh-git-workflow/scripts/branch-guard.py`. It prints a
  `PreToolUse` `permissionDecision: deny` with the redirect reason. Wired in `hooks/hooks.json` as a
  third `PreToolUse` entry, `matcher: "AskUserQuestion"`, same command shape as the bulk-read guards.
- **Why a guard, not prose alone:** the built-in `AskUserQuestion` description, which this repo
  cannot edit, and `agent-coding-contract`'s stop conditions both send the agent to the tool, so a
  prose rule competes with two instructions that point the other way.
- **Version:** PATCH, 2.7.11 to 2.7.12. A hook and a rule are content, not a new skill or agent.

### Vision check (`docs/VISION.md`)

| Section                                       | Verdict               | Reason                                                                                                                                                                            |
| --------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Autonomy and its limits, "How it asks"        | passes                | Which questions get asked stays the same. Only how they are shown changes. Several blocks in one reply keep "once, up front".                                                     |
| Interviews are the exception                  | passes                | An adaptive interview asks one round per reply instead of one dialog per round. The number of exchanges is the same.                                                              |
| Headless runs (`claude -p`)                   | passes                | `AskUserQuestion` has no human in a headless run anyway. A decision block in the final text is readable output, and "conservative option, report it" still applies.               |
| Scope test for components a person sees       | passes                | The vision names "draws its closing questions as options" as passing.                                                                                                             |
| Non-goal: rebuilding Claude Code              | passes, with a reason | The panel duplicates part of `AskUserQuestion` on purpose. What Claude Code lacks is a question that does not block the turn, and that is the delta. The changelog entry says so. |
| Principle 6, one use case, one install        | passes                | No new dependency. The guard changes other plugins' behavior only while `ceh-every-session` is enabled, and they still work without it.                                           |
| Principle 7, guide first, enforce on evidence | weak                  | The conflicting instructions are in the text, but no session has yet shown the agent calling `AskUserQuestion` against the output style. See Open.                                |
| Principle 8, opinions with reasons            | passes                | The output-style rule carries its reason.                                                                                                                                         |

No change to `docs/VISION.md` is needed.

## Phases

### Phase 1: Output-style rule

- **Builds:** the single decision-block rule with its reason in
  `output-styles/ceh-every-session.md`, and the output-style row in the plugin `README.md`.
- **Check:** `python tools/validate-plugins/validate.py` passes, and
  `grep -n "AskUserQuestion\|can wait" plugins/standalone/ceh-every-session/output-styles/ceh-every-session.md`
  prints nothing.
- **Status:** done: the grep printed nothing (exit 1), and `validate.py` printed
  `OK: all plugin checks passed`.

### Phase 2: Guard

- **Builds:** the guard script and its `hooks.json` entry; the README Hooks table row, a short
  subsection, and the `CEH_DISABLED_HOOKS` name list; the new copy in `docs/CROSS_REFERENCES.md`
  under Hook kill switch; the script name in `docs/ENVIRONMENT_VARIABLES.md` if that row lists names.
- **Check:** `echo '{"tool_name":"AskUserQuestion","tool_input":{}}' | python3 -I -S plugins/standalone/ceh-every-session/scripts/ask-user-question-guard.py`
  prints a JSON deny with the redirect reason, and prints nothing with
  `CEH_DISABLED_HOOKS=ask-user-question-guard` set. `validate.py` passes. Manual check after a
  reload (the user): a prompt that triggers a stop condition gets a decision block, not a dialog,
  because no command can drive the interactive tool.
- **Status:** done, including the manual check reported by the user on 2026-11-13, not run by
  the agent. The explicit `AskUserQuestion` attempt was denied with the redirect reason, no dialog
  opened, and the reply ended with a decision block. The ordinary user-only question also ended
  with a decision block and no dialog. Claude Code and plugin versions were not supplied.
  The guard printed the deny JSON for
  `AskUserQuestion` and nothing when switched off, for another tool, or for bad JSON.
  `validate.py` first failed with "hook script has no fixture in validate.py hook_fixtures()", so
  three fixtures were added there (deny, other tool, switched off), and it then printed
  `OK: all plugin checks passed`. `docs/ENVIRONMENT_VARIABLES.md` lists no script names, so it is
  unchanged.

### Phase 3: Registration

- **Builds:** PATCH bump in `plugin.json`, `.claude-plugin/marketplace.json`, and
  `docs/PLUGIN_VERSIONS.md`; the `## 2026-10-14` `CHANGELOG.md` entry with the test evidence and
  the rebuilding-Claude-Code reason.
- **Check:** `python tools/validate-plugins/validate.py` passes.
- **Status:** done: `validate.py` printed `OK: all plugin checks passed`.

## Open

- None. The user reported on 2026-11-13 that both the live hook-denial check and the ordinary
  user-only question check passed. Phase 2 is retained.

## Record

- 2026-10-14 Planned: status draft
- 2026-10-14 Built Phase 1: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
- 2026-10-14 Built Phase 2: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
- 2026-10-14 Built Phase 3: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
- 2026-10-14 PR: #105 https://github.com/cheneeheng/ceh-claude-code-library/pull/105
- 2026-11-13 Manual Phase 2 checks: both passed, reported by the user, not run by the agent.
  The live `AskUserQuestion` call was denied and redirected to a decision block without a dialog;
  the ordinary user-only question also produced a decision block without a dialog. Status built.
- 2026-11-13 PR: #272 https://github.com/cheneeheng/ceh-claude-code-library/pull/272
