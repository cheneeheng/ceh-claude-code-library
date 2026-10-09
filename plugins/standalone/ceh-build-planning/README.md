# ceh-build-planning

Decide how to build something before any code is written: a new app to its MVP, or one feature in
an existing codebase. The result is one committed plan file an agent can build from without asking
again.

The plan is the handoff between the lifecycle stages. `ceh-build-from-plan` builds it phase by
phase, and `ceh-check-build-against-plan` checks the finished code against it. Each of the three
plugins works installed alone, and they share the plan format in
`skills/write-build-plan/references/plan-format.md`.

## Skills

| Skill              | When it loads                                    | What it does                                                                                                                                                                                                                                                                      |
| ------------------ | ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-build-plan` | Before building an app or feature, to decide how | Triages the work as spike, bounded, or architectural, draws In and Out scope, plans in detail only as far as the build is foreseeable, and writes phases that each end in a runnable check. It's working if it announces the triage label first and saves `docs/plans/<slug>.md`. |

**Manual trigger:** `/ceh-build-planning:write-build-plan [what to build]`, or say
`"plan this app"` / `"plan the next feature"`.

## Plan mode is for the research before this skill, not for running it

Claude Code's plan mode blocks file writes until you approve a plan, and this skill's deliverable
is a file. Use plan mode to explore an unfamiliar codebase first, then leave it and run the skill.

## Not this plugin

- Whether the product is worth building, and who pays: use `ceh-business-plan`. When a
  `BUSINESS_PLAN.md` exists, the build plan points to it for the goal and target user instead of
  restating them.
- Building or checking the plan: `ceh-build-from-plan` and `ceh-check-build-against-plan`.
