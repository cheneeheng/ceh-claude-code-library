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
and a PreToolUse guard denying hand edits to that Markdown. Each plugin that holds the format
carries its own copy of the model, `artifact.py`, and the hooks. The build plan (`plan/v2`) is the
trial. Other formats follow only once the user approves it.

Why: the user asked for handoff files that are deterministic and checkable
(VISION, Who overrides), which satisfies principle 7's evidence bar in place of an observed
failure. The guard does narrow what an agent may do, because a hand edit to generated Markdown is
silently lost at the next render.
