# ceh-check-build-against-plan

Check whether finished code is what its plan said to build. Tests show that what exists works.
This check shows whether what exists is what was planned: every planned item built, nothing built
that the plan left out, and each phase's check still passing.

It reads the plan format `ceh-build-planning` writes, copied into
`skills/check-build-against-plan/references/plan-schema.md`. Without a plan, it checks against the
spec you name, so it works installed alone.

## Skills

| Skill                      | When it loads                                 | What it does                                                                                                                                                                                                                                                                                                                                             |
| -------------------------- | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `check-build-against-plan` | When asking whether the code matches the plan | Lists every plan item, marks each Built, Gap, Deviation, Extra, Failing, or Cannot verify with quoted evidence, and reruns each phase's check. Report-only unless asked to fix. Say "gate it" to have two fresh reviewers recheck the fix, both required to pass, for up to three rounds. It's working if the report opens with a `Build vs plan` table. |

**Manual trigger:** `/ceh-check-build-against-plan:check-build-against-plan [plan-file]`, or say
`"does the code match the plan"` / `"did we build what we planned"`. Each check appends a Checked
line to the plan's append-only `## Record` in `product/plans/`.

## Hooks

The plugin ships two hooks (`hooks/hooks.json`) that activate automatically when the plugin is
enabled. They act only on `plan/v2` plans, the YAML format in the skill's
`references/plan-schema.md`, and are the same hooks `ceh-build-planning` ships, so the check works
with this plugin installed alone.

| Hook                 | Event                                        | Script                    | Default |
| -------------------- | -------------------------------------------- | ------------------------- | ------- |
| Artifact check       | `PostToolUse` (`Edit`, `Write`, `MultiEdit`) | `artifact-render-hook.py` | on      |
| Generated-file guard | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `generated-md-guard.py`   | on      |

The artifact check runs `scripts/artifact.py render` on each write to a `product/plans/*.yaml`.
Errors go back to the agent to fix, and the Markdown beside the YAML is rendered only once the
YAML is valid. It needs [uv](https://docs.astral.sh/uv/), which installs pydantic and PyYAML on
first use. Without uv, the check says once per session that the file was not checked. The guard
denies a hand edit to a Markdown file whose frontmatter says `generated_from:`. The skill also
runs `artifact.py check` before it reads a `plan/v2` plan.

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                                       |
| -------------------- | -------------------- | -------------------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns both hooks off                                                                   |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook script names to skip, such as `artifact-render-hook,generated-md-guard` |

## Not this plugin

- Reviewing one diff or pull request: `ceh-git-workflow:code-review`, which also checks a diff
  against a linked spec.
- Finding bugs in working code: `ceh-testing`.
