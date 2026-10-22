# Run state schema

`{run}/run-state.md`, written by the runner when a flow is `resumable: true` and updated after every
stage change, per `flow-config-schema.md` beside this file. A new file is a copy of
`../assets/run-state.template.md`, relative to this file. The `schema: run-state/v1` line stays as
written. This file is copied word for word into `ceh-workflow-builder` and `ceh-workflow-runner`.

## Header

- **Title:** `Run state: <flow>/<run id>`.
- `flow`: the flow's name.
- `config`: the path to its `flow.yaml`.
- `mode`: `interactive` or `headless`.
- `inputs`: the run's inputs, as `name=value` pairs separated by commas.

## Sections

- **Stages:** one line per stage, `<id>: <state> | <artifact paths or -> | <note>`. `<state>` is
  `pending`, `done`, `awaiting-approval`, or `failed`. The note carries the gate evidence in one
  line.
- **Approvals:** one line per decision, `<id>: <approved | rejected> | <source> | <time>`. The
  source is `interactive`, `approve=<id>`, or `resume-prompt`, and the time is ISO-8601.
- **`FLOW STATUS` line:** the file's last line, the same as the run's reply, per
  `flow-config-schema.md`.

## Worked example

```markdown
---
schema: run-state/v1
---

# Run state: prepublish/20261003-0930

flow: prepublish
config: .claude/skills/prepublish-flow/flow.yaml
mode: headless
inputs: repo=.

## Stages

- audit: done | findings.md | fallback: agent (Workflow tool absent)
- fix: done | fixes/ | 12 items
- verify: failed | - | attempt 3 of 3: 2 tests red
- publish: awaiting-approval | - | {run}/approval-publish.md

## Approvals

- publish: approved | approve=publish | 2026-10-03T10:05

FLOW STATUS: awaiting-approval publish
```
