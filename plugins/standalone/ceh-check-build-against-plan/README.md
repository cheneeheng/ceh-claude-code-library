# ceh-check-build-against-plan

Check whether finished code or docs is what its plan said to build. Tests show that what exists
works. This check shows whether what exists is what was planned: every planned item built, nothing
built that the plan left out, and each phase's check still passing.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). The plan check needs
[uv](https://docs.astral.sh/uv/), which installs pydantic and PyYAML on first use. Without uv, the
check says once per session that the file was not checked.

It reads the plan format `ceh-build-plan` writes. Without a plan, it checks against the spec you
name, so it works installed alone.

## Skills

| Skill                      | Say or type                                                                                                                          | What it does                                                                                                                                                                                                                   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `check-build-against-plan` | "does the code match the plan", "did we build what we planned", `/ceh-check-build-against-plan:check-build-against-plan [plan-file]` | Lists every plan item, marks each Built, Gap, Deviation, Extra, Failing, or Cannot verify with quoted evidence, and reruns each phase's check. Report-only unless asked to fix. The report opens with a `Build vs plan` table. |

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled. They act only on YAML plans, and are
the same hooks `ceh-build-plan` ships, so the check works with this plugin installed alone.
[Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                                    |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Artifact check       | Checks each plan in `.agents_workspace/product/plan/` when it is written. Errors go back to the agent to fix, and the Markdown beside the YAML is rendered only once the YAML is valid. |
| Generated-file guard | Stops a hand edit to a Markdown file that is generated from a YAML file, so the edit is not lost at the next render.                                                                    |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                                       |
| -------------------- | -------------------- | -------------------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns both hooks off                                                                   |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook script names to skip, such as `artifact-render-hook,generated-md-guard` |

## How it works

### Gate the fix with two reviewers

When you ask it to fix the gaps, say "gate it" to have two fresh reviewers recheck the fix, both
required to pass, for up to three rounds.

## Not this plugin

- Reviewing one diff or pull request: `ceh-git-workflow:write-code-review`, which also checks a diff
  against a linked spec.
- Finding bugs in working code: `ceh-testing`.
- Writing or reviewing the plan itself: `ceh-build-plan`.

## Where its files live

The plugin saves and reads product files in `.agents_workspace/product/`. Each check appends a
Checked line to the plan's append-only `## Record` in `.agents_workspace/product/plan/`. A project
with a root `product/` folder moves each file to the same sub-path under
`.agents_workspace/product/`, or names its own location in `CLAUDE.md`. A linked worktree gets a workspace only when `.agents_workspace/` is a git repo, so
building in a worktree without one needs the plan's path passed by hand.
