---
schema: decision-rule/v2
decided: 2026-10-06
source: "plugins/CLAUDE.md (1778e9c)"
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Skill bundled files

Each skill is self-contained with inline content. `references/` holds only two kinds of file, and
output templates live in `assets/` instead:

- A schema: the schema of an output template, or one used by several skills. Skills of one plugin
  share one copy in the plugin's own `references/`, cited as `${CLAUDE_PLUGIN_ROOT}/references/<file>`.
  A file used by one skill lives in that skill's `references/`. Only a file needed by skills of
  different plugins is copied word for word into each and registered in `docs/CROSS_REFERENCES.md`.
- A standards set too large to inline.

Never general reference material a model already knows. A rule that applies on every run stays
inline. Exceptions: `ceh-ui-design:design-ui` and `ceh-web-frontend:visualize-graph-cytoscape`
keep their catalog files, a new catalog skill argues its own exception in its PR, and scaffold or
script bundles a skill executes or copies are allowed (`ceh-ag-ui`, `ceh-git-datastore`,
`ceh-business-plan`).

Why: a model can skip a link and never see it, so only what a run reads in part leaves the body.
