---
schema: decision-rule/v2
decided: 2026-11-20
source: ".agents_workspace/product/plan/artifact-validation.md"
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
hooks. The formats checked this way are the ones with a `<schema>-model.py` in a skill's
`references/`. A format no other stage reads gets the same when the user decides so. A core
plugin carries the hooks when the user chooses so, as `ceh-coding-conduct` does for the fix
record, so a record is checked even without `ceh-testing`, and `ceh-every-session` for the
session handoff.

Why: the user asked for handoff files that are deterministic and checkable
(VISION, Who overrides), which satisfies principle 7's evidence bar in place of an observed
failure. The guard does narrow what an agent may do, because a hand edit to generated Markdown is
silently lost at the next render.
