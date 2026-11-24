# ceh-workflow-runner design notes

## Native first

Each stage's work goes to a Claude Code native capability. The runner keeps only what native lacks.
As Claude Code covers one of those, that part of the runner goes.

## The flow.yaml contract and the builder

The `flow.yaml` contract in `skills/run-agentic-workflow/references/flow-config-schema.md` is a
word-for-word copy of the builder's. How build and run fit together, and the tests behind the
headless and dynamic-workflow design, are in the builder's
[docs/ARCHITECTURE.md](../../ceh-workflow-builder/docs/ARCHITECTURE.md) and
[docs/TEST_RESULTS.md](../../ceh-workflow-builder/docs/TEST_RESULTS.md).

## Hooks

Two hooks on `Edit|Write|MultiEdit`, both Python scripts that need `python3` on `PATH`:

- `artifact-render-hook.py` (PostToolUse) checks a written `run-state.yaml` against its model and
  renders `run-state.md` beside it. The check needs `uv`; without it the agent is told once per
  session that the run state went unchecked.
- `generated-md-guard.py` (PreToolUse) denies a hand edit to the generated Markdown, which the
  next render would overwrite.

`CEH_ARTIFACT_CHECK=off` turns both off, and `CEH_DISABLED_HOOKS` turns off either by name.
