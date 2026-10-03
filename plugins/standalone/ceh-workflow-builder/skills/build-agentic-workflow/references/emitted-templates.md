# Emitted templates

The three `SKILL.md` shapes `build-agentic-workflow` emits into the target repo. Fill every
placeholder; the frontmatter rules in the skill's Rules section apply to all three.

## The single-skill template

The Phase 2 default, and the path most tasks end on.

```markdown
---
name: <name>
description: >-
  <The moment, as a verb.> Trigger on "<phrase>", "<phrase>". Not for <nearest neighbour>, use
  <that> instead.
compatibility: >-
  <Only if it needs a CLI, service, credential, or network.>
---

# <Name>

<One paragraph: what this does and the one thing it gets right that doing it ad hoc does not.>

## Procedure

1. <step>
2. <step> — <how to tell it worked, only where that is not self-evident>
3. <irreversible step> — <confirm with the user first, showing exactly what will be sent or changed>

## Done when

<The falsifiable end condition from spec question 6.>
```

No pipeline table, no run directory, no schemas: a single skill runs in one context and hands nothing
off. Adding those is the over-engineering Phase 2 exists to prevent.

## The thin trigger skill template

The flow's `SKILL.md` carries the trigger and nothing else. Ordering, gates and approvals live in
`flow.yaml`; the runner executes them.

```markdown
---
name: <name>-flow
description: >-
  <The moment, as a verb.> Trigger on "<phrase>", "<phrase>". Runs the <name> flow from its
  flow.yaml through ceh-workflow-builder:run-agentic-workflow. Not for <nearest neighbour>, use
  <that> instead.
argument-hint: "<Launch args, e.g. [mode=headless] [repo=<path>] [approve=<stage-id>]>"
compatibility: >-
  Needs the ceh-workflow-builder plugin installed where the flow runs. <Only if a stage is a saved
  workflow: Claude Code v2.1.269+ with the Workflow tool on (Dynamic workflows in /config, or
  headless --settings '{"enableWorkflows": true, "disableWorkflows": false}'). Also name any CLI a
  stage needs, with its minimum version and what fails without it.>
---

# <Name> Flow

<One paragraph: the stages as an arrow chain, and what this adds over running the steps ad hoc.>

Invoke the Skill tool with skill="ceh-workflow-builder:run-agentic-workflow", passing
`config=${CLAUDE_SKILL_DIR}/<flow.yaml>` followed by `$ARGUMENTS` unchanged. If that skill cannot be
called, stop and say the ceh-workflow-builder plugin must be installed. Do not run the stages
yourself.
```

Beside it sit `flow.yaml` and the invocation guide `README.md`. `flow.yaml` follows
`${CLAUDE_PLUGIN_ROOT}/references/flow-config-schema.md`, whose Complete example section is the
model for it: copy its shape, not its stages.

In the emitted files, spell the delegation out as a literal instruction to invoke the Skill tool
with the runner's name, and give each schema its real filename and `flow.yaml` its real path. The
template above keeps `flow.yaml` as an angle-bracket placeholder on purpose: _this_ repo's
`validate.py` resolves every literal `${CLAUDE_SKILL_DIR}/…` and `references/…` path it finds, so a
concrete example here would fail the repo's own gate. Do not "fix" it.

## The step skill template

```markdown
---
name: <name>-<step>
description: >-
  <The moment.> Called by `<name>-flow` as stage `<stage-id>`; not for direct use outside that flow.
compatibility: >-
  <Only if this step needs a CLI, service, credential, or network. A step is the usual place such a
  need appears, so check before omitting.>
---

# <Name>: <Step>

Reads `<artifact>` at `<run>/<file>` per `<schema>`, where `<run>` is the run directory the flow
passes in as `run=<path>`; writes `<artifact>` to `<run>/<file>`. <Omit whichever half does not
apply.>

<The step's actual instructions.>

## Done when

<The falsifiable condition the flow's gate checks.>
```
