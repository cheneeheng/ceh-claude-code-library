---
schema: plan/v1
title: The CEH Every Session output style keeps working when no user is present
status: ready
created: 2026-11-06
---

## Goal

A session that no user watches, such as a headless `claude -p` run launched by a scheduler, no
longer ends its turn on a `**Decision:**` block nobody will read. Today the `CEH Every Session`
style, forced for its plugin, tells every session to close a user-only question as a decision block
and end the turn. In a `-p` run the session then exits with the work undone. With this change the
question goes where the caller says, or is decided, recorded and the work continues, as
`docs/VISION.md` "With no human present" already requires. The first caller is Nightshift, whose
job sessions run `claude -p` with a first prompt that says no user is present (its plan
`product/plans/first-job-1-launch.md`, Phase 3, in `ceh-nightshift`).

## Scope

**In:**

- The output style has one rule for sessions with no user present: a question goes where the
  caller's instructions say, and the work continues. With nowhere named, the agent takes the
  conservative option, records it, reports it in the reply, and continues the turn. An
  irreversible or outward-facing action the caller did not authorize stays undone and reported.
- A session that nothing marks as unwatched behaves exactly as today.
- The plugin README's output-style row names the rule.

**Out:**

- Detecting `claude -p` from inside the session: the model cannot see its launch flags, so the
  rule keys on what the prompt or caller says, never on a guess about the runtime.
- The `take-decisions.ts` mod and `ask-user-question-guard.py`: neither changes. The mod draws only
  blocks that exist, and the guard denies a tool the unwatched session still must not call.
- The decision-block rule's wording for watched sessions: it stays as it is.
- `agent-coding-contract` and other plugins' stop conditions: they already say decide, document,
  continue in Autonomous Mode, and `ceh-every-session` must not assume they are installed.

## Design

- **Where the rule goes:** one new bullet in `# Response` of
  `plugins/standalone/ceh-every-session/output-styles/ceh-every-session.md`, directly after the
  two decision-block bullets, because it is the exception to them and a reader meets both together.
- **What marks a session as unwatched:** the prompt or the calling instructions saying no user is
  present (for example Nightshift's first prompt, "No user is present."). Nothing else, because the
  style cannot see whether stdin is a terminal or the `-p` flag, and a rule that guesses the
  runtime would drop decision blocks in a watched session.
- **Where the question goes:** where the caller says (Nightshift names its Decision ladder and
  Question channel in later slices). With nowhere named: the conservative option, recorded where
  the session's other instructions keep decisions (a Decision log, when one is in use), and named
  in the reply. The style names no file, because `ceh-every-session` must work without
  `ceh-coding-conduct`, whose contract defines `.agents_workspace/DECISION_LOG.md`.
- **Irreversible actions:** left undone and reported unless the caller authorized that class of
  action, word for word the VISION's "With no human present" line, because a style must not widen
  what an agent may do.
- **The reply itself:** keeps the summary list and every other rule. A choice taken alone has
  Status `decided` in its summary item, not `your call`, so a reader of the transcript sees which
  forks the agent settled.
- **Rule text:**

  > - When the prompt or the caller says no user is present, as in a scheduled `claude -p` run, no
  >   reply ends on a decision block, because nobody reads it and the run ends with the work
  >   undone. A question goes where the caller's instructions say, and the work continues. With
  >   nowhere named, take the conservative option, record it where the session keeps decisions,
  >   give its summary item the Status "decided", and continue. An irreversible or outward-facing
  >   action the caller did not authorize stays undone and reported.

- **Version:** PATCH, `ceh-every-session` 2.8.18 to 2.8.19, because a rule is content, not a new
  skill or agent.

### Vision check (`docs/VISION.md`)

| Section                                          | Verdict | Reason                                                                                      |
| ------------------------------------------------ | ------- | ------------------------------------------------------------------------------------------- |
| Agents first, "no human watching"                | passes  | The style's first reader is an agent with no human watching, and today it stops that agent. |
| Autonomy and its limits, "With no human present" | passes  | The rule restates it inside the style that contradicted it.                                 |
| Claude Code native, adds only what it lacks      | passes  | Claude Code has no style variant for headless runs.                                         |
| Principle 6, one use case, one install           | passes  | No new dependency. The rule names no other plugin's file.                                   |
| Principle 7, guide first, enforce on evidence    | passes  | Prose only, no hook. Nightshift's Phase 3 check is the first measurement.                   |

No change to `docs/VISION.md` is needed.

## Phases

### Phase 1: The rule

- **Builds:** the rule bullet in `output-styles/ceh-every-session.md`, and the output-style row in
  `plugins/standalone/ceh-every-session/README.md`.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, and
  `grep -c "no user is present" plugins/standalone/ceh-every-session/output-styles/ceh-every-session.md plugins/standalone/ceh-every-session/README.md`
  prints 1 for each file.
- **Status:** todo

### Phase 2: Registration

- **Builds:** the PATCH bump in `plugin.json`, `.claude-plugin/marketplace.json` and
  `docs/PLUGIN_VERSIONS.md`, and the entry in the `## 2026-11-06` section of `CHANGELOG.md`, its
  plugin versions table gaining the `ceh-every-session` row.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`, and
  `grep -rn "2.8.19" plugins/standalone/ceh-every-session/.claude-plugin/plugin.json .claude-plugin/marketplace.json docs/PLUGIN_VERSIONS.md CHANGELOG.md`
  prints one line per file.
- **Status:** todo

## Open

- Whether the model follows the rule in a real `claude -p` run: assumed it does. The proof is
  Nightshift's Phase 3 check, run in its sandbox after this lands: `claude -p` with "No user is
  present. Should this repo use tabs or spaces?" ends with a Decision log entry and no
  `**Decision:**` block. It is a live model run, so it is not in this plan's Checks.

## Record

- 2026-11-06 Planned: status ready
