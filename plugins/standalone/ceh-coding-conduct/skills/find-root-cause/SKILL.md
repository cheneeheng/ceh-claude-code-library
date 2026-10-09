---
name: find-root-cause
description: >-
  Load this skill when something is broken and its cause is not yet known, before any fix is
  written: reproduce the symptom with one command, list falsifiable hypotheses, gather evidence
  to kill them, and name the cause with the chain from cause to symptom. Trigger on "debug this",
  "why is this failing", "figure out what's wrong", a stack trace with no obvious cause, or a
  second fix attempt that did not hold. Not for writing the regression test once the cause is
  known (use ceh-testing:test-a-bug-fix).
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Find Root Cause

Find why something fails before changing any code to fix it. The task is done when you can name
the cause at a `file:line` or a condition, show the evidence that links it to the symptom, and
predict one observation you have not made yet that then comes true.

## Procedure

1. **Make one command go red on the exact symptom.** A test, a script, a `curl`, or a CLI call
   that shows the reported failure, not a nearby one. Run it and keep its output. Form no theory
   before this: a theory formed without a reproduction picks which evidence you go looking for.
   If it will not fail on demand, run it in a loop or force the timing, as in
   `ceh-testing:test-a-bug-fix` "When it will not reproduce deterministically".
2. **Read the whole failure.** The first error, not the last: later errors are often fallout. In
   a stack trace, find the deepest frame in this repo's code, and read that code before going
   further.
3. **Write 3 to 5 hypotheses, each with what would refute it.** "The cache returns a stale row"
   is refuted by "the row read at line 40 matches the database". A hypothesis no observation can
   refute is a mood, so rewrite it or drop it. Order them by how cheap they are to test, then by
   how likely they are.
4. **Gather evidence, one variable at a time.** Log or print at the boundary in question, step
   through it in a debugger, capture the request or the trace, or `git bisect run` the command
   from step 1 when the behavior used to work. Mark each hypothesis refuted, standing, or
   confirmed, with the output that decided it.
5. **Narrow until one cause remains.** Halve the input, the code path, or the commit range, and
   rerun the step 1 command after each cut. When every hypothesis is refuted, go back to step 3
   with what the evidence showed, and do not reuse the refuted ones.
6. **Confirm by prediction.** From the cause, predict something new: another input that must
   also fail, or one that must pass. Run it. A cause that predicts nothing new is still a guess.
7. **Remove the instrumentation** you added, then hand over with the Output below.

## Rules

- **No fix to test a theory.** A change that makes the symptom go away without a confirmed
  cause hides the bug at best and moves it at worst. Change code to gather evidence, never to
  see whether the failure stops.
- **After two failed fixes, attack the premise.** Stop proposing fixes. List what every attempt
  so far assumed, then check each assumption directly: the code that runs is the code you are
  reading (right file, branch, build, installed version), the config and environment are the
  ones you think, the input is what the logs claim, and the cache or build output is not stale.
- **Evidence is output you ran.** A conclusion from reading code is a hypothesis until a command
  confirms it, and the report labels it inferred.
- **A cause in a dependency is reported, not patched.** Name the package, version, and upstream
  issue if one exists, and propose the workaround in this repo's code.

## Output

```markdown
**Symptom:** `<command>` → <the failing output line>

| Hypothesis | Refuted by                       | Result                                        |
| ---------- | -------------------------------- | --------------------------------------------- |
| <claim>    | <observation that would kill it> | refuted / confirmed: <output that decided it> |

**Cause:** <file:line or condition>: <one sentence on the chain from cause to symptom>

**Prediction:** `<command>` → <result predicted and seen>

**Status:** verified (prediction held) or inferred (<what stayed unrun and why>)
```

## Stop conditions

- The symptom does not reproduce after a loop and forced timing → report what was tried and
  what each attempt showed. Do not ship a speculative fix.
- Confirming the cause needs a production system, real customer data, or a paid service → stop
  and name the exact check the user should run.

## Hands off to

Once the cause is confirmed, `ceh-testing:test-a-bug-fix` turns the step 1 command into a
regression test and drives the fix, when `ceh-testing` is installed. Otherwise write the failing
test before the fix yourself.
