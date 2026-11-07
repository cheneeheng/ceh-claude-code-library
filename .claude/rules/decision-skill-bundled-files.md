---
schema: decision-rule/v2
decided: 2026-11-07
source: "product/plans/skill-local-files.yaml"
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Skill bundled files

Each skill is self-contained with inline content. `references/` holds only two kinds of file, and
output templates live in `assets/` instead:

- A schema: the schema of an output template, or one used by several skills, and for a YAML
  format its `<schema>-model.py` beside it (`decision-output-templates.md`). Every file a skill
  reads, copies or runs lives in that skill's own `assets/`, `references/` or `scripts/`, cited as
  `${CLAUDE_SKILL_DIR}/<folder>/<file>`, so a skill folder works wherever it is copied. A file
  several skills need, in one plugin or several, is copied word for word into each, registered in
  `docs/CROSS_REFERENCES.md`, and kept byte-identical by the `copies` check. A plugin root holds
  only `scripts/` for its hooks and agents.
- A standards set too large to inline.

Never general reference material a model already knows. A rule that applies on every run stays
inline. Exceptions: `ceh-ui-design:design-ui` and `ceh-web-frontend:visualize-graph-cytoscape`
keep their catalog files, a new catalog skill argues its own exception in its PR, and scaffold or
script bundles a skill executes or copies are allowed (`ceh-ag-ui`, `ceh-git-datastore`,
`ceh-business-plan`, and `scripts/artifact.py` in each skill that carries a YAML format's model).

Why: a model can skip a link and never see it, so only what a run reads in part leaves the body.
