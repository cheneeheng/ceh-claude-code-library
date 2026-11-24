# ceh-build-plan

Decide how to build something before anything is built, then build it one phase at a time. It
works for a new app up to its MVP, one feature in an existing codebase, or a new document set.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). The plan checks need
[uv](https://docs.astral.sh/uv/). Without uv everything still works, and the agent says once per
session that a file went unchecked.

## Skills

| Skill                    | Say or type                                                                                                                                                                                             | What it does                                                                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-technical-design` | "write the technical design", "pick the stack", `/ceh-build-plan:write-technical-design`                                                                                                                | Writes the shared decisions (stack, data model, components, interfaces, ownership, deployment) into `ARCHITECTURE.yaml`, each with its reason and the option it rejected. |
| `write-build-plan`       | Loads by itself before the first edit of a change with no plan, such as "build me X" or "add X to the app". Or "plan this app", `/ceh-build-plan:write-build-plan [what to build \| <draft plan path>]` | Sizes the work, draws what is in and out of scope, and writes phases that each end in a check you can run. Given a draft plan, it completes that plan in place.           |
| `review-build-plan`      | "review this plan", `/ceh-build-plan:review-build-plan [plan-file]`                                                                                                                                     | Reviews the plan on scope, engineering, content, design and developer experience, and quotes the plan line behind each finding. It changes nothing unless asked to fix.   |
| `implement-from-plan`    | "build from the plan", "build phase 2", `/ceh-build-plan:implement-from-plan [plan-file] [phase]`                                                                                                       | Per phase: writes the failing check first, builds only what the phase names, runs the check, and records the evidence. It stops after two failed fixes of one failure.    |

## Agents

This plugin has no agents.

## Hooks

Three hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Artifact check       | Checks each plan, and each architecture, vision, strategy and requirements file, when it is written. Errors go back to the agent to fix.                 |
| Generated-file guard | Stops a hand edit to a Markdown file that is generated from a YAML file, and names the YAML to edit instead, so the edit is not lost at the next render. |
| Build record guard   | Stops a "Built Phase" line being added to a plan unless `implement-from-plan` ran in the session, so the plan never records a build that was not proven. |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                 | Default              | Effect                                                                                                 |
| ------------------------ | -------------------- | ------------------------------------------------------------------------------------------------------ |
| `CEH_ARTIFACT_CHECK`     | unset (check on)     | `off` turns the artifact check and the generated-file guard off                                        |
| `CEH_BUILD_RECORD_GUARD` | unset (guard on)     | `off` allows Built Phase lines without `implement-from-plan`                                           |
| `CEH_DISABLED_HOOKS`     | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard`, `build-record-guard` |

## How it works

### How the four skills fit together

1. `write-technical-design` settles the decisions several features share, once per product. Skip
   it for a single feature.
2. `write-build-plan` writes one plan file an agent can build from without asking again, then
   starts the review by itself.
3. `review-build-plan` reads the plan from a fresh context and gives a verdict before anyone
   builds.
4. `implement-from-plan` builds the plan phase by phase and proves each phase with its own check
   before starting the next. Without a plan, it writes a minimal one from the request first.

The evidence goes back into the plan, so the plan always says what is built and how it was proven.

### With a product requirements file

When the repo has a `.agents_workspace/product/PRD.yaml`, written by
`ceh-product-direction:write-product-requirements`, the plan comes from its feature list:

- `write-build-plan` takes the matched feature's requirements as the plan's scope and its
  acceptance items as phase checks, then marks the feature `planned`.
- `implement-from-plan` marks the feature `built` once every plan it lists is built.
- A request the file does not list is still planned, and the reply says so.
- A request that names a replaced feature is planned from the feature that replaced it.

Without the file nothing changes.

### Plan mode comes before `write-build-plan`, not during it

Claude Code's plan mode blocks file writes until you approve a plan, and `write-build-plan`'s
result is a file. Use plan mode to explore an unfamiliar codebase first, then leave it and run the
skill.

## Not this plugin

- Whether the product is worth building, and who pays: `ceh-product-direction`.
- Checking finished code against the plan: `ceh-check-build-against-plan`.
- How to write the code or docs themselves: the stack plugins (`ceh-python-service`,
  `ceh-web-frontend`, and the rest) and `ceh-documentation`, which load at their own moments while
  `implement-from-plan` runs.

## Where its files live

The plugin saves and reads its files in `.agents_workspace/product/`, and a built plan stays in
`.agents_workspace/product/plan/` with its history. A project with a root `product/` folder moves
each file to the same sub-path under `.agents_workspace/product/`, or names its own location in
`CLAUDE.md`. A git worktree has a workspace only when `.agents_workspace/` is a git repo. Otherwise
pass the plan's path by hand when building in a worktree.
