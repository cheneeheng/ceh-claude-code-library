---
name: explain-action
description: >-
  Load this skill when the user asks why you did or did not do something this session: find
  the turn in the transcript, quote what applied and what you did, name the cause. Trigger
  on "why didn't you use X", "why did you do that". Not for a whole session (use
  ceh-session-learning:diagnose-session).
argument-hint: "[the action]"
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Explain an action

Answer why you did, or did not do, one thing in this session, from the transcript and not from
memory of it. Done means the reply cites the turn, quotes the instruction that applied and what
you did instead, names the cause, and ends on one question, with nothing changed.

## Procedure

1. **Name the action** in one line: what was done, or not done, and the turn the question points
   at. When it fits several turns, take the latest and say which.
2. **Find the transcript.** Glob `*/${CLAUDE_SESSION_ID}.jsonl` with the path
   `~/.claude/projects`, and say which file it is. The project folder is named for the directory
   the session was launched in, so do not build the path from the current directory.
3. **Find the turn** with Grep in content mode, matching only, and a bounded pattern such as
   `.{0,300}<phrase>.{0,300}`. One transcript line is a whole message and can run to thousands of
   characters, so never Read the file. A user message repeats in later `last-prompt` lines: the
   first hit is the turn. Use the transcript even when the turn is still in context, because
   after a compaction the context holds only a summary of it.
4. **Quote what applied** at that turn, with where it stands: a line of the skill listing, a rule
   in `CLAUDE.md` or a rules file, a step of a loaded skill, or the user's own message. Then
   quote what you did instead: the tool call or reply, on its transcript line.
5. **Name the cause** from the two quotes:

   | Cause       | Meaning                                                           |
   | ----------- | ----------------------------------------------------------------- |
   | Request     | The request was ambiguous, and your reading was reasonable        |
   | Guidance    | A skill, `CLAUDE.md`, or hook was wrong, missing, or never loaded |
   | Environment | A tool, permission, dependency, or service failed underneath      |
   | Model       | Clear, loaded guidance said otherwise and you did not follow it   |
   | Claude Code | The harness misbehaved: a tool, compaction, or a hook not firing  |

6. **Answer, then stop** (see Output).

## Rules

- **Change nothing.** No edit, no saved file, no redo of the skipped step, no fix. The question
  may be only a question, and the user may see from the answer that nothing went wrong. A fix
  made before they have read it cannot be declined.
- **The reason is inferred, never recalled.** The transcript holds what you read and did, not why,
  so the answer rests on the two quotes, and says so. A cause with no quote behind it is a
  hypothesis, given with what would confirm it.
- **One turn.** When the question turns out to span several turns, answer the one asked about
  and name `ceh-session-learning:diagnose-session` for the rest.
- Mask secrets in every quote as `<secret>`.

## Output

A reply, in this order, and no file:

1. What happened, with its `<transcript>:<line>`.
2. The instruction that applied, quoted, with where it stands.
3. The cause, in one sentence, marked as inferred.
4. One closing question: whether to run `ceh-every-session:prevent-repeat-mistake` on this cause.
   Ask, never run it. Add that `ceh-session-learning:diagnose-session` covers a later look at
   the whole session.
