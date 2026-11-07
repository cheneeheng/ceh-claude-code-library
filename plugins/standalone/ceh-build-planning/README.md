# ceh-build-planning

Decide how to build something before any code is written: a new app to its MVP, or one feature in
an existing codebase. The result is one committed plan file an agent can build from without asking
again.

The plan is the handoff between the lifecycle stages. `ceh-build-from-plan` builds it phase by
phase, and `ceh-check-build-against-plan` checks the finished code against it. Each of the three
plugins works installed alone, and they share the plan format in `references/plan-schema.md`.

## Skills

| Skill               | When it loads                                                                                                                                                      | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-build-plan`  | Before the first edit of an unplanned change: a new app or tool, a feature added to existing code even a quick one, or a multi-file change such as a retro's fixes | Triages the work as spike, bounded, or architectural, draws In and Out scope, plans in detail only as far as the build is foreseeable, and writes phases that each end in a runnable check. Given a draft plan's path, it completes that plan in place and keeps its goal and Scope In items word for word. It's working if it announces the triage label first and saves `product/plans/<slug>.yaml` with its rendered `.md`, then hands every saved plan to `review-build-plan`. |
| `review-build-plan` | After a plan or spec is written, before anyone builds from it, even for a quick look                                                                               | Reviews it from a fresh context through scope, engineering, design, and developer-experience lenses, checks it for gaps, quotes the plan line behind each blocking or advisory finding, and gives a verdict. Report-only unless asked to fix. It's working if it saves `.agents_workspace/product/plan-reviews/<slug>-<YYYY-MM-DD>.md` and the reply gives the verdict, the blocking findings, and that path.                                                                      |

**Manual trigger:** `/ceh-build-planning:write-build-plan [what to build | <draft plan path>]`, or say
`"plan this app"` / `"plan the next feature"`. `/ceh-build-planning:review-build-plan [plan-file]`,
or `"review this plan"`.

## Hooks

The plugin ships two hooks (`hooks/hooks.json`) that activate automatically when the plugin is
enabled. They act only on `plan/v2` plans, the YAML format in `references/plan-schema.md`. The
skills still write `plan/v1` Markdown, so today they act only on a plan YAML written by hand.

| Hook                 | Event                                        | Script                    | Default |
| -------------------- | -------------------------------------------- | ------------------------- | ------- |
| Artifact check       | `PostToolUse` (`Edit`, `Write`, `MultiEdit`) | `artifact-render-hook.py` | on      |
| Generated-file guard | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `generated-md-guard.py`   | on      |

The artifact check runs `scripts/artifact.py render` on each write to a `product/plans/*.yaml`, or
to any YAML whose `schema:` names a model in this plugin. Errors go back to the agent to fix, and
the Markdown beside the YAML is rendered only once the YAML is valid. It needs
[uv](https://docs.astral.sh/uv/), which installs pydantic and PyYAML on first use. Without uv, the
check says once per session that the file was not checked. The guard denies a hand edit to a
Markdown file whose frontmatter says `generated_from:`, and names the YAML to edit instead.

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                                       |
| -------------------- | -------------------- | -------------------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns both hooks off                                                                   |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook script names to skip, such as `artifact-render-hook,generated-md-guard` |

## Plan mode is for the research before this skill, not for running it

Claude Code's plan mode blocks file writes until you approve a plan, and this skill's deliverable
is a file. Use plan mode to explore an unfamiliar codebase first, then leave it and run the skill.

## Not this plugin

- Whether the product is worth building, and who pays: use `ceh-business-plan`. When a
  `.agents_workspace/product/business/BUSINESS_PLAN.md` exists, the build plan points to it for the goal and target user
  instead of restating them.
- Building or checking the plan: `ceh-build-from-plan` and `ceh-check-build-against-plan`.
