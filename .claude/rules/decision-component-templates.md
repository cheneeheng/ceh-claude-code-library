---
schema: decision-rule/v1
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Component templates

Every new `SKILL.md` and `agents/*.md` starts as a copy of the templates in
`.claude/skills/add-plugin-component/assets/`. Frontmatter uses only the fields in the official
Claude Code [skills](https://code.claude.com/docs/en/skills#frontmatter-reference) and
[subagents](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) references.

Why: every component then shares one frontmatter order, one heading set, and one voice. Decided 2026-10-06. Source: plugins/CLAUDE.md (1778e9c).
