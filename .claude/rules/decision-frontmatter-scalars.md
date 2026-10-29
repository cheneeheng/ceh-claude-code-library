---
schema: decision-rule/v2
decided: 2026-10-06
source: "plugins/CLAUDE.md (1778e9c)"
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Frontmatter scalars

A skill or agent `description` is always a folded block scalar (`>-`), never quoted and never
plain, and at most 300 characters. For a skill, write the moment, two or three trigger phrases,
and at most one "Not for" pointer. For an agent, write when to delegate and whether it is
read-only. Every other frontmatter key containing `: ` is quoted, single quotes by default. Add
`compatibility` (same `>-` scalar, at most 500 characters) only when running the skill needs
software the machine may not have, naming the runtime, its minimum version, and what fails
without it.

Why: `>-` has no escaping burden, and once the skill listing overflows its budget Claude Code drops whole descriptions.
