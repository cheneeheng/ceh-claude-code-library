# ceh-workflow-builder

Turn repeated product work into something an agent runs: a weekly SEO or usability pass, a
pre-release check, a recurring feature loop. Repetition is the intake test. A workflow exists
because the same steps run again in the same shape and only the input changes, so a one-off or a
task whose steps change every time gets no workflow. The result is one skill when the task is
simple, or a `flow.yaml` config with gates and approvals plus a thin trigger skill, written into the
target repo's `.claude/skills/`.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). The hooks need `python3` on `PATH`.
Checking the workflow spec and run state needs [uv](https://docs.astral.sh/uv/). Without uv the
agent says once per session that the spec went unchecked.

A multi-step workflow runs through the generic runner in the separate `ceh-workflow-runner`
plugin, so that plugin must be installed wherever the flow runs. This plugin is not needed there.
The built artifact lands in the target repo's `.claude/skills/`, so it needs no install step of its
own.

## Skills

| Skill                     | Say or type                                                                                                                                                                               | What it does                                         |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| `interview-workflow-task` | "interview me about this task", "help me spec out this workflow", `/ceh-workflow-builder:interview-workflow-task`. Also loads when `build-agentic-workflow` finds its inputs incomplete.  | Asks the nine questions and writes the workflow spec |
| `build-agentic-workflow`  | "turn this into a workflow", "we run the same check every release", "build an agentic workflow", "I need a skill that calls other skills", `/ceh-workflow-builder:build-agentic-workflow` | Designs and emits the artifact from that spec        |

Either is a valid entry point. `build-agentic-workflow` opens with an intake gate and calls the
interview itself when the task is not yet described, so a user who has nothing written down can
still start there.

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                         |
| -------------------- | -------------------------------------------------------------------------------------------- |
| Artifact check       | Checks a written workflow spec or run state YAML against its model and renders its Markdown. |
| Generated-file guard | Stops a hand edit to the generated Markdown, which the next render would overwrite.          |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                 | Default                       | Effect                                                                                                                 |
| ------------------------ | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK`     | unset (check on)              | `off` turns both hooks off                                                                                             |
| `CEH_DISABLED_HOOKS`     | unset (all hooks on)          | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard`                                       |
| `CEH_WORKFLOW_BUILD_DIR` | `.agents_workspace/workflow/` | Where the interview spec is written while authoring                                                                    |
| `CEH_WORKFLOW_RUN_DIR`   | `.agents_workspace/workflow/` | Where a generated workflow writes its step artifacts and run state, read by `ceh-workflow-runner:run-agentic-workflow` |

## How it works

### One skill or a workflow

The hard part is not writing a `SKILL.md`. Three other tools do that. The hard parts are deciding
whether the task is one skill or a multi-step workflow, and making the handoffs between steps
explicit. A workflow whose steps pass data with no declared shape fails the same way every time: a
later step infers a shape from whatever artifact it finds, infers it wrong, and the run keeps
producing garbage past a green gate.

### The interview

`interview-workflow-task` pulls the task out of your head and onto disk as
`$CEH_WORKFLOW_BUILD_DIR/<name>-workflow-spec.yaml`, one answer for each of nine fixed questions,
with a readable Markdown copy beside it. The builder will not start until all nine are there. It
opens with the repetition test: a task that will not run again in the same shape gets no
spec.

It records unanswered questions as unanswered rather than as "none". Questions 8 (which steps
damage something if run twice) and 9 (which steps are irreversible) are the two people skip, and
assuming them empty is what produces a workflow with no re-run guard that publishes without
pausing.

### The build

`build-agentic-workflow` checks the nine answers exist, applies the one-skill-vs-workflow gate,
decides per step whether it becomes an existing skill, a script, inline prose, or its own step
skill, then emits the set leaf-first so every reference resolves as it is written.

It covers the assumed-capability contract, the six-condition workflow gate, the
step-earns-a-skill test, saved dynamic workflows as an optional stage backend, data-contract
schemas for non-adjacent handoffs (step N to step N+m), the falsifiable-gate rule, and the two run
directories. A workflow comes out as `flow.yaml`, a thin `<name>-flow` trigger skill and an
invocation guide with the interactive and headless commands. Launch arguments, approvals, headless
permissions and the dynamic-workflow setup are documented with the runner in
[`ceh-workflow-runner`](../ceh-workflow-runner/README.md).

Stages go to Claude Code's native capabilities (skills, subagents, scripts, saved dynamic
workflows) wherever they cover the step. The runner adds only what native lacks: approvals between
stages, world checks before a re-run, resume state, and the `FLOW STATUS:` line.

### With nobody to ask

Building asks a person. With nobody to ask (`claude -p`), the build writes a draft to the build
directory, marks every gap, and ends with the questions a person must answer. Nothing lands in
`.claude/skills/` until they agree. Running works interactively and headless.

### Packaging a generated workflow as a plugin

Not automated yet. Keep the output in `.claude/skills/` unless the workflow is shared across repos.
To package it by hand:

1. Create `<plugin>/.claude-plugin/plugin.json` with `name`, `version`, and `description`.
2. Move every `<name>-*` skill directory into `<plugin>/skills/`. The skills' own script paths
   keep working, because `skills/` stays flat.
3. Prefix every Skill tool call with the plugin name: `skill="<name>-step"` becomes
   `skill="<plugin>:<name>-step"`. Plugin skills are namespaced, so an unprefixed call no longer
   resolves. This is the one step a plain copy gets wrong.
4. Check that every call now names a skill that exists in the plugin.

## Not this plugin

- Running a built workflow: `ceh-workflow-runner`.
- Evaluating a skill that already exists.
- Delegating one big task to subagents right now, without producing a reusable artifact.

## Where its files live

| What                                                | Where                                    |
| --------------------------------------------------- | ---------------------------------------- |
| The interview spec and build notes, while authoring | `$CEH_WORKFLOW_BUILD_DIR`                |
| A generated workflow's step artifacts and run state | `$CEH_WORKFLOW_RUN_DIR/<name>/<run-id>/` |
| The built skill or flow                             | the target repo's `.claude/skills/`      |

Each run gets its own `<run-dir>/<name>/<run-id>/`, so a second run never reads the first one's
artifacts, and that directory is expected to be git-ignored.
