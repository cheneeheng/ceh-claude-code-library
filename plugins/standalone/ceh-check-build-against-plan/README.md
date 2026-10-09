# ceh-check-build-against-plan

Check whether finished code is what its plan said to build. Tests show that what exists works.
This check shows whether what exists is what was planned: every planned item built, nothing built
that the plan left out, and each phase's check still passing.

It reads the plan format `ceh-build-planning` writes, copied into
`skills/check-build-against-plan/references/plan-format.md`. Without a plan, it checks against the
spec you name, so it works installed alone.

## Skills

| Skill                      | When it loads                                 | What it does                                                                                                                                                                                                                                                                                                                                             |
| -------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `check-build-against-plan` | When asking whether the code matches the plan | Lists every plan item, marks each Built, Gap, Deviation, Extra, Failing, or Cannot verify with quoted evidence, and reruns each phase's check. Report-only unless asked to fix. Say "gate it" to have two fresh reviewers recheck the fix, both required to pass, for up to three rounds. It's working if the report opens with a `Build vs plan` table. |

**Manual trigger:** `/ceh-check-build-against-plan:check-build-against-plan [plan-file]`, or say
`"does the code match the plan"` / `"did we build what we planned"`.

## Not this plugin

- Reviewing one diff or pull request: `ceh-git-workflow:code-review`, which also checks a diff
  against a linked spec.
- Finding bugs in working code: `ceh-testing`.
