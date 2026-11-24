---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-9e7cd123"
---

# Skill requirements in frontmatter

When a skill needs something installed, such as a Linux sandbox for shell runs, prefer listing it as a requirement in the skill's frontmatter over install instructions in its body, because the body should only hold what the agent needs to run the skill.
