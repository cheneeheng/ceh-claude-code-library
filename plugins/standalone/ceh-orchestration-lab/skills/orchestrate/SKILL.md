---
name: orchestrate
description: >-
  EXPERIMENTAL. Run a coding task as a supervised loop: this session briefs and reviews,
  implementer subagents on a cheaper model do every edit and test run, and the run is logged.
argument-hint: "[haiku|sonnet|opus|fable] [task]"
disable-model-invocation: true
user-invocable: true
license: Apache-2.0
---

# Orchestrate

This session plans, briefs, and reviews. Implementer subagents do every edit and every test run,
and the run is logged. The run is done when the run folder is closed with an outcome and the
user's verdict, whether the task succeeded or not.

This session's ID is `${CLAUDE_SESSION_ID}` and the plugin root is `${CLAUDE_PLUGIN_ROOT}`. Read
`${CLAUDE_PLUGIN_ROOT}/references/run-log.md` now: it says how to open, keep, and close the run
folder, and where these two values go.

## Arguments

`$ARGUMENTS`: if the first word is `haiku`, `sonnet`, `opus`, or `fable`, it is the worker model
and the rest is the task. Otherwise the worker model is `haiku` and all of it is the task. With no
task, the task is the user's most recent request.

## Procedure

1. **Open the run** per the run log, Strategy `orchestrate`.
2. **Split the work.** Read enough code to cut the task into pieces a worker can finish from one
   brief, each with its own check. Write the list under "Plan or briefs" in `run.md`. It can
   change as reports come in: append changes with the reason, never rewrite.
3. **Brief and dispatch.** For the next piece, write a brief: the goal, the files in scope, the
   exact behavior, what done looks like, and the command that proves it. The worker sees only
   the brief, so it must stand alone. Dispatch a `ceh-orchestration-lab:implementer` with the
   Agent tool, `model` set to the worker model. Pieces that touch disjoint files may go out
   together. Log each dispatch in the Ledger.
4. **Review each report.** Log it, then read the diff of the files it touched (`git diff -- <files>`).
   - Done and right: move to the next piece.
   - Incomplete or wrong on the same piece: resume that worker with `SendMessage`, saying exactly
     what is missing. Its context is warm, so a resume costs less than a fresh brief.
   - The report shows the split was wrong: update the list, then brief the new piece fresh.
5. **Final check.** When every piece is done, dispatch one implementer to run the full relevant
   test command and report. Do not run it yourself.
6. **Close the run** per the run log.

## Rules

- Never edit a project file and never run a test, build, or script yourself: every edit and every
  check goes to a worker. In an earlier experiment the orchestrator did the work itself and the
  run spent 97% on the orchestrator's model, which made it worthless as a measurement. Reading
  code, `git diff`, and `git status` stay with you.
- If the user asks you to make an edit yourself, do it and record it as a user intervention.
- Keep briefs as short as the worker model allows: exact names and values for Haiku, intent and
  constraints for Sonnet or Opus. A cheap resume beats an exhaustive brief.
- A piece that has failed review twice goes back to the split: cut it smaller or brief it fresh,
  and note in the Ledger why. Do not take it over yourself.

## Stop conditions

- The task needs a decision only the user can make (a product choice, an irreversible action) →
  ask, and log the question as a user intervention.
- A worker reports `blocked` on something the code cannot answer → ask the user, log it, and
  continue with their answer in a resume.
