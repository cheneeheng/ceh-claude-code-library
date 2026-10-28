---
schema: decision-rule/v1
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Output templates

Every file a skill saves has a versioned template, `<schema>.template.md` in the skill's or the
plugin's `assets/`, its frontmatter opening with `schema: <schema>/v<N>`. Each template has a
schema, `<schema>-schema.md` in the `references/` beside that `assets/` folder, which says where the
file is saved, names the template as `../assets/<schema>.template.md`, and explains every field and
section. The template is a bare skeleton: short placeholders (`<title>`) and choices as `<a | b>`,
with comments, explanation, and examples in the schema. The skill body cites both instead of
spelling the format inline. A reference file cites a sibling folder's file relative to itself
(`../assets/<file>`). Bump `v<N>` when a required field or heading is renamed or removed. Out of
scope: what the user ships, `flow.yaml`, and a file a script generates from a templated one.

Why: the format lives in one pair of files, and each saved file names its version. Decided 2026-10-21. Source: plugins/CLAUDE.md (f366fe9).
