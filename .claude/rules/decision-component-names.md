---
schema: decision-rule/v1
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Component names

Name skills with a verb phrase and agents with a noun, and put the framework or library in the
name when a skill is specific to one (`write-fastapi-endpoints`, `write-pytest-service-tests`). A
skill is something you do at a moment (`commit`, `shrink-diff`), an agent something you delegate
to (`bulk-reader`). Pick the word you would say out loud, not a generic one like `optimize`.
Exempt: model-only standards named for what they carry (`agent-coding-contract`,
`usage-limit-handoff`), and terms of art (`pull-request`, `release`). A plugin is named for its
use case, a script for what it does, and the `ceh-` prefix is exempt.

Why: vision principle 10, "Names say what they do": anyone who has seen only the name can say what the component does and when. Decided 2026-10-06. Source: plugins/CLAUDE.md (1778e9c).
