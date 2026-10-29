---
schema: decision-rule/v2
decided: 2026-10-28
source: "conversation"
paths:
  - "plugins/**"
  - ".claude/skills/**"
---

# Skill references

In a skill body, write `Invoke the Skill tool with skill="<plugin>:<skill>"` when the procedure
runs that skill as a step, every time the step is reached, even when the step itself has a
condition. Write the bare name (`ceh-<plugin>:<skill>`) for a redirect, a suggestion, a citation of
the skill's content, a command the user runs, or a skill in another plugin that is not a declared
dependency.

Why: an explicit call makes the model load the skill and lets `validate.py` check it, while a bare
name is only a pointer the model may skip.
