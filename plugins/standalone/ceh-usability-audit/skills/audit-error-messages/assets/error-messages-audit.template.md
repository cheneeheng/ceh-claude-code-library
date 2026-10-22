---
schema: error-messages-audit/v1
target: <target>
run: <NNN>
date: YYYY-MM-DD
harvested: <messages harvested>
already_complete: <how many satisfied all three parts before any rewrite>
---

# Error messages — <target>, run <NNN>

**Messages harvested:** <n>
**Complete before rewriting:** <n> of <n>

## Triage

| #   | Location        | Current text | 1   | 2   | 3   | Severity                         | Rewrite | Applied                  |
| --- | --------------- | ------------ | --- | --- | --- | -------------------------------- | ------- | ------------------------ |
| 1   | `<path>:<line>` | `<text>`     | ✓/✗ | ✓/✗ | ✓/✗ | <Blocker/Detour/Friction/Polish> | `<new>` | <yes / no: <the reason>> |

## Systemic causes

<Each shared handler or wrapper behind several ✗ rows, and whether it was fixed once.>
