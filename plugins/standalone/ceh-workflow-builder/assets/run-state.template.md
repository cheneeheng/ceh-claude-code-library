---
schema: run-state/v1
---

# Run state: <flow>/<run id>

flow: <flow>
config: <path to flow.yaml>
mode: <interactive | headless>
inputs: <name=value, ...>

## Stages

- <id>: <pending | done | awaiting-approval | failed> | <artifact paths or -> | <note>

## Approvals

- <id>: <approved | rejected> | <interactive | approve=<id> | resume-prompt> | <ISO time>

FLOW STATUS: <done | awaiting-approval <stage-id> | failed <stage-id> <reason>>
