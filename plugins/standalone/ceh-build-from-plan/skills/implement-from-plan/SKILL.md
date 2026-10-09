---
name: implement-from-plan
description: >-
  Load this skill when building from a written plan: work through its phases in order, write the
  failing test first, implement only what the phase names, run the phase's check, and record the
  evidence in the plan. Works without a plan by writing a minimal one first. Trigger on "implement
  the plan", "build from the plan", "build phase 2", "start building docs/plans/mvp.md". Not for
  writing the plan (use ceh-build-planning:write-build-plan) or checking finished code against it
  (use ceh-check-build-against-plan:check-build-against-plan).
argument-hint: "[plan-file] [phase]"
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Implement From a Plan

Build a plan one phase at a time, and prove each phase with its own check before starting the
next. The plan format is in `${CLAUDE_SKILL_DIR}/references/plan-format.md`. Done means every
targeted phase is `done` with evidence in the plan, or the run stopped at a named phase with the
reason recorded.

## Procedure

1. **Find the plan.** Take the path from the arguments. Otherwise look in the plans folder for a
   plan with `status: ready` or `building`, and when there are several, take the most recently
   created and say which. With no plan at all, write a minimal one from the request in the plan
   format: Goal, Scope, and phases with checks, every assumption under Open. Say that you did,
   because the user may have expected a plan to exist.
2. **Read the whole plan before any code.** Design is binding. An Open item marked as blocking
   stops the run before it starts. Set `status: building`.
3. **Build each targeted phase in order.** The target is the named phase, or by default every
   `todo` phase. Skip `done` phases. At an `unplanned` phase, stop: it needs planning first.
   For each phase:
   1. Say which phase you are starting and what it builds, in one line.
   2. Write the failing test for the behavior the phase adds, and run it to see it fail. When
      `ceh-testing` is installed, `ceh-testing:write-test-first` sets out how.
   3. Implement what **Builds** names, and nothing else.
   4. Run the phase's **Check**. When it fails, fix and rerun. When the same failure comes back
      after two fixes, stop: record the failure and what you tried in the phase's Status, leave
      it `todo`, and report. A third blind fix rarely works, and the next session needs the
      record.
   5. Set the phase's Status to `done` with its evidence: the commit, or the check command and
      one line of its passing output.
4. **Close the plan.** When every phase is `done`, set `status: built`.

## Rules

- Build only what the phase names. A gap you find in the plan goes under Open with the
  assumption you took, never into code as unplanned scope.
- When the code has to depart from Design, edit the Design line in the plan and give the reason in
  the phase's Status, so the plan stays true to the code.
- A phase is `done` only on a passing Check run after its last edit. A check you could not run
  leaves the phase `todo`, with the reason in its Status.

## Output

After the run, report per phase: done or stopped, the Check command and its result, assumptions
taken, and anything not verified with the command the user should run.

## Stop conditions

- An Open item blocks building, or the next phase is `unplanned` → stop and name it. With
  `ceh-build-planning` installed, `ceh-build-planning:write-build-plan` plans it.
- A Check needs a secret, a service, or a device the session cannot reach → stop at that phase,
  record what it needs, and report. Never mark it `done` on a skipped check.
- The same check failure survives two fixes → stop as in step 3.4.
