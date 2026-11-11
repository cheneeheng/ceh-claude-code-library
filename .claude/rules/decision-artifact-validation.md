---
schema: decision-rule/v2
decided: 2026-11-06
source: "product/plans/artifact-validation.md"
paths:
  - "plugins/**"
  - "tools/validate-plugins/**"
---

# Artifact validation

A handoff file one stage writes and another reads is checked by code, not only described: a YAML
format with a pydantic model (`decision-output-templates.md`), checked by a PostToolUse hook on
every write and by `artifact.py check` in each skill that reads it, with its Markdown generated
and a PreToolUse guard denying hand edits to that Markdown. Each skill that reads the format
carries its own copy of the model and `artifact.py`, and each plugin whose skills write it keeps
`artifact.py` and the hooks at its root for its hooks. A plugin in `READERS` in `checks/artifact_models.py`,
whose skills read a format or, as `write-fastapi-endpoints` does, render it themselves, carries no
hooks. The user approved the build plan trial
(`plan/v2`) on 2026-11-07, and the other spine formats follow it, per
`product/plans/artifact-validation-formats.yaml`: the evidence report (`evidence/v2`), the
architecture document (`architecture/v3`), the vision and strategy (`vision/v2`,
`strategy/v2`), and the business plan (`business-plan/v3`). The reports
`write-evidence-report` reads follow them, per `product/plans/report-only-formats.yaml`: the QA
report (`qa-report/v2`), the performance file (`perf-report/v2`), the security audit
(`security-audit/v2`), and the three usability audits (`first-run-audit/v2`, `interface-audit/v2`,
`error-messages-audit/v2`). The fix record (`fix-record/v2`) follows, per
`product/plans/fix-record-yaml.yaml`, with the hooks in core `ceh-coding-conduct` by the user's
choice, so a record is checked even without `ceh-testing`. The session handoff (`handoff/v2`)
follows, per `product/plans/handoff-yaml.yaml`, with the hooks in `ceh-every-session`, which leaves
`READERS`, also by the user's choice. The workflow spec (`workflow-spec/v2`) follows, per
`product/plans/workflow-spec-yaml.yaml`, with the hooks in `ceh-workflow-builder`, which holds both
its writer and its reader. The run state (`run-state/v2`) follows, per
`product/plans/run-state-yaml.yaml`, with the hooks in `ceh-workflow-runner`, which writes and
reads it, and its model copied beside the `flow.yaml` contract in `ceh-workflow-builder`. The
competitor report (`competitor-report/v2`) follows, per
`product/plans/competitor-report-yaml.yaml`, with the hooks in `ceh-competitor-analysis`, which
holds both its writer and its reader.

Why: the user asked for handoff files that are deterministic and checkable
(VISION, Who overrides), which satisfies principle 7's evidence bar in place of an observed
failure. The guard does narrow what an agent may do, because a hand edit to generated Markdown is
silently lost at the next render.
