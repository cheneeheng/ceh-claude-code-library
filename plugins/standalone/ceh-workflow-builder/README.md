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
repo's `.claude/skills/`, so there is no install step. A multi-step workflow
is emitted as a `flow.yaml` config plus a thin trigger skill, and runs through
the generic runner in this plugin, so the plugin must be installed wherever
the flow runs.

Building is interactive only. Running works interactively and headless
(`claude -p`).

How the pieces fit together, with diagrams, is in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). The tests behind the headless
and dynamic-workflow design are in [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md).

## Skills

| Skill                     | Invoke                                          | Does                                                                                |
| ------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------- |
| `interview-workflow-task` | `/ceh-workflow-builder:interview-workflow-task` | Asks the nine questions, writes the workflow spec                                   |
| `build-agentic-workflow`  | `/ceh-workflow-builder:build-agentic-workflow`  | Designs and emits the artifact from that spec                                       |
| `run-agentic-workflow`    | `/ceh-workflow-builder:run-agentic-workflow`    | Runs a built workflow from its `flow.yaml`: stages, approvals, gates, state, resume |

Either of the first two is a valid entry point. `build-agentic-workflow` opens with an
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
step-earns-a-skill test, saved dynamic workflows as an optional stage backend,
data-contract schemas for non-adjacent handoffs (step N to step N+m), the
falsifiable-gate rule, and the two run directories. A workflow comes out as
`flow.yaml` (format: `references/flow-config-schema.md`), a thin
`<name>-flow` trigger skill and an invocation guide with the interactive and
headless commands.

### `run-agentic-workflow`

The generic runner. Reads a `flow.yaml`, checks it, then walks its stages in
order. Each stage runs as a skill, an `Agent` dispatch, a script, inline
instructions, or a saved dynamic workflow. The runner owns ordering, approvals,
gates, run state and resume, and ends every run with one line:

```
FLOW STATUS: done
FLOW STATUS: awaiting-approval <stage-id>
FLOW STATUS: failed <stage-id> <reason>
```

Generated `<name>-flow` skills call it; you can also call it directly with
`config=<path>`. Launch arguments:

| Argument  | Meaning                                                        |
| --------- | -------------------------------------------------------------- |
| `config`  | Path to `flow.yaml`. Required                                  |
| `mode`    | `interactive` (default) or `headless`. Explicit, never guessed |
| `resume`  | `latest` or `new`. Default: ask interactively, `new` headless  |
| `approve` | Stage ids approved in advance, comma-separated                 |
| other     | The flow's own `inputs`, as `name=value`                       |

**Approvals.** Interactive asks. Headless follows each approval's `headless`
setting: `stop` (default) ends the session at `awaiting-approval` so a later
launch can approve, `preapproved-only` proceeds only for an `approve=` id, and
`fail` ends the run. Resume with `claude -p --resume <session-id> 'APPROVED
<stage-id>'`, or in a fresh session with `resume=latest approve=<stage-id>`;
the state file is the record, `--resume` only keeps context.

**Headless needs explicit permissions.** Nobody is there to prompt, so pass
every tool a stage needs in `--allowedTools` (the builder derives the list into
the flow's guide). Pass `--output-format json` and branch on the status line in
`result`.

**Saved dynamic workflows are optional.** The Workflow tool is off by default.
Interactive: turn on Dynamic workflows in `/config`. Headless: pass `--settings
'{"enableWorkflows": true, "disableWorkflows": false}'` (the `enableWorkflows`
key is undocumented and may change) plus `--allowedTools 'Workflow(<name>)'`.
Without the tool a workflow stage runs its declared fallback or fails; the
runner never imitates it by hand. Workflow `.js` files need LF line endings.

## Directories

|            | Variable                  | Default              | Holds                                                                                |
| ---------- | ------------------------- | -------------------- | ------------------------------------------------------------------------------------ |
| Build time | `$CEH_WORKFLOW_BUILD_DIR` | `.agents_workspace/` | the interview spec while authoring                                                   |
| Run time   | `$CEH_WORKFLOW_RUN_DIR`   | `.agents_workspace/` | a generated workflow's step artifacts and run state (read by `run-agentic-workflow`) |

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
