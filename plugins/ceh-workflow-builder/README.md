# ceh-workflow-builder

Turn a repetitive multi-step task into something an agent runs, instead of
something you drive by hand every time.

The hard part is not writing a `SKILL.md` — three other tools do that. The hard
parts are deciding whether the task is one skill or a multi-step workflow, and
making the handoffs between steps explicit. A workflow whose steps pass data
with no declared shape fails the same way every time: a later step infers a
shape from whatever artifact it finds, infers it wrong, and the run keeps
producing garbage past a green gate.

Target runtime is **Claude Code**. The emitted artifact lands in the target
repo's `.claude/skills/`, so there is no install step.

## Skills

| Skill                     | Invoke                                          | Does                                              |
| ------------------------- | ----------------------------------------------- | ------------------------------------------------- |
| `interview-workflow-task` | `/ceh-workflow-builder:interview-workflow-task` | Asks the nine questions, writes the workflow spec |
| `build-agentic-workflow`  | `/ceh-workflow-builder:build-agentic-workflow`  | Designs and emits the artifact from that spec     |

Either one is a valid entry point. `build-agentic-workflow` opens with an
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

**Auto-triggers on:** "interview me about this task", "ask me what you need to
automate this", "help me spec out this workflow", or "I'm not sure what you
need to know".

### `build-agentic-workflow`

Checks the nine answers exist, applies the one-skill-vs-workflow gate, decides
per step whether it becomes an existing skill, a script, inline prose, or its
own step skill, then emits the set leaf-first so every reference resolves as it
is written.

**Auto-triggers on:** "turn this into a skill", "turn this into a workflow",
"build an agentic workflow", "automate this process", "make this repeatable",
"I do this by hand every time", or "I need a skill that calls other skills".

Covers the assumed-capability contract, the six-condition workflow gate, the
step-earns-a-skill test, data-contract schemas for non-adjacent handoffs
(step N to step N+m), the falsifiable-gate rule, and the two run directories.

## Directories

|            | Variable                  | Default              | Holds                                               |
| ---------- | ------------------------- | -------------------- | --------------------------------------------------- |
| Build time | `$CEH_WORKFLOW_BUILD_DIR` | `.agents_workspace/` | the interview spec while authoring                  |
| Run time   | `$CEH_WORKFLOW_RUN_DIR`   | `.agents_workspace/` | a generated workflow's step artifacts and run state |

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

- Evaluating a skill that already exists.
- Delegating one big task to subagents right now, without producing a reusable
  artifact.
