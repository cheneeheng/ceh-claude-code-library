# ceh-build-from-plan

Build a written plan one phase at a time, and prove each phase with its own check before starting
the next. The evidence goes back into the plan, so the plan always says what is built and how it
was proven.

It reads the plan format `ceh-build-planning` writes, copied into
`skills/implement-from-plan/references/plan-format.md`. Without a plan, it writes a minimal one from
the request first, so it works installed alone.

## Skills

| Skill                 | When it loads                             | What it does                                                                                                                                                                                                                                                                             |
| --------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `implement-from-plan` | Pointing at a plan and asking to build it | Per phase: writes the failing test first, implements only what the phase names, runs the phase's check, and records the evidence. Stops after two failed fixes of the same failure. It's working if each finished phase's Status in the plan reads `done` with a commit or check output. |

**Manual trigger:** `/ceh-build-from-plan:implement-from-plan [plan-file] [phase]`, or say
`"build from the plan"` / `"build phase 2"`.

## Not this plugin

- Writing the plan: `ceh-build-planning`.
- Checking finished code against the plan: `ceh-check-build-against-plan`.
- How to write the code itself: the stack plugins (`ceh-python-service`, `ceh-web-frontend`, and
  the rest) load at their own moments while this skill runs.
