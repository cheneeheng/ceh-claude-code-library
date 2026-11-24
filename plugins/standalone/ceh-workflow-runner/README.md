# ceh-workflow-runner

Run a workflow that `ceh-workflow-builder` built for repeated product work, such as a weekly SEO
pass or a pre-release check. The builder is for authoring and is not needed once the flow exists,
so this plugin carries only the runner: install it wherever a flow runs, interactively or headless
(`claude -p`).

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). No other plugin depends on this one. The
hooks need `python3` on `PATH`. Checking and rendering the run state needs `uv`. Without it the
agent is told once per session that the run state went unchecked. A flow with a `workflow` stage
needs Claude Code v2.1.269+ with the Workflow tool on, as [Saved dynamic workflows](#saved-dynamic-workflows)
describes.

## Skills

| Skill                  | Say or type                                                                                                                                                                        | What it does                                                                        |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `run-agentic-workflow` | "run the flow.yaml", `/ceh-workflow-runner:run-agentic-workflow config=<path> [mode=...] [resume=...]`. Loads by itself when a generated `<name>-flow` skill hands over its config | Runs a built workflow from its `flow.yaml`: stages, approvals, gates, state, resume |

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                               |
| -------------------- | ---------------------------------------------------------------------------------- |
| Run state check      | Checks each written `run-state.yaml` and renders `run-state.md` beside it          |
| Generated-file guard | Stops a hand edit to the generated Markdown, which the next render would overwrite |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable               | Default                       | Effect                                                                                                                         |
| ---------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `CEH_WORKFLOW_RUN_DIR` | `.agents_workspace/workflow/` | Where a run keeps its step artifacts and `run-state.yaml` with its rendered `run-state.md`, under `<run-dir>/<name>/<run-id>/` |
| `CEH_ARTIFACT_CHECK`   | unset (check on)              | `off` turns the run state check and the generated-file guard off                                                               |
| `CEH_DISABLED_HOOKS`   | unset (all hooks on)          | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard`                                               |

## How it works

### What the runner adds

Each stage's work goes to a Claude Code native capability. The runner keeps only what native
lacks: approvals between stages, world checks before a re-run, run state for resume, and the
`FLOW STATUS:` line. The `flow.yaml` contract is in
[skills/run-agentic-workflow/references/flow-config-schema.md](skills/run-agentic-workflow/references/flow-config-schema.md).

### A run

The runner reads a `flow.yaml`, checks it, then walks its stages in order. Each stage runs as a
skill, an `Agent` dispatch, a script, inline instructions, or a saved dynamic workflow. The runner
owns ordering, approvals, gates, run state and resume, and ends every run with one line:

```
FLOW STATUS: done
FLOW STATUS: awaiting-approval <stage-id>
FLOW STATUS: failed <stage-id> <reason>
```

Generated `<name>-flow` skills call it. You can also call it directly with `config=<path>`.

### Launch arguments

| Argument  | Meaning                                                        |
| --------- | -------------------------------------------------------------- |
| `config`  | Path to `flow.yaml`. Required                                  |
| `mode`    | `interactive` (default) or `headless`. Explicit, never guessed |
| `resume`  | `latest` or `new`. Default: ask interactively, `new` headless  |
| `approve` | Stage ids approved in advance, comma-separated                 |
| other     | The flow's own `inputs`, as `name=value`                       |

### Approvals

Interactive asks. Headless follows each approval's `headless` setting:

- `stop` (default) ends the session at `awaiting-approval` so a later launch can approve.
- `preapproved-only` proceeds only for an `approve=` id.
- `fail` ends the run.

Resume with `claude -p --resume <session-id> 'APPROVED <stage-id>'`, or in a fresh session with
`resume=latest approve=<stage-id>`. The state file is the record, and `--resume` only keeps
context.

### Headless needs explicit permissions

Nobody is there to prompt, so pass every tool a stage needs in `--allowedTools` (the builder
derives the list into the flow's guide). For a resumable flow also pass
`Bash(uv run --script:*)`, which checks and renders the run state. Pass `--output-format json` and
branch on the status line in `result`.

### Saved dynamic workflows

They are optional. The Workflow tool is off by default. Interactive: turn on Dynamic workflows in
`/config`. Headless: pass `--settings '{"enableWorkflows": true, "disableWorkflows": false}'` (the
`enableWorkflows` key is undocumented and may change) plus `--allowedTools 'Workflow(<name>)'`.
Without the tool a workflow stage runs its declared fallback or fails. The runner never imitates it
by hand. Workflow `.js` files need LF line endings.

## Not this plugin

- Building or specifying a workflow: `ceh-workflow-builder`.

## Where its files live

Each run writes its step artifacts and `run-state.yaml`, with `run-state.md` rendered beside it, to
`.agents_workspace/workflow/<name>/<run-id>/`, or under `CEH_WORKFLOW_RUN_DIR` when set. Keep that
folder git-ignored.
