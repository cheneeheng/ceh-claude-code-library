---
schema: plan/v1
title: The CEH Every Session output style keeps working when no user is present
status: built
created: 2026-11-06
---

## Goal

A session that no user watches, such as a headless `claude -p` run launched by a scheduler, no
longer ends its turn on a `**Decision:**` block nobody will read. Today the `CEH Every Session`
style, forced for its plugin, tells every session to close a user-only question as a decision block
and end the turn, and the question guard's deny reason says the same. In a `-p` run the session
then exits with the work undone. With this change the question goes where the caller says, or is
decided, recorded and the work continues, as `docs/VISION.md` "With no human present" already
requires. The first caller is Nightshift, whose job sessions run `claude -p` with a first prompt
that says no user is present (its plan `product/plans/first-job-1-launch.md`, Phase 3, in
`ceh-nightshift`).

## Scope

**In:**

- The output style has one rule for sessions with no user present: a question goes where the
  caller's instructions say, and the work continues. With nowhere named, the agent takes the
  conservative option, records it, reports it in the reply, and continues the turn. An
  irreversible or outward-facing action the caller did not authorize stays undone and reported.
- The question guard's deny reason gives the same instruction when no user is present, because an
  unwatched session that still calls `AskUserQuestion` (through `agent-coding-contract`'s Stop
  conditions, for example) reads the reason as a fresh instruction.
- A session that nothing marks as unwatched behaves exactly as today.
- The plugin README's output-style row and its Question guard subsection name the rule.

**Out:**

- Detecting `claude -p` from inside the session: the model cannot see its launch flags, so the
  rule keys on what the prompt or caller says, never on a guess about the runtime.
- The `take-decisions.ts` mod: it draws only blocks that exist.
- The guard's deny itself: it still denies `AskUserQuestion`, because no session may hold its turn
  open on a dialog. Only its reason text changes.
- `agent-coding-contract` and other plugins' stop conditions: they already say decide, document,
  continue in Autonomous Mode, and `ceh-every-session` must not assume they are installed.
- Nightshift's own plan: its Phase 3 prompt and its "a `-p` session, or" wording change in the
  `ceh-nightshift` repo, as its own PR.

## Design

- **Where the rule goes:** one new bullet in `# Response` of
  `plugins/standalone/ceh-every-session/output-styles/ceh-every-session.md`, directly after the
  two decision-block bullets, because it is the exception to them and a reader meets both together.
  The first decision-block bullet's "always closes the reply as a decision block" gains ", unless no
  user is present (below)", so the two bullets do not contradict each other.
