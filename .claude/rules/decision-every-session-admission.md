---
schema: decision-rule/v2
decided: 2026-11-20
source: "CLAUDE.md (1142f63)"
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Every-session admission

`ceh-every-session` admits only what holds however Claude Code is used: coding, writing, research,
or ops. If a component assumes a repository, code, or a specific activity, it belongs elsewhere.
"Useful almost everywhere" is not the test.

Why: that test is how an every-session plugin becomes a dumping ground.
