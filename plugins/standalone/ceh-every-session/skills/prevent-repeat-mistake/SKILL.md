---
name: prevent-repeat-mistake
description: >-
  Load this skill when the same mistake has happened more than once: pick the strongest fix that
  would have caught it (a setting or check before written guidance) and prove it on the real
  mistake. Trigger on "you did X again", "I keep telling you", "make sure this never happens again".
argument-hint: "[the mistake | retro]"
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Prevent a repeat mistake

Turn a mistake that keeps coming back into a fix that stops it, placed at the strongest level that
works. The files can be anything: code, a knowledge base of notes, plans, a roadmap, a business
strategy. Done means each mistake has a fix that is either in place and proven, or drafted and
waiting for the user's approval.

## Procedure

1. **Name the mistake from evidence.** Quote what went wrong: the tool call, the file and line,
   the wrong output, and the correction that preceded it. "Was sloppy" is not a mistake, "wrote
   dates as `10/09/2026` in `roadmap.md:14` after being told ISO dates" is. If you cannot quote it,
   stop: there is nothing to fix yet. In `retro` mode, list every correction from this session that
   happened twice or more, then run steps 2 to 5 on each, most costly first, at most five.
2. **Climb the ladder, strongest first.** Stop at the first rung that would have caught this exact
   mistake:

   | Rung                    | In code                                          | In notes, plans, or documents                                       |
   | ----------------------- | ------------------------------------------------ | ------------------------------------------------------------------- |
   | 1. Remove the cause     | Delete the second code path, merge the duplicate | One source note instead of copies, a template, rename what misleads |
   | 2. Claude Code setting  | A `permissions.deny` rule in `settings.json`     | The same: deny writes to a folder that must not change              |
   | 3. Check at write time  | A type, a lint rule, a hook                      | A frontmatter schema, a link or date-format check, a hook           |
   | 4. Check before landing | A test, a CI job                                 | A validator script, a CI job, a checklist the file itself carries   |
   | 5. Written guidance     | `CLAUDE.md`, a skill, a code comment at the trap | `CLAUDE.md`, memory, a style note in the folder                     |

   Rung 5 is for judgment calls nothing mechanical can check. Choosing it for a mistake that a
   pattern match would catch is choosing the rung that already failed.

3. **Build or draft the fix.** Build rungs 3 and 4 when they live in the current repository and
   touch nothing else: they are checks that prove work, and the contract allows them. Draft, do
   not apply, anything that changes how later sessions behave or rewrites the user's content:
   rung 1, rung 2, a hook, and every rung 5 edit (`CLAUDE.md`, memory, a skill, a plugin). Show the
   draft and wait for approval.
4. **Prove it.** Replay the real mistake against the fix and show it fails, then show the correct
   version passes. Keep the failing case as a test or fixture where the repo has a place for one.
   A rung 5 fix cannot be proven this way: say so, and say why no higher rung fit.
5. **Report** in the format under Output.

## Rules

- One mistake per fix. A fix aimed at two mistakes usually stops neither.
- Fix the class, not the instance: the check catches every future `10/09/2026`, not only the one
  in `roadmap.md`.
- A new check must not fail on correct existing files. Run it over what is already there before
  calling it done, and fix or exempt real violations only with the user's approval.
- Correcting the file the mistake landed in is part of the fix, but it is not the fix.

## Output

```markdown
| Mistake    | Evidence                        | Rung  | Fix                         | Proof                                           | Status                        |
| ---------- | ------------------------------- | ----- | --------------------------- | ----------------------------------------------- | ----------------------------- |
| <one line> | <path:line or quoted tool call> | <1-5> | <what was added or drafted> | <fails on the real mistake: yes / not provable> | <applied / awaiting approval> |
```

Below the table, for each rung chosen, one line on why the rungs above it did not fit.