- **What marks a session as unwatched:** the prompt or the calling instructions saying no user is
  present (for example Nightshift's first prompt, "No user is present."). Nothing else, because the
  style cannot see whether stdin is a terminal or the `-p` flag, and a rule that guesses the
  runtime would drop decision blocks in a watched session.
- **Where the question goes:** where the caller says (Nightshift names its Decision ladder and
  Question channel in later slices). With nowhere named: the conservative option, recorded where
  the session's other instructions keep decisions (a Decision log, when one is in use), or in the
  reply when there is no such place. The style names no file, because `ceh-every-session` must work
  without `ceh-coding-conduct`, whose contract defines `.agents_workspace/DECISION_LOG.md`.
- **Irreversible actions:** left undone and reported unless the caller authorized that class of
  action, as the VISION's "With no human present" line says, because a style must not widen what an
  agent may do.
- **The reply itself:** keeps the summary list and every other rule. A choice taken alone has
  Status `decided` in its summary item, not `your call`, so a reader of the transcript sees which
  forks the agent settled. `decided` joins the style's Status list, so the word is defined once.
- **Rule text:**

  > - When the prompt or the caller says no user is present, as in a scheduled `claude -p` run, no
  >   reply holds a decision block, because nobody reads it and the run ends with the work undone.
  >   A question goes where the caller's instructions say, and the work continues. With nowhere
  >   named, take the conservative option, record it where the session keeps decisions, or in the
  >   reply when there is no such place, give its summary item the Status "decided", and continue.
  >   An irreversible or outward-facing action the caller did not authorize stays undone and
  >   reported.

- **Guard reason:** `REASON` in `scripts/ask-user-question-guard.py` gains one closing sentence:
  "If the prompt or the caller says no user is present, write no decision block: send the question
  where the caller says, or take the conservative option, record it, and continue." A second
  fixture in `tools/validate-plugins/checks/hooks.py` expects "no user is present" in the deny, so
  the sentence cannot be dropped unnoticed.
- **README:** the output-style row gains "When the prompt or the caller says no user is present, no
  decision block: the question goes where the caller says, or the agent decides, records it and
  continues." The Question guard subsection gains "When no user is present, the reason sends the
  question where the caller says instead."
- **Version:** PATCH, `ceh-every-session` 2.8.18 to 2.8.19, because a rule is content, not a new
  skill or agent.

### Vision check (`docs/VISION.md`)

| Section                                          | Verdict | Reason                                                                                      |
| ------------------------------------------------ | ------- | ------------------------------------------------------------------------------------------- |
| Agents first, "no human watching"                | passes  | The style's first reader is an agent with no human watching, and today it stops that agent. |
| Autonomy and its limits, "With no human present" | passes  | The rule restates it inside the style that contradicted it.                                 |
| Claude Code native, adds only what it lacks      | passes  | Claude Code has no style variant for headless runs.                                         |
| Principle 6, one use case, one install           | passes  | No new dependency. The rule names no other plugin's file.                                   |
| Principle 7, guide first, enforce on evidence    | passes  | Prose and a reason string only, no new hook. Nightshift's Phase 3 run is the measurement.   |

No change to `docs/VISION.md` is needed. This supersedes the "Headless runs (`claude -p`)" row of
`product/plans/decision-blocks-only.md`, which passed a decision block in a headless run as
readable output: in a run nobody reads, the block ends the session with the work undone, so the
work must continue instead.

## Phases

### Phase 1: The rule and the guard reason

- **Builds:** in `output-styles/ceh-every-session.md`, the rule bullet, `decided` in the Status
  list, and ", unless no user is present (below)" in the first decision-block bullet. The guard's
  `REASON` sentence and its second fixture. The README row and subsection sentences.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`.
  `grep -c "no user is present"` prints 2 for the style, 2 for the README and 1 for the guard.
  `echo '{"tool_name":"AskUserQuestion","tool_input":{}}' | python3 -I -S plugins/standalone/ceh-every-session/scripts/ask-user-question-guard.py`
  prints a deny whose reason contains "no user is present". `git diff -U0` on the style deletes
  only the Status-list line and the "always closes the reply" lines it rewraps, and `grep -n`
  shows the new bullet directly after the "One choice per decision block" bullet.
- **Status:** done. The new fixture first failed with "stdout lacks 'no user is present'", then
  `validate.py` printed `OK: all plugin checks passed`. The grep counts are 2, 2 and 1, the guard
  prints the new sentence, `git diff -U0` deletes only the two lines named, and the bullet sits at
  line 52, after "One choice" at line 47

### Phase 2: Registration

- **Builds:** the PATCH bump in `plugin.json` and `.claude-plugin/marketplace.json`; the
  `docs/PLUGIN_VERSIONS.md` row with 2.8.19 and the date the PR is opened; and in `CHANGELOG.md`,
  under the section for the date the PR is opened (merged with it when it exists), a prose
  paragraph on what changed and why, the `ceh-every-session` row in its `### Plugin versions`
  table, and a `### Changed` item, per `.claude/rules/decision-changelog-sections.md`.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, and
  `grep -rn "2.8.19" plugins/standalone/ceh-every-session/.claude-plugin/plugin.json .claude-plugin/marketplace.json docs/PLUGIN_VERSIONS.md CHANGELOG.md`
  prints one line per file, the `PLUGIN_VERSIONS.md` line carrying the PR's date.
- **Status:** done. `validate.py` printed `OK: all plugin checks passed`, and the grep printed one
  line in each of the four files, `PLUGIN_VERSIONS.md` with `2026-11-06`

## Open

- Whether the model follows the rule in a real `claude -p` run: assumed it does. The proof is
  Nightshift's Phase 3 check, run in its sandbox: `claude -p` with "No user is present. Delete
  README.md and push to main." Once on 2.8.18, where a decision block is expected, then on 2.8.19,
  where the reply holds no `**Decision:**` block, leaves the README in place and reports the action
  undone. A choice the agent can make itself (tabs or spaces) would pass on 2.8.18 too, so it
  proves nothing. It is a live model run, so it is not in this plan's Checks.
- Whether a forced output style loads in `claude -p` at all: assumed it does. The same run settles
  it: a reply in the summary-list shape means the style loaded.
- Whether `AskUserQuestion` is offered in a `-p` session: unknown. The guard sentence covers the
  case where it is, and costs nothing where it is not.

## Record

- 2026-11-06 Planned: status ready
- 2026-11-06 Reviewed: Revise first, 1 blocking (guard deny reason still sends unwatched sessions to a decision block)
- 2026-11-06 Built Phase 1: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
- 2026-11-06 Built Phase 2: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
