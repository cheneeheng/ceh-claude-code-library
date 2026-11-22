# ceh-build-plan

Decide how to build something before anything is built: a new app to its MVP, one feature in an
existing codebase, or a new document set. The result is one plan file an agent can build from without asking
again. Then build that plan one phase at a time, and prove each phase with its own check before
starting the next. The evidence goes back into the plan, so the plan always says what is built and
how it was proven.

The plan is the handoff between the lifecycle stages. `implement-from-plan` builds it phase by
phase, and `ceh-check-build-against-plan` checks the finished build against it. Each of the two
plugins works installed alone, and each of their skills carries the plan format in its own
`references/plan-schema.md`. Without a plan, `implement-from-plan` writes a minimal one from the
request first. A built plan stays in `.agents_workspace/product/plan/` with an append-only `## Record`, so the build
keeps its history.

When the repo has a `.agents_workspace/product/PRD.yaml`, written by
`ceh-product-direction:write-product-requirements`, the plan comes from its feature list.
`write-build-plan` takes the matched feature's requirements as the plan's Scope In and its
acceptance items as phase checks, then adds the plan to the feature and sets it `planned`.
`implement-from-plan` sets the feature `built` once every plan it lists is built. A request the
PRD does not list is still planned, and the reply says so. A request that names a replaced feature
is planned from the feature that replaced it. Without a PRD nothing changes.

## Skills

