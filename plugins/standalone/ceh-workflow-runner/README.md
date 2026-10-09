# ceh-workflow-runner

Run a workflow that `ceh-workflow-builder` built for repeated product work,
such as a weekly SEO pass or a pre-release check. The builder is for authoring
and is not needed once the flow exists, so this plugin carries only the runner:
install it wherever a flow runs, interactively or headless (`claude -p`).

Each stage's work goes to a Claude Code native capability. The runner keeps
only what native lacks: approvals between stages, world checks before a re-run,
run state for resume, and the `FLOW STATUS:` line. As Claude Code covers one of
those, that part of the runner goes.

The `flow.yaml` contract is in
[references/flow-config-schema.md](references/flow-config-schema.md), a
word-for-word copy of the builder's. How build and run fit together, and the
tests behind the headless and dynamic-workflow design, are in the builder's
[docs/ARCHITECTURE.md](../ceh-workflow-builder/docs/ARCHITECTURE.md) and
[docs/TEST_RESULTS.md](../ceh-workflow-builder/docs/TEST_RESULTS.md).

## Skills

| Skill                  | Invoke                                      | Does                                                                                |
| ---------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------- |
| `run-agentic-workflow` | `/ceh-workflow-runner:run-agentic-workflow` | Runs a built workflow from its `flow.yaml`: stages, approvals, gates, state, resume |

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

## Environment variables

| Variable                | Required | Default              | Holds                                                                                                     |
| ----------------------- | -------- | -------------------- | --------------------------------------------------------------------------------------------------------- |
| `$CEH_WORKFLOW_RUN_DIR` | no       | `.agents_workspace/` | a run's step artifacts and `run-state.md`, under `<run-dir>/<name>/<run-id>/`, expected to be git-ignored |

## Not this plugin

- Building or specifying a workflow: use `ceh-workflow-builder`.
