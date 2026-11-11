---
schema: decision-rule/v2
decided: 2026-10-21
source: "plugins/CLAUDE.md (f366fe9)"
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Output templates

Every file a skill saves has a versioned template, `<schema>.template.md` in the skill's
`assets/`, its frontmatter opening with `schema: <schema>/v<N>`. Each template has a
schema, `<schema>-schema.md` in the `references/` beside that `assets/` folder, which says where the
file is saved, names the template as `../assets/<schema>.template.md`, and explains every field and
section. The template is a bare skeleton: short placeholders (`<title>`) and choices as `<a | b>`,
with comments, explanation, and examples in the schema. The skill body cites both instead of
spelling the format inline. A reference file cites a sibling folder's file relative to itself
(`../assets/<file>`). Bump `v<N>` when a required field or heading is renamed or removed. Out of
scope: what the user ships, `flow.yaml`, and a file a script generates from a templated one.

A format may instead be YAML validated end to end: `<schema>.template.yaml`, whose first key is
`schema: <schema>/v<N>`, with `<schema>-model.py` beside the schema file holding its pydantic model
and Markdown renderer. The skill saves the YAML, and the Markdown generated from it is committed
beside it with `generated_from: <file>.yaml` and a do-not-edit `generated_note` in its
frontmatter, its body inside a prettier-ignore range, and never edited by hand: the skill that
edits the YAML re-renders it. The YAML formats so far are the build plan (`plan/v2`), the
evidence report (`evidence/v2`), the architecture document (`architecture/v3`), the vision and
strategy (`vision/v2`, `strategy/v2`), the business plan (`business-plan/v3`), the QA report
(`qa-report/v2`), the performance file (`perf-report/v2`), the security audit
(`security-audit/v2`), the three usability audits (`first-run-audit/v2`, `interface-audit/v2`,
`error-messages-audit/v2`), the fix record (`fix-record/v2`), the session handoff
(`handoff/v2`), the workflow spec (`workflow-spec/v2`), and the run state (`run-state/v2`).

Why: the format lives in one pair of files, and each saved file names its version. A YAML format
adds the model, so every field of the file, body included, is checked rather than described.
