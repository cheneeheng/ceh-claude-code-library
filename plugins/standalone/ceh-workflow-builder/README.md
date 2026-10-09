# ceh-workflow-builder

Turn repeated product work into something an agent runs: a weekly SEO or
usability pass, a pre-release check, a recurring feature loop. Repetition is the
intake test. A workflow exists because the same steps run again in the same
shape and only the input changes, so a one-off or a task whose steps change
every time gets no workflow.

The hard part is not writing a `SKILL.md` — three other tools do that. The hard
parts are deciding whether the task is one skill or a multi-step workflow, and
making the handoffs between steps explicit. A workflow whose steps pass data
with no declared shape fails the same way every time: a later step infers a
shape from whatever artifact it finds, infers it wrong, and the run keeps
producing garbage past a green gate.

Target runtime is **Claude Code**. The emitted artifact lands in the target
repo's `.claude/skills/`, so there is no install step. A multi-step workflow
is emitted as a `flow.yaml` config plus a thin trigger skill, and runs through
the generic runner in the separate `ceh-workflow-runner` plugin, so that plugin
must be installed wherever the flow runs. This plugin is not needed there.

Building asks a person. With nobody to ask (`claude -p`), the build writes a
draft to the build directory, marks every gap, and ends with the questions a
person must answer; nothing lands in `.claude/skills/` until they agree.
Running works interactively and headless.

Stages go to Claude Code's native capabilities (skills, subagents, scripts,
saved dynamic workflows) wherever they cover the step. The runner adds only
what native lacks: approvals between stages, world checks before a re-run,
resume state, and the `FLOW STATUS:` line.

How the pieces fit together, with diagrams, is in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). The tests behind the headless
and dynamic-workflow design are in [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md).

## Skills

| Skill                     | Invoke                                          | Does                                              |
| ------------------------- | ----------------------------------------------- | ------------------------------------------------- |
| `interview-workflow-task` | `/ceh-workflow-builder:interview-workflow-task` | Asks the nine questions, writes the workflow spec |
| `build-agentic-workflow`  | `/ceh-workflow-builder:build-agentic-workflow`  | Designs and emits the artifact from that spec     |

Either is a valid entry point. `build-agentic-workflow` opens with an
intake gate and calls the interview itself when the task is not yet described,
so a user who has nothing written down can still start there.

### `interview-workflow-task`

Pulls the task out of the user's head and onto disk as
`$CEH_WORKFLOW_BUILD_DIR/<name>-workflow-spec.md`, under nine fixed headings
the builder gates on by name. Records unanswered questions as unanswered
rather than as "none" — questions 8 (which steps damage something if run
twice) and 9 (which steps are irreversible) are the two people skip, and
assuming them empty is what produces a workflow with no re-run guard that
publishes without pausing.

Opens with the repetition test: a task that will not run again in the same
shape gets no spec.

**Auto-triggers on:** "interview me about this task", "help me spec out this
workflow", or when `build-agentic-workflow` finds its inputs incomplete.

### `build-agentic-workflow`

Checks the nine answers exist, applies the one-skill-vs-workflow gate, decides
per step whether it becomes an existing skill, a script, inline prose, or its
own step skill, then emits the set leaf-first so every reference resolves as it
is written.

**Auto-triggers on:** "turn this into a workflow", "we run the same check
every release", "build an agentic workflow", or "I need a skill that calls
other skills".

Covers the assumed-capability contract, the six-condition workflow gate, the
step-earns-a-skill test, saved dynamic workflows as an optional stage backend,
data-contract schemas for non-adjacent handoffs (step N to step N+m), the
falsifiable-gate rule, and the two run directories. A workflow comes out as
`flow.yaml` (format: `references/flow-config-schema.md`), a thin
`<name>-flow` trigger skill and an invocation guide with the interactive and
headless commands. Launch arguments, approvals, headless permissions and the
dynamic-workflow setup are documented with the runner in
[`ceh-workflow-runner`](../ceh-workflow-runner/README.md).

## Directories

|            | Variable                  | Default              | Holds                                                                                                    |
| ---------- | ------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------- |
| Build time | `$CEH_WORKFLOW_BUILD_DIR` | `.agents_workspace/` | the interview spec while authoring                                                                       |
| Run time   | `$CEH_WORKFLOW_RUN_DIR`   | `.agents_workspace/` | a generated workflow's step artifacts and run state (read by `ceh-workflow-runner:run-agentic-workflow`) |

Two variables on purpose. Building one workflow must not collide with running
another. Each run gets its own `<run-dir>/<name>/<run-id>/`, so a second run
never reads the first one's artifacts, and that directory is expected to be
git-ignored.

## Packaging a generated workflow as a plugin

Not automated yet. Keep the output in `.claude/skills/` unless the workflow is
shared across repos. To package it by hand:

1. Create `<plugin>/.claude-plugin/plugin.json` with `name`, `version`, and
   `description`.
2. Move every `<name>-*` skill directory into `<plugin>/skills/`. Script paths
   through `${CLAUDE_SKILL_DIR}` keep resolving, because `skills/` stays flat.
3. Prefix every Skill tool call with the plugin name: `skill="<name>-step"`
   becomes `skill="<plugin>:<name>-step"`. Plugin skills are namespaced, so an
   unprefixed call no longer resolves. This is the one step a plain copy gets
   wrong.
4. Check that every call now names a skill that exists in the plugin.

A copy script was considered and rejected: steps 1 and 2 are a few shell
commands, and step 3 needs to tell a call from a mention, which the agent that
built the workflow already knows.

## Not this plugin

- Running a built workflow: use `ceh-workflow-runner`.
- Evaluating a skill that already exists.
- Delegating one big task to subagents right now, without producing a reusable
  artifact.
