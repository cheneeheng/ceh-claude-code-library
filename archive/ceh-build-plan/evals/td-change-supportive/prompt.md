---
tags: [trigger, single-arm]
max_turns: 60
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
plugins:
  [
    "../..",
    "../../../ceh-codebase-explanation",
    "../../../ceh-product-direction",
  ]
---

update the technical design: persistence moves from SQLite to PostgreSQL
