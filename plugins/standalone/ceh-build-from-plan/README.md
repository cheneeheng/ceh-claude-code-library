# ceh-build-from-plan

Build a written plan one phase at a time, and prove each phase with its own check before starting
the next. The evidence goes back into the plan, so the plan always says what is built and how it
was proven.

It reads the plan format `ceh-build-planning` writes, copied into
`skills/implement-from-plan/references/plan-schema.md`. Without a plan, it writes a minimal one from
the request first, so it works installed alone. A built plan stays in `product/plans/` with an
append-only `## Record`, so the build keeps its history.

## Skills

| Skill                 | When it loads                             | What it does                                                                                                                                                                                                                                                                             |
| --------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `implement-from-plan` | Pointing at a plan and asking to build it | Per phase: writes the failing test first, implements only what the phase names, runs the phase's check, and records the evidence. Stops after two failed fixes of the same failure. It's working if each finished phase's Status in the plan reads `done` with a commit or check output. |

**Manual trigger:** `/ceh-build-from-plan:implement-from-plan [plan-file] [phase]`, or say
`"build from the plan"` / `"build phase 2"`.

## Hooks

The plugin ships a hook (`hooks/hooks.json`) that activates automatically when the plugin is
enabled.

| Guard                                     | Event                                       | Script                  | Default |
| ----------------------------------------- | ------------------------------------------- | ----------------------- | ------- |
| [Build record guard](#build-record-guard) | `PreToolUse` (`Edit`, `Write`, `MultiEdit`) | `build-record-guard.py` | on      |

### Build record guard

Denies an edit that adds a `- YYYY-MM-DD Built Phase` line to a plan in `product/plans/`, unless
`implement-from-plan` was started in the session, by the Skill tool or its slash command. A Built
Phase line is the plan's evidence that a phase was built test first and proven by its own check,
so a line written by hand records a build that procedure never ran. It happened once: a session
hand-wrote three Built lines, recorded in `product/retros/2026-10-26-repeat-mistake.md` in this
library's repo. Built lines already in the file do not count, so rewriting a plan that has them
passes. The guard fails open: unparseable input or a missing transcript allows the edit.

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to undo it.

| Variable                 | Default              | Effect                                                                          |
| ------------------------ | -------------------- | ------------------------------------------------------------------------------- |
| `CEH_BUILD_RECORD_GUARD` | unset (guard on)     | `off` allows Built Phase lines without `implement-from-plan`                    |
| `CEH_DISABLED_HOOKS`     | unset (all hooks on) | Comma-separated hook script names to skip; `build-record-guard` switches it off |

## Not this plugin

- Writing the plan: `ceh-build-planning`.
- Checking finished code against the plan: `ceh-check-build-against-plan`.
- How to write the code itself: the stack plugins (`ceh-python-service`, `ceh-web-frontend`, and
  the rest) load at their own moments while this skill runs.