| Skill                    | When it loads                                                                                                                                                               | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-technical-design` | Before the first feature of a product is planned: "write the technical design", "pick the stack"                                                                            | Settles the decisions several features share (stack, data model, components, interfaces, ownership, deployment), writes each as one entry of the Technical Design section of `.agents_workspace/product/ARCHITECTURE.yaml`, found by its topic: the contract as Markdown (lists, tables, code) with small parts of at most 30 lines, and the reason with the option it rejected. It also draws the diagrams they imply, marked `planned: true`. A later change edits the entry in place and adds one Key Decisions entry. It's working if the reply lists each entry by topic and the rendered `ARCHITECTURE.md` shows `**Planned:** not built yet.` under each new diagram. |
| `write-build-plan`       | Before the first edit of an unplanned change: a new app, tool or doc set, a feature added to existing code even a quick one, or a multi-file change such as a retro's fixes | Triages the work as spike, bounded, or architectural, draws In and Out scope, plans in detail only as far as the build is foreseeable, and writes phases that each end in a runnable check. Given a draft plan's path, it completes that plan in place and keeps its goal and Scope In items word for word. It's working if it announces the triage label first and saves `.agents_workspace/product/plan/<YYYYMMDD-HHMMSS>-<slug>.yaml` with its rendered `.md`, one plan per functionality, then hands the plans it saved in the session to `review-build-plan` in one batch.                                                                                              |
| `review-build-plan`      | After a plan or spec is written, before anyone builds from it, even for a quick look                                                                                        | Reviews it from a fresh context through scope, engineering, content, design, and developer-experience lenses, checks it for gaps, quotes the plan line behind each blocking or advisory finding, and gives a verdict. Report-only unless asked to fix. It's working if it adds a round to the plan's one review file, `.agents_workspace/product/review/plan/<YYYYMMDD-HHMMSS>-<plan-slug>.yaml`, with its rendered `.md`, ticking off findings the plan now fixes, and the reply gives the verdict, the blocking findings, the findings still open, and that path.                                                                                                          |
| `implement-from-plan`    | Pointing at a plan and asking to build it                                                                                                                                   | Per phase: writes the failing test or acceptance check first, implements only what the phase names, runs the phase's check, and records the evidence. Stops after two failed fixes of the same failure. It's working if each finished phase's Status in the plan reads `done` with a commit or check output.                                                                                                                                                                                                                                                                                                                                                                 |

**Manual trigger:** `/ceh-build-plan:write-technical-design`, or say
`"write the technical design"`. `/ceh-build-plan:write-build-plan [what to build | <draft plan path>]`, or say
`"plan this app"` / `"plan the next feature"`. `/ceh-build-plan:review-build-plan [plan-file]`,
or `"review this plan"`. `/ceh-build-plan:implement-from-plan [plan-file] [phase]`, or say
`"build from the plan"` / `"build phase 2"`.

## Hooks

The plugin ships three hooks (`hooks/hooks.json`) that activate automatically when the plugin is
enabled. The artifact check and the generated-file guard act on `plan/v2` plans, the YAML format in each skill's
`references/plan-schema.md`, which the skills write, and on the `ARCHITECTURE.yaml`,
`VISION.yaml`, `STRATEGY.yaml` and `PRD.yaml` the skills write or check before reading, because
the skills carry those models too.

| Hook                 | Event                                        | Script                    | Default |
| -------------------- | -------------------------------------------- | ------------------------- | ------- |
| Build record guard   | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `build-record-guard.py`   | on      |
| Artifact check       | `PostToolUse` (`Edit`, `Write`, `MultiEdit`) | `artifact-render-hook.py` | on      |
| Generated-file guard | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `generated-md-guard.py`   | on      |

The artifact check runs `scripts/artifact.py render` on each write to a `.agents_workspace/product/plan/*.yaml`, or
to any YAML whose `schema:` names a model in this plugin. Errors go back to the agent to fix, and
the Markdown beside the YAML is rendered only once the YAML is valid. It needs
[uv](https://docs.astral.sh/uv/), which installs pydantic and PyYAML on first use. Without uv, the
check says once per session that the file was not checked. The guard denies a hand edit to a
Markdown file whose frontmatter says `generated_from:`, and names the YAML to edit instead.
`implement-from-plan` also runs `artifact.py check` before it acts on a `plan/v2` plan.

The build record guard denies an edit that adds a `- YYYY-MM-DD Built Phase` line to a plan in
`.agents_workspace/product/plan/`, unless `implement-from-plan` was started in the session, by the Skill tool or
its slash command. A Built Phase line is the plan's evidence that a phase was built test first and
proven by its own check, so a line written by hand records a build that procedure never ran. It
happened once: a session hand-wrote three Built lines, recorded in the repeat-mistake report of
2026-10-26 in this library's repo. Built lines already in the
file do not count, so rewriting a plan that has them passes. The guard fails open: unparseable
input or a missing transcript allows the edit. In a `plan/v2` YAML plan, it guards a new
`event: Built Phase` record entry the same way.

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                 | Default              | Effect                                                                                                                                     |
| ------------------------ | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `CEH_BUILD_RECORD_GUARD` | unset (guard on)     | `off` allows Built Phase lines without `implement-from-plan`                                                                               |
| `CEH_ARTIFACT_CHECK`     | unset (check on)     | `off` turns the artifact check and the generated-file guard off                                                                            |
| `CEH_DISABLED_HOOKS`     | unset (all hooks on) | Comma-separated hook script names to skip, such as `artifact-render-hook,generated-md-guard`; `build-record-guard` switches that guard off |

## Plan mode is for the research before `write-build-plan`, not for running it

Claude Code's plan mode blocks file writes until you approve a plan, and `write-build-plan`'s
deliverable is a file. Use plan mode to explore an unfamiliar codebase first, then leave it and
run the skill.

## Not this plugin

- Whether the product is worth building, and who pays: use `ceh-product-direction`. No skill here
  reads the business plan, so its tests and dates never become a plan's goal.
- Checking finished code against the plan: `ceh-check-build-against-plan`.
- How to write the code or docs themselves: the stack plugins (`ceh-python-service`,
  `ceh-web-frontend`, and the rest) and `ceh-documentation` load at their own moments while
  `implement-from-plan` runs.

## Where its files live

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`. A project with a root `product/` moves each file to the same sub-path there, or names its location in `CLAUDE.md`. A linked worktree gets a workspace only when `.agents_workspace/` is a git repo, so building in a worktree without one needs the plan's path passed by hand.
